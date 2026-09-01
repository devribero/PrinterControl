"""
Fase 10 - Preparacao para producao corporativa.

Cobre o que protege a exposicao externa (Cloudflare Tunnel, proxima fase):

    CORS      -> producao recusa subir com lista vazia, "*", localhost ou http
    logs      -> nenhum segredo chega ao arquivo, nem vindo de terceiros
    /health   -> diagnostico util para monitor, sem nada sensivel

Como as demais suites desde a Fase 1, NAO precisa do backend rodando.

    .\\venv\\Scripts\\python.exe tests_production.py
"""
import logging
import os
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="printercontrol-prod-"))
os.environ["DATABASE_URL"] = f"sqlite:///{(_TMP / 'prod_test.db').as_posix()}"
os.environ["ENVIRONMENT"] = "development"

from fastapi.testclient import TestClient  # noqa: E402

from app import config as config_module  # noqa: E402
from app.config import Settings  # noqa: E402
from app.database import create_db_and_tables  # noqa: E402
from app.logging_config import RedactSecretsFilter  # noqa: E402
from app.main import app  # noqa: E402

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


def producao(**overrides):
    base = dict(
        environment="production",
        secret_key=SECRET_VALIDO,
        print_server_mode="real",
        allow_mock_collect=False,
        cors_origins=["https://painel.exemplo.com"],
        _env_file=None,
    )
    base.update(overrides)
    return Settings(**base)


# ---------------------------------------------------------------------------
#  CORS
# ---------------------------------------------------------------------------
print("\n[1] Producao recusa CORS inseguro")
casos_recusa = [
    ("lista vazia", []),
    ("curinga '*'", ["*"]),
    ("curinga junto de origem valida", ["https://painel.exemplo.com", "*"]),
    ("localhost", ["http://localhost:3000"]),
    ("127.0.0.1", ["https://painel.exemplo.com", "http://127.0.0.1:3000"]),
    ("http sem TLS", ["http://painel.exemplo.com"]),
]
for nome, origens in casos_recusa:
    try:
        producao(cors_origins=origens)
        check_true(f"recusa {nome}", False, "subiu sem erro")
    except ValueError:
        check_true(f"recusa {nome}", True)

print("\n[2] Producao aceita origens HTTPS explicitas")
try:
    s = producao(cors_origins=["https://painel.vercel.app", "https://elginprint.devribero.online"])
    check("duas origens https aceitas", len(s.cors_origins), 2)
except Exception as exc:  # noqa: BLE001
    check_true("duas origens https aceitas", False, str(exc))

print("\n[3] Fora de producao o default local continua valendo")
dev = Settings(environment="development", _env_file=None)
check_true("development mantem localhost", any("localhost" in o for o in dev.cors_origins))

print("\n[4] CORS_ORIGINS aceita virgulas, e nao so JSON")
# O jeito natural de escrever no .env nao pode ser o jeito que quebra.
s = Settings(environment="development", cors_origins="https://a.com, https://b.com", _env_file=None)
check("string com virgulas vira lista", s.cors_origins, ["https://a.com", "https://b.com"])
s = Settings(environment="development", cors_origins='["https://c.com"]', _env_file=None)
check("JSON continua funcionando", s.cors_origins, ["https://c.com"])

print("\n[4b] O caminho REAL: CORS_ORIGINS vindo de variavel de ambiente")
# Este bloco existe por causa de um bug encontrado ao subir o processo de
# verdade. Os checks acima passam valores como ARGUMENTO, e nesse caminho o
# pydantic-settings nao tenta decodificar JSON. Vindo do AMBIENTE ele tenta —
# e `CORS_ORIGINS=https://x.com` explodia antes de chegar ao validador.
# Testar so por argumento dava falsa confianca justamente na forma que a
# documentacao manda usar.
import subprocess  # noqa: E402

BACKEND = Path(__file__).resolve().parent
PY = BACKEND / "venv" / "Scripts" / "python.exe"


def subir_com_ambiente(**variaveis) -> tuple[bool, str]:
    """Sobe um processo separado e diz se a configuracao foi aceita."""
    ambiente = dict(os.environ)
    ambiente.update({k: str(v) for k, v in variaveis.items()})
    ambiente["DATABASE_URL"] = os.environ["DATABASE_URL"]
    proc = subprocess.run(
        [str(PY), "-c", "from app.config import settings; print(settings.cors_origins)"],
        capture_output=True, text=True, cwd=str(BACKEND), env=ambiente,
    )
    return proc.returncode == 0, (proc.stdout + proc.stderr)


ok, saida = subir_com_ambiente(ENVIRONMENT="development", CORS_ORIGINS="https://x.com,https://y.com")
check_true("virgulas via env NAO explodem", ok, saida.strip()[-120:])
check_true("as duas origens chegaram", "https://x.com" in saida and "https://y.com" in saida, saida.strip()[:80])

ok, saida = subir_com_ambiente(ENVIRONMENT="development", CORS_ORIGINS='["https://z.com"]')
check_true("JSON via env continua funcionando", ok and "https://z.com" in saida, saida.strip()[-120:])

print("\n[4c] Fail-fast de producao vale no processo real, nao so na classe")
producao_env = dict(
    ENVIRONMENT="production", SECRET_KEY=SECRET_VALIDO,
    PRINT_SERVER_MODE="real", ALLOW_MOCK_COLLECT="false",
    CORS_ORIGINS="https://painel.vercel.app",
)
ok, saida = subir_com_ambiente(**producao_env)
check_true("producao coerente sobe", ok, saida.strip()[-120:])

