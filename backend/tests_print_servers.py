"""
Fase 4 - Registro de Print Servers e operacao por servidor.

Como tests_rbac.py/tests_users.py, NAO precisa do backend rodando: TestClient
contra um SQLite temporario. O banco real nunca e aberto.

    .\\venv\\Scripts\\python.exe tests_print_servers.py
"""
import os
import sqlite3
import tempfile
from pathlib import Path

# Antes de importar app.config: as Settings leem o ambiente no import.
_TMP = Path(tempfile.mkdtemp(prefix="printercontrol-servers-"))
_TMP_DB = _TMP / "servers_test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP_DB.as_posix()}"
os.environ["ENVIRONMENT"] = "development"
os.environ["PRINT_SERVER_MODE"] = "mock"
os.environ["PRINT_SERVER_HOST"] = "srv-padrao"

from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import Session, select  # noqa: E402

from app.config import settings  # noqa: E402
from app.database import create_db_and_tables, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models.print_server import PrintServer  # noqa: E402
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
    "admin": ("admin@teste-srv.com", Role.ADMIN.value),
    "operator": ("operator@teste-srv.com", Role.OPERATOR.value),
    "viewer": ("viewer@teste-srv.com", Role.VIEWER.value),
}


def h(token):
    return {"Authorization": f"Bearer {token}"}


