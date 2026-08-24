"""
Fase 1 - Autenticacao, RBAC e protecao das rotas.

Diferente dos demais tests_*.py, este NAO precisa do backend rodando: usa o
TestClient do FastAPI contra um SQLite temporario, criado do zero e apagado no
final. O banco real (printer_control.db) nunca e tocado.

    .\\venv\\Scripts\\python.exe tests_rbac.py
"""
import os
import tempfile
from pathlib import Path

# Precisa vir ANTES de importar app.config: as Settings leem o ambiente no import.
_TMP_DB = Path(tempfile.mkdtemp(prefix="printercontrol-rbac-")) / "rbac_test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP_DB.as_posix()}"
os.environ["ALLOW_MOCK_COLLECT"] = "true"
os.environ["ENVIRONMENT"] = "development"

from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import Session, select  # noqa: E402

from app.database import create_db_and_tables, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models.alert import Alert  # noqa: E402
from app.models.printer import Printer  # noqa: E402
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
    "admin": ("admin@teste-rbac.com", Role.ADMIN.value, True),
    "operator": ("operator@teste-rbac.com", Role.OPERATOR.value, True),
    "viewer": ("viewer@teste-rbac.com", Role.VIEWER.value, True),
    "inativo": ("inativo@teste-rbac.com", Role.ADMIN.value, False),
}


def semear():
    """Cria as contas de teste e uma impressora + alerta para as rotas de escrita."""
    create_db_and_tables()
    with Session(engine) as s:
        for _, (email, role, ativo) in CONTAS.items():
            s.add(User(email=email, password_hash=hash_password(SENHA), name=email,
                       role=role, is_active=ativo))
        printer = Printer(server="teste", name="IMPRESSORA_RBAC", ip="10.255.255.253",
                          model="Modelo Teste", department="TI")
        s.add(printer)
        s.commit()
        s.refresh(printer)
        alerta = Alert(printer_id=printer.id, severity="critical",
                       message="alerta de teste", alert_type="toner:K")
        s.add(alerta)
        s.commit()
        s.refresh(alerta)
        return printer.id, alerta.id


def h(token):
    return {"Authorization": f"Bearer {token}"}


