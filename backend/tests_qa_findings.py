"""
Regressao dos achados da auditoria QA (08/09/2026).

Um teste por achado CORRIGIDO, escrito a partir da reproducao que confirmou
cada um. Existe para que nenhum deles volte em silencio: todos passaram a
vida inteira do projeto ate aqui sem quebrar suite nenhuma, justamente porque
ninguem os exercitava.

Nao precisa do backend rodando: TestClient contra um SQLite temporario,
criado do zero e apagado no final. O banco real nunca e tocado.

    .\\venv\\Scripts\\python.exe tests_qa_findings.py
"""
import os
import tempfile
from pathlib import Path

# Precisa vir ANTES de importar app.config: as Settings leem o ambiente no import.
_TMP_DB = Path(tempfile.mkdtemp(prefix="printercontrol-qa-")) / "qa_test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP_DB.as_posix()}"
os.environ["ALLOW_MOCK_COLLECT"] = "true"
os.environ["ENVIRONMENT"] = "development"

from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import Session, select  # noqa: E402

from app.config import Settings  # noqa: E402
from app.database import create_db_and_tables, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models.alert import Alert  # noqa: E402
from app.models.printer import Printer, PrinterReading  # noqa: E402
from app.models.user import Role, User  # noqa: E402
from app.services import printer_collector as pc  # noqa: E402
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
EMAIL = "qa@teste-findings.com"


def semear():
    create_db_and_tables()
    with Session(engine) as s:
        s.add(
            User(
                email=EMAIL,
                password_hash=hash_password(SENHA),
                name="QA",
                role=Role.ADMIN.value,
                is_active=True,
                must_change_password=False,
            )
        )
        s.add(
            Printer(
                server="srv-qa",
                name="P1",
                ip="10.0.0.1",
                model="Modelo QA",
                department="TI",
                port_name="",
                driver_name="",
                active=True,
            )
        )
        s.commit()


def entrar(client):
    r = client.post("/api/auth/login", json={"email": EMAIL, "password": SENHA})
    return r.json()["access_token"]


def h(token):
    return {"Authorization": f"Bearer {token}"}


