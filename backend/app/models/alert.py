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


class TonerHistory(SQLModel, table=True):
    __tablename__ = "toner_history"

    id: int | None = Field(default=None, primary_key=True)
    printer_id: int = Field(foreign_key="printers.id")
    color: str  # K, C, M, Y
    percent: int
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
