"""
Etapa 7 - persistencia de uptime.

Parte A roda sobre uma COPIA do banco REAL (nunca o original), para provar
que a migracao aditiva preserva 100% dos dados existentes. Partes B-E rodam
num banco sintetico isolado, para validar o fluxo completo sem depender dos
73 registros de producao.

Executar:  .\\venv\\Scripts\\python.exe tests_uptime.py
"""
import os
import shutil
import sqlite3
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE_DB = os.path.join(HERE, "printer_control.db")
TEST_DB_A = os.path.join(tempfile.gettempdir(), "test_uptime_migration.db")

if os.path.exists(TEST_DB_A):
    os.remove(TEST_DB_A)
shutil.copyfile(SOURCE_DB, TEST_DB_A)

# Contagens ANTES da migracao, direto no arquivo copiado.
_raw = sqlite3.connect(TEST_DB_A)
BEFORE_PRINTERS = _raw.execute("select count(*) from printers").fetchone()[0]
BEFORE_READINGS = _raw.execute("select count(*) from printer_readings").fetchone()[0]
BEFORE_ALERTS = _raw.execute("select count(*) from alerts").fetchone()[0]
BEFORE_COLS = {row[1] for row in _raw.execute("PRAGMA table_info(printer_readings)")}
SAMPLE_READING = _raw.execute("select id, printer_id, page_count from printer_readings order by id limit 1").fetchone()
_raw.close()

os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_A.replace(os.sep, '/')}"

from sqlmodel import Session, create_engine, select  # noqa: E402

from app.database import _migrate_reading_uptime, create_db_and_tables, engine  # noqa: E402
from app.models.alert import Alert  # noqa: E402
from app.models.printer import Printer, PrinterReading  # noqa: E402

failures = []


def check(label, got, expected):
    ok = got == expected
    print(f"[{'OK ' if ok else 'FAIL'}] {label}: {got}" + ("" if ok else f" (esperado {expected})"))
    if not ok:
        failures.append(label)


def check_true(label, condition, detail=""):
    print(f"[{'OK ' if condition else 'FAIL'}] {label}" + (f": {detail}" if detail else ""))
    if not condition:
        failures.append(label)


print("=== PARTE A: migracao aditiva sobre copia do banco real ===\n")
# Informativo, nao falha o teste: da primeira vez que este teste roda contra
# um printer_control.db sem a coluna, este bloco confirma o cenario "antes".
# Depois que a Etapa 7 aplica a migracao no banco real (uma vez, feito nesta
# sessao), o proprio arquivo de origem ja vem com a coluna — nesse caso o
# teste abaixo so confirma que reaplicar a migracao continua idempotente.
if "uptime" in BEFORE_COLS:
    print("[INFO] banco de origem ja tem uptime (migracao real ja aplicada nesta maquina) — validando idempotencia")
else:
    print("[INFO] banco de origem ainda sem uptime — validando migracao aditiva do zero")

create_db_and_tables()  # dispara _migrate_reading_uptime() dentro do fluxo normal de startup

with Session(engine) as s:
    after_printers = len(s.exec(select(Printer)).all())
    after_readings = len(s.exec(select(PrinterReading)).all())
    after_alerts = len(s.exec(select(Alert)).all())
    cols_after = set()
    from sqlalchemy import text
    with engine.connect() as conn:
        cols_after = {row[1] for row in conn.execute(text("PRAGMA table_info(printer_readings)"))}

    sample = s.get(PrinterReading, SAMPLE_READING[0])

check("coluna uptime foi adicionada", "uptime" in cols_after, True)
check("quantidade de impressoras preservada", after_printers, BEFORE_PRINTERS)
check("quantidade de leituras preservada", after_readings, BEFORE_READINGS)
check("quantidade de alertas preservada", after_alerts, BEFORE_ALERTS)
check("leitura amostrada preserva printer_id", sample.printer_id, SAMPLE_READING[1])
check("leitura amostrada preserva page_count", sample.page_count, SAMPLE_READING[2])
check_true("leitura antiga ficou com uptime=NULL (nao inventado)", sample.uptime is None)

with Session(engine) as s:
    fk_ok = all(
        s.get(Printer, r.printer_id) is not None
        for r in s.exec(select(PrinterReading).limit(50)).all()
    )
check_true("FK printer_id continua valida (amostra de 50 leituras)", fk_ok)

print("\n--- idempotencia: rodar a migracao de novo nao quebra nada ---")
_migrate_reading_uptime()
_migrate_reading_uptime()
with Session(engine) as s:
    check("segunda/terceira chamada nao duplica leituras", len(s.exec(select(PrinterReading)).all()), BEFORE_READINGS)

print(f"\nBanco de teste (copia): {TEST_DB_A}")

# ─────────────────────────────────────────────────────────────────────────
print("\n=== PARTE B-E: fluxo completo em banco sintetico isolado ===\n")

TEST_DB_B = os.path.join(tempfile.gettempdir(), "test_uptime_flow.db")
if os.path.exists(TEST_DB_B):
    os.remove(TEST_DB_B)

