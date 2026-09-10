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
import re
import subprocess
from dataclasses import dataclass

from app.config import settings

logger = logging.getLogger("printercontrol.print_server")


class PrintServerError(Exception):
    """RPC ao Print Server falhou ou saida do PowerShell nao pode ser interpretada."""


# ─────────────────────────────────────────────────────────────────────────
#  Validacao do host — o nome do servidor entra em uma linha de PowerShell
# ─────────────────────────────────────────────────────────────────────────
#
# `server` chega de fonte controlavel por um admin (PRINT_SERVER_HOST no .env
# ou o campo `host` de um PrintServer gravado por `POST /api/servers`) e e
# interpolado num comando executado por powershell.exe. Sem validacao, um host
# como
#
#     elgjunprt'; Remove-Item C:\ -Recurse -Force; '
#
# fecha a string do Get-Printer e executa o que vier depois — com os
# privilegios do servico. Nao e teorico: a rota de cadastro de servidores
# aceita texto livre.
#
# A defesa e uma allowlist, e nao uma lista de caracteres proibidos: um host
# de Print Server e sempre um hostname NetBIOS, um FQDN ou um IPv4, e todos
# tres cabem no conjunto [A-Za-z0-9.-]. Qualquer coisa fora disso e recusada
# antes de chegar ao subprocess.
#
# Regras de rotulo (RFC 1123): 1-63 caracteres, comeca e termina em
# alfanumerico, hifen permitido no meio. Ate 253 caracteres no total.
_HOSTNAME_LABEL = r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
_HOSTNAME_RE = re.compile(rf"^{_HOSTNAME_LABEL}(?:\.{_HOSTNAME_LABEL})*\.?$")
_MAX_HOSTNAME_LENGTH = 253


def validar_host(server: str) -> str:
    """
    Devolve o host se for hostname/FQDN/IPv4 valido; levanta PrintServerError
    caso contrario.

    Publica de proposito: a rota de cadastro de Print Servers pode usa-la para
    recusar o valor no momento em que ele e digitado, em vez de deixar o erro
    aparecer so na primeira sincronizacao.
    """
    if not isinstance(server, str):
        raise PrintServerError(f"Host do Print Server invalido: {server!r} (esperado texto).")

    limpo = server.strip()

    if not limpo:
        raise PrintServerError("Host do Print Server vazio.")

    if len(limpo) > _MAX_HOSTNAME_LENGTH:
        raise PrintServerError(
            f"Host do Print Server muito longo ({len(limpo)} caracteres, maximo "
            f"{_MAX_HOSTNAME_LENGTH})."
        )

    if not _HOSTNAME_RE.match(limpo):
        raise PrintServerError(
            f"Host do Print Server invalido: {server!r}. Use apenas o nome do "
            "servidor (ex.: elgjunprt), um FQDN (ex.: elgjunprt.elgin.local) ou "
            "um IPv4. Espacos, aspas, ponto-e-virgula e outros caracteres nao "
            "sao aceitos porque o nome e usado em um comando do sistema."
        )

    return limpo


def _escapar_powershell(valor: str) -> str:
    """
    Escapa aspas simples para string literal do PowerShell ('' = uma aspa).

    Redundante depois de `validar_host` — a allowlist ja exclui aspas. E de
    proposito: se um dia alguem afrouxar a regex, ou usar esta funcao com
    outro campo, a interpolacao continua nao permitindo fechar a string.
    """
    return valor.replace("'", "''")


@dataclass
class DiscoveredPrinter:
    """Uma linha do que Get-Printer + Get-PrinterPort devolveriam, combinadas."""

    name: str
    server: str
    port_name: str
    ip: str  # PrinterHostAddress (via PortName) ou o proprio PortName, como no Main.ps1
    driver_name: str


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
    # Duas camadas antes da interpolacao: a allowlist recusa o host que nao
    # for hostname/FQDN/IPv4, e o escape neutraliza aspas simples caso algo
    # passe. `server` original segue sendo usado no retorno (identidade do
    # registro); so o que entra no comando e a versao validada.
    host = validar_host(server)
    host_ps = _escapar_powershell(host)

    printers_cmd = (
        f"Get-Printer -ComputerName '{host_ps}' -ErrorAction Stop | "
        "Select-Object Name, DriverName, PortName | ConvertTo-Json -Compress"
    )
    ports_cmd = (
        f"Get-PrinterPort -ComputerName '{host_ps}' -ErrorAction Stop | "
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

def discover_printers(
    server: str | None = None, mode: str | None = None
) -> list[DiscoveredPrinter]:
    """
    Descobre as impressoras publicadas em um Print Server.

    `server` e `mode` sao opcionais e caem na configuracao global quando
    omitidos — e o comportamento que sempre existiu. A partir da Fase 4 o
    chamador pode passar o modo do PrintServer registrado, porque numa
    instalacao com varios servidores um pode estar em producao ("real") e
    outro sendo simulado ("mock").

    Levanta PrintServerError em modo "real" quando o RPC falha — ao
    contrario do Main.ps1, que cai silenciosamente no mock embutido; aqui a
    falha e explicita e quem decide o fallback e o chamador (rota), para
    nao mascarar um problema real de rede/dominio.
    """
    server = server or settings.print_server_host
    mode = mode or settings.print_server_mode

    if mode == "mock":
        logger.info("Descoberta em modo mock | server=%s", server)
        return _mock_discover(server)

    if mode == "real":
        logger.info("Descoberta em modo real | server=%s", server)
        return _real_discover(server, settings.print_server_timeout_seconds)

    raise PrintServerError(f"PRINT_SERVER_MODE invalido: {mode!r} (use 'mock' ou 'real')")
