"""
Alertas automaticos (Etapa 8A, re-alerta de toner na Fase 11).

Roda logo apos cada PrinterReading ser persistida. Para cada condicao
(offline, toner por cor) existe no maximo UM alerta ativo por impressora,
identificado por Alert.alert_type:

    "offline"   -> impressora nao respondeu
    "toner:K"   -> nivel do toner preto (idem C, M, Y)

Offline: se a condicao continua, o alerta existente e mantido (nada e
criado). Se a condicao some, o alerta e resolvido automaticamente.

Toner (Fase 11): a partir de TONER_ALERT_THRESHOLD (10%), qualquer leitura
com percentual MENOR que o do alerta ativo dispara um novo alerta — mesmo
sem trocar de "severidade", porque so existe uma severidade nesta zona
("critical"). E o que faz o alerta re-avisar a cada ponto percentual que o
toner continua caindo (10%, 9%, 8%...), em vez de avisar uma unica vez ao
cruzar o limiar e ficar em silencio dali para baixo. Uma leitura igual ou
maior (mas ainda dentro da zona) nao re-avisa; sair da zona (>10%) resolve.

Canais de notificacao (Fase 11):
  - Site (sino, Notification): offline E toner, para todos os usuarios
    ativos — fan-out, uma linha por pessoa (ver models/notification.py).
  - Teams (webhook): SO toner. Offline nunca dispara webhook — decisao
    explicita para nao lotar o canal da equipe com um evento que ja e bem
    visivel no proprio painel.
"""
import logging
from datetime import datetime

from sqlmodel import Session, select

from app.models.alert import Alert
from app.models.notification import Notification
from app.models.printer import Printer, PrinterReading
from app.models.user import User
from app.services.webhook_notifier import send_toner_alert_webhook

logger = logging.getLogger("printercontrol.alert_engine")

# Fase 11: zona unica de alerta de toner, severidade "critical" sempre.
# Substituiu os dois niveis antigos (20%=warning, 10%=critical) — ver design
# aprovado na sessao: re-alerta a cada ponto percentual, nao so a entrada.
TONER_ALERT_THRESHOLD = 10

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
) -> tuple[str, Alert | None]:
    """
    Cria, mantem ou resolve o alerta de uma condicao de severidade fixa
    (hoje, so "offline"). Retorna (acao, alerta) — alerta e o que ficou
    ativo (None quando resolvido ou nao havia nada a fazer).
    """
    existing = _active(session, printer_id, alert_type)

    if not active:
        if existing:
            existing.resolved_at = datetime.utcnow()
            session.add(existing)
            return "resolved", None
        return "none", None

    if existing:
        return "kept", existing

    novo = Alert(printer_id=printer_id, alert_type=alert_type, severity=severity, message=message)
    session.add(novo)
    return "created", novo


def _sync_toner_condition(
    session: Session, printer_id: int, color: str, percent: int
) -> tuple[str, Alert | None]:
    """
    Cria, re-alerta ou resolve o alerta de toner de UMA cor, com re-alerta a
    cada ponto percentual que o nivel continua caindo (ver docstring do
    modulo). Retorna (acao, alerta).
    """
    alert_type = f"toner:{color}"
    existing = _active(session, printer_id, alert_type)

    if percent > TONER_ALERT_THRESHOLD:
        if existing:
            existing.resolved_at = datetime.utcnow()
            session.add(existing)
            return "resolved", None
        return "none", None

    message = f"Toner {color} critico: {percent}%"

    if existing:
        # value=None so acontece em alerta criado antes desta coluna existir
        # (migracao aditiva) — trata como "sem referencia", deixa cair para
        # o caminho de re-alerta em vez de silenciar por falta de dado.
        caiu_mais = existing.value is None or percent < existing.value
        if not caiu_mais:
            return "kept", existing

        existing.resolved_at = datetime.utcnow()
        session.add(existing)

    novo = Alert(
        printer_id=printer_id,
        alert_type=alert_type,
        severity="critical",
        message=message,
        value=percent,
    )
    session.add(novo)
    return ("escalated" if existing else "created"), novo


def _notify_all_active_users(session: Session, message: str, severity: str, alert_id: int | None) -> None:
    """
    Fan-out de uma Notification por usuario ativo (Fase 11) — e o canal
    "site" dos alertas automaticos. Contas desativadas nao recebem: a caixa
    delas nunca sera aberta.
    """
    usuarios = session.exec(select(User).where(User.is_active == True)).all()  # noqa: E712
    if not usuarios:
        return
    for usuario in usuarios:
        session.add(Notification(user_id=usuario.id, message=message, severity=severity, alert_id=alert_id))
    session.commit()


def evaluate_reading(session: Session, printer_id: int, reading: PrinterReading) -> dict:
    """
    Avalia uma leitura e sincroniza os alertas da impressora.

    Faz commit ao final. Retorna {alert_type: acao} para log/teste.
    """
    actions: dict[str, str] = {}

    # status possiveis: "online", "atencao", "offline" (ver services/snmp.py)
    offline = reading.status == "offline"
    offline_action, offline_alert = _sync_condition(
        session,
        printer_id,
        "offline",
        active=offline,
        severity="critical",
        message="Impressora offline (sem resposta na ultima coleta)",
    )
    actions["offline"] = offline_action

    # (color, percent, alerta) dos toners que viraram/re-alertaram NESTA
    # leitura com acao created/escalated — so estes disparam notificacao.
    critical_toner_events: list[tuple[str, int, Alert]] = []

    for color, field in TONER_FIELDS.items():
        percent = getattr(reading, field)
        key = f"toner:{color}"

        if offline or percent is None:
            # Sem dado confiavel de toner: nao cria nem resolve nada.
            actions[key] = "skipped"
            continue

        action, alert = _sync_toner_condition(session, printer_id, color, percent)
        actions[key] = action
        if action in ("created", "escalated") and alert is not None:
            critical_toner_events.append((color, percent, alert))

    session.commit()

    # Site (Fase 11): offline criado/escalado tambem avisa, so nao vai para
    # o Teams — o proprio painel ja deixa isso bem visivel.
    if offline_action == "created" and offline_alert is not None:
        printer = session.get(Printer, printer_id)
        nome = printer.name if printer else f"impressora #{printer_id}"
        _notify_all_active_users(
            session,
            message=f"{nome} ficou offline (sem resposta na ultima coleta).",
            severity="critical",
            alert_id=offline_alert.id,
        )

    # Toner: site + Teams para cada evento novo/escalado desta leitura.
    if critical_toner_events:
        printer = session.get(Printer, printer_id)
        if printer:
            for color, percent, alert in critical_toner_events:
                _notify_all_active_users(
                    session,
                    message=f"Toner {color} de {printer.name} em {percent}%.",
                    severity="critical",
                    alert_id=alert.id,
                )
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
