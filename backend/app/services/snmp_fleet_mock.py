"""
Simulador de frota — APENAS PARA TESTE LOCAL.

Diferenca para snmp_mock.py: la cada cenario e um resultado FIXO, igual para
qualquer impressora e igual em toda coleta. Aqui cada impressora tem um perfil
proprio, derivado do seu id, e o contador CRESCE de uma coleta para a outra
(recebe o valor anterior e soma um incremento deterministico).

Determinismo: o mesmo id sempre produz o mesmo perfil e o mesmo incremento, de
modo que duas execucoes da suite dao o mesmo resultado. Nada e aleatorio.
"""
from app.services.snmp import SNMPResult, TonerInfo

# Perfis distribuidos por (printer_id % 20) — proporcoes pensadas para uma
# frota plausivel: a maioria saudavel, alguns com toner baixo, poucos fora.
OFFLINE_BUCKETS = {0, 7}          # ~10% fora do ar
SNMP_MUDO_BUCKETS = {13}          # ~5% respondem ping mas nao SNMP
CRITICO_BUCKETS = {3}             # ~5% toner critico (<=10%)
BAIXO_BUCKETS = {5, 11}           # ~10% toner baixo (<=20%)

TONER_LABELS = {"K": "Preto", "C": "Ciano", "M": "Magenta", "Y": "Amarelo"}


def _toner(color: str, percent: int, index: int) -> TonerInfo:
    return TonerInfo(
        color=color,
        percent=max(0, min(100, percent)),  # nunca sai de 0-100
        index=index,
        maximum=10000,
        description=f"{color} Toner (frota simulada)",
    )


def profile_for(printer_id: int) -> str:
    """Perfil deterministico da impressora: online | offline | snmp_mudo | baixo | critico."""
    bucket = printer_id % 20
    if bucket in OFFLINE_BUCKETS:
        return "offline"
    if bucket in SNMP_MUDO_BUCKETS:
        return "snmp_mudo"
    if bucket in CRITICO_BUCKETS:
        return "critico"
    if bucket in BAIXO_BUCKETS:
        return "baixo"
    return "online"


def _base_page_count(printer_id: int) -> int:
    """Contador inicial plausivel para uma impressora que nunca foi lida."""
    return 1200 + (printer_id * 787) % 90000


def _increment(printer_id: int) -> int:
    """Paginas impressas entre duas coletas — fixo por impressora, 5 a 124."""
    return 5 + (printer_id * 37) % 120


def _toner_percent(printer_id: int, profile: str, color: str) -> int:
    """
    Nivel do toner: base do perfil + desvio deterministico por impressora/cor,
    sempre dentro da faixa que o perfil promete.
    """
    spread = (printer_id * 13 + ord(color)) % 7  # 0..6
    if profile == "critico":
        return 3 + spread % 6          # 3..8   -> <=10, dispara alerta (alert_engine.TONER_ALERT_THRESHOLD)
    if profile == "baixo":
        return 12 + spread % 8         # 12..19 -> acima do limiar, nao dispara nada
    return 35 + (printer_id * 17 + ord(color)) % 60  # 35..94, saudavel


class FleetMockClient:
    """
    Substituto do SNMPClient com a mesma assinatura de collect().

    Args:
        printer_id: define o perfil e o incremento (determinismo).
        previous_page_count: contador da ultima leitura; None se nunca lida.
        simulate_reset: forca contador reiniciado (troca de placa/formatador).
    """

    def __init__(
        self,
        printer_id: int,
        previous_page_count: int | None = None,
        simulate_reset: bool = False,
    ):
        self.printer_id = printer_id
        self.previous_page_count = previous_page_count
        self.simulate_reset = simulate_reset

    def collect(self, ip: str, is_color: bool = False) -> SNMPResult:
        profile = profile_for(self.printer_id)

        if profile == "offline":
            return SNMPResult(
                status="offline",
                page_count=None,
                toners=[],
                uptime="N/A",
                reachable=False,
                snmp_responded=False,
                error="sem resposta ao ping (frota simulada)",
            )

        if profile == "snmp_mudo":
            return SNMPResult(
                status="online",
                page_count=None,
                toners=[],
                uptime="N/A",
                reachable=True,
                snmp_responded=False,
                error="SNMP sem resposta (frota simulada)",
            )

        # Contador SEMPRE crescente, exceto num reset explicito.
        if self.simulate_reset:
            page_count = _increment(self.printer_id)
        elif self.previous_page_count is None:
            page_count = _base_page_count(self.printer_id)
        else:
            page_count = self.previous_page_count + _increment(self.printer_id)

        colors = ["C", "M", "Y", "K"] if is_color else ["K"]
        toners = [
            _toner(color, _toner_percent(self.printer_id, profile, color), index + 1)
            for index, color in enumerate(colors)
        ]

        status = "atencao" if profile in ("baixo", "critico") else "online"
        return SNMPResult(
            status=status,
            page_count=page_count,
            toners=toners,
            uptime=f"{10 + self.printer_id % 200}d, {self.printer_id % 24}h, {self.printer_id % 60}m",
            reachable=True,
            snmp_responded=True,
        )