def main():
    printer_id, alert_id = semear()
    client = TestClient(app)
    tokens = {}

    print("\n[1] Login")
    for papel, (email, _, _) in CONTAS.items():
        r = client.post("/api/auth/login", json={"email": email, "password": SENHA})
        if papel == "inativo":
            check("login de conta desativada -> 403", r.status_code, 403)
        else:
            check(f"login {papel}", r.status_code, 200)
            body = r.json()
            tokens[papel] = body["access_token"]
            check(f"login {papel} devolve role", body["user"]["role"], CONTAS[papel][1])
            check(f"login {papel} devolve is_active", body["user"]["is_active"], True)

    r = client.post("/api/auth/login", json={"email": "admin@teste-rbac.com", "password": "errada"})
    check("senha errada -> 401", r.status_code, 401)

    print("\n[2] GET /api/auth/me")
    check("sem token -> 401", client.get("/api/auth/me").status_code, 401)
    check("token invalido -> 401", client.get("/api/auth/me", headers=h("a.b.c")).status_code, 401)
    r = client.get("/api/auth/me", headers=h(tokens["viewer"]))
    check("com token -> 200", r.status_code, 200)
    check("papel correto", r.json()["role"], "viewer")

    print("\n[3] Usuario desativado APOS a emissao do token")
    # Token emitido enquanto a conta estava ativa continua valido no JWT,
    # mas o usuario e relido do banco a cada request -> perde o acesso.
    token_temp = tokens["operator"]
    _set_ativo(CONTAS["operator"][0], False)
    check("token de conta desativada -> 403", client.get("/api/auth/me", headers=h(token_temp)).status_code, 403)
    _set_ativo(CONTAS["operator"][0], True)
    check("reativado -> 200", client.get("/api/auth/me", headers=h(token_temp)).status_code, 200)

    print("\n[4] Criacao de conta e administrativa (POST /api/users, Fase 3)")
    # Ate a Fase 2 isso vivia em POST /api/auth/register; a Fase 3 moveu a
    # criacao para o recurso /api/users. O que importa aqui e o RBAC — a
    # cobertura funcional completa esta em tests_users.py.
    novo = {"email": "novo@teste-rbac.com", "password": "outra-senha-123", "name": "Novo"}
    check("sem token -> 401", client.post("/api/users", json=novo).status_code, 401)
    check("viewer -> 403", client.post("/api/users", json=novo, headers=h(tokens["viewer"])).status_code, 403)
    check("operator -> 403", client.post("/api/users", json=novo, headers=h(tokens["operator"])).status_code, 403)
    r = client.post("/api/users", json=novo, headers=h(tokens["admin"]))
    check("admin -> 201", r.status_code, 201)
    check("papel padrao e viewer", r.json()["role"], "viewer")
    check_true("nao devolve token", "access_token" not in r.json())
    check("email duplicado -> 409",
          client.post("/api/users", json=novo, headers=h(tokens["admin"])).status_code, 409)
    r = client.post("/api/users",
                    json={"email": "op2@teste-rbac.com", "password": "outra-senha-123",
                          "name": "Op", "role": "operator"},
                    headers=h(tokens["admin"]))
    check("admin pode definir role", r.json().get("role"), "operator")
    check("role invalida -> 422",
          client.post("/api/users",
                      json={**novo, "email": "x@teste-rbac.com", "role": "root"},
                      headers=h(tokens["admin"])).status_code, 422)
    check("GET /api/users viewer -> 403",
          client.get("/api/users", headers=h(tokens["viewer"])).status_code, 403)
    check("GET /api/users admin -> 200",
          client.get("/api/users", headers=h(tokens["admin"])).status_code, 200)

    print("\n[5] PATCH /api/alerts/{id}/resolve (estava SEM protecao antes da Fase 1)")
    check("sem token -> 401", client.patch(f"/api/alerts/{alert_id}/resolve").status_code, 401)
    check("viewer -> 403", client.patch(f"/api/alerts/{alert_id}/resolve", headers=h(tokens["viewer"])).status_code, 403)
    r = client.patch(f"/api/alerts/{alert_id}/resolve", headers=h(tokens["operator"]))
    check("operator -> 200", r.status_code, 200)
    check_true("alerta marcado como resolvido", r.json().get("resolved_at") is not None)

    print("\n[6] POST /api/alerts/{id}/notify")
    check("sem token -> 401", client.post(f"/api/alerts/{alert_id}/notify").status_code, 401)
    check("viewer -> 403", client.post(f"/api/alerts/{alert_id}/notify", headers=h(tokens["viewer"])).status_code, 403)
    check("operator -> 200", client.post(f"/api/alerts/{alert_id}/notify", headers=h(tokens["operator"])).status_code, 200)

    print("\n[7] Cadastro de impressoras e administrativo")
    nova = {"ip": "10.255.255.252", "name": "RBAC_TEMP", "model": "M", "department": "TI"}
    check("sem token -> 401", client.post("/api/printers", json=nova).status_code, 401)
    check("viewer -> 403", client.post("/api/printers", json=nova, headers=h(tokens["viewer"])).status_code, 403)
    check("operator -> 403", client.post("/api/printers", json=nova, headers=h(tokens["operator"])).status_code, 403)
    check("admin -> 200", client.post("/api/printers", json=nova, headers=h(tokens["admin"])).status_code, 200)
    check("PATCH viewer -> 403",
          client.patch(f"/api/printers/{printer_id}", json={"department": "X"}, headers=h(tokens["viewer"])).status_code, 403)
    check("PATCH admin -> 200",
          client.patch(f"/api/printers/{printer_id}", json={"department": "TI"}, headers=h(tokens["admin"])).status_code, 200)

    print("\n[8] Leituras manuais sao operacionais")
    leitura = {"status": "online", "page_count": 10}
    check("sem token -> 401", client.post(f"/api/printers/{printer_id}/readings", json=leitura).status_code, 401)
    check("viewer -> 403",
          client.post(f"/api/printers/{printer_id}/readings", json=leitura, headers=h(tokens["viewer"])).status_code, 403)
    check("operator -> 200",
          client.post(f"/api/printers/{printer_id}/readings", json=leitura, headers=h(tokens["operator"])).status_code, 200)

    print("\n[9] Coleta simulada e administrativa")
    mock = {"mode": "mock", "scenario": "online_mono"}
    check("mock sem token -> 401", client.post(f"/api/collect/printers/{printer_id}", json=mock).status_code, 401)
    check("mock com viewer -> 403",
          client.post(f"/api/collect/printers/{printer_id}", json=mock, headers=h(tokens["viewer"])).status_code, 403)
    check("mock com operator -> 403",
          client.post(f"/api/collect/printers/{printer_id}", json=mock, headers=h(tokens["operator"])).status_code, 403)
    check("mock com admin -> 200",
          client.post(f"/api/collect/printers/{printer_id}", json=mock, headers=h(tokens["admin"])).status_code, 200)
    check("/collect/fleet operator -> 403", client.post("/api/collect/fleet", headers=h(tokens["operator"])).status_code, 403)
    check("/collect/scenarios sem token -> 401", client.get("/api/collect/scenarios").status_code, 401)
    check("/collect/scenarios viewer -> 403",
          client.get("/api/collect/scenarios", headers=h(tokens["viewer"])).status_code, 403)
    check("/collect/scenarios admin -> 200",
          client.get("/api/collect/scenarios", headers=h(tokens["admin"])).status_code, 200)
    check("/collect/scheduler operator -> 403",
          client.get("/api/collect/scheduler", headers=h(tokens["operator"])).status_code, 403)

    print("\n[10] Print Server")
    check("/servers/current sem token -> 401", client.get("/api/servers/current").status_code, 401)
    check("/servers/current viewer -> 200",
          client.get("/api/servers/current", headers=h(tokens["viewer"])).status_code, 200)
    check("/servers/discover operator -> 403",
          client.post("/api/servers/discover", headers=h(tokens["operator"])).status_code, 403)
    check("/servers/sync operator -> 403",
          client.post("/api/servers/sync", headers=h(tokens["operator"])).status_code, 403)

    print("\n[11] Leitura passou a exigir sessao (Fase 2)")
    check("GET /api/printers sem token -> 401", client.get("/api/printers").status_code, 401)
    check("GET /api/printers/with-status sem token -> 401",
          client.get("/api/printers/with-status").status_code, 401)
    check("GET /api/printers/monthly-report sem token -> 401",
          client.get("/api/printers/monthly-report").status_code, 401)
    check("GET /api/printers/{id}/readings sem token -> 401",
          client.get(f"/api/printers/{printer_id}/readings").status_code, 401)
    check("GET /api/alerts sem token -> 401", client.get("/api/alerts").status_code, 401)
    check("GET /api/alerts/{id} sem token -> 401",
          client.get(f"/api/alerts/{alert_id}").status_code, 401)
    # Viewer le tudo isso normalmente — fechar nao pode virar bloqueio geral.
    for rota in ("/api/printers", "/api/printers/with-status", "/api/alerts",
                 f"/api/printers/{printer_id}", f"/api/alerts/{alert_id}",
                 f"/api/printers/{printer_id}/readings"):
        check(f"viewer le {rota}", client.get(rota, headers=h(tokens["viewer"])).status_code, 200)
    check("token invalido na leitura -> 401",
          client.get("/api/printers", headers=h("a.b.c")).status_code, 401)
    # Conta desativada perde ate a leitura, mesmo com token ainda valido.
    _set_ativo(CONTAS["viewer"][0], False)
    check("conta desativada na leitura -> 403",
          client.get("/api/printers", headers=h(tokens["viewer"])).status_code, 403)
    _set_ativo(CONTAS["viewer"][0], True)

    print("\n[11b] Superficie publica restante")
    publicas = sorted(
        (metodo.upper(), rota)
        for rota, ops in app.openapi()["paths"].items()
        for metodo, op in ops.items()
        if not op.get("security")
    )
    print(f"       {publicas}")
    check("apenas login e health sao publicos", publicas,
          [("GET", "/"), ("GET", "/health"), ("POST", "/api/auth/login")])

    print("\n[12] SECRET_KEY em producao")
    from pydantic import ValidationError

    from app.config import DEV_SECRET_KEY, Settings

    # PRINT_SERVER_MODE=real entra em todo caso de producao a partir da Fase 9:
    # producao passou a recusar tambem a simulacao, e o validador dela roda
    # ANTES do de secret. Sem isso, os casos abaixo passariam a ser recusados
    # pelo motivo errado — e o positivo falharia. Fixar o modo mantem a
    # SECRET_KEY como unica variavel sob teste aqui; o bloqueio de simulacao
    # tem suite propria em tests_environment.py.
    # allow_mock_collect explicito porque esta suite exporta
    # ALLOW_MOCK_COLLECT=true no topo do arquivo, e `_env_file=None` desliga
    # apenas o .env — as variaveis do PROCESSO continuam sendo lidas.
    producao = dict(environment="production", print_server_mode="real", allow_mock_collect=False)

    casos = [
        ("secret default em producao e recusado", dict(producao, secret_key=DEV_SECRET_KEY), False),
        ("secret curta em producao e recusada", dict(producao, secret_key="curta"), False),
        ("secret forte em producao e aceita", dict(producao, secret_key="k" * 48), True),
        ("development continua com o default", dict(environment="development", secret_key=DEV_SECRET_KEY), True),
    ]
    for nome, kwargs, deve_aceitar in casos:
        try:
            Settings(_env_file=None, **kwargs)
            aceitou = True
        except ValidationError:
            aceitou = False
        check_true(nome, aceitou == deve_aceitar, f"aceitou={aceitou}")

    print("\n[13] Frontend espelha a mesma hierarquia de papeis")
    check_true("ROLE_IMPLIES do frontend == do backend", _confere_rbac_do_frontend())

    print("\n[14] Migracao aditiva de banco legado (sem role/is_active)")
    check_true("usuario legado preservado e promovido a admin", _testa_migracao_legada())

    print("\n" + "=" * 70)
    if _falhas:
        print(f"{len(_falhas)} FALHA(S): {_falhas}")
    else:
        print("TODOS OS TESTES PASSARAM")
    print("=" * 70)
    return 1 if _falhas else 0


