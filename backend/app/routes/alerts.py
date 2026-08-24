from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from datetime import datetime
from app.database import get_session
from app.dependencies import require_operator, require_user
from app.models.alert import Alert
from app.models.printer import Printer
from app.models.user import User
from app.services.webhook_notifier import send_toner_alert_webhook
from typing import List

# Fase 2: alertas expoem estado da frota — exigem sessao em todas as rotas.
# As acoes (notify/resolve) continuam declarando require_operator por cima.
router = APIRouter(
    prefix="/alerts",
    tags=["alerts"],
    dependencies=[Depends(require_user)],
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


@router.get("/{alert_id}")
def get_alert(alert_id: int, session: Session = Depends(get_session)):
    alert = session.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    return alert


@router.post("/{alert_id}/notify")
def notify_alert(
    alert_id: int,
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
    )

    return {
        "alert_id": alert.id,
        "printer_id": printer.id,
        "sent": sent,
        "detail": "Webhook enviado." if sent else "Webhook desabilitado ou falhou (ver logs do servidor).",
    }


@router.patch("/{alert_id}/resolve")
def resolve_alert(
    alert_id: int,
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
