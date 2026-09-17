"""
Validacao local do SNMPClient sem impressoras reais.

Sobe um agente SNMP falso em UDP (127.0.0.1) que responde aos mesmos OIDs
da Printer-MIB e exercita o caminho SNMP REAL de ponta a ponta: codificacao
do pedido, GETBULK, fallback para GET individual, parsing e classificacao.

Uso:
    python tests_snmp_local.py
"""
import socket
import threading
import time
from dataclasses import asdict

from app.schemas.printer import PaperTray, validate_probe_ip
from app.services.snmp import (
    EXCEPTION_TAGS,
    TAG_COUNTER32,
    TAG_INTEGER,
    TAG_OCTET_STRING,
    TAG_SEQUENCE,
    TAG_TIMETICKS,
    SNMPClient,
    _read_oid,
    _read_tlv,
    decode_error_state,
    parse_response,
    parse_varbinds,
)

OK = "[OK]"
FAIL = "[FALHA]"
_falhas = []


def check(nome, obtido, esperado):
    if obtido == esperado:
        print(f"  {OK} {nome}: {obtido!r}")
    else:
        print(f"  {FAIL} {nome}: obtido {obtido!r}, esperado {esperado!r}")
        _falhas.append(nome)


# ─────────────────────────────────────────────────────────────────────────────
#  Agente SNMP falso
# ─────────────────────────────────────────────────────────────────────────────
class FakeAgent(threading.Thread):
    """Responde GET, GETNEXT e GETBULK para um conjunto de OIDs configurado."""

    daemon = True

    def __init__(
        self,
        supplies,
        page_count=123456,
        uptime=500000,
        support_bulk=True,
        mute=False,
        drop_first=0,
        extra=None,
        send_stale=False,
    ):
        super().__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", 0))
        self.port = self.sock.getsockname()[1]
        self.supplies = supplies  # [(index, level, max, desc)]
        self.page_count = page_count
        self.uptime = uptime
        self.support_bulk = support_bulk
        self.mute = mute
        # Simula pacote perdido: ignora os N primeiros pedidos recebidos (nao
        # responde nada, como se o UDP tivesse comido o pacote), responde
        # normalmente dali em diante — para testar que o RETRY do cliente
        # recupera do que seria, sem ele, um falso "sem resposta".
        self.drop_first = drop_first
        self._dropped = 0
        self.extra = extra or {}  # {oid: (tag, valor)} alem de uptime/contador/toner
        # Antes de cada resposta de GET manda outra com request-id diferente e
        # valor falso, como a resposta atrasada de um pedido anterior.
        self.send_stale = send_stale
        self.requests = 0
        self.running = True
        self._c = SNMPClient()

    def stop(self):
        self.running = False
        try:
            self.sock.close()
        except Exception:
            pass

    # -- tabela de valores ------------------------------------------------
    def values(self):
        v = {
            SNMPClient.OID_UPTIME: (TAG_TIMETICKS, self.uptime),
            SNMPClient.OID_PAGE_COUNT: (TAG_COUNTER32, self.page_count),
        }
        for idx, level, maximum, desc in self.supplies:
            v[f"{SNMPClient.OID_TONER_LEVEL}.{idx}"] = (TAG_INTEGER, level)
            v[f"{SNMPClient.OID_TONER_MAX}.{idx}"] = (TAG_INTEGER, maximum)
            v[f"{SNMPClient.OID_TONER_DESC}.{idx}"] = (TAG_OCTET_STRING, desc)
        v.update(self.extra)
        return v

    def _encode_value(self, tag, value):
        if tag == TAG_OCTET_STRING:
            return self._c._tlv(tag, value if isinstance(value, bytes) else value.encode("ascii"))
        if tag == TAG_INTEGER:
            return self._c._tlv(tag, value.to_bytes((value.bit_length() + 8) // 8, "big", signed=True))
        if value == 0:
            return self._c._tlv(tag, b"\x00")
        raw = value.to_bytes((value.bit_length() + 7) // 8, "big")
        return self._c._tlv(tag, raw)

    def _varbind(self, oid, tag, value):
        return self._c._tlv(
            TAG_SEQUENCE,
            self._c._tlv(0x06, self._c._encode_oid(oid)) + self._encode_value(tag, value),
        )

    def _response(self, varbinds_payload, request_id):
        body = (
            self._c._tlv(TAG_INTEGER, request_id)
            + self._c._tlv(TAG_INTEGER, b"\x00")
            + self._c._tlv(TAG_INTEGER, b"\x00")
            + self._c._tlv(TAG_SEQUENCE, varbinds_payload)
        )
        return self._c._wrap(0, self._c._tlv(0xA2, body))

    # -- leitura do pedido ------------------------------------------------
    @staticmethod
    def _request(data):
        """Extrai (pdu_tag, request_id_bytes, [oids]) de um GET/GETNEXT/GETBULK."""
        _t, _l, outer, _n = _read_tlv(data, 0)
        pos = outer
        _t, _l, _v, pos = _read_tlv(data, pos)  # version
        _t, _l, _v, pos = _read_tlv(data, pos)  # community
        pdu_tag, _l, pdu_start, _n = _read_tlv(data, pos)
        _t, rid_len, rid_start, pos = _read_tlv(data, pdu_start)
        request_id = data[rid_start : rid_start + rid_len]
        for _ in range(2):
            _t, _l, _v, pos = _read_tlv(data, pos)
        _t, _l, vb_start, vb_end = _read_tlv(data, pos)
        oids, pos = [], vb_start
        while pos < vb_end:
            _t, _l, inner, nxt = _read_tlv(data, pos)
            _ot, olen, ostart, _after = _read_tlv(data, inner)
            oids.append(_read_oid(data, ostart, olen))
            pos = nxt
        return pdu_tag, request_id, oids

    @staticmethod
    def _next_oid(oid, values):
        def chave(o):
            return tuple(int(p) for p in o.split("."))

        seguintes = [o for o in values if chave(o) > chave(oid)]
        return min(seguintes, key=chave) if seguintes else None

    def run(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(8192)
            except Exception:
                return
            self.requests += 1
            if self.mute:
                continue
            if self._dropped < self.drop_first:
                self._dropped += 1
                continue
            try:
                pdu_tag, request_id, oids = self._request(data)
                values = self.values()

                if pdu_tag == 0xA5:  # GETBULK
                    if not self.support_bulk:
                        continue  # agente sem v2c: nao responde
                    payload = b""
                    for idx, _lvl, _max, _desc in self.supplies:
                        for col in (
                            SNMPClient.OID_TONER_LEVEL,
                            SNMPClient.OID_TONER_MAX,
                            SNMPClient.OID_TONER_DESC,
                        ):
                            oid = f"{col}.{idx}"
                            tag, val = values[oid]
                            payload += self._varbind(oid, tag, val)
                    self.sock.sendto(self._response(payload, request_id), addr)
                elif pdu_tag == 0xA1:  # GETNEXT
                    nxt = self._next_oid(oids[0], values)
                    if nxt is None:  # endOfMibView
                        payload = self._c._tlv(
                            TAG_SEQUENCE,
                            self._c._tlv(0x06, self._c._encode_oid(oids[0])) + self._c._tlv(0x82, b""),
                        )
                    else:
                        payload = self._varbind(nxt, *values[nxt])
                    self.sock.sendto(self._response(payload, request_id), addr)
                else:  # GET
                    oid = oids[0]
                    if self.send_stale:
                        outro_id = bytes(b ^ 0x55 for b in request_id)
                        self.sock.sendto(
                            self._response(self._varbind(oid, TAG_COUNTER32, 7777777), outro_id), addr
                        )
                    if oid in values:
                        tag, val = values[oid]
                        self.sock.sendto(self._response(self._varbind(oid, tag, val), request_id), addr)
                    else:
                        # noSuchInstance
                        payload = self._c._tlv(
                            TAG_SEQUENCE,
                            self._c._tlv(0x06, self._c._encode_oid(oid))
                            + self._c._tlv(0x81, b""),
                        )
                        self.sock.sendto(self._response(payload, request_id), addr)
            except Exception:
                continue


def device_oids(
    index=1,
    errors=b"\x00\x00",
    device_status=2,
    printer_status=3,
    serial="BRX123456",
    model="HP LaserJet M608",
    display=("Pronta",),
    trays=(),
):
    """OIDs de identificacao/estado do equipamento (MIB-II, HOST-RESOURCES, Printer-MIB)."""
    v = {
        SNMPClient.OID_SYS_DESCR: (TAG_OCTET_STRING, "HP ETHERNET MULTI-ENVIRONMENT"),
        SNMPClient.OID_SYS_NAME: (TAG_OCTET_STRING, "NPI1A2B3C"),
        SNMPClient.OID_SYS_LOCATION: (TAG_OCTET_STRING, "Diretoria 2o andar"),
        f"{SNMPClient.OID_HR_DEVICE_DESCR}.{index}": (TAG_OCTET_STRING, model),
        f"{SNMPClient.OID_HR_DEVICE_STATUS}.{index}": (TAG_INTEGER, device_status),
        f"{SNMPClient.OID_HR_PRINTER_STATUS}.{index}": (TAG_INTEGER, printer_status),
        f"{SNMPClient.OID_HR_PRINTER_ERRORS}.{index}": (TAG_OCTET_STRING, errors),
        f"{SNMPClient.OID_SERIAL_NUMBER}.{index}": (TAG_OCTET_STRING, serial),
    }
    for line, text in enumerate(display, 1):
        v[f"{SNMPClient.OID_CONSOLE_TEXT}.{index}.{line}"] = (TAG_OCTET_STRING, text)
    for tray, (name, level, maximum) in enumerate(trays, 1):
        v[f"{SNMPClient.OID_INPUT_LEVEL}.{index}.{tray}"] = (TAG_INTEGER, level)
        v[f"{SNMPClient.OID_INPUT_MAX}.{index}.{tray}"] = (TAG_INTEGER, maximum)
        v[f"{SNMPClient.OID_INPUT_NAME}.{index}.{tray}"] = (TAG_OCTET_STRING, name)
    return v


class LocalSNMPClient(SNMPClient):
    """SNMPClient apontando para a porta do agente falso, com o resultado do ping controlado."""

    def __init__(self, port, ping_ok=True, **kw):
        super().__init__(**kw)
        self.port = port
        self.ping_ok = ping_ok

    def _ping(self, ip):
        return self.ping_ok


def iniciar(agent):
    agent.start()
    time.sleep(0.2)
    return agent


# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("=" * 70)
    print("VALIDACAO DO CAMINHO SNMP REAL (agente falso em UDP local)")
    print("=" * 70)

    c = SNMPClient()

    # 1. BER: ida e volta
    print("\n[1] Codificacao/decodificacao BER")
    check("encode OID 1.3.6.1.2.1.1.3.0", c._encode_oid("1.3.6.1.2.1.1.3.0").hex(),
          "2b06010201010300")
    pkt = c._build_get(SNMPClient.OID_PAGE_COUNT)
    check("GET e SEQUENCE valida", pkt[0], 0x30)
    check("GET declara version 0 (v1)", pkt[4], 0x00)
    bulk = c._build_getbulk([SNMPClient.OID_TONER_LEVEL], 15)
    check("GETBULK declara version 1 (v2c)", bulk[4], 0x01)
    check("GETBULK usa PDU 0xA5", 0xA5 in bulk, True)

    # 2. Parsing dos tipos que o codigo anterior errava
    print("\n[2] Parsing de tipos SNMP")
    agent = iniciar(FakeAgent(supplies=[(1, 8500, 10000, "Black Toner Cartridge")]))
    cli = LocalSNMPClient(agent.port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)
    check("TimeTicks (sysUpTime)", cli._get_numeric(sock, "127.0.0.1", SNMPClient.OID_UPTIME), 500000)
    check("Counter32 (page count)", cli._get_numeric(sock, "127.0.0.1", SNMPClient.OID_PAGE_COUNT), 123456)
    check("INTEGER (toner level)",
          cli._get_numeric(sock, "127.0.0.1", f"{SNMPClient.OID_TONER_LEVEL}.1"), 8500)
    check("OCTET STRING (descricao)",
          cli._get_string(sock, "127.0.0.1", f"{SNMPClient.OID_TONER_DESC}.1"),
          "Black Toner Cartridge")
    check("noSuchInstance vira None",
          cli._get_numeric(sock, "127.0.0.1", f"{SNMPClient.OID_TONER_LEVEL}.99"), None)
    sock.close()

    # 3. Mono via GETBULK
    print("\n[3] Impressora monocromatica (GETBULK)")
    r = cli.collect("127.0.0.1", is_color=False)
    check("status", r.status, "online")
    check("snmp_responded", r.snmp_responded, True)
    check("page_count", r.page_count, 123456)
    check("qtd toners", len(r.toners), 1)
    check("cor", r.toners[0].color, "K")
    check("percentual", r.toners[0].percent, 85)
    check("uptime (500000 ticks = 5000s)", r.uptime, "0d, 1h, 23m")
    agent.stop()

    # 4. Colorida + descarte de waste toner
    print("\n[4] Impressora colorida + filtro de consumivel")
    agent = iniciar(FakeAgent(supplies=[
        (1, 7200, 10000, "Black Toner"),
        (2, 5800, 10000, "Cyan Toner"),
        (3, 6100, 10000, "Magenta Toner"),
        (4, 5500, 10000, "Yellow Toner"),
        (5, 9000, 10000, "Waste Toner Container"),
    ]))
    r = LocalSNMPClient(agent.port).collect("127.0.0.1", is_color=True)
    check("qtd toners (waste excluido)", len(r.toners), 4)
    check("ordem C,M,Y,K", [t.color for t in r.toners], ["C", "M", "Y", "K"])
    check("percentuais", {t.color: t.percent for t in r.toners},
          {"C": 58, "M": 61, "Y": 55, "K": 72})
    check("status", r.status, "online")
    agent.stop()

    # 5. Toner baixo -> atencao
    print("\n[5] Toner baixo dispara status 'atencao'")
    agent = iniciar(FakeAgent(supplies=[(1, 1500, 10000, "Black Toner")]))
    r = LocalSNMPClient(agent.port).collect("127.0.0.1", is_color=False)
    check("percentual", r.toners[0].percent, 15)
    check("status", r.status, "atencao")
    agent.stop()

    # 6. Fallback GET individual (agente sem GETBULK)
    print("\n[6] Fallback para GET individual (agente sem v2c)")
    agent = iniciar(FakeAgent(supplies=[(1, 4000, 10000, "Black Toner")], support_bulk=False))
    r = LocalSNMPClient(agent.port, timeout=0.4).collect("127.0.0.1", is_color=False)
    check("qtd toners", len(r.toners), 1)
    check("percentual", r.toners[0].percent, 40)
    check("snmp_responded", r.snmp_responded, True)
    agent.stop()

    # 7. Mono escolhe o de maior capacidade (regra do PS1)
    print("\n[7] Mono: escolhe o consumivel de maior capacidade")
    agent = iniciar(FakeAgent(supplies=[
        (1, 500, 1000, "Maintenance Kit"),
        (2, 9000, 20000, "Black Toner"),
    ], support_bulk=True))
    r = LocalSNMPClient(agent.port).collect("127.0.0.1", is_color=False)
    check("escolheu maior capacidade", r.toners[0].maximum, 20000)
    check("percentual", r.toners[0].percent, 45)
    agent.stop()

    # 8. SNMP mudo (ping ok, porta 161 sem resposta)
    print("\n[8] SNMP sem resposta (porta muda)")
    agent = iniciar(FakeAgent(supplies=[(1, 5000, 10000, "Black")], mute=True))
    r = LocalSNMPClient(agent.port, timeout=0.3).collect("127.0.0.1", is_color=False)
    time.sleep(0.1)
    check("reachable", r.reachable, True)
    check("snmp_responded", r.snmp_responded, False)
    check("status", r.status, "online")
    check("page_count", r.page_count, None)
    check("qtd toners", len(r.toners), 0)
    check("tem mensagem de erro", bool(r.error), True)
    check("desiste apos o sysUpTime (1 pedido + 1 retry)", agent.requests, 2)
    agent.stop()

    # 9. IP invalido / ausente
    print("\n[9] IP invalido ('N/A')")
    r = SNMPClient().collect("N/A", is_color=False)
    check("status", r.status, "offline")
    check("reachable", r.reachable, False)

    # 10. Host inalcancavel (ping falha)
    print("\n[10] Host inalcancavel (ping e SNMP falham)")
    r = SNMPClient(timeout=0.3).collect("192.0.2.1", is_color=False)  # TEST-NET-1, RFC 5737
    check("status", r.status, "offline")
    check("reachable", r.reachable, False)
    check("snmp_responded", r.snmp_responded, False)

    # 11. Colorida adivinhada errado como mono (Fase 14) — GETBULK ja
    # descobre as 4 cores (nao e limitado pelo palpite is_color); o palpite
    # errado nao pode fazer _select_toners descartar 3 delas so porque o
    # modelo/nome nao continha "color" (ex.: "Kyocera M5021cdn").
    print("\n[11] Colorida com is_color=False (palpite errado no nome do modelo)")
    agent = iniciar(FakeAgent(supplies=[
        (1, 7200, 10000, "Black Toner"),
        (2, 5800, 10000, "Cyan Toner"),
        (3, 6100, 10000, "Magenta Toner"),
        (4, 5500, 10000, "Yellow Toner"),
    ]))
    r = LocalSNMPClient(agent.port).collect("127.0.0.1", is_color=False)  # palpite errado de proposito
    check("qtd toners (as 4 cores, mesmo com palpite errado)", len(r.toners), 4)
    check("ordem C,M,Y,K", [t.color for t in r.toners], ["C", "M", "Y", "K"])
    agent.stop()

    # 11b. Retry (Fase 17): 1 pacote perdido, retries=1 -> recupera na
    # segunda tentativa em vez de virar "sem resposta".
    print("\n[11b] Retry recupera de 1 pacote perdido (SNMP_RETRIES=1)")
    agent = iniciar(FakeAgent(supplies=[(1, 4500, 10000, "Black Toner")], drop_first=1))
    r = LocalSNMPClient(agent.port, timeout=0.3, retries=1).collect("127.0.0.1", is_color=False)
    check("snmp_responded (recuperou do pacote perdido)", r.snmp_responded, True)
    check("qtd toners", len(r.toners), 1)
    check("percentual correto apesar do pacote perdido", r.toners[0].percent, 45)
    agent.stop()

    # 11c. Perdas alem do que o retry cobre: continua falhando (nao trava
    # tentando pra sempre, e nao finge sucesso). Testa _get_numeric()
    # isolado (nao collect() inteiro) porque collect() consulta varios
    # campos — cada um com seu proprio orcamento de retry — e um agente com
    # "drop_first" global misturaria o orcamento de um campo com o de outro.
    print("\n[11c] Perdas alem do limite de retry (consulta isolada): continua reportando falha")
    agent = iniciar(FakeAgent(supplies=[(1, 4500, 10000, "Black Toner")], drop_first=2))
    cli = LocalSNMPClient(agent.port, timeout=0.2, retries=1)
    sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock2.settimeout(2)
    check(
        "None apos esgotar as 2 tentativas (1 inicial + 1 retry)",
        cli._get_numeric(sock2, "127.0.0.1", SNMPClient.OID_UPTIME),
        None,
    )
    sock2.close()
    agent.stop()

    # 12. Mono de verdade continua escolhendo so 1, mesmo com is_color=True
    # por engano (nao regride: sem cor distinta nos candidatos, mantem so
    # o de maior capacidade).
    print("\n[12] Mono de verdade nao vira colorida por engano")
    agent = iniciar(FakeAgent(supplies=[
        (1, 500, 1000, "Maintenance Kit"),
        (2, 9000, 20000, "Black Toner"),
    ]))
    r = LocalSNMPClient(agent.port).collect("127.0.0.1", is_color=False)
    check("qtd toners (so 1, cores nao distintas)", len(r.toners), 1)
    check("escolheu maior capacidade", r.toners[0].maximum, 20000)
    agent.stop()

    print("\n[13] ICMP filtrado, SNMP responde: nao e offline")
    agent = iniciar(FakeAgent(supplies=[(1, 6000, 10000, "Black Toner")], extra=device_oids()))
    r = LocalSNMPClient(agent.port, ping_ok=False).collect("127.0.0.1", is_color=False)
    check("status", r.status, "online")
    check("reachable", r.reachable, True)
    check("page_count", r.page_count, 123456)
    check("percentual", [t.percent for t in r.toners], [60])
    agent.stop()

    print("\n[14] Sem ping e SNMP mudo: offline com um unico pedido")
    agent = iniciar(FakeAgent(supplies=[], mute=True))
    r = LocalSNMPClient(agent.port, ping_ok=False, timeout=0.2, retries=1).collect("127.0.0.1")
    time.sleep(0.1)
    check("status", r.status, "offline")
    check("reachable", r.reachable, False)
    check("status_reason", r.status_reason, "ping_failed")
    check("pedidos enviados (sysUpTime sem retry)", agent.requests, 1)
    agent.stop()

    print("\n[15] Resposta com outro request-id e descartada")
    agent = iniciar(FakeAgent(supplies=[(1, 5000, 10000, "Black Toner")], send_stale=True))
    r = LocalSNMPClient(agent.port).collect("127.0.0.1", is_color=False)
    check("page_count nao assume o valor da resposta alheia", r.page_count, 123456)
    check("uptime nao assume o valor da resposta alheia", r.uptime, "0d, 1h, 23m")
    agent.stop()

    print("\n[16] Estado do equipamento: atolamento vira 'atencao' e a identificacao e lida")
    agent = iniciar(FakeAgent(
        supplies=[(1, 8000, 10000, "Black Toner")],
        extra=device_oids(errors=bytes([0x04, 0x00]), device_status=3, display=("Atolamento", "Abra a porta A")),
    ))
    r = LocalSNMPClient(agent.port).collect("127.0.0.1", is_color=False)
    check("status", r.status, "atencao")
    check("error_states", r.error_states, ["jammed"])
    check("device_status", r.device_status, "warning")
    check("printer_state", r.printer_state, "idle")
    check("serial_number", r.serial_number, "BRX123456")
    check("device_model", r.device_model, "HP LaserJet M608")
    check("sys_description", r.sys_description, "HP ETHERNET MULTI-ENVIRONMENT")
    check("sys_name", r.sys_name, "NPI1A2B3C")
    check("sys_location", r.sys_location, "Diretoria 2o andar")
    check("display_text", r.display_text, "Atolamento | Abra a porta A")
    agent.stop()

    print("\n[17] Equipamento 'down' sem bit de erro; hrDeviceIndex 2 descoberto por GETNEXT")
    agent = iniciar(FakeAgent(
        supplies=[(1, 8000, 10000, "Black Toner")],
        extra=device_oids(index=2, device_status=5, printer_status=1, serial="IDX2-SERIAL"),
    ))
    r = LocalSNMPClient(agent.port).collect("127.0.0.1", is_color=False)
    check("status", r.status, "atencao")
    check("device_status", r.device_status, "down")
    check("printer_state", r.printer_state, "other")
    check("serial do indice 2", r.serial_number, "IDX2-SERIAL")
    agent.stop()

    print("\n[18] Avisos (papel baixo, bandeja manual vazia) nao mudam o status")
    agent = iniciar(FakeAgent(
        supplies=[(1, 8000, 10000, "Black Toner")],
        extra=device_oids(errors=bytes([0x80, 0x04])),
    ))
    r = LocalSNMPClient(agent.port).collect("127.0.0.1", is_color=False)
    check("status", r.status, "online")
    check("error_states", r.error_states, ["lowPaper", "inputTrayEmpty"])
    agent.stop()

    print("\n[19] Bandejas de papel")
    agent = iniciar(FakeAgent(
        supplies=[(1, 8000, 10000, "Black Toner")],
        extra=device_oids(trays=(("Bandeja 1", -3, 500), ("Bandeja 2", 0, 250), ("Manual", 50, 100))),
    ))
    r = LocalSNMPClient(agent.port).collect("127.0.0.1", is_color=False)
    check("nomes", [t.name for t in r.paper_trays], ["Bandeja 1", "Bandeja 2", "Manual"])
    check("niveis crus (-3 = ha papel)", [t.level for t in r.paper_trays], [-3, 0, 50])
    check("capacidades", [t.max_capacity for t in r.paper_trays], [500, 250, 100])
    bandejas = [PaperTray(**asdict(t)) for t in r.paper_trays]
    check("estado", [b.state for b in bandejas], ["com_papel", "vazia", "com_papel"])
    check("percentual", [b.percent for b in bandejas], [None, 0, 50])
    check("sobrevive a ida e volta pelo JSON", PaperTray(**bandejas[1].model_dump()).state, "vazia")
    agent.stop()

    print("\n[20] Nivel especial de toner (-3 = 'ha toner') nao vira 100%")
    agent = iniciar(FakeAgent(supplies=[(1, -3, 10000, "Black Toner")]))
    r = LocalSNMPClient(agent.port).collect("127.0.0.1", is_color=False)
    check("GETBULK: nenhum percentual inventado", [t.percent for t in r.toners], [])
    agent.stop()
    agent = iniciar(FakeAgent(supplies=[(1, -3, 10000, "Black Toner")], support_bulk=False))
    r = LocalSNMPClient(agent.port, timeout=0.3).collect("127.0.0.1", is_color=False)
    check("GET individual: nenhum percentual inventado", [t.percent for t in r.toners], [])
    agent.stop()
    agent = iniciar(FakeAgent(supplies=[(1, 40000, 60000, "Black Toner")]))
    r = LocalSNMPClient(agent.port).collect("127.0.0.1", is_color=False)
    check("nivel alto continua positivo", [t.percent for t in r.toners], [67])
    agent.stop()

    print("\n[21] Etiquetadora: conectividade por SNMP quando o ping e filtrado")
    agent = iniciar(FakeAgent(supplies=[]))
    r = LocalSNMPClient(agent.port, ping_ok=False).check_connectivity("127.0.0.1")
    check("responde SNMP -> online", r.status, "online")
    check("reachable", r.reachable, True)
    check("uptime lido", r.uptime, "0d, 1h, 23m")
    agent.stop()
    agent = iniciar(FakeAgent(supplies=[], mute=True))
    r = LocalSNMPClient(agent.port, ping_ok=False, timeout=0.2).check_connectivity("127.0.0.1")
    check("mudo -> offline", r.status, "offline")
    check("reachable", r.reachable, False)
    agent.stop()

    print("\n[22] Decodificacao de hrPrinterDetectedErrorState")
    check("sem papel (bit 1)", decode_error_state(bytes([0x40])), ["noPaper"])
    check("vazio", decode_error_state(b""), [])
    check("manutencao preventiva (bit 14)", decode_error_state(bytes([0x00, 0x02])), ["overduePreventMaint"])

    print("\n[23] Request-id viaja no pacote")
    check("request-id do GET", parse_response(c._build_get(SNMPClient.OID_UPTIME, 123456789))[0], 123456789)
    check(
        "GETNEXT usa PDU 0xA1",
        FakeAgent._request(c._build_get(SNMPClient.OID_UPTIME, 7, SNMPClient.PDU_GETNEXT))[0],
        0xA1,
    )

    print("\n[24] IP aceito pela consulta ao vivo")
    check("IPv4 privado aceito", validate_probe_ip(" 10.150.26.40 "), "10.150.26.40")
    for ip in ("127.0.0.1", "8.8.8.8", "255.255.255.255", "169.254.1.1", "0.0.0.0", "abc"):
        try:
            validate_probe_ip(ip)
            recusado = False
        except ValueError:
            recusado = True
        check(f"{ip} recusado", recusado, True)

    print("\n[25] Etiquetadora identificada pelo proprio SNMP, mesmo cadastrada como laser")
    agent = iniciar(FakeAgent(
        supplies=[(1, 0, 100, "Ribbon")],
        page_count=400000000,
        extra=device_oids(model="TT042-50 V8.13 EZD"),
    ))
    r = LocalSNMPClient(agent.port).collect("127.0.0.1", is_color=True)
    check("status", r.status, "online")
    check("sem toner inventado", r.toners, [])
    check("sem contador inventado", r.page_count, None)
    check("status_reason", r.status_reason, "snmp_not_applicable")
    check("modelo lido", r.device_model, "TT042-50 V8.13 EZD")
    agent.stop()

    print("\n" + "=" * 70)
    if _falhas:
        print(f"{FAIL} {len(_falhas)} verificacao(oes) falharam: {_falhas}")
        return 1
    print(f"{OK} Todas as verificacoes do caminho SNMP real passaram.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
