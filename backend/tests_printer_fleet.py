"""
Etapa 5 - orquestracao da frota (printer_fleet.collect_fleet).

Roda sobre um banco SQLite temporario e ISOLADO (nao o real, nao uma copia
dele) — a frota aqui e sintetica, pensada para exercitar agrupamento por IP,
dedupe dentro do ciclo, paralelismo e isolamento de falha sem depender dos
dados de producao.

Executar:  .\\venv\\Scripts\\python.exe tests_printer_fleet.py
"""
import os
import tempfile
from unittest import mock

TEST_DB = os.path.join(tempfile.gettempdir(), "test_printer_fleet.db")
if os.path.exists(TEST_DB):
    os.remove(TEST_DB)
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.replace(os.sep, '/')}"

from sqlmodel import Session, select  # noqa: E402

from app.database import create_db_and_tables, engine  # noqa: E402
from app.models.printer import Printer, PrinterReading  # noqa: E402
from app.services import printer_fleet  # noqa: E402
from app.services.printer_fleet import collect_fleet  # noqa: E402
from app.services.snmp import SNMPClient, SNMPResult  # noqa: E402
from app.services.snmp_fleet_mock import FleetMockClient  # noqa: E402

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


create_db_and_tables()

# ── frota sintetica ─────────────────────────────────────────────────────
# 10.0.0.1: 2 impressoras (1 colorida, 1 mono) compartilhando IP -> dedupe
# 10.0.0.2: 1 impressora solo
# 10.0.0.3: 1 impressora INATIVA -> nao deve entrar no ciclo
# 10.0.0.4: 2 etiquetadoras (so etiqueta) -> grupo so-ping
# 10.0.0.5: 1 nao-etiqueta + 1 etiqueta -> grupo misto = SNMP completo
# 10.0.0.6: 1 impressora usada para simular falha de rede
PRINTERS = [
    dict(server="srvtest", name="A_Color", ip="10.0.0.1", model="Kyocera M6530cdn XPS", active=True),
    dict(server="srvtest", name="A_Mono", ip="10.0.0.1", model="Kyocera M3040", active=True),
    dict(server="srvtest", name="B_Solo", ip="10.0.0.2", model="Ricoh P502", active=True),
    dict(server="srvtest", name="C_Inactive", ip="10.0.0.3", model="Ricoh P502", active=False),
    dict(server="srvtest", name="D_Label1", ip="10.0.0.4", model="Elgin TT042 Class Driver", active=True),
    dict(server="srvtest", name="D_Label2", ip="10.0.0.4", model="Elgin TT042 Class Driver", active=True),
    dict(server="srvtest", name="E_MixedNonLabel", ip="10.0.0.5", model="HP LaserJet PCL 6", active=True),
    dict(server="srvtest", name="E_MixedLabel", ip="10.0.0.5", model="Elgin TT042 Class Driver", active=True),
    dict(server="srvtest", name="F_Fail", ip="10.0.0.6", model="Ricoh P502", active=True),
]

with Session(engine) as s:
    for p in PRINTERS:
        s.add(Printer(**p))
    s.commit()

ACTIVE_COUNT = sum(1 for p in PRINTERS if p["active"])          # 8
UNIQUE_IPS_ACTIVE = len({p["ip"] for p in PRINTERS if p["active"]})  # 5

print("=== 1. frota ativa / inativa ===")
with Session(engine) as s:
    result = collect_fleet(s, mode="fleet", max_workers=3)

check("total_printers cobre so active=True", result.total_printers, ACTIVE_COUNT)
check("unique_ips agrupados corretamente", result.unique_ips, UNIQUE_IPS_ACTIVE)
check("nenhuma falha no cenario base", result.failed, 0)

with Session(engine) as s:
    inactive = s.exec(select(Printer).where(Printer.name == "C_Inactive")).one()
    reading = s.exec(
        select(PrinterReading).where(PrinterReading.printer_id == inactive.id)
    ).first()
check_true("impressora inativa nao recebeu leitura", reading is None)

print("\n=== 2. dedupe por IP (modo fleet) ===")
original_collect = FleetMockClient.collect
call_log = []


def counting_collect(self, ip, is_color=False):
    call_log.append(ip)
    return original_collect(self, ip, is_color=is_color)


call_log.clear()
with mock.patch.object(FleetMockClient, "collect", counting_collect):
    with Session(engine) as s:
        # limpa leituras da rodada 1 para nao confundir a comparacao "mesmo IP"
        for r in s.exec(select(PrinterReading)):
            s.delete(r)
        s.commit()
        result2 = collect_fleet(s, mode="fleet", max_workers=3)

