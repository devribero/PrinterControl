"""
Orquestracao da coleta da frota inteira (Etapa 5).

Separacao de responsabilidades:
    printer_collector.py -> coleta de UMA impressora/IP (SNMP, conversao em
                             PrinterReading, persistencia) — reaproveitado
                             aqui como biblioteca, nao duplicado.
    printer_fleet.py      -> este modulo: agrupamento por IP, dedupe dentro
                             do ciclo, paralelismo limitado e o loop que
                             cobre a frota inteira.

Equivalente a Process-ImpressorasList / Atualizar-ImpressorasAsync do
Main.ps1: percorre a frota, evita consultar duas vezes o mesmo IP quando
impressoras o compartilham, e faz isso em paralelo com um limite de workers.

Fonte da frota: SEMPRE `SELECT * FROM printers WHERE active=True`. Este
modulo nao chama print_server.py nem printer_sync.py — descobrir/sincronizar
com o Print Server continua uma acao manual e separada (POST
/api/servers/sync), porque em modo mock ela desativaria a maior parte da
frota real. Ver printer_sync.py para o motivo completo.

Dedupe por IP — o que e compartilhado e o que nao e:
    Compartilhado (mesma consulta de rede, reaproveitada para todo o grupo):
        status, page_count, toners, uptime, reachable, snmp_responded, error
        — sao o retorno de UMA consulta SNMP/ping ao dispositivo fisico por
        tras do IP. Duas impressoras cadastradas no mesmo IP sao a mesma
        maquina publicada duas vezes (ex.: fila colorida + fila mono do
        mesmo equipamento), entao a leitura de rede e legitimamente a mesma.
    Processado por impressora (nunca compartilhado):
        is_color_printer / is_label_printer / modelo / tipo — decidem COMO
        o grupo e consultado (ver `_group_plan` abaixo) e como a leitura de
        cada membro e persistida, mas a decisao usa as caracteristicas de
        CADA impressora do grupo, nao de uma so.

O dedupe vale apenas DENTRO de um ciclo (uma chamada a collect_fleet). Nao ha
cache entre ciclos — cada chamada agrupa e consulta do zero, para nao usar
dado SNMP velho como se fosse atual.

Threads e banco: os workers do ThreadPoolExecutor SO fazem I/O de rede
(SNMP/ping) — nenhum acessa a Session. Os resultados voltam para o thread
principal, que persiste tudo sequencialmente numa unica Session (o mesmo
padrao ja usado por PrinterCollector.collect_and_save), evitando qualquer
uso concorrente da Session/engine SQLite.
"""
import logging
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

from sqlmodel import Session, select

from app.config import settings
from app.models.printer import Printer, PrinterReading
from app.services.alert_engine import evaluate_reading
from app.services.printer_collector import PrinterCollector
from app.services.snmp import SNMPClient, SNMPResult
from app.services.snmp_fleet_mock import FleetMockClient
from app.services.snmp_mock import MockSNMPClient

logger = logging.getLogger("printercontrol.fleet")


@dataclass
class FleetCollectionResult:
    total_printers: int
    unique_ips: int
    collected: int = 0
    failed: int = 0
    by_status: dict = field(default_factory=dict)
    alerts_created: int = 0
    alerts_resolved: int = 0
    errors: list = field(default_factory=list)


def _group_by_ip(printers: list[Printer]) -> dict[str, list[Printer]]:
    groups: dict[str, list[Printer]] = defaultdict(list)
    for p in printers:
        groups[p.ip].append(p)
    return groups


def _group_plan(members: list[Printer]) -> tuple[bool, bool]:
    """
    Decide como o grupo (impressoras que compartilham este IP) deve ser
    consultado, a partir das caracteristicas INDIVIDUAIS de cada membro:

        full_snmp: True se ALGUM membro nao for etiquetadora/portatil ->
            o grupo recebe a consulta SNMP completa (equivalente ao PS1
            pular SNMP so quando TODAS as filas daquele IP sao etiqueta).
        is_color: True se ALGUM membro for colorido -> a consulta pede os
            toners CMY, nao so K (impressora mono do mesmo grupo simplesmente
            ignora os campos extra ao persistir).
    """
    full_snmp = any(not PrinterCollector.is_label_printer(p) for p in members)
    is_color = any(PrinterCollector.is_color_printer(p) for p in members)
    return full_snmp, is_color


