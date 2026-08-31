"""
Coleta agendada (Etapa 7; frota inteira desde a Etapa 5; fechamento
mensal na Fase 12).

APScheduler roda dentro do proprio processo do FastAPI e apenas dispara
printer_fleet.collect_fleet() — nenhuma logica de coleta e duplicada aqui.
O job e sincrono, entao o AsyncIOScheduler o executa em uma thread separada
e o event loop continua atendendo requisicoes HTTP normalmente.

Etapa 5: o ciclo cobre TODA a frota ativa (active=True no banco), agrupada
por IP com dedupe dentro do ciclo — ver printer_fleet.py. O scheduler NUNCA
chama discover_printers()/sync_printers(): a fonte da frota e exclusivamente
o banco, para nao arriscar aplicar a descoberta mock sobre os dados reais
(ver printer_sync.py). collection_printer_ids ficou sem uso aqui (legado,
mantido em config.py sem remocao).

Fase 12 — fechamento mensal automatico
---------------------------------------
GET /monthly-report ja calculava "maior contador do mes - menor contador do
mes" a partir de PrinterReading, mas dependia de qual leitura calhou de ser
a primeira/ultima do mes — se o ciclo de coleta atrasar ou falhar perto da
virada do mes, o numero fica levemente subestimado.

Dois jobs novos, no MESMO scheduler:
  - Dia 1, de madrugada: forca um ciclo de coleta extra, garantindo uma
    leitura logo no inicio do mes (nao depende so do intervalo de N em N
    minutos ter calhado de rodar bem na virada).
  - Ultimo dia do mes, a noite: forca outro ciclo, depois congela o
    resultado do mes que esta terminando em PrinterMonthly — a mesma
    tabela que o importador de historico (import_historico_planilha.py)
    usa. Dali em diante GET /monthly-report usa esse numero oficial para
    aquele mes, em vez de recalcular ao vivo toda vez.
"""
import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlmodel import Session, select

from app.config import settings
from app.database import engine
from app.services.monthly_report import month_bounds, month_period, pages_from_readings, upsert_printer_monthly
from app.services.printer_fleet import collect_fleet

logger = logging.getLogger("printercontrol.scheduler")

JOB_ID = "collect_printers"
MONTH_START_JOB_ID = "month_start_snapshot"
MONTH_CLOSE_JOB_ID = "month_close"

_scheduler: AsyncIOScheduler | None = None


def run_collection_cycle() -> None:
    """Um ciclo de coleta: toda a frota ativa, agrupada por IP (printer_fleet.collect_fleet)."""
    mode = settings.collection_mode

    logger.info(
        "Ciclo iniciado | mode=%s scenario=%s max_workers=%s",
        mode,
        settings.collection_scenario if mode == "mock" else "-",
        settings.collection_max_workers,
    )

    with Session(engine) as session:
        result = collect_fleet(
            session,
            mode=mode,
            mock_scenario=settings.collection_scenario,
            max_workers=settings.collection_max_workers,
        )

    logger.info(
        "Ciclo concluido | frota=%s ips_unicos=%s sucesso=%s falha=%s status=%s alertas_criados=%s alertas_resolvidos=%s",
        result.total_printers,
        result.unique_ips,
        result.collected,
        result.failed,
        result.by_status,
        result.alerts_created,
        result.alerts_resolved,
    )
    for err in result.errors[:10]:
        logger.warning("FALHA| %s", err)


def run_month_start_snapshot() -> None:
    """
    Dia 1 de cada mes, de madrugada: forca um ciclo de coleta extra so para
    garantir uma leitura logo no inicio do mes, sem depender do intervalo
    normal (COLLECTION_INTERVAL_MINUTES) ter calhado de rodar perto da
    virada. A leitura em si e um PrinterReading normal — nada de especial
    e gravado aqui, so run_collection_cycle() de novo.
    """
    logger.info("Snapshot de inicio de mes: coleta extra")
    run_collection_cycle()


