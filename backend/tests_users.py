"""
Fase 3 - Gestao administrativa de contas (/api/users).

Como tests_rbac.py, NAO precisa do backend rodando: TestClient do FastAPI
contra um SQLite temporario, criado do zero e apagado no fim. O banco real
(printer_control.db) nunca e aberto.

    .\\venv\\Scripts\\python.exe tests_users.py
"""
import os
import tempfile
from pathlib import Path

# Antes de importar app.config: as Settings leem o ambiente no import.
_TMP_DB = Path(tempfile.mkdtemp(prefix="printercontrol-users-")) / "users_test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP_DB.as_posix()}"
os.environ["ENVIRONMENT"] = "development"

from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import Session, select  # noqa: E402

from app.database import create_db_and_tables, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models.user import Role, User  # noqa: E402
from app.services.auth import hash_password, verify_password  # noqa: E402

_falhas = []


def check(nome, obtido, esperado):
    ok = obtido == esperado
    print(f"  [{'OK  ' if ok else 'FALHA'}] {nome}: {obtido!r}" + ("" if ok else f" (esperado {esperado!r})"))
    if not ok:
        _falhas.append(nome)


def check_true(nome, cond, detalhe=""):
    print(f"  [{'OK  ' if cond else 'FALHA'}] {nome}" + (f": {detalhe}" if detalhe else ""))
    if not cond:
        _falhas.append(nome)


SENHA = "senha-de-teste-123"
CONTAS = {
    "admin": ("admin@teste-users.com", Role.ADMIN.value),
    "admin2": ("admin2@teste-users.com", Role.ADMIN.value),
    "operator": ("operator@teste-users.com", Role.OPERATOR.value),
    "viewer": ("viewer@teste-users.com", Role.VIEWER.value),
}


def semear():
    create_db_and_tables()
    with Session(engine) as s:
        for email, role in CONTAS.values():
            s.add(User(email=email, password_hash=hash_password(SENHA), name=email, role=role))
        s.commit()


def h(token):
    return {"Authorization": f"Bearer {token}"}


def _set_ativo(email, ativo):
    with Session(engine) as s:
        u = s.exec(select(User).where(User.email == email)).first()
        u.is_active = ativo
        s.add(u)
        s.commit()


def _hash_de(email):
    with Session(engine) as s:
        return s.exec(select(User).where(User.email == email)).first().password_hash


