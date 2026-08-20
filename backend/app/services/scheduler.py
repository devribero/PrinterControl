"""
Coleta agendada (Etapa 7; frota inteira desde a Etapa 5).

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
"""
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlmodel import Session

from app.config import settings
from app.database import engine
from app.services.printer_fleet import collect_fleet

logger = logging.getLogger("printercontrol.scheduler")

JOB_ID = "collect_printers"

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
    _scheduler.start()

    logger.info(
        "Scheduler iniciado | intervalo=%smin mode=%s max_workers=%s scenario=%s (frota ativa completa)",
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
    }
