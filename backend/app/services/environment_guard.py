"""
Guarda de ambiente (Fase 9) — impede simulacao em producao.

Complementa, e nao substitui, o fail-fast de `config.py`. Sao camadas com
alcances diferentes:

    config.py   -> recusa SUBIR quando a configuracao GLOBAL e simulada
                   (PRINT_SERVER_MODE != real, ALLOW_MOCK_COLLECT=true).
    este modulo -> recusa a REQUISICAO que pede simulacao em tempo de
                   execucao.

A segunda camada existe porque a primeira nao alcanca o modo POR SERVIDOR da
Fase 4: um Print Server gravado com mode="mock" antes de a instancia virar
producao continua no banco, e nenhuma validacao de boot o enxerga. Sem esta
guarda, um "Sincronizar" nesse servidor publicaria a frota ficticia e
desativaria as impressoras reais ausentes dela.

409 (Conflict), e nao 403: nao e falta de permissao — nem um admin pode fazer
isso, e apresentar como permissao sugeriria, falsamente, que outra conta
poderia. O conflito e com o estado do ambiente, e a mensagem diz qual.
"""
from fastapi import HTTPException, status

from app.config import settings


def bloquear_mock_em_producao(operacao: str, detalhe: str = "") -> None:
    """
    Levanta 409 quando uma operacao simulada e pedida em producao.

    `operacao` entra na mensagem para que o log e a interface digam O QUE foi
    recusado, em vez de um "nao permitido" generico que obrigaria quem opera a
    adivinhar a origem.
    """
    if not settings.is_production:
        return

    sufixo = f" {detalhe}" if detalhe else ""
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=(
            f"{operacao} esta bloqueada em ENVIRONMENT=production: dado "
            f"ficticio gravado no banco de producao e indistinguivel de dado "
            f"real depois." + sufixo
        ),
    )
