"""
Sincronizacao Print Server -> banco (Etapa 4).

    Print Server -> discover_printers() -> normalizar (modelo, tipo)
                  -> comparar com o banco -> criar / atualizar / desativar

O banco e cache/historico, NAO origem: a identidade de cada impressora e
(server, name), nunca o IP — varias impressoras podem compartilhar IP (o
mock ja inclui um caso assim, e o Main.ps1 trata isso no agrupamento).

Impressora que sumiu do Print Server nunca e apagada: fica active=False,
preservando leituras e alertas associados.
"""
from dataclasses import dataclass
from datetime import datetime

from sqlmodel import Session, select

from app.config import settings
from app.models.print_server import PrintServer
from app.models.printer import Printer
from app.services.print_server import discover_printers
from app.services.printer_rules import obter_modelo, obter_tipo_impressora


@dataclass
class SyncResult:
    server: str
    discovered: int
    created: int
    updated: int
    reactivated: int
    deactivated: int


def sync_printers(
    session: Session, server: str | None = None, mode: str | None = None
) -> SyncResult:
    """
    Executa um ciclo completo de sincronizacao para UM Print Server.

    Ja era escopado por servidor desde a Etapa 4 (so mexe nas impressoras
    daquele host). A Fase 4 acrescenta duas coisas: `mode` opcional, para o
    servidor registrado ditar seu proprio modo, e o preenchimento da FK
    `print_server_id` junto com a string `server` — as duas representacoes
    do mesmo servidor sao gravadas SEMPRE aqui, no mesmo lugar, para nao
    divergirem.

    Levanta PrintServerError (de print_server.py) se a descoberta falhar —
    o chamador decide como responder (a rota traduz em 502). Nada e alterado
    no banco quando a descoberta falha, porque a excecao interrompe antes do
    primeiro `session.add`.
    """
    server = server or settings.print_server_host
    discovered = discover_printers(server, mode=mode)
    now = datetime.utcnow()

    # Id do registro deste host, quando existir. Nao criamos o PrintServer
    # aqui: quem registra servidor e a rota administrativa/migracao — o sync
    # apenas liga as impressoras ao registro que ja existe.
    registro = session.exec(select(PrintServer).where(PrintServer.host == server)).first()
    print_server_id = registro.id if registro else None

    # So considera impressoras JA associadas a este servidor — sincronizar
    # elgjunprt nao pode desativar impressoras de outro servidor.
    existing = {
        (p.server, p.name): p
        for p in session.exec(select(Printer).where(Printer.server == server))
    }

    seen_keys: set[tuple[str, str]] = set()
    created = updated = reactivated = 0

    for d in discovered:
        key = (d.server, d.name)
        seen_keys.add(key)

        modelo = obter_modelo(d.driver_name)
        tipo = obter_tipo_impressora(d.name, modelo)

        printer = existing.get(key)
        if printer is None:
            printer = Printer(
                server=d.server,
                print_server_id=print_server_id,
                name=d.name,
                ip=d.ip,
                port_name=d.port_name,
                driver_name=d.driver_name,
                model=modelo,
                printer_type=tipo,
                department="",
                active=True,
                last_seen_at=now,
            )
            session.add(printer)
            created += 1
            continue

        if not printer.active:
            reactivated += 1

        printer.print_server_id = print_server_id
        printer.ip = d.ip
        printer.port_name = d.port_name
        printer.driver_name = d.driver_name
        printer.model = modelo
        printer.printer_type = tipo
        printer.active = True
        printer.last_seen_at = now
        printer.updated_at = now
        session.add(printer)
        updated += 1

    deactivated = 0
    for key, printer in existing.items():
        if key not in seen_keys and printer.active:
            printer.active = False
            printer.updated_at = now
            session.add(printer)
            deactivated += 1

    session.commit()

    return SyncResult(
        server=server,
        discovered=len(discovered),
        created=created,
        updated=updated,
        reactivated=reactivated,
        deactivated=deactivated,
    )
