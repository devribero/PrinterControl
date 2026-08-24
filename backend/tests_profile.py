"""
Fase 8 - Perfil proprio e troca de senha.

Como as demais suites desde a Fase 1, NAO precisa do backend rodando:
TestClient contra um SQLite temporario. O banco real nunca e aberto.

    .\\venv\\Scripts\\python.exe tests_profile.py
"""
import os
import tempfile
from pathlib import Path

# Antes de importar app.config: as Settings leem o ambiente no import.
_TMP = Path(tempfile.mkdtemp(prefix="printercontrol-perfil-"))
os.environ["DATABASE_URL"] = f"sqlite:///{(_TMP / 'perfil_test.db').as_posix()}"
os.environ["ENVIRONMENT"] = "development"
os.environ["PRINT_SERVER_MODE"] = "mock"

from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import Session  # noqa: E402

from app.database import create_db_and_tables, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models.user import Role, User  # noqa: E402
from app.services.auth import hash_password  # noqa: E402

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
    "admin": ("admin@teste-perfil.com", Role.ADMIN.value),
    "viewer": ("viewer@teste-perfil.com", Role.VIEWER.value),
}


def h(token):
    return {"Authorization": f"Bearer {token}"}


def login(client, email, senha):
    return client.post("/api/auth/login", json={"email": email, "password": senha})


def main():
    create_db_and_tables()

    ids = {}
    with Session(engine) as s:
        for papel, (email, role) in CONTAS.items():
            u = User(email=email, password_hash=hash_password(SENHA), name=f"Nome {papel}", role=role)
            s.add(u)
            s.commit()
            s.refresh(u)
            ids[papel] = u.id

    client = TestClient(app)
    tokens = {papel: login(client, email, SENHA).json()["access_token"] for papel, (email, _) in CONTAS.items()}

    print("\n[1] Editar o proprio nome (PATCH /api/auth/me)")
    check("sem token -> 401", client.patch("/api/auth/me", json={"name": "X"}).status_code, 401)
    r = client.patch("/api/auth/me", json={"name": "  Nome Novo  "}, headers=h(tokens["viewer"]))
    check("viewer edita o proprio -> 200", r.status_code, 200)
    check("nome salvo com trim", r.json()["name"], "Nome Novo")
    check("GET /me reflete", client.get("/api/auth/me", headers=h(tokens["viewer"])).json()["name"], "Nome Novo")
    check("nome vazio -> 422",
          client.patch("/api/auth/me", json={"name": "   "}, headers=h(tokens["viewer"])).status_code, 422)

    print("\n[2] O perfil proprio nao e porta dos fundos para escalar privilegio")
    # Campos extras sao IGNORADOS pelo schema (ProfileUpdate so tem `name`).
    # Se um dia alguem acrescentar role/is_active ali, este teste quebra.
    r = client.patch(
        "/api/auth/me",
        json={"name": "Tentativa", "role": "admin", "is_active": False, "email": "outro@x.com"},
        headers=h(tokens["viewer"]),
    )
    check("PATCH com campos extras -> 200", r.status_code, 200)
    depois = client.get("/api/auth/me", headers=h(tokens["viewer"])).json()
    check("papel continua viewer", depois["role"], "viewer")
    check("conta continua ativa", depois["is_active"], True)
    check("e-mail intacto", depois["email"], CONTAS["viewer"][0])
    check("so o nome mudou", depois["name"], "Tentativa")

    print("\n[3] Nao ha como editar o perfil de outra pessoa por esta rota")
    # A rota nao aceita id: o alvo e sempre a sessao.
    check("PATCH /api/auth/me/{id} nao existe -> 404 ou 405",
          client.patch(f"/api/auth/me/{ids['admin']}", json={"name": "Invadido"},
                       headers=h(tokens["viewer"])).status_code in (404, 405), True)
    check("nome do admin intacto",
          client.get("/api/auth/me", headers=h(tokens["admin"])).json()["name"], "Nome admin")

    print("\n[4] Trocar a propria senha exige a senha ATUAL")
    check("sem token -> 401",
          client.post("/api/auth/change-password",
                      json={"current_password": SENHA, "new_password": "outrasenha1"}).status_code, 401)
    check("senha atual errada -> 400",
          client.post("/api/auth/change-password",
                      json={"current_password": "chute-errado", "new_password": "outrasenha1"},
                      headers=h(tokens["viewer"])).status_code, 400)
    check("senha inalterada apos tentativa errada",
          login(client, CONTAS["viewer"][0], SENHA).status_code, 200)

    print("\n[5] Regras da senha nova")
    check("menos de 8 caracteres -> 422",
          client.post("/api/auth/change-password",
                      json={"current_password": SENHA, "new_password": "curta"},
                      headers=h(tokens["viewer"])).status_code, 422)
    check("igual a atual -> 400",
          client.post("/api/auth/change-password",
                      json={"current_password": SENHA, "new_password": SENHA},
                      headers=h(tokens["viewer"])).status_code, 400)

    print("\n[6] Troca bem-sucedida")
    NOVA = "senha-nova-987654"
    r = client.post("/api/auth/change-password",
                    json={"current_password": SENHA, "new_password": NOVA},
                    headers=h(tokens["viewer"]))
    check("troca -> 204", r.status_code, 204)
    check("login com a senha NOVA -> 200", login(client, CONTAS["viewer"][0], NOVA).status_code, 200)
    check("login com a senha ANTIGA -> 401", login(client, CONTAS["viewer"][0], SENHA).status_code, 401)
    check("a senha do admin nao foi tocada", login(client, CONTAS["admin"][0], SENHA).status_code, 200)

    print("\n[7] Limitacao conhecida: o token antigo sobrevive a troca")
    # Documentada no docstring da rota. O JWT e stateless e nao guarda versao
    # de senha, entao sessoes abertas antes da troca seguem validas ate
    # expirarem. Este teste existe para a limitacao ser VISIVEL: se um dia
    # ela for fechada, ele falha e obriga a atualizar a documentacao.
    ainda_vale = client.get("/api/auth/me", headers=h(tokens["viewer"]))
    check_true("token emitido antes da troca continua aceito", ainda_vale.status_code == 200,
               f"status={ainda_vale.status_code} (se virou 401, a limitacao foi fechada)")

    print("\n[8] A rota administrativa continua existindo e separada")
    # Trocar a propria senha nao substitui o reset por admin da Fase 3.
    r = client.patch(f"/api/users/{ids['viewer']}", json={"password": "reset-pelo-admin-1"},
                     headers=h(tokens["admin"]))
    check("admin ainda redefine senha de terceiro -> 200", r.status_code, 200)
    check("login com a senha redefinida",
          login(client, CONTAS["viewer"][0], "reset-pelo-admin-1").status_code, 200)
    check("viewer NAO redefine a senha de outro -> 403",
          client.patch(f"/api/users/{ids['admin']}", json={"password": "tentativa123"},
                       headers=h(tokens["viewer"])).status_code, 403)

    print("\n" + "=" * 70)
    if _falhas:
        print(f"{len(_falhas)} FALHA(S): {_falhas}")
    else:
        print("TODOS OS TESTES PASSARAM")
    print("=" * 70)
    return 1 if _falhas else 0


if __name__ == "__main__":
    raise SystemExit(main())
