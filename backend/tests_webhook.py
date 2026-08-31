"""
Etapa 6 - webhook de alerta critico de toner.

Banco SQLite temporario e ISOLADO (nao o real). NENHUMA chamada HTTP real e
feita — httpx.post e sempre mockado. Nenhuma URL de webhook real aparece
aqui: uso apenas "http://example.test/fake-webhook", um dominio reservado
para documentacao/testes (RFC 2606), nunca resolvido de verdade.

Executar:  .\\venv\\Scripts\\python.exe tests_webhook.py
"""
import os
import tempfile
from unittest import mock

TEST_DB = os.path.join(tempfile.gettempdir(), "test_webhook.db")
if os.path.exists(TEST_DB):
    os.remove(TEST_DB)
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.replace(os.sep, '/')}"

from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import Session  # noqa: E402

from app.config import settings  # noqa: E402
from app.database import create_db_and_tables, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models.alert import Alert  # noqa: E402
from app.models.printer import Printer, PrinterReading  # noqa: E402
from app.models.user import Role, User  # noqa: E402
from app.services import alert_engine, webhook_notifier  # noqa: E402
from app.services.auth import create_access_token, hash_password  # noqa: E402

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


FAKE_WEBHOOK = "http://example.test/fake-webhook"  # RFC 2606 — nunca resolve de verdade

create_db_and_tables()

with Session(engine) as s:
    printer = Printer(server="srvtest", name="WH_Test", ip="10.9.9.9", model="Ricoh P502", active=True)
    s.add(printer)
    # Fase 1: /notify e uma acao operacional — o usuario do teste precisa
    # do papel "operator" (o default de User e "viewer", somente leitura).
    s.add(User(email="webhook.test@example.com", password_hash=hash_password("x"),
               name="Webhook Test", role=Role.OPERATOR.value))
    s.commit()
    s.refresh(printer)
    PRINTER_ID = printer.id

TOKEN = create_access_token({"sub": "webhook.test@example.com"})
client = TestClient(app)


def make_reading(**toner) -> PrinterReading:
    return PrinterReading(
        printer_id=PRINTER_ID,
        status="atencao",
        page_count=100,
        toner_k=toner.get("k"),
        toner_c=toner.get("c"),
        toner_m=toner.get("m"),
        toner_y=toner.get("y"),
    )


def make_offline_reading() -> PrinterReading:
    return PrinterReading(printer_id=PRINTER_ID, status="offline", page_count=100)


def reset_alerts_and_readings(session):
    from sqlmodel import select
    for a in session.exec(select(Alert)).all():
        session.delete(a)
    for r in session.exec(select(PrinterReading)).all():
        session.delete(r)
    session.commit()


print("=== 1. WEBHOOK_URL vazio -> nenhuma chamada, fluxo continua ===")
settings.webhook_url = ""
with mock.patch.object(webhook_notifier.httpx, "post") as post_mock:
    with Session(engine) as s:
        reset_alerts_and_readings(s)
        reading = make_reading(k=5)  # critico
        s.add(reading)
        s.commit()
        s.refresh(reading)
        actions = alert_engine.evaluate_reading(s, PRINTER_ID, reading)
check_true("evaluate_reading nao lancou excecao e retornou acoes", isinstance(actions, dict))
check("nenhuma chamada HTTP (webhook desabilitado)", post_mock.call_count, 0)

settings.webhook_url = FAKE_WEBHOOK

print("\n=== 2. created + toner critical -> 1 chamada ===")
with mock.patch.object(webhook_notifier.httpx, "post") as post_mock:
    post_mock.return_value = mock.Mock(status_code=200)
    with Session(engine) as s:
        reset_alerts_and_readings(s)
        reading = make_reading(k=5)
        s.add(reading)
        s.commit()
        s.refresh(reading)
        actions = alert_engine.evaluate_reading(s, PRINTER_ID, reading)
check("acao toner:K = created", actions["toner:K"], "created")
check("1 chamada de webhook", post_mock.call_count, 1)

print("\n=== 3. Fase 11: toner continua caindo (10% -> 5%) -> re-alerta, 1 chamada por degrau ===")
with Session(engine) as s:
    reset_alerts_and_readings(s)
    with mock.patch.object(webhook_notifier.httpx, "post") as first_mock:
        first_mock.return_value = mock.Mock(status_code=200)
        r1 = make_reading(k=10)  # entra na zona critica
        s.add(r1)
        s.commit()
        s.refresh(r1)
        actions_first = alert_engine.evaluate_reading(s, PRINTER_ID, r1)
    check("acao toner:K = created (10%)", actions_first["toner:K"], "created")
    check("1 chamada de webhook ao entrar na zona", first_mock.call_count, 1)

    with mock.patch.object(webhook_notifier.httpx, "post") as esc_mock:
        esc_mock.return_value = mock.Mock(status_code=200)
        r2 = make_reading(k=5)  # caiu mais -> re-alerta
        s.add(r2)
        s.commit()
        s.refresh(r2)
        actions_esc = alert_engine.evaluate_reading(s, PRINTER_ID, r2)
check("acao toner:K = escalated", actions_esc["toner:K"], "escalated")
check("1 chamada de webhook na escalada", esc_mock.call_count, 1)

print("\n=== 4. kept (mesmo nivel, nao caiu mais) -> nenhuma chamada ===")
with Session(engine) as s:
    with mock.patch.object(webhook_notifier.httpx, "post") as kept_mock:
        kept_mock.return_value = mock.Mock(status_code=200)
        r3 = make_reading(k=5)  # mesmo nivel do ultimo alerta (5%)
        s.add(r3)
        s.commit()
        s.refresh(r3)
        actions_kept = alert_engine.evaluate_reading(s, PRINTER_ID, r3)
