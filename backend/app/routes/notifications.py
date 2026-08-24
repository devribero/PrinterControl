"""
Central de notificacoes internas (Fase 7).

Caixa PESSOAL: `GET` e `PATCH` operam exclusivamente sobre as notificacoes de
quem esta logado — nao existe rota para ler a caixa de outra pessoa, nem
mesmo para admin. Admin cria comunicacoes; ler o que chegou continua sendo do
dono da conta.

Isto NAO substitui `/api/alerts`. O historico tecnico continua la, intacto:
alerta e evento de impressora, notificacao e mensagem para gente. Ver o
docstring de `app/models/notification.py` para o desenho completo.
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field, field_validator
from sqlmodel import Session, func, select

from app.database import get_session
from app.dependencies import require_active_user, require_admin
from app.models.alert import Alert
from app.models.notification import SEVERITIES, Notification
from app.models.user import User

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
    dependencies=[Depends(require_active_user)],
)


# ─────────────────────────────────────────────────────────────────────────
#  Schemas
# ─────────────────────────────────────────────────────────────────────────

class AlertRef(BaseModel):
    """
    Referencia ao alerta de origem — link, nao conteudo.

    A notificacao ja carrega a propria mensagem; isto existe so para o painel
    poder oferecer "ver o alerta" e mostrar se ele ainda esta aberto. Se o
    alerta nao existir mais, a resposta traz `alert: null` e a notificacao
    continua perfeitamente legivel.
    """

    id: int
    printer_id: int
    alert_type: str | None
    severity: str
    resolved: bool


class NotificationResponse(BaseModel):
    id: int
    message: str
    severity: str
    read_at: datetime | None
    created_at: datetime
    alert_id: int | None
    alert: AlertRef | None = None


class NotificationCreate(BaseModel):
    """Uma comunicacao para um ou mais destinatarios (uma linha por pessoa)."""

    user_ids: list[int] = Field(min_length=1)
    message: str = Field(min_length=1)
    severity: str = "info"
    alert_id: int | None = None

    @field_validator("message")
    @classmethod
    def _message_not_blank(cls, value: str) -> str:
        limpo = value.strip()
        if not limpo:
            raise ValueError("Mensagem nao pode ser vazia.")
        return limpo

    @field_validator("severity")
    @classmethod
    def _severity_valida(cls, value: str) -> str:
        if value not in SEVERITIES:
            raise ValueError(f"severidade invalida: {value!r} (use {' ou '.join(SEVERITIES)})")
        return value

    @field_validator("user_ids")
    @classmethod
    def _sem_duplicatas(cls, value: list[int]) -> list[int]:
        # Mandar o mesmo id duas vezes criaria duas linhas identicas na caixa
        # de uma pessoa so. Ordem preservada para o retorno ser previsivel.
        vistos: list[int] = []
        for uid in value:
            if uid not in vistos:
                vistos.append(uid)
        return vistos


class UnreadCount(BaseModel):
    unread: int


class ReadAllResult(BaseModel):
    #: Quantas estavam nao lidas e foram marcadas agora. 0 quando a caixa ja
    #: estava toda lida — nao e erro, e o resultado correto.
    marked: int


# ─────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────

def _to_response(session: Session, n: Notification) -> NotificationResponse:
    ref: AlertRef | None = None
    if n.alert_id is not None:
        alerta = session.get(Alert, n.alert_id)
        if alerta:
            ref = AlertRef(
                id=alerta.id,
                printer_id=alerta.printer_id,
                alert_type=alerta.alert_type,
                severity=alerta.severity,
                resolved=alerta.resolved_at is not None,
            )

    return NotificationResponse(
        id=n.id,
        message=n.message,
        severity=n.severity,
        read_at=n.read_at,
        created_at=n.created_at,
        alert_id=n.alert_id,
        alert=ref,
    )


def _minha_ou_404(session: Session, notification_id: int, user: User) -> Notification:
    """
    Busca a notificacao exigindo que ela seja do usuario logado.

    404 (e nao 403) quando pertence a outra pessoa, de proposito: um 403
    confirmaria que aquele id existe. Numa caixa pessoal a existencia da
    mensagem alheia ja e informacao — para quem nao e o dono, ela simplesmente
    nao existe.
    """
    n = session.get(Notification, notification_id)
    if not n or n.user_id != user.id:
        raise HTTPException(status_code=404, detail="Notificacao nao encontrada")
    return n


# ─────────────────────────────────────────────────────────────────────────
#  Rotas
# ─────────────────────────────────────────────────────────────────────────

@router.get("", response_model=list[NotificationResponse])
def list_notifications(
    unread_only: bool = False,
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_session),
    user: User = Depends(require_active_user),
):
    """
    Caixa do usuario logado, mais recentes primeiro.

    Nao aceita `user_id` como filtro: o destinatario e sempre quem esta
    autenticado. Sem parametro, sem chance de vazar a caixa alheia.
    """
    query = select(Notification).where(Notification.user_id == user.id)
    if unread_only:
        query = query.where(Notification.read_at == None)  # noqa: E711

    query = query.order_by(Notification.created_at.desc(), Notification.id.desc()).limit(limit)
    return [_to_response(session, n) for n in session.exec(query).all()]


@router.get("/unread-count", response_model=UnreadCount)
def unread_count(
    session: Session = Depends(get_session),
    user: User = Depends(require_active_user),
):
    """Contador para o badge do sino, sem trazer a lista inteira."""
    total = session.exec(
        select(func.count())
        .select_from(Notification)
        .where(Notification.user_id == user.id, Notification.read_at == None)  # noqa: E711
    ).one()
    return UnreadCount(unread=total)


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
def mark_as_read(
    notification_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(require_active_user),
):
    """
    Marca como lida. Idempotente: reler nao mexe no `read_at` original, para
    o instante guardado continuar sendo o da PRIMEIRA leitura.
    """
    n = _minha_ou_404(session, notification_id, user)

    if n.read_at is None:
        n.read_at = datetime.utcnow()
        session.add(n)
        session.commit()
        session.refresh(n)

    return _to_response(session, n)


@router.post("/read-all", response_model=ReadAllResult)
def mark_all_as_read(
    session: Session = Depends(get_session),
    user: User = Depends(require_active_user),
):
    """
    Marca como lidas todas as nao lidas da CAIXA DE QUEM ESTA LOGADO.

    Nao aceita destinatario: como no `GET`, o escopo vem da sessao, entao nao
    ha parametro capaz de esvaziar a caixa de outra pessoa — nem para admin.

    Um unico instante para todas: elas foram lidas no mesmo gesto, e dar
    timestamps diferentes por linha inventaria uma ordem que nao existiu.

    Idempotente: chamar de novo devolve `marked: 0` e nao reescreve nenhum
    `read_at` ja gravado, preservando o instante da primeira leitura.
    """
    pendentes = session.exec(
        select(Notification).where(
            Notification.user_id == user.id,
            Notification.read_at == None,  # noqa: E711
        )
    ).all()

    if not pendentes:
        return ReadAllResult(marked=0)

    agora = datetime.utcnow()
    for n in pendentes:
        n.read_at = agora
        session.add(n)
    session.commit()

    return ReadAllResult(marked=len(pendentes))


@router.post("", response_model=list[NotificationResponse], status_code=status.HTTP_201_CREATED)
def create_notifications(
    data: NotificationCreate,
    session: Session = Depends(get_session),
    _admin: User = Depends(require_admin),
):
    """
    Envia uma comunicacao para um ou mais destinatarios — uma linha por pessoa.

    Exige admin: escrever na caixa dos outros e acao administrativa, na mesma
    linha do resto da Fase 3.
    """
    destinatarios = session.exec(select(User).where(User.id.in_(data.user_ids))).all()
    encontrados = {u.id for u in destinatarios}
    faltando = [uid for uid in data.user_ids if uid not in encontrados]
    if faltando:
        raise HTTPException(
            status_code=404,
            detail=f"Usuario(s) nao encontrado(s): {', '.join(str(u) for u in faltando)}",
        )

    # Conta desativada nao recebe: a caixa dela nunca sera aberta, e o
    # remetente precisa saber que a mensagem nao chegou a ninguem.
    inativos = [u.id for u in destinatarios if not u.is_active]
    if inativos:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Conta(s) desativada(s) nao recebem notificacao: {', '.join(str(u) for u in inativos)}",
        )

    if data.alert_id is not None and not session.get(Alert, data.alert_id):
        raise HTTPException(status_code=404, detail="Alerta referenciado nao existe")

    criadas = [
        Notification(
            user_id=uid,
            message=data.message,
            severity=data.severity,
            alert_id=data.alert_id,
        )
        for uid in data.user_ids
    ]
    for n in criadas:
        session.add(n)
    session.commit()
    for n in criadas:
        session.refresh(n)

    return [_to_response(session, n) for n in criadas]
