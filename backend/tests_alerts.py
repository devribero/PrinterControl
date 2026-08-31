"""
Etapa 8A / Fase 11 - validacao dos alertas automaticos.

Usa banco SQLite temporario e o mock SNMP: cenarios simples (saudavel,
offline) sao coletados pelo PrinterCollector, como antes. A escada de
re-alerta de toner (Fase 11) e testada chamando alert_engine.evaluate_reading
diretamente com leituras construidas a mao — os cenarios SNMP mock sao fixos
(nao dá para simular "o mesmo toner caindo ponto a ponto" com eles).

Executar:  .\\venv\\Scripts\\python.exe tests_alerts.py
"""
import os
import tempfile

DB = os.path.join(tempfile.gettempdir(), "test_alerts.db")
if os.path.exists(DB):
    os.remove(DB)
os.environ["DATABASE_URL"] = f"sqlite:///{DB}"

from sqlmodel import Session, SQLModel, create_engine, select  # noqa: E402

from app.models.alert import Alert  # noqa: E402
from app.models.notification import Notification  # noqa: E402
from app.models.printer import Printer, PrinterReading  # noqa: E402
from app.models.user import User  # noqa: E402
from app.services.alert_engine import evaluate_reading  # noqa: E402
from app.services.printer_collector import PrinterCollector  # noqa: E402

engine = create_engine(f"sqlite:///{DB}", connect_args={"check_same_thread": False})
SQLModel.metadata.create_all(engine)

failures = []


def check(label, got, expected):
    ok = got == expected
    print(f"[{'OK ' if ok else 'FAIL'}] {label}: {got}" + ("" if ok else f" (esperado {expected})"))
    if not ok:
        failures.append(label)


def collect(session, scenario, is_color=False):
    return PrinterCollector(mode="mock", mock_scenario=scenario).collect_and_save(
        1, session, is_color=is_color
    )


def reading(status="atencao", page_count=1000, **toners):
    return PrinterReading(printer_id=1, status=status, page_count=page_count, **toners)


def active(session, alert_type=None):
    q = select(Alert).where(Alert.printer_id == 1).where(Alert.resolved_at == None)  # noqa: E711
    if alert_type:
        q = q.where(Alert.alert_type == alert_type)
    return session.exec(q).all()


def resolved(session):
    return session.exec(
        select(Alert).where(Alert.printer_id == 1).where(Alert.resolved_at != None)  # noqa: E711
    ).all()


def notifications(session):
    return session.exec(select(Notification)).all()


