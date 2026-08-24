"""
Print Servers — registro (Fase 4) e descoberta/sincronizacao (Etapas 3 e 4).

Ate a Fase 3 este modulo operava sobre UM host global
(`settings.print_server_host`). A Fase 4 acrescenta o registro
`print_servers` e rotas que operam sobre um servidor especifico
(`/servers/{id}/discover` e `/servers/{id}/sync`), sem remover as rotas
antigas: `/servers/discover` e `/servers/sync` continuam funcionando sobre o
servidor padrao, que e o que o painel usa hoje.

A camada de servico ja era multi-servidor — `discover_printers(server)` e
`sync_printers(session, server=...)` sempre aceitaram o host e o sync so
mexe nas impressoras daquele servidor. O que faltava, e o que esta fase
entrega, era o registro por tras dessa string.
"""
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlmodel import Session, func, select

from app.config import settings
from app.database import get_session
from app.dependencies import require_admin, require_user
from app.models.print_server import (
    STATUS_ERROR,
    STATUS_ONLINE,
    VALID_MODES,
    PrintServer,
)
from app.models.printer import Printer
from app.services.environment_guard import bloquear_mock_em_producao
from app.models.user import User
from app.services.discovery import enrich_discovered_printers
from app.services.print_server import PrintServerError, discover_printers
from app.services.printer_sync import sync_printers

router = APIRouter(prefix="/servers", tags=["servers"])


# ─────────────────────────────────────────────────────────────────────────
#  Schemas
# ─────────────────────────────────────────────────────────────────────────

class ServerStatus(BaseModel):
    host: str
    mode: str


class PrintServerResponse(BaseModel):
    id: int
    host: str
    name: str
    mode: str
    active: bool
    last_status: str
    last_error: str | None
    last_seen_at: datetime | None
    last_sync_at: datetime | None
    created_at: datetime
    #: Impressoras associadas a este servidor (todas e so as ativas).
    printer_count: int = 0
    active_printer_count: int = 0
    #: True para o host de `PRINT_SERVER_HOST`, usado pelas rotas sem id.
    is_default: bool = False


class PrintServerCreate(BaseModel):
    host: str = Field(min_length=1)
    name: str = ""
    mode: str = "mock"

    @field_validator("host", "name")
    @classmethod
    def _trim(cls, value: str) -> str:
        return value.strip()

    @field_validator("mode")
    @classmethod
    def _mode_valido(cls, value: str) -> str:
        if value not in VALID_MODES:
            raise ValueError(f"modo invalido: {value!r} (use {' ou '.join(VALID_MODES)})")
        return value


class PrintServerUpdate(BaseModel):
    """
    `host` fica de fora de proposito: ele e a chave natural que aparece em
    `printers.server` e no UniqueConstraint (server, name). Renomea-lo aqui
    orfanaria silenciosamente todas as impressoras do servidor.
    """

    name: str | None = None
    mode: str | None = None
    active: bool | None = None

    @field_validator("mode")
    @classmethod
    def _mode_valido(cls, value: str | None) -> str | None:
        if value is not None and value not in VALID_MODES:
            raise ValueError(f"modo invalido: {value!r} (use {' ou '.join(VALID_MODES)})")
        return value


class DiscoveredPrinterResponse(BaseModel):
    name: str
    server: str
    port_name: str
    ip: str | None
    driver_name: str
    model: str | None = None
    printer_type: str | None = None
    source: Literal["print_server_real", "print_server_mock"]
    ip_resolution: Literal["resolved", "unresolved"]
    ip_group_size: int = 1
    network_query_reused: bool = False
    reachable: bool | None = None
    snmp_responded: bool = False
    status: str = "unknown"
    status_reason: str = "not_enriched"
    page_count: int | None = None
    uptime: str | None = None
    toners: list[dict] = []
    error: str | None = None


class DiscoverResponse(BaseModel):
    server: str
    mode: str
    source: Literal["print_server_real", "print_server_mock"]
    count: int
    unique_ips: int
    printers: list[DiscoveredPrinterResponse]


class SyncResponse(BaseModel):
    server: str
    discovered: int
    created: int
    updated: int
    reactivated: int
    deactivated: int


# ─────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────

def _to_response(session: Session, server: PrintServer) -> PrintServerResponse:
    """Conta as impressoras pela CHAVE NATURAL (host == printers.server).

    Contar por `print_server_id` deixaria de fora impressoras cadastradas
    antes da migracao que ainda nao passaram por um sync — a string e que
    sempre esteve la.
    """
    total = session.exec(
        select(func.count()).select_from(Printer).where(Printer.server == server.host)
    ).one()
    ativas = session.exec(
        select(func.count())
        .select_from(Printer)
        .where(Printer.server == server.host, Printer.active == True)  # noqa: E712
    ).one()

    return PrintServerResponse(
        id=server.id,
        host=server.host,
        name=server.display_name,
        mode=server.mode,
        active=server.active,
        last_status=server.last_status,
        last_error=server.last_error,
        last_seen_at=server.last_seen_at,
        last_sync_at=server.last_sync_at,
        created_at=server.created_at,
        printer_count=total,
        active_printer_count=ativas,
        is_default=server.host == settings.print_server_host,
    )


