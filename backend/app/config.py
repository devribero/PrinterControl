from typing import Annotated

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode
from pathlib import Path


# Raiz do backend (…/backend), independente de onde o uvicorn foi iniciado.
BACKEND_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = BACKEND_DIR / "printer_control.db"


# Valor historico do secret_key. Continua sendo o default para nao quebrar o
# ambiente de desenvolvimento, mas e explicitamente recusado em producao.
DEV_SECRET_KEY = "dev-secret-key-change-in-production"
MIN_PRODUCTION_SECRET_LENGTH = 32

# Ambientes reconhecidos (Fase 9).
#   development -> maquina de quem desenvolve; simulacao liberada.
#   demo        -> instancia de demonstracao; dados ficticios sao ESPERADOS e
#                  a interface os anuncia permanentemente.
#   production  -> frota real. Qualquer simulacao aqui e erro de configuracao,
#                  nao preferencia.
ENVIRONMENTS = ("development", "demo", "production")


class Settings(BaseSettings):
    # Ambiente de execucao: "development" (padrao), "demo" ou "production".
    # Em producao as validacoes abaixo passam a ser obrigatorias.
    environment: str = "development"

    # Database — caminho ABSOLUTO de proposito: com um caminho relativo o
    # SQLite seguiria o cwd e um `uvicorn` iniciado da raiz do projeto criaria
    # um banco vazio no lugar errado.
    database_url: str = f"sqlite:///{DEFAULT_DB_PATH.as_posix()}"

    # JWT
    secret_key: str = DEV_SECRET_KEY
    algorithm: str = "HS256"
    access_token_expire_hours: int = 24

    # SNMP
    snmp_community: str = "public"
    snmp_timeout: float = 1.5
    snmp_retries: int = 1

    # Coleta simulada: habilita mode="mock" em /api/collect.
    # Deve permanecer False em producao — com ele ligado a API grava
    # leituras ficticias no banco como se fossem reais.
    allow_mock_collect: bool = False

    # Coleta agendada (APScheduler, dentro do proprio FastAPI)
    collection_enabled: bool = False
    collection_interval_minutes: int = 5
    # "real" = SNMP de verdade; "mock" = cenario simulado (exige allow_mock_collect)
    collection_mode: str = "real"
    # Ids das impressoras coletadas a cada ciclo, separados por virgula.
    # LEGADO (Etapa 5): desde que o scheduler passou a coletar toda a frota
    # ativa (active=True), este campo nao e mais lido pelo scheduler. Mantido
    # sem uso conhecido fora daqui para nao remover configuracao existente
    # sem necessidade comprovada.
    collection_printer_ids: str = "1"
    # Cenario usado quando collection_mode="mock"
    collection_scenario: str = "online_mono"
    # Paralelismo da coleta de frota (Etapa 5): consultas de rede/SNMP por
    # IP unico rodam em ate N threads simultaneas. A persistencia no banco
    # continua sequencial, numa unica Session no thread principal.
    collection_max_workers: int = 4

    # ------------------------------------------------------------------
    # Print Server (Etapa 3) — fonte real das impressoras, como no Main.ps1
    # (Get-Printer -ComputerName / Get-PrinterPort -ComputerName).
    # "mock" simula o retorno sem tocar em rede/Windows; "real" dispara
    # PowerShell via subprocess contra print_server_host.
    # ------------------------------------------------------------------
    print_server_mode: str = "mock"
    print_server_host: str = "elgjunprt"
    print_server_timeout_seconds: int = 30

    # ------------------------------------------------------------------
    # Webhook de alerta critico de toner (Etapa 6), equivalente a
    # Send-AlertaWebhook do Main.ps1 (Adaptive Card via Power Automate/Teams).
    # Vazio = desabilitado — nunca commitar a URL real aqui nem em .env.example.
    # ------------------------------------------------------------------
    webhook_url: str = ""
    webhook_timeout_seconds: float = 5.0

    @property
    def is_production(self) -> bool:
        return self.environment.strip().lower() == "production"

    @property
    def is_demo(self) -> bool:
        return self.environment.strip().lower() == "demo"

    @field_validator("environment")
    @classmethod
    def _environment_conhecido(cls, value: str) -> str:
        """
        Um ambiente escrito errado nao pode cair no default em silencio:
        `ENVIRONMENT=producao` (ou "prod", ou "Production" com espaco) daria
        uma instancia de producao rodando com as regras de desenvolvimento —
        exatamente o acidente que esta fase existe para impedir. Normaliza
        caixa e espaco, e recusa o que nao reconhece.
        """
        normalizado = value.strip().lower()
        if normalizado not in ENVIRONMENTS:
            raise ValueError(
                f"ENVIRONMENT invalido: {value!r}. Use um de: {', '.join(ENVIRONMENTS)}."
            )
        return normalizado

    @model_validator(mode="after")
    def _validate_production_mock(self) -> "Settings":
        """
        Fail-fast: producao nao sobe com simulacao ligada (Fase 9).

        O risco concreto e o default de `print_server_mode`, que e "mock" por
        razoes historicas. Um deploy de producao que apenas herde esse default
        e depois rode "Sincronizar" recebe a frota FICTICIA do simulador e
        marca como inativa toda impressora real que ele nao publica — ou seja,
        apaga a frota de producao e a substitui por uma inventada, gravando
        tudo no banco real.

        Recusar no boot, e nao avisar, e deliberado: um aviso em log seria
        lido depois do estrago. Vale o mesmo raciocinio ja aplicado a
        SECRET_KEY logo abaixo — configuracao incoerente com o ambiente e
        erro de operacao, nao preferencia.
        """
        if not self.is_production:
            return self

        if self.print_server_mode != "real":
            raise ValueError(
                f"PRINT_SERVER_MODE={self.print_server_mode!r} e incompativel com "
                "ENVIRONMENT=production: um Print Server simulado publica uma frota "
                "ficticia, e o proximo sync desativaria as impressoras reais que ela "
                "nao contem. Defina PRINT_SERVER_MODE=real."
            )

        if self.allow_mock_collect:
            raise ValueError(
                "ALLOW_MOCK_COLLECT=true e incompativel com ENVIRONMENT=production: "
                "a coleta simulada grava leituras ficticias no banco como se fossem "
                "reais, contaminando contadores e relatorios. Remova a variavel ou "
                "defina ALLOW_MOCK_COLLECT=false."
            )

        return self

    @model_validator(mode="after")
    def _validate_production_secrets(self) -> "Settings":
        """
        Impede que um ambiente de producao suba silenciosamente com o secret
        de desenvolvimento. Em development nada muda — o default continua
        valendo, apenas fica claramente identificado como tal.
        """
        if not self.is_production:
            return self

        if self.secret_key == DEV_SECRET_KEY or not self.secret_key.strip():
            raise ValueError(
                "SECRET_KEY invalida para ENVIRONMENT=production: defina uma chave "
                "propria (ex.: `python -c \"import secrets;print(secrets.token_urlsafe(48))\"`). "
                "O valor de desenvolvimento e publico e permitiria forjar JWTs."
            )

        if len(self.secret_key) < MIN_PRODUCTION_SECRET_LENGTH:
            raise ValueError(
                f"SECRET_KEY muito curta para producao: use ao menos "
                f"{MIN_PRODUCTION_SECRET_LENGTH} caracteres."
            )

        return self

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _cors_lista(cls, value):
        """
        Aceita "https://a.com, https://b.com" alem da lista JSON.

        Sem isto, `CORS_ORIGINS=https://painel.exemplo.com` no .env explodiria
        com erro de JSON invalido — e o jeito de escrever que falha e
        justamente o mais natural.
        """
        if isinstance(value, str):
            texto = value.strip()
            if not texto:
                return []

            # JSON e resolvido AQUI, e nao delegado ao pydantic: vindo de
            # variavel de ambiente o pydantic-settings ja o decodifica antes,
            # mas passado como argumento (testes, uso programatico) nao — e a
            # mesma string se comportaria de dois jeitos diferentes.
            if texto.startswith("["):
                import json

                try:
                    decodificado = json.loads(texto)
                except json.JSONDecodeError:
                    raise ValueError(
                        f"CORS_ORIGINS parece JSON mas nao e valido: {texto!r}. "
                        "Use JSON correto ou uma lista separada por virgulas."
                    ) from None
                return decodificado

            return [item.strip() for item in texto.split(",") if item.strip()]
        return value

    @model_validator(mode="after")
    def _validate_production_cors(self) -> "Settings":
        """
        Producao exige origens proprias e explicitas (Fase 10).

        Tres recusas, todas por motivos distintos:

        - lista vazia: nenhum navegador conseguiria usar o painel, e o
          sintoma (erro de CORS no console do usuario) nao aponta para a
          causa. Melhor falhar no boot, onde a mensagem e clara.
        - "*": com o backend exposto publicamente, qualquer pagina da
          internet passaria a poder chamar a API com o token da vitima.
        - localhost: nao e teoria — significa que o .env de producao e uma
          copia do de desenvolvimento, e entao PROVAVELMENTE ha mais coisa
          errada nele. Alem disso, uma pagina rodando na maquina de alguem
          poderia falar com a API de producao.
        """
        if not self.is_production:
            return self

        origens = [o.strip() for o in self.cors_origins if str(o).strip()]

        if not origens:
            raise ValueError(
                "CORS_ORIGINS vazio com ENVIRONMENT=production: defina a(s) origem(ns) "
                "HTTPS do painel (ex.: CORS_ORIGINS=https://painel.vercel.app). "
                "Sem isso o navegador bloqueia toda chamada do frontend."
            )

        if any(o == "*" for o in origens):
            raise ValueError(
                "CORS_ORIGINS='*' e proibido com ENVIRONMENT=production: com o backend "
                "exposto publicamente, qualquer site poderia chamar a API usando o token "
                "de quem estivesse logado. Liste as origens explicitamente."
            )

        locais = [o for o in origens if "localhost" in o or "127.0.0.1" in o]
        if locais:
            raise ValueError(
                f"CORS_ORIGINS contem origem local {locais!r} com ENVIRONMENT=production. "
                "Isso normalmente indica um .env de desenvolvimento copiado para o "
                "servidor — reveja o arquivo inteiro, nao apenas esta variavel."
            )

        inseguras = [o for o in origens if not o.startswith("https://")]
        if inseguras:
            raise ValueError(
                f"CORS_ORIGINS contem origem sem HTTPS {inseguras!r} com "
                "ENVIRONMENT=production: o token trafega no header Authorization e "
                "seria exposto em transito."
            )

        return self

    @field_validator("database_url")
    @classmethod
    def _absolute_sqlite_path(cls, value: str) -> str:
        """
        Normaliza um DATABASE_URL sqlite relativo (ex.: sqlite:///./x.db) para
        um caminho absoluto sob backend/, para que o banco seja sempre o mesmo
        arquivo, nao importa o cwd de quem iniciou o servidor.
        """
        prefix = "sqlite:///"
        if not value.startswith(prefix):
            return value

        raw = value[len(prefix) :]
        if not raw or raw.startswith("/"):  # ":memory:" ou ja absoluto no POSIX
            return value

        path = Path(raw)
        if path.is_absolute():
            return value

        return f"{prefix}{(BACKEND_DIR / path).resolve().as_posix()}"

    @property
    def collection_printer_id_list(self) -> list[int]:
        return [int(p) for p in self.collection_printer_ids.split(",") if p.strip()]

    # API
    api_prefix: str = "/api"

    # ------------------------------------------------------------------
    # CORS (Fase 10) — lista EXPLICITA de origens do painel.
    #
    # O default cobre o desenvolvimento local. Em producao ele nao serve e
    # o backend recusa subir com ele: ver _validate_production_cors. A lista
    # aceita tanto JSON (pydantic-settings) quanto valores separados por
    # virgula no .env, que e como uma pessoa naturalmente escreve.
    # ------------------------------------------------------------------
    # NoDecode desliga a decodificacao automatica de JSON que o
    # pydantic-settings aplica a campos de tipo complexo vindos do ambiente.
    # Sem ele, `CORS_ORIGINS=https://painel.vercel.app` — a forma natural de
    # escrever — nem chega ao validador: explode antes, com erro de JSON.
    # Com NoDecode o valor chega cru e _cors_lista trata os dois formatos.
    cors_origins: Annotated[list[str], NoDecode] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ]

    # ------------------------------------------------------------------
    # Logs (Fase 10)
    #
    # Rodando como tarefa agendada do Windows, ninguem le stdout: sem
    # arquivo, um erro de madrugada nao deixa rastro. O nivel cai para
    # WARNING em producao apenas se explicitado; o padrao INFO registra o
    # ciclo de coleta, que e o que se quer auditar.
    # ------------------------------------------------------------------
    log_level: str = "INFO"
    #: Vazio = so console. Caminho relativo e resolvido sob backend/.
    log_file: str = "logs/printercontrol.log"
    log_max_bytes: int = 5 * 1024 * 1024
    log_backup_count: int = 10

    class Config:
        # Caminho absoluto pelo mesmo motivo do database_url: um `.env`
        # relativo so seria encontrado se o servidor fosse iniciado de dentro
        # de backend/, e o resto das configuracoes cairia silenciosamente no
        # default (scheduler desligado, mock bloqueado...).
        env_file = str(BACKEND_DIR / ".env")
        case_sensitive = False


settings = Settings()
