r"""
Relatorio mensal por EQUIPAMENTO, nao por fila (21/09/2026).

Filas que dividem o mesmo IP sao o mesmo equipamento: a coleta grava a
mesma leitura em cada uma, e somar por fila contava o mesmo contador varias
vezes (77% a mais em setembro/2026). Cobre:

  - 3 filas num IP contam uma vez so;
  - a fila representante e a de maior total (a cadastrada depois tem menos
    leituras), empate fica com o menor id;
  - filas sem IP utilizavel continuam cada uma por si;
  - o endpoint soma o mes uma vez por equipamento.

    .\venv\Scripts\python.exe tests_monthly_devices.py
"""
import os
import tempfile
from datetime import datetime, timedelta

DB = os.path.join(tempfile.gettempdir(), "test_monthly_devices.db")
if os.path.exists(DB):
    os.remove(DB)
os.environ["DATABASE_URL"] = f"sqlite:///{DB}"
os.environ["ENVIRONMENT"] = "development"
os.environ["PRINT_SERVER_MODE"] = "mock"

from sqlmodel import Session  # noqa: E402

from app.database import create_db_and_tables, engine  # noqa: E402
from app.models.printer import Printer, PrinterReading  # noqa: E402
from app.services.monthly_report import month_bounds, pages_from_readings  # noqa: E402

failures = []


def check(label, got, expected):
    ok = got == expected
    print(f"[{'OK ' if ok else 'FAIL'}] {label}: {got}" + ("" if ok else f" (esperado {expected})"))
    if not ok:
        failures.append(label)


create_db_and_tables()
agora = datetime.utcnow()
inicio, fim = month_bounds(agora)
t0 = inicio + timedelta(hours=1)

with Session(engine) as s:
    def fila(nome, ip, dept="TI"):
        p = Printer(server="srv", name=nome, ip=ip, model="M", department=dept, active=True)
        s.add(p)
        s.commit()
        s.refresh(p)
        return p.id

    # Um equipamento com 3 filas; a terceira foi cadastrada depois e perdeu
    # a primeira leitura.
    a1, a2, a3 = fila("A_fila1", "10.9.0.1"), fila("A_fila2", "10.9.0.1"), fila("A_fila3", "10.9.0.1")
    for i, contador in enumerate((1000, 1200, 1500)):
        for pid in (a1, a2):
            s.add(PrinterReading(printer_id=pid, status="online", page_count=contador, timestamp=t0 + timedelta(hours=i)))
        if i > 0:
            s.add(PrinterReading(printer_id=a3, status="online", page_count=contador, timestamp=t0 + timedelta(hours=i)))

    # Equipamento sozinho no seu IP.
    b = fila("B", "10.9.0.2")
    for i, contador in enumerate((50, 80)):
        s.add(PrinterReading(printer_id=b, status="online", page_count=contador, timestamp=t0 + timedelta(hours=i)))

    # Duas filas sem IP utilizavel: nao da para saber se sao o mesmo
    # equipamento, entao cada uma conta por si.
    u1, u2 = fila("USB_1", "USB001"), fila("USB_2", "")
    for pid in (u1, u2):
        for i, contador in enumerate((10, 30)):
            s.add(PrinterReading(printer_id=pid, status="online", page_count=contador, timestamp=t0 + timedelta(hours=i)))
    s.commit()

    r = pages_from_readings(s, inicio, fim)

check("equipamento de 3 filas aparece uma vez", len([p for p in (a1, a2, a3) if p in r]), 1)
check("representante e a de maior total, empate no menor id", a1 in r, True)
check("paginas do equipamento contadas uma vez (1500-1000)", r.get(a1), 500)
check("fila cadastrada depois nao entra", a3 in r, False)
check("equipamento sozinho no IP", r.get(b), 30)
check("fila sem IP (USB001) conta por si", r.get(u1), 20)
check("fila sem IP (vazio) conta por si", r.get(u2), 20)
check("total = 500 + 30 + 20 + 20", sum(r.values()), 570)

print()
if failures:
    print(f"FALHOU: {failures}")
    raise SystemExit(1)
print("Todos os testes de relatorio por equipamento passaram.")
