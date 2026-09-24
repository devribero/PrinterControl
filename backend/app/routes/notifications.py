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
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlmodel import Session, func, select

from app.database import get_session
from app.dependencies import rate_limited_action, require_active_user, require_admin
from app.models.alert import Alert
from app.models.email_recipient import EmailRecipient
from app.models.notification import SEVERITIES, Notification
from app.models.unit import Unit
from app.models.user import User
from app.schemas.common import RecursoId
from app.services import audit_log, email_notifier
from app.services.webhook_notifier import send_test_webhook

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


class WebhookTestResult(BaseModel):
    """Desfecho do envio ao webhook. Nunca carrega a URL (tem assinatura)."""

    configured: bool
    sent: bool
    # "enviado", "nao_configurado", "http_<status>", "timeout", "erro_de_rede"
    detail: str


class TestAlertResult(BaseModel):
    notification: "NotificationResponse"
    webhook: WebhookTestResult


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
    notification_id: RecursoId,
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


@router.post("/test", response_model=TestAlertResult, status_code=status.HTTP_201_CREATED)
def send_test_alert(
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin),
):
    """
    Botao "Testar alerta" da aba Notificacoes: confere os dois canais de
    aviso de uma vez, sem esperar uma impressora cair.

      1. Notificacao critica na caixa de QUEM CLICOU — so dele: mandar para
         todos a cada teste encheria a caixa dos colegas.
      2. Card de teste no webhook (Teams/Power Automate), marcado como TESTE
         no titulo e no texto para ninguem no canal confundir com toner real.

    Os dois desfechos voltam separados: a notificacao e gravada mesmo que o
    webhook falhe, e a tela diz o que chegou e o que nao chegou. Nada e
    criado em /alerts — nao ha impressora nem alerta real por tras.

    Exige admin, como qualquer envio para a caixa (POST /notifications).
    """
    hora = datetime.now().strftime("%H:%M")
    notificacao = Notification(
        user_id=admin.id,
        message=(
            f"Alerta de teste enviado as {hora}. Se ele apareceu aqui e no contador "
            "do cabecalho, as notificacoes estao funcionando."
        ),
        severity="critical",
    )
    session.add(notificacao)
    session.commit()
    session.refresh(notificacao)

    enviado, motivo = send_test_webhook(requested_by=f"{admin.name} ({admin.email})")

    return TestAlertResult(
        notification=_to_response(session, notificacao),
        webhook=WebhookTestResult(configured=motivo != "nao_configurado", sent=enviado, detail=motivo),
    )


# ─────────────────────────────────────────────────────────────────────────
#  E-mail (24/09/2026)
# ─────────────────────────────────────────────────────────────────────────

class EmailStatus(BaseModel):
    """Situacao do e-mail para a tela de Configuracoes. Nunca traz a senha."""

    configured: bool
    smtp_host: str
    sender: str
    #: Listas fixas do backend/.env — so leitura no painel.
    env_alert_recipients: list[str]
    env_report_recipients: list[str]


class EmailRecipientCreate(BaseModel):
    email: EmailStr
    kind: Literal["alert", "report"]
    #: So para kind="alert". None = recebe alertas de todas as impressoras.
    unit_id: int | None = None


class EmailRecipientResponse(BaseModel):
    id: int
    email: str
    kind: str
    unit_id: int | None
    unit_name: str | None
    created_at: datetime


def _recipient_response(session: Session, r: EmailRecipient) -> EmailRecipientResponse:
    unidade = session.get(Unit, r.unit_id) if r.unit_id else None
    return EmailRecipientResponse(
        id=r.id, email=r.email, kind=r.kind, unit_id=r.unit_id,
        unit_name=unidade.name if unidade else None, created_at=r.created_at,
    )


def _recipient_snapshot(session: Session, r: EmailRecipient) -> dict:
    return {"email": r.email, "kind": r.kind, "unit_id": r.unit_id,
            "unit_name": _recipient_response(session, r).unit_name}


