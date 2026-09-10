"""
Camada de Print Server (Etapa 3).

Descoberta ativa em Python com transporte PowerShell inline:

    Get-Printer     -ComputerName $servidor   -> Nome, DriverName, PortName
    Get-PrinterPort -ComputerName $servidor   -> PortName, PrinterHostAddress

O Print Server e a FONTE das impressoras — o banco e cache/historico, nao
origem. Este modulo so descobre; sincronizar com o banco e a Etapa 4.

Dois modos, controlados por settings.print_server_mode:
    "mock" -> dados simulados, no MESMO formato do caminho real, incluindo
              impressoras que compartilham IP (necessario para o agrupamento
              da Etapa 8). Nao toca rede nem Windows.
    "real" -> PowerShell via subprocess, sem arquivo .ps1.
"""
import json
import logging
import re
import subprocess
import time
from uuid import uuid4
from dataclasses import dataclass

from app.config import settings

logger = logging.getLogger("printercontrol.print_server")


class PrintServerError(Exception):
    """Falha categorizada; a mensagem continua disponivel via str(exc)."""

    def __init__(self, message: str, category: str = "unknown_error", **context):
        super().__init__(message)
        self.category = category
        self.context = context

    def as_dict(self) -> dict:
        return {"detail": str(self), "category": self.category, **self.context}


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
        raise PrintServerError(f"Host do Print Server invalido: {server!r} (esperado texto).", "invalid_configuration")

    limpo = server.strip()

    if not limpo:
        raise PrintServerError("Host do Print Server vazio.", "invalid_configuration")

    if len(limpo) > _MAX_HOSTNAME_LENGTH:
        raise PrintServerError(
            f"Host do Print Server muito longo ({len(limpo)} caracteres, maximo "
            f"{_MAX_HOSTNAME_LENGTH}).", "invalid_configuration"
        )

    if not _HOSTNAME_RE.match(limpo):
        raise PrintServerError(
            f"Host do Print Server invalido: {server!r}. Use apenas o nome do "
            "servidor (ex.: elgjunprt), um FQDN (ex.: elgjunprt.elgin.local) ou "
            "um IPv4. Espacos, aspas, ponto-e-virgula e outros caracteres nao "
            "sao aceitos porque o nome e usado em um comando do sistema.", "invalid_configuration"
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

def _effective_identity() -> tuple[str | None, str | None]:
    """Identidade herdada pelo subprocess; nunca usa USERNAME como substituto."""
    try:
        result = subprocess.run(
            ["whoami.exe"], capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip(), None
        return None, "whoami_failed"
    except (OSError, subprocess.TimeoutExpired):
        return None, "whoami_unavailable"


def _error_category(evidence: dict, fallback: str) -> str:
    """Codigos primeiro; texto apenas quando a evidencia e especifica."""
    codes = set()
    for key in ("hresult", "native_code"):
        try:
            codes.add(int(evidence.get(key)) & 0xFFFF)
        except (ValueError, TypeError):
            pass
    description = " ".join(str(evidence.get(k, "")) for k in
                           ("type", "root_type", "error_id", "message")).lower()
    # CimException pode ter HResult generico, mas trazer o HRESULT Windows
    # real em FullyQualifiedErrorId (independente do idioma da mensagem).
    codes.update(int(code, 16) & 0xFFFF for code in re.findall(r"0x[0-9a-f]{8}\b", description))
    if "commandnotfoundexception" in description:
        return "cmdlet_not_found"
    if evidence.get("stage") == "dns" or codes & {11001, 11002, 11003, 11004}:
        return "dns_resolution_failed"
    if (5 in codes or "unauthorizedaccessexception" in description
            or evidence.get("native_status") == "AccessDenied"):
        return "access_denied"
    if codes & {1722, 1726, 1460, 121, 10060}:
        return "rpc_timeout_or_unavailable"
    description += " " + fallback.lower()
    if "commandnotfoundexception" in description:
        return "cmdlet_not_found"
    if any(s in description for s in ("access is denied", "access denied", "access was denied", "acesso negado")):
        return "access_denied"
    if "spooler" in description and any(s in description for s in
            ("not running", "unavailable", "not available", "indispon", "parado", "não está", "nao esta")):
        return "spooler_unavailable"
    if any(s in description for s in ("rpc server is unavailable", "servidor rpc", "timed out", "timeout")):
        return "rpc_timeout_or_unavailable"
    return "unknown_error"


def _run_powershell_json(command: str, timeout: int, *, server: str | None = None,
                         operation: str = "PowerShell", telemetry: dict | None = None) -> list[dict]:
    """Comandos inline, DNS e erro estruturado; stdout reservado ao resultado JSON."""
    context = telemetry if telemetry is not None else {}
    context.update(server=server, operation=operation, call_id=uuid4().hex)
    identity, identity_error = _effective_identity()
    context.update(identity=identity, identity_error=identity_error)
    logger.info("Print Server chamada | %s", context)
    if identity_error:
        logger.warning("Identidade indisponivel | %s", context)
    # DNS executado no mesmo processo PowerShell, sob o timeout da chamada.
    dns = ""
    if server is not None:
        host = _escapar_powershell(validar_host(server))
        dns = (f"$stage='dns'; [void][System.Net.Dns]::GetHostAddresses('{host}'); "
               "$stage='cmdlet'; ")
    wrapped = (
        "[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false); "
        "$ErrorActionPreference='Stop'; $stage='cmdlet'; try { "
        + dns + command + " } catch { "
        "$e=$_.Exception; $root=$e.GetBaseException(); "
        "$info=@{stage=$stage; type=$e.GetType().FullName; "
        "root_type=$root.GetType().FullName; native_status=[string]$root.NativeErrorCode; "
        "error_id=$_.FullyQualifiedErrorId; hresult=$root.HResult; "
        "native_code=$root.NativeErrorCode; message=$e.Message}; "
        "[Console]::Error.WriteLine('PRINT_SERVER_ERROR:' + ($info | ConvertTo-Json -Compress)); exit 1 }"
    )
    started = time.perf_counter()
    count = None
    category = None
    failure = None
    try:
        try:
            proc = subprocess.run(
                ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", wrapped],
                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout,
            )
        except FileNotFoundError as exc:
            raise PrintServerError("powershell.exe nao encontrado neste host", "powershell_not_found") from exc
        except subprocess.TimeoutExpired as exc:
            raise PrintServerError(f"PowerShell nao respondeu em {timeout}s", "rpc_timeout_or_unavailable") from exc
        except OSError as exc:
            raise PrintServerError("Nao foi possivel iniciar powershell.exe", "transport_unavailable") from exc

        if proc.returncode != 0:
            raw_error = proc.stderr.strip() or proc.stdout.strip()
            evidence = {}
            for line in raw_error.splitlines():
                if line.startswith("PRINT_SERVER_ERROR:"):
                    try:
                        parsed = json.loads(line.split(":", 1)[1])
                        if isinstance(parsed, dict):
                            evidence = parsed
                    except json.JSONDecodeError:
                        pass
            category = _error_category(evidence, raw_error)
            message = evidence.get("message") or raw_error or "erro sem detalhe"
            raise PrintServerError(f"PowerShell falhou: {message}", category,
                                   error_id=evidence.get("error_id"), hresult=evidence.get("hresult"))

        raw = proc.stdout.strip().lstrip("\ufeff")
        try:
            data = json.loads(raw) if raw else []
        except json.JSONDecodeError as exc:
            raise PrintServerError("Saida do PowerShell nao e JSON valido", "invalid_json") from exc
        # ConvertTo-Json pode emitir null, objeto unico ou array.
        rows = [] if data is None else data if isinstance(data, list) else [data]
        if not all(isinstance(row, dict) and isinstance(row.get("Name"), str)
                   and row["Name"].strip() for row in rows):
            raise PrintServerError("JSON do PowerShell tem estrutura invalida", "invalid_json")
        count = len(rows)
        return rows
    except PrintServerError as exc:
        category = exc.category
        failure = exc
        raise
    finally:
        context.update(duration_ms=round((time.perf_counter() - started) * 1000, 2),
                       count=count, category=category)
        if failure is not None:
            failure.context.update({k: v for k, v in context.items() if k != "category"})
        log = logger.error if category else logger.info
        log("Print Server resultado | %s", context)


def _real_discover(server: str, timeout: int) -> list[DiscoveredPrinter]:
    """
    Combina filas e portas do Print Server. Ping/SNMP pertencem ao
    enriquecimento posterior; nao ha dependencia de script legado.
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

    printers = _run_powershell_json(printers_cmd, timeout, server=host, operation="Get-Printer")
    ports = _run_powershell_json(ports_cmd, timeout, server=host, operation="Get-PrinterPort")

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
    mode = settings.print_server_mode if mode is None else mode

    if mode == "mock":
        if settings.environment not in {"development", "demo"}:
            raise PrintServerError("Mock permitido apenas em development/demo", "invalid_configuration")
        logger.info("Descoberta em modo mock | server=%s", server)
        return _mock_discover(server)

    if mode == "real":
        logger.info("Descoberta em modo real | server=%s", server)
        return _real_discover(server, settings.print_server_timeout_seconds)

    raise PrintServerError(f"PRINT_SERVER_MODE invalido: {mode!r} (use 'mock' ou 'real')", "invalid_configuration")


def diagnose_print_server() -> dict:
    """Consulta real minima; nao usa discovery, portas, SNMP nem banco."""
    telemetry = {}
    result = {"server": settings.print_server_host, "configured_mode": settings.print_server_mode,
              "probe_mode": "real", "identity": None, "identity_error": None,
              "category": None, "duration_ms": None, "count": None}
    try:
        host = _escapar_powershell(validar_host(settings.print_server_host))
        _run_powershell_json(
            f"Get-Printer -ComputerName '{host}' -ErrorAction Stop | "
            "Select-Object Name | ConvertTo-Json -Compress",
            settings.print_server_timeout_seconds, server=settings.print_server_host,
            operation="Get-Printer", telemetry=telemetry,
        )
        result.update(telemetry, success=True)
    except PrintServerError as exc:
        result.update(exc.as_dict())
        result.update(telemetry, success=False, category=exc.category)
    return result
