"""
Grava entradas da trilha de auditoria administrativa. Ver models/audit_log.py
para o que e por que.
"""
import json
from typing import Any

from sqlmodel import Session

from app.models.audit_log import AuditLog
from app.models.user import User


def record(
    session: Session,
    actor: User,
    action: str,
    target_type: str,
    target_id: int,
    before: dict[str, Any] | None = None,
    after: dict[str, Any] | None = None,
) -> None:
    """
    Adiciona uma linha da trilha a sessao. NAO commita — quem chama grava
    isto na MESMA transacao da mutacao que esta registrando (antes do
    commit dela). Se a mutacao falhar, o registro de auditoria tambem nao
    fica gravado sozinho e inconsistente com o que de fato aconteceu.

    `before`/`after` sao dict simples (nunca o objeto do model direto —
    quem chama decide exatamente quais campos entram, para nunca vazar
    password_hash ou algo assim sem querer).
    """
    session.add(
        AuditLog(
            actor_user_id=actor.id,
            actor_email=actor.email,
            action=action,
            target_type=target_type,
            target_id=target_id,
            before=json.dumps(before, default=str) if before is not None else None,
            after=json.dumps(after, default=str) if after is not None else None,
        )
    )
