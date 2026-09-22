r"""
Descoberta quando Get-PrinterPort falha (21/09/2026).

Em 10.40.0.10 o Get-Printer respondeu e o Get-PrinterPort estourou o
timeout; a descoberta inteira caia. Agora ela segue, derivando o IP do nome
da porta. Nenhum Print Server real e tocado: o PowerShell e simulado.

    .\venv\Scripts\python.exe tests_print_server_ports.py
"""
import os
import tempfile
from unittest.mock import patch

os.environ["DATABASE_URL"] = f"sqlite:///{os.path.join(tempfile.gettempdir(), 'test_ps_ports.db')}"
os.environ["ENVIRONMENT"] = "development"

from app.services import print_server  # noqa: E402
from app.services.print_server import PrintServerError, discover_printers  # noqa: E402

failures = []


def check(label, got, expected):
    ok = got == expected
    print(f"[{'OK ' if ok else 'FAIL'}] {label}: {got!r}" + ("" if ok else f" (esperado {expected!r})"))
    if not ok:
        failures.append(label)


FILAS = [
    {"Name": "FILA_A", "DriverName": "Kyocera X KX", "PortName": "IP_10.40.1.10", "ShareName": "FILA_A"},
    {"Name": "FILA_B", "DriverName": "Ricoh Y PCL 6", "PortName": "10.40.1.11", "ShareName": "FILA_B"},
    {"Name": "FILA_C", "DriverName": "Generic / Text Only", "PortName": "WSD-3f2a", "ShareName": "FILA_C"},
    {"Name": "FILA_D", "DriverName": "HP Z PCL 6", "PortName": "MC_SEALAUT", "ShareName": "FILA_D"},
]
COMANDOS = []


def powershell(portas_falham):
    def run(cmd, timeout, server=None, operation=None, **_):
        COMANDOS.append((operation, cmd))
        if operation == "Get-Printer":
            return FILAS
        if portas_falham:
            raise PrintServerError("timeout", "rpc_timeout_or_unavailable")
        return [{"Name": "MC_SEALAUT", "PrinterHostAddress": "10.40.1.50"}]
    return run


print("--- 1. Get-PrinterPort falha: descoberta segue, IP sai do nome da porta ---")
with patch.object(print_server, "_run_powershell_json", side_effect=powershell(True)):
    filas = {d.name: d for d in discover_printers("10.40.0.10", mode="real")}
check("as 4 filas vieram", sorted(filas), ["FILA_A", "FILA_B", "FILA_C", "FILA_D"])
check("porta de nome livre sem resposta fica com o nome", filas["FILA_D"].ip, "MC_SEALAUT")
check("IP_10.40.1.10 -> 10.40.1.10", filas["FILA_A"].ip, "10.40.1.10")
check("10.40.1.11 -> 10.40.1.11", filas["FILA_B"].ip, "10.40.1.11")
check("porta WSD fica com o nome (sem IP para adivinhar)", filas["FILA_C"].ip, "WSD-3f2a")

print("\n--- 2. Get-PrinterPort so para portas de nome livre (22/09/2026) ---")
COMANDOS.clear()
with patch.object(print_server, "_run_powershell_json", side_effect=powershell(False)):
    filas = {d.name: d for d in discover_printers("10.40.0.10", mode="real")}
cmd_portas = next((c for op, c in COMANDOS if op == "Get-PrinterPort"), "")
check("porta de nome livre resolvida pelo Get-PrinterPort", filas["FILA_D"].ip, "10.40.1.50")
check("IP no nome continua valendo", filas["FILA_A"].ip, "10.40.1.10")
check("so MC_SEALAUT foi perguntada",
      ("'MC_SEALAUT'" in cmd_portas, "IP_10.40.1.10" in cmd_portas, "WSD-3f2a" in cmd_portas),
      (True, False, False))

print("\n--- 2b. todas as portas com IP no nome ou sem endereco: nem consulta ---")
COMANDOS.clear()
so_ip = [f for f in FILAS if f["Name"] != "FILA_D"]


def run_so_ip(cmd, timeout, server=None, operation=None, **_):
    COMANDOS.append((operation, cmd))
    return so_ip if operation == "Get-Printer" else []


with patch.object(print_server, "_run_powershell_json", side_effect=run_so_ip):
    discover_printers("10.40.0.10", mode="real")
check("sem chamada ao Get-PrinterPort", [op for op, _ in COMANDOS], ["Get-Printer"])

print("\n--- 2c. IP ja conhecido no cadastro dispensa a consulta ---")
COMANDOS.clear()
with patch.object(print_server, "_run_powershell_json", side_effect=powershell(False)):
    filas = {d.name: d for d in discover_printers(
        "10.40.0.10", mode="real", portas_conhecidas={"MC_SEALAUT": "10.40.1.77"})}
check("usou o IP do cadastro", filas["FILA_D"].ip, "10.40.1.77")
check("sem chamada ao Get-PrinterPort", [op for op, _ in COMANDOS], ["Get-Printer"])

print("\n--- 3. Get-Printer falhando continua sendo erro ---")
def printer_falha(cmd, timeout, server=None, operation=None, **_):
    raise PrintServerError("negado", "access_denied")
with patch.object(print_server, "_run_powershell_json", side_effect=printer_falha):
    try:
        discover_printers("10.40.0.10", mode="real")
        check("levantou erro", False, True)
    except PrintServerError as exc:
        check("levantou erro categorizado", exc.category, "access_denied")

print()
if failures:
    print(f"FALHOU: {failures}")
    raise SystemExit(1)
print("Todos os testes de descoberta com portas falhando passaram.")
