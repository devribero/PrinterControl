"""
Unidades (21/09/2026) — agrupam Print Servers e usuarios por local e
definem para onde vao os avisos. Ver models/unit.py para o desenho.

Leitura para qualquer sessao ativa (o painel precisa dos nomes para o
filtro); criar, alterar, excluir e testar o webhook exigem admin.

A URL do webhook NUNCA sai daqui: a resposta traz so `webhook_configured` e
`webhook_host`. A URL carrega a assinatura do Teams/Power Automate — quem a
tem posta no canal. Pelo mesmo motivo ela nao entra na trilha de auditoria
(so o host e o fato de ter mudado).
"""
from datetime import datetime

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlmodel import Session, func, select

from app.config import settings
from app.database import get_session
from app.dependencies import require_active_user, require_admin
from app.models.email_recipient import EmailRecipient
from app.models.print_server import PrintServer
from app.models.unit import UNIT_NAME_MAX, Unit
from app.models.user import User
from app.schemas.common import RecursoId
from app.services import audit_log
from app.services.webhook_notifier import _safe_host, send_unit_test_webhook

router = APIRouter(
    prefix="/units",
    tags=["units"],
    dependencies=[Depends(require_active_user)],
)


# ─────────────────────────────────────────────────────────────────────────
#  Schemas
# ─────────────────────────────────────────────────────────────────────────

def _limpar_nome(value: str) -> str:
    limpo = " ".join(value.split())
    if not limpo:
        raise ValueError("Nome da unidade nao pode ser vazio.")
    if len(limpo) > UNIT_NAME_MAX:
        raise ValueError(f"Nome da unidade deve ter no maximo {UNIT_NAME_MAX} caracteres.")
    return limpo


def _validar_webhook(value: str) -> str:
    """"" limpa; qualquer outro valor precisa ser https:// com host."""
    limpo = value.strip()
    if not limpo:
        return ""
    try:
        url = httpx.URL(limpo)
    except Exception:
        raise ValueError("URL do webhook invalida.") from None
    if url.scheme != "https" or not url.host:
        # Mensagem sem ecoar o valor: ele pode ser a URL com assinatura.
        raise ValueError("URL do webhook deve comecar com https://")
    if not settings.webhook_host_permitido(url.host):
        # Protege contra SSRF: sem isto o backend postava em qualquer host
        # https, inclusive servicos internos da rede. Ver WEBHOOK_ALLOWED_HOSTS.
        raise ValueError(
            "Dominio do webhook nao permitido. Use um webhook do Teams ou do "
            "Power Automate, ou peca para incluir o dominio em WEBHOOK_ALLOWED_HOSTS."
        )
    return limpo


class UnitCreate(BaseModel):
    name: str
    webhook_url: str = ""

    @field_validator("name")
    @classmethod
    def _nome(cls, value: str) -> str:
        return _limpar_nome(value)

    @field_validator("webhook_url")
    @classmethod
    def _webhook(cls, value: str) -> str:
        return _validar_webhook(value)


class UnitUpdate(BaseModel):
    """Todos opcionais. `webhook_url` omitido = mantem; "" = limpa."""

    name: str | None = None
    webhook_url: str | None = None
    active: bool | None = None

    @field_validator("name")
    @classmethod
    def _nome(cls, value: str | None) -> str | None:
        return None if value is None else _limpar_nome(value)

    @field_validator("webhook_url")
    @classmethod
    def _webhook(cls, value: str | None) -> str | None:
        return None if value is None else _validar_webhook(value)


class UnitResponse(BaseModel):
    """Unidade exposta pela API. Nunca carrega a URL do webhook."""

    id: int
    name: str
    active: bool
    webhook_configured: bool
    #: So o host da URL ("" sem webhook) — para o admin reconhecer o destino.
    webhook_host: str
    server_hosts: list[str]
    server_count: int
    user_count: int
    created_at: datetime


class UnitWebhookTestResult(BaseModel):
    """Mesmo formato do `webhook` de POST /api/notifications/test."""

    sent: bool
    configured: bool
    # "enviado", "nao_configurado", "http_<status>", "timeout", "erro_de_rede"
    detail: str


# ─────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────

def _webhook_host(unit: Unit) -> str:
    return _safe_host(unit.webhook_url) if unit.webhook_url else ""


def _to_response(session: Session, unit: Unit) -> UnitResponse:
    hosts = session.exec(
        select(PrintServer.host).where(PrintServer.unit_id == unit.id).order_by(PrintServer.host)
    ).all()
    usuarios = session.exec(
        select(func.count()).select_from(User).where(User.unit_id == unit.id)
    ).one()
    return UnitResponse(
        id=unit.id,
        name=unit.name,
        active=unit.active,
        webhook_configured=bool(unit.webhook_url),
        webhook_host=_webhook_host(unit),
        server_hosts=list(hosts),
        server_count=len(hosts),
        user_count=usuarios,
        created_at=unit.created_at,
    )


def _snapshot(unit: Unit) -> dict:
    """Campos seguros para a auditoria — a URL do webhook NUNCA entra."""
    return {"name": unit.name, "active": unit.active, "webhook_host": _webhook_host(unit)}