def _collect_ip_network(
    ip: str,
    members: list[Printer],
    mode: str,
    mock_scenario: str,
    fleet_previous_page_count: int | None,
    fleet_representative_id: int,
) -> SNMPResult:
    """
    UMA consulta de rede para o IP (chamada dentro do worker thread).

    Sem acesso a banco — qualquer dado que dependa da Session (contador
    anterior para o modo "fleet") e lido pelo thread principal ANTES de
    submeter esta tarefa ao pool, e passado por parametro.
    """
    full_snmp, is_color = _group_plan(members)

    if mode == "fleet":
        client = FleetMockClient(
            printer_id=fleet_representative_id,
            previous_page_count=fleet_previous_page_count,
        )
        return client.collect(ip, is_color=is_color)

    if mode == "real" and not full_snmp:
        # Etiquetadora/portatil (ou grupo so com elas): PS1 nao consulta
        # SNMP, so a conectividade.
        reachable = SNMPClient()._ping(ip)
        result = SNMPResult(
            status="online" if reachable else "offline",
            reachable=True,
            snmp_responded=False,
            error="etiquetadora/portatil: SNMP nao consultado",
        )
        result.reachable = result.status == "online"
        return result

    if mode == "real":
        client = SNMPClient(community=settings.snmp_community, timeout=settings.snmp_timeout)
        return client.collect(ip, is_color=is_color)

    if mode == "mock":
        client = MockSNMPClient(scenario=mock_scenario)
        return client.collect(ip, is_color=is_color)

    raise ValueError(f"modo de coleta invalido: {mode!r}")


def collect_fleet(
    session: Session,
    mode: str = "real",
    mock_scenario: str = "online_mono",
    max_workers: int | None = None,
) -> FleetCollectionResult:
    """
    Um ciclo completo de coleta sobre toda a frota ATIVA (active=True).

    Nunca chama o Print Server nem sync_printers — a fonte e exclusivamente
    o banco, para nao arriscar aplicar a frota mock (7 impressoras) sobre as
    73 reais.
    """
    max_workers = max_workers or settings.collection_max_workers

    printers = list(session.exec(select(Printer).where(Printer.active == True)))  # noqa: E712
    groups = _group_by_ip(printers)
    result = FleetCollectionResult(total_printers=len(printers), unique_ips=len(groups))

    # Leitura do contador anterior (modo fleet) — acesso a Session fica
    # inteiramente no thread principal, antes de qualquer submit ao pool.
    fleet_prev_counts: dict[str, int | None] = {}
    fleet_representative: dict[str, int] = {}
    if mode == "fleet":
        for ip, members in groups.items():
            rep = min(members, key=lambda p: p.id)
            fleet_representative[ip] = rep.id
            previous = session.exec(
                select(PrinterReading)
                .where(PrinterReading.printer_id == rep.id)
                .order_by(PrinterReading.id.desc())
            ).first()
            fleet_prev_counts[ip] = previous.page_count if previous and previous.page_count else None

    raw_results: dict[str, SNMPResult] = {}
    network_errors: dict[str, str] = {}

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(
                _collect_ip_network,
                ip,
                members,
                mode,
                mock_scenario,
                fleet_prev_counts.get(ip),
                fleet_representative.get(ip, min(members, key=lambda p: p.id).id),
            ): ip
            for ip, members in groups.items()
        }
        for future in as_completed(futures):
            ip = futures[future]
            try:
                raw_results[ip] = future.result()
            except Exception as exc:  # nunca deixa uma falha de IP derrubar o ciclo
                network_errors[ip] = f"{type(exc).__name__}: {exc}"
                logger.warning("Falha na coleta de rede | ip=%s erro=%s", ip, network_errors[ip])

    # Persistencia sequencial, thread principal, uma unica Session — mesmo
    # padrao de PrinterCollector.collect_and_save.
    for ip, members in groups.items():
        if ip in network_errors:
            result.failed += len(members)
            result.errors.append(f"ip {ip}: {network_errors[ip]}")
            continue

        snmp_result = raw_results[ip]
        for printer in members:
            try:
                reading = PrinterCollector._result_to_reading(printer.id, snmp_result)
                session.add(reading)
                session.commit()
                session.refresh(reading)

                alert_actions = evaluate_reading(session, printer.id, reading)

                result.collected += 1
                result.by_status[snmp_result.status] = result.by_status.get(snmp_result.status, 0) + 1
                for action in alert_actions.values():
                    if action == "created" or action == "escalated":
                        result.alerts_created += 1
                    elif action == "resolved":
                        result.alerts_resolved += 1
            except Exception as exc:
                session.rollback()
                result.failed += 1
                result.errors.append(f"printer {printer.id}: {type(exc).__name__}: {exc}")

    return result
