"""
Fase 15 - GET /api/printers/with-status devolve a leitura mais recente por
impressora sem escanear o historico inteiro (era o gargalo de concorrencia
achado no teste de carga: 20 usuarios simultaneos -> p95 de ~8s por causa
de uma query sem LIMIT que crescia para sempre a cada ciclo de coleta).

Cobre: com centenas de leituras para uma unica impressora, a rota ainda
devolve exatamente a leitura de maior id (a mais recente) — nao a primeira
nem uma aleatoria — e o corpo da resposta bate com o que a leitura tem.

Executar:  .\\venv\\Scripts\\python.exe tests_with_status_latest.py
"""
import os
import tempfile
from datetime import datetime, timedelta

DB = os.path.join(tempfile.gettempdir(), "test_with_status_latest.db")
if os.path.exists(DB):
    os.remove(DB)
os.environ["DATABASE_URL"] = f"sqlite:///{DB}"

from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import Session  # noqa: E402

from app.database import create_db_and_tables, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models.printer import Printer, PrinterReading  # noqa: E402
from app.models.user import Role, User  # noqa: E402
from app.services.auth import create_access_token, hash_password  # noqa: E402

failures = []


def check(label, got, expected):
    ok = got == expected
    print(f"[{'OK ' if ok else 'FAIL'}] {label}: {got}" + ("" if ok else f" (esperado {expected})"))
    if not ok:
        failures.append(label)


create_db_and_tables()

with Session(engine) as s:
    p1 = Printer(server="srvtest", name="ComHistorico", ip="10.9.1.1", model="X", department="TI", active=True)
    p2 = Printer(server="srvtest", name="SemLeitura", ip="10.9.1.2", model="X", department="TI", active=True)
    s.add(p1)
    s.add(p2)
    s.add(User(email="withstatus.test@example.com", password_hash=hash_password("x"), name="With Status Test", role=Role.VIEWER.value))
    s.commit()
    s.refresh(p1)
    s.refresh(p2)
    P1, P2 = p1.id, p2.id

    # 300 leituras pra P1, contador sempre crescendo — a mais recente
    # (maior id) precisa ser a que a rota devolve, nao a primeira nem uma
    # leitura do meio.
    base = datetime.utcnow() - timedelta(days=1)
    for i in range(300):
        s.add(PrinterReading(
            printer_id=P1, status="online", page_count=1000 + i,
            toner_k=max(0, 90 - i // 10), timestamp=base + timedelta(minutes=i),
        ))
    s.commit()

TOKEN = create_access_token({"sub": "withstatus.test@example.com"})
client = TestClient(app)

resp = client.get("/api/printers/with-status", headers={"Authorization": f"Bearer {TOKEN}"})
check("status 200", resp.status_code, 200)
data = {p["id"]: p for p in resp.json()}

print("\n--- 1. impressora com 300 leituras: devolve a MAIS RECENTE (maior id, page_count=1299) ---")
check("page_count e o da ultima leitura (1000+299)", data[P1]["page_count"], 1299)
check("toner_k e o da ultima leitura (90 - 299//10)", data[P1]["toner"][0]["percent"] if data[P1]["toner"] else None, 61)

print("\n--- 2. impressora sem nenhuma leitura: offline, last_seen nulo ---")
check("status offline sem leitura", data[P2]["status"], "offline")
check("last_seen nulo sem leitura", data[P2]["last_seen"], None)

print("\n--- 3. quantidade de impressoras na resposta bate com o cadastro ---")
check("2 impressoras na resposta", len(data), 2)

print(f"\nBanco de teste: {DB}")
print("RESULTADO:", "TODOS OS TESTES PASSARAM" if not failures else f"FALHAS: {failures}")
raise SystemExit(1 if failures else 0)
