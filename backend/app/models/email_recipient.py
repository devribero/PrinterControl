"""
Destinatarios de e-mail cadastrados pelo painel (24/09/2026).

Antes as listas so existiam no backend/.env (ALERT_EMAIL_TO, REPORT_EMAIL_TO),
e mudar quem recebe exigia acesso ao servidor. Agora um admin gerencia em
Configuracoes > Notificacoes. As listas do .env continuam valendo e SOMAM a
estas (services/email_notifier.py) — nada que ja funcionava deixa de receber.

  kind="alert"  -> alerta de toner critico. `unit_id` None = recebe de TODAS
                   as impressoras; com unidade = so das impressoras dela.
  kind="report" -> relatorio mensal com a planilha. Sem unidade (o
                   levantamento e um so para a empresa inteira).
"""
from datetime import datetime

from sqlmodel import Field, SQLModel

KINDS = ("alert", "report")


class EmailRecipient(SQLModel, table=True):
    __tablename__ = "email_recipients"

    id: int | None = Field(default=None, primary_key=True)
    #: Sempre minusculo (normalizado na rota) — a duplicidade e checada assim.
    email: str = Field(index=True, max_length=254)
    kind: str = Field(index=True)
    unit_id: int | None = Field(default=None, foreign_key="units.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
