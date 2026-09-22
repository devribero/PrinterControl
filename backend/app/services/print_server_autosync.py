"""
Sincronizacao automatica dos Print Servers registrados (22/09/2026).

Antes, cadastrar um servidor nao trazia impressora nenhuma: o card ficava
em "0 ativa(s) de 0 cadastrada(s) · Ultimo sync: nunca" ate alguem abrir a
tela, clicar Descobrir, esperar (ate 1 minuto nos servidores de outras
unidades) e depois Sincronizar. Com varios servidores, metade ficava
esquecida assim.

Agora o proprio backend sincroniza:
  - logo depois do cadastro (ou de virar mode='real'), em segundo plano;
  - na subida, so os servidores que estao sem sync ha mais de
    PRINT_SERVER_SYNC_HOURS (com --reload o backend reinicia a cada arquivo
    salvo; sem esse filtro cada reinicio consultaria todos os servidores);
  - a cada PRINT_SERVER_SYNC_HOURS horas.

Seguranca: so servidores ativos com mode='real'. A descoberta simulada
nunca e aplicada sobre o banco por aqui (mesma preocupacao do docstring do
scheduler). E o sync continua com a trava de queda brusca do printer_sync:
uma descoberta que devolve bem menos filas que o cadastro nao desativa nada.

Uma trava por host impede dois syncs do MESMO servidor ao mesmo tempo (o
automatico e o botao), que criariam a mesma fila duas vezes.
"""
import logging
import threading
from datetime import datetime, timedelta

from sqlmodel import Session, select

from app.config import settings
from app.database import engine
from app.models.print_server import STATUS_ERROR, STATUS_ONLINE, PrintServer
from app.services import data_version
from app.services.print_server import PrintServerError
from app.services.printer_sync import SyncResult, sync_printers

logger = logging.getLogger("printercontrol.autosync")

_travas: dict[str, threading.Lock] = {}
_travas_guarda = threading.Lock()


class SyncEmAndamento(Exception):
    """Ja existe um sync deste servidor rodando."""


def _trava(host: str) -> threading.Lock:
    with _travas_guarda:
        return _travas.setdefault(host.lower(), threading.Lock())


def marcar_resultado(
    session: Session, server: PrintServer, *, erro: str | None, sincronizou: bool = False
) -> None:
    """Registra o desfecho da ultima descoberta/sync no proprio servidor."""
    agora = datetime.utcnow()
    if erro:
        server.last_status = STATUS_ERROR
        server.last_error = erro
    else:
        server.last_status = STATUS_ONLINE
        server.last_error = None
        server.last_seen_at = agora
        if sincronizou:
            server.last_sync_at = agora
    server.updated_at = agora
    session.add(server)
    session.commit()


def sincronizar_servidor(
    session: Session, server: PrintServer, *, usar_portas_conhecidas: bool = False
) -> SyncResult:
    """
    Sync de um servidor registrado, com a trava por host e o registro do
    desfecho. Levanta SyncEmAndamento se outro sync dele estiver rodando e
    PrintServerError se a descoberta falhar (ja registrado no servidor).
    """
    trava = _trava(server.host)
    if not trava.acquire(blocking=False):
        raise SyncEmAndamento(server.host)
    try:
        try:
            resultado = sync_printers(
                session, server=server.host, mode=server.mode,
                usar_portas_conhecidas=usar_portas_conhecidas,
            )
        except PrintServerError as exc:
            marcar_resultado(session, server, erro=f"[{exc.category}] {exc}")
            raise
        marcar_resultado(session, server, erro=None, sincronizou=True)
        data_version.bump()
        return resultado
    finally:
        trava.release()


def _sincronizar_por_id(server_id: int, motivo: str) -> None:
    with Session(engine) as session:
        server = session.get(PrintServer, server_id)
        if not server or not server.active or server.mode != "real":
            return
        inicio = datetime.utcnow()
        try:
            r = sincronizar_servidor(session, server)
        except SyncEmAndamento:
            logger.info("Sync automatico pulado | server=%s motivo=%s (ja em andamento)", server.host, motivo)
        except PrintServerError as exc:
            logger.warning(
                "Sync automatico falhou | server=%s motivo=%s categoria=%s erro=%s",
                server.host, motivo, exc.category, exc,
            )
        except Exception:
            # Um servidor quebrado nao pode derrubar a rodada dos outros.
            logger.exception("Sync automatico com erro inesperado | server=%s motivo=%s", server.host, motivo)
        else:
            logger.info(
                "Sync automatico concluido | server=%s motivo=%s filas=%s criadas=%s atualizadas=%s "
                "reativadas=%s desativadas=%s duracao=%ss",
                server.host, motivo, r.discovered, r.created, r.updated, r.reactivated, r.deactivated,
                round((datetime.utcnow() - inicio).total_seconds(), 1),
            )


def sincronizar_em_segundo_plano(server_id: int, motivo: str) -> None:
    """Dispara o sync de um servidor sem segurar a requisicao que pediu."""
    threading.Thread(
        target=_sincronizar_por_id, args=(server_id, motivo),
        name=f"autosync-{server_id}", daemon=True,
    ).start()


def run_auto_sync(somente_atrasados: bool = True) -> int:
    """
    Sincroniza os servidores reais ativos, um de cada vez. Com
    `somente_atrasados`, pula quem sincronizou ha menos de
    PRINT_SERVER_SYNC_HOURS. Devolve quantos foram tentados.
    """
    horas = settings.print_server_sync_hours
    limite = datetime.utcnow() - timedelta(hours=horas) if horas > 0 else None
    with Session(engine) as session:
        servidores = session.exec(
            select(PrintServer)
            .where(PrintServer.active == True, PrintServer.mode == "real")  # noqa: E712
            .order_by(PrintServer.id)
        ).all()
        alvos = [
            s.id for s in servidores
            if not somente_atrasados or limite is None or s.last_sync_at is None or s.last_sync_at < limite
        ]
    if alvos:
        logger.info("Sync automatico dos Print Servers | servidores=%s", len(alvos))
    for server_id in alvos:
        _sincronizar_por_id(server_id, "agendado")
    return len(alvos)
