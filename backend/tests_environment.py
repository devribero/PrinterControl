"""
Fase 9 - Mock e Demo Seguros.

Cobre as DUAS camadas que protegem o risco critico levantado no levantamento
desta fase: um Print Server em modo simulado sincronizando contra o banco de
producao, o que desativa toda impressora real ausente da frota ficticia.

    camada 1 (boot)       -> config.py recusa subir com config global simulada
    camada 2 (requisicao) -> rotas respondem 409 a operacoes simuladas

Como as demais suites desde a Fase 1, NAO precisa do backend rodando.

    .\\venv\\Scripts\\python.exe tests_environment.py
"""
import os
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="printercontrol-ambiente-"))
os.environ["DATABASE_URL"] = f"sqlite:///{(_TMP / 'ambiente_test.db').as_posix()}"
os.environ["ENVIRONMENT"] = "development"
os.environ["PRINT_SERVER_MODE"] = "mock"

from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import Session, select  # noqa: E402

from app import config as config_module  # noqa: E402
from app.config import ENVIRONMENTS, Settings  # noqa: E402
from app.database import create_db_and_tables, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models.print_server import PrintServer  # noqa: E402
from app.models.printer import Printer  # noqa: E402
from app.models.user import Role, User  # noqa: E402
from app.services.auth import hash_password  # noqa: E402

_falhas = []
SECRET_VALIDO = "x" * 48


def check(nome, obtido, esperado):
    ok = obtido == esperado
    print(f"  [{'OK  ' if ok else 'FALHA'}] {nome}: {obtido!r}" + ("" if ok else f" (esperado {esperado!r})"))
    if not ok:
        _falhas.append(nome)


def check_true(nome, cond, detalhe=""):
    print(f"  [{'OK  ' if cond else 'FALHA'}] {nome}" + (f": {detalhe}" if detalhe else ""))
    if not cond:
        _falhas.append(nome)


def settings_de_producao(**overrides):
    """Settings de producao valida, sobrescrevendo so o que o teste investiga."""
    base = dict(
        environment="production",
        secret_key=SECRET_VALIDO,
        print_server_mode="real",
        allow_mock_collect=False,
        # cors_origins explicito desde a Fase 10: producao passou a recusar o
        # default local. Sem isto, todo caso aqui seria recusado pelo motivo
        # errado — e o positivo falharia. O CORS tem suite propria em
        # tests_production.py.
        cors_origins=["https://painel.exemplo.com"],
        _env_file=None,  # ignora backend/.env: o teste define o cenario inteiro
    )
    base.update(overrides)
    return Settings(**base)


# ---------------------------------------------------------------------------
#  CAMADA 1 - fail-fast de boot
# ---------------------------------------------------------------------------
print("\n[1] ENVIRONMENT so aceita os tres valores conhecidos")
check("valores reconhecidos", set(ENVIRONMENTS), {"development", "demo", "production"})

for valor in ("producao", "prod", "PRODUCTION_", "staging", ""):
    try:
        Settings(environment=valor, _env_file=None)
        check_true(f"ENVIRONMENT={valor!r} recusado", False, "subiu sem erro")
    except Exception:
        check_true(f"ENVIRONMENT={valor!r} recusado", True)

# Normalizacao: caixa e espaco nao podem virar um ambiente desconhecido.
check("'  Production ' normaliza", settings_de_producao(environment="  Production ").environment, "production")
check("is_production apos normalizar", settings_de_producao(environment="PRODUCTION").is_production, True)
check("is_demo em demo", Settings(environment="DEMO", _env_file=None).is_demo, True)
check("is_demo em production", settings_de_producao().is_demo, False)

print("\n[2] Producao recusa subir com Print Server simulado")
try:
    settings_de_producao(print_server_mode="mock")
    check_true("PRINT_SERVER_MODE=mock + production -> recusa", False, "subiu sem erro")
except ValueError as exc:
    check_true("PRINT_SERVER_MODE=mock + production -> recusa", True)
    check_true("erro explica o risco do sync", "sync" in str(exc).lower(), str(exc)[:90])

print("\n[3] Producao recusa subir com coleta simulada habilitada")
try:
    settings_de_producao(allow_mock_collect=True)
    check_true("ALLOW_MOCK_COLLECT=true + production -> recusa", False, "subiu sem erro")
except ValueError as exc:
    check_true("ALLOW_MOCK_COLLECT=true + production -> recusa", True)
    check_true("erro cita a variavel", "ALLOW_MOCK_COLLECT" in str(exc), str(exc)[:90])

print("\n[4] Producao coerente sobe normalmente")
try:
    check("producao valida sobe", settings_de_producao().is_production, True)
except Exception as exc:  # noqa: BLE001
    check_true("producao valida sobe", False, str(exc))

print("\n[5] development e demo continuam livres para simular")
for ambiente_livre in ("development", "demo"):
    try:
        s = Settings(environment=ambiente_livre, print_server_mode="mock", allow_mock_collect=True, _env_file=None)
        check_true(f"{ambiente_livre} aceita simulacao", s.print_server_mode == "mock")
    except Exception as exc:  # noqa: BLE001
        check_true(f"{ambiente_livre} aceita simulacao", False, str(exc))

