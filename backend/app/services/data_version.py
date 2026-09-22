"""
Versao dos dados da frota: sobe a cada leitura nova gravada (22/09/2026).

O painel pergunta GET /api/updates/version a cada poucos segundos — resposta
de poucos bytes — e so recarrega a frota, os alertas e o relatorio mensal
quando o numero muda. Assim a tela reage em segundos a uma folha impressa
sem baixar tudo de novo o tempo inteiro.

Em memoria de proposito: reiniciar o backend zera o contador, o painel ve um
numero diferente do ultimo e recarrega uma vez — que e exatamente o certo
depois de um reinicio.
"""
import threading
from datetime import datetime, timezone

_trava = threading.Lock()
_versao = 0
_alterado_em = datetime.now(timezone.utc)


def bump() -> int:
    """Marca que ha dado novo. Devolve a versao nova."""
    global _versao, _alterado_em
    with _trava:
        _versao += 1
        _alterado_em = datetime.now(timezone.utc)
        return _versao


def current() -> tuple[int, datetime]:
    with _trava:
        return _versao, _alterado_em
