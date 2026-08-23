"""
Etapa 4 - migracao de schema + sincronizacao Print Server -> banco.

Roda inteiramente sobre uma COPIA do banco real (nunca o original), para
que a migracao destrutiva (rename/recreate de `printers`) seja exercitada
com dados de producao de verdade, sem risco.

Executar:  .\\venv\\Scripts\\python.exe tests_printer_sync.py
"""
import glob
import os
import shutil
import sqlite3
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
# Fonte da Parte A: precisa ser um banco com o schema ANTIGO (ip UNIQUE,
# sem `server`) para exercitar de fato a migracao destrutiva. Um backup
# *.backup-*.db (criado automaticamente por _migrate_printer_schema antes
# de alterar o schema) serve exatamente para isso; sem um disponivel, cai
# no banco atual (a Parte A vira no-op se ele ja estiver migrado).
_old_schema_backups = sorted(glob.glob(os.path.join(HERE, "printer_control.backup-*.db")))
SOURCE_DB = _old_schema_backups[0] if _old_schema_backups else os.path.join(HERE, "printer_control.db")
TEST_DB = os.path.join(tempfile.gettempdir(), "test_printer_sync.db")

if os.path.exists(TEST_DB):
    os.remove(TEST_DB)
for old_backup in glob.glob(TEST_DB.replace(".db", ".backup-*.db")):
    os.remove(old_backup)
shutil.copyfile(SOURCE_DB, TEST_DB)

# Contagens ANTES da migracao, direto no arquivo copiado (ainda schema antigo).
_raw = sqlite3.connect(TEST_DB)
BEFORE_PRINTERS = _raw.execute("select count(*) from printers").fetchone()[0]
BEFORE_READINGS = _raw.execute("select count(*) from printer_readings").fetchone()[0]
BEFORE_ALERTS = _raw.execute("select count(*) from alerts").fetchone()[0]
SAMPLE_READING = _raw.execute(
    "select id, printer_id from printer_readings order by id limit 1"
).fetchone()
_raw.close()

os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.replace(os.sep, '/')}"

from sqlmodel import Session, create_engine, select  # noqa: E402

import app.services.printer_sync as printer_sync  # noqa: E402
from app.database import create_db_and_tables  # noqa: E402
from app.models.printer import Printer  # noqa: E402
from app.services.print_server import DiscoveredPrinter  # noqa: E402
from app.services.printer_rules import obter_modelo, obter_tipo_impressora  # noqa: E402
from app.services.printer_sync import sync_printers  # noqa: E402

failures = []


def check(label, got, expected):
    ok = got == expected
    print(f"[{'OK ' if ok else 'FAIL'}] {label}: {got}" + ("" if ok else f" (esperado {expected})"))
    if not ok:
        failures.append(label)


def check_true(label, cond, detail=""):
    print(f"[{'OK ' if cond else 'FAIL'}] {label}" + (f": {detail}" if detail else ""))
    if not cond:
        failures.append(label)


print("=== PARTE A: migracao de schema preserva dados existentes ===\n")
create_db_and_tables()  # dispara _migrate_printer_schema na copia

engine = create_engine(f"sqlite:///{TEST_DB.replace(os.sep, '/')}", connect_args={"check_same_thread": False})

with Session(engine) as s:
    after_printers = len(s.exec(select(Printer)).all())
    check("quantidade de impressoras preservada", after_printers, BEFORE_PRINTERS)

    conn = sqlite3.connect(TEST_DB)
    after_readings = conn.execute("select count(*) from printer_readings").fetchone()[0]
    after_alerts = conn.execute("select count(*) from alerts").fetchone()[0]
    check("quantidade de leituras preservada", after_readings, BEFORE_READINGS)
    check("quantidade de alertas preservada", after_alerts, BEFORE_ALERTS)

    reading_id, printer_id = SAMPLE_READING
    ainda_existe = conn.execute("select id from printers where id = ?", (printer_id,)).fetchone()
    check_true(
        "FK de uma leitura amostrada continua valida (printer_id existe)",
        ainda_existe is not None,
        f"reading {reading_id} -> printer_id {printer_id}",
    )
    conn.close()

    legados = s.exec(select(Printer)).all()
    check_true("todas as impressoras legadas ficaram active=True", all(p.active for p in legados))
    check_true(
        "todas ganharam 'server' (default = print_server_host)",
        all(p.server for p in legados),
    )
    check_true("ip original preservado em pelo menos uma", any(p.ip for p in legados))

backups = glob.glob(TEST_DB.replace(".db", ".backup-*.db"))
check_true("backup do banco foi criado antes da migracao destrutiva", len(backups) == 1, str(backups))

print("\n=== PARTE B: sincronizacao (criar / atualizar / desativar / reativar) ===\n")

SERVER = "TESTSRV"  # isolado dos dados legados migrados na Parte A


