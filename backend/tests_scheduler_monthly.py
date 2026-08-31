"""
Fase 12 - fechamento mensal automatico do scheduler.

Cobre: os dois jobs novos (snapshot dia 1, fechamento ultimo dia) sao
registrados com o cron certo quando o scheduler liga; run_month_close()
congela o mes corrente em PrinterMonthly; rodar de novo no mesmo mes
ATUALIZA em vez de duplicar (upsert por printer_id+month); meses
anteriores (fechados antes, ou importados de planilha) nunca sao tocados.

Executar:  .\\venv\\Scripts\\python.exe tests_scheduler_monthly.py
"""
import os
import tempfile
from datetime import datetime
from unittest import mock

DB = os.path.join(tempfile.gettempdir(), "test_scheduler_monthly.db")
if os.path.exists(DB):
    os.remove(DB)
os.environ["DATABASE_URL"] = f"sqlite:///{DB}"
os.environ["COLLECTION_ENABLED"] = "true"
os.environ["COLLECTION_MODE"] = "mock"
os.environ["ALLOW_MOCK_COLLECT"] = "true"
os.environ["COLLECTION_SCENARIO"] = "online_mono"

from sqlmodel import Session, select  # noqa: E402

from app.database import create_db_and_tables, engine  # noqa: E402
from app.models.printer import Printer, PrinterMonthly, PrinterReading  # noqa: E402
from app.services import scheduler  # noqa: E402
from app.services.monthly_report import month_period  # noqa: E402

failures = []


def check(label, got, expected):
    ok = got == expected
    print(f"[{'OK ' if ok else 'FAIL'}] {label}: {got}" + ("" if ok else f" (esperado {expected})"))
    if not ok:
        failures.append(label)


create_db_and_tables()

with Session(engine) as s:
    p1 = Printer(server="srvtest", name="Fechamento_A", ip="10.6.6.1", model="X", department="TI", active=True)
    s.add(p1)
    s.commit()
    s.refresh(p1)
    P1 = p1.id

print("--- 1. start_scheduler registra os dois jobs novos ---")
sched = scheduler.start_scheduler()
check("scheduler ligou", sched is not None, True)
job_start = sched.get_job(scheduler.MONTH_START_JOB_ID)
job_close = sched.get_job(scheduler.MONTH_CLOSE_JOB_ID)
check("job de snapshot de inicio de mes existe", job_start is not None, True)
check("job de fechamento de mes existe", job_close is not None, True)
check("snapshot roda dia 1", str(job_start.trigger.fields[2]), "1")  # indice 2 = campo 'day' do CronTrigger
check("fechamento roda no ultimo dia (day='last')", str(job_close.trigger.fields[2]), "last")
scheduler.shutdown_scheduler()

print("\n--- 2. run_month_close() forca uma coleta final e congela o mes corrente ---")
# run_collection_cycle mockado aqui: em modo mock ele grava um contador FIXO
# (online_mono = sempre 5000), o que contaminaria as contas abaixo. O
# proprio disparo de run_collection_cycle() e verificado pelo call_count;
# a agregacao e testada isolada, com leituras que eu controlo.
with Session(engine) as s:
    hoje = datetime.utcnow()
    s.add(PrinterReading(printer_id=P1, status="online", page_count=1000, timestamp=hoje))
    s.add(PrinterReading(printer_id=P1, status="online", page_count=1400, timestamp=hoje))
    s.commit()

with mock.patch.object(scheduler, "run_collection_cycle") as cycle_mock:
    scheduler.run_month_close()
check("run_month_close() forca uma coleta final", cycle_mock.call_count, 1)

periodo = month_period(datetime.utcnow())
with Session(engine) as s:
    row = s.exec(
        select(PrinterMonthly).where(PrinterMonthly.printer_id == P1).where(PrinterMonthly.month == periodo)
    ).first()
check("PrinterMonthly criado pro mes corrente", row is not None, True)
check("pages_printed = maior-menor contador", row.pages_printed if row else None, 400)

print("\n--- 3. rodar de novo no mesmo mes ATUALIZA, nao duplica ---")
with Session(engine) as s:
    s.add(PrinterReading(printer_id=P1, status="online", page_count=1900, timestamp=datetime.utcnow()))
    s.commit()

with mock.patch.object(scheduler, "run_collection_cycle"):
    scheduler.run_month_close()

with Session(engine) as s:
    rows = s.exec(
        select(PrinterMonthly).where(PrinterMonthly.printer_id == P1).where(PrinterMonthly.month == periodo)
    ).all()
check("continua uma unica linha pro mes (upsert, nao duplicou)", len(rows), 1)
check("valor atualizado com a nova leitura (1900-1000)", rows[0].pages_printed, 900)

print("\n--- 4. mes anterior ja fechado (ex.: importado de planilha) fica intocado ---")
with Session(engine) as s:
    s.add(PrinterMonthly(printer_id=P1, month="2026-01", pages_printed=12345,
                          month_start=datetime(2026, 1, 1), month_end=datetime(2026, 2, 1)))
    s.commit()

with mock.patch.object(scheduler, "run_collection_cycle"):
    scheduler.run_month_close()

with Session(engine) as s:
    antigo = s.exec(
        select(PrinterMonthly).where(PrinterMonthly.printer_id == P1).where(PrinterMonthly.month == "2026-01")
    ).first()
check("mes de Janeiro/26 nao foi alterado pelo fechamento do mes corrente", antigo.pages_printed, 12345)

print(f"\nBanco de teste: {DB}")
print("RESULTADO:", "TODOS OS TESTES PASSARAM" if not failures else f"FALHAS: {failures}")
raise SystemExit(1 if failures else 0)
