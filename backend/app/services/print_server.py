"""
Camada de Print Server (Etapa 3).

Reproduz a descoberta de impressoras do Main.ps1:

    Get-Printer     -ComputerName $servidor   -> Nome, DriverName, PortName
    Get-PrinterPort -ComputerName $servidor   -> PortName, PrinterHostAddress

O Print Server e a FONTE das impressoras — o banco e cache/historico, nao
origem. Este modulo so descobre; sincronizar com o banco e a Etapa 4.

Dois modos, controlados por settings.print_server_mode:
    "mock" -> dados simulados, no MESMO formato do caminho real, incluindo
              impressoras que compartilham IP (necessario para o agrupamento
              da Etapa 8). Nao toca rede nem Windows.
    "real" -> PowerShell via subprocess, fiel ao Main.ps1.
"""
import json
import logging
import subprocess
from dataclasses import dataclass

from app.config import settings

logger = logging.getLogger("printercontrol.print_server")


@dataclass
class DiscoveredPrinter:
    """Uma linha do que Get-Printer + Get-PrinterPort devolveriam, combinadas."""

    name: str
    server: str
    port_name: str
    ip: str  # PrinterHostAddress (via PortName) ou o proprio PortName, como no Main.ps1
    driver_name: str


class PrintServerError(Exception):
    """RPC ao Print Server falhou ou saida do PowerShell nao pode ser interpretada."""


# ─────────────────────────────────────────────────────────────────────────
#  MOCK — mesmo formato do real, para desenvolvimento fora do dominio
# ─────────────────────────────────────────────────────────────────────────

def _mock_discover(server: str) -> list[DiscoveredPrinter]:
    """
    Frota simulada. Inclui de proposito:
      - drivers que casam as regras de Obter-Modelo (Etapa 4): Ricoh P 502,
        Kyocera M3040, Kyocera M6530 (color), Elgin TT042, Honeywell.
      - DUAS impressoras no mesmo IP (10.150.6.20), para validar o
        agrupamento por IP (Etapa 8) desde ja.
      - uma porta nao numerica (USB001), como impressoras locais reais.
    """
    rows = [
        ("VLO_Diretoria", "LPT_VLO_DIR", "10.150.6.10", "Ricoh P 502 PCL 6"),
        ("VLO_Financeiro", "LPT_VLO_FIN", "10.150.6.11", "Kyocera M3040idn KX"),
        ("VLO_Marketing", "LPT_VLO_MKT", "10.150.6.20", "Kyocera M6530cdn XPS"),
        ("VLO_Marketing_Cor", "LPT_VLO_MKT2", "10.150.6.20", "Kyocera M6530cdn XPS"),
        ("MC_Expedicao_Etiqueta", "LPT_MC_EXP", "10.150.7.30", "Elgin TT042 Class Driver"),
        ("MC_Recepcao_Portatil", "LPT_MC_REC", "10.150.7.31", "Honeywell RP4f"),
        ("JUN_Operacao_Local", "USB001", "USB001", "HP LaserJet PCL 6"),
    ]
    return [
        DiscoveredPrinter(name=name, server=server, port_name=port, ip=ip, driver_name=driver)
        for name, port, ip, driver in rows
    ]


# ─────────────────────────────────────────────────────────────────────────
#  REAL — PowerShell via subprocess, mesma chamada do Main.ps1
# ─────────────────────────────────────────────────────────────────────────

def _run_powershell_json(command: str, timeout: int) -> list[dict]:
    """
    Executa um comando PowerShell que termina em `ConvertTo-Json` e devolve
    sempre uma lista de dict — o `ConvertTo-Json` do Windows devolve um
    objeto solto (nao lista) quando ha exatamente 1 resultado, entao
    normalizamos aqui.
    """
    try:
        proc = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        raise PrintServerError("powershell.exe nao encontrado neste host") from exc
    except subprocess.TimeoutExpired as exc:
        raise PrintServerError(f"PowerShell nao respondeu em {timeout}s") from exc

    if proc.returncode != 0:
        raise PrintServerError(f"PowerShell falhou: {proc.stderr.strip() or proc.stdout.strip()}")

    raw = proc.stdout.strip()
    if not raw:
        return []

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise PrintServerError(f"Saida do PowerShell nao e JSON valido: {exc}") from exc

    return data if isinstance(data, list) else [data]


def _real_discover(server: str, timeout: int) -> list[DiscoveredPrinter]:
    """
    Equivalente exato de Get-ImpressorasEmpresa + o inicio de
    Process-ImpressorasList no Main.ps1 (so a parte de descoberta —
    ping/SNMP ficam para a Etapa 5).
    """
    printers_cmd = (
        f"Get-Printer -ComputerName '{server}' -ErrorAction Stop | "
        "Select-Object Name, DriverName, PortName | ConvertTo-Json -Compress"
    )
    ports_cmd = (
        f"Get-PrinterPort -ComputerName '{server}' -ErrorAction Stop | "
        "Select-Object Name, PrinterHostAddress | ConvertTo-Json -Compress"
    )

    printers = _run_powershell_json(printers_cmd, timeout)
    ports = _run_powershell_json(ports_cmd, timeout)

    # portMap[PortName] = PrinterHostAddress — mesma logica do Main.ps1.
    port_map = {
        p["Name"]: p.get("PrinterHostAddress") or ""
        for p in ports
        if p.get("Name")
    }

    discovered = []
    for p in printers:
        name = p.get("Name")
        port_name = p.get("PortName") or ""
        if not name:
            continue
        ip = port_map.get(port_name) or port_name  # fallback identico ao Main.ps1
        discovered.append(
            DiscoveredPrinter(
                name=name,
                server=server,
                port_name=port_name,
                ip=ip,
                driver_name=p.get("DriverName") or "",
            )
        )
    return discovered


# ─────────────────────────────────────────────────────────────────────────
#  Interface publica
# ─────────────────────────────────────────────────────────────────────────

def discover_printers(server: str | None = None) -> list[DiscoveredPrinter]:
    """
    Descobre as impressoras publicadas no Print Server configurado.

    Levanta PrintServerError em modo "real" quando o RPC falha — ao
    contrario do Main.ps1, que cai silenciosamente no mock embutido; aqui a
    falha e explicita e quem decide o fallback e o chamador (rota), para
    nao mascarar um problema real de rede/dominio.
    """
    server = server or settings.print_server_host
    mode = settings.print_server_mode

    if mode == "mock":
        logger.info("Descoberta em modo mock | server=%s", server)
        return _mock_discover(server)

    if mode == "real":
        logger.info("Descoberta em modo real | server=%s", server)
        return _real_discover(server, settings.print_server_timeout_seconds)

    raise PrintServerError(f"PRINT_SERVER_MODE invalido: {mode!r} (use 'mock' ou 'real')")
