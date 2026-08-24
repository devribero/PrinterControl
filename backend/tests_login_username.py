"""
Login por username e troca de senha obrigatoria (2026-08-24).

Cobre as duas mudancas desta rodada:

    1. `POST /api/auth/login` aceita e-mail OU username no mesmo campo
       `email`, levando a MESMA conta (mesmo `sub` no JWT).
    2. `must_change_password`: conta criada ou resetada por um admin nasce
       trancada — `require_active_user` recusa tudo com 403 exceto
       `GET /api/auth/me` e `POST /api/auth/change-password` — ate a propria
       pessoa trocar a senha.

Como as demais suites desde a Fase 1, NAO precisa do backend rodando.

    .\\venv\\Scripts\\python.exe tests_login_username.py
"""
import os
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="printercontrol-login-username-"))
os.environ["DATABASE_URL"] = f"sqlite:///{(_TMP / 'login_username_test.db').as_posix()}"
os.environ["ENVIRONMENT"] = "development"
os.environ["PRINT_SERVER_MODE"] = "mock"

from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import Session  # noqa: E402

from app.database import create_db_and_tables, engine  # noqa: E402
from app.dependencies import MUST_CHANGE_PASSWORD_DETAIL  # noqa: E402
from app.main import app  # noqa: E402
from app.models.user import Role, User  # noqa: E402
from app.routes.auth import login_limiter  # noqa: E402
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


create_db_and_tables()
client = TestClient(app)


def h(token):
    return {"Authorization": f"Bearer {token}"}


def login(identificador, senha):
    login_limiter.reset()
    return client.post("/api/auth/login", json={"email": identificador, "password": senha})


# ---------------------------------------------------------------------------
print("\n[1] Login por e-mail e por username levam a mesma conta")

SENHA_ANA = "senha-correta-123"
with Session(engine) as s:
    ana = User(
        email="ana.souza@elgin.com.br",
        username="ana.souza",
        name="Ana Souza",
        password_hash=hash_password(SENHA_ANA),
        role=Role.VIEWER,
        must_change_password=False,
    )
    s.add(ana)
    s.commit()

r_email = login("ana.souza@elgin.com.br", SENHA_ANA)
check("login por e-mail -> 200", r_email.status_code, 200)

r_user = login("ana.souza", SENHA_ANA)
check("login por username -> 200", r_user.status_code, 200)

check_true(
    "os dois tokens carregam o mesmo `sub` (e-mail)",
    r_email.json()["user"]["email"] == r_user.json()["user"]["email"] == "ana.souza@elgin.com.br",
)
check("username devolvido no login", r_user.json()["user"]["username"], "ana.souza")

check("username em CAIXA ALTA tambem entra (normalizado)", login("ANA.SOUZA", SENHA_ANA).status_code, 200)

check(
    "username com senha errada -> 401 (mesma mensagem do e-mail)",
    login("ana.souza", "chute-errado").json()["detail"],
    login("ana.souza@elgin.com.br", "chute-errado").json()["detail"],
)

check("username inexistente -> 401 (nao 404, nao revela)", login("nao-existe-ninguem", "qualquer").status_code, 401)


# ---------------------------------------------------------------------------
print("\n[2] Username e e-mail da MESMA conta compartilham o limitador")
# Risco real: se as duas formas caissem em baldes diferentes, alternar entre
# elas dobraria as tentativas permitidas contra uma unica conta.
login_limiter.reset()
for _ in range(login_limiter.max_tentativas):
    client.post("/api/auth/login", json={"email": "ana.souza", "password": "errada"})

r_bloqueado_email = client.post(
    "/api/auth/login", json={"email": "ana.souza@elgin.com.br", "password": SENHA_ANA}
)
check_true(
    "estourar tentativas pelo username tambem bloqueia a forma por e-mail",
    r_bloqueado_email.status_code == 429,
    str(r_bloqueado_email.status_code),
)
login_limiter.reset()


# ---------------------------------------------------------------------------
print("\n[3] Conta criada por admin nasce com must_change_password=True")