def main():
    create_db_and_tables()
    with Session(engine) as s:
        for email, role in CONTAS.values():
            s.add(User(email=email, password_hash=hash_password(SENHA), name=email, role=role))
        s.commit()

    client = TestClient(app)
    tokens = {
        papel: client.post("/api/auth/login", json={"email": email, "password": SENHA}).json()["access_token"]
        for papel, (email, _) in CONTAS.items()
    }

    print("\n[1] O servidor padrao ja nasce registrado")
    r = client.get("/api/servers", headers=h(tokens["viewer"]))
    check("GET /api/servers -> 200", r.status_code, 200)
    servidores = r.json()
    check("1 servidor registrado", len(servidores), 1)
    padrao = servidores[0]
    check("host = PRINT_SERVER_HOST", padrao["host"], "srv-padrao")
    check("marcado como padrao", padrao["is_default"], True)
    check("modo herdado da config global", padrao["mode"], settings.print_server_mode)
    check("status inicial", padrao["last_status"], "unknown")
    check("sem impressoras ainda", padrao["printer_count"], 0)

    print("\n[2] RBAC do registro")
    check("GET sem token -> 401", client.get("/api/servers").status_code, 401)
    novo = {"host": "srv-filial", "name": "Filial Norte", "mode": "mock"}
    check("POST sem token -> 401", client.post("/api/servers", json=novo).status_code, 401)
    check("POST viewer -> 403", client.post("/api/servers", json=novo, headers=h(tokens["viewer"])).status_code, 403)
    check("POST operator -> 403", client.post("/api/servers", json=novo, headers=h(tokens["operator"])).status_code, 403)
    check("PATCH viewer -> 403",
          client.patch(f"/api/servers/{padrao['id']}", json={"name": "X"},
                       headers=h(tokens["viewer"])).status_code, 403)
    check("discover por id viewer -> 403",
          client.post(f"/api/servers/{padrao['id']}/discover", headers=h(tokens["viewer"])).status_code, 403)
    check("sync por id operator -> 403",
          client.post(f"/api/servers/{padrao['id']}/sync", headers=h(tokens["operator"])).status_code, 403)

    print("\n[3] Registro de um segundo servidor")
    r = client.post("/api/servers", json=novo, headers=h(tokens["admin"]))
    check("POST admin -> 201", r.status_code, 201)
    filial = r.json()
    filial_id = filial["id"]
    check("host gravado", filial["host"], "srv-filial")
    check("rotulo gravado", filial["name"], "Filial Norte")
    check("nao e o padrao", filial["is_default"], False)
    check("host duplicado -> 409",
          client.post("/api/servers", json=novo, headers=h(tokens["admin"])).status_code, 409)
    check("modo invalido -> 422",
          client.post("/api/servers", json={"host": "srv-x", "mode": "turbo"},
                      headers=h(tokens["admin"])).status_code, 422)
    check("host vazio -> 422",
          client.post("/api/servers", json={"host": ""}, headers=h(tokens["admin"])).status_code, 422)
    check("id inexistente -> 404",
          client.patch("/api/servers/999999", json={"name": "X"}, headers=h(tokens["admin"])).status_code, 404)

    print("\n[4] Sync por servidor mantem os parques isolados")
    r = client.post(f"/api/servers/{padrao['id']}/sync", headers=h(tokens["admin"]))
    check("sync do padrao -> 200", r.status_code, 200)
    criadas_padrao = r.json()["created"]
    check_true("criou impressoras no padrao", criadas_padrao > 0, str(criadas_padrao))
    check("sync reporta o servidor certo", r.json()["server"], "srv-padrao")

    r = client.post(f"/api/servers/{filial_id}/sync", headers=h(tokens["admin"]))
    check("sync da filial -> 200", r.status_code, 200)
    check("filial criou o mesmo tanto", r.json()["created"], criadas_padrao)
    check("filial nao desativou nada do padrao", r.json()["deactivated"], 0)

    with Session(engine) as s:
        do_padrao = s.exec(select(Printer).where(Printer.server == "srv-padrao")).all()
        da_filial = s.exec(select(Printer).where(Printer.server == "srv-filial")).all()
    check("impressoras do padrao intactas", len(do_padrao), criadas_padrao)
    check("impressoras da filial criadas", len(da_filial), criadas_padrao)
    check_true("todas do padrao seguem ativas", all(p.active for p in do_padrao))

    print("\n[5] FK print_server_id acompanha a string `server`")
    with Session(engine) as s:
        registros = {ps.host: ps.id for ps in s.exec(select(PrintServer)).all()}
        todas = s.exec(select(Printer)).all()
    check_true("toda impressora tem FK preenchida", all(p.print_server_id is not None for p in todas))
    check_true("FK aponta para o servidor da string `server`",
               all(p.print_server_id == registros[p.server] for p in todas))
    check("contagem do padrao na API",
          next(x for x in client.get("/api/servers", headers=h(tokens["admin"])).json()
               if x["host"] == "srv-padrao")["printer_count"], criadas_padrao)

    print("\n[6] Estado do servidor apos a descoberta")
    r = client.post(f"/api/servers/{filial_id}/discover", headers=h(tokens["admin"]))
    check("discover por id -> 200", r.status_code, 200)
    check("descoberta usa o host do registro", r.json()["server"], "srv-filial")
    check("descoberta usa o modo do registro", r.json()["mode"], "mock")
    depois = next(x for x in client.get("/api/servers", headers=h(tokens["admin"])).json()
                  if x["id"] == filial_id)
    check("last_status vira online", depois["last_status"], "online")
    check_true("last_seen_at preenchido", depois["last_seen_at"] is not None)
    check_true("last_sync_at preenchido pelo sync anterior", depois["last_sync_at"] is not None)

    print("\n[7] Servidor desativado nao roda descoberta")
    r = client.patch(f"/api/servers/{filial_id}", json={"active": False}, headers=h(tokens["admin"]))
    check("PATCH desativar -> 200", r.status_code, 200)
    check("active=false", r.json()["active"], False)
    check("discover em servidor desativado -> 409",
          client.post(f"/api/servers/{filial_id}/discover", headers=h(tokens["admin"])).status_code, 409)
    check("sync em servidor desativado -> 409",
          client.post(f"/api/servers/{filial_id}/sync", headers=h(tokens["admin"])).status_code, 409)
    check("reativar -> 200",
          client.patch(f"/api/servers/{filial_id}", json={"active": True},
                       headers=h(tokens["admin"])).status_code, 200)

    print("\n[8] Modo por servidor")
    r = client.patch(f"/api/servers/{filial_id}", json={"mode": "real"}, headers=h(tokens["admin"]))
    check("PATCH modo -> 200", r.status_code, 200)
    check("modo alterado so na filial", r.json()["mode"], "real")
    padrao_agora = next(x for x in client.get("/api/servers", headers=h(tokens["admin"])).json()
                        if x["host"] == "srv-padrao")
    check("padrao continua em mock", padrao_agora["mode"], "mock")
    check("modo invalido no PATCH -> 422",
          client.patch(f"/api/servers/{filial_id}", json={"mode": "turbo"},
                       headers=h(tokens["admin"])).status_code, 422)
    # Modo "real" sem PowerShell/dominio: a rota precisa reportar 502 e
    # registrar o erro no proprio servidor, nunca estourar 500.
    r = client.post(f"/api/servers/{filial_id}/discover", headers=h(tokens["admin"]))
    check_true("modo real fora do dominio -> 502 ou 200", r.status_code in (200, 502), str(r.status_code))
    if r.status_code == 502:
        estado = next(x for x in client.get("/api/servers", headers=h(tokens["admin"])).json()
                      if x["id"] == filial_id)
        check("falha registrada no servidor", estado["last_status"], "error")
        check_true("mensagem de erro guardada", bool(estado["last_error"]), str(estado["last_error"]))
    client.patch(f"/api/servers/{filial_id}", json={"mode": "mock"}, headers=h(tokens["admin"]))

    print("\n[9] Rotas antigas continuam funcionando (compatibilidade)")
    r = client.get("/api/servers/current", headers=h(tokens["viewer"]))
    check("GET /servers/current -> 200", r.status_code, 200)
    check("host do current", r.json()["host"], "srv-padrao")
    check("POST /servers/discover -> 200",
          client.post("/api/servers/discover", headers=h(tokens["admin"])).status_code, 200)
    r = client.post("/api/servers/sync", headers=h(tokens["admin"]))
    check("POST /servers/sync -> 200", r.status_code, 200)
    check("sync padrao nao recriou nada", r.json()["created"], 0)
    check("sync padrao nao desativou nada", r.json()["deactivated"], 0)
    check("host nao pode ser alterado por PATCH",
          "host" not in client.patch(f"/api/servers/{filial_id}", json={"host": "sequestrado"},
                                     headers=h(tokens["admin"])).json()
          or client.get("/api/servers", headers=h(tokens["admin"])).json()[0]["host"] != "sequestrado",
          True)

    print("\n[10] Migracao aditiva sobre banco pre-Fase 4")
    check_true("banco legado migrado sem perda", _testa_migracao_legada())

    print("\n" + "=" * 70)
    if _falhas:
        print(f"{len(_falhas)} FALHA(S): {_falhas}")
    else:
        print("TODOS OS TESTES PASSARAM")
    print("=" * 70)
    return 1 if _falhas else 0


