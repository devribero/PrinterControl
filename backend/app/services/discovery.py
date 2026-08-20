"""Enriquecimento transitório de filas descobertas com telemetria SNMP."""

import re
from dataclasses import dataclass
from ipaddress import IPv4Address, AddressValueError
from typing import Callable

from app.config import settings
from app.services.print_server import DiscoveredPrinter
from app.services.snmp import SNMPClient, SNMPResult
from app.services.snmp_mock import MockSNMPClient

LABEL_RE = re.compile(r"TT042|Honeywell|Etiqueta|Zebra|Argox|Sewoo|RP4f", re.I)
COLOR_RE = re.compile(r"color|M6530", re.I)


@dataclass
class EnrichedDiscoveredPrinter:
    name: str
    server: str
    port_name: str
    ip: str | None
    driver_name: str
    model: str | None
    printer_type: str | None
    ip_group_size: int
    network_query_reused: bool
    reachable: bool | None
    snmp_responded: bool
    status: str
    status_reason: str
    page_count: int | None
    uptime: str | None
    toners: list
    error: str | None


def _normalize_ip(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return str(IPv4Address(value.strip()))
    except (AddressValueError, ValueError):
        return None


def _is_label(printer: DiscoveredPrinter) -> bool:
    return bool(LABEL_RE.search(printer.driver_name or "") or LABEL_RE.search(printer.name or ""))


def _is_color(printer: DiscoveredPrinter) -> bool:
    return bool(COLOR_RE.search(printer.driver_name or "") or COLOR_RE.search(printer.name or ""))


def _empty_result(reason: str, error: str | None = None) -> SNMPResult:
    return SNMPResult(
        status="offline" if reason in {"invalid_or_missing_ip", "ping_failed"} else "online",
        reachable=False if reason in {"invalid_or_missing_ip", "ping_failed"} else None,
        snmp_responded=False,
        page_count=None,
        uptime="N/A",
        error=error,
        status_reason=reason,
    )


def _result_for_ip(
    ip: str,
    members: list[DiscoveredPrinter],
    client_factory: Callable[[], object],
) -> SNMPResult:
    if not any(_normalize_ip(member.ip) for member in members):
        return _empty_result("invalid_or_missing_ip", "IP ausente ou inválido")

    if all(_is_label(member) for member in members):
        client = client_factory()
        reachable = client._ping(ip) if hasattr(client, "_ping") else True
        return SNMPResult(
            status="online" if reachable else "offline",
            reachable=reachable,
            snmp_responded=False,
            uptime="N/A",
            status_reason="snmp_not_applicable",
            error="Printer-MIB não aplicável ao dispositivo",
        )

    try:
        client = client_factory()
        result = client.collect(ip, is_color=any(_is_color(member) for member in members))
        if result.status_reason is None:
            if not result.reachable:
                result.status_reason = "ping_failed"
            elif not result.snmp_responded:
                result.status_reason = "ping_ok_snmp_not_responding"
            elif result.page_count is None:
                result.status_reason = "snmp_without_page_count"
            elif not result.toners:
                result.status_reason = "snmp_partial_data"
            else:
                result.status_reason = "snmp_data_available"
        return result
    except TimeoutError:
        return _empty_result("snmp_timeout", "Timeout SNMP")
    except OSError as exc:
        return _empty_result("snmp_socket_error", f"Erro de socket SNMP: {type(exc).__name__}")
    except Exception as exc:
        return _empty_result("snmp_error", f"Falha SNMP: {type(exc).__name__}")


def enrich_discovered_printers(
    printers: list[DiscoveredPrinter],
    mode: str,
    mock_scenario: str = "online_mono",
    client_factory: Callable[[], object] | None = None,
) -> list[EnrichedDiscoveredPrinter]:
    """Enriquece filas em memória; não recebe nem acessa uma sessão SQL."""
    groups: dict[str, list[DiscoveredPrinter]] = {}
    for printer in printers:
        ip = _normalize_ip(printer.ip)
        if ip is not None:
            groups.setdefault(ip, []).append(printer)

    if client_factory is None:
        if mode == "mock":
            client_factory = lambda: MockSNMPClient(mock_scenario)
        elif mode == "real":
            client_factory = lambda: SNMPClient(
                community=settings.snmp_community,
                timeout=settings.snmp_timeout,
            )
        else:
            raise ValueError(f"modo de Print Server inválido: {mode!r}")

    results: dict[str, SNMPResult] = {
        ip: _result_for_ip(ip, members, client_factory) for ip, members in groups.items()
    }
    enriched: list[EnrichedDiscoveredPrinter] = []
    for printer in printers:
        ip = _normalize_ip(printer.ip)
        group = groups.get(ip, []) if ip else []
        result = _empty_result("invalid_or_missing_ip", "IP ausente ou inválido") if not ip else results[ip]
        if ip and len(group) > 1 and result.status_reason == "snmp_data_available":
            reason = "snmp_data_available"
        else:
            reason = result.status_reason or "unknown"
        enriched.append(
            EnrichedDiscoveredPrinter(
                name=printer.name,
                server=printer.server,
                port_name=printer.port_name,
                ip=ip,
                driver_name=printer.driver_name,
                model=None,
                printer_type=None,
                ip_group_size=len(group),
                network_query_reused=bool(ip and len(group) > 1),
                reachable=result.reachable,
                snmp_responded=result.snmp_responded,
                status=result.status,
                status_reason=reason,
                page_count=result.page_count,
                uptime=None if result.uptime == "N/A" else result.uptime,
                toners=result.toners,
                error=result.error,
            )
        )
    return enriched