class EmailTestRequest(BaseModel):
    #: Vazio = o e-mail de quem clicou.
    to: str | None = Field(default=None, max_length=254)

    @field_validator("to")
    @classmethod
    def _endereco(cls, value: str | None) -> str | None:
        if value is None or not value.strip():
            return None
        limpo = value.strip()
        # Validacao simples de proposito: o SMTP e quem da a palavra final, e
        # o objetivo aqui e so recusar lixo e injecao de cabecalho.
        if "@" not in limpo or any(c in limpo for c in "\r\n,; <>"):
            raise ValueError("Informe um unico endereco de e-mail valido.")
        return limpo


class EmailTestResult(BaseModel):
    configured: bool
    sent: bool
    # "enviado", "nao_configurado", "autenticacao", "recusado", "timeout", "erro_de_rede"
    detail: str
    to: str


@router.get("/email-status", response_model=EmailStatus)
def get_email_status(_admin: User = Depends(require_admin)):
    """Se o SMTP esta configurado e quantos destinatarios cada lista tem."""
    return EmailStatus(**email_notifier.status())


@router.post("/test-email", response_model=EmailTestResult)
def send_test_email(
    data: EmailTestRequest | None = None,
    admin: User = Depends(rate_limited_action("test_email")),
):
    """
    Envia um e-mail de TESTE e devolve o que aconteceu, para quem esta
    configurando o SMTP ver na hora se deu certo (e por que nao).

    Limitado como as acoes de rede: e um disparo real de e-mail, e um laco
    no botao nao pode transformar o sistema em fonte de spam.
    """
    destino = (data.to if data and data.to else admin.email)
    enviado, motivo = email_notifier.send_test_email(destino, requested_by=f"{admin.name} ({admin.email})")
    return EmailTestResult(configured=motivo != "nao_configurado", sent=enviado, detail=motivo, to=destino)


@router.get("/email-recipients", response_model=list[EmailRecipientResponse])
def list_email_recipients(
    session: Session = Depends(get_session),
    _admin: User = Depends(require_admin),
):
    """Destinatarios cadastrados pelo painel (alerta e relatorio)."""
    itens = session.exec(select(EmailRecipient).order_by(EmailRecipient.kind, EmailRecipient.email)).all()
    return [_recipient_response(session, r) for r in itens]


@router.post("/email-recipients", response_model=EmailRecipientResponse, status_code=status.HTTP_201_CREATED)
def add_email_recipient(
    data: EmailRecipientCreate,
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin),
):
    """
    Adiciona um destinatario. Mesmo endereco pode estar nas duas listas, e
    em unidades diferentes; so nao pode repetir no mesmo lugar (409).
    """
    email = str(data.email).strip().lower()
    unit_id = data.unit_id if data.kind == "alert" else None
    if data.kind == "report" and data.unit_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O relatorio mensal e um so para a empresa: nao escolha unidade.",
        )
    if unit_id is not None and session.get(Unit, unit_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unidade nao encontrada")

    filtro_unidade = EmailRecipient.unit_id.is_(None) if unit_id is None else EmailRecipient.unit_id == unit_id
    existente = session.exec(
        select(EmailRecipient).where(
            EmailRecipient.email == email, EmailRecipient.kind == data.kind, filtro_unidade
        )
    ).first()
    if existente:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{email} ja esta nesta lista.")

    r = EmailRecipient(email=email, kind=data.kind, unit_id=unit_id)
    session.add(r)
    session.flush()
    audit_log.record(session, admin, "email_recipient.create", "email_recipient", r.id,
                     after=_recipient_snapshot(session, r))
    session.commit()
    session.refresh(r)
    return _recipient_response(session, r)


@router.delete("/email-recipients/{recipient_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_email_recipient(
    recipient_id: RecursoId,
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin),
):
    """Remove um destinatario cadastrado pelo painel (os do .env nao passam por aqui)."""
    r = session.get(EmailRecipient, recipient_id)
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Destinatario nao encontrado")
    audit_log.record(session, admin, "email_recipient.delete", "email_recipient", r.id,
                     before=_recipient_snapshot(session, r))
    session.delete(r)
    session.commit()
