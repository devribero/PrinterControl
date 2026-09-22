"""
Unidade (21/09/2026): agrupamento de Print Servers e usuarios por local
(ex.: "Manaus", "Vila Olimpia").

A unidade NAO restringe acesso — todo mundo continua vendo todos os
servidores e impressoras. Ela so decide duas coisas:

  1. o filtro padrao do painel (feito no frontend, a partir de
     `User.unit_id`);
  2. o roteamento de notificacoes: o alerta de toner vai para o webhook da
     unidade da impressora (alem do webhook central de `settings.webhook_url`)
     e o sino so avisa quem e da unidade da impressora ou da central (usuario
     sem unidade). Ver services/units.py.

Ligacoes:
  - `PrintServer.unit_id` -> uma unidade tem 1+ servidores; cada servidor
    pertence a no maximo uma.
  - `User.unit_id` -> no maximo uma por usuario, definida SO por admin.
  - A impressora nao tem coluna propria: a unidade dela e a do Print Server
    cujo `host` casa com `Printer.server` (mesma chave natural de sempre).

`webhook_url` carrega assinatura (Teams/Power Automate). Nunca sai em
resposta da API nem em log — so o host, como em webhook_notifier._safe_host.
"""
from datetime import datetime

from sqlmodel import Field, SQLModel

#: Tamanho maximo do nome da unidade.
UNIT_NAME_MAX = 80


class Unit(SQLModel, table=True):
    __tablename__ = "units"

    id: int | None = Field(default=None, primary_key=True)
    #: Unico (a checagem sem diferenciar maiusculas fica na rota).
    name: str = Field(unique=True, index=True, max_length=UNIT_NAME_MAX)
    #: Vazio = unidade sem webhook proprio (alertas vao so para a central).
    webhook_url: str = Field(default="")
    #: Unidade inativa nao recebe webhook (alertas vao so para a central).
    active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
