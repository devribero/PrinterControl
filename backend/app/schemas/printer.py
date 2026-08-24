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


# Estados que a coleta real (services/snmp.py) e capaz de produzir, e os
# unicos que o painel sabe desenhar (PrinterStatusBadge, StatCards,
# NetworkView). Qualquer outro valor gravado aqui chega ao frontend como um
# badge sem cor e sem rotulo, e some dos contadores por status.
PRINTER_STATUSES = ("online", "offline", "atencao")

# Toner e percentual. O SNMP devolve 0-100; valores fora disso so entram por
# escrita manual e envenenam o motor de alertas, que compara o nivel com os
# limiares para decidir se abre alerta critico.
TONER_MIN = 0
TONER_MAX = 100


class PrinterReadingCreate(BaseModel):
    """
    Leitura enviada por `POST /api/printers/{id}/readings`.

    Ate a Fase 10 esta rota aceitava QUALQUER conteudo: status inventado,
    contador negativo, toner em 5000%. Como as leituras alimentam o painel,
    o relatorio mensal (que subtrai contadores) e o motor de alertas, um
    unico registro invalido corrompe as tres coisas — e nao ha como
    distingui-lo de uma leitura real depois de gravado.
    """

    status: str
    page_count: int
    toner_k: int | None = None
    toner_c: int | None = None
    toner_m: int | None = None
    toner_y: int | None = None
    uptime: str | None = None

    @field_validator("status")
    @classmethod
    def _status_conhecido(cls, value: str) -> str:
        limpo = value.strip().lower()
        if limpo not in PRINTER_STATUSES:
            raise ValueError(
                f"status invalido: {value!r}. Use um de: {', '.join(PRINTER_STATUSES)}."
            )
        return limpo

    @field_validator("page_count")
    @classmethod
    def _contador_nao_negativo(cls, value: int) -> int:
        # Contador de paginas e cumulativo e so cresce. Um valor negativo
        # tornaria negativo o "paginas do mes" do relatorio, que e a
        # diferenca entre o maior e o menor contador do periodo.
        if value < 0:
            raise ValueError(f"page_count nao pode ser negativo: {value}.")
        return value

    @field_validator("toner_k", "toner_c", "toner_m", "toner_y")
    @classmethod
    def _toner_percentual(cls, value: int | None, info) -> int | None:
        if value is None:
            return None
        if not (TONER_MIN <= value <= TONER_MAX):
            raise ValueError(
                f"{info.field_name} deve estar entre {TONER_MIN} e {TONER_MAX} "
                f"(percentual); recebido {value}."
            )
        return value


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
