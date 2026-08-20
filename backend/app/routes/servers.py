"""
Print Server (Etapa 3) — descoberta pura, sem tocar no banco.

Sincronizar o resultado da descoberta com a tabela `printers` e a Etapa 4;
aqui a rota so expoe o que o Print Server (real ou mock) devolveria.
"""
from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from app.database import get_session
from app.dependencies import require_user
from app.models.user import User
from app.services.print_server import PrintServerError, discover_printers
from app.services.printer_sync import sync_printers
from app.config import settings

router = APIRouter(prefix="/servers", tags=["servers"])


class ServerStatus(BaseModel):
    host: str
    mode: str


class DiscoveredPrinterResponse(BaseModel):
    name: str
    server: str
    port_name: str
    ip: str
    driver_name: str


class DiscoverResponse(BaseModel):
    server: str
    mode: str
    count: int
    printers: list[DiscoveredPrinterResponse]


class SyncResponse(BaseModel):
    server: str
    discovered: int
    created: int
    updated: int
    reactivated: int
    deactivated: int


@router.get("/current", response_model=ServerStatus)
def get_current_server():
    """Print Server configurado e modo ativo (mock ou real)."""
    return ServerStatus(host=settings.print_server_host, mode=settings.print_server_mode)


@router.post("/discover", response_model=DiscoverResponse)
def discover(_user: User = Depends(require_user)):
    """
    Descobre as impressoras publicadas no Print Server configurado
    (equivalente a Get-Printer + Get-PrinterPort do Main.ps1).

    Nao grava nada no banco — apenas retorna o que foi encontrado.
    """
    try:
        found = discover_printers()
    except PrintServerError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    return DiscoverResponse(
        server=settings.print_server_host,
        mode=settings.print_server_mode,
        count=len(found),
        printers=[DiscoveredPrinterResponse(**asdict(p)) for p in found],
    )


@router.post("/sync", response_model=SyncResponse)
def sync(session: Session = Depends(get_session), _user: User = Depends(require_user)):
    """
    Descobre e sincroniza com o banco (Etapa 4): cria impressoras novas,
    atualiza as existentes, marca como inativas as que sumiram do servidor.
    Nunca apaga — leituras e alertas de impressoras inativas sao preservados.
    """
    try:
        result = sync_printers(session)
    except PrintServerError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    return SyncResponse(
        server=result.server,
        discovered=result.discovered,
        created=result.created,
        updated=result.updated,
        reactivated=result.reactivated,
        deactivated=result.deactivated,
    )