def _set_ativo(email, ativo):
    with Session(engine) as s:
        u = s.exec(select(User).where(User.email == email)).first()
        u.is_active = ativo
        s.add(u)
        s.commit()


def _confere_rbac_do_frontend():
    """
    O frontend tem a sua propria copia da hierarquia de papeis, em
    src/lib/permissions.ts (o navegador nao consulta ROLE_IMPLIES do Python).
    Este teste compara as duas para que uma nao mude sem a outra — o risco
    real de duplicar a regra e ela silenciosamente divergir.
    """
    import re

    from app.models.user import ROLE_IMPLIES

    arquivo = Path(__file__).resolve().parent.parent / "src" / "lib" / "permissions.ts"
    if not arquivo.exists():
        print(f"       [ignorado] {arquivo} nao encontrado")
        return True

    texto = arquivo.read_text(encoding="utf-8")
    bloco = re.search(r"ROLE_IMPLIES:\s*Record<Role,\s*readonly Role\[\]>\s*=\s*\{(.*?)\n\};",
                      texto, re.S)
    if not bloco:
        print("       [FALHA] nao encontrei ROLE_IMPLIES em permissions.ts")
        return False

    do_frontend = {
        papel: set(re.findall(r'"(\w+)"', lista))
        for papel, lista in re.findall(r"(\w+):\s*\[([^\]]*)\]", bloco.group(1))
    }
    print(f"       backend : { {k: sorted(v) for k, v in ROLE_IMPLIES.items()} }")
    print(f"       frontend: { {k: sorted(v) for k, v in do_frontend.items()} }")
    return do_frontend == {k: set(v) for k, v in ROLE_IMPLIES.items()}