with Session(engine) as s:
    s.add(Printer(id=1, name="TESTE", ip="10.0.0.1", model="HP LaserJet", department="lab"))
    ativo = User(email="ativo@teste.com", username="ativo", name="Ativo", password_hash="x", role="operator", is_active=True)
    inativo = User(email="inativo@teste.com", username="inativo", name="Inativo", password_hash="x", role="operator", is_active=False)
    s.add(ativo)
    s.add(inativo)
    s.commit()
    s.refresh(ativo)
    s.refresh(inativo)

    print("\n--- 1. cenario saudavel: nenhum alerta ---")
    collect(s, "online_mono")
    check("alertas ativos", len(active(s)), 0)

    print("\n--- 2. offline: cria alerta critical + notifica usuarios ativos ---")
    r = collect(s, "offline")
    check("acao", r["alerts"].get("offline"), "created")
    a = active(s, "offline")
    check("ativos offline", len(a), 1)
    check("severidade", a[0].severity, "critical")
    first_id = a[0].id
    notifs = notifications(s)
    check("notificacoes criadas (so o usuario ativo)", len(notifs), 1)
    check("notificacao referencia o alerta", notifs[0].alert_id, first_id)
    check("notificacao foi para o usuario ativo", notifs[0].user_id, ativo.id)
    check("notificacao NAO foi para o usuario inativo", notifs[0].user_id != inativo.id, True)

    print("\n--- 3. offline de novo: NAO duplica alerta nem notificacao ---")
    r = collect(s, "offline")
    check("acao", r["alerts"].get("offline"), "kept")
    a = active(s, "offline")
    check("ativos offline", len(a), 1)
    check("mesmo alerta", a[0].id, first_id)
    check("nenhuma notificacao nova", len(notifications(s)), 1)

    print("\n--- 4. volta online: resolve automaticamente ---")
    r = collect(s, "online_mono")
    check("acao", r["alerts"].get("offline"), "resolved")
    check("ativos offline", len(active(s, "offline")), 0)
    check("resolvidos", len(resolved(s)), 1)

    print("\n--- 5. toner acima do limiar (12%): nenhum alerta ---")
    evaluate_reading(s, 1, reading(toner_k=12))
    check("ativos toner:K", len(active(s, "toner:K")), 0)

    print("\n--- 6. toner cruza o limiar (10%): cria alerta + notifica ---")
    n_antes = len(notifications(s))
    evaluate_reading(s, 1, reading(toner_k=10))
    a = active(s, "toner:K")
    check("ativos toner:K", len(a), 1)
    check("severidade", a[0].severity, "critical")
    check("value gravado", a[0].value, 10)
    ten_id = a[0].id
    check("notificacao nova", len(notifications(s)) - n_antes, 1)

    print("\n--- 7. toner no mesmo nivel (10% de novo): NAO re-alerta ---")
    n_antes = len(notifications(s))
    evaluate_reading(s, 1, reading(toner_k=10))
    a = active(s, "toner:K")
    check("ativos toner:K", len(a), 1)
    check("mesmo alerta (nao escalou)", a[0].id, ten_id)
    check("nenhuma notificacao nova", len(notifications(s)) - n_antes, 0)

    print("\n--- 8. toner cai para 9%: re-alerta (escalated) ---")
    n_antes = len(notifications(s))
    evaluate_reading(s, 1, reading(toner_k=9))
    a = active(s, "toner:K")
    check("ativos toner:K", len(a), 1)
    check("novo alerta (anterior resolvido)", a[0].id != ten_id, True)
    check("value atualizado", a[0].value, 9)
    nine_id = a[0].id
    check("notificacao nova", len(notifications(s)) - n_antes, 1)

    print("\n--- 9. toner sobe pra 10 mas continua na zona critica: NAO re-alerta ---")
    n_antes = len(notifications(s))
    evaluate_reading(s, 1, reading(toner_k=10))
    a = active(s, "toner:K")
    check("mesmo alerta (9% continua sendo o minimo)", a[0].id, nine_id)
    check("nenhuma notificacao nova", len(notifications(s)) - n_antes, 0)

    print("\n--- 10. toner cai para 8%: re-alerta de novo ---")
    n_antes = len(notifications(s))
    evaluate_reading(s, 1, reading(toner_k=8))
    a = active(s, "toner:K")
    check("novo alerta", a[0].id != nine_id, True)
    check("value atualizado", a[0].value, 8)
    check("notificacao nova", len(notifications(s)) - n_antes, 1)

    print("\n--- 11. toner recupera (15%): resolve automaticamente ---")
    evaluate_reading(s, 1, reading(toner_k=15))
    check("ativos toner:K", len(active(s, "toner:K")), 0)

    print("\n--- 12. colorida com todos os niveis acima do limiar: nenhum alerta ---")
    r = collect(s, "color_mixed_levels", is_color=True)
    a = active(s)
    check("nenhum alerta de toner (todas as cores > 10%)", len(a), 0)

    print("\n--- 13. offline nao gera alerta falso de toner ---")
    collect(s, "online_mono")
    r = collect(s, "offline")
    toner_actions = {k: v for k, v in r["alerts"].items() if k.startswith("toner")}
    check("nenhuma acao de toner enquanto offline", toner_actions, {})

print(f"\nBanco de teste: {DB}")
print("RESULTADO:", "TODOS OS TESTES PASSARAM" if not failures else f"FALHAS: {failures}")
raise SystemExit(1 if failures else 0)