def _get_or_404(session: Session, server_id: int) -> PrintServer:
    server = session.get(PrintServer, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Print Server nao encontrado")
    return server


def _marcar_resultado(
    session: Session, server: PrintServer, *, erro: str | None, sincronizou: bool = False
) -> None:
    """Registra o desfecho da ultima descoberta/sync no proprio servidor."""
    agora = datetime.utcnow()
    if erro:
        server.last_status = STATUS_ERROR
        server.last_error = erro
    else:
        server.last_status = STATUS_ONLINE
        server.last_error = None
        server.last_seen_at = agora
        if sincronizou:
            server.last_sync_at = agora
    server.updated_at = agora
    session.add(server)
    session.commit()


def _executar_discover(server_host: str, mode: str) -> DiscoverResponse:
    """Descoberta + enriquecimento SNMP, sem tocar no banco."""
    # Ponto unico das duas rotas de discover (a global e a por servidor).
    # Discover nao grava nada, mas e o que alimenta a tela que leva ao sync:
    # deixar a frota ficticia aparecer em producao ja induz o erro seguinte.
    if mode == "mock":
        bloquear_mock_em_producao(
            "A descoberta simulada",
            f"O Print Server {server_host} esta cadastrado com mode='mock'; "
            "mude para 'real' em /network.",
        )

    found = discover_printers(server_host, mode=mode)
    enriched = enrich_discovered_printers(found, mode=mode)
    source = "print_server_real" if mode == "real" else "print_server_mock"

    return DiscoverResponse(
        server=server_host,
        mode=mode,
        source=source,
        count=len(found),
        unique_ips=len({item.ip for item in enriched if item.ip}),
        printers=[
            DiscoveredPrinterResponse(
                name=p.name,
                server=p.server,
                port_name=p.port_name,
                ip=p.ip,
                driver_name=p.driver_name,
                model=p.model,
                printer_type=p.printer_type,
                source=source,
                ip_resolution=("resolved" if p.ip else "unresolved"),
                ip_group_size=p.ip_group_size,
                network_query_reused=p.network_query_reused,
                reachable=p.reachable,
                snmp_responded=p.snmp_responded,
                status=p.status,
                status_reason=p.status_reason,
                page_count=p.page_count,
                uptime=p.uptime,
                toners=[toner.__dict__ for toner in p.toners],
                error=p.error,
            )
            for p in enriched
        ],
    )


# ─────────────────────────────────────────────────────────────────────────
#  Registro de servidores (Fase 4)
#
#  ATENCAO a ordem: rotas de caminho fixo ("/current") precisam ser
#  declaradas antes de qualquer "/{server_id}", senao "current" seria lido
#  como um id.
# ─────────────────────────────────────────────────────────────────────────

@router.get("/current", response_model=ServerStatus)
def get_current_server(_user: User = Depends(require_user)):
    """
    Print Server padrao (`PRINT_SERVER_HOST`) e o modo global.

    Mantida como estava para nao quebrar quem ja consome; a visao completa
    do parque de servidores esta em `GET /api/servers`.
    """
    return ServerStatus(host=settings.print_server_host, mode=settings.print_server_mode)


@router.get("", response_model=list[PrintServerResponse])
def list_servers(session: Session = Depends(get_session), _user: User = Depends(require_user)):
    """Servidores registrados, com a contagem de impressoras de cada um."""
    servers = session.exec(select(PrintServer).order_by(PrintServer.host)).all()
    return [_to_response(session, s) for s in servers]


@router.post("", response_model=PrintServerResponse, status_code=status.HTTP_201_CREATED)
def create_server(
    data: PrintServerCreate,
    session: Session = Depends(get_session),
    _admin: User = Depends(require_admin),
):
    """Registra um Print Server. O host e unico — e a chave natural."""
    existente = session.exec(select(PrintServer).where(PrintServer.host == data.host)).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ja existe um Print Server registrado com o host {data.host}.",
        )

    # O default de `mode` e "mock" (historico). Em producao, registrar um
    # servidor simulado e sempre engano — inclusive por omissao do campo.
    if data.mode == "mock":
        bloquear_mock_em_producao(
            "O cadastro de um Print Server simulado",
            "Informe mode='real' ao registrar o servidor.",
        )

    server = PrintServer(host=data.host, name=data.name or data.host, mode=data.mode)
    session.add(server)
    session.commit()
    session.refresh(server)

    # Impressoras que ja existiam com esta string de servidor (cadastro
    # manual ou sync anterior ao registro) passam a apontar para ele.
    orfas = session.exec(
        select(Printer).where(Printer.server == server.host, Printer.print_server_id == None)  # noqa: E711
    ).all()
    for printer in orfas:
        printer.print_server_id = server.id
        session.add(printer)
    if orfas:
        session.commit()

    return _to_response(session, server)