def _get_or_404(session: Session, unit_id: int) -> Unit:
    unit = session.get(Unit, unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unidade nao encontrada")
    return unit


def _nome_em_uso(session: Session, nome: str, ignorar_id: int | None = None) -> bool:
    """
    Compara sem diferenciar maiusculas em Python (casefold), e nao com
    lower() do SQLite, que so conhece ASCII — "VILA OLÍMPIA" e "Vila
    Olímpia" passariam como nomes diferentes. Sao poucas unidades.
    """
    alvo = nome.casefold()
    for unit_id, existente in session.exec(select(Unit.id, Unit.name)).all():
        if unit_id != ignorar_id and existente.casefold() == alvo:
            return True
    return False


def _conflito_nome(nome: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"Ja existe uma unidade chamada {nome}.",
    )


# ─────────────────────────────────────────────────────────────────────────
#  Rotas
# ─────────────────────────────────────────────────────────────────────────

@router.get("", response_model=list[UnitResponse])
def list_units(session: Session = Depends(get_session)):
    """Todas as unidades, por nome."""
    unidades = session.exec(select(Unit).order_by(Unit.name)).all()
    return [_to_response(session, u) for u in unidades]


@router.post("", response_model=UnitResponse, status_code=status.HTTP_201_CREATED)
def create_unit(
    data: UnitCreate,
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin),
):
    """Cria uma unidade. Nome unico, sem diferenciar maiusculas."""
    if _nome_em_uso(session, data.name):
        raise _conflito_nome(data.name)

    unit = Unit(name=data.name, webhook_url=data.webhook_url)
    session.add(unit)
    session.flush()  # atribui o id sem commitar, para o registro de auditoria abaixo
    audit_log.record(session, admin, "unit.create", "unit", unit.id, after=_snapshot(unit))
    session.commit()
    session.refresh(unit)
    return _to_response(session, unit)


@router.patch("/{unit_id}", response_model=UnitResponse)
def update_unit(
    unit_id: RecursoId,
    update: UnitUpdate,
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin),
):
    """Altera nome, webhook e/ou ativacao."""
    unit = _get_or_404(session, unit_id)
    before = _snapshot(unit)
    data = update.model_dump(exclude_unset=True)

    if data.get("name") is not None:
        if _nome_em_uso(session, data["name"], ignorar_id=unit.id):
            raise _conflito_nome(data["name"])
        unit.name = data["name"]

    webhook_alterado = False
    if data.get("webhook_url") is not None and data["webhook_url"] != unit.webhook_url:
        unit.webhook_url = data["webhook_url"]
        webhook_alterado = True

    if data.get("active") is not None:
        unit.active = data["active"]

    session.add(unit)
    after = _snapshot(unit)
    if webhook_alterado:
        # O host pode ser o mesmo com outra assinatura: registra o fato.
        after["webhook"] = "webhook alterado"
    audit_log.record(session, admin, "unit.update", "unit", unit.id, before=before, after=after)
    session.commit()
    session.refresh(unit)
    return _to_response(session, unit)


@router.delete("/{unit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_unit(
    unit_id: RecursoId,
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin),
):
    """
    Exclui a unidade. Servidores e usuarios dela ficam sem unidade
    (unit_id = NULL) — nada alem do vinculo e apagado.
    """
    unit = _get_or_404(session, unit_id)

    servidores = session.exec(select(PrintServer).where(PrintServer.unit_id == unit.id)).all()
    for server in servidores:
        server.unit_id = None
        session.add(server)
    usuarios = session.exec(select(User).where(User.unit_id == unit.id)).all()
    for usuario in usuarios:
        usuario.unit_id = None
        session.add(usuario)

    # E-mails de alerta da unidade saem junto. Ficar sem unidade (NULL) os
    # promoveria a destinatarios de TODAS as impressoras — o contrario do
    # que quem os cadastrou pediu.
    destinatarios = session.exec(select(EmailRecipient).where(EmailRecipient.unit_id == unit.id)).all()
    for destinatario in destinatarios:
        session.delete(destinatario)

    before = _snapshot(unit)
    before["server_count"] = len(servidores)
    before["user_count"] = len(usuarios)
    before["email_recipient_count"] = len(destinatarios)
    audit_log.record(session, admin, "unit.delete", "unit", unit.id, before=before)
    session.delete(unit)
    session.commit()


@router.post("/{unit_id}/test-webhook", response_model=UnitWebhookTestResult)
def test_unit_webhook(
    unit_id: RecursoId,
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin),
):
    """
    Envia um card de TESTE so para o webhook desta unidade (a central nao
    recebe). Funciona mesmo com a unidade inativa, para o admin conferir o
    canal antes de ativa-la. Mesmo desfecho do teste da aba Notificacoes.
    """
    unit = _get_or_404(session, unit_id)
    enviado, motivo = send_unit_test_webhook(
        unit_name=unit.name,
        url=unit.webhook_url,
        requested_by=f"{admin.name} ({admin.email})",
    )
    return UnitWebhookTestResult(sent=enviado, configured=motivo != "nao_configurado", detail=motivo)
