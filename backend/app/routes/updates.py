"""
GET /api/updates/version — o painel pergunta a cada poucos segundos se ha
dado novo (services/data_version.py) e so recarrega a frota quando o numero
muda. Resposta minima de proposito: e chamada o tempo todo por cada aba
aberta.
"""
from fastapi import APIRouter, Depends

from app.dependencies import require_active_user
from app.models.user import User
from app.services import data_version

router = APIRouter(prefix="/updates", tags=["updates"])


@router.get("/version")
def get_version(_user: User = Depends(require_active_user)) -> dict:
    versao, alterado_em = data_version.current()
    return {"version": versao, "changed_at": alterado_em.isoformat()}