# Troca o engine global do app.database para o banco B (fresco, sem uptime
# pre-existente tambem, mas criado do zero por create_all — outro caminho
# de idempotencia: coluna ja nasce junto pelo metadata, e a migracao aditiva
# vira no-op).
import app.database as database_module  # noqa: E402

database_module.engine = create_engine(
    f"sqlite:///{TEST_DB_B.replace(os.sep, '/')}", connect_args={"check_same_thread": False}
)
database_module.create_db_and_tables()

from app.config import settings  # noqa: E402
from app.services.printer_collector import PrinterCollector  # noqa: E402
from app.services.printer_fleet import collect_fleet  # noqa: E402
from app.services.scheduler import run_collection_cycle  # noqa: E402

with Session(database_module.engine) as s:
    p1 = Printer(server="srvtest", name="UP_Solo", ip="10.1.1.1", model="Ricoh P502", active=True)
    p2a = Printer(server="srvtest", name="UP_SharedA", ip="10.1.1.2", model="Kyocera M3040", active=True)
    p2b = Printer(server="srvtest", name="UP_SharedB", ip="10.1.1.2", model="Kyocera M3040", active=True)
    s.add_all([p1, p2a, p2b])
    s.commit()
    s.refresh(p1)
    s.refresh(p2a)
    s.refresh(p2b)
    P1_ID, P2A_ID, P2B_ID = p1.id, p2a.id, p2b.id

print("--- B. coleta individual (mock) persiste uptime ---")
with Session(database_module.engine) as s:
    collector = PrinterCollector(mode="mock", mock_scenario="online_mono")
    result = collector.collect_and_save(P1_ID, s)
check_true("coleta individual teve sucesso", result["success"], result.get("error"))
check("uptime retornado no payload da coleta individual", result["uptime"], "45d, 3h, 22m")

with Session(database_module.engine) as s:
    reading = s.exec(
        select(PrinterReading).where(PrinterReading.printer_id == P1_ID).order_by(PrinterReading.id.desc())
    ).first()
check("uptime persistido pela coleta individual", reading.uptime, "45d, 3h, 22m")

print("\n--- C. coleta de frota (printer_fleet.collect_fleet) persiste uptime, IPs compartilhados identicos ---")
with Session(database_module.engine) as s:
    fleet_result = collect_fleet(s, mode="mock", mock_scenario="online_mono", max_workers=2)
check("frota coletada sem falhas", fleet_result.failed, 0)

with Session(database_module.engine) as s:
    r_a = s.exec(
        select(PrinterReading).where(PrinterReading.printer_id == P2A_ID).order_by(PrinterReading.id.desc())
    ).first()
    r_b = s.exec(
        select(PrinterReading).where(PrinterReading.printer_id == P2B_ID).order_by(PrinterReading.id.desc())
    ).first()
check("uptime persistido na coleta de frota", r_a.uptime, "45d, 3h, 22m")
check("mesmo IP -> mesmo uptime entre impressoras do grupo", r_a.uptime, r_b.uptime)

print("\n--- D. fluxo do scheduler (run_collection_cycle) persiste uptime ---")
settings.collection_mode = "mock"
settings.collection_scenario = "online_mono"
settings.allow_mock_collect = True
settings.collection_max_workers = 2
run_collection_cycle()

with Session(database_module.engine) as s:
    scheduler_reading = s.exec(
        select(PrinterReading).where(PrinterReading.printer_id == P1_ID).order_by(PrinterReading.id.desc())
    ).first()
check("uptime persistido apos ciclo do scheduler", scheduler_reading.uptime, "45d, 3h, 22m")

print("\n--- E. leitura do historico pela API inclui uptime ---")
from fastapi.testclient import TestClient  # noqa: E402
import app.main as main_module  # noqa: E402
import app.routes.printers as printers_route_module  # noqa: E402
import app.database as db_module  # noqa: E402

# app.database.engine ja aponta para o banco B (trocado acima); as rotas
# usam get_session(), que le esse mesmo modulo — nenhuma troca adicional.
client = TestClient(main_module.app)

resp_readings = client.get(f"/api/printers/{P1_ID}/readings")
check("GET /readings -> 200", resp_readings.status_code, 200)
readings_payload = resp_readings.json()
check_true("historico contem uptime", len(readings_payload) > 0 and "uptime" in readings_payload[0])
check("uptime correto no historico via API", readings_payload[0]["uptime"], "45d, 3h, 22m")

resp_status = client.get("/api/printers/with-status")
check("GET /with-status -> 200", resp_status.status_code, 200)
status_payload = {p["id"]: p for p in resp_status.json()}
check_true("with-status contem uptime para P1", "uptime" in status_payload[P1_ID])
check("uptime correto em with-status", status_payload[P1_ID]["uptime"], "45d, 3h, 22m")

print(f"\nBanco de teste (sintetico): {TEST_DB_B}")
print("RESULTADO:", "TODOS OS TESTES PASSARAM" if not failures else f"FALHAS: {failures}")
raise SystemExit(1 if failures else 0)
