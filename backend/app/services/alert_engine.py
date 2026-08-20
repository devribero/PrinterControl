"""
Alertas automaticos (Etapa 8A).

Roda logo apos cada PrinterReading ser persistida. Para cada condicao
(offline, toner por cor) existe no maximo UM alerta ativo por impressora,
identificado por Alert.alert_type:

    "offline"   -> impressora nao respondeu
    "toner:K"   -> nivel do toner preto (idem C, M, Y)

Se a condicao continua, o alerta existente e mantido (nada e criado).
Se a severidade muda (warning -> critical), o alerta antigo e resolvido e um
novo e criado, para o historico registrar a escalada.
Se a condicao some, o alerta e resolvido automaticamente.
"""
import logging
from datetime import datetime

from sqlmodel import Session, select

from app.models.alert import Alert
from app.models.printer import Printer, PrinterReading
from app.services.webhook_notifier import send_toner_alert_webhook

logger = logging.getLogger("printercontrol.alert_engine")

TONER_WARNING_PCT = 20
TONER_CRITICAL_PCT = 10

TONER_FIELDS = {"K": "toner_k", "C": "toner_c", "M": "toner_m", "Y": "toner_y"}


def _active(session: Session, printer_id: int, alert_type: str) -> Alert | None:
    return session.exec(
        select(Alert)
        .where(Alert.printer_id == printer_id)
        .where(Alert.alert_type == alert_type)
        .where(Alert.resolved_at == None)  # noqa: E711
        .order_by(Alert.created_at.desc())
    ).first()


def _sync_condition(
    session: Session,
    printer_id: int,
    alert_type: str,
    active: bool,
    severity: str | None = None,
    message: str | None = None,
) -> str:
    """Cria, mantem ou resolve o alerta de uma condicao. Retorna a acao tomada."""
    existing = _active(session, printer_id, alert_type)

    if not active:
        if existing:
            existing.resolved_at = datetime.utcnow()
            session.add(existing)
            return "resolved"
        return "none"

    if existing:
        if existing.severity == severity:
            return "kept"
        # Escalada/desescalada: fecha o anterior e abre um com a nova severidade.
        existing.resolved_at = datetime.utcnow()
        session.add(existing)

    session.add(
        Alert(printer_id=printer_id, alert_type=alert_type, severity=severity, message=message)
    )
    return "created" if not existing else "escalated"


def evaluate_reading(session: Session, printer_id: int, reading: PrinterReading) -> dict:
    """
    Avalia uma leitura e sincroniza os alertas da impressora.

    Faz commit ao final. Retorna {alert_type: acao} para log/teste.
    """
    actions: dict[str, str] = {}
    # (color, percent) dos toners que viraram/permaneceram critical NESTA
    # leitura com acao created/escalated — so estes disparam webhook (Etapa 6).
    critical_toner_notifications: list[tuple[str, int]] = []

    # status possiveis: "online", "atencao", "offline" (ver services/snmp.py)
    offline = reading.status == "offline"
    actions["offline"] = _sync_condition(
        session,
        printer_id,
        "offline",
        active=offline,
        severity="critical",
        message="Impressora offline (sem resposta na ultima coleta)",
    )

    for color, field in TONER_FIELDS.items():
        percent = getattr(reading, field)
        key = f"toner:{color}"

        if offline or percent is None:
            # Sem dado confiavel de toner: nao cria nem resolve nada.
            actions[key] = "skipped"
            continue

        if percent <= TONER_CRITICAL_PCT:
            actions[key] = _sync_condition(
                session, printer_id, key, True, "critical",
                f"Toner {color} critico: {percent}%",
            )
            if actions[key] in ("created", "escalated"):
                critical_toner_notifications.append((color, percent))
        elif percent <= TONER_WARNING_PCT:
            actions[key] = _sync_condition(
                session, printer_id, key, True, "warning",
                f"Toner {color} baixo: {percent}%",
            )
        else:
            actions[key] = _sync_condition(session, printer_id, key, False)

    session.commit()

    # Webhook (Etapa 6): so toner critical, so created/escalated (nunca
    # "kept" — a idempotencia desta etapa e o proprio estado do Alert, sem
    # coluna/tabela nova para registrar entrega). Nunca deixa uma falha de
    # rede propagar para quem chamou evaluate_reading.
    if critical_toner_notifications:
        printer = session.get(Printer, printer_id)
        if printer:
            for color, percent in critical_toner_notifications:
                try:
                    send_toner_alert_webhook(
                        printer_name=printer.name,
                        model=printer.model,
                        color=color,
                        level_text=f"{percent}%",
                        manual=False,
                    )
                except Exception:
                    # send_toner_alert_webhook ja captura tudo internamente;
                    # este except e defesa extra para nunca derrubar a coleta.
                    logger.warning("Webhook automatico falhou de forma inesperada | printer_id=%s", printer_id)

    return actions