def _testa_migracao_legada():
    """
    Monta um banco no formato ANTERIOR a Fase 4 (printers sem
    print_server_id, sem tabela print_servers), roda a migracao e confere
    que: nada foi perdido, cada host virou um registro e a FK foi ligada.
    """
    from sqlalchemy import create_engine as sa_create_engine, text
    from sqlmodel import SQLModel

    legado = _TMP / "legado.db"
    if legado.exists():
        legado.unlink()

    con = sqlite3.connect(legado)
    con.executescript(
        """
        CREATE TABLE printers (
            id INTEGER PRIMARY KEY,
            server VARCHAR,
            name VARCHAR,
            ip VARCHAR,
            port_name VARCHAR,
            driver_name VARCHAR,
            model VARCHAR,
            printer_type VARCHAR,
            department VARCHAR,
            active BOOLEAN,
            last_seen_at DATETIME,
            created_at DATETIME,
            updated_at DATETIME
        );
        INSERT INTO printers (server, name, ip, port_name, driver_name, model,
                              printer_type, department, active, last_seen_at,
                              created_at, updated_at)
        VALUES
          ('srv-a', 'IMP_A1', '10.0.0.1', 'P1', 'D', 'M', 'A4', 'TI', 1, NULL,
           '2020-01-01 00:00:00', '2020-01-01 00:00:00'),
          ('srv-a', 'IMP_A2', '10.0.0.2', 'P2', 'D', 'M', 'A4', 'TI', 1, NULL,
           '2020-01-01 00:00:00', '2020-01-01 00:00:00'),
          ('srv-b', 'IMP_B1', '10.0.1.1', 'P3', 'D', 'M', 'A4', 'RH', 1, NULL,
           '2020-01-01 00:00:00', '2020-01-01 00:00:00'),
          ('',      'MANUAL', '10.0.9.9', '',   '',  'M', NULL,  '',   1, NULL,
           '2020-01-01 00:00:00', '2020-01-01 00:00:00');
        """
    )
    con.commit()
    con.close()

    import app.database as db

    engine_original = db.engine
    db.engine = sa_create_engine(
        f"sqlite:///{legado.as_posix()}", connect_args={"check_same_thread": False}
    )
    try:
        # `print_servers` e criada pelo create_all; a migracao cuida do resto.
        SQLModel.metadata.tables["print_servers"].create(bind=db.engine, checkfirst=True)
        db._migrate_print_servers()
        db._migrate_print_servers()  # idempotencia
        with db.engine.connect() as conn:
            impressoras = list(
                conn.execute(text("SELECT name, server, print_server_id FROM printers ORDER BY id"))
            )
            servidores = list(conn.execute(text("SELECT host FROM print_servers ORDER BY host")))
    finally:
        db.engine.dispose()
        db.engine = engine_original

    print(f"       servidores registrados: {[s[0] for s in servidores]}")
    print(f"       impressoras: {impressoras}")

    por_host = {h for (h,) in servidores}
    ligacao = {nome: (server, fk) for nome, server, fk in impressoras}

    return (
        len(impressoras) == 4                                  # nada perdido
        and {"srv-a", "srv-b", "srv-padrao"} <= por_host        # hosts + o do .env
        and ligacao["IMP_A1"][1] is not None
        and ligacao["IMP_A1"][1] == ligacao["IMP_A2"][1]        # mesmo servidor, mesma FK
        and ligacao["IMP_B1"][1] != ligacao["IMP_A1"][1]        # servidores diferentes
        and ligacao["MANUAL"][1] is None                        # server='' fica sem FK
    )


if __name__ == "__main__":
    import shutil
    import sys

    try:
        codigo = main()
    finally:
        shutil.rmtree(_TMP, ignore_errors=True)
    sys.exit(codigo)
