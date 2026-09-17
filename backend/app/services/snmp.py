"""
SNMP Collector para impressoras.

Porte direto da funcao Get-TonerSNMP de scripts/Coletar-Impressoras.ps1.
Mantem os mesmos OIDs, a mesma ordem GetBulk -> fallback GET individual,
os mesmos filtros de consumivel e a mesma regra de escolha de toner.
"""
import itertools
import platform
import random
import re
import socket
import subprocess
from dataclasses import dataclass, field
from typing import Optional

# Tags BER usadas nas respostas SNMP
TAG_INTEGER = 0x02
TAG_OCTET_STRING = 0x04
TAG_NULL = 0x05
TAG_OID = 0x06
TAG_SEQUENCE = 0x30
TAG_COUNTER32 = 0x41
TAG_GAUGE32 = 0x42
TAG_TIMETICKS = 0x43
TAG_COUNTER64 = 0x46

# Tipos numericos aceitos ao ler um valor inteiro (PS1: Parse-SnmpInt/Counter)
NUMERIC_TAGS = (TAG_INTEGER, TAG_COUNTER32, TAG_GAUGE32, TAG_TIMETICKS, TAG_COUNTER64)

# Excecoes SNMPv2: noSuchObject / noSuchInstance / endOfMibView
EXCEPTION_TAGS = (0x80, 0x81, 0x82)

# Consumiveis que nao sao toner (PS1: waste|descarte|lixeira|recovery|container|cleaner)
IGNORE_SUPPLY_RE = re.compile(r"waste|descarte|lixeira|recovery|container|cleaner", re.I)

# Deteccao de cor pela descricao (PS1: mesmos regex, com \b)
COLOR_PATTERNS = (
    ("C", re.compile(r"cyan|ciano|azul|\bc\b", re.I)),
    ("M", re.compile(r"magenta|rosa|\bm\b", re.I)),
    ("Y", re.compile(r"yellow|amarelo|\by\b", re.I)),
    ("K", re.compile(r"black|preto|negro|\bk\b", re.I)),
)

# Ordem de exibicao dos toners coloridos (PS1: pesos Ciano=1, Magenta=2, Amarelo=3, Preto=4)
COLOR_ORDER = {"C": 1, "M": 2, "Y": 3, "K": 4}

# Fallback por indice quando a descricao nao identifica a cor (PS1: $indice % 4)
INDEX_COLOR_FALLBACK = {1: "C", 2: "M", 3: "Y", 0: "K"}

# HOST-RESOURCES-MIB (RFC 2790)
DEVICE_STATUS = {1: "unknown", 2: "running", 3: "warning", 4: "testing", 5: "down"}
PRINTER_STATE = {1: "other", 2: "unknown", 3: "idle", 4: "printing", 5: "warmup"}

# hrPrinterDetectedErrorState: bit 0 e o mais significativo do 1o octeto (bits 8-14 da RFC 3805).
ERROR_STATE_BITS = (
    "lowPaper", "noPaper", "lowToner", "noToner", "doorOpen", "jammed", "offline",
    "serviceRequested", "inputTrayMissing", "outputTrayMissing", "markerSupplyMissing",
    "outputNearFull", "outputFull", "inputTrayEmpty", "overduePreventMaint",
)

# Fora daqui ficam so avisos: inputTrayEmpty, por exemplo, fica ligado com a bandeja manual vazia.
ATTENTION_ERROR_STATES = frozenset({
    "noPaper", "noToner", "doorOpen", "jammed", "offline", "serviceRequested",
    "inputTrayMissing", "outputTrayMissing", "markerSupplyMissing", "outputFull",
})

# Printer-MIB: -1 other, -2 unknown, -3 "ha pelo menos uma unidade".
PRINTER_MIB_SPECIAL_VALUES = (-1, -2, -3)

MAX_TEXT_LENGTH = 255

# Etiquetadoras/portateis: nao expoem Printer-MIB utilizavel (toner vira ribbon, contador sem sentido)
# (PS1: $modelo -notmatch 'TT042|Honeywell' -and $p.Name -notmatch 'TT042|Honeywell|Etiqueta|Elgin')
LABEL_RE = re.compile(r"TT042|Honeywell|Etiqueta|Zebra|Argox|Sewoo|RP4f", re.I)


@dataclass
class TonerInfo:
    """Nivel de um consumivel de toner."""

    color: str  # K, C, M, Y
    percent: int  # 0-100
    index: int  # indice na tabela prtMarkerSupplies
    maximum: int = 0  # capacidade total (usado para escolher o toner principal)
    description: str = ""


@dataclass
class PaperTrayInfo:
    """Bandeja de papel (prtInputTable)."""

    index: int
    name: str
    level: int  # -3 ha papel, -2 desconhecido, -1 outro
    max_capacity: int