def main():
    semear()
    # raise_server_exceptions=False para que um 500 chegue como 500, e nao
    # como excecao — sem isso um erro nao tratado abortaria a suite em vez de
    # ser reportado como falha do teste.
    client = TestClient(app, raise_server_exceptions=False)
    token = entrar(client)

    print("\n[QA-01] Banco novo nasce com FK integra")
    from sqlalchemy import text

    with engine.connect() as conn:
        violacoes = len(list(conn.execute(text("PRAGMA foreign_key_check"))))
        alvos = {
            t: {row[2] for row in conn.execute(text(f"PRAGMA foreign_key_list({t})"))}
            for t in ("printer_readings", "printer_monthly", "alerts", "toner_history")
        }
    check("PRAGMA foreign_key_check sem violacoes", violacoes, 0)
    for tabela, destino in alvos.items():
        check_true(f"{tabela} referencia printers", destino == {"printers"}, str(destino))
    check_true(
        "nenhuma tabela *_old sobrou",
        not [
            r
            for r in engine.connect().execute(
                text("SELECT name FROM sqlite_master WHERE name LIKE '%_old'")
            )
        ],
    )

    print("\n[QA-04] Troca de senha e reativacao encerram as sessoes antigas")
    r = client.post(
        "/api/auth/change-password",
        json={"current_password": SENHA, "new_password": "senha-nova-98765"},
        headers=h(token),
    )
    check("change-password -> 200 (era 204)", r.status_code, 200)
    novo_token = r.json().get("access_token")
    check_true("resposta traz token novo", isinstance(novo_token, str) and len(novo_token) > 20)
    check("token ANTERIOR a troca -> 401", client.get("/api/auth/me", headers=h(token)).status_code, 401)
    check("token devolvido pela troca -> 200", client.get("/api/auth/me", headers=h(novo_token)).status_code, 200)

    with Session(engine) as s:
        u = s.exec(select(User)).first()
        u.is_active = False
        u.token_version += 1  # o mesmo que PATCH /api/users/{id} faz
        s.add(u)
        s.commit()
    check("conta desativada -> 403", client.get("/api/auth/me", headers=h(novo_token)).status_code, 403)
    with Session(engine) as s:
        u = s.exec(select(User)).first()
        u.is_active = True
        s.add(u)
        s.commit()
    # ERA AQUI O BUG: o token de antes da desativacao voltava a funcionar
    # junto com a conta, e a orientacao "desative e reative para encerrar
    # sessoes suspeitas" nao encerrava nada.
    check(
        "apos reativar, token anterior -> 401",
        client.get("/api/auth/me", headers=h(novo_token)).status_code,
        401,
    )
    r = client.post("/api/auth/login", json={"email": EMAIL, "password": "senha-nova-98765"})
    check("login com a senha nova -> 200", r.status_code, 200)
    token = r.json()["access_token"]
    check("token do login novo funciona -> 200", client.get("/api/auth/me", headers=h(token)).status_code, 200)

    print("\n[QA-05] Falha ao avaliar alertas nao deixa leitura gravada")
    def explodir(*_a, **_k):
        raise RuntimeError("falha simulada na avaliacao de alertas")

    original = pc.evaluate_reading
    pc.evaluate_reading = explodir
    try:
        with Session(engine) as s:
            antes = len(s.exec(select(PrinterReading)).all())
            resultado = pc.PrinterCollector(mode="mock").collect_and_save(1, s)
        with Session(engine) as s:
            depois = len(s.exec(select(PrinterReading)).all())
    finally:
        pc.evaluate_reading = original
    check("coleta reporta falha", resultado.get("success"), False)
    check("nenhuma leitura ficou gravada", depois, antes)

    print("\n[QA-07] PATCH com null em campo obrigatorio")
    for campo in ("name", "model", "department", "ip"):
        check(
            f"PATCH {{{campo}: null}} -> 422 (era 500)",
            client.patch("/api/printers/1", json={campo: None}, headers=h(token)).status_code,
            422,
        )
    r = client.patch("/api/printers/1", json={"department": "Financeiro"}, headers=h(token))
    check("PATCH com valor de verdade continua funcionando", r.status_code, 200)
    check("campo omitido nao e alterado", r.json()["name"], "P1")

    print("\n[QA-08] Inteiros fora do alcance do banco")
    gigante = 10**30
    check(
        f"GET /api/printers/{gigante} -> 422 (era 500)",
        client.get(f"/api/printers/{gigante}", headers=h(token)).status_code,
        422,
    )
    check(
        "GET /api/alerts/<gigante> -> 422",
        client.get(f"/api/alerts/{gigante}", headers=h(token)).status_code,
        422,
    )
    check(
        "POST leitura com page_count 1e30 -> 422 (era 500)",
        client.post(
            "/api/printers/1/readings",
            json={"status": "online", "page_count": gigante},
            headers=h(token),
        ).status_code,
        422,
    )
    check(
        "id zero -> 422",
        client.get("/api/printers/0", headers=h(token)).status_code,
        422,
    )

    print("\n[QA-11] Leitura manual passa pela avaliacao de alertas")
    with Session(engine) as s:
        alertas_antes = len(s.exec(select(Alert)).all())
    r = client.post(
        "/api/printers/1/readings",
        json={"status": "offline", "page_count": 10, "toner_k": 1},
        headers=h(token),
    )
    check("leitura manual -> 200", r.status_code, 200)
    with Session(engine) as s:
        alertas = s.exec(select(Alert)).all()
    check_true(
        "leitura offline abriu alerta (antes nao abria nenhum)",
        len(alertas) > alertas_antes,
        f"{alertas_antes} -> {len(alertas)}",
    )
    check_true(
        "o alerta e de offline",
        any(a.alert_type == "offline" for a in alertas),
        str([a.alert_type for a in alertas]),
    )

    print("\n[QA-16] Subrecurso de impressora inexistente")
    check("GET /api/printers/999999 -> 404", client.get("/api/printers/999999", headers=h(token)).status_code, 404)
    check(
        "GET /api/printers/999999/readings -> 404 (era 200 com [])",
        client.get("/api/printers/999999/readings", headers=h(token)).status_code,
        404,
    )
    check(
        "impressora existente sem filtro continua 200",
        client.get("/api/printers/1/readings", headers=h(token)).status_code,
        200,
    )

    print("\n[QA-10] X-Forwarded-For so vale vindo de um proxy conhecido")
    s = Settings(trust_proxy_headers=True, trusted_proxy_ips="127.0.0.1, 10.0.0.0/8")
    check_true("proxy na lista e confiavel", s.proxy_confiavel("127.0.0.1"))
    check_true("endereco dentro do CIDR e confiavel", s.proxy_confiavel("10.9.9.9"))
    check_true("endereco de fora NAO e confiavel", not s.proxy_confiavel("8.8.8.8"))
    check_true("endereco malformado NAO e confiavel", not s.proxy_confiavel("nao-e-ip"))
    vazio = Settings(trust_proxy_headers=True)
    check_true(
        "lista vazia mantem o comportamento anterior (compatibilidade)",
        vazio.proxy_confiavel("8.8.8.8"),
    )

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