# O secret de dev nao pode passar em producao - regra da Fase 1, revalidada
# aqui porque o validador de ambiente novo roda antes dela.
print("\n[6] A validacao de SECRET_KEY nao foi enfraquecida")
try:
    settings_de_producao(secret_key="dev-secret-key-change-in-production")
    check_true("secret de dev em producao -> recusa", False, "subiu sem erro")
except ValueError:
    check_true("secret de dev em producao -> recusa", True)


# ---------------------------------------------------------------------------
#  CAMADA 2 - 409 por requisicao
# ---------------------------------------------------------------------------
create_db_and_tables()
client = TestClient(app)

with Session(engine) as s:
    s.add(User(email="admin@teste.com", name="Admin", password_hash=hash_password("senha12345"), role=Role.ADMIN))
    s.add(PrintServer(host="srv-mock", name="Simulado", mode="mock"))
    s.add(PrintServer(host="srv-real", name="Real", mode="real"))
    s.commit()
    servidor_mock = s.exec(select(PrintServer).where(PrintServer.host == "srv-mock")).first().id
    servidor_real = s.exec(select(PrintServer).where(PrintServer.host == "srv-real")).first().id

token = client.post("/api/auth/login", json={"email": "admin@teste.com", "password": "senha12345"}).json()["access_token"]
H = {"Authorization": f"Bearer {token}"}


class ambiente:
    """Troca settings.environment durante o bloco - as rotas leem em runtime."""

    def __init__(self, valor):
        self.valor = valor

    def __enter__(self):
        self.anterior = config_module.settings.environment
        config_module.settings.environment = self.valor

    def __exit__(self, *a):
        config_module.settings.environment = self.anterior


print("\n[7] Em producao, sincronizar servidor simulado -> 409")
with ambiente("production"):
    r = client.post(f"/api/servers/{servidor_mock}/sync", headers=H)
    check("sync de servidor mock", r.status_code, 409)
    check_true("mensagem explica a desativacao da frota real",
               "ficticia" in r.text.lower() or "inativa" in r.text.lower(), r.text[:110])

    r = client.post(f"/api/servers/{servidor_mock}/discover", headers=H)
    check("discover de servidor mock", r.status_code, 409)

print("\n[8] Em producao, cadastrar/editar servidor simulado -> 409")
with ambiente("production"):
    r = client.post("/api/servers", headers=H, json={"host": "novo-srv", "mode": "mock"})
    check("criar servidor mock", r.status_code, 409)

    # O default do campo e "mock": omitir tambem precisa ser barrado.
    r = client.post("/api/servers", headers=H, json={"host": "novo-srv-2"})
    check("criar servidor omitindo mode (default mock)", r.status_code, 409)

    r = client.patch(f"/api/servers/{servidor_real}", headers=H, json={"mode": "mock"})
    check("mudar servidor real para mock", r.status_code, 409)

print("\n[9] Em producao, coleta simulada -> 409")
with ambiente("production"):
    r = client.post("/api/collect/printers/1", headers=H, json={"mode": "mock", "scenario": "online_mono"})
    check("coleta simulada de impressora", r.status_code, 409)
    r = client.post("/api/collect/fleet", headers=H)
    check("coleta simulada de frota", r.status_code, 409)

print("\n[10] O que e REAL continua funcionando em producao")
with ambiente("production"):
    r = client.patch(f"/api/servers/{servidor_real}", headers=H, json={"name": "Renomeado"})
    check("editar servidor real (sem tocar no modo)", r.status_code, 200)
    r = client.get("/api/servers", headers=H)
    check("listar servidores", r.status_code, 200)

print("\n[11] Fora de producao nada disso e bloqueado")
with ambiente("demo"):
    r = client.post("/api/servers", headers=H, json={"host": "demo-srv", "mode": "mock"})
    check_true("demo permite cadastrar servidor mock", r.status_code == 201, f"status={r.status_code}")
    r = client.post(f"/api/servers/{servidor_mock}/discover", headers=H)
    check_true("demo permite discover simulado", r.status_code != 409, f"status={r.status_code}")

print("\n[12] /health identifica o ambiente sem exigir token e sem vazar segredo")
r = client.get("/health")
check("health publico", r.status_code, 200)
corpo = r.json()
check_true("traz 'environment'", "environment" in corpo, str(corpo))
check_true("traz is_demo e is_production", "is_demo" in corpo and "is_production" in corpo)
proibidos = ("secret", "password", "database_url", "token", "webhook")
vazou = [k for k in corpo if any(p in k.lower() for p in proibidos)]
check("nenhuma chave sensivel no corpo", vazou, [])
check_true("nenhum valor parece um secret", all(SECRET_VALIDO not in str(v) for v in corpo.values()))

with ambiente("demo"):
    check("health reflete demo", client.get("/health").json()["is_demo"], True)

