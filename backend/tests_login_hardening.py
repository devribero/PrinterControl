"""
Fase 10 - endurecimento do login.

Cobre as duas falhas levantadas na auditoria em `POST /api/auth/login`:

    1. tentativas ILIMITADAS -> forca bruta na velocidade da rede;
    2. oraculo de tempo      -> "e-mail nao existe" respondia visivelmente
                                mais rapido que "senha errada", revelando
                                quais contas existem.

Como as demais suites desde a Fase 1, NAO precisa do backend rodando.

    .\\venv\\Scripts\\python.exe tests_login_hardening.py
"""
import os
import statistics
import tempfile
import time
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="printercontrol-login-"))
os.environ["DATABASE_URL"] = f"sqlite:///{(_TMP / 'login_test.db').as_posix()}"
os.environ["ENVIRONMENT"] = "development"
os.environ["PRINT_SERVER_MODE"] = "mock"

from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import Session  # noqa: E402

from app.database import create_db_and_tables, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models.user import Role, User  # noqa: E402
from app.routes.auth import login_limiter  # noqa: E402
from app.services.auth import hash_password  # noqa: E402
from app.services.rate_limit import RateLimiter  # noqa: E402

_falhas = []

EMAIL = "operador@teste.com"
SENHA = "senha-correta-123"
INEXISTENTE = "nao-existe-de-jeito-nenhum@teste.com"


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

with Session(engine) as s:
    s.add(User(email=EMAIL, name="Operador", password_hash=hash_password(SENHA), role=Role.OPERATOR))
    s.commit()


def tentar(email, senha):
    """Tentativa com a contagem limpa — isola o caso do limite de tentativas."""
    login_limiter.reset()
    return client.post("/api/auth/login", json={"email": email, "password": senha})


# ---------------------------------------------------------------------------
print("\n[1] O limitador em si (janela deslizante)")
# Testado isolado do HTTP: aqui interessa a contagem, nao a rota.
lim = RateLimiter(max_tentativas=3, janela_segundos=60)

check("primeira tentativa passa", lim.verificar(["a"]).bloqueado, False)
for _ in range(3):
    lim.registrar_falha(["a"])
check("bloqueia na 4a tentativa", lim.verificar(["a"]).bloqueado, True)
check_true("informa quanto esperar", lim.verificar(["a"]).retry_after > 0, str(lim.verificar(["a"]).retry_after))
check("outra chave nao e afetada", lim.verificar(["b"]).bloqueado, False)

lim.limpar(["a"])
check("login bem-sucedido zera a contagem", lim.verificar(["a"]).bloqueado, False)

# Janela deslizante: passado o tempo, o acesso volta SOZINHO. Bloqueio
# permanente viraria negacao de servico contra o dono legitimo da conta.
curta = RateLimiter(max_tentativas=2, janela_segundos=1)
curta.registrar_falha(["c"])
curta.registrar_falha(["c"])
check("bloqueado dentro da janela", curta.verificar(["c"]).bloqueado, True)
time.sleep(1.1)
check("liberado sozinho apos a janela", curta.verificar(["c"]).bloqueado, False)

# Duas chaves: basta UMA estourar para bloquear (IP ou e-mail).
duas = RateLimiter(max_tentativas=2, janela_segundos=60)
duas.registrar_falha(["ip:1.2.3.4"])
duas.registrar_falha(["ip:1.2.3.4"])
check(
    "estouro em uma chave bloqueia o par",
    duas.verificar(["ip:1.2.3.4", "email:outro@x.com"]).bloqueado,
    True,
)


# ---------------------------------------------------------------------------
print("\n[2] A rota de login corta a forca bruta")
login_limiter.reset()

vistos = []
for _ in range(login_limiter.max_tentativas + 3):
    r = client.post("/api/auth/login", json={"email": EMAIL, "password": "chute-errado"})
    vistos.append(r.status_code)

check_true(
    "as primeiras tentativas respondem 401",
    vistos[: login_limiter.max_tentativas] == [401] * login_limiter.max_tentativas,
    str(vistos),
)
check_true(
    "as seguintes respondem 429",
    all(c == 429 for c in vistos[login_limiter.max_tentativas:]),
    str(vistos),
)

r = client.post("/api/auth/login", json={"email": EMAIL, "password": "chute-errado"})
check_true("resposta 429 traz Retry-After", "retry-after" in {k.lower() for k in r.headers}, str(dict(r.headers)))
check_true("mensagem diz para tentar mais tarde", "tentativas" in r.text.lower(), r.text[:90])

