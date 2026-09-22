from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from datetime import datetime
from app.database import get_session
from app.dependencies import require_active_user, require_operator
from app.models.alert import Alert
from app.models.printer import Printer
from app.models.user import User
from app.services.units import unit_for_printer, unit_webhook_url
from app.services.webhook_notifier import send_toner_alert_webhook
from typing import List
from pydantic import BaseModel, Field
from app.schemas.common import RecursoId
from app.services import audit_log

# Fase 2: alertas expoem estado da frota — exigem sessao em todas as rotas.
# As acoes (notify/resolve) continuam declarando require_operator por cima.
router = APIRouter(
    prefix="/alerts",
    tags=["alerts"],
    dependencies=[Depends(require_active_user)],
)


@router.get("")
def list_alerts(
    severity: str | None = None,
    resolved: bool | None = False,
    printer_id: int | None = None,
    alert_type: str | None = None,
    # Paginacao (Fase 10). Alertas RESOLVIDOS nunca sao apagados, entao a
    # tabela so cresce: `?resolved=true` ou `?resolved=` (todos) devolvia o
    # historico inteiro numa unica resposta. O padrao 200 cobre com folga os
    # alertas ativos, que e o que o painel mostra; o historico longo passa a
    # ser lido por paginas via `offset`. Mesmo teto de /api/notifications.
    limit: int = Query(default=200, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session),
):
    """resolved=false (padrao) -> ativos | true -> resolvidos | omitido como null -> todos."""
    query = select(Alert)

    if resolved is False:
        query = query.where(Alert.resolved_at == None)  # noqa: E711
    elif resolved is True:
        query = query.where(Alert.resolved_at != None)  # noqa: E711

    if severity:
        query = query.where(Alert.severity == severity)

    if printer_id is not None:
        query = query.where(Alert.printer_id == printer_id)

    if alert_type:
        query = query.where(Alert.alert_type == alert_type)

    query = query.order_by(Alert.created_at.desc()).offset(offset).limit(limit)
    alerts = session.exec(query).all()
    return alerts


class ReadAllRequest(BaseModel):
    """Corpo opcional de POST /alerts/read-all. Sem `ids` = todos os ativos."""

    ids: List[int] | None = Field(default=None, max_length=1000)


def _leitor(user: User) -> str:
    return (user.name or "").strip() or user.email


@router.post("/read-all")
def mark_all_alerts_read(
    body: ReadAllRequest | None = None,
    session: Session = Depends(get_session),
    user: User = Depends(require_active_user),
):
    """
    Marca como lidos varios alertas de uma vez. Com `ids`, so esses (o painel
    manda os que estao visiveis no filtro atual); sem `ids`, todos os alertas
    ATIVOS ainda nao lidos. Alertas ja lidos ficam como estao (preserva quem
    leu primeiro). Informativo: nunca resolve nada. Fica na trilha de
    auditoria por ser uma acao em massa.
    """
    query = select(Alert).where(Alert.read_at == None)  # noqa: E711
    ids = body.ids if body is not None else None
    if ids is not None:
        if not ids:
            return {"updated": 0}
        query = query.where(Alert.id.in_(ids))
    else:
        query = query.where(Alert.resolved_at == None)  # noqa: E711

    alertas = session.exec(query).all()
    agora = datetime.utcnow()
    leitor = _leitor(user)
    for alerta in alertas:
        alerta.read_at = agora
        alerta.read_by = leitor
        session.add(alerta)

    if alertas:
        audit_log.record(
            session,
            user,
            "alert.read_all",
            "alert",
            0,
            after={"ids": [a.id for a in alertas], "count": len(alertas), "scope": "ids" if ids is not None else "all_active"},
        )
    session.commit()
    return {"updated": len(alertas)}


@router.patch("/{alert_id}/read")
def mark_alert_read(
    alert_id: RecursoId,
    session: Session = Depends(get_session),
    user: User = Depends(require_active_user),
):
    """
    Marca um alerta como lido. Idempotente: se ja estava lido, mantem o
    primeiro read_at/read_by. Nao resolve o alerta — ele continua ativo ate a
    condicao sumir (alert_engine) ou alguem resolver.
    """
    alert = session.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    if alert.read_at is None:
        alert.read_at = datetime.utcnow()
        alert.read_by = _leitor(user)
        session.add(alert)
        session.commit()
        session.refresh(alert)
    return alert


@router.patch("/{alert_id}/unread")
def mark_alert_unread(
    alert_id: RecursoId,
    session: Session = Depends(get_session),
    _user: User = Depends(require_active_user),
):
    """Desfaz o "lido". Idempotente."""
    alert = session.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    if alert.read_at is not None or alert.read_by is not None:
        alert.read_at = None
        alert.read_by = None
        session.add(alert)
        session.commit()
        session.refresh(alert)
    return alert


@router.get("/{alert_id}")
def get_alert(alert_id: RecursoId, session: Session = Depends(get_session)):
    alert = session.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    return alert


@router.post("/{alert_id}/notify")
def notify_alert(
    alert_id: RecursoId,
    session: Session = Depends(get_session),
    _user: User = Depends(require_operator),
):
    """
    Disparo manual do webhook de alerta (Etapa 6) — equivalente ao botao
    "avisar" do card de detalhes no Main.ps1. Nunca cria, resolve ou altera
    o Alert; so envia a notificacao (ou reporta que o webhook esta
    desabilitado/falhou). Idempotencia nesta etapa e responsabilidade de
    quem clica — nada e persistido sobre a tentativa de entrega.
    """
    alert = session.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")

    printer = session.get(Printer, alert.printer_id)
    if not printer:
        raise HTTPException(status_code=404, detail="Impressora do alerta não encontrada")

    color = alert.alert_type.split(":", 1)[1] if alert.alert_type and alert.alert_type.startswith("toner:") else "K"
    sent = send_toner_alert_webhook(
        printer_name=printer.name,
        model=printer.model,
        color=color,
        level_text=alert.message,
        manual=True,
        # Unidades (21/09/2026): mesmo roteamento do automatico — webhook da
        # unidade da impressora + central, sem repetir URL.
        unit_url=unit_webhook_url(unit_for_printer(session, printer)),
    )

    return {
        "alert_id": alert.id,
        "printer_id": printer.id,
        "sent": sent,
        "detail": "Webhook enviado." if sent else "Webhook desabilitado ou falhou (ver logs do servidor).",
    }


@router.patch("/{alert_id}/resolve")
def resolve_alert(
    alert_id: RecursoId,
    session: Session = Depends(get_session),
    _user: User = Depends(require_operator),
):
    """
    Resolve um alerta. Ate a Fase 1 esta rota estava SEM protecao alguma —
    qualquer um com acesso a API podia apagar alertas ativos do painel. E
    uma acao operacional: exige operator (admin herda).
    """
    alert = session.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")

    alert.resolved_at = datetime.utcnow()
    session.add(alert)
    session.commit()
    session.refresh(alert)
    return alert
