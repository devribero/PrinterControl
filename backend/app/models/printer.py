from sqlmodel import SQLModel, Field, UniqueConstraint
from typing import Optional
from datetime import datetime


class Printer(SQLModel, table=True):
    """
    Etapa 4: identidade e (server, name), NAO ip — o Print Server permite
    varias impressoras no mesmo IP (confirmado no Main.ps1 e refletido no
    UniqueConstraint abaixo, que substitui o antigo `ip UNIQUE`).
    """

    __tablename__ = "printers"
    __table_args__ = (UniqueConstraint("server", "name", name="uq_printer_server_name"),)

    id: int | None = Field(default=None, primary_key=True)

    # Origem no Print Server (Get-Printer/Get-PrinterPort do Main.ps1).
    # server="" para registros legados/manuais sem Print Server associado.
    #
    # Continua sendo a CHAVE NATURAL: participa do UniqueConstraint acima e
    # e o que o sync compara. A FK abaixo (Fase 4) e a ligacao estruturada
    # com `print_servers`; as duas guardam o mesmo servidor e sao gravadas
    # juntas pelo printer_sync, nunca separadamente.
    server: str = Field(default="", index=True)

    # Fase 4: ligacao com o registro de Print Servers. Nula em impressoras
    # manuais/legadas (server="") e em bancos antes da migracao; a migracao
    # preenche a partir do host. Coluna aditiva — nenhuma linha e reescrita.
    print_server_id: Optional[int] = Field(
        default=None, foreign_key="print_servers.id", index=True
    )
    name: str = Field(index=True)
    ip: str = Field(index=True)  # NAO unico: impressoras podem compartilhar IP
    port_name: str = Field(default="")
    driver_name: str = Field(default="")

    # Obter-Modelo(driver_name) / Obter-TipoImpressora(name, model) do Main.ps1
    model: str
    printer_type: Optional[str] = Field(default=None)  # "A4" | "Etiqueta" | "Portatil"

    department: str = Field(default="")  # enriquecimento manual; Print Server nao fornece

    # Sincronizacao (Etapa 4): impressora que sumiu do Print Server fica
    # active=False, nunca e apagada — preserva leituras e alertas.
    active: bool = Field(default=True, index=True)
    last_seen_at: Optional[datetime] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PrinterReading(SQLModel, table=True):
    __tablename__ = "printer_readings"

    id: int | None = Field(default=None, primary_key=True)
    printer_id: int = Field(foreign_key="printers.id")
    status: str  # online, offline, atencao
    page_count: int
    toner_k: int | None = None
    toner_c: int | None = None
    toner_m: int | None = None
    toner_y: int | None = None
    # Etapa 7: mesmo texto formatado de SNMPResult.uptime (ex.: "45d, 3h, 22m"
    # ou "N/A"). Coluna adicionada via migracao aditiva — leituras anteriores
    # a Etapa 7 ficam com uptime=NULL, nunca reescritas.
    uptime: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)


class PrinterMonthly(SQLModel, table=True):
    __tablename__ = "printer_monthly"

    id: int | None = Field(default=None, primary_key=True)
    printer_id: int = Field(foreign_key="printers.id")
    month: str  # "Jan", "Fev", etc
    pages_printed: int
    month_start: datetime
    month_end: datetime