@router.patch("/{server_id}", response_model=PrintServerResponse)
def update_server(
    server_id: int,
    update: PrintServerUpdate,
    session: Session = Depends(get_session),
    _admin: User = Depends(require_admin),
):
    """Altera rotulo, modo e ativacao. `host` nao muda (ver PrintServerUpdate)."""
    server = _get_or_404(session, server_id)

    data = update.model_dump(exclude_unset=True)
    if data.get("mode") == "mock":
        bloquear_mock_em_producao(
            "Mudar um Print Server para o modo simulado",
            f"{server.host} tem impressoras reais associadas ao cadastro.",
        )

    for field, value in data.items():
        if value is not None:
            setattr(server, field, value)

    server.updated_at = datetime.utcnow()
    session.add(server)
    session.commit()
    session.refresh(server)
    return _to_response(session, server)


# ─────────────────────────────────────────────────────────────────────────
#  Descoberta e sincronizacao
# ─────────────────────────────────────────────────────────────────────────

@router.post("/discover", response_model=DiscoverResponse)
def discover(_user: User = Depends(require_admin)):
    """
    Descobre as impressoras do servidor PADRAO (equivalente a Get-Printer +
    Get-PrinterPort do Main.ps1). Nao grava nada no banco.

    Continua existindo para nao quebrar o painel; para escolher o servidor,
    use `POST /api/servers/{id}/discover`.
    """
    try:
        return _executar_discover(settings.print_server_host, settings.print_server_mode)
    except PrintServerError as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@router.post("/sync", response_model=SyncResponse)
def sync(session: Session = Depends(get_session), _user: User = Depends(require_admin)):
    """
    Descobre e sincroniza o servidor PADRAO com o banco (Etapa 4): cria as
    novas, atualiza as existentes, marca como inativas as que sumiram.
    Nunca apaga — leituras e alertas sao preservados.
    """
    if settings.print_server_mode == "mock":
        bloquear_mock_em_producao(
            "A sincronizacao simulada",
            "Ela desativaria as impressoras reais ausentes da frota ficticia.",
        )

    try:
        result = sync_printers(session)
    except PrintServerError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    return SyncResponse(**result.__dict__)


@router.post("/{server_id}/discover", response_model=DiscoverResponse)
def discover_server(
    server_id: int,
    session: Session = Depends(get_session),
    _admin: User = Depends(require_admin),
):
    """Descoberta de UM servidor registrado, no modo configurado nele."""
    server = _get_or_404(session, server_id)
    if not server.active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Print Server {server.host} esta desativado.",
        )

    try:
        resposta = _executar_discover(server.host, server.mode)
    except PrintServerError as exc:
        _marcar_resultado(session, server, erro=str(exc))
        raise HTTPException(status_code=502, detail=str(exc))

    _marcar_resultado(session, server, erro=None)
    return resposta


@router.post("/{server_id}/sync", response_model=SyncResponse)
def sync_server(
    server_id: int,
    session: Session = Depends(get_session),
    _admin: User = Depends(require_admin),
):
    """
    Sincroniza UM servidor registrado. O escopo por servidor ja era garantido
    pelo `printer_sync` desde a Etapa 4: impressoras de outros servidores nao
    sao tocadas nem desativadas.
    """
    server = _get_or_404(session, server_id)
    if not server.active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Print Server {server.host} esta desativado.",
        )

    # O caso critico desta fase: o modo vive na LINHA do servidor, gravado
    # antes de a instancia virar producao, entao nenhuma validacao de boot o
    # enxerga. Sincronizar aqui publicaria a frota ficticia e marcaria como
    # inativa toda impressora real que ela nao contem.
    if server.mode == "mock":
        bloquear_mock_em_producao(
            "A sincronizacao simulada",
            f"O Print Server {server.host} esta cadastrado com mode='mock'; "
            "ela desativaria as impressoras reais ausentes da frota ficticia.",
        )

    try:
        result = sync_printers(session, server=server.host, mode=server.mode)
    except PrintServerError as exc:
        _marcar_resultado(session, server, erro=str(exc))
        raise HTTPException(status_code=502, detail=str(exc))

    _marcar_resultado(session, server, erro=None, sincronizou=True)
    return SyncResponse(**result.__dict__)
