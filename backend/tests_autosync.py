r"""
Sync automatico dos Print Servers (22/09/2026).

Cobre, sem rede (descoberta substituida por funcao falsa):
  1. run_auto_sync so toca servidores ativos com mode='real';
  2. com somente_atrasados, pula quem sincronizou ha pouco;
  3. o sync grava last_sync_at/last_status e traz as filas;
  4. falha da descoberta marca o servidor com erro e nao para os outros;
  5. dois syncs do mesmo servidor ao mesmo tempo: o segundo e recusado;
  6. cadastrar um servidor real dispara o sync em segundo plano; mock nao.

    .\venv\Scripts\python.exe tests_autosync.py
"""
import os
import tempfile
from datetime import datetime, timedelta
from unittest.mock import patch

DB = os.path.join(tempfile.gettempdir(), "test_autosync.db")
if os.path.exists(DB):
    os.remove(DB)
os.environ["DATABASE_URL"] = f"sqlite:///{DB}"
os.environ["ENVIRONMENT"] = "development"
os.environ["PRINT_SERVER_MODE"] = "mock"

from sqlmodel import Session, select  # noqa: E402

from app.database import create_db_and_tables, engine  # noqa: E402
from app.models.print_server import PrintServer  # noqa: E402
from app.models.printer import Printer  # noqa: E402
from app.services import print_server_autosync as autosync  # noqa: E402
from app.services import printer_sync  # noqa: E402
from app.services.print_server import DiscoveredPrinter, PrintServerError  # noqa: E402

failures = []


def check(label, got, expected):
    ok = got == expected
    print(f"[{'OK ' if ok else 'FAIL'}] {label}: {got!r}" + ("" if ok else f" (esperado {expected!r})"))
    if not ok:
        failures.append(label)


chamados = []


def descoberta_falsa(server, mode=None, portas_conhecidas=None):
    chamados.append(server)
    if server == "srv-quebrado":
        raise PrintServerError("PowerShell nao respondeu em 90s", "rpc_timeout_or_unavailable")
    return [
        DiscoveredPrinter(name=f"{server}_FILA1", server=server, port_name="10.9.0.1", ip="10.9.0.1",
                          driver_name="Kyocera ECOSYS M3655idn KX"),
        DiscoveredPrinter(name=f"{server}_FILA2", server=server, port_name="10.9.0.2", ip="10.9.0.2",
                          driver_name="HP LaserJet M404 PCL 6"),
    ]


create_db_and_tables()
with Session(engine) as s:
    for host, mode, ativo, sync in [
        ("srv-real", "real", True, None),
        ("srv-quebrado", "real", True, None),
        ("srv-recente", "real", True, datetime.utcnow() - timedelta(minutes=10)),
        ("srv-mock", "mock", True, None),
        ("srv-desligado", "real", False, None),
    ]:
        s.add(PrintServer(host=host, name=host, mode=mode, active=ativo, last_sync_at=sync))
    s.commit()

print("--- 1/2. quem entra na rodada ---")
with patch.object(printer_sync, "discover_printers", side_effect=descoberta_falsa):
    tentados = autosync.run_auto_sync(somente_atrasados=True)
check("tentados (real, ativo e atrasado)", tentados, 2)
check("descoberta chamada para", sorted(chamados), ["srv-quebrado", "srv-real"])

print("\n--- 3. sync bem-sucedido grava o desfecho e traz as filas ---")
with Session(engine) as s:
    real = s.exec(select(PrintServer).where(PrintServer.host == "srv-real")).one()
    filas = s.exec(select(Printer).where(Printer.server == "srv-real")).all()
check("last_status", real.last_status, "online")
check("last_sync_at gravado", real.last_sync_at is not None, True)
check("filas criadas", len(filas), 2)

print("\n--- 4. falha marca erro sem parar os outros ---")
with Session(engine) as s:
    quebrado = s.exec(select(PrintServer).where(PrintServer.host == "srv-quebrado")).one()
check("last_status", quebrado.last_status, "error")
check("categoria no erro", (quebrado.last_error or "").startswith("[rpc_timeout_or_unavailable]"), True)
check("sem last_sync_at", quebrado.last_sync_at, None)

print("\n--- 5. dois syncs do mesmo servidor ao mesmo tempo ---")
trava = autosync._trava("srv-real")
trava.acquire()
try:
    with Session(engine) as s:
        real = s.exec(select(PrintServer).where(PrintServer.host == "srv-real")).one()
        try:
            autosync.sincronizar_servidor(s, real)
            check("segundo sync recusado", False, True)
        except autosync.SyncEmAndamento:
            check("segundo sync recusado", True, True)
finally:
    trava.release()

print("\n--- 6. cadastro de servidor real dispara sync em segundo plano ---")
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.dependencies import require_admin  # noqa: E402
from app.models.user import User  # noqa: E402

with Session(engine) as s:
    admin = User(email="adm@x.test", name="Adm", password_hash="x", role="admin")
    s.add(admin)
    s.commit()
    s.refresh(admin)
app.dependency_overrides[require_admin] = lambda: admin
disparos = []
with patch("app.routes.servers.sincronizar_em_segundo_plano", side_effect=lambda sid, motivo: disparos.append(motivo)):
    client = TestClient(app)
    r1 = client.post("/api/servers", json={"host": "srv-novo", "name": "Novo", "mode": "real"})
    r2 = client.post("/api/servers", json={"host": "srv-novo-mock", "name": "Mock", "mode": "mock"})
app.dependency_overrides.clear()
check("cadastros aceitos", (r1.status_code, r2.status_code), (201, 201))
check("so o real disparou sync", disparos, ["cadastro"])

print()
if failures:
    print(f"FALHOU: {failures}")
    raise SystemExit(1)
print("Todos os testes de sync automatico passaram.")
