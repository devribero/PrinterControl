"""
Levantamento mensal em Excel (22/09/2026) — ver services/levantamento.py.

    GET  /api/levantamento                  estado: base, meses, arquivos gerados
    POST /api/levantamento/gerar            {mes: "2026-09"} -> relatorio (admin)
    GET  /api/levantamento/arquivos/{nome}  download de um arquivo da lista
    GET  /api/levantamento/relatorio/{nome} relatorio guardado de um arquivo gerado
    POST /api/levantamento/base             upload de uma nova planilha base (admin)

Leitura e download para qualquer sessao ativa; gerar e trocar a base exigem
admin e ficam na trilha de auditoria. O download so aceita um nome que esteja
na lista registrada — nunca um caminho (ver arquivo_para_download).
"""
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.database import get_session
from app.dependencies import require_active_user, require_admin
from app.models.user import User
from app.services import audit_log, levantamento

router = APIRouter(
    prefix="/levantamento",
    tags=["levantamento"],
    dependencies=[Depends(require_active_user)],
)

XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class GerarRequest(BaseModel):
    mes: str = Field(pattern=r"^\d{4}-\d{2}$", description="Mes a gerar, AAAA-MM (ex.: 2026-09)")


def _mes_id(mes: str) -> int:
    """'2026-09' -> 202609: id numerico para a trilha de auditoria."""
    return int(mes.replace("-", ""))


@router.get("")
def get_estado(_user: User = Depends(require_active_user)) -> dict:
    return levantamento.estado()


@router.post("/gerar")
def gerar(
    body: GerarRequest,
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin),
) -> dict:
    try:
        relatorio = levantamento.gerar(session, body.mes)
    except levantamento.LevantamentoError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from None
    audit_log.record(
        session, admin, "levantamento.generate", "levantamento", _mes_id(body.mes),
        after={
            "arquivo": relatorio["arquivo"],
            "previa": relatorio["previa"],
            "preenchidas": relatorio["preenchidas"],
            "vazias": len(relatorio["vazias"]),
            "novos": len(relatorio["novos"]),
            "base_atualizada": relatorio["base_atualizada"],
        },
    )
    session.commit()
    return relatorio


@router.get("/arquivos/{nome}")
def baixar(nome: str, _user: User = Depends(require_active_user)) -> FileResponse:
    try:
        caminho = levantamento.arquivo_para_download(nome)
    except levantamento.LevantamentoError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None
    return FileResponse(caminho, media_type=XLSX_MIME, filename=caminho.name)


@router.get("/relatorio/{nome}")
def relatorio(nome: str, _user: User = Depends(require_active_user)) -> dict:
    try:
        levantamento.arquivo_para_download(nome)
    except levantamento.LevantamentoError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None
    dados = levantamento.relatorio_do_arquivo(nome)
    if dados is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Este arquivo nao tem relatorio de geracao.")
    return dados


@router.post("/base")
async def enviar_base(
    arquivo: UploadFile = File(...),
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin),
) -> dict:
    nome = arquivo.filename or ""
    if not nome.lower().endswith(".xlsx"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Envie a planilha em formato .xlsx.")
    dados = await arquivo.read(levantamento.TAMANHO_MAXIMO_BASE + 1)
    try:
        resultado = levantamento.substituir_base(dados, nome_original=nome, origem="upload")
    except levantamento.LevantamentoError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from None
    audit_log.record(
        session, admin, "levantamento.upload_base", "levantamento", 0,
        after={"nome_original": nome, "tamanho": len(dados), **resultado},
    )
    session.commit()
    return resultado
