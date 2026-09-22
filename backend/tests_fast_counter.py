r"""
Leitura rapida do contador + versao dos dados (22/09/2026).

Sem rede: o leitor SNMP e substituido por uma funcao falsa.

  1. contador mudou -> leitura nova em TODAS as filas do IP, com status e
     toner copiados, e a versao sobe;
  2. contador igual -> nada gravado, versao parada;
  3. impressora offline ou com leitura velha nao e consultada;
  4. coleta completa em andamento -> rodada pulada;
  5. GET /api/updates/version devolve a versao (e exige login).

    .\venv\Scripts\python.exe tests_fast_counter.py
"""
import os
import tempfile
from datetime import datetime, timedelta
from unittest.mock import patch

DB = os.path.join(tempfile.gettempdir(), "test_fast_counter.db")
if os.path.exists(DB):
    os.remove(DB)
os.environ["DATABASE_URL"] = f"sqlite:///{DB}"
os.environ["ENVIRONMENT"] = "development"

from sqlmodel import Session, select  # noqa: E402

from app.config import settings  # noqa: E402
from app.database import create_db_and_tables, engine  # noqa: E402
from app.models.printer import Printer, PrinterReading  # noqa: E402
from app.services import data_version, printer_fleet  # noqa: E402
from app.services.fast_counter import run_fast_counter_poll  # noqa: E402

failures = []


def check(label, got, expected):
    ok = got == expected
    print(f"[{'OK ' if ok else 'FAIL'}] {label}: {got!r}" + ("" if ok else f" (esperado {expected!r})"))
    if not ok:
        failures.append(label)


create_db_and_tables()
agora = datetime.utcnow()
with Session(engine) as s:
    a1 = Printer(server="srv", name="A_FILA1", ip="10.7.0.1", model="M", active=True)
    a2 = Printer(server="srv", name="A_FILA2", ip="10.7.0.1", model="M", active=True)
    off = Printer(server="srv", name="OFF", ip="10.7.0.2", model="M", active=True)
    velha = Printer(server="srv", name="VELHA", ip="10.7.0.3", model="M", active=True)
    s.add_all([a1, a2, off, velha])
    s.commit()
    for p in (a1, a2, off, velha):
        s.refresh(p)
    ids = {"a1": a1.id, "a2": a2.id}
    s.add(PrinterReading(printer_id=a1.id, status="online", page_count=1000, toner_k=55, timestamp=agora - timedelta(minutes=3)))
    s.add(PrinterReading(printer_id=a2.id, status="online", page_count=1000, toner_k=55, timestamp=agora - timedelta(minutes=3)))
    s.add(PrinterReading(printer_id=off.id, status="offline", page_count=500, timestamp=agora - timedelta(minutes=3)))
    s.add(PrinterReading(printer_id=velha.id, status="online", page_count=700, timestamp=agora - timedelta(days=1)))
    s.commit()

consultados = []


def leitor(valores):
    def ler(ip):
        consultados.append(ip)
        return valores.get(ip)
    return ler


with patch.object(settings, "collection_mode", "real"):
    print("--- 1. contador mudou ---")
    v0, _ = data_version.current()
    alterados = run_fast_counter_poll(leitor({"10.7.0.1": 1003}))
    check("equipamentos alterados", alterados, 1)
    check("so impressoras online e recentes consultadas", sorted(consultados), ["10.7.0.1"])
    with Session(engine) as s:
        for nome in ("a1", "a2"):
            ultima = s.exec(select(PrinterReading).where(PrinterReading.printer_id == ids[nome])
                            .order_by(PrinterReading.id.desc())).first()
            check(f"{nome}: contador novo", ultima.page_count, 1003)
            check(f"{nome}: toner copiado", ultima.toner_k, 55)
    check("versao subiu", data_version.current()[0], v0 + 1)

    print("\n--- 2. contador igual ---")
    with Session(engine) as s:
        antes = len(s.exec(select(PrinterReading)).all())
    check("nada alterado", run_fast_counter_poll(leitor({"10.7.0.1": 1003})), 0)
    with Session(engine) as s:
        check("nenhuma leitura nova", len(s.exec(select(PrinterReading)).all()), antes)
    check("versao parada", data_version.current()[0], v0 + 1)

    print("\n--- 3. sem resposta SNMP ---")
    check("None nao grava", run_fast_counter_poll(leitor({})), 0)

    print("\n--- 4. coleta completa em andamento ---")
    printer_fleet._fleet_lock.acquire()
    try:
        consultados.clear()
        check("rodada pulada", run_fast_counter_poll(leitor({"10.7.0.1": 2000})), 0)
        check("ninguem consultado", consultados, [])
    finally:
        printer_fleet._fleet_lock.release()

print("\n--- 5. endpoint de versao ---")
from fastapi.testclient import TestClient  # noqa: E402

from app.dependencies import require_active_user  # noqa: E402
from app.main import app  # noqa: E402
from app.models.user import User  # noqa: E402

client = TestClient(app)
check("sem login -> 401", client.get("/api/updates/version").status_code, 401)
app.dependency_overrides[require_active_user] = lambda: User(email="x@x.test", name="X", password_hash="x")
r = client.get("/api/updates/version")
app.dependency_overrides.clear()
check("com login -> 200", r.status_code, 200)
check("devolve a versao atual", r.json().get("version"), data_version.current()[0])

print()
if failures:
    print(f"FALHOU: {failures}")
    raise SystemExit(1)
print("Todos os testes da leitura rapida do contador passaram.")