check("acao toner:K = kept", actions_kept["toner:K"], "kept")
check("nenhuma chamada em 'kept'", kept_mock.call_count, 0)

print("\n=== 5. alerta nao relacionado a toner (offline) -> nenhuma chamada automatica ===")
with Session(engine) as s:
    reset_alerts_and_readings(s)
    with mock.patch.object(webhook_notifier.httpx, "post") as off_mock:
        off_mock.return_value = mock.Mock(status_code=200)
        r4 = make_offline_reading()
        s.add(r4)
        s.commit()
        s.refresh(r4)
        actions_off = alert_engine.evaluate_reading(s, PRINTER_ID, r4)
check("alerta offline criado", actions_off["offline"], "created")
check("offline nao dispara webhook", off_mock.call_count, 0)

print("\n=== 6. Fase 11: toner acima do limiar (15%, fora da zona critica) -> nenhum alerta, nenhuma chamada ===")
with Session(engine) as s:
    reset_alerts_and_readings(s)
    with mock.patch.object(webhook_notifier.httpx, "post") as warn2_mock:
        warn2_mock.return_value = mock.Mock(status_code=200)
        r5 = make_reading(k=15)
        s.add(r5)
        s.commit()
        s.refresh(r5)
        actions_w = alert_engine.evaluate_reading(s, PRINTER_ID, r5)
check("acao toner:K = none (acima do limiar)", actions_w["toner:K"], "none")
check("nenhum webhook fora da zona critica", warn2_mock.call_count, 0)

print("\n=== 7. erro HTTP -> evaluate_reading continua normalmente ===")
with Session(engine) as s:
    reset_alerts_and_readings(s)
    with mock.patch.object(webhook_notifier.httpx, "post") as err_mock:
        err_mock.return_value = mock.Mock(status_code=500)
        r6 = make_reading(k=3)
        s.add(r6)
        s.commit()
        s.refresh(r6)
        actions_err = alert_engine.evaluate_reading(s, PRINTER_ID, r6)
check("alerta criado mesmo com erro HTTP no webhook", actions_err["toner:K"], "created")
check_true("nenhuma excecao propagou", True)

print("\n=== 8. timeout/excecao de rede -> evaluate_reading continua ===")
import httpx  # noqa: E402

with Session(engine) as s:
    reset_alerts_and_readings(s)
    with mock.patch.object(webhook_notifier.httpx, "post", side_effect=httpx.TimeoutException("timeout")):
        r7 = make_reading(k=2)
        s.add(r7)
        s.commit()
        s.refresh(r7)
        actions_to = alert_engine.evaluate_reading(s, PRINTER_ID, r7)
check("alerta criado mesmo com timeout no webhook", actions_to["toner:K"], "created")

with Session(engine) as s:
    reset_alerts_and_readings(s)
    with mock.patch.object(webhook_notifier.httpx, "post", side_effect=ConnectionError("recusado")):
        r8 = make_reading(k=2)
        s.add(r8)
        s.commit()
        s.refresh(r8)
        actions_conn = alert_engine.evaluate_reading(s, PRINTER_ID, r8)
check("alerta criado mesmo com excecao de conexao no webhook", actions_conn["toner:K"], "created")

print("\n=== 9. endpoint manual exige JWT ===")
resp_no_auth = client.post(f"/api/alerts/1/notify")
check("sem token -> 401", resp_no_auth.status_code, 401)

resp_bad_auth = client.post("/api/alerts/1/notify", headers={"Authorization": "Bearer token-invalido"})
check("token invalido -> 401", resp_bad_auth.status_code, 401)

print("\n=== 10. endpoint manual com Alert inexistente -> 404 ===")
resp_404 = client.post("/api/alerts/999999/notify", headers={"Authorization": f"Bearer {TOKEN}"})
check("alert inexistente -> 404", resp_404.status_code, 404)

print("\n=== 11. endpoint manual dispara notificacao sem criar/duplicar Alert ===")
with Session(engine) as s:
    from sqlmodel import select
    alert = s.exec(select(Alert).where(Alert.printer_id == PRINTER_ID)).first()
    ALERT_ID = alert.id

with Session(engine) as s:
    from sqlmodel import func, select
    alerts_before = s.exec(select(func.count()).select_from(Alert)).one()

with mock.patch.object(webhook_notifier.httpx, "post") as manual_mock:
    manual_mock.return_value = mock.Mock(status_code=200)
    resp_manual = client.post(f"/api/alerts/{ALERT_ID}/notify", headers={"Authorization": f"Bearer {TOKEN}"})

check("disparo manual -> 200", resp_manual.status_code, 200)
check("resposta reporta sent=True", resp_manual.json().get("sent"), True)
check("1 chamada HTTP no disparo manual", manual_mock.call_count, 1)

with Session(engine) as s:
    from sqlmodel import func, select
    alerts_after = s.exec(select(func.count()).select_from(Alert)).one()
check("nenhum Alert novo criado pelo disparo manual", alerts_after, alerts_before)

with Session(engine) as s:
    unchanged = s.get(Alert, ALERT_ID)
check_true("severity do alerta original inalterada", unchanged.severity == "critical", unchanged.severity)

print(f"\nBanco de teste: {TEST_DB}")
print("Nenhuma URL de webhook real foi usada neste arquivo (apenas example.test).")
print("RESULTADO:", "TODOS OS TESTES PASSARAM" if not failures else f"FALHAS: {failures}")
raise SystemExit(1 if failures else 0)