# O bloqueio vale ate para a senha CERTA: senao bastaria continuar tentando
# ate acertar, e o limite nao teria efeito nenhum.
r = client.post("/api/auth/login", json={"email": EMAIL, "password": SENHA})
check("senha correta durante o bloqueio tambem e 429", r.status_code, 429)

login_limiter.reset()
check("apos a janela, a senha correta entra", tentar(EMAIL, SENHA).status_code, 200)


print("\n[3] Login bem-sucedido no meio nao acumula bloqueio")
login_limiter.reset()
for _ in range(login_limiter.max_tentativas - 1):
    client.post("/api/auth/login", json={"email": EMAIL, "password": "errado"})
check(
    "acerto apos alguns erros",
    client.post("/api/auth/login", json={"email": EMAIL, "password": SENHA}).status_code,
    200,
)
# Se o acerto nao tivesse limpado a contagem, a proxima falha ja bloquearia.
check(
    "contagem foi zerada pelo acerto",
    client.post("/api/auth/login", json={"email": EMAIL, "password": "errado"}).status_code,
    401,
)


print("\n[4] Conta inexistente e senha errada sao indistinguiveis")
r_inexistente = tentar(INEXISTENTE, "qualquer-coisa")
r_senha_errada = tentar(EMAIL, "senha-errada")

check("mesmo status", r_inexistente.status_code, r_senha_errada.status_code)
check("mesmo corpo", r_inexistente.json(), r_senha_errada.json())
check_true(
    "corpo nao revela qual dos dois falhou",
    "existe" not in r_inexistente.text.lower() and "cadastr" not in r_inexistente.text.lower(),
    r_inexistente.text[:90],
)


print("\n[5] O tempo de resposta tambem nao revela (oraculo de tempo)")
# ANTES da correcao: e-mail inexistente pulava o argon2 e respondia em
# microssegundos, enquanto a senha errada pagava dezenas de milissegundos.
# A diferenca era visivel de fora e entregava a lista de contas validas.
RODADAS = 7


def medir(email, senha):
    amostras = []
    for _ in range(RODADAS):
        inicio = time.perf_counter()
        tentar(email, senha)
        amostras.append(time.perf_counter() - inicio)
    return statistics.median(amostras)


t_inexistente = medir(INEXISTENTE, "qualquer-coisa")
t_senha_errada = medir(EMAIL, "senha-errada")

print(f"       mediana e-mail inexistente: {t_inexistente * 1000:.1f} ms")
print(f"       mediana senha errada:       {t_senha_errada * 1000:.1f} ms")

# Ambos precisam pagar o hash. Se o e-mail inexistente pulasse o argon2, a
# razao seria de uma ordem de grandeza; exigir menos de 3x deixa folga para
# o ruido de uma maquina compartilhada sem deixar passar o oraculo antigo.
razao = max(t_inexistente, t_senha_errada) / max(min(t_inexistente, t_senha_errada), 1e-9)
check_true("tempos na mesma ordem de grandeza (< 3x)", razao < 3, f"razao={razao:.2f}x")
check_true(
    "e-mail inexistente tambem paga o custo do hash (> 5 ms)",
    t_inexistente > 0.005,
    f"{t_inexistente * 1000:.1f} ms",
)


print("\n[6] X-Forwarded-For so e respeitado quando configurado")
from app import config as config_module  # noqa: E402
from app.routes.auth import _identificar_origem  # noqa: E402


class _Req:
    """Request minimo: so o que _identificar_origem le."""

    def __init__(self, headers, host="10.0.0.1"):
        self.headers = headers
        self.client = type("C", (), {"host": host})()


anterior = config_module.settings.trust_proxy_headers
try:
    config_module.settings.trust_proxy_headers = False
    check(
        "sem proxy confiavel, o cabecalho forjado e ignorado",
        _identificar_origem(_Req({"x-forwarded-for": "1.2.3.4"})),
        "10.0.0.1",
    )

    config_module.settings.trust_proxy_headers = True
    check(
        "com proxy confiavel, usa o primeiro da cadeia",
        _identificar_origem(_Req({"x-forwarded-for": "1.2.3.4, 10.0.0.9"})),
        "1.2.3.4",
    )
    check("cabecalho ausente cai no IP da conexao", _identificar_origem(_Req({})), "10.0.0.1")
finally:
    config_module.settings.trust_proxy_headers = anterior

login_limiter.reset()

print("\n" + "=" * 70)
if _falhas:
    print(f"FALHAS: {_falhas}")
    raise SystemExit(1)
print("TODOS OS TESTES PASSARAM")
print("=" * 70)
