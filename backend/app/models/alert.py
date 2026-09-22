from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Alert(SQLModel, table=True):
    __tablename__ = "alerts"

    id: int | None = Field(default=None, primary_key=True)
    printer_id: int = Field(foreign_key="printers.id")
    # Condicao que gerou o alerta: "offline", "toner:K", "toner:C"...
    # Chave de deduplicacao: no maximo um alerta ativo por (printer_id, alert_type).
    alert_type: str | None = Field(default=None, index=True)
    severity: str  # critical, warning, info
    message: str

    # Percentual do toner no momento deste alerta (alertas de toner) ou nulo
    # (offline, e qualquer alerta anterior a esta coluna). Usado pelo
    # alert_engine para saber se o toner caiu mais desde o ultimo alerta —
    # sem isso, um alerta "critical" parado em 10% nunca re-avisaria
    # conforme o nivel continuasse descendo ate 0%.
    value: int | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    resolved_at: datetime | None = None

    # "Marcar como lido" (22/09/2026). Puramente informativo: NAO resolve o
    # alerta nem mexe no alert_engine. E um estado do alerta (compartilhado
    # pela equipe), nao por usuario — a caixa pessoal com read_at por pessoa
    # e a Notification. Re-alerta de toner cria uma LINHA NOVA (a anterior e
    # resolvida), entao a nova queda ja nasce como nao lida sem limpar nada.
    read_at: datetime | None = None
    # Nome (ou e-mail, se sem nome) de quem marcou; texto livre de proposito
    # para sobreviver a exclusao/renomeacao da conta.
    read_by: str | None = None


class TonerHistory(SQLModel, table=True):
    __tablename__ = "toner_history"

    id: int | None = Field(default=None, primary_key=True)
    printer_id: int = Field(foreign_key="printers.id")
    color: str  # K, C, M, Y
    percent: int
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