def _testa_migracao_legada():
    """
    Cria um banco no formato ANTERIOR a Fase 1 (users sem role/is_active),
    roda a migracao e confirma que o usuario existente foi preservado e
    promovido a admin.
    """
    import sqlite3

    from sqlalchemy import create_engine as sa_create_engine, text

    legado = _TMP_DB.with_name("legado.db")
    if legado.exists():
        legado.unlink()
    con = sqlite3.connect(legado)
    con.executescript(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            email VARCHAR UNIQUE,
            password_hash VARCHAR,
            name VARCHAR,
            created_at DATETIME
        );
        INSERT INTO users (email, password_hash, name, created_at)
        VALUES ('antigo@teste-rbac.com', 'hash', 'Antigo', '2020-01-01 00:00:00');
        """
    )
    con.commit()
    con.close()

    import app.database as db

    engine_original = db.engine
    db.engine = sa_create_engine(f"sqlite:///{legado.as_posix()}",
                                 connect_args={"check_same_thread": False})
    try:
        db._migrate_user_rbac()
        db._migrate_user_rbac()  # idempotencia: rodar de novo nao pode falhar
        with db.engine.connect() as conn:
            linhas = list(conn.execute(text("SELECT email, name, role, is_active FROM users")))
    finally:
        db.engine.dispose()
        db.engine = engine_original

    print(f"       usuarios apos migracao: {linhas}")
    return (
        len(linhas) == 1
        and linhas[0][0] == "antigo@teste-rbac.com"
        and linhas[0][2] == "admin"
        and bool(linhas[0][3])
    )


if __name__ == "__main__":
    import shutil
    import sys

    try:
        codigo = main()
    finally:
        shutil.rmtree(_TMP_DB.parent, ignore_errors=True)
    sys.exit(codigo)