def main():
    semear()
    client = TestClient(app)

    tokens = {}
    for papel, (email, _) in CONTAS.items():
        r = client.post("/api/auth/login", json={"email": email, "password": SENHA})
        tokens[papel] = r.json()["access_token"]

    print("\n[1] GET /api/users — so admin")
    check("sem token -> 401", client.get("/api/users").status_code, 401)
    check("token invalido -> 401", client.get("/api/users", headers=h("a.b.c")).status_code, 401)
    check("viewer -> 403", client.get("/api/users", headers=h(tokens["viewer"])).status_code, 403)
    check("operator -> 403", client.get("/api/users", headers=h(tokens["operator"])).status_code, 403)
    r = client.get("/api/users", headers=h(tokens["admin"]))
    check("admin -> 200", r.status_code, 200)
    lista = r.json()
    check("4 contas semeadas", len(lista), 4)
    check_true("campos esperados",
               set(lista[0]) == {"id", "email", "name", "role", "is_active", "created_at"},
               str(sorted(lista[0])))
    check_true("password_hash ausente na listagem",
               all("password_hash" not in u and "password" not in u for u in lista))

    print("\n[2] POST /api/users — so admin")
    novo = {"email": "novo@teste-users.com", "password": "outra-senha-123", "name": "Conta Nova"}
    check("sem token -> 401", client.post("/api/users", json=novo).status_code, 401)
    check("viewer -> 403", client.post("/api/users", json=novo, headers=h(tokens["viewer"])).status_code, 403)
    check("operator -> 403", client.post("/api/users", json=novo, headers=h(tokens["operator"])).status_code, 403)

    r = client.post("/api/users", json=novo, headers=h(tokens["admin"]))
    check("admin -> 201", r.status_code, 201)
    criado = r.json()
    novo_id = criado["id"]
    check("papel padrao e viewer", criado["role"], "viewer")
    check("nasce ativo", criado["is_active"], True)
    check_true("password_hash ausente na criacao",
               "password_hash" not in criado and "password" not in criado, str(sorted(criado)))

    print("\n[3] Senha guardada como hash, nunca em texto claro")
    guardado = _hash_de(novo["email"])
    check_true("hash != senha", guardado != novo["password"])
    check_true("formato argon2", guardado.startswith("$argon2"), guardado[:16])
    check_true("hash confere com a senha", verify_password(novo["password"], guardado))
    check("login com a senha definida pelo admin",
          client.post("/api/auth/login",
                      json={"email": novo["email"], "password": novo["password"]}).status_code, 200)

    print("\n[4] Validacoes de criacao")
    check("e-mail duplicado -> 409",
          client.post("/api/users", json=novo, headers=h(tokens["admin"])).status_code, 409)
    check("papel invalido -> 422",
          client.post("/api/users", json={**novo, "email": "x@teste-users.com", "role": "root"},
                      headers=h(tokens["admin"])).status_code, 422)
    check("senha curta -> 422",
          client.post("/api/users", json={**novo, "email": "y@teste-users.com", "password": "123"},
                      headers=h(tokens["admin"])).status_code, 422)
    check("e-mail invalido -> 422",
          client.post("/api/users", json={**novo, "email": "nao-e-email"},
                      headers=h(tokens["admin"])).status_code, 422)
    check("nome em branco -> 422",
          client.post("/api/users", json={**novo, "email": "z@teste-users.com", "name": "   "},
                      headers=h(tokens["admin"])).status_code, 422)

    print("\n[5] PATCH /api/users/{id} — so admin")
    check("sem token -> 401", client.patch(f"/api/users/{novo_id}", json={"name": "X"}).status_code, 401)
    check("viewer -> 403",
          client.patch(f"/api/users/{novo_id}", json={"name": "X"}, headers=h(tokens["viewer"])).status_code, 403)
    check("operator -> 403",
          client.patch(f"/api/users/{novo_id}", json={"name": "X"}, headers=h(tokens["operator"])).status_code, 403)
    check("id inexistente -> 404",
          client.patch("/api/users/999999", json={"name": "X"}, headers=h(tokens["admin"])).status_code, 404)

    r = client.patch(f"/api/users/{novo_id}",
                     json={"name": "Conta Renomeada", "role": "operator"},
                     headers=h(tokens["admin"]))
    check("admin -> 200", r.status_code, 200)
    check("nome alterado", r.json()["name"], "Conta Renomeada")
    check("papel alterado", r.json()["role"], "operator")
    check_true("password_hash ausente no PATCH", "password_hash" not in r.json())
    check("papel invalido no PATCH -> 422",
          client.patch(f"/api/users/{novo_id}", json={"role": "root"}, headers=h(tokens["admin"])).status_code, 422)

    print("\n[6] Campos protegidos nao mudam por PATCH")
    hash_antes = _hash_de(novo["email"])
    r = client.patch(f"/api/users/{novo_id}",
                     json={"id": 4242, "email": "sequestrado@teste-users.com",
                           "password_hash": "invadido", "name": "So o nome muda"},
                     headers=h(tokens["admin"]))
    check("PATCH ignora campos extras -> 200", r.status_code, 200)
    check("id preservado", r.json()["id"], novo_id)
    check("email preservado", r.json()["email"], novo["email"])
    check("nome aplicado", r.json()["name"], "So o nome muda")
    check("password_hash preservado", _hash_de(novo["email"]), hash_antes)

    print("\n[7] Redefinicao de senha pelo admin")
    r = client.patch(f"/api/users/{novo_id}", json={"password": "senha-nova-4567"},
                     headers=h(tokens["admin"]))
    check("PATCH senha -> 200", r.status_code, 200)
    check_true("hash mudou", _hash_de(novo["email"]) != hash_antes)
    check("senha antiga nao entra mais",
          client.post("/api/auth/login",
                      json={"email": novo["email"], "password": novo["password"]}).status_code, 401)
    check("senha nova entra",
          client.post("/api/auth/login",
                      json={"email": novo["email"], "password": "senha-nova-4567"}).status_code, 200)
    check("senha curta no PATCH -> 422",
          client.patch(f"/api/users/{novo_id}", json={"password": "123"},
                       headers=h(tokens["admin"])).status_code, 422)

    print("\n[8] Desativacao corta o acesso na hora (mecanismo da Fase 1)")
    token_alvo = client.post("/api/auth/login",
                             json={"email": novo["email"], "password": "senha-nova-4567"}).json()["access_token"]
    check("antes: /me -> 200", client.get("/api/auth/me", headers=h(token_alvo)).status_code, 200)
    r = client.patch(f"/api/users/{novo_id}", json={"is_active": False}, headers=h(tokens["admin"]))
    check("PATCH desativar -> 200", r.status_code, 200)
    check("is_active=false", r.json()["is_active"], False)
    check("JWT antigo -> 403", client.get("/api/auth/me", headers=h(token_alvo)).status_code, 403)
    check("leitura tambem bloqueada -> 403",
          client.get("/api/printers", headers=h(token_alvo)).status_code, 403)
    check("login de conta desativada -> 403",
          client.post("/api/auth/login",
                      json={"email": novo["email"], "password": "senha-nova-4567"}).status_code, 403)
    check("reativar -> 200",
          client.patch(f"/api/users/{novo_id}", json={"is_active": True},
                       headers=h(tokens["admin"])).status_code, 200)
    check("depois de reativar, /me -> 200", client.get("/api/auth/me", headers=h(token_alvo)).status_code, 200)

    print("\n[9] Ultimo admin ativo nao pode perder o proprio acesso")
    admin_id = next(u["id"] for u in client.get("/api/users", headers=h(tokens["admin"])).json()
                    if u["email"] == CONTAS["admin"][0])
    admin2_id = next(u["id"] for u in client.get("/api/users", headers=h(tokens["admin"])).json()
                     if u["email"] == CONTAS["admin2"][0])

    # Com DOIS admins ativos, rebaixar um e permitido (o outro desfaz).
    check("com outro admin ativo, rebaixar -> 200",
          client.patch(f"/api/users/{admin2_id}", json={"role": "viewer"},
                       headers=h(tokens["admin"])).status_code, 200)

    # Agora so resta um admin ativo: nem rebaixar nem desativar.
    check("ultimo admin: rebaixar -> 409",
          client.patch(f"/api/users/{admin_id}", json={"role": "operator"},
                       headers=h(tokens["admin"])).status_code, 409)
    check("ultimo admin: desativar -> 409",
          client.patch(f"/api/users/{admin_id}", json={"is_active": False},
                       headers=h(tokens["admin"])).status_code, 409)
    check("ultimo admin: renomear continua permitido -> 200",
          client.patch(f"/api/users/{admin_id}", json={"name": "Admin Renomeado"},
                       headers=h(tokens["admin"])).status_code, 200)

    with Session(engine) as s:
        ainda_admin = s.exec(select(User).where(User.email == CONTAS["admin"][0])).first()
    check("papel do ultimo admin intacto", ainda_admin.role, "admin")
    check("ultimo admin continua ativo", ainda_admin.is_active, True)

    # Repor um segundo admin destrava a operacao.
    check("promover outro admin -> 200",
          client.patch(f"/api/users/{admin2_id}", json={"role": "admin"},
                       headers=h(tokens["admin"])).status_code, 200)
    check("com dois admins, desativar o primeiro -> 200",
          client.patch(f"/api/users/{admin_id}", json={"is_active": False},
                       headers=h(tokens["admin"])).status_code, 200)
    _set_ativo(CONTAS["admin"][0], True)

    print("\n[10] POST /api/auth/register nao existe mais (migrado para /api/users)")
    check("register -> 404",
          client.post("/api/auth/register", json=novo, headers=h(tokens["admin"])).status_code, 404)

    print("\n" + "=" * 70)
    if _falhas:
        print(f"{len(_falhas)} FALHA(S): {_falhas}")
    else:
        print("TODOS OS TESTES PASSARAM")
    print("=" * 70)
    return 1 if _falhas else 0


if __name__ == "__main__":
    import shutil
    import sys

    try:
        codigo = main()
    finally:
        shutil.rmtree(_TMP_DB.parent, ignore_errors=True)
    sys.exit(codigo)