for nome, mudanca, marca in [
    ("PRINT_SERVER_MODE=mock", {"PRINT_SERVER_MODE": "mock"}, "PRINT_SERVER_MODE"),
    ("ALLOW_MOCK_COLLECT=true", {"ALLOW_MOCK_COLLECT": "true"}, "ALLOW_MOCK_COLLECT"),
    ("CORS_ORIGINS vazio", {"CORS_ORIGINS": ""}, "CORS_ORIGINS"),
    ("CORS_ORIGINS com localhost", {"CORS_ORIGINS": "http://localhost:3000"}, "CORS_ORIGINS"),
    ("SECRET_KEY default", {"SECRET_KEY": "dev-secret-key-change-in-production"}, "SECRET_KEY"),
]:
    ok, saida = subir_com_ambiente(**{**producao_env, **mudanca})
    check_true(f"recusa {nome}", not ok and marca in saida, saida.strip()[-90:] if ok else "")


# ---------------------------------------------------------------------------
#  Redacao de segredos no log
# ---------------------------------------------------------------------------
print("\n[5] Segredos nao chegam ao log")
redator = RedactSecretsFilter()


def redigir(msg, *args):
    registro = logging.LogRecord("qualquer", logging.INFO, __file__, 1, msg, args, None)
    redator.filter(registro)
    return registro.getMessage()


sensiveis = [
    ("secret_key", "conectando com secret_key=super-secreta-123", "super-secreta-123"),
    ("password", "login {'email': 'a@b.com', 'password': 'MinhaSenha1'}", "MinhaSenha1"),
    ("senha", "senha=Trocar@123", "Trocar@123"),
    ("token", "token: eyJhbGciOiJIUzI1NiJ9.payload.assinatura", "eyJhbGciOiJIUzI1NiJ9.payload.assinatura"),
    ("Bearer", "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9abcdef", "eyJhbGciOiJIUzI1NiJ9abcdef"),
    ("snmp_community", "consultando snmp_community=publico-interno", "publico-interno"),
    ("webhook_url", "webhook_url=https://outlook.office.com/webhook/AAA-BBB", "AAA-BBB"),
    ("password_hash", "user password_hash=$argon2id$v=19$m=65536", "argon2id"),
    # Fase 16 (LGPD): dado pessoal no log de bloqueio de rate-limit do login.
    ("conta (e-mail)", "Login bloqueado | conta=pedro.ribeiro@elgin.com.br | retry_after=60s", "pedro.ribeiro@elgin.com.br"),
    ("origem (IP)", "Login bloqueado | conta=x | origem=192.168.1.42 | retry_after=60s", "192.168.1.42"),
]
for nome, mensagem, segredo in sensiveis:
    saida = redigir(mensagem)
    check_true(f"{nome} redigido", segredo not in saida, saida[:70])

print("\n[5b] Mensagem real de bloqueio de login: e-mail E IP redigidos juntos")
saida = redigir(
    "Login bloqueado por excesso de tentativas | conta=%s | origem=%s | retry_after=%ss",
    "pedro.ribeiro@elgin.com.br", "10.0.0.5", 60,
)
check_true("e-mail ausente", "pedro.ribeiro@elgin.com.br" not in saida, saida)
check_true("IP ausente", "10.0.0.5" not in saida, saida)
check_true("retry_after (nao e PII) continua legivel", "60s" in saida, saida)

print("\n[6] A redacao alcanca args de terceiros (uvicorn, sqlalchemy)")
# Bibliotecas logam com %s; se a redacao rodasse antes da formatacao, o
# segredo passaria batido. Este e o caso que justifica filtrar no handler.
saida = redigir("query %s", "SELECT * FROM users WHERE token=abc123def456")
check_true("segredo vindo em args e redigido", "abc123def456" not in saida, saida[:70])

print("\n[7] A redacao nao destroi mensagem normal")
check("mensagem sem segredo intacta", redigir("Ciclo concluido | frota=%s", 73), "Ciclo concluido | frota=73")
check_true("nao redige a palavra sozinha", "impressora" in redigir("token da impressora ausente"))


# ---------------------------------------------------------------------------
#  /health
# ---------------------------------------------------------------------------
print("\n[8] /health serve para monitorar sem vazar configuracao")
create_db_and_tables()
client = TestClient(app)

r = client.get("/health")
check("publico, sem token", r.status_code, 200)
corpo = r.json()

for campo in ("status", "version", "environment", "uptime_seconds", "database", "scheduler"):
    check_true(f"traz '{campo}'", campo in corpo, str(corpo)[:80])

check("banco acessivel -> status ok", corpo["status"], "ok")
check("database ok", corpo["database"], "ok")
check_true("uptime e numero >= 0", isinstance(corpo["uptime_seconds"], (int, float)) and corpo["uptime_seconds"] >= 0)
check_true("scheduler traz running", "running" in corpo["scheduler"])

print("\n[9] /health nao expoe segredo nem topologia interna")
texto = r.text.lower()
proibidos = ["secret", "password", "sqlite:", "c:\\\\", "cors", "webhook", "database_url", ".db", "token"]
vazando = [p for p in proibidos if p in texto]
check("nenhum termo sensivel no corpo", vazando, [])
check_true("SECRET_KEY nao aparece", SECRET_VALIDO not in r.text)
check_true("host do print server nao aparece", config_module.settings.print_server_host not in r.text)

print("\n" + "=" * 70)
if _falhas:
    print(f"FALHAS: {_falhas}")
    raise SystemExit(1)
print("TODOS OS TESTES PASSARAM")
print("=" * 70)