ADMIN_SENHA = "senha-admin-123456"
with Session(engine) as s:
    admin = User(
        email="admin@elgin.com.br",
        username="admin",
        name="Admin",
        password_hash=hash_password(ADMIN_SENHA),
        role=Role.ADMIN,
        must_change_password=False,
    )
    s.add(admin)
    s.commit()

token_admin = login("admin@elgin.com.br", ADMIN_SENHA).json()["access_token"]

r_novo = client.post(
    "/api/users",
    json={
        "email": "novato@elgin.com.br",
        "username": "novato",
        "password": "senha-provisoria-123",
        "name": "Conta Nova",
        "role": "viewer",
    },
    headers=h(token_admin),
)
check("criacao -> 201", r_novo.status_code, 201)
check_true("nasce com must_change_password=True", r_novo.json()["must_change_password"] is True)

r_login_novo = login("novato", "senha-provisoria-123")
check("login da conta nova (por username) -> 200", r_login_novo.status_code, 200)
check_true(
    "login sinaliza must_change_password na resposta",
    r_login_novo.json()["user"]["must_change_password"] is True,
)
token_novo = r_login_novo.json()["access_token"]


# ---------------------------------------------------------------------------
print("\n[4] must_change_password bloqueia tudo, exceto /me e /change-password")

r_printers = client.get("/api/printers", headers=h(token_novo))
check("GET /api/printers -> 403 (trancado)", r_printers.status_code, 403)
check("detail explica o motivo", r_printers.json()["detail"], MUST_CHANGE_PASSWORD_DETAIL)

r_patch_perfil = client.patch("/api/auth/me", json={"name": "Tentando escapar"}, headers=h(token_novo))
check("PATCH /api/auth/me -> 403 (nao e uma das duas excecoes)", r_patch_perfil.status_code, 403)

r_me = client.get("/api/auth/me", headers=h(token_novo))
check("GET /api/auth/me continua acessivel -> 200", r_me.status_code, 200)
check_true("me tambem mostra a flag ligada", r_me.json()["must_change_password"] is True)

r_troca_errada = client.post(
    "/api/auth/change-password",
    json={"current_password": "senha-errada", "new_password": "outra-senha-1234"},
    headers=h(token_novo),
)
check("POST /change-password acessivel mesmo trancado -> 400 (senha atual errada)", r_troca_errada.status_code, 400)


# ---------------------------------------------------------------------------
print("\n[5] Trocar a senha destranca a conta")

r_troca = client.post(
    "/api/auth/change-password",
    json={"current_password": "senha-provisoria-123", "new_password": "senha-definitiva-1234"},
    headers=h(token_novo),
)
check("troca com a senha certa -> 204", r_troca.status_code, 204)

r_me_depois = client.get("/api/auth/me", headers=h(token_novo))
check_true("must_change_password desligou", r_me_depois.json()["must_change_password"] is False)

r_printers_depois = client.get("/api/printers", headers=h(token_novo))
check("GET /api/printers liberado apos a troca -> 200", r_printers_depois.status_code, 200)

r_login_depois = login("novato", "senha-definitiva-1234")
check("login com a senha nova (username) -> 200", r_login_depois.status_code, 200)
check_true(
    "login seguinte nao pede mais troca",
    r_login_depois.json()["user"]["must_change_password"] is False,
)


# ---------------------------------------------------------------------------
print("\n[6] Admin redefinindo a senha de outro religa a flag")

r_reset = client.patch(
    f"/api/users/{r_novo.json()['id']}",
    json={"password": "senha-imposta-pelo-admin"},
    headers=h(token_admin),
)
check("PATCH senha pelo admin -> 200", r_reset.status_code, 200)
check_true("must_change_password religou", r_reset.json()["must_change_password"] is True)

r_login_resetado = login("novato@elgin.com.br", "senha-imposta-pelo-admin")
token_resetado = r_login_resetado.json()["access_token"]
r_bloqueado_de_novo = client.get("/api/printers", headers=h(token_resetado))
check("conta resetada volta a ficar trancada -> 403", r_bloqueado_de_novo.status_code, 403)


# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
if _falhas:
    print(f"{len(_falhas)} FALHA(S): {_falhas}")
    raise SystemExit(1)
print("TODOS OS TESTES PASSARAM")
print("=" * 70)
