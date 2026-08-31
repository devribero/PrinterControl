"""
Fase 12 - relatorio mensal: mescla PrinterMonthly (meses fechados, via
importacao de planilha ou fechamento automatico) com calculo ao vivo
(mes em andamento, a partir de PrinterReading). Cobre tambem o total por
departamento, que passou a vir do backend em vez de mockup fixo.

Executar:  .\\venv\\Scripts\\python.exe tests_monthly_report.py
"""
import os
import tempfile
from datetime import datetime

DB = os.path.join(tempfile.gettempdir(), "test_monthly_report.db")
if os.path.exists(DB):
    os.remove(DB)
os.environ["DATABASE_URL"] = f"sqlite:///{DB}"

from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import Session  # noqa: E402

from app.database import create_db_and_tables, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models.printer import Printer, PrinterMonthly, PrinterReading  # noqa: E402
from app.models.user import Role, User  # noqa: E402
from app.services.auth import create_access_token, hash_password  # noqa: E402
from app.services.monthly_report import month_period  # noqa: E402

failures = []


def check(label, got, expected):
    ok = got == expected
    print(f"[{'OK ' if ok else 'FAIL'}] {label}: {got}" + ("" if ok else f" (esperado {expected})"))
    if not ok:
        failures.append(label)


create_db_and_tables()

with Session(engine) as s:
    p1 = Printer(server="srvtest", name="Mensal_A", ip="10.5.5.1", model="X", department="Financeiro", active=True)
    p2 = Printer(server="srvtest", name="Mensal_B", ip="10.5.5.2", model="X", department="Financeiro", active=True)
    p3 = Printer(server="srvtest", name="Mensal_C", ip="10.5.5.3", model="X", department="RH", active=True)
    s.add(p1)
    s.add(p2)
    s.add(p3)
    s.add(User(email="mensal.test@example.com", password_hash=hash_password("x"), name="Mensal Test", role=Role.VIEWER.value))
    s.commit()
    s.refresh(p1)
    s.refresh(p2)
    s.refresh(p3)
    P1, P2, P3 = p1.id, p2.id, p3.id

    hoje = datetime.utcnow()
    mes_atual = month_period(hoje)

    # Mes fechado (Julho/26, importado de planilha ou fechado pelo scheduler)
    # — SO existe em PrinterMonthly, nao ha PrinterReading nenhuma pra ele.
    s.add(PrinterMonthly(printer_id=P1, month="2026-07", pages_printed=1000,
                          month_start=datetime(2026, 7, 1), month_end=datetime(2026, 8, 1)))
    s.add(PrinterMonthly(printer_id=P3, month="2026-07", pages_printed=200,
                          month_start=datetime(2026, 7, 1), month_end=datetime(2026, 8, 1)))

    # Mes atual, em andamento: so leituras (P1 e P2), sem fechamento ainda.
    s.add(PrinterReading(printer_id=P1, status="online", page_count=5000, timestamp=hoje))
    s.add(PrinterReading(printer_id=P1, status="online", page_count=5300, timestamp=hoje))
    s.add(PrinterReading(printer_id=P2, status="online", page_count=800, timestamp=hoje))
    s.add(PrinterReading(printer_id=P2, status="online", page_count=950, timestamp=hoje))

    # Mes atual com AMBOS PrinterMonthly (autoridade) e leituras — o valor
    # gravado em PrinterMonthly deve vencer, nao o calculado ao vivo.
    s.add(PrinterMonthly(printer_id=P3, month=mes_atual, pages_printed=777,
                          month_start=hoje.replace(day=1), month_end=hoje))
    s.add(PrinterReading(printer_id=P3, status="online", page_count=1, timestamp=hoje))
    s.add(PrinterReading(printer_id=P3, status="online", page_count=99999, timestamp=hoje))

    s.commit()

TOKEN = create_access_token({"sub": "mensal.test@example.com"})
client = TestClient(app)

resp = client.get("/api/printers/monthly-report?months=12", headers={"Authorization": f"Bearer {TOKEN}"})
check("status 200", resp.status_code, 200)
data = resp.json()

by_ip = {p["ip"]: p for p in data["printers"]}

print("\n--- 1. mes fechado (PrinterMonthly, sem nenhuma leitura) ---")
p1_months = {m["period"]: m["pages"] for m in by_ip["10.5.5.1"]["monthly_pages"]}
check("Julho/26 de P1 vem do fechamento", p1_months.get("2026-07"), 1000)

print("\n--- 2. mes em andamento calculado ao vivo (sem fechamento) ---")
p1_atual = {m["period"]: m["pages"] for m in by_ip["10.5.5.1"]["monthly_pages"]}.get(mes_atual)
check("P1 mes atual = maior-menor contador (5300-5000)", p1_atual, 300)
p2_atual = {m["period"]: m["pages"] for m in by_ip["10.5.5.2"]["monthly_pages"]}.get(mes_atual)
check("P2 mes atual = maior-menor contador (950-800)", p2_atual, 150)

print("\n--- 3. PrinterMonthly vence quando os dois existem pro mesmo mes ---")
p3_atual = {m["period"]: m["pages"] for m in by_ip["10.5.5.3"]["monthly_pages"]}.get(mes_atual)
check("P3 mes atual usa o fechado (777), ignora leituras (99998)", p3_atual, 777)

print("\n--- 4. total da empresa por mes soma os dois printers ---")
usage_by_period = {m["period"]: m["pages"] for m in data["monthly_usage"]}
check("Julho/26 = so P1 (P2/P3 sem dado nesse mes na conta = so P1+P3=1000+200)", usage_by_period.get("2026-07"), 1200)
check(f"{mes_atual} = P1(300)+P2(150)+P3(777, fechado)", usage_by_period.get(mes_atual), 300 + 150 + 777)

print("\n--- 5. total por departamento ---")
dept_by_name = {d["department"]: d for d in data["department_usage"]}
check("Financeiro existe", "Financeiro" in dept_by_name, True)
check("RH existe", "RH" in dept_by_name, True)
financeiro_periods = {m["period"]: m["pages"] for m in dept_by_name["Financeiro"]["monthly"]}
check("Financeiro/Julho = so P1 (1000)", financeiro_periods.get("2026-07"), 1000)
check("Financeiro total = P1(1000+300) + P2(150)", dept_by_name["Financeiro"]["total"], 1000 + 300 + 150)
rh_periods = {m["period"]: m["pages"] for m in dept_by_name["RH"]["monthly"]}
check("RH/Julho = P3 (200)", rh_periods.get("2026-07"), 200)
check("RH total = P3(200+777)", dept_by_name["RH"]["total"], 200 + 777)

print(f"\nBanco de teste: {DB}")
print("RESULTADO:", "TODOS OS TESTES PASSARAM" if not failures else f"FALHAS: {failures}")
raise SystemExit(1 if failures else 0)
