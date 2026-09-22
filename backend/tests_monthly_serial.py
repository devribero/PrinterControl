r"""
Historico mensal segue o numero de serie quando o equipamento muda de IP
(22/09/2026).

  1. folha de teste: meses do cadastro antigo (mesmo serie) completam o
     historico, sem sobrescrever o que a fila atual ja tem;
  2. sem serie confirmado por SNMP, nada e emprestado;
  3. painel (/monthly-report): a impressora ativa ganha os meses do cadastro
     INATIVO, e o total da frota nao muda.

    .\venv\Scripts\python.exe tests_monthly_serial.py
"""
import os
import tempfile
from datetime import datetime, timedelta

DB = os.path.join(tempfile.gettempdir(), "test_monthly_serial.db")
if os.path.exists(DB):
    os.remove(DB)
os.environ["DATABASE_URL"] = f"sqlite:///{DB}"
os.environ["ENVIRONMENT"] = "development"

from sqlmodel import Session  # noqa: E402

from app.database import create_db_and_tables, engine  # noqa: E402
from app.models.printer import Printer, PrinterMonthly, PrinterReading  # noqa: E402
from app.routes.printers import monthly_report  # noqa: E402
from app.services.monthly_report import device_monthly_history  # noqa: E402

failures = []


def check(label, got, expected):
    ok = got == expected
    print(f"[{'OK ' if ok else 'FAIL'}] {label}: {got!r}" + ("" if ok else f" (esperado {expected!r})"))
    if not ok:
        failures.append(label)


create_db_and_tables()
agora = datetime.utcnow()
with Session(engine) as s:
    antiga = Printer(server="", name="ANTIGA", ip="10.9.9.1", model="M", serial_number="SER123", active=False)
    atual = Printer(server="srv", name="ATUAL", ip="10.9.9.2", model="M", serial_number="ser123 ",
                    active=True, snmp_updated_at=agora)
    sem_snmp = Printer(server="srv", name="SEM_SNMP", ip="10.9.9.3", model="M", serial_number="SER123", active=True)
    s.add_all([antiga, atual, sem_snmp])
    s.commit()
    for p in (antiga, atual, sem_snmp):
        s.refresh(p)
    ids = {"antiga": antiga.id, "atual": atual.id, "sem_snmp": sem_snmp.id}
    for mes, paginas in (("2026-06", 600), ("2026-07", 700)):
        ano, m = map(int, mes.split("-"))
        s.add(PrinterMonthly(printer_id=antiga.id, month=mes, pages_printed=paginas,
                             month_start=datetime(ano, m, 1), month_end=datetime(ano, m + 1, 1)))
    # A fila atual ja tem julho proprio: o emprestado nao pode sobrescrever.
    s.add(PrinterMonthly(printer_id=atual.id, month="2026-07", pages_printed=777,
                         month_start=datetime(2026, 7, 1), month_end=datetime(2026, 8, 1)))
    for pid in (atual.id, sem_snmp.id):
        s.add(PrinterReading(printer_id=pid, status="online", page_count=1000, timestamp=agora - timedelta(days=2)))
        s.add(PrinterReading(printer_id=pid, status="online", page_count=1050, timestamp=agora - timedelta(hours=1)))
    s.commit()

    print("--- 1. folha de teste ---")
    hist = {rotulo: paginas for rotulo, paginas, _, _ in device_monthly_history(s, ids["atual"])}
    check("junho veio do cadastro antigo", hist.get("Jun/26"), 600)
    check("julho proprio nao foi sobrescrito", hist.get("Jul/26"), 777)

    print("\n--- 2. sem serie confirmado por SNMP ---")
    hist2 = {rotulo for rotulo, _, _, _ in device_monthly_history(s, ids["sem_snmp"])}
    check("nada emprestado", "Jun/26" in hist2, False)

    print("\n--- 3. painel ---")
    r = monthly_report(months=24, session=s)
    por_id = {p["id"]: {m["period"]: m["pages"] for m in p["monthly_pages"]} for p in r["printers"]}
    check("impressora ativa ganha junho", por_id.get(ids["atual"], {}).get("2026-06"), 600)
    check("julho proprio mantido", por_id.get(ids["atual"], {}).get("2026-07"), 777)
    junho = next((m["pages"] for m in r["monthly_usage"] if m["period"] == "2026-06"), None)
    check("total de junho da frota nao dobra", junho, 600)

print()
if failures:
    print(f"FALHOU: {failures}")
    raise SystemExit(1)
print("Todos os testes de historico por numero de serie passaram.")
