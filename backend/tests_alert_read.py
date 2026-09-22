"""
"Marcar como lido" dos alertas (22/09/2026).

TestClient contra SQLite temporario (mesmo esquema de tests_rbac.py). Cobre:
PATCH /api/alerts/{id}/read e /unread (idempotentes, qualquer usuario ativo),
POST /api/alerts/read-all (com e sem `ids`), read_at/read_by nas respostas,
que ler NAO resolve o alerta, que o re-alerta de toner nasce nao lido, a
trilha de auditoria do read-all e a migracao aditiva em banco antigo.

    env -u DATABASE_URL ./venv/Scripts/python.exe tests_alert_read.py
"""
import os
import sqlite3
import sys
import tempfile
from pathlib import Path

# Precisa vir ANTES de importar app.config: as Settings leem o ambiente no import.
_TMP_DIR = Path(tempfile.mkdtemp(prefix="printercontrol-alertread-"))
_TMP_DB = _TMP_DIR / "alert_read_test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP_DB.as_posix()}"
os.environ["ENVIRONMENT"] = "development"

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine as sa_create_engine, text  # noqa: E402
from sqlmodel import Session, select  # noqa: E402

import app.database as database  # noqa: E402
from app.database import create_db_and_tables, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models.alert import Alert  # noqa: E402
from app.models.audit_log import AuditLog  # noqa: E402
from app.models.printer import Printer, PrinterReading  # noqa: E402
from app.models.user import Role, User  # noqa: E402
from app.services.alert_engine import evaluate_reading  # noqa: E402
from app.services.auth import hash_password  # noqa: E402

_falhas = []


def check(nome, obtido, esperado):
    ok = obtido == esperado
    print(f"  [{'OK  ' if ok else 'FALHA'}] {nome}: {obtido!r}" + ("" if ok else f" (esperado {esperado!r})"))
    if not ok:
        _falhas.append(nome)


SENHA = "senha-de-teste-123"


def semear():
    create_db_and_tables()
    with Session(engine) as s:
        s.add(User(email="viewer@teste-read.com", password_hash=hash_password(SENHA),
                   name="Vera Viewer", role=Role.VIEWER.value, is_active=True))
        s.add(User(email="admin@teste-read.com", password_hash=hash_password(SENHA),
                   name="Ana Admin", role=Role.ADMIN.value, is_active=True))
        p = Printer(server="teste", name="IMP_READ", ip="10.255.255.200", model="M", department="TI")
        s.add(p)
        s.commit()
        s.refresh(p)
        ids = []
        for i in range(3):
            a = Alert(printer_id=p.id, severity="critical", message=f"alerta {i}", alert_type=f"toner:{'KCM'[i]}", value=5)
            s.add(a)
            s.commit()
            s.refresh(a)
            ids.append(a.id)
        return p.id, ids


def h(token):
    return {"Authorization": f"Bearer {token}"}


def login(client, email):
    r = client.post("/api/auth/login", json={"email": email, "password": SENHA})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def testar_migracao():
    print("\n[6] Migracao aditiva em banco sem read_at/read_by")
    antigo = _TMP_DIR / "antigo.db"
    con = sqlite3.connect(antigo)
    con.execute("CREATE TABLE alerts (id INTEGER PRIMARY KEY, printer_id INTEGER, alert_type VARCHAR,"
                " severity VARCHAR, message VARCHAR, value INTEGER, created_at DATETIME, resolved_at DATETIME)")
    con.execute("INSERT INTO alerts (printer_id, severity, message) VALUES (1, 'critical', 'x')")
    con.commit()
    con.close()

    original = database.engine
    eng = sa_create_engine(f"sqlite:///{antigo.as_posix()}")
    database.engine = eng
    try:
        database._migrate_alert_read()
        database._migrate_alert_read()  # idempotente
    finally:
        database.engine = original
    with eng.connect() as conn:
        cols = {row[1] for row in conn.execute(text("PRAGMA table_info(alerts)"))}
        linha = conn.execute(text("SELECT read_at, read_by FROM alerts")).one()
    eng.dispose()
    check("colunas criadas", {"read_at", "read_by"} <= cols, True)
    check("alerta antigo fica nao lido", tuple(linha), (None, None))


