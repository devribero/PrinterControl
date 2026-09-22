"""
Resolucao de unidade e roteamento de notificacoes (21/09/2026).

Ponto unico que responde "de que unidade e esta impressora?" e "quem deve
ser avisado?". Tanto o motor de alertas quanto o disparo manual
(POST /api/alerts/{id}/notify) passam por aqui, para as regras nao
divergirem. Ver models/unit.py para o desenho.

Regras:
  - Impressora -> unidade: `Printer.server` == `PrintServer.host` ->
    `PrintServer.unit_id`. Sem servidor registrado ou servidor sem unidade =
    impressora sem unidade.
  - Webhook: unidade ativa com URL propria recebe, alem da central. A
    deduplicacao por URL fica em webhook_notifier.
  - Sino: usuarios ativos sem unidade (central/TI) + os da unidade da
    impressora. Impressora sem unidade avisa todos os ativos, como antes.
"""
from sqlmodel import Session, select

from app.models.print_server import PrintServer
from app.models.printer import Printer
from app.models.unit import Unit
from app.models.user import User
from app.schemas.user import UserResponse


def unit_for_printer(session: Session, printer: Printer | None) -> Unit | None:
    """Unidade da impressora (via Print Server), ou None."""
    if printer is None or not printer.server:
        return None
    unit_id = session.exec(
        select(PrintServer.unit_id).where(PrintServer.host == printer.server)
    ).first()
    if unit_id is None:
        return None
    return session.get(Unit, unit_id)


def unit_webhook_url(unit: Unit | None) -> str:
    """URL do webhook da unidade, ou "" quando nao deve receber (sem URL/inativa)."""
    if unit is None or not unit.active:
        return ""
    return (unit.webhook_url or "").strip()


def notification_recipients(session: Session, unit: Unit | None) -> list[User]:
    """
    Usuarios ativos que recebem no sino um alerta de impressora da `unit`.

    Sem unidade -> todos os ativos. Com unidade -> central (unit_id NULL) +
    quem e da propria unidade. Unidade inativa continua roteando o sino: ela
    so perde o webhook proprio.
    """
    query = select(User).where(User.is_active == True)  # noqa: E712
    if unit is not None:
        query = query.where((User.unit_id == None) | (User.unit_id == unit.id))  # noqa: E711
    return list(session.exec(query).all())


def unit_name(session: Session, unit_id: int | None) -> str | None:
    """Nome da unidade pelo id, ou None."""
    if unit_id is None:
        return None
    unit = session.get(Unit, unit_id)
    return unit.name if unit else None


def user_response(session: Session, user: User) -> UserResponse:
    """UserResponse com o nome da unidade preenchido."""
    resposta = UserResponse.model_validate(user)
    resposta.unit_name = unit_name(session, user.unit_id)
    return resposta
