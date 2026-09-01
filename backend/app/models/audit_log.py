"""
Trilha de auditoria administrativa (Fase 16).

Registra QUEM fez, O QUE e QUANDO em acoes administrativas destrutivas ou
sensiveis (criar/editar/excluir usuario, criar/editar/excluir Print
Server). Nao cobre rotina (sync, coleta) — isso encheria a trilha de ruido
sem valor forense; o alvo aqui e responder "quem mudou isso e quando" para
uma acao que afeta acesso ou cadastro, nao o dia a dia operacional.

Diferente do log de arquivo rotativo (logging_config.py): este fica no
banco, e estruturado (before/after em JSON, nao texto livre), tem
`target_id` pesquisavel, e nao desaparece quando o arquivo de log
rotaciona (LOG_BACKUP_COUNT).
"""
from datetime import datetime

from sqlmodel import Field, SQLModel


class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_log"

    id: int | None = Field(default=None, primary_key=True)

    # FK opcional: se a conta do autor for excluida depois, o registro do
    # que ela fez continua legivel (so a referencia vira null). O e-mail
    # abaixo e a copia que garante isso na pratica.
    actor_user_id: int | None = Field(default=None, foreign_key="users.id", index=True)
    actor_email: str

    # "user.create" | "user.update" | "user.delete" |
    # "server.create" | "server.update" | "server.delete"
    action: str = Field(index=True)
    target_type: str = Field(index=True)  # "user" | "print_server"
    target_id: int = Field(index=True)

    # Estado antes/depois, serializado como JSON (texto — sem tipo JSON
    # nativo em uso no resto do projeto, sem motivo pra introduzir um so
    # aqui). Nulo em create (nao ha "antes") e em delete (nao ha "depois").
    # NUNCA inclui password_hash — ver os `_snapshot_*` em cada rota que
    # grava aqui.
    before: str | None = None
    after: str | None = None

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
