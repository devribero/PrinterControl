"""
Etapa 3 - camada de Print Server.

Valida o modo mock (sempre executavel, sem Windows/dominio) e, quando
PRINT_SERVER_MODE=real no ambiente, faz uma tentativa best-effort contra o
servidor de verdade (pulada com aviso se PowerShell/rede nao estiverem
disponiveis - nao e uma falha do teste).

Executar:  .\\venv\\Scripts\\python.exe tests_print_server.py
"""
import os

os.environ.setdefault("PRINT_SERVER_MODE", "mock")

from app.config import settings  # noqa: E402
from app.services.print_server import (  # noqa: E402
    DiscoveredPrinter,
    PrintServerError,
    _escapar_powershell,
    _real_discover,
    discover_printers,
    validar_host,
)

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


print("--- 1. modo mock: formato e conteudo ---")
settings.print_server_mode = "mock"
result = discover_printers()

check_true("retorna lista nao vazia", len(result) > 0, f"{len(result)} impressoras")
check_true("todos sao DiscoveredPrinter", all(isinstance(p, DiscoveredPrinter) for p in result))
check_true(
    "todos os campos preenchidos (name/server/port_name/ip/driver_name)",
    all(p.name and p.server and p.port_name and p.ip and p.driver_name for p in result),
)

print("\n--- 2. mesmo formato do modo real (mesmos campos) ---")
sample = result[0]
check_true(
    "campos = name, server, port_name, ip, driver_name",
    set(sample.__dataclass_fields__) == {"name", "server", "port_name", "ip", "driver_name"},
)

print("\n--- 3. impressoras compartilhando IP (necessario p/ agrupamento) ---")
from collections import Counter  # noqa: E402

ip_counts = Counter(p.ip for p in result)
shared = {ip: n for ip, n in ip_counts.items() if n > 1}
check_true("existe pelo menos um IP com 2+ impressoras", len(shared) > 0, str(shared))

print("\n--- 4. drivers cobrem as regras de Obter-Modelo (Etapa 4) ---")
drivers = " | ".join(p.driver_name for p in result)
for termo in ["P 502", "M3040", "M6530", "TT042", "Honeywell"]:
    check_true(f"driver contendo '{termo}' presente", termo in drivers)

print("\n--- 5. porta nao numerica (impressora local, sem IP de rede) ---")
check_true(
    "existe port_name nao numerico usado como ip (ex.: USB001)",
    any(not p.ip[:1].isdigit() for p in result),
)

print("\n--- 6. modo invalido leva a erro explicito ---")
settings.print_server_mode = "algo_invalido"
try:
    discover_printers()
    check_true("deveria levantar PrintServerError", False)
except PrintServerError:
    check_true("PrintServerError levantado corretamente", True)
finally:
    settings.print_server_mode = "mock"

print("\n--- 7. modo real (best-effort, nao bloqueia o resultado do teste) ---")
if os.environ.get("PRINT_SERVER_MODE") == "real":
    settings.print_server_mode = "real"
    try:
        real_result = discover_printers()
        print(f"[OK ] modo real respondeu: {len(real_result)} impressoras")
    except PrintServerError as exc:
        print(f"[SKIP] modo real indisponivel neste ambiente: {exc}")
    settings.print_server_mode = "mock"
else:
    print("[SKIP] PRINT_SERVER_MODE=real nao definido no ambiente - pulando (normal fora do dominio)")

print("\n--- 8. host malicioso e recusado ANTES de chegar ao PowerShell ---")
# O host e interpolado em `Get-Printer -ComputerName '<host>'`. Cada entrada
# abaixo fecha a aspa simples, encadeia um comando, ou usa um caractere que o
# shell interpreta. Nenhuma pode chegar ao subprocess.
BARRA = chr(92)
HOSTS_MALICIOSOS = [
    f"elgjunprt'; Remove-Item C:{BARRA} -Recurse -Force; '",
    f"elgjunprt' ; Get-Content C:{BARRA}Windows{BARRA}win.ini ; '",
    "'; calc.exe; '",
    "elgjunprt`; whoami",
    f"elgjunprt | Out-File C:{BARRA}evil.txt",
    "elgjunprt & whoami",
    "elgjunprt$(whoami)",
    "elgjunprt" + chr(10) + "whoami",
    "elgjunprt; shutdown /s",
    "elgjunprt with space",
    "",
    "   ",
    "-elgjunprt",       # rotulo nao pode comecar com hifen
    "elgjunprt-",       # nem terminar
    "elg..junprt",      # rotulo vazio no meio
    "a" * 254,          # acima do limite de 253 caracteres
]

for host in HOSTS_MALICIOSOS:
    rotulo = repr(host)[:48]
    try:
        validar_host(host)
        check_true(f"host recusado: {rotulo}", False, "ACEITO - injecao possivel")
    except PrintServerError:
        check_true(f"host recusado: {rotulo}", True)

# Se alguem afrouxar a regex, o subprocess ainda nao pode ser alcancado:
# _real_discover valida ANTES de montar qualquer comando. Este teste prova
# que a chamada morre na validacao, e nao dentro do PowerShell.
try:
    _real_discover("elgjunprt'; calc.exe; '", timeout=1)
    check_true("_real_discover recusa host malicioso", False, "nao levantou")
except PrintServerError as exc:
    check_true(
        "_real_discover recusa host malicioso antes do subprocess",
        "invalido" in str(exc).lower(),
        str(exc)[:70],
    )

print("\n--- 9. hosts legitimos continuam aceitos ---")
HOSTS_VALIDOS = [
    ("elgjunprt", "elgjunprt"),
    ("ELGJUNPRT", "ELGJUNPRT"),
    ("elgjunprt.elgin.local", "elgjunprt.elgin.local"),
    ("srv-print-01", "srv-print-01"),
    ("10.150.6.10", "10.150.6.10"),
    ("  elgjunprt  ", "elgjunprt"),            # espaco em volta e aparado
    ("elgjunprt.elgin.local.", "elgjunprt.elgin.local."),  # FQDN com ponto final
]
for entrada, esperado in HOSTS_VALIDOS:
    try:
        check(f"host valido {entrada!r}", validar_host(entrada), esperado)
    except PrintServerError as exc:
        check_true(f"host valido {entrada!r}", False, f"recusado: {exc}")

print("\n--- 10. escape de aspas (2a camada, redundante por escolha) ---")
check("aspa simples duplicada", _escapar_powershell("a'b"), "a''b")
check("sem aspas fica igual", _escapar_powershell("elgjunprt"), "elgjunprt")

print("\nRESULTADO:", "TODOS OS TESTES PASSARAM" if not failures else f"FALHAS: {failures}")
raise SystemExit(1 if failures else 0)
