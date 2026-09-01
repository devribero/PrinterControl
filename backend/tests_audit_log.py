"""
Fase 16 - trilha de auditoria administrativa.

Cobre: criar/editar/excluir usuario e Print Server gravam entrada com
autor, antes/depois; GET /api/audit-log so admin; password_hash nunca
aparece no before/after de usuario.

Executar:  .\\venv\\Scripts\\python.exe tests_audit_log.py
"""
import os
import tempfile

DB = os.path.join(tempfile.gettempdir(), "test_audit_log.db")
if os.path.exists(DB):
    os.remove(DB)
os.environ["DATABASE_URL"] = f"sqlite:///{DB}"

from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import Session  # noqa: E402

from app.database import create_db_and_tables, engine  # noqa: E402
from app.main import app  # noqa: E402
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
    admin = User(email="auditoria.admin@example.com", password_hash=hash_password("x"),
                 name="Admin Auditoria", role=Role.ADMIN.value)
    viewer = User(email="auditoria.viewer@example.com", password_hash=hash_password("x"),
                  name="Viewer Auditoria", role=Role.VIEWER.value)
    s.add(admin)
    s.add(viewer)
    s.commit()
    s.refresh(admin)
    s.refresh(viewer)

ADMIN_TOKEN = create_access_token({"sub": "auditoria.admin@example.com"})
VIEWER_TOKEN = create_access_token({"sub": "auditoria.viewer@example.com"})
H_ADMIN = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
H_VIEWER = {"Authorization": f"Bearer {VIEWER_TOKEN}"}
client = TestClient(app)

print("--- 1. GET /api/audit-log exige admin ---")
check("viewer -> 403", client.get("/api/audit-log", headers=H_VIEWER).status_code, 403)
check("admin -> 200", client.get("/api/audit-log", headers=H_ADMIN).status_code, 200)
check("sem token -> 401", client.get("/api/audit-log").status_code, 401)

print("\n--- 2. criar usuario grava user.create com after, sem before ---")
resp = client.post("/api/users", headers=H_ADMIN, json={
    "email": "novo.usuario@example.com", "name": "Novo Usuario", "password": "senha1234", "role": "viewer",
})
check("criacao ok", resp.status_code, 201)
new_user_id = resp.json()["id"]

log = client.get("/api/audit-log", headers=H_ADMIN, params={"target_type": "user", "target_id": new_user_id}).json()
check("1 entrada pra esse usuario", len(log), 1)
entry = log[0]
check("action = user.create", entry["action"], "user.create")
check("actor = quem criou", entry["actor_email"], "auditoria.admin@example.com")
check("before nulo (nao havia 'antes')", entry["before"], None)
check("after tem o email novo", entry["after"]["email"], "novo.usuario@example.com")
check("password_hash NAO aparece no after", "password_hash" in entry["after"], False)

print("\n--- 3. editar usuario grava user.update com before E after ---")
resp = client.patch(f"/api/users/{new_user_id}", headers=H_ADMIN, json={"role": "operator"})
check("edicao ok", resp.status_code, 200)

log = client.get("/api/audit-log", headers=H_ADMIN, params={"target_type": "user", "target_id": new_user_id}).json()
update_entry = next(e for e in log if e["action"] == "user.update")
check("before.role = viewer (o que era antes)", update_entry["before"]["role"], "viewer")
check("after.role = operator (o que passou a ser)", update_entry["after"]["role"], "operator")

print("\n--- 4. excluir usuario grava user.delete com before, sem after ---")
resp = client.request("DELETE", f"/api/users/{new_user_id}", headers=H_ADMIN, json={"confirm_email": "novo.usuario@example.com"})
check("exclusao ok", resp.status_code, 204)

log = client.get("/api/audit-log", headers=H_ADMIN, params={"target_type": "user", "target_id": new_user_id}).json()
delete_entry = next(e for e in log if e["action"] == "user.delete")
check("before tem o email de quem foi excluido", delete_entry["before"]["email"], "novo.usuario@example.com")
check("after nulo (nao ha 'depois' de uma exclusao)", delete_entry["after"], None)
check("3 entradas no total pra esse usuario (create+update+delete)", len(log), 3)

print("\n--- 5. Print Server: create/update/delete tambem gravam ---")
resp = client.post("/api/servers", headers=H_ADMIN, json={"host": "srv-auditoria-teste", "mode": "mock"})
check("criacao de servidor ok", resp.status_code, 201)
server_id = resp.json()["id"]

client.patch(f"/api/servers/{server_id}", headers=H_ADMIN, json={"active": False})
client.request("DELETE", f"/api/servers/{server_id}", headers=H_ADMIN, json={"confirm_host": "srv-auditoria-teste"})

log = client.get("/api/audit-log", headers=H_ADMIN, params={"target_type": "print_server", "target_id": server_id}).json()
actions = sorted(e["action"] for e in log)
check("create+delete+update registrados pro servidor", actions, ["server.create", "server.delete", "server.update"])

print(f"\nBanco de teste: {DB}")
print("RESULTADO:", "TODOS OS TESTES PASSARAM" if not failures else f"FALHAS: {failures}")
raise SystemExit(1 if failures else 0)
