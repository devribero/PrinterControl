"""
Leitura rapida do contador de paginas (22/09/2026).

A coleta completa (status, toner, bandejas, alertas) roda a cada
COLLECTION_INTERVAL_MINUTES. Entre uma e outra, este job pergunta SO o
contador de paginas as impressoras que estavam online e com contador na
ultima leitura — um GET SNMP por IP, em paralelo, timeout curto — a cada
FAST_COUNTER_INTERVAL_SECONDS. Quando o numero mudou, grava uma leitura nova
em cada fila do IP (copiando status e toner da ultima leitura, que a coleta
completa atualiza) e sobe a versao dos dados; o painel ve e recarrega.

So grava quando o contador MUDA: com 60 impressoras respondendo, gravar a
cada 30s seriam ~170 mil linhas por dia sem informacao nova nenhuma.

Nao roda junto com a coleta completa (mesma trava da frota): as duas
gravariam leitura do mesmo instante. Nao reavalia alertas — status e toner
nao mudam aqui; isso continua com a coleta completa.
"""
import logging
import re
import socket
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

from sqlmodel import Session, func, select

from app.config import settings
from app.database import engine
from app.models.printer import Printer, PrinterReading
from app.services import data_version, printer_fleet
from app.services.counter_series import ponto
from app.services.snmp import SNMPClient

logger = logging.getLogger("printercontrol.fast_counter")

_IPV4 = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")
# Leitura mais velha que isto nao conta como "estava online": a impressora
# pode ter sumido, e perguntar a ela a cada 30s so gastaria timeout.
_LEITURA_RECENTE = timedelta(hours=2)
_TIMEOUT_SNMP = 1.0
_WORKERS = 16


def _ler_contador(ip: str) -> tuple[int | None, int | None]:
    """(fabricante, padrao), lidos separadamente — ver counter_series."""
    cliente = SNMPClient(community=settings.snmp_community, timeout=_TIMEOUT_SNMP, retries=1)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(_TIMEOUT_SNMP)
    try:
        return cliente._contadores(sock, ip)
    except Exception:
        return None, None
    finally:
        sock.close()


def run_fast_counter_poll(ler_contador=_ler_contador) -> int:
    """Uma rodada. Devolve quantos equipamentos tiveram o contador alterado."""
    if settings.collection_mode != "real":
        return 0
    # Coleta completa em andamento: ela ja vai gravar o contador.
    if printer_fleet._fleet_lock.locked():
        return 0

    limite = datetime.utcnow() - _LEITURA_RECENTE
    with Session(engine) as session:
        ultimas_ids = select(func.max(PrinterReading.id)).group_by(PrinterReading.printer_id)
        linhas = session.exec(
            select(Printer, PrinterReading)
            .join(PrinterReading, PrinterReading.printer_id == Printer.id)
            .where(PrinterReading.id.in_(ultimas_ids))
            .where(Printer.active == True)  # noqa: E712
        ).all()

        por_ip: dict[str, list[tuple[Printer, PrinterReading]]] = {}
        for printer, leitura in linhas:
            if not _IPV4.match(printer.ip or ""):
                continue
            tem_contador = leitura.page_count or leitura.counter_vendor or leitura.counter_std
            if leitura.status == "offline" or not tem_contador or leitura.timestamp < limite:
                continue
            por_ip.setdefault(printer.ip, []).append((printer, leitura))
        if not por_ip:
            return 0

        with ThreadPoolExecutor(max_workers=min(_WORKERS, len(por_ip)), thread_name_prefix="fast-counter") as pool:
            lidos = dict(zip(por_ip, pool.map(ler_contador, por_ip)))

        agora = datetime.utcnow()
        alterados = 0
        for ip, filas in por_ip.items():
            fabricante, padrao = lidos.get(ip) or (None, None)
            _, ultima = max(filas, key=lambda f: f[1].id)
            anterior_fab, anterior_pad = ponto(ultima.page_count, ultima.counter_vendor, ultima.counter_std)
            # Cada contador comparado com ele mesmo. Equipamento com contador
            # do fabricante que desta vez nao o respondeu: espera a proxima
            # rodada em vez de gravar so o padrao.
            if anterior_fab and not fabricante:
                continue
            mudou = (fabricante and fabricante != anterior_fab) or (
                not fabricante and padrao and padrao != anterior_pad
            )
            if not mudou:
                continue
            alterados += 1
            exibido = fabricante or padrao
            for printer, leitura in filas:
                session.add(
                    PrinterReading(
                        printer_id=printer.id,
                        status=leitura.status,
                        page_count=exibido,
                        counter_vendor=fabricante,
                        counter_std=padrao,
                        toner_k=leitura.toner_k,
                        toner_c=leitura.toner_c,
                        toner_m=leitura.toner_m,
                        toner_y=leitura.toner_y,
                        uptime=leitura.uptime,
                        device_status=leitura.device_status,
                        printer_state=leitura.printer_state,
                        error_states=leitura.error_states,
                        timestamp=agora,
                    )
                )
        if alterados:
            session.commit()
            data_version.bump()
            logger.info("Contador atualizado | equipamentos=%s consultados=%s", alterados, len(por_ip))
        return alterados
