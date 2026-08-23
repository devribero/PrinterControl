"""
Print Server como entidade (Fase 4).

Ate aqui um Print Server existia de duas formas soltas:

  1. `settings.print_server_host` — UM host global, no .env;
  2. `Printer.server` — a string do servidor de origem, ja parte da
     identidade `(server, name)` desde a Etapa 4.

Ou seja: a identidade por servidor JA existia e o sync ja era escopado por
servidor (`sync_printers(session, server=...)` so mexe nas impressoras
daquele host). O que faltava era um registro: nao havia como saber quais
servidores existem sem varrer `printers`, nem guardar modo, rotulo ou o
resultado da ultima descoberta de cada um.

Relacao com `Printer`
---------------------
`PrintServer.host` guarda EXATAMENTE o mesmo valor de `Printer.server`. Essa
string continua sendo a chave natural: ela participa do
`UniqueConstraint("server", "name")` e e o que o sync compara. Trocar isso
por um id exigiria reconstruir a tabela `printers` inteira (SQLite nao
remove constraint) — o caminho arriscado da Etapa 4, fora do escopo desta
fase e sem ganho real.

`Printer.print_server_id` e a ligacao estruturada (FK), preenchida pela
migracao a partir do host e mantida pelo sync. As duas representacoes sao
gravadas sempre juntas, em um unico lugar (`printer_sync`), para nao
divergirem.
"""
from datetime import datetime

from sqlmodel import Field, SQLModel


class ServerMode(str):
    """Modos aceitos, iguais aos de `settings.print_server_mode`."""

    MOCK = "mock"
    REAL = "real"


VALID_MODES = ("mock", "real")

#: Estado da ultima descoberta/sync — observado, nao configurado.
STATUS_UNKNOWN = "unknown"  # nunca consultado desde o registro
STATUS_ONLINE = "online"    # ultima descoberta respondeu
STATUS_ERROR = "error"      # ultima descoberta falhou (ver last_error)


class PrintServer(SQLModel, table=True):
    __tablename__ = "print_servers"

    id: int | None = Field(default=None, primary_key=True)

    #: Host usado no `-ComputerName` do PowerShell. Mesmo valor de
    #: `Printer.server` — e por isso e unico.
    host: str = Field(unique=True, index=True)

    #: Rotulo legivel para a interface. Cai no proprio host quando vazio.
    name: str = Field(default="")

    #: "mock" ou "real", POR SERVIDOR: numa instalacao com varios servidores
    #: um pode estar em producao e outro sendo simulado. Sem isso, o modo
    #: continuaria sendo uma chave global — exatamente o que esta fase
    #: veio desfazer.
    mode: str = Field(default="mock")

    #: Desligar um servidor sem apagar o registro (mesma ideia de
    #: `Printer.active` e `User.is_active`): o historico continua, a
    #: descoberta para de rodar contra ele.
    active: bool = Field(default=True, index=True)

    last_status: str = Field(default=STATUS_UNKNOWN)
    last_error: str | None = Field(default=None)
    #: Ultima descoberta bem-sucedida.
    last_seen_at: datetime | None = Field(default=None)
    #: Ultimo sync bem-sucedido com o banco.
    last_sync_at: datetime | None = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def display_name(self) -> str:
        return self.name or self.host
