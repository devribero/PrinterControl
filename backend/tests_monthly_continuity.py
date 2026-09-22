r"""
Relatorio mensal: estimativa do comeco do mes e continuidade (21/09/2026).

Cobre, com datas fixas (marco/2026):

  1. equipamento cuja coleta comecou no meio do mes: os dias antes da
     primeira leitura sao estimados pela media diaria medida no mes;
  2. a estimativa parte do fim do ultimo periodo ja fechado do equipamento
     (a planilha fecha cada mes no dia 3 do seguinte), mesmo que esse
     fechamento esteja gravado em OUTRA fila do mesmo IP;
  3. equipamento com leitura ANTES do mes nao e estimado: continua a
     contagem de onde parou, e o salto da virada e dividido pelo tempo;
  4. menos de 1 dia medido nao estima (media seria ruido);
  5. o fechamento grava a parte estimada, e o endpoint a devolve em
     monthly_usage[].estimated.

    .\venv\Scripts\python.exe tests_monthly_continuity.py
"""
import os
import tempfile
from datetime import datetime, timedelta

DB = os.path.join(tempfile.gettempdir(), "test_monthly_continuity.db")
if os.path.exists(DB):
    os.remove(DB)
os.environ["DATABASE_URL"] = f"sqlite:///{DB}"
os.environ["ENVIRONMENT"] = "development"
os.environ["PRINT_SERVER_MODE"] = "mock"

from sqlmodel import Session, select  # noqa: E402

from app.database import create_db_and_tables, engine  # noqa: E402
from app.models.printer import Printer, PrinterMonthly, PrinterReading  # noqa: E402
from app.routes.printers import monthly_report  # noqa: E402
from app.services.monthly_report import close_pending_months, month_pages  # noqa: E402

failures = []


def check(label, got, expected):
    ok = got == expected
    print(f"[{'OK ' if ok else 'FAIL'}] {label}: {got!r}" + ("" if ok else f" (esperado {expected!r})"))
    if not ok:
        failures.append(label)


create_db_and_tables()
MARCO, ABRIL = datetime(2026, 3, 1), datetime(2026, 4, 1)

with Session(engine) as s:
    def fila(nome, ip):
        p = Printer(server="srv", name=nome, ip=ip, model="M", department="TI", active=True)
        s.add(p)
        s.commit()
        s.refresh(p)
        return p.id

    def leituras(pid, pontos):
        for contador, ts in pontos:
            s.add(PrinterReading(printer_id=pid, status="online", page_count=contador, timestamp=ts))
        s.commit()

    # 1) coleta comeca dia 11; 700 paginas nos primeiros 7 dias -> 100/dia
    #    (a media da estimativa usa so essa janela). 1000 medidas no total.
    a = fila("A_comeca_dia_11", "10.8.0.1")
    leituras(a, [(5000, MARCO + timedelta(days=10)), (5700, MARCO + timedelta(days=17)), (6000, MARCO + timedelta(days=20))])

    # 2) mesmo ritmo, mas o equipamento tem fevereiro fechado ate 04/03 (como
    #    a planilha faz), gravado na OUTRA fila do mesmo IP.
    b1, b2 = fila("B_fila_1", "10.8.0.2"), fila("B_fila_2", "10.8.0.2")
    s.add(PrinterMonthly(printer_id=b2, month="2026-02", pages_printed=999,
                          month_start=datetime(2026, 2, 4), month_end=datetime(2026, 3, 4)))
    s.commit()
    leituras(b1, [(5000, MARCO + timedelta(days=10)), (5700, MARCO + timedelta(days=17)), (6000, MARCO + timedelta(days=20))])

    # 3) tem leitura em fevereiro: continua a contagem, sem estimativa.
    c = fila("C_continua", "10.8.0.3")
    leituras(c, [(1000, datetime(2026, 2, 27)), (1300, MARCO + timedelta(days=2)), (1500, MARCO + timedelta(days=5))])

    # 4) so 2 horas medidas: sem estimativa.
    d = fila("D_pouco_medido", "10.8.0.4")
    leituras(d, [(100, MARCO + timedelta(days=15)), (130, MARCO + timedelta(days=15, hours=2))])

    mes = month_pages(s, MARCO, ABRIL)

print("--- 1. coleta comecou no meio do mes ---")
check("medido 1000 + estimado 10 dias x 100/dia", mes.pages.get(a), 2000)
check("parte estimada", mes.estimated.get(a), 1000)

print("\n--- 1b. imprimir mais depois da janela de 7 dias: +1 por pagina, estimativa congelada ---")
with Session(engine) as s:
    s.add(PrinterReading(printer_id=a, status="online", page_count=6003, timestamp=MARCO + timedelta(days=21)))
    s.commit()
    mes_depois = month_pages(s, MARCO, ABRIL)
check("3 paginas a mais -> total sobe 3", mes_depois.pages.get(a), 2003)
check("estimativa nao mudou", mes_depois.estimated.get(a), 1000)

print("\n--- 2. estimativa parte do fim do periodo fechado (04/03), ate em outra fila ---")
check("medido 1000 + estimado 7 dias x 100/dia", mes.pages.get(b1), 1700)
check("parte estimada", mes.estimated.get(b1), 700)
check("uma fila so por equipamento", b2 in mes.pages, False)

print("\n--- 3. leitura antes do mes: continuidade, sem estimativa ---")
# Salto 1000 -> 1300 atravessa a virada: 27/02 00h ate 03/03 00h = 4 dias,
# 2 deles em marco -> metade (150) fica em marco. Mais 200 dentro do mes.
check("150 da virada + 200 do mes", mes.pages.get(c), 350)
check("nada estimado", mes.estimated.get(c), None)

print("\n--- 4. menos de 1 dia medido: sem estimativa ---")
check("so o medido", mes.pages.get(d), 30)
check("nada estimado", mes.estimated.get(d), None)

print("\n--- 5. fechamento grava a estimativa e o endpoint a devolve ---")
with Session(engine) as s:
    # Leitura em abril: a coleta voltou depois do fim de marco, entao ele fecha.
    s.add(PrinterReading(printer_id=a, status="online", page_count=6100, timestamp=ABRIL + timedelta(days=1)))
    s.commit()
    fechados = close_pending_months(s, now=ABRIL + timedelta(days=2))
    linha_a = s.exec(select(PrinterMonthly).where(PrinterMonthly.printer_id == a).where(PrinterMonthly.month == "2026-03")).first()
    relatorio = monthly_report(months=60, session=s)

check("marco fechado", "2026-03" in fechados, True)
check("estimativa gravada no fechamento", linha_a.estimated_pages if linha_a else None, 1000)
marco = next((m for m in relatorio["monthly_usage"] if m["period"] == "2026-03"), None)
check("endpoint devolve a parte estimada do mes", marco["estimated"] if marco else None, 1000 + 700)
check("marco nao esta em andamento", marco["in_progress"] if marco else None, False)

print()
if failures:
    print(f"FALHOU: {failures}")
    raise SystemExit(1)
print("Todos os testes de estimativa e continuidade passaram.")
