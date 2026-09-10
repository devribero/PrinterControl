"""Diagnostico administrativo real do Print Server, independente do mock."""
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.dependencies import rate_limited_action
from app.models.user import User
from app.services.print_server import diagnose_print_server

router = APIRouter(tags=["servers"])


@router.get("/health/print-server")
def print_server_health(_admin: User = Depends(rate_limited_action("print_server_health"))):
    """Get-Printer real sem sync; whoami descreve o processo, nao o usuario da API."""
    result = diagnose_print_server()
    return JSONResponse(status_code=200 if result["success"] else 503, content=result)
