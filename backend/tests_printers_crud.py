"""
Etapa 12 - CRUD de impressoras contra o servidor rodando.

Usa o banco REAL, entao cria apenas uma impressora temporaria e a remove ao
final. Nenhuma das 73 e alterada de forma permanente: a edicao de teste e
feita numa impressora existente e revertida no fim.

Pre-requisito: backend rodando. Passe a URL como argumento se nao for :8000.
    .\\venv\\Scripts\\python.exe tests_printers_crud.py http://127.0.0.1:8000
"""
import json
import os
import sys
import urllib.error
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
# Credenciais pelo ambiente (Fase 10): a senha das contas semeadas deixou de
# ser fixa — seed.py agora gera uma aleatoria ou usa SEED_ADMIN_PASSWORD.
#     set TEST_ADMIN_PASSWORD=<senha>   (ou SEED_ADMIN_PASSWORD)
EMAIL = os.environ.get("TEST_ADMIN_EMAIL", "mateus.vicentino@elgin.com.br")
PASSWORD = os.environ.get("TEST_ADMIN_PASSWORD") or os.environ.get("SEED_ADMIN_PASSWORD", "")
TEST_IP = "10.255.255.254"  # fora das faixas usadas pelas 73

failures = []


def check(label, got, expected):
    ok = got == expected
    print(f"[{'OK ' if ok else 'FAIL'}] {label}: {got}" + ("" if ok else f" (esperado {expected})"))
    if not ok:
        failures.append(label)


def check_true(label, cond, detail=""):
    print(f"[{'OK ' if cond else 'FAIL'}] {label}" + (f": {detail}" if detail else ""))
    if not cond:
        failures.append(label)


def request(method, path, body=None, token=None):
    """Devolve (status, payload)."""
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{BASE}{path}", data=data, method=method)
    if data:
        req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read() or "null")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or "null")


print("--- 0. login ---")
if not PASSWORD:
    raise SystemExit(
        "Defina TEST_ADMIN_PASSWORD (ou SEED_ADMIN_PASSWORD) com a senha da conta "
        f"{EMAIL}. Ela e mostrada uma unica vez por seed.py; para gerar outra: "
        "python seed.py --resetar-senhas"
    )

status, payload = request("POST", "/api/auth/login", {"email": EMAIL, "password": PASSWORD})
check("login", status, 200)
token = payload["access_token"]

print("\n--- 1. leitura (exige JWT desde a Fase 2) ---")
check("GET /api/printers sem token -> 401", request("GET", "/api/printers")[0], 401)
check("GET /api/alerts sem token -> 401", request("GET", "/api/alerts")[0], 401)

status, printers = request("GET", "/api/printers", token=token)
check("GET /api/printers", status, 200)
check("73 impressoras", len(printers), 73)

first_id = printers[0]["id"]
status, one = request("GET", f"/api/printers/{first_id}", token=token)
check("GET /api/printers/{id}", status, 200)
check_true("campos presentes", all(k in one for k in ("ip", "name", "model", "department")))
check("id inexistente -> 404", request("GET", "/api/printers/999999", token=token)[0], 404)

print("\n--- 2. escrita exige JWT ---")
novo = {"ip": TEST_IP, "name": "TESTE_TEMP", "model": "Modelo Teste", "department": "TI"}
check("POST sem token -> 401", request("POST", "/api/printers", novo)[0], 401)
check("PATCH sem token -> 401", request("PATCH", f"/api/printers/{first_id}", {"name": "x"})[0], 401)
check("POST com token invalido -> 401", request("POST", "/api/printers", novo, "abc.def.ghi")[0], 401)

print("\n--- 3. validacoes ---")
casos = [
    ("IP invalido", {**novo, "ip": "999.1.1.1"}),
    ("IP vazio", {**novo, "ip": ""}),
    ("nome vazio", {**novo, "name": "   "}),
    ("modelo vazio", {**novo, "model": ""}),
    ("departamento vazio", {**novo, "department": ""}),
]
for label, body in casos:
    status, resp = request("POST", "/api/printers", body, token)
    check(f"{label} -> 422", status, 422)

print("\n--- 4. criar impressora temporaria ---")
status, criada = request("POST", "/api/printers", novo, token)
check("POST -> 200", status, 200)
temp_id = criada["id"]
check("ip gravado", criada["ip"], TEST_IP)
check("nome gravado", criada["name"], "TESTE_TEMP")

status, lista = request("GET", "/api/printers", token=token)
check("agora sao 74", len(lista), 74)
status, com_status = request("GET", "/api/printers/with-status", token=token)
nova = next(p for p in com_status if p["id"] == temp_id)
check("aparece em with-status", nova["name"], "TESTE_TEMP")
check("sem leitura -> last_seen nulo", nova["last_seen"], None)
check("sem PrinterReading artificial", request("GET", f"/api/printers/{temp_id}/readings", token=token)[1], [])

print("\n--- 5. identidade e (server, name), nao IP (Etapa 4) ---")
status, outra = request("POST", "/api/printers", {**novo, "name": "OUTRA_COM_MESMO_IP"}, token)
check("POST com MESMO IP mas nome diferente -> 200 (permitido)", status, 200)
check("ip realmente repetido", outra["ip"], TEST_IP)
outra_id = outra["id"]

