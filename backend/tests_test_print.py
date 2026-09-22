r"""
Impressao de teste direto no IP (POST /api/printers/{id}/test-print).

Nenhuma impressora real e tocada: um servidor TCP local faz o papel da
porta 9100 e guarda os bytes recebidos. Cobre:

  - laser recebe um documento PJL/PCL valido, com os dados da fila;
  - etiquetadora (TT042) e fila "Generic / Text Only" recebem 422 e nada e
    enviado;
  - inativa -> 409; viewer -> 403;
  - porta fechada vira sent=False / "porta_fechada";
  - cada disparo fica na auditoria;
  - /with-status expoe test_print_supported.

    .\venv\Scripts\python.exe tests_test_print.py
"""
import os
from datetime import datetime
import socket
import tempfile
import threading
from pathlib import Path
from unittest.mock import patch

_TMP = Path(tempfile.mkdtemp(prefix="printercontrol-testprint-"))
os.environ["DATABASE_URL"] = f"sqlite:///{(_TMP / 'test_print.db').as_posix()}"
os.environ["ENVIRONMENT"] = "development"
os.environ["PRINT_SERVER_MODE"] = "mock"

from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import Session, select  # noqa: E402

from app.database import create_db_and_tables, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models.audit_log import AuditLog  # noqa: E402
from app.models.printer import Printer, PrinterMonthly, PrinterReading  # noqa: E402
from app.models.user import Role, User  # noqa: E402
from app.routes import printers as printers_route  # noqa: E402
from app.services import test_print  # noqa: E402
from app.services.auth import hash_password  # noqa: E402

SENHA = "senha-de-teste-123"
_falhas = []


def check(nome, obtido, esperado):
    ok = obtido == esperado
    print(f"  [{'OK  ' if ok else 'FALHA'}] {nome}: {obtido!r}" + ("" if ok else f" (esperado {esperado!r})"))
    if not ok:
        _falhas.append(nome)


class FakeRawPort:
    """Servidor TCP de uma conexao: faz o papel da porta 9100."""

    def __init__(self):
        self.sock = socket.socket()
        self.sock.bind(("127.0.0.1", 0))
        self.sock.listen(1)
        self.port = self.sock.getsockname()[1]
        self.received = b""
        self._t = threading.Thread(target=self._serve, daemon=True)
        self._t.start()

    def _serve(self):
        conn, _ = self.sock.accept()
        with conn:
            while chunk := conn.recv(65536):
                self.received += chunk

    def join(self):
        self._t.join(timeout=5)
        self.sock.close()


class ColetorAoVivoFalso:
    """
    Faz o papel da leitura SNMP ao vivo que a rota faz antes de montar a
    folha: grava uma leitura nova com o contador 3 paginas acima da ultima,
    como se a impressora tivesse impresso mais folhas desde a coleta agendada.
    """

    chamadas = 0

    def __init__(self, mode):
        self.mode = mode

    def collect_and_save(self, printer_id, session, is_color=None):
        ColetorAoVivoFalso.chamadas += 1
        from sqlmodel import select as _select
        ultima = session.exec(
            _select(PrinterReading).where(PrinterReading.printer_id == printer_id).order_by(PrinterReading.id.desc())
        ).first()
        session.add(PrinterReading(printer_id=printer_id, status="online",
                                   page_count=(ultima.page_count if ultima else 0) + 3, toner_k=44))
        session.commit()
        return {"success": True}


class ColetorQuebrado:
    def __init__(self, mode):
        pass

    def collect_and_save(self, printer_id, session, is_color=None):
        raise RuntimeError("SNMP fora do ar")


def porta_livre():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    porta = s.getsockname()[1]
    s.close()  # ninguem escuta nela depois disto: conexao recusada
    return porta