@dataclass
class SNMPResult:
    """
    Resultado de uma coleta SNMP.

    Distingue os tres cenarios de falha exigidos pela Etapa 6:

      reachable=False                      -> impressora offline (sem resposta ao ping nem ao SNMP)
      reachable=True, snmp_responded=False -> responde ping, mas SNMP mudo
      reachable=True, snmp_responded=True  -> SNMP respondeu (dados podem vir parciais)
    """

    status: str  # online | atencao | offline
    page_count: Optional[int] = None
    toners: list[TonerInfo] = field(default_factory=list)
    uptime: str = "N/A"
    reachable: bool = True
    snmp_responded: bool = False
    error: Optional[str] = None
    status_reason: Optional[str] = None
    sys_description: Optional[str] = None
    sys_name: Optional[str] = None
    sys_location: Optional[str] = None
    device_model: Optional[str] = None
    serial_number: Optional[str] = None
    device_status: Optional[str] = None
    printer_state: Optional[str] = None
    error_states: list[str] = field(default_factory=list)
    display_text: Optional[str] = None
    paper_trays: list[PaperTrayInfo] = field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
#  Decodificacao BER
# ─────────────────────────────────────────────────────────────────────────────
def _read_tlv(data: bytes, pos: int) -> tuple[int, int, int, int]:
    """Le um TLV BER. Retorna (tag, length, value_start, next_pos)."""
    if pos + 2 > len(data):
        raise ValueError("TLV truncado")
    tag = data[pos]
    pos += 1
    length = data[pos]
    pos += 1
    if length & 0x80:  # forma longa
        n = length & 0x7F
        if pos + n > len(data):
            raise ValueError("comprimento BER truncado")
        length = 0
        for _ in range(n):
            length = (length << 8) | data[pos]
            pos += 1
    if pos + length > len(data):
        raise ValueError("valor BER truncado")
    return tag, length, pos, pos + length


