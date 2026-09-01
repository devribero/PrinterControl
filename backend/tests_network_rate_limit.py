"""
Fase 16 - limite de taxa em acoes de rede (discover/sync/coleta), alem do
login. Ver dependencies.py (rate_limited_action) e config.py
(NETWORK_ACTION_MAX_ATTEMPTS/WINDOW).

Executar:  .\\venv\\Scripts\\python.exe tests_network_rate_limit.py
"""
import os
import tempfile

DB = os.path.join(tempfile.gettempdir(), "test_network_rate_limit.db")
if os.path.exists(DB):
    os.remove(DB)
os.environ["DATABASE_URL"] = f"sqlite:///{DB}"
os.environ["NETWORK_ACTION_MAX_ATTEMPTS"] = "3"
os.environ["NETWORK_ACTION_WINDOW_SECONDS"] = "60"

from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import Session  # noqa: E402

import app.dependencies as deps  # noqa: E402
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
    admin1 = User(email="ratelimit.admin1@example.com", password_hash=hash_password("x"),
                  name="Admin 1", role=Role.ADMIN.value)
    admin2 = User(email="ratelimit.admin2@example.com", password_hash=hash_password("x"),
                  name="Admin 2", role=Role.ADMIN.value)
    s.add(admin1)
    s.add(admin2)
    s.commit()

TOKEN1 = create_access_token({"sub": "ratelimit.admin1@example.com"})
TOKEN2 = create_access_token({"sub": "ratelimit.admin2@example.com"})
H1 = {"Authorization": f"Bearer {TOKEN1}"}
H2 = {"Authorization": f"Bearer {TOKEN2}"}
client = TestClient(app)

print("--- 1. 3 chamadas passam (limite configurado pro teste = 3), a 4a bloqueia ---")
# discover(): mode 'mock' por padrao das settings de teste, sem PRINT_SERVER
# real configurado — o que importa aqui e o codigo de status ANTES do corpo
# da rota rodar (o rate limit e a primeira coisa checada).
statuses = [client.post("/api/servers/discover", headers=H1).status_code for _ in range(4)]
check("as 3 primeiras passam do rate limit (nao sao 429)", [s != 429 for s in statuses[:3]], [True, True, True])
check("a 4a e bloqueada com 429", statuses[3], 429)

print("\n--- 2. Retry-After presente na resposta 429 ---")
resp = client.post("/api/servers/discover", headers=H1)
check("status 429", resp.status_code, 429)
check("cabecalho Retry-After presente", "Retry-After" in resp.headers, True)

print("\n--- 3. outro usuario tem orcamento PROPRIO (nao compartilha com admin1) ---")
resp2 = client.post("/api/servers/discover", headers=H2)
check("admin2 nao bloqueado pelo limite do admin1", resp2.status_code != 429, True)

print("\n--- 4. acoes diferentes tem orcamento PROPRIO (discover != sync) ---")
resp_sync = client.post("/api/servers/sync", headers=H1)
check("admin1 no limite de 'discover' ainda pode chamar 'sync'", resp_sync.status_code != 429, True)

deps._network_action_limiter.reset()

print(f"\nBanco de teste: {DB}")
print("RESULTADO:", "TODOS OS TESTES PASSARAM" if not failures else f"FALHAS: {failures}")
raise SystemExit(1 if failures else 0)