print("\n[13] POST /api/printers/{id}/readings: a porta dos fundos da Fase 9")
# Ate aqui esta rota era o unico caminho de ESCRITA de leitura que nao
# passava por guarda nenhuma: /api/collect recusa simulacao em producao, mas
# quem tivesse token de operator gravava a mesma leitura ficticia por aqui.
with Session(engine) as s:
    s.add(Printer(server="srv-real", ip="10.150.6.99", name="Impressora Teste", model="Teste", department="TI"))
    s.commit()
    impressora_id = s.exec(select(Printer).where(Printer.ip == "10.150.6.99")).first().id

LEITURA_VALIDA = {"status": "online", "page_count": 1000, "toner_k": 50}

with ambiente("production"):
    r = client.post(f"/api/printers/{impressora_id}/readings", headers=H, json=LEITURA_VALIDA)
    check("gravacao manual de leitura em producao", r.status_code, 409)
    check_true(
        "mensagem aponta a coleta como origem legitima",
        "collect" in r.text.lower(),
        r.text[:120],
    )

with ambiente("development"):
    r = client.post(f"/api/printers/{impressora_id}/readings", headers=H, json=LEITURA_VALIDA)
    check("fora de producao a gravacao manual continua disponivel", r.status_code, 200)

print("\n[14] Campos de PrinterReadingCreate sao validados (422)")
# Sem isto, um unico registro invalido corrompe as tres coisas que consomem
# leitura: o badge do painel, o relatorio mensal (que subtrai contadores) e
# o motor de alertas (que compara o toner com os limiares).
PAYLOADS_INVALIDOS = [
    ("status inventado", {"status": "bombando", "page_count": 10}),
    ("status vazio", {"status": "", "page_count": 10}),
    ("status de severidade de alerta", {"status": "critical", "page_count": 10}),
    ("page_count negativo", {"status": "online", "page_count": -1}),
    ("page_count muito negativo", {"status": "online", "page_count": -999999}),
    ("toner_k acima de 100", {"status": "online", "page_count": 10, "toner_k": 101}),
    ("toner_k absurdo", {"status": "online", "page_count": 10, "toner_k": 5000}),
    ("toner_k negativo", {"status": "online", "page_count": 10, "toner_k": -1}),
    ("toner_c fora da faixa", {"status": "online", "page_count": 10, "toner_c": 200}),
    ("toner_m fora da faixa", {"status": "online", "page_count": 10, "toner_m": -5}),
    ("toner_y fora da faixa", {"status": "online", "page_count": 10, "toner_y": 101}),
]

with ambiente("development"):
    for rotulo, payload in PAYLOADS_INVALIDOS:
        r = client.post(f"/api/printers/{impressora_id}/readings", headers=H, json=payload)
        check(f"recusa {rotulo}", r.status_code, 422)

    # Os limites da faixa sao VALIDOS — a validacao nao pode recusar leitura real.
    for rotulo, payload in [
        ("toner em 0 (vazio de verdade)", {"status": "online", "page_count": 0, "toner_k": 0}),
        ("toner em 100 (cheio)", {"status": "online", "page_count": 1, "toner_k": 100}),
        ("status atencao", {"status": "atencao", "page_count": 2, "toner_k": 8}),
        ("status offline", {"status": "offline", "page_count": 0}),
        ("caixa alta normalizada", {"status": "ONLINE", "page_count": 3}),
        ("sem toner algum (mono)", {"status": "online", "page_count": 4}),
    ]:
        r = client.post(f"/api/printers/{impressora_id}/readings", headers=H, json=payload)
        check(f"aceita {rotulo}", r.status_code, 200)

    check(
        "status e normalizado para minusculas",
        client.post(
            f"/api/printers/{impressora_id}/readings",
            headers=H,
            json={"status": "Atencao", "page_count": 5},
        ).json()["status"],
        "atencao",
    )

print("\n[15] Teto de paginacao nas rotas de leitura")
with ambiente("development"):
    for rota in (
        f"/api/printers/{impressora_id}/readings?limit=100000",
        "/api/printers?limit=100000",
        "/api/printers/with-status?limit=100000",
        "/api/alerts?limit=100000",
        "/api/printers/monthly-report?months=999",
    ):
        check(f"limite absurdo recusado: {rota.split('?')[1]} em {rota.split('?')[0]}",
              client.get(rota, headers=H).status_code, 422)

    for rota in (
        f"/api/printers/{impressora_id}/readings?limit=500",
        "/api/printers?limit=500&offset=0",
        "/api/printers/with-status?limit=500",
        "/api/alerts?limit=500&offset=0",
        "/api/printers/monthly-report?months=12",
    ):
        check(f"limite no teto aceito: {rota}", client.get(rota, headers=H).status_code, 200)

print("\n" + "=" * 70)
if _falhas:
    print(f"FALHAS: {_falhas}")
    raise SystemExit(1)
print("TODOS OS TESTES PASSARAM")
print("=" * 70)
