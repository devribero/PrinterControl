"""
Configuracao de log (Fase 10).

Por que existe como modulo, e nao como um logging.basicConfig em main.py:
rodando como tarefa agendada do Windows, ninguem le stdout. Sem arquivo, um
erro as 3h da manha nao deixa rastro nenhum — e o primeiro sintoma vira "o
painel esta estranho", dias depois, sem nada para investigar.

O que este modulo garante:

  1. arquivo com rotacao, para o disco nao encher em silencio;
  2. o MESMO formato no console e no arquivo, para nao existir "o log que eu
     vi no terminal" diferente do "log que ficou gravado";
  3. um filtro de redacao, para que segredo nenhum entre no arquivo — nem
     por engano futuro. Ver RedactSecretsFilter.
"""
import logging
import logging.handlers
import re
from pathlib import Path

from app.config import BACKEND_DIR, settings

FORMATO = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"

#: Padroes redigidos antes de a linha chegar ao arquivo. A lista e curta de
#: proposito: cada item existe porque o valor correspondente REALMENTE circula
#: no processo (ver config.py). Nao e um antivirus de texto — e uma rede de
#: seguranca para o dia em que alguem logar `settings` inteiro num debug.
_PADROES_SENSIVEIS = [
    # Bearer vem PRIMEIRO, e nao depois: o padrao chave=valor abaixo casa
    # "authorization: Bearer" e trataria "Bearer" como o valor — redigindo a
    # palavra e deixando o token logo atras, que e o oposto do objetivo.
    # Redigido o token antes, sobra apenas o rotulo.
    re.compile(r"(?i)(bearer\s+)([A-Za-z0-9._\-]{8,})"),
    # chave=valor em querystring, .env, repr de dict/objeto.
    # As aspas opcionais ANTES do separador cobrem repr de dicionario
    # ({'password': 'x'}) e JSON ("password": "x"), que e como a maioria dos
    # vazamentos reais aparece — quase nunca como password=x.
    re.compile(
        r"(?i)[\"']?\b(secret_key|secret|password|senha|passwd|token|authorization|api_key|"
        r"snmp_community|webhook_url|password_hash)\b[\"']?\s*[=:]\s*[\"']?([^\s,;\"'}\])]+)"
    ),
    # LGPD (Fase 16): dado pessoal, nao segredo tecnico — mas o mesmo raciocinio
    # de "nunca deveria sobreviver no arquivo de log" se aplica. Alvo especifico:
    # o log de bloqueio de rate-limit do login (routes/auth.py), que grava
    # e-mail e IP em texto claro toda vez que alguem erra a senha demais vezes.
    # Escopado aos rotulos "conta=" e "origem=" (nao "qualquer coisa que
    # pareca e-mail em qualquer log") de proposito: um filtro de e-mail
    # generico redigiria identificadores uteis em outras mensagens
    # operacionais (ex.: "usuario X criado por Y"), reduzindo o valor de
    # depuracao sem ganho de privacidade correspondente — aqui o campo e
    # sempre PII (conta/IP de quem tentou logar), nunca outra coisa.
    re.compile(r"(?i)\b(conta|origem)=([^\s|]+)"),
]

_MASCARA = "***REDIGIDO***"


class RedactSecretsFilter(logging.Filter):
    """
    Substitui valores sensiveis na mensagem antes de ela ser emitida.

    Fica no HANDLER, e nao no logger da aplicacao: assim tambem alcanca o que
    bibliotecas de terceiros (uvicorn, sqlalchemy, apscheduler) escrevem, que
    e exatamente onde um vazamento apareceria sem ninguem ter escrito a linha.

    Limitacao assumida: a redacao roda sobre a mensagem ja formatada, entao
    custa uma formatacao extra por registro. Com o volume desta aplicacao
    (um ciclo de coleta a cada poucos minutos) isso e irrelevante, e a
    alternativa — confiar que ninguem jamais logue um segredo — nao e uma
    garantia, e uma esperanca.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            texto = record.getMessage()
        except Exception:  # noqa: BLE001 — log nunca pode derrubar a aplicacao
            return True

        redigido = texto
        for padrao in _PADROES_SENSIVEIS:
            redigido = padrao.sub(lambda m: f"{m.group(1)}{_MASCARA}", redigido)

        if redigido != texto:
            # Reescreve a mensagem e descarta os args, que ja foram aplicados
            # na formatacao acima — mante-los faria o handler tentar formatar
            # de novo e reintroduzir o valor original.
            record.msg = redigido
            record.args = ()

        return True


def _caminho_do_log() -> Path | None:
    """Resolve settings.log_file. Vazio = so console."""
    bruto = settings.log_file.strip()
    if not bruto:
        return None

    caminho = Path(bruto)
    if not caminho.is_absolute():
        caminho = BACKEND_DIR / caminho
    return caminho


def setup_logging() -> None:
    """
    Instala console + arquivo rotativo na raiz do logging.

    Idempotente: chamar duas vezes (reload do uvicorn, teste que importa o
    app mais de uma vez) nao duplica handlers — sem isso cada linha
    apareceria repetida, que e um jeito eficiente de tornar um log inutil.
    """
    raiz = logging.getLogger()
    nivel = getattr(logging, settings.log_level.strip().upper(), logging.INFO)
    raiz.setLevel(nivel)

    marca = "printercontrol_handler"
    if any(getattr(h, marca, False) for h in raiz.handlers):
        return

    formatter = logging.Formatter(FORMATO)
    redator = RedactSecretsFilter()

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    console.addFilter(redator)
    setattr(console, marca, True)
    raiz.addHandler(console)

    caminho = _caminho_do_log()
    if caminho is None:
        return

    try:
        caminho.parent.mkdir(parents=True, exist_ok=True)
        arquivo = logging.handlers.RotatingFileHandler(
            caminho,
            maxBytes=settings.log_max_bytes,
            backupCount=settings.log_backup_count,
            encoding="utf-8",
        )
        arquivo.setFormatter(formatter)
        arquivo.addFilter(redator)
        setattr(arquivo, marca, True)
        raiz.addHandler(arquivo)
    except OSError as exc:
        # Disco cheio, permissao negada, caminho em unidade de rede fora do
        # ar: nada disso pode impedir a API de subir. Perde-se o arquivo, nao
        # o servico — e o aviso sai no console, que ainda existe.
        raiz.warning("Log em arquivo desabilitado (%s): %s", caminho, exc)
