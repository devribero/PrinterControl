"""
Notificacoes internas (Fase 7).

Por que uma tabela separada de `alerts`
---------------------------------------
Um Alert e um EVENTO TECNICO sobre uma impressora: nasce do
`alert_engine.evaluate_reading`, e deduplicado por (printer_id, alert_type),
tem no maximo uma instancia ativa por condicao e se resolve sozinho quando a
condicao some. Ninguem "le" um alerta — ele esta aberto ou fechado.

Uma Notification e uma COMUNICACAO DIRIGIDA A UMA PESSOA: tem destinatario,
tem status de leitura individual e nao se resolve sozinha. A mesma
comunicacao pode ir para varias pessoas, e cada uma le a sua no seu tempo.

Sao ciclos de vida diferentes. Guardar os dois na mesma tabela obrigaria
`alerts.user_id` nulo na maioria das linhas e `notifications.printer_id` nulo
na maioria das outras — o classico registro que e duas coisas pela metade.

Como o vinculo com Alert evita acoplamento
------------------------------------------
`alert_id` e uma FK OPCIONAL, e a notificacao carrega a propria `message`
(instantaneo do momento em que foi criada), em vez de renderizar texto lendo
o alerta. Isso significa que:

  - uma notificacao pode existir sem alerta nenhum (aviso administrativo);
  - resolver, escalar ou reavaliar o alerta NAO altera o que a pessoa leu;
  - se o alerta sumir, a notificacao continua legivel — a referencia vira
    apenas `null` na resposta da API.

O alerta e citado, nunca consultado para montar o conteudo. A leitura do
alerta atual acontece so para oferecer o link/estado ao painel.

Um destinatario por linha
-------------------------
"Varios destinatarios" e resolvido por fan-out: uma comunicacao para tres
pessoas vira tres linhas. E o que torna `read_at` individual — que e o ponto
da tabela. Agrupar os destinatarios numa linha so exigiria uma tabela de
juncao para guardar a leitura de cada um, sem ganho nenhum nesta escala.
"""
from datetime import datetime

from sqlmodel import Field, SQLModel

#: Mesmo vocabulario de `Alert.severity`, de proposito: quando a notificacao
#: nasce de um alerta o valor e copiado tal e qual, e o painel usa uma unica
#: escala visual para as duas coisas.
SEVERITIES = ("info", "warning", "critical")


class Notification(SQLModel, table=True):
    __tablename__ = "notifications"

    id: int | None = Field(default=None, primary_key=True)

    #: Destinatario. Indexado porque TODA consulta desta tabela filtra por ele
    #: — a caixa e sempre pessoal, nunca global.
    user_id: int = Field(foreign_key="users.id", index=True)

    #: Texto ja pronto para exibicao, gravado no momento da criacao. E um
    #: instantaneo: nao se atualiza se o alerta de origem mudar depois.
    message: str

    severity: str = Field(default="info")

    #: Alerta que originou a comunicacao, quando houver. Nulo na maioria dos
    #: casos (avisos administrativos, mensagens de sistema).
    alert_id: int | None = Field(default=None, foreign_key="alerts.id", index=True)

    #: Nulo = nao lida. Guardar o INSTANTE da leitura em vez de um booleano
    #: custa o mesmo e responde "quando" alem de "se".
    read_at: datetime | None = Field(default=None, index=True)

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    @property
    def is_read(self) -> bool:
        return self.read_at is not None