def main():
    create_db_and_tables()
    with Session(engine) as s:
        for papel, role in (("operador", Role.OPERATOR.value), ("viewer", Role.VIEWER.value)):
            s.add(User(email=f"{papel}@teste-print.com", password_hash=hash_password(SENHA), name=papel, role=role))
        laser = Printer(server="srv", name="MC_M2040_TESTE", ip="127.0.0.1", model="Kyocera ECOSYS M2040dn",
                        driver_name="Kyocera ECOSYS M2040dn KX", printer_type="A4", department="HDB - QLD — MC",
                        serial_number="VR99762994", snmp_model="ECOSYS M2040dn", share_name="MC_M2040_SHARE",
                        active=True)
        etiqueta = Printer(server="srv", name="MC_ETIQUETA_1", ip="127.0.0.1", model="Elgin TT042",
                           driver_name="ELGIN TT042 PLUS (203 dpi)", printer_type="Etiqueta", department="TI", active=True)
        generica = Printer(server="srv", name="JUN_LOG_01", ip="127.0.0.1", model="Generic / Text Only",
                           driver_name="Generic / Text Only", printer_type="A4", department="TI", active=True)
        inativa = Printer(server="srv", name="MC_P2135_OLD", ip="127.0.0.1", model="Kyocera ECOSYS P2135dn",
                          driver_name="Kyocera P2135dn KX", printer_type="A4", department="TI", active=False)
        for p in (laser, etiqueta, generica, inativa):
            s.add(p)
        s.commit()
        s.add(PrinterReading(printer_id=laser.id, status="online", page_count=123456, toner_k=45))
        # Historico mensal do equipamento (fechado/importado), para a secao
        # "PAGINAS POR MES" da folha.
        for mes, paginas, estimadas in (("2026-07", 900, 0), ("2026-08", 1234, 200)):
            s.add(PrinterMonthly(printer_id=laser.id, month=mes, pages_printed=paginas, estimated_pages=estimadas,
                                 month_start=datetime(2026, int(mes[5:]), 1), month_end=datetime(2026, int(mes[5:]) + 1, 1)))
        s.commit()
        ids = {n: p.id for n, p in (("laser", laser), ("etiqueta", etiqueta), ("generica", generica), ("inativa", inativa))}

    client = TestClient(app)

    def token(papel):
        r = client.post("/api/auth/login", json={"email": f"{papel}@teste-print.com", "password": SENHA})
        return {"Authorization": f"Bearer {r.json()['access_token']}"}

    op = token("operador")
    original = test_print.send_raw
    # Nenhuma leitura SNMP de verdade no teste: a leitura ao vivo da rota
    # passa pelo coletor falso (ver ColetorAoVivoFalso).
    patch.object(printers_route, "PrinterCollector", ColetorAoVivoFalso).start()
    patch.object(printers_route.settings, "collection_mode", "real").start()

    print("--- 1. laser recebe PJL/PCL com os dados da fila ---")
    fake = FakeRawPort()
    with patch.object(printers_route, "send_raw", lambda ip, payload: original(ip, payload, port=fake.port)):
        r = client.post(f"/api/printers/{ids['laser']}/test-print", headers=op)
    fake.join()
    check("status 200", r.status_code, 200)
    check("sent", r.json().get("sent"), True)
    check("detail", r.json().get("detail"), "enviado")
    doc = fake.received
    check("comeca com UEL + PJL", doc.startswith(b"\x1b%-12345X@PJL"), True)
    check("entra em PCL", b"@PJL ENTER LANGUAGE=PCL" in doc, True)
    check("traz o titulo", b"PrinterControl" in doc and "Página de teste".encode("latin-1") in doc, True)
    check("traz o nome da fila", b"MC_M2040_TESTE" in doc, True)
    check("traz o numero de serie", b"VR99762994" in doc, True)
    check("modelo do SNMP", b"ECOSYS M2040dn" in doc, True)
    check("rotulos das secoes", all(r.encode("latin-1") in doc for r in ("EQUIPAMENTO", "REDE E SERVIDOR", "CONTADOR E TONER")), True)
    check("logo Elgin em raster (600 px, 300 dpi)", b"\x1b*r600S" in doc and b"\x1b*rC" in doc, True)
    check("sem escala de cinza na pagina moderna", "ESCALA DE CINZA".encode("latin-1") in doc, False)
    check("departamento separado da unidade", b"HDB - QLD" in doc and "HDB - QLD — MC".encode("latin-1", "replace") not in doc, True)
    check("unidade", b"Unidade" in doc and b"MC" in doc, True)
    check("compartilhamento", rb"\\srv\MC_M2040_SHARE" in doc, True)
    check("leitura ao vivo feita antes de montar a folha", ColetorAoVivoFalso.chamadas, 1)
    with Session(engine) as s:
        irma = s.exec(
            select(PrinterReading).where(PrinterReading.printer_id == ids["generica"]).order_by(PrinterReading.id.desc())
        ).first()
    check("leitura ao vivo copiada para as outras filas ativas do mesmo IP", irma.page_count if irma else None, 123459)
    check("contador atualizado pela leitura ao vivo (123456 + 3)", b"123.459" in doc, True)
    check("toner tambem vem da leitura ao vivo (44%)", b"Preto" in doc and b"44%" in doc, True)
    check("barra de toner desenhada (retangulo PCL)", b"*c" in doc and b"b0P" in doc, True)
    check("campo sem dado diz 'nao informado'", "não informado".encode("latin-1") in doc, True)
    check("secao de paginas por mes", "PÁGINAS POR MÊS".encode("latin-1") in doc, True)
    check("meses no formato Jul/26 e Ago/26", b"Jul/26" in doc and b"Ago/26" in doc, True)
    check("valor do mes com marca de estimativa", b"1.234*" in doc, True)
    check("mes sem estimativa sem marca", b"900" in doc and b"900*" not in doc, True)
    check("nota explicando o asterisco", "* inclui estimativa".encode("latin-1") in doc, True)
    check("mes corrente marcado como em andamento", "mês em andamento".encode("latin-1") in doc, True)
    check("laser mono recebe a versao monocromatica (sem PCL5c)", b"\x1b*v6W" in doc, False)
    check("traz quem pediu", b"operador@teste-print.com" in doc, True)
    check("acento em Latin-1 (ç)", "ç".encode("latin-1") in doc, True)
    check("ejeta a pagina (form feed)", b"\x0c" in doc, True)
    check("termina com EOJ + UEL", doc.endswith(b"@PJL EOJ\r\n\x1b%-12345X"), True)

    print("\n--- 1b. segunda folha em seguida: contador ja inclui as paginas novas ---")
    fake2 = FakeRawPort()
    with patch.object(printers_route, "send_raw", lambda ip, payload: original(ip, payload, port=fake2.port)):
        client.post(f"/api/printers/{ids['laser']}/test-print", headers=op)
    fake2.join()
    check("contador subiu de novo (123459 + 3)", b"123.462" in fake2.received, True)

    print("\n--- 1c. leitura ao vivo falha: a folha sai com a ultima leitura boa ---")
    fake3 = FakeRawPort()
    with patch.object(printers_route, "PrinterCollector", ColetorQuebrado), \
         patch.object(printers_route, "send_raw", lambda ip, payload: original(ip, payload, port=fake3.port)):
        r3 = client.post(f"/api/printers/{ids['laser']}/test-print", headers=op)
    fake3.join()
    check("folha enviada mesmo sem leitura ao vivo", r3.json().get("sent"), True)
    check("usa a ultima leitura valida", b"123.462" in fake3.received, True)

    print("\n--- 2. etiquetadora e generica: 422, nada enviado ---")
    with patch.object(printers_route, "send_raw") as envio:
        r1 = client.post(f"/api/printers/{ids['etiqueta']}/test-print", headers=op)
        r2 = client.post(f"/api/printers/{ids['generica']}/test-print", headers=op)
    check("TT042 recebe 422", r1.status_code, 422)
    check("Generic / Text Only recebe 422", r2.status_code, 422)
    check("nenhum envio", envio.call_count, 0)

    print("\n--- 3. inativa, viewer, inexistente ---")
    with patch.object(printers_route, "send_raw") as envio:
        check("inativa recebe 409", client.post(f"/api/printers/{ids['inativa']}/test-print", headers=op).status_code, 409)
        check("viewer recebe 403", client.post(f"/api/printers/{ids['laser']}/test-print", headers=token("viewer")).status_code, 403)
        check("inexistente recebe 404", client.post("/api/printers/99999/test-print", headers=op).status_code, 404)
    check("nenhum envio", envio.call_count, 0)

    print("\n--- 4. porta fechada ---")
    fechada = porta_livre()
    with patch.object(printers_route, "send_raw", lambda ip, payload: original(ip, payload, port=fechada)):
        r = client.post(f"/api/printers/{ids['laser']}/test-print", headers=op)
    check("sent", r.json().get("sent"), False)
    check("detail", r.json().get("detail"), "porta_fechada")

    print("\n--- 5. auditoria e /with-status ---")
    with Session(engine) as s:
        trilha = s.exec(select(AuditLog).where(AuditLog.action == "printer.test_print")).all()
    check("cada disparo auditado (3 enviados + porta fechada)", len(trilha), 4)
    frota = {p["name"]: p["test_print_supported"] for p in client.get("/api/printers/with-status", headers=op).json()}
    check("laser suportada", frota.get("MC_M2040_TESTE"), True)
    check("etiquetadora nao suportada", frota.get("MC_ETIQUETA_1"), False)
    check("generica nao suportada", frota.get("JUN_LOG_01"), False)

    print()
    if _falhas:
        print(f"FALHOU: {_falhas}")
        raise SystemExit(1)
    print("Todos os testes de impressao de teste passaram.")


if __name__ == "__main__":
    main()