def fake_discover(rows):
    # `mode` foi acrescentado em discover_printers() na Fase 4 (modo por
    # servidor); o dublê precisa aceitar o mesmo contrato.
    def _discover(server=None, mode=None):
        return [
            DiscoveredPrinter(name=n, server=SERVER, port_name=pn, ip=ip, driver_name=dn)
            for n, pn, ip, dn in rows
        ]
    return _discover


P1 = ("P1", "PORT1", "10.99.1.1", "Ricoh P 502 PCL 6")
P2 = ("P2", "PORT2", "10.99.1.1", "HP LaserJet PCL 6")  # MESMO ip que P1, de proposito
P3 = ("P3", "PORT3", "10.99.1.2", "Elgin TT042 Class Driver")
P4 = ("P4", "PORT4", "10.99.1.3", "Kyocera M6530cdn XPS")

with Session(engine) as s:
    print("--- 1a sincronizacao: 3 impressoras novas ---")
    printer_sync.discover_printers = fake_discover([P1, P2, P3])
    r = sync_printers(s, server=SERVER)
    check("criadas", r.created, 3)
    check("atualizadas", r.updated, 0)
    check("desativadas", r.deactivated, 0)

    rows = s.exec(select(Printer).where(Printer.server == SERVER)).all()
    check("3 linhas no banco para o servidor de teste", len(rows), 3)
    check_true(
        "P1 e P2 compartilham o mesmo IP (identidade nao e mais o IP)",
        next(p.ip for p in rows if p.name == "P1") == next(p.ip for p in rows if p.name == "P2"),
    )

    print("\n--- 2a sincronizacao (mesmos dados): sem duplicar ---")
    r = sync_printers(s, server=SERVER)
    check("nenhuma criada", r.created, 0)
    check("3 atualizadas (todas re-confirmadas)", r.updated, 3)
    rows = s.exec(select(Printer).where(Printer.server == SERVER)).all()
    check("continuam 3 linhas (nao duplicou)", len(rows), 3)

    print("\n--- 3a sincronizacao: P2 sumiu do Print Server ---")
    printer_sync.discover_printers = fake_discover([P1, P3])
    r = sync_printers(s, server=SERVER)
    check("nenhuma criada", r.created, 0)
    check("1 desativada (P2)", r.deactivated, 1)
    p2 = s.exec(select(Printer).where(Printer.server == SERVER, Printer.name == "P2")).first()
    check_true("P2 continua no banco (nao foi apagada)", p2 is not None)
    check("P2 marcada inativa", p2.active, False)

    print("\n--- 4a sincronizacao: P2 reaparece + P4 e nova ---")
    printer_sync.discover_printers = fake_discover([P1, P2, P3, P4])
    r = sync_printers(s, server=SERVER)
    check("1 criada (P4)", r.created, 1)
    check("1 reativada (P2)", r.reactivated, 1)
    p2 = s.exec(select(Printer).where(Printer.server == SERVER, Printer.name == "P2")).first()
    check("P2 ativa novamente", p2.active, True)
    rows = s.exec(select(Printer).where(Printer.server == SERVER)).all()
    check("4 linhas no total (nunca duplicou)", len(rows), 4)
    check_true("todas ativas ao final", all(p.active for p in rows))

print("\n=== PARTE C: Obter-Modelo / Obter-TipoImpressora (fidelidade ao Main.ps1) ===\n")

MODEL_CASES = [
    ("Ricoh Aficio SP P 311 PCL 6", "Ricoh P311"),
    ("Ricoh P 502 PCL 6", "Ricoh P502"),
    ("Kyocera M3040idn KX", "Kyocera M3040idn"),
    ("Kyocera P3055dn PS", "Kyocera P3055dn"),
    ("Kyocera M6530cdn XPS", "Kyocera M6530cdn"),
    ("Honeywell RP4f Class Driver", "Honeywell RP4f"),
    ("Elgin TT042 Class Driver", "Elgin TT042"),
    ("ELGIN Generic", "Elgin TT042 Plus"),
    ("HP LaserJet Pro PCL 6", "HP LaserJet Pro"),  # default: sufixo removido
]
for driver, esperado in MODEL_CASES:
    check(f"obter_modelo({driver!r})", obter_modelo(driver), esperado)

TYPE_CASES = [
    ("MC_Deposito_Zebra", "Zebra ZD230", "Etiqueta"),
    ("VLO_Etiquetadora", "Elgin TT042", "Etiqueta"),
    ("MC_Recepcao_Portatil", "Honeywell RP4f", "Portatil"),
    ("VLO_Diretoria", "Ricoh P502", "A4"),
    ("JUN_Financeiro", "Kyocera M3040idn", "A4"),
    ("Desconhecido", "Impressora Generica", "A4"),  # default
]
for nome, modelo, esperado in TYPE_CASES:
    check(f"obter_tipo_impressora({nome!r}, {modelo!r})", obter_tipo_impressora(nome, modelo), esperado)

print(f"\nBanco de teste: {TEST_DB}")
print("RESULTADO:", "TODOS OS TESTES PASSARAM" if not failures else f"FALHAS: {failures}")
raise SystemExit(1 if failures else 0)
