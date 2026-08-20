from ipaddress import IPv4Address, AddressValueError

from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime


class TonerLevel(BaseModel):
    color: str
    label: str
    percent: int


def _validate_ip(value: str) -> str:
    """
    IPv4 valido. "N/A" e aceito porque a planilha de origem usa esse valor
    para impressoras sem IP fixo, e ha registros assim entre as 73.
    """
    value = value.strip()
    if value.upper() == "N/A":
        return "N/A"
    try:
        return str(IPv4Address(value))
    except AddressValueError:
        raise ValueError(f"IP invalido: {value!r}. Use IPv4 (ex.: 10.150.6.11) ou 'N/A'.")


def _validate_texto(value: str, campo: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError(f"O campo '{campo}' e obrigatorio.")
    return value


class PrinterCreate(BaseModel):
    """
    Cadastro manual — excecao, nao o fluxo principal (Etapa 4: a frota vem
    do Print Server via POST /api/servers/sync). `server` e opcional porque
    uma impressora cadastrada a mao pode nao pertencer a nenhum Print Server.
    """

    ip: str
    name: str
    model: str
    department: str
    server: Optional[str] = None

    @field_validator("ip")
    @classmethod
    def _ip(cls, v: str) -> str:
        return _validate_ip(v)

    @field_validator("name", "model", "department")
    @classmethod
    def _obrigatorio(cls, v: str, info) -> str:
        return _validate_texto(v, info.field_name)


class PrinterUpdate(BaseModel):
    ip: Optional[str] = None
    name: Optional[str] = None
    model: Optional[str] = None
    department: Optional[str] = None

    @field_validator("ip")
    @classmethod
    def _ip(cls, v: Optional[str]) -> Optional[str]:
        return None if v is None else _validate_ip(v)

    @field_validator("name", "model", "department")
    @classmethod
    def _obrigatorio(cls, v: Optional[str], info) -> Optional[str]:
        return None if v is None else _validate_texto(v, info.field_name)


class PrinterResponse(BaseModel):
    id: int
    server: str
    ip: str
    port_name: str
    driver_name: str
    name: str
    model: str
    printer_type: Optional[str] = None
    department: str
    active: bool
    last_seen_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PrinterWithStatus(PrinterResponse):
    """Impressora + ultima leitura conhecida (o que o painel consome)."""
    status: str
    page_count: int
    toner: Optional[List[TonerLevel]] = None
    # ISO da ultima leitura; None quando a impressora nunca foi coletada.
    last_seen: Optional[str] = None
    # Etapa 7: uptime formatado da ultima leitura (ex.: "45d, 3h, 22m"); None
    # quando nunca coletada ou quando a leitura e anterior a Etapa 7.
    uptime: Optional[str] = None


class PrinterReadingCreate(BaseModel):
    status: str
    page_count: int
    toner_k: int | None = None
    toner_c: int | None = None
    toner_m: int | None = None
    toner_y: int | None = None
    uptime: str | None = None


class PrinterReadingResponse(BaseModel):
    id: int
    printer_id: int
    status: str
    page_count: int
    toner_k: int | None = None
    toner_c: int | None = None
    toner_m: int | None = None
    toner_y: int | None = None
    uptime: str | None = None
    timestamp: datetime

    class Config:
        from_attributes = True
