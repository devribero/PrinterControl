"""
Leitura da trilha de auditoria administrativa (Fase 16). Ver
models/audit_log.py e services/audit_log.py para o que e gravado e por que.

So admin: quem alterou usuarios/servidores e informacao sensivel, no mesmo
nivel de quem pode fazer essas alteracoes.
"""
import json

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from app.database import get_session
from app.dependencies import require_admin
from app.models.audit_log import AuditLog

router = APIRouter(
    prefix="/audit-log",
    tags=["audit-log"],
    dependencies=[Depends(require_admin)],
)

# Mesmo teto das outras listagens paginadas (alerts, notifications) — ver
# routes/alerts.py. A trilha so cresce, nunca e apagada.
LIMITE_PADRAO = 200
LIMITE_MAXIMO = 500


@router.get("")
def list_audit_log(
    action: str | None = None,
    target_type: str | None = None,
    target_id: int | None = None,
    limit: int = Query(default=LIMITE_PADRAO, ge=1, le=LIMITE_MAXIMO),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session),
):
    """Mais recentes primeiro. Filtros combinam com AND quando informados juntos."""
    query = select(AuditLog)

    if action:
        query = query.where(AuditLog.action == action)
    if target_type:
        query = query.where(AuditLog.target_type == target_type)
    if target_id is not None:
        query = query.where(AuditLog.target_id == target_id)

    query = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit)
    entries = session.exec(query).all()

    return [
        {
            "id": e.id,
            "actor_user_id": e.actor_user_id,
            "actor_email": e.actor_email,
            "action": e.action,
            "target_type": e.target_type,
            "target_id": e.target_id,
            "before": json.loads(e.before) if e.before else None,
            "after": json.loads(e.after) if e.after else None,
            "created_at": e.created_at.isoformat(),
        }
        for e in entries
    ]