def main():
    printer_id, ids = semear()
    client = TestClient(app)
    viewer = login(client, "viewer@teste-read.com")
    admin = login(client, "admin@teste-read.com")

    print("\n[1] Estado inicial e resposta")
    r = client.get("/api/alerts", headers=h(viewer))
    check("lista 200", r.status_code, 200)
    primeiro = r.json()[0]
    check("read_at na resposta", "read_at" in primeiro and primeiro["read_at"] is None, True)
    check("read_by na resposta", "read_by" in primeiro and primeiro["read_by"] is None, True)

    print("\n[2] PATCH /read (viewer pode) e idempotencia")
    check("sem token -> 401", client.patch(f"/api/alerts/{ids[0]}/read").status_code, 401)
    r = client.patch(f"/api/alerts/{ids[0]}/read", headers=h(viewer))
    check("viewer marca lido", r.status_code, 200)
    corpo = r.json()
    check("read_by = nome", corpo["read_by"], "Vera Viewer")
    check("read_at preenchido", corpo["read_at"] is not None, True)
    check("continua ativo (nao resolve)", corpo["resolved_at"], None)
    r2 = client.patch(f"/api/alerts/{ids[0]}/read", headers=h(admin))
    check("repetir -> 200", r2.status_code, 200)
    check("mantem primeiro leitor", r2.json()["read_by"], "Vera Viewer")
    check("mantem primeiro read_at", r2.json()["read_at"], corpo["read_at"])
    check("inexistente -> 404", client.patch("/api/alerts/999999/read", headers=h(viewer)).status_code, 404)

    print("\n[3] PATCH /unread")
    r = client.patch(f"/api/alerts/{ids[0]}/unread", headers=h(viewer))
    check("unread 200", r.status_code, 200)
    check("read_at limpo", r.json()["read_at"], None)
    check("read_by limpo", r.json()["read_by"], None)
    check("unread de novo -> 200", client.patch(f"/api/alerts/{ids[0]}/unread", headers=h(viewer)).status_code, 200)

    print("\n[4] POST /read-all")
    r = client.post("/api/alerts/read-all", json={"ids": [ids[0]]}, headers=h(admin))
    check("com ids -> so 1", r.json(), {"updated": 1})
    r = client.post("/api/alerts/read-all", json={"ids": []}, headers=h(admin))
    check("ids vazio -> 0", r.json(), {"updated": 0})
    # resolve o terceiro: o read-all sem ids so pega os ativos
    with Session(engine) as s:
        a = s.get(Alert, ids[2])
        from datetime import datetime
        a.resolved_at = datetime.utcnow()
        s.add(a)
        s.commit()
    r = client.post("/api/alerts/read-all", headers=h(viewer))
    check("sem corpo -> ativos nao lidos", r.json(), {"updated": 1})
    r = client.post("/api/alerts/read-all", json={}, headers=h(viewer))
    check("de novo -> 0", r.json(), {"updated": 0})
    with Session(engine) as s:
        check("primeiro lido pelo admin (preservado)", s.get(Alert, ids[0]).read_by, "Ana Admin")
        check("segundo lido pela viewer", s.get(Alert, ids[1]).read_by, "Vera Viewer")
        check("resolvido nao foi marcado", s.get(Alert, ids[2]).read_at, None)
        check("nenhum ativo resolvido pela leitura", s.get(Alert, ids[1]).resolved_at, None)
        logs = s.exec(select(AuditLog).where(AuditLog.action == "alert.read_all")).all()
        check("auditoria: 2 registros (so quando mudou algo)", len(logs), 2)

    print("\n[5] Re-alerta de toner nasce nao lido")
    with Session(engine) as s:
        # ids[0] e toner:K em 5%, lido. Nova queda para 3% -> escala.
        evaluate_reading(s, printer_id, PrinterReading(printer_id=printer_id, status="atencao",
                                                       page_count=10, toner_k=3))
        s.commit()
        ativos = s.exec(select(Alert).where(Alert.alert_type == "toner:K")
                        .where(Alert.resolved_at == None)).all()  # noqa: E711
        check("um ativo toner:K", len(ativos), 1)
        check("e uma linha nova", ativos[0].id != ids[0], True)
        check("nova linha nao lida", ativos[0].read_at, None)
        check("antiga resolvida", s.get(Alert, ids[0]).resolved_at is not None, True)

    testar_migracao()

    print()
    if _falhas:
        print(f"FALHAS ({len(_falhas)}): {', '.join(_falhas)}")
        sys.exit(1)
    print("Todos os testes passaram.")


if __name__ == "__main__":
    main()