def run_month_close() -> None:
    """
    Ultimo dia de cada mes, a noite: forca uma coleta final (garante
    leitura bem no fim do mes) e congela o resultado do mes que esta
    terminando em PrinterMonthly — maior contador do mes menos o menor,
    mesma conta de pages_from_readings() usada por GET /monthly-report.

    Upsert por (printer_id, month): rodar de novo no mesmo mes (ex.:
    reiniciar o processo perto da meia-noite) atualiza o numero em vez de
    duplicar. So mexe no mes corrente — nunca recalcula ou apaga meses
    anteriores, sejam eles fechados por este job ou importados de planilha.
    """
    logger.info("Fechamento mensal: coleta final antes de congelar o mes")
    run_collection_cycle()

    with Session(engine) as session:
        hoje = datetime.utcnow()
        mes_inicio, mes_fim = month_bounds(hoje)
        periodo = month_period(hoje)

        paginas_por_impressora = pages_from_readings(session, mes_inicio, mes_fim)
        for printer_id, paginas in paginas_por_impressora.items():
            upsert_printer_monthly(session, printer_id, periodo, paginas, mes_inicio, hoje)
        session.commit()

    logger.info(
        "Fechamento mensal concluido | mes=%s impressoras_fechadas=%s",
        periodo,
        len(paginas_por_impressora),
    )


def start_scheduler() -> AsyncIOScheduler | None:
    """Liga o scheduler conforme o .env. Retorna None quando desabilitado."""
    global _scheduler

    if not settings.collection_enabled:
        logger.info("Scheduler desabilitado (COLLECTION_ENABLED=false)")
        return None

    if settings.collection_mode == "mock" and not settings.allow_mock_collect:
        logger.error(
            "Scheduler NAO iniciado: COLLECTION_MODE=mock exige ALLOW_MOCK_COLLECT=true. "
            "Em producao use COLLECTION_MODE=real."
        )
        return None

    if settings.collection_mode not in ("real", "mock"):
        logger.error(
            "Scheduler NAO iniciado: COLLECTION_MODE=%r invalido (use 'real' ou 'mock')",
            settings.collection_mode,
        )
        return None

    _scheduler = AsyncIOScheduler(timezone="America/Sao_Paulo")
    _scheduler.add_job(
        run_collection_cycle,
        trigger="interval",
        minutes=settings.collection_interval_minutes,
        id=JOB_ID,
        # Impede sobreposicao: se um ciclo demorar mais que o intervalo,
        # o proximo disparo e descartado em vez de rodar em paralelo.
        max_instances=1,
        coalesce=True,
        misfire_grace_time=30,
    )

    # Fase 12: fechamento mensal. Grace time generoso (1h) de proposito —
    # diferente do ciclo normal (roda a cada poucos minutos, perder um
    # disparo nao importa), estes rodam uma vez por mes: se o processo
    # estiver reiniciando exatamente nesse minuto, vale a pena tentar de
    # novo dentro da hora seguinte em vez de esperar o mes que vem.
    _scheduler.add_job(
        run_month_start_snapshot,
        trigger="cron",
        day=1,
        hour=0,
        minute=10,
        id=MONTH_START_JOB_ID,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=3600,
    )
    _scheduler.add_job(
        run_month_close,
        trigger="cron",
        day="last",
        hour=23,
        minute=50,
        id=MONTH_CLOSE_JOB_ID,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=3600,
    )

    _scheduler.start()

    logger.info(
        "Scheduler iniciado | intervalo=%smin mode=%s max_workers=%s scenario=%s (frota ativa completa; "
        "fechamento mensal dia 1 00:10 e ultimo dia 23:50)",
        settings.collection_interval_minutes,
        settings.collection_mode,
        settings.collection_max_workers,
        settings.collection_scenario if settings.collection_mode == "mock" else "-",
    )
    return _scheduler


def shutdown_scheduler() -> None:
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler encerrado")
    _scheduler = None


def scheduler_status() -> dict:
    """Estado atual, para o endpoint de diagnostico."""
    from sqlmodel import func, select

    from app.models.printer import Printer

    job = _scheduler.get_job(JOB_ID) if _scheduler else None
    month_start_job = _scheduler.get_job(MONTH_START_JOB_ID) if _scheduler else None
    month_close_job = _scheduler.get_job(MONTH_CLOSE_JOB_ID) if _scheduler else None
    with Session(engine) as session:
        active_printers = session.exec(
            select(func.count()).select_from(Printer).where(Printer.active == True)  # noqa: E712
        ).one()

    return {
        "enabled": settings.collection_enabled,
        "running": bool(_scheduler and _scheduler.running),
        "mode": settings.collection_mode,
        "interval_minutes": settings.collection_interval_minutes,
        "max_workers": settings.collection_max_workers,
        "active_printers": active_printers,
        "scenario": settings.collection_scenario if settings.collection_mode == "mock" else None,
        "next_run": job.next_run_time.isoformat() if job and job.next_run_time else None,
        "next_month_start_snapshot": month_start_job.next_run_time.isoformat() if month_start_job and month_start_job.next_run_time else None,
        "next_month_close": month_close_job.next_run_time.isoformat() if month_close_job and month_close_job.next_run_time else None,
    }
