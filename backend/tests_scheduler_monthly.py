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
# run_collection_cycle mockado: em modo mock ele grava um contador FIXO
# (online_mono = sempre 5000), o que contaminaria as contas abaixo. O
# proprio disparo de run_collection_cycle() e verificado pelo call_count.
#
# 21/09/2026: leituras sempre em ordem cronologica (como a coleta real grava)
# e o total esperado calculado pela regra de continuidade: o salto entre a
# ultima leitura de um mes e a primeira do seguinte e dividido entre os dois
# na proporcao do tempo (ver monthly_report.month_pages). Leituras com menos
# de 1 dia entre si, para a estimativa do comeco do mes nao entrar aqui — ela
# tem teste proprio em tests_monthly_continuity.py.
agora = datetime.utcnow()
inicio_atual = datetime(agora.year, agora.month, 1)
inicio_anterior = datetime((inicio_atual - timedelta(days=1)).year, (inicio_atual - timedelta(days=1)).month, 1)
PASSADO = month_period(inicio_anterior)
ATUAL = month_period(agora)


def fracao(a, b, ini, fim):
    return max(0.0, (min(b, fim) - max(a, ini)).total_seconds()) / (b - a).total_seconds()


def linhas(printer_id, periodo):
    with Session(engine) as s:
        return s.exec(
            select(PrinterMonthly).where(PrinterMonthly.printer_id == printer_id).where(PrinterMonthly.month == periodo)
        ).all()


t1 = inicio_anterior + timedelta(days=2)
t2 = t1 + timedelta(hours=1)
t_atual = inicio_atual + (agora - inicio_atual) / 2  # dentro do mes corrente e no passado

with Session(engine) as s:
    s.add(PrinterReading(printer_id=P1, status="online", page_count=1000, timestamp=t1))
    s.add(PrinterReading(printer_id=P1, status="online", page_count=1400, timestamp=t2))
    s.commit()

print("\n--- 2a. sem leitura DEPOIS do fim do mes, ele ainda nao fecha ---")
scheduler.run_close_pending_months()
check("mes anterior ainda aberto (falta o pedaco final)", len(linhas(P1, PASSADO)), 0)

with Session(engine) as s:
    s.add(PrinterReading(printer_id=P1, status="online", page_count=1500, timestamp=t_atual))
    s.commit()

with mock.patch.object(scheduler, "run_collection_cycle") as cycle_mock:
    scheduler.run_month_close()
check("run_month_close() forca uma coleta final", cycle_mock.call_count, 1)

esperado = round(400 + 100 * fracao(t2, t_atual, inicio_anterior, inicio_atual))
check("mes anterior congelado", len(linhas(P1, PASSADO)), 1)
check("total = saltos do mes + parte proporcional da virada", linhas(P1, PASSADO)[0].pages_printed, esperado)
check("mes corrente, ainda em andamento, NAO e congelado", len(linhas(P1, ATUAL)), 0)

print("\n--- 3. rodar de novo nao duplica nem recalcula mes fechado ---")
with mock.patch.object(scheduler, "run_collection_cycle"):
    scheduler.run_month_close()
check("continua uma unica linha pro mes (nao duplicou)", len(linhas(P1, PASSADO)), 1)
check("mes fechado nao foi recalculado", linhas(P1, PASSADO)[0].pages_printed, esperado)

print("\n--- 4. mes anterior ja fechado (ex.: importado de planilha) fica intocado ---")
with Session(engine) as s:
    s.add(PrinterMonthly(printer_id=P1, month="2026-01", pages_printed=12345,
                          month_start=datetime(2026, 1, 1), month_end=datetime(2026, 2, 1)))
    s.commit()
with mock.patch.object(scheduler, "run_collection_cycle"):
    scheduler.run_month_close()
check("mes de Janeiro/26 nao foi alterado pelo fechamento", linhas(P1, "2026-01")[0].pages_printed, 12345)

print("\n--- 5. maquina desligada: dois meses fechados com atraso, sem perder a virada ---")
# Outra impressora (outro IP), leituras em ordem: dois meses atras, mes
# passado, e agora. Os dois meses ja terminados estao abertos; um unico
# fechamento pega os dois, e cada um leva sua parte dos saltos que
# atravessam as viradas.
with Session(engine) as s:
    p3 = Printer(server="srvtest", name="Fechamento_C", ip="10.6.6.3", model="X", department="TI", active=True)
    s.add(p3)
    s.commit()
    s.refresh(p3)
    P3 = p3.id

inicio_ha_2 = datetime((inicio_anterior - timedelta(days=1)).year, (inicio_anterior - timedelta(days=1)).month, 1)
HA_2 = month_period(inicio_ha_2)
pontos = [
    (100, inicio_ha_2 + timedelta(days=5)),
    (350, inicio_ha_2 + timedelta(days=5, hours=1)),
    (500, inicio_anterior + timedelta(days=5)),
    (520, inicio_anterior + timedelta(days=5, hours=1)),
    (600, t_atual),
]
with Session(engine) as s:
    for contador, ts in pontos:
        s.add(PrinterReading(printer_id=P3, status="online", page_count=contador, timestamp=ts))
    # Tira os fechamentos ja gravados, para os dois meses estarem pendentes
    # no banco de teste (o mes passado foi fechado no passo 2 para P1).
    for linha in s.exec(select(PrinterMonthly).where(PrinterMonthly.month.in_([HA_2, PASSADO]))).all():
        s.delete(linha)
    s.commit()

scheduler.run_close_pending_months()


def esperado_mes(ini, fim):
    total = 0.0
    for (c_a, t_a), (c_b, t_b) in zip(pontos, pontos[1:]):
        if c_b > c_a:
            total += (c_b - c_a) * fracao(t_a, t_b, ini, fim)
    return round(total)


got_ha_2 = linhas(P3, HA_2)
got_passado = linhas(P3, PASSADO)
check(f"mes {HA_2} fechado com atraso", got_ha_2[0].pages_printed if got_ha_2 else None,
      esperado_mes(inicio_ha_2, inicio_anterior))
check(f"mes {PASSADO} fechado com atraso", got_passado[0].pages_printed if got_passado else None,
      esperado_mes(inicio_anterior, inicio_atual))

print(f"\nBanco de teste: {DB}")
print("RESULTADO:", "TODOS OS TESTES PASSARAM" if not failures else f"FALHAS: {failures}")
raise SystemExit(1 if failures else 0)