status, resp = request("POST", "/api/printers", novo, token)
check("POST com nome repetido -> 400", status, 400)
check_true("mensagem clara", "TESTE_TEMP" in resp["detail"], resp["detail"])

print("\n--- 6. editar ---")
status, editada = request("PATCH", f"/api/printers/{temp_id}", {"name": "TESTE_EDITADO", "department": "Financeiro"}, token)
check("PATCH -> 200", status, 200)
check("nome atualizado", editada["name"], "TESTE_EDITADO")
check("departamento atualizado", editada["department"], "Financeiro")
check("persistiu", request("GET", f"/api/printers/{temp_id}", token=token)[1]["name"], "TESTE_EDITADO")

status, resp = request("PATCH", f"/api/printers/{temp_id}", {"ip": printers[0]["ip"]}, token)
check("PATCH para IP de outra impressora -> 200 (IP nao e mais unico)", status, 200)

status, resp = request("PATCH", f"/api/printers/{outra_id}", {"name": "TESTE_EDITADO"}, token)
check("PATCH para nome ja usado (mesmo server) -> 400", status, 400)
check("PATCH id inexistente -> 404", request("PATCH", "/api/printers/999999", {"name": "x"}, token)[0], 404)

print("\n--- 7. leituras historicas intactas ---")
com_leituras = [p for p in com_status if p["last_seen"]]
alvo = com_leituras[0]
antes = request("GET", f"/api/printers/{alvo['id']}/readings?limit=500", token=token)[1]
request("PATCH", f"/api/printers/{alvo['id']}", {"department": "TEMP_TESTE"}, token)
depois = request("GET", f"/api/printers/{alvo['id']}/readings?limit=500", token=token)[1]
check("quantidade de leituras inalterada", len(depois), len(antes))
check_true("conteudo das leituras inalterado", depois == antes, f"{len(antes)} leituras conferidas")
# reverte a edicao da impressora real
request("PATCH", f"/api/printers/{alvo['id']}", {"department": alvo["department"]}, token)
check("departamento restaurado", request("GET", f"/api/printers/{alvo['id']}", token=token)[1]["department"], alvo["department"])

print("\n--- 7b. escrita de leituras e coleta exigem JWT (Etapa 13) ---")
leitura = {"status": "online", "page_count": 123, "toner_k": 50}
check("POST readings sem token -> 401", request("POST", f"/api/printers/{temp_id}/readings", leitura)[0], 401)
check("POST readings com token -> 200", request("POST", f"/api/printers/{temp_id}/readings", leitura, token)[0], 200)

mock_body = {"mode": "mock", "scenario": "online_mono"}
check("coleta mock sem token -> 401", request("POST", f"/api/collect/printers/{temp_id}", mock_body)[0], 401)
check("coleta fleet sem token -> 401", request("POST", "/api/collect/fleet")[0], 401)
check("token invalido -> 401", request("POST", f"/api/collect/printers/{temp_id}", mock_body, "nao.e.um.jwt")[0], 401)

status, resp = request("POST", f"/api/collect/printers/{temp_id}", mock_body, token)
# Fase 1: /api/collect/scenarios expoe a configuracao de mock e passou a
# exigir admin — a conta usada por este teste tem esse papel.
check("scenarios sem token -> 401", request("GET", "/api/collect/scenarios")[0], 401)
mock_ligado = request("GET", "/api/collect/scenarios", token=token)[1]["mock_enabled"]
if mock_ligado:
    check("coleta mock com token e ALLOW_MOCK_COLLECT=true -> 200", status, 200)
else:
    check("coleta mock bloqueada com ALLOW_MOCK_COLLECT=false -> 403", status, 403)
    check_true("mensagem explica o bloqueio", "ALLOW_MOCK_COLLECT" in resp["detail"], resp["detail"])

# Token expirado e recusado igual a um invalido.
from datetime import timedelta  # noqa: E402
from app.services.auth import create_access_token  # noqa: E402

expirado = create_access_token({"sub": EMAIL}, expires_delta=timedelta(seconds=-60))
check("token expirado -> 401", request("POST", "/api/printers", novo, expirado)[0], 401)

print("\n--- 8. limpeza ---")
# Nao ha DELETE na API (ver pendencias); a temporaria e removida direto no banco.
import os  # noqa: E402
import sqlite3  # noqa: E402

db = os.path.join(os.path.dirname(os.path.abspath(__file__)), "printer_control.db")
conn = sqlite3.connect(db)
for pid in (temp_id, outra_id):
    conn.execute("delete from alerts where printer_id = ?", (pid,))
    conn.execute("delete from printer_readings where printer_id = ?", (pid,))
    conn.execute("delete from printers where id = ?", (pid,))
conn.commit()
conn.close()
check("temporaria removida", request("GET", f"/api/printers/{temp_id}", token=token)[0], 404)
check("voltou a 73", len(request("GET", "/api/printers", token=token)[1]), 73)

print("\nRESULTADO:", "TODOS OS TESTES PASSARAM" if not failures else f"FALHAS: {failures}")
raise SystemExit(1 if failures else 0)
