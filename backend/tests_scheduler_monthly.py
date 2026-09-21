r"""
Fase 12 - fechamento mensal automatico do scheduler.

Cobre: os dois jobs novos (snapshot dia 1, fechamento ultimo dia) sao
registrados com o cron certo quando o scheduler liga; run_month_close()
fecha os meses JA TERMINADOS em PrinterMonthly e nunca o mes em andamento;
mes fechado e definitivo (nao duplica nem recalcula); meses importados de
planilha nunca sao tocados; e meses que ninguem fechou (maquina desligada
na virada) sao fechados com atraso.

Executar:  .\\venv\\Scripts\\python.exe tests_scheduler_monthly.py
"""
import asyncio
import os
import tempfile
from datetime import datetime, timedelta
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

# Python 3.14 nao cria mais event loop implicito: AsyncIOScheduler.start()
# fora de um loop quebrava o teste antes de qualquer verificacao.
asyncio.set_event_loop(asyncio.new_event_loop())

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

print("\n--- 2. run_month_close() forca coleta final e fecha o mes que TERMINOU ---")
# run_collection_cycle mockado aqui: em modo mock ele grava um contador FIXO
# (online_mono = sempre 5000), o que contaminaria as contas abaixo. O
# proprio disparo de run_collection_cycle() e verificado pelo call_count;
# a agregacao e testada isolada, com leituras que eu controlo.
#
# 21/09/2026: o job fechava "o mes de agora" em UTC — que, disparado as
# 23:50 de Brasilia, ja e o mes SEGUINTE. Agora fecha os meses terminados
# que faltam. As leituras abaixo ficam no mes ANTERIOR ao corrente.
agora = datetime.utcnow()
inicio_atual = datetime(agora.year, agora.month, 1)
mes_passado = inicio_atual - timedelta(days=10)  # algum dia do mes anterior
PASSADO = month_period(mes_passado)
ATUAL = month_period(agora)

with Session(engine) as s:
    s.add(PrinterReading(printer_id=P1, status="online", page_count=1000, timestamp=mes_passado))
    s.add(PrinterReading(printer_id=P1, status="online", page_count=1400, timestamp=mes_passado + timedelta(hours=1)))
    # Mes corrente, ainda em andamento: NAO pode ser congelado.
    s.add(PrinterReading(printer_id=P1, status="online", page_count=2000, timestamp=agora))
    s.add(PrinterReading(printer_id=P1, status="online", page_count=2300, timestamp=agora))
    s.commit()

with mock.patch.object(scheduler, "run_collection_cycle") as cycle_mock:
    scheduler.run_month_close()
check("run_month_close() forca uma coleta final", cycle_mock.call_count, 1)


def linhas(periodo):
    with Session(engine) as s:
        return s.exec(
            select(PrinterMonthly).where(PrinterMonthly.printer_id == P1).where(PrinterMonthly.month == periodo)
        ).all()


check("mes anterior congelado", len(linhas(PASSADO)), 1)
check("pages_printed do mes anterior = soma dos saltos (1400-1000)", linhas(PASSADO)[0].pages_printed, 400)
check("mes corrente, ainda em andamento, NAO e congelado", len(linhas(ATUAL)), 0)

print("\n--- 3. rodar de novo nao duplica nem recalcula mes fechado ---")
with Session(engine) as s:
    # Leitura atrasada caindo no mes ja fechado: mes fechado e definitivo.
    s.add(PrinterReading(printer_id=P1, status="online", page_count=1900, timestamp=mes_passado + timedelta(hours=2)))
    s.commit()

with mock.patch.object(scheduler, "run_collection_cycle"):
    scheduler.run_month_close()

check("continua uma unica linha pro mes (nao duplicou)", len(linhas(PASSADO)), 1)
check("mes fechado nao foi recalculado", linhas(PASSADO)[0].pages_printed, 400)

print("\n--- 4. mes anterior ja fechado (ex.: importado de planilha) fica intocado ---")
with Session(engine) as s:
    s.add(PrinterMonthly(printer_id=P1, month="2026-01", pages_printed=12345,
                          month_start=datetime(2026, 1, 1), month_end=datetime(2026, 2, 1)))
    s.commit()

with mock.patch.object(scheduler, "run_collection_cycle"):
    scheduler.run_month_close()

check("mes de Janeiro/26 nao foi alterado pelo fechamento", linhas("2026-01")[0].pages_printed, 12345)

print("\n--- 5. maquina desligada na virada: fecha com atraso, varios meses ---")
with Session(engine) as s:
    for dias_atras, contadores in ((75, (100, 350)), (45, (500, 520))):
        dia = inicio_atual - timedelta(days=dias_atras)
        for i, c in enumerate(contadores):
            s.add(PrinterReading(printer_id=P1, status="online", page_count=c, timestamp=dia + timedelta(hours=i)))
    s.commit()

scheduler.run_close_pending_months()
for dias_atras, esperado in ((75, 250), (45, 20)):
    periodo = month_period(inicio_atual - timedelta(days=dias_atras))
    got = linhas(periodo)
    check(f"mes {periodo} fechado com atraso", got[0].pages_printed if got else None, esperado)

print(f"\nBanco de teste: {DB}")
print("RESULTADO:", "TODOS OS TESTES PASSARAM" if not failures else f"FALHAS: {failures}")
raise SystemExit(1 if failures else 0)
