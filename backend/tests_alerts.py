"""
Etapa 8A - validacao dos alertas automaticos.

Usa banco SQLite temporario e o mock SNMP: cada cenario e coletado pelo
PrinterCollector e os alertas resultantes sao conferidos.

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
from app.models.printer import Printer  # noqa: E402
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


def active(session, alert_type=None):
    q = select(Alert).where(Alert.printer_id == 1).where(Alert.resolved_at == None)  # noqa: E711
    if alert_type:
        q = q.where(Alert.alert_type == alert_type)
    return session.exec(q).all()


def resolved(session):
    return session.exec(
        select(Alert).where(Alert.printer_id == 1).where(Alert.resolved_at != None)  # noqa: E711
    ).all()


with Session(engine) as s:
    s.add(Printer(id=1, name="TESTE", ip="10.0.0.1", model="HP LaserJet", department="lab"))
    s.commit()

    print("\n--- 1. cenario saudavel: nenhum alerta ---")
    collect(s, "online_mono")
    check("alertas ativos", len(active(s)), 0)

    print("\n--- 2. offline: cria alerta critical ---")
    r = collect(s, "offline")
    check("acao", r["alerts"].get("offline"), "created")
    a = active(s, "offline")
    check("ativos offline", len(a), 1)
    check("severidade", a[0].severity, "critical")
    first_id = a[0].id

    print("\n--- 3. offline de novo: NAO duplica ---")
    r = collect(s, "offline")
    check("acao", r["alerts"].get("offline"), "kept")
    a = active(s, "offline")
    check("ativos offline", len(a), 1)
    check("mesmo alerta", a[0].id, first_id)

    print("\n--- 4. volta online: resolve automaticamente ---")
    r = collect(s, "online_mono")
    check("acao", r["alerts"].get("offline"), "resolved")
    check("ativos offline", len(active(s, "offline")), 0)
    check("resolvidos", len(resolved(s)), 1)

    print("\n--- 5. toner baixo (<=20%): cria warning ---")
    r = collect(s, "attention_low_toner")
    check("acao", r["alerts"].get("toner:K"), "created")
    a = active(s, "toner:K")
    check("ativos toner:K", len(a), 1)
    check("severidade", a[0].severity, "warning")
    low_id = a[0].id

    print("\n--- 6. toner baixo de novo: NAO duplica ---")
    r = collect(s, "attention_low_toner")
    check("acao", r["alerts"].get("toner:K"), "kept")
    check("ativos toner:K", len(active(s, "toner:K")), 1)

    print("\n--- 7. toner critico (<=10%): escala sem duplicar ativo ---")
    r = collect(s, "mono_critical")
    check("acao", r["alerts"].get("toner:K"), "escalated")
    a = active(s, "toner:K")
    check("ativos toner:K", len(a), 1)
    check("severidade", a[0].severity, "critical")
    check("warning anterior foi resolvido", a[0].id != low_id, True)

    print("\n--- 8. toner critico de novo: NAO duplica ---")
    r = collect(s, "mono_critical")
    check("acao", r["alerts"].get("toner:K"), "kept")
    check("ativos toner:K", len(active(s, "toner:K")), 1)

    print("\n--- 9. toner recupera: resolve automaticamente ---")
    r = collect(s, "online_mono")
    check("acao", r["alerts"].get("toner:K"), "resolved")
    check("ativos", len(active(s)), 0)

    print("\n--- 10. colorida com niveis mistos ---")
    r = collect(s, "color_mixed_levels", is_color=True)
    a = active(s)
    print("     ativos:", {x.alert_type: x.severity for x in a})
    check("alertas por cor gerados", len(a) > 0, True)

    print("\n--- 11. offline nao gera alerta falso de toner ---")
    collect(s, "online_mono")
    r = collect(s, "offline")
    toner_actions = {k: v for k, v in r["alerts"].items() if k.startswith("toner")}
    check("nenhuma acao de toner enquanto offline", toner_actions, {})

print(f"\nBanco de teste: {DB}")
print("RESULTADO:", "TODOS OS TESTES PASSARAM" if not failures else f"FALHAS: {failures}")
raise SystemExit(1 if failures else 0)