def _read_oid(data: bytes, pos: int, length: int) -> str:
    """Decodifica um OID BER para notacao pontuada."""
    end = pos + length
    first = data[pos]
    pos += 1
    parts = [str(first // 40), str(first % 40)]
    while pos < end:
        val = 0
        while pos < end:
            b = data[pos]
            pos += 1
            val = (val << 7) | (b & 0x7F)
            if not (b & 0x80):
                break
        parts.append(str(val))
    return ".".join(parts)


def _read_uint(data: bytes) -> int:
    """Decodifica bytes BER como inteiro sem sinal."""
    val = 0
    for b in data:
        val = (val << 8) | b
    return val


def _read_printer_mib_int(data: bytes) -> int:
    """
    INTEGER da Printer-MIB: preserva os valores especiais -1/-2/-3 e le o
    resto sem sinal, para nao negativar agente que omite o octeto de sinal.
    """
    signed = int.from_bytes(data, "big", signed=True) if data else 0
    return signed if signed in PRINTER_MIB_SPECIAL_VALUES else _read_uint(data)


def decode_error_state(raw: bytes) -> list[str]:
    """Codigos ligados em hrPrinterDetectedErrorState, na ordem da RFC."""
    return [
        name
        for bit, name in enumerate(ERROR_STATE_BITS)
        if bit // 8 < len(raw) and raw[bit // 8] & (0x80 >> (bit % 8))
    ]


def _clean_text(raw: bytes) -> str:
    return raw.decode("ascii", errors="ignore").replace("\x00", "").strip()[:MAX_TEXT_LENGTH]


def parse_response(data: bytes) -> tuple[int, list[tuple[str, int, bytes]]]:
    """
    Extrai o request-id e a lista de varbinds de uma resposta SNMP.

    Percorre a estrutura completa (SEQUENCE > version, community, PDU >
    request-id, error-status, error-index, varbind-list) em vez de varrer
    bytes soltos — a varredura ingenua casava com o campo `version` e com a
    community string antes de chegar no valor real.

    Retorna (request_id, [(oid, tag_do_valor, bytes_do_valor)]).
    """
    _tag, _len, outer_start, _next = _read_tlv(data, 0)
    pos = outer_start

    _t, _l, _vs, pos = _read_tlv(data, pos)  # version
    _t, _l, _vs, pos = _read_tlv(data, pos)  # community

    _pdu_tag, _pdu_len, pdu_start, _pdu_next = _read_tlv(data, pos)  # PDU
    pos = pdu_start

    _t, rid_len, rid_start, pos = _read_tlv(data, pos)  # request-id
    request_id = int.from_bytes(data[rid_start : rid_start + rid_len], "big", signed=True)
    _t, _l, _vs, pos = _read_tlv(data, pos)  # error-status
    _t, _l, _vs, pos = _read_tlv(data, pos)  # error-index

    _vb_tag, _vb_len, vb_start, vb_end = _read_tlv(data, pos)  # varbind list

    varbinds: list[tuple[str, int, bytes]] = []
    pos = vb_start
    while pos < vb_end:
        _t, _l, inner, next_vb = _read_tlv(data, pos)  # varbind
        _ot, oid_len, oid_start, after_oid = _read_tlv(data, inner)
        oid = _read_oid(data, oid_start, oid_len)
        val_tag, val_len, val_start, _after_val = _read_tlv(data, after_oid)
        varbinds.append((oid, val_tag, data[val_start : val_start + val_len]))
        pos = next_vb
    return request_id, varbinds


def parse_varbinds(data: bytes) -> list[tuple[str, int, bytes]]:
    """Varbinds de uma resposta SNMP: [(oid, tag_do_valor, bytes_do_valor)]."""
    return parse_response(data)[1]


class SNMPClient:
    """Cliente SNMP para coleta de impressoras (Printer-MIB, RFC 3805)."""

    # OIDs — identicos aos do Coletar-Impressoras.ps1
    OID_UPTIME = "1.3.6.1.2.1.1.3.0"  # sysUpTime
    OID_PAGE_COUNT = "1.3.6.1.2.1.43.10.2.1.4.1.1"  # prtMarkerLifeCount
    OID_TONER_LEVEL = "1.3.6.1.2.1.43.11.1.1.9.1"  # prtMarkerSuppliesLevel
    OID_TONER_MAX = "1.3.6.1.2.1.43.11.1.1.8.1"  # prtMarkerSuppliesMaxCapacity
    OID_TONER_DESC = "1.3.6.1.2.1.43.11.1.1.6.1"  # prtMarkerSuppliesDescription

    OID_SYS_DESCR = "1.3.6.1.2.1.1.1.0"
    OID_SYS_NAME = "1.3.6.1.2.1.1.5.0"
    OID_SYS_LOCATION = "1.3.6.1.2.1.1.6.0"
    OID_HR_DEVICE_DESCR = "1.3.6.1.2.1.25.3.2.1.3"  # .hrDeviceIndex
    OID_HR_DEVICE_STATUS = "1.3.6.1.2.1.25.3.2.1.5"  # .hrDeviceIndex
    OID_HR_PRINTER_STATUS = "1.3.6.1.2.1.25.3.5.1.1"  # .hrDeviceIndex
    OID_HR_PRINTER_ERRORS = "1.3.6.1.2.1.25.3.5.1.2"  # .hrDeviceIndex
    OID_SERIAL_NUMBER = "1.3.6.1.2.1.43.5.1.1.17"  # prtGeneralSerialNumber.hrDeviceIndex
    OID_CONSOLE_TEXT = "1.3.6.1.2.1.43.16.5.1.2"  # prtConsoleDisplayBufferText.hrDeviceIndex.linha
    OID_INPUT_MAX = "1.3.6.1.2.1.43.8.2.1.9"  # prtInputMaxCapacity.hrDeviceIndex.bandeja
    OID_INPUT_LEVEL = "1.3.6.1.2.1.43.8.2.1.10"  # prtInputCurrentLevel.hrDeviceIndex.bandeja
    OID_INPUT_NAME = "1.3.6.1.2.1.43.8.2.1.13"  # prtInputName.hrDeviceIndex.bandeja

    TONER_LOW_THRESHOLD = 20  # PS1: $piorPct -le 20 -> "atencao"
    MAX_SUPPLY_INDEX = 20  # PS1: foreach ($indice in 1..20)
    MAX_CONSECUTIVE_FAILS = 3  # PS1: if ($falhasConsecutivas -ge 3) { break }
    BULK_MAX_REPETITIONS = 15  # PS1: -MaxRepetitions 15
    MAX_PAPER_TRAYS = 10
    MAX_DISPLAY_LINES = 4

    PDU_GET = 0xA0
    PDU_GETNEXT = 0xA1

    def __init__(
        self, community: str = "public", timeout: float = 1.5, ping_timeout_ms: int = 400, retries: int = 1
    ):
        self.community = community
        self.timeout = timeout
        self.ping_timeout_ms = ping_timeout_ms
        # Fase 17: SNMP_RETRIES existia em config.py mas nada usava — cada
        # troca era feita uma unica vez. UDP nao garante entrega; um pacote
        # perdido virava "sem resposta" mesmo com a impressora saudavel.
        # Ver _exchange() para onde isto de fato reenvia.
        self.retries = max(0, retries)
        self.port = 161
        self._request_ids = itertools.count(random.randint(1, 0x3FFFFFFF))
        self._snmp_answered = False
        self._last_network_error: str | None = None

    # ─────────────────────────────────────────────────────────────────────
    #  Fluxo principal
    # ─────────────────────────────────────────────────────────────────────
    def collect(self, ip: str, is_color: bool = False) -> SNMPResult:
        """
        Coleta status, contador de paginas, toners e o estado do equipamento.

        Nunca levanta excecao: qualquer falha vira um SNMPResult descrevendo
        o que aconteceu, para que a coleta das demais impressoras continue.
        """
        self._last_network_error = None
        self._snmp_answered = False

        if not ip or not self._is_ip_like(ip):
            return SNMPResult(
                status="offline",
                reachable=False,
                error=f"IP invalido ou ausente: {ip!r}",
                status_reason="invalid_or_missing_ip",
            )

        # Sem ping o SNMP ainda e tentado: rede que filtra ICMP e libera UDP/161 nao pode virar "offline".
        ping_ok = self._ping(ip)

        result = SNMPResult(status="online", reachable=True)
        sock: socket.socket | None = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.timeout)

            uptime_ticks = self._probe_uptime(sock, ip, retry=ping_ok)
            if uptime_ticks is not None:
                result.snmp_responded = True
                result.uptime = self._format_uptime(uptime_ticks)

            label_device = False
            # Agente que nao respondeu nem o sysUpTime nao responde o resto: evita um timeout por OID.
            if self._snmp_answered:
                self._collect_device_info(sock, ip, result)
                # Vale o que o equipamento diz ser, nao o cadastro: ha etiquetadora cadastrada como laser.
                label_device = self._is_label_device(result)

                if not label_device:
                    page_count = self._get_numeric(sock, ip, self.OID_PAGE_COUNT)
                    if page_count is not None:
                        result.snmp_responded = True
                        result.page_count = page_count

                    candidates, toners_responded = self._collect_supplies(sock, ip, is_color)
                    if toners_responded:
                        result.snmp_responded = True
                    result.toners = self._select_toners(candidates, is_color)

            if label_device:
                result.error = "etiquetadora identificada pelo SNMP: toner e contador nao se aplicam"
                result.status_reason = "snmp_not_applicable"
            elif not result.snmp_responded:
                result.error = "SNMP sem resposta (impressora acessivel, porta 161 muda)"
                result.status_reason = self._last_network_error or "ping_ok_snmp_not_responding"
            elif result.page_count is None and not result.toners:
                result.error = "SNMP respondeu, mas sem contador nem toner disponiveis"
                result.status_reason = "snmp_partial_data"
            elif result.page_count is None:
                result.status_reason = "snmp_without_page_count"
            elif not result.toners:
                result.status_reason = "snmp_partial_data"
            else:
                result.status_reason = "snmp_data_available"

        except Exception as exc:  # nunca propaga para nao derrubar a coleta em lote
            result.error = f"{type(exc).__name__}: {exc}"
            result.status_reason = "snmp_socket_error" if isinstance(exc, OSError) else "snmp_error"
        finally:
            if sock is not None:
                sock.close()

        if not ping_ok and not self._snmp_answered:
            return SNMPResult(
                status="offline",
                reachable=False,
                error="sem resposta ao ping nem ao SNMP (UDP/161)",
                status_reason="ping_failed",
            )

        result.status = self._status_for(result)
        return result

    def check_connectivity(self, ip: str) -> SNMPResult:
        """
        So conectividade, para etiquetadoras/portateis sem Printer-MIB.

        Quando o ping falha, um GET de sysUpTime decide, pelo mesmo motivo de collect().
        """
        self._last_network_error = None
        self._snmp_answered = False
        if not ip or not self._is_ip_like(ip):
            return SNMPResult(
                status="offline",
                reachable=False,
                error=f"IP invalido ou ausente: {ip!r}",
                status_reason="invalid_or_missing_ip",
            )

        aviso = "etiquetadora/portatil: SNMP de impressora nao consultado"
        if self._ping(ip):
            return SNMPResult(status="online", reachable=True, error=aviso)

        uptime = "N/A"
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.settimeout(self.timeout)
                ticks = self._probe_uptime(sock, ip, retry=False)
                if ticks is not None:
                    uptime = self._format_uptime(ticks)
        except OSError:
            pass

        if self._snmp_answered:
            return SNMPResult(status="online", reachable=True, uptime=uptime, error=aviso)
        return SNMPResult(
            status="offline",
            reachable=False,
            error="sem resposta ao ping nem ao SNMP (UDP/161)",
            status_reason="ping_failed",
        )

    def _probe_uptime(self, sock: socket.socket, ip: str, retry: bool) -> Optional[int]:
        """sysUpTime, o primeiro OID de toda coleta. Sem retry quando o ping ja falhou: host fora do ar custa um timeout so."""
        retries = self.retries
        if not retry:
            self.retries = 0
        try:
            return self._get_numeric(sock, ip, self.OID_UPTIME)
        finally:
            self.retries = retries

    @staticmethod
    def _is_label_device(result: SNMPResult) -> bool:
        return bool(LABEL_RE.search(result.device_model or "") or LABEL_RE.search(result.sys_description or ""))

    def _status_for(self, result: SNMPResult) -> str:
        if result.toners and min(t.percent for t in result.toners) <= self.TONER_LOW_THRESHOLD:
            return "atencao"
        if result.device_status == "down" or ATTENTION_ERROR_STATES.intersection(result.error_states):
            return "atencao"
        return "online"

    # ─────────────────────────────────────────────────────────────────────
    #  Conectividade
    # ─────────────────────────────────────────────────────────────────────
    @staticmethod
    def _is_ip_like(ip: str) -> bool:
        """PS1: `if ($ip -match '^\\d')` — descarta 'N/A' e nomes de porta."""
        return bool(re.match(r"^\d", ip.strip()))

    def _ping(self, ip: str) -> bool:
        """
        ICMP ping, equivalente ao `New-Object ...Ping).Send($ip, 400)` do PS1.

        SNMP roda em UDP/161; abrir um socket TCP nessa porta (implementacao
        anterior) falharia mesmo em impressora saudavel.
        """
        system = platform.system().lower()
        if system == "windows":
            cmd = ["ping", "-n", "1", "-w", str(self.ping_timeout_ms), ip]
        else:
            secs = max(1, round(self.ping_timeout_ms / 1000))
            cmd = ["ping", "-c", "1", "-W", str(secs), ip]

        kwargs = {"capture_output": True, "timeout": (self.ping_timeout_ms / 1000) + 3}
        if system == "windows" and hasattr(subprocess, "CREATE_NO_WINDOW"):
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

        try:
            return subprocess.run(cmd, **kwargs).returncode == 0
        except Exception:
            return False

    # ─────────────────────────────────────────────────────────────────────
    #  Toners: GetBulk com fallback para GET individual (ordem do PS1)
    # ─────────────────────────────────────────────────────────────────────
    def _collect_supplies(
        self, sock: socket.socket, ip: str, is_color: bool
    ) -> tuple[list[TonerInfo], bool]:
        """Retorna (candidatos, houve_resposta_snmp)."""
        candidates = self._supplies_via_bulk(sock, ip, is_color)
        if candidates:
            return candidates, True

        candidates, responded = self._supplies_via_get(sock, ip, is_color)
        return candidates, responded

    def _supplies_via_bulk(
        self, sock: socket.socket, ip: str, is_color: bool
    ) -> list[TonerInfo]:
        """GETBULK das tres colunas de uma vez (PS1: Build-SnmpGetBulk)."""
        try:
            request_id = self._next_request_id()
            packet = self._build_getbulk(
                [self.OID_TONER_LEVEL, self.OID_TONER_MAX, self.OID_TONER_DESC],
                self.BULK_MAX_REPETITIONS,
                request_id,
            )
            response = self._exchange(sock, ip, packet, request_id)
            if not response:
                return []
            varbinds = parse_varbinds(response)
        except Exception:
            return []

        # PS1: exige grupos completos de 3 (nivel, maximo, descricao)
        if len(varbinds) < 3 or len(varbinds) % 3 != 0:
            return []

        candidates: list[TonerInfo] = []
        for i in range(0, len(varbinds), 3):
            level_vb, max_vb, desc_vb = varbinds[i], varbinds[i + 1], varbinds[i + 2]

            # Saiu das colunas pedidas -> fim da tabela
            if not level_vb[0].startswith(self.OID_TONER_LEVEL + ".") or not max_vb[
                0
            ].startswith(self.OID_TONER_MAX + "."):
                break
            if level_vb[1] in EXCEPTION_TAGS or max_vb[1] in EXCEPTION_TAGS:
                break

            try:
                index = int(level_vb[0][len(self.OID_TONER_LEVEL) + 1 :])
            except ValueError:
                break

            level = _read_printer_mib_int(level_vb[2])
            maximum = _read_printer_mib_int(max_vb[2])
            desc = ""
            if desc_vb[1] == TAG_OCTET_STRING:
                desc = _clean_text(desc_vb[2])

            toner = self._build_toner(index, level, maximum, desc, is_color)
            if toner is not None:
                candidates.append(toner)

        return candidates

    def _supplies_via_get(
        self, sock: socket.socket, ip: str, is_color: bool
    ) -> tuple[list[TonerInfo], bool]:
        """Fallback: um GET por indice (PS1: laco 1..20 com 3 falhas seguidas)."""
        candidates: list[TonerInfo] = []
        consecutive_fails = 0
        responded = False

        for index in range(1, self.MAX_SUPPLY_INDEX + 1):
            level = self._get_printer_mib_int(sock, ip, f"{self.OID_TONER_LEVEL}.{index}")
            maximum = self._get_printer_mib_int(sock, ip, f"{self.OID_TONER_MAX}.{index}")

            if level is not None or maximum is not None:
                responded = True

            if level is None or maximum is None or maximum <= 0:
                consecutive_fails += 1
                if consecutive_fails >= self.MAX_CONSECUTIVE_FAILS:
                    break
                continue

            consecutive_fails = 0
            desc = self._get_string(sock, ip, f"{self.OID_TONER_DESC}.{index}") or ""

            toner = self._build_toner(index, level, maximum, desc, is_color)
            if toner is not None:
                candidates.append(toner)

            # PS1: mono para no 1o toner; colorida para em 8 candidatos
            if not is_color and candidates:
                break
            if is_color and len(candidates) >= 8:
                break

        return candidates, responded

    def _build_toner(
        self, index: int, level: int, maximum: int, desc: str, is_color: bool
    ) -> Optional[TonerInfo]:
        """Aplica os filtros do PS1 e monta um candidato a toner."""
        if maximum <= 0:
            return None
        # -3 ("ha toner") e -2 ("desconhecido") nao sao nivel mensuravel.
        if level < 0:
            return None
        if IGNORE_SUPPLY_RE.search(desc):
            return None
        percent = max(0, min(100, round((level / maximum) * 100)))
        return TonerInfo(
            color=self._detect_color(desc, index, is_color),
            percent=percent,
            index=index,
            maximum=maximum,
            description=desc,
        )

    def _select_toners(self, candidates: list[TonerInfo], is_color: bool) -> list[TonerInfo]:
        """
        Escolhe os toners finais.

        PS1 colorida: um por cor (primeiro de cada grupo), ordem C, M, Y, K.
        PS1 mono: apenas o de maior capacidade — evita devolver o kit de
        manutencao no lugar do cartucho principal.

        `is_color` e so um palpite (regex em modelo/nome — ver
        PrinterCollector.is_color_printer). O GETBULK nao e limitado por
        esse palpite e frequentemente encontra as 4 cores mesmo quando a
        impressora foi adivinhada como mono (modelo sem "color" no nome,
        ex.: "Kyocera M5021cdn"). Corrige aqui pela cor de verdade: se os
        proprios candidatos ja trazem mais de uma cor distinta (via
        descricao do consumivel, ex.: "Cyan Toner Cartridge"), trata como
        colorida e mantem todas — em vez de descartar 3 das 4 cores por
        causa de um palpite errado no nome do modelo.
        """
        if not candidates:
            return []

        cores_distintas = {t.color for t in candidates}
        e_colorida_de_verdade = is_color or len(cores_distintas) > 1

        if not e_colorida_de_verdade:
            return [max(candidates, key=lambda t: t.maximum)]

        by_color: dict[str, TonerInfo] = {}
        for toner in candidates:
            by_color.setdefault(toner.color, toner)
        return sorted(by_color.values(), key=lambda t: COLOR_ORDER.get(t.color, 99))

    @staticmethod
    def _detect_color(desc: str, index: int, is_color: bool) -> str:
        """Cor pela descricao; se nao identificar e for colorida, usa indice % 4."""
        for color, pattern in COLOR_PATTERNS:
            if pattern.search(desc):
                return color
        if is_color:
            return INDEX_COLOR_FALLBACK.get(index % 4, "K")
        return "K"

    def _collect_device_info(self, sock: socket.socket, ip: str, result: SNMPResult) -> None:
        """Identificacao, estado e bandejas. Cada OID e opcional: o que o agente nao expoe fica vazio."""
        result.sys_description = self._get_string(sock, ip, self.OID_SYS_DESCR) or None
        result.sys_name = self._get_string(sock, ip, self.OID_SYS_NAME) or None
        result.sys_location = self._get_string(sock, ip, self.OID_SYS_LOCATION) or None

        device_index, printer_status = self._printer_device_index(sock, ip)
        if printer_status is not None:
            result.printer_state = PRINTER_STATE.get(printer_status, "unknown")

        device_status = self._get_numeric(sock, ip, f"{self.OID_HR_DEVICE_STATUS}.{device_index}")
        if device_status is not None:
            result.device_status = DEVICE_STATUS.get(device_status, "unknown")

        errors = self._get_octets(sock, ip, f"{self.OID_HR_PRINTER_ERRORS}.{device_index}")
        if errors is not None:
            result.error_states = decode_error_state(errors)

        result.device_model = self._get_string(sock, ip, f"{self.OID_HR_DEVICE_DESCR}.{device_index}") or None
        result.serial_number = self._get_string(sock, ip, f"{self.OID_SERIAL_NUMBER}.{device_index}") or None
        result.display_text = self._display_text(sock, ip, device_index)
        result.paper_trays = self._paper_trays(sock, ip, device_index)

    def _printer_device_index(self, sock: socket.socket, ip: str) -> tuple[int, Optional[int]]:
        """(hrDeviceIndex da impressora, hrPrinterStatus). Indice 1 quando o agente nao expoe hrPrinterTable."""
        prefix = self.OID_HR_PRINTER_STATUS + "."
        vb = self._get_next(sock, ip, self.OID_HR_PRINTER_STATUS)
        if vb is None or not vb[0].startswith(prefix) or vb[1] not in NUMERIC_TAGS or not vb[2]:
            return 1, None
        suffix = vb[0][len(prefix):]
        if not suffix.isdigit():
            return 1, None
        return int(suffix), _read_uint(vb[2])

    def _display_text(self, sock: socket.socket, ip: str, device_index: int) -> Optional[str]:
        lines = []
        for line in range(1, self.MAX_DISPLAY_LINES + 1):
            text = self._get_string(sock, ip, f"{self.OID_CONSOLE_TEXT}.{device_index}.{line}")
            if text is None:
                break
            if text:
                lines.append(text)
        return " | ".join(lines)[:MAX_TEXT_LENGTH] or None

    def _paper_trays(self, sock: socket.socket, ip: str, device_index: int) -> list[PaperTrayInfo]:
        prefix = f"{self.OID_INPUT_LEVEL}.{device_index}."
        oid = f"{self.OID_INPUT_LEVEL}.{device_index}"
        trays: list[PaperTrayInfo] = []
        for _ in range(self.MAX_PAPER_TRAYS):
            vb = self._get_next(sock, ip, oid)
            if vb is None or not vb[0].startswith(prefix) or vb[1] not in NUMERIC_TAGS:
                break
            suffix = vb[0][len(prefix):]
            if not suffix.isdigit():
                break
            index = int(suffix)
            maximum = self._get_printer_mib_int(sock, ip, f"{self.OID_INPUT_MAX}.{device_index}.{index}")
            name = self._get_string(sock, ip, f"{self.OID_INPUT_NAME}.{device_index}.{index}")
            trays.append(
                PaperTrayInfo(
                    index=index,
                    name=name or f"Bandeja {index}",
                    level=_read_printer_mib_int(vb[2]),
                    max_capacity=-2 if maximum is None else maximum,
                )
            )
            oid = vb[0]
        return trays

    # ─────────────────────────────────────────────────────────────────────
    #  Primitivas SNMP
    # ─────────────────────────────────────────────────────────────────────
    def _get_numeric(self, sock: socket.socket, ip: str, oid: str) -> Optional[int]:
        """GET de um valor numerico (INTEGER, Counter32, Gauge32, TimeTicks)."""
        vb = self._get_varbind(sock, ip, oid)
        if vb is None:
            return None
        _oid, tag, value = vb
        if tag not in NUMERIC_TAGS or not value:
            return None
        return _read_uint(value)

    def _get_printer_mib_int(self, sock: socket.socket, ip: str, oid: str) -> Optional[int]:
        """GET de um INTEGER da Printer-MIB, preservando -1/-2/-3."""
        vb = self._get_varbind(sock, ip, oid)
        if vb is None or vb[1] not in NUMERIC_TAGS or not vb[2]:
            return None
        return _read_printer_mib_int(vb[2])

    def _get_octets(self, sock: socket.socket, ip: str, oid: str) -> Optional[bytes]:
        """GET de uma OCTET STRING, em bytes."""
        vb = self._get_varbind(sock, ip, oid)
        if vb is None or vb[1] != TAG_OCTET_STRING:
            return None
        return vb[2]

    def _get_string(self, sock: socket.socket, ip: str, oid: str) -> Optional[str]:
        """GET de uma OCTET STRING."""
        raw = self._get_octets(sock, ip, oid)
        return None if raw is None else _clean_text(raw)

    def _get_varbind(
        self, sock: socket.socket, ip: str, oid: str
    ) -> Optional[tuple[str, int, bytes]]:
        """Envia um GET e devolve o varbind da resposta, desde que seja do OID pedido."""
        vb = self._request_varbind(sock, ip, oid, self.PDU_GET)
        if vb is None or vb[0] != oid:
            return None
        return vb

    def _get_next(
        self, sock: socket.socket, ip: str, oid: str
    ) -> Optional[tuple[str, int, bytes]]:
        """GETNEXT: o varbind seguinte a `oid` na arvore do agente."""
        return self._request_varbind(sock, ip, oid, self.PDU_GETNEXT)

    def _request_varbind(
        self, sock: socket.socket, ip: str, oid: str, pdu_type: int
    ) -> Optional[tuple[str, int, bytes]]:
        try:
            request_id = self._next_request_id()
            response = self._exchange(sock, ip, self._build_get(oid, request_id, pdu_type), request_id)
            if not response:
                return None
            varbinds = parse_varbinds(response)
            if not varbinds:
                return None
            first = varbinds[0]
            if first[1] in EXCEPTION_TAGS or first[1] == TAG_NULL:
                return None
            return first
        except Exception:
            return None

    def _next_request_id(self) -> int:
        return next(self._request_ids) % 0x7FFFFFFF + 1

    def _exchange(
        self, sock: socket.socket, ip: str, packet: bytes, request_id: int | None = None
    ) -> Optional[bytes]:
        """
        Envia um pacote e aguarda a resposta (UDP/161).

        Reenvia em TIMEOUT (ate `self.retries` vezes) — UDP nao garante
        entrega, um pacote perdido no meio do caminho nao deveria virar
        "sem resposta" se a proxima tentativa passar. Nao reenvia em outro
        tipo de erro de socket (ex.: rede inalcancavel): esse e um problema
        persistente, nao passageiro, e tentar de novo so soma latencia sem
        chance real de sucesso.

        Com `request_id`, descarta resposta de outro pedido: a resposta
        atrasada de um GET que ja estourou o timeout chega no mesmo socket e
        seria lida como o valor do OID seguinte.
        """
        tentativas = 1 + self.retries
        for tentativa in range(tentativas):
            try:
                sock.sendto(packet, (ip, self.port))
                while True:
                    response, _addr = sock.recvfrom(8192)
                    if request_id is None or self._response_request_id(response) == request_id:
                        self._snmp_answered = True
                        return response
            except socket.timeout:
                self._last_network_error = "snmp_timeout"
                if tentativa + 1 < tentativas:
                    continue
                return None
            except OSError:
                self._last_network_error = "snmp_socket_error"
                return None
        return None

    @staticmethod
    def _response_request_id(response: bytes) -> Optional[int]:
        try:
            return parse_response(response)[0]
        except (ValueError, IndexError):
            return None

    # ─────────────────────────────────────────────────────────────────────
    #  Codificacao BER dos pedidos
    # ─────────────────────────────────────────────────────────────────────
    @staticmethod
    def _encode_oid(oid: str) -> bytes:
        parts = [int(p) for p in oid.split(".")]
        out = bytearray([parts[0] * 40 + parts[1]])
        for val in parts[2:]:
            if val < 128:
                out.append(val)
            else:
                chunk = bytearray([val & 0x7F])
                val >>= 7
                while val > 0:
                    chunk.insert(0, (val & 0x7F) | 0x80)
                    val >>= 7
                out.extend(chunk)
        return bytes(out)

    @staticmethod
    def _tlv(tag: int, value: bytes) -> bytes:
        if len(value) < 0x80:
            return bytes([tag, len(value)]) + value
        length = len(value)
        length_bytes = length.to_bytes((length.bit_length() + 7) // 8, "big")
        return bytes([tag, 0x80 | len(length_bytes)]) + length_bytes + value

    def _varbind(self, oid: str) -> bytes:
        return self._tlv(
            TAG_SEQUENCE,
            self._tlv(TAG_OID, self._encode_oid(oid)) + self._tlv(TAG_NULL, b""),
        )

    def _wrap(self, version: int, pdu: bytes) -> bytes:
        return self._tlv(
            TAG_SEQUENCE,
            self._tlv(TAG_INTEGER, bytes([version]))
            + self._tlv(TAG_OCTET_STRING, self.community.encode("ascii"))
            + pdu,
        )

    def _build_get(self, oid: str, request_id: int = 1, pdu_type: int = PDU_GET) -> bytes:
        """SNMPv1 GET (PS1: Build-SnmpGet, version 0, PDU 0xA0) ou GETNEXT (PDU 0xA1)."""
        body = (
            self._tlv(TAG_INTEGER, request_id.to_bytes(4, "big"))  # request-id
            + self._tlv(TAG_INTEGER, b"\x00")  # error-status
            + self._tlv(TAG_INTEGER, b"\x00")  # error-index
            + self._tlv(TAG_SEQUENCE, self._varbind(oid))
        )
        return self._wrap(0, self._tlv(pdu_type, body))

    def _build_getbulk(self, oids: list[str], max_repetitions: int, request_id: int = 2) -> bytes:
        """SNMPv2c GETBULK (PS1: Build-SnmpGetBulk, version 1, PDU 0xA5)."""
        varbinds = b"".join(self._varbind(oid) for oid in oids)
        body = (
            self._tlv(TAG_INTEGER, request_id.to_bytes(4, "big"))  # request-id
            + self._tlv(TAG_INTEGER, b"\x00")  # non-repeaters
            + self._tlv(TAG_INTEGER, bytes([max_repetitions]))  # max-repetitions
            + self._tlv(TAG_SEQUENCE, varbinds)
        )
        return self._wrap(1, self._tlv(0xA5, body))

    # ─────────────────────────────────────────────────────────────────────
    @staticmethod
    def _format_uptime(ticks: int) -> str:
        """Ticks de 1/100s -> 'Xd, Yh, Zm' (mesmo formato do PS1)."""
        seconds = ticks / 100
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{days}d, {hours}h, {minutes}m"