check("uma consulta de rede por IP unico ativo", len(call_log), UNIQUE_IPS_ACTIVE)
check("nenhum IP consultado duas vezes", len(call_log), len(set(call_log)))

with Session(engine) as s:
    p1 = s.exec(select(Printer).where(Printer.name == "A_Color")).one()
    p2 = s.exec(select(Printer).where(Printer.name == "A_Mono")).one()
    r1 = s.exec(
        select(PrinterReading).where(PrinterReading.printer_id == p1.id).order_by(PrinterReading.id.desc())
    ).first()
    r2 = s.exec(
        select(PrinterReading).where(PrinterReading.printer_id == p2.id).order_by(PrinterReading.id.desc())
    ).first()

check("mesmo IP -> mesmo status", r1.status, r2.status)
check("mesmo IP -> mesmo page_count", r1.page_count, r2.page_count)
check("mesmo IP -> mesmo toner_k", r1.toner_k, r2.toner_k)

print("\n=== 3. paralelismo respeita COLLECTION_MAX_WORKERS ===")
captured_max_workers = {}
_OriginalTPE = printer_fleet.ThreadPoolExecutor


class RecordingThreadPoolExecutor(_OriginalTPE):
    def __init__(self, max_workers=None, *args, **kwargs):
        captured_max_workers["value"] = max_workers
        super().__init__(max_workers=max_workers, *args, **kwargs)


with mock.patch.object(printer_fleet, "ThreadPoolExecutor", RecordingThreadPoolExecutor):
    with Session(engine) as s:
        collect_fleet(s, mode="fleet", max_workers=2)

check("ThreadPoolExecutor recebeu max_workers configurado", captured_max_workers.get("value"), 2)

print("\n=== 4. falha de um IP nao interrompe a frota ===")


def failing_collect(self, ip, is_color=False):
    if ip == "10.0.0.6":
        raise TimeoutError("simulado: sem resposta")
    return original_collect(self, ip, is_color=is_color)


with mock.patch.object(FleetMockClient, "collect", failing_collect):
    with Session(engine) as s:
        result3 = collect_fleet(s, mode="fleet", max_workers=3)

check("apenas 1 impressora falhou (F_Fail)", result3.failed, 1)
check("as demais 7 impressoras foram coletadas", result3.collected, ACTIVE_COUNT - 1)
check_true("erro de rede registrado", any("10.0.0.6" in e for e in result3.errors))

print("\n=== 5. modo real: grupo so-etiqueta faz so ping; grupo misto faz SNMP completo ===")
ping_calls = []
collect_calls = []


def fake_ping(self, ip):
    ping_calls.append(ip)
    return True


def fake_real_collect(self, ip, is_color=False):
    collect_calls.append(ip)
    return SNMPResult(status="online", page_count=100, toners=[], uptime="1d", reachable=True, snmp_responded=True)


ping_calls.clear()
collect_calls.clear()
with mock.patch.object(SNMPClient, "_ping", fake_ping), mock.patch.object(SNMPClient, "collect", fake_real_collect):
    with Session(engine) as s:
        collect_fleet(s, mode="real", max_workers=3)

check_true("grupo so-etiqueta (10.0.0.4) so fez ping", "10.0.0.4" in ping_calls and "10.0.0.4" not in collect_calls)
check_true(
    "grupo misto (10.0.0.5) fez SNMP completo, nao so ping",
    "10.0.0.5" in collect_calls and "10.0.0.5" not in ping_calls,
)
check("SNMP completo so nos grupos nao-etiqueta", sorted(set(collect_calls)), ["10.0.0.1", "10.0.0.2", "10.0.0.5", "10.0.0.6"])

print("\n=== 6. scheduler: trava contra execucao concorrente preservada ===")
from app.services.scheduler import JOB_ID, shutdown_scheduler, start_scheduler  # noqa: E402
from app.config import settings  # noqa: E402

settings.collection_enabled = True
settings.collection_mode = "mock"
settings.allow_mock_collect = True
settings.collection_interval_minutes = 60
sched = start_scheduler()
job = sched.get_job(JOB_ID) if sched else None
check_true("scheduler iniciado", sched is not None)
check("max_instances=1 preservado", job.max_instances if job else None, 1)
shutdown_scheduler()

print(f"\nBanco de teste: {TEST_DB}")
print("RESULTADO:", "TODOS OS TESTES PASSARAM" if not failures else f"FALHAS: {failures}")
raise SystemExit(1 if failures else 0)
