import logging
import re

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, func, select
from app.database import get_session
from pydantic import BaseModel

from app.dependencies import rate_limited_action, require_active_user, require_admin, require_operator
from app.models.user import User
from datetime import datetime, timedelta

from app.models.printer import Printer, PrinterMonthly, PrinterReading
from app.config import settings
from app.services.alert_engine import evaluate_reading
from app.services.printer_collector import PrinterCollector
from app.services.snmp import SNMPClient
from app.services import audit_log, data_version
from app.services.test_print import TestPageInfo, build_test_page, is_supported as is_test_print_supported, send_raw
from app.services.environment_guard import bloquear_mock_em_producao
from app.services.monthly_report import (
    device_monthly_history,
    filas_com_o_mesmo_serial,
    month_bounds,
    month_label,
    month_pages,
    month_period,
)
from app.schemas.printer import (
    TONER_LABELS,
    PrinterCreate,
    PrinterUpdate,
    PrinterResponse,
    PrinterReadingCreate,
    PrinterWithStatus,
    TonerLevel,
)
from typing import List
from app.schemas.common import RecursoId

logger = logging.getLogger("printercontrol.printers")

# Fase 2: TODA rota de impressoras exige sessao. A dependencia fica no
# router para que nenhuma rota nova nasca publica por esquecimento; as rotas
# de escrita continuam declarando o papel exigido (require_admin/operator),
# que roda alem desta.
router = APIRouter(
    prefix="/printers",
    tags=["printers"],
    dependencies=[Depends(require_active_user)],
)


# Teto das listagens (Fase 10). A frota real tem ~85 impressoras, entao o
# limite nao corta nada hoje; ele existe para que a resposta continue
# limitada se a frota crescer ou se alguem pedir `?limit=` absurdo. `offset`
# acompanha para que uma frota maior que o teto ainda seja alcancavel por
# paginas, em vez de simplesmente sumir.
LIMITE_PADRAO_FROTA = 500
LIMITE_MAXIMO_FROTA = 500


@router.get("", response_model=List[PrinterResponse])
def list_printers(
    limit: int = Query(default=LIMITE_PADRAO_FROTA, ge=1, le=LIMITE_MAXIMO_FROTA),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session),
):
    printers = session.exec(
        select(Printer).order_by(Printer.id).offset(offset).limit(limit)
    ).all()
    return printers


def _inicio_da_janela(months: int) -> datetime:
    """Primeiro instante do mes que abre uma janela de `months` meses ate hoje."""
    hoje = datetime.utcnow()
    total = (hoje.year * 12 + (hoje.month - 1)) - (months - 1)
    ano, mes = divmod(total, 12)
    return datetime(ano, mes + 1, 1)


# Precisa vir antes de /{printer_id}, senao "with-status" e lido como id.
@router.get("/with-status", response_model=List[PrinterWithStatus])
def list_printers_with_status(
    limit: int = Query(default=LIMITE_PADRAO_FROTA, ge=1, le=LIMITE_MAXIMO_FROTA),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session),
):
    """
    Impressoras + ultima leitura de cada uma, em uma unica chamada.

    E o que o painel consome: sem isto o frontend precisaria de 1 request
    por impressora. Sem leitura registrada, a impressora vem como "offline"
    com last_seen nulo.
    """
    printers = session.exec(
        select(Printer).order_by(Printer.id).offset(offset).limit(limit)
    ).all()

    # Ultima leitura das impressoras DESTA pagina (id maior = mais recente).
    #
    # Fase 15: o filtro por printer_id sozinho nao bastava — ele limita QUAIS
    # impressoras entram, mas nao QUANTAS leituras de cada uma. A tabela
    # cresce a cada ciclo de coleta, para sempre; num banco com meses de
    # historico isso significa trazer o historico INTEIRO das impressoras da
    # pagina so para descartar quase tudo em Python (setdefault). Sob carga
    # concorrente (~20 usuarios simultaneos) isso vira gargalo real: o SQL em
    # si e rapido, mas o ORM monta um objeto por linha e o Pydantic serializa
    # tudo, tudo isso preso ao GIL — 20 requisicoes concorrentes enfileiram
    # esse trabalho em vez de paralelizar. Confirmado com teste de carga:
    # p95 caiu de ~8s para a casa de dezenas de ms depois desta mudanca.
    #
    # A subquery MAX(id) GROUP BY printer_id faz o SQL decidir qual e a
    # ultima leitura de cada impressora; a query externa busca so essas
    # linhas — no maximo uma por impressora da pagina, nunca o historico.
    ids_pagina = [p.id for p in printers]
    latest: dict[int, PrinterReading] = {}
    if ids_pagina:
        ultimos_ids = (
            select(func.max(PrinterReading.id))
            .where(PrinterReading.printer_id.in_(ids_pagina))
            .group_by(PrinterReading.printer_id)
        )
        for reading in session.exec(
            select(PrinterReading).where(PrinterReading.id.in_(ultimos_ids))
        ):
            latest[reading.printer_id] = reading

    result = []
    for printer in printers:
        reading = latest.get(printer.id)
        toner = None
        if reading:
            levels = [
                TonerLevel(color=color, label=TONER_LABELS[color], percent=value)
                for color, value in (
                    ("K", reading.toner_k),
                    ("C", reading.toner_c),
                    ("M", reading.toner_m),
                    ("Y", reading.toner_y),
                )
                if value is not None
            ]
            toner = levels or None

        result.append(
            PrinterWithStatus(
                **PrinterResponse.model_validate(printer).model_dump(),
                status=reading.status if reading else "offline",
                page_count=reading.page_count if reading else 0,
                toner=toner,
                last_seen=reading.timestamp.isoformat() if reading else None,
                uptime=reading.uptime if reading else None,
                device_status=reading.device_status if reading else None,
                printer_state=reading.printer_state if reading else None,
                error_states=reading.error_states.split(",") if reading and reading.error_states else [],
            )
        )

    return result


@router.get("/monthly-report")
def monthly_report(
    # Janela em meses (Fase 10). Esta rota lia a tabela INTEIRA de leituras a
    # cada chamada — e a tabela cresce a cada ciclo de coleta, sem fim: com
    # 85 impressoras a cada 5 minutos sao ~7,3 milhoes de linhas por ano,
    # todas carregadas em memoria para montar um relatorio que na pratica
    # mostra os ultimos 12 meses. A janela e o limite equivalente ao `limit`
    # das outras leituras; o intervalo maximo (60) existe para que nem um
    # pedido explicito de "tudo" derrube o processo.
    months: int = Query(default=12, ge=1, le=60),
    session: Session = Depends(get_session),
):
    """
    Contagem mensal por impressora, por mes e por departamento.

    Fase 12: mes ja FECHADO (existe em PrinterMonthly — importado de
    planilha historica ou congelado pelo fechamento automatico do
    scheduler no ultimo dia do mes) usa o numero oficial gravado la. O mes
    EM ANDAMENTO (o mes atual, que ainda ninguem fechou) e calculado ao
    vivo a partir de PrinterReading, como sempre foi: maior contador do mes
    menos o menor, o incremento REALMENTE observado. PrinterMonthly tem
    prioridade quando os dois existirem para o mesmo (impressora, mes) —
    nao deveria acontecer no uso normal, mas evita numero duplicado/errado
    se um fechamento manual for reaplicado sobre um mes que a coleta ao
    vivo tambem ve.

    Sem nenhum dos dois, devolve listas vazias e o painel segue exibindo o
    relatorio de demonstracao (sinalizado no cabecalho).

    `months` recorta quantos meses para tras entram na conta (padrao 12).
    """
    inicio = _inicio_da_janela(months)
    printers = {p.id: p for p in session.exec(select(Printer))}

    # (printer_id, period) -> paginas. PrinterMonthly primeiro (autoridade),
    # depois o mes em andamento so preenche o que ainda nao esta la.
    por_impressora_periodo: dict[tuple[int, str], int] = {}
    # Parte estimada de cada mes (dias sem coleta no comeco do mes, pela
    # media diaria — ver monthly_report.month_pages). O painel mostra isso
    # ao lado do total para ninguem ler estimativa como medicao.
    estimado_por_periodo: dict[str, int] = {}

    fechados = session.exec(
        select(PrinterMonthly).where(PrinterMonthly.month_start >= inicio)
    ).all()
    for row in fechados:
        por_impressora_periodo[(row.printer_id, row.month)] = row.pages_printed
        if row.estimated_pages:
            estimado_por_periodo[row.month] = estimado_por_periodo.get(row.month, 0) + row.estimated_pages

    hoje = datetime.utcnow()
    periodo_atual = month_period(hoje)
    if periodo_atual >= month_period(inicio):
        mes_ini, mes_fim = month_bounds(hoje)
        mes_atual = month_pages(session, mes_ini, mes_fim)
        for printer_id, pages in mes_atual.pages.items():
            if (printer_id, periodo_atual) in por_impressora_periodo:
                continue
            por_impressora_periodo[(printer_id, periodo_atual)] = pages
            estimado = mes_atual.estimated.get(printer_id, 0)
            if estimado:
                estimado_por_periodo[periodo_atual] = estimado_por_periodo.get(periodo_atual, 0) + estimado

    if not por_impressora_periodo:
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "monthly_usage": [],
            "printers": [],
            "department_usage": [],
        }

    per_printer: dict[int, list[dict]] = {}
    per_month: dict[str, int] = {}
    # Uma entrada por impressora e periodo ja e uma por EQUIPAMENTO: o mes
    # ao vivo so traz a fila representante, e o fechamento grava so ela.
    equipamentos_por_periodo: dict[str, int] = {}
    # departamento -> periodo -> paginas
    per_department: dict[str, dict[str, int]] = {}

    for (printer_id, period), pages in sorted(por_impressora_periodo.items(), key=lambda kv: kv[0][1]):
        printer = printers.get(printer_id)
        if not printer:
            continue
        per_printer.setdefault(printer_id, []).append(
            {"month": month_label(period), "pages": pages, "period": period}
        )
        per_month[period] = per_month.get(period, 0) + pages
        equipamentos_por_periodo[period] = equipamentos_por_periodo.get(period, 0) + 1

        departamento = printer.department or "Sem departamento"
        per_department.setdefault(departamento, {})
        per_department[departamento][period] = per_department[departamento].get(period, 0) + pages

    # Equipamento que mudou de IP: o historico da planilha ficou no cadastro
    # INATIVO do IP antigo. O grafico da impressora atual (mesmo serie lido
    # por SNMP) mostra esses meses tambem. So o `printers` do payload muda —
    # os totais acima ja contam cada mes uma vez, e cadastro inativo nao
    # aparece no painel, entao nada e somado em dobro.
    for printer_id in list(per_printer):
        printer = printers.get(printer_id)
        if not printer or not printer.active:
            continue
        meses = {m["period"] for m in per_printer[printer_id]}
        for outro in filas_com_o_mesmo_serial(session, printer, somente_inativas=True):
            for m in per_printer.get(outro, []):
                if m["period"] not in meses:
                    per_printer[printer_id].append(dict(m))
                    meses.add(m["period"])
        per_printer[printer_id].sort(key=lambda m: m["period"])

    department_usage = [
        {
            "department": departamento,
            "monthly": [
                {"month": month_label(period), "pages": pages, "period": period}
                for period, pages in sorted(periodos.items())
            ],
            "total": sum(periodos.values()),
        }
        for departamento, periodos in per_department.items()
    ]
    department_usage.sort(key=lambda d: -d["total"])

    return {
        "generated_at": datetime.utcnow().isoformat(),
        "monthly_usage": [
            {
                "month": month_label(period),
                "pages": pages,
                "period": period,
                # Quanto de `pages` e estimativa; 0 = medido de ponta a ponta.
                "estimated": estimado_por_periodo.get(period, 0),
                # Mes ainda em andamento: o total cresce ate o fechamento.
                "in_progress": period == periodo_atual,
                # Equipamentos com dado no mes. Comparar meses so faz sentido
                # com cobertura parecida: em set/2026 a coleta ao vivo ainda
                # nao alcancava unidades inteiras que a planilha de agosto tinha.
                "devices": equipamentos_por_periodo.get(period, 0),
            }
            for period, pages in sorted(per_month.items())
        ],
        "printers": [
            {
                # QA-03: identidade estavel. O frontend casava o relatorio
                # com a frota POR IP, e desde a Etapa 4 duas filas do mesmo
                # Print Server podem dividir um IP — a segunda sobrescrevia
                # a primeira no mapa e as duas passavam a exibir o total da
                # ultima. `ip` continua no payload porque o relatorio de
                # demonstracao (data/printers.ts) so tem IP.
                "id": pid,
                "ip": printers[pid].ip,
                "name": printers[pid].name,
                "department": printers[pid].department,
                "monthly_pages": months,
            }
            for pid, months in per_printer.items()
        ],
        "department_usage": department_usage,
    }


@router.get("/{printer_id}", response_model=PrinterResponse)
def get_printer(printer_id: RecursoId, session: Session = Depends(get_session)):
    printer = session.get(Printer, printer_id)
    if not printer:
        raise HTTPException(status_code=404, detail="Impressora não encontrada")
    return printer


@router.post("", response_model=PrinterResponse)
def create_printer(
    printer_data: PrinterCreate,
    session: Session = Depends(get_session),
    _user: User = Depends(require_admin),
):
    # Etapa 4: identidade e (server, name) — IP pode repetir (varias
    # impressoras no mesmo Print Server compartilham porta/endereco).
    server = printer_data.server or ""
    existing = session.exec(
        select(Printer).where(Printer.server == server, Printer.name == printer_data.name)
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Já existe uma impressora '{printer_data.name}' no servidor '{server or '(nenhum)'}'.",
        )

    printer = Printer(**printer_data.model_dump(exclude={"server"}), server=server)
    session.add(printer)
    session.commit()
    session.refresh(printer)
    return printer


@router.patch("/{printer_id}", response_model=PrinterResponse)
def update_printer(
    printer_id: RecursoId,
    printer_data: PrinterUpdate,
    session: Session = Depends(get_session),
    _user: User = Depends(require_admin),
):
    printer = session.get(Printer, printer_id)
    if not printer:
        raise HTTPException(status_code=404, detail="Impressora não encontrada")

    update_data = printer_data.model_dump(exclude_unset=True)

    # Etapa 4: IP nao e mais identidade — so o par (server, name) precisa
    # continuar unico se o nome for alterado.
    novo_nome = update_data.get("name")
    if novo_nome and novo_nome != printer.name:
        em_uso = session.exec(
            select(Printer).where(Printer.server == printer.server, Printer.name == novo_nome)
        ).first()
        if em_uso:
            raise HTTPException(
                status_code=400,
                detail=f"Já existe uma impressora '{novo_nome}' no servidor '{printer.server or '(nenhum)'}'.",
            )

    for field, value in update_data.items():
        setattr(printer, field, value)
    printer.updated_at = datetime.utcnow()

    session.add(printer)
    session.commit()
    session.refresh(printer)
    return printer


@router.get("/{printer_id}/readings")
def get_printer_readings(
    printer_id: RecursoId,
    # Teto explicito (Fase 10): sem ele, `?limit=99999999` carregava o
    # historico inteiro da impressora em memoria e no JSON de resposta.
    # Mesmo padrao ja usado em /api/notifications.
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_session),
):
    # QA-16: 404 quando a impressora nao existe, em vez de 200 com lista
    # vazia. Sem isto, "impressora inexistente" e "impressora sem historico"
    # davam a MESMA resposta — um id errado no painel aparecia como uma
    # impressora real que nunca foi coletada.
    if not session.get(Printer, printer_id):
        raise HTTPException(status_code=404, detail="Impressora não encontrada")

    readings = session.exec(
        select(PrinterReading)
        .where(PrinterReading.printer_id == printer_id)
        .order_by(PrinterReading.timestamp.desc())
        .limit(limit)
    ).all()
    return readings


@router.post("/{printer_id}/readings")
def create_printer_reading(
    printer_id: RecursoId,
    reading_data: PrinterReadingCreate,
    session: Session = Depends(get_session),
    _user: User = Depends(require_operator),
):
    """
    Grava uma leitura A MAO. Bloqueada em ENVIRONMENT=production.

    Esta rota era a porta dos fundos da Fase 9: `/api/collect` recusa
    simulacao em producao, mas quem tivesse um token de operator podia
    gravar exatamente a mesma leitura ficticia por aqui, sem passar por
    nenhuma guarda. Em producao a origem legitima de leitura e sempre a
    coleta (SNMP, manual ou agendada), que escreve pelo PrinterCollector;
    o painel so LE deste endpoint. Nada real e perdido ao fecha-lo.
    """
    bloquear_mock_em_producao(
        "A gravacao manual de leitura",
        "Em producao as leituras vem da coleta (POST /api/collect/printers/{id}).",
    )

    printer = session.get(Printer, printer_id)
    if not printer:
        raise HTTPException(status_code=404, detail="Impressora não encontrada")

    reading = PrinterReading(
        printer_id=printer_id,
        status=reading_data.status,
        page_count=reading_data.page_count,
        toner_k=reading_data.toner_k,
        toner_c=reading_data.toner_c,
        toner_m=reading_data.toner_m,
        toner_y=reading_data.toner_y,
        uptime=reading_data.uptime,
    )
    session.add(reading)

    # QA-11: a mesma avaliacao que a coleta aplica. Ate aqui esta rota
    # gravava a leitura e parava — uma leitura offline com toner em 1%
    # entrava no banco, aparecia no painel e nao abria alerta nenhum, ao
    # contrario da leitura identica vinda da coleta. Como este e o caminho
    # usado para montar cenarios em demo/desenvolvimento, a diferenca fazia
    # a tela de alertas mentir justamente onde ela e demonstrada.
    #
    # flush + evaluate_reading, mesmo desenho do PrinterCollector: um unico
    # commit no final de evaluate_reading, leitura e alertas juntos.
    session.flush()
    session.refresh(reading)
    evaluate_reading(session, printer_id, reading)
    session.refresh(reading)
    return reading


class TestPrintResponse(BaseModel):
    printer_id: int
    ip: str
    sent: bool
    # "enviado", "porta_fechada", "sem_resposta", "erro_de_rede"
    detail: str


_COLORIDA_RE = re.compile(r"colou?r|\bc\d{3,4}\b|\d{3,4}c(dn|dw|dnw|i|idn|fdw)?\b|\b(mp|im|mc) c", re.IGNORECASE)


def _e_colorida(printer: Printer, leitura: PrinterReading | None) -> bool:
    """
    Colorida pela LEITURA (tem toner ciano/magenta/amarelo) e, sem leitura de
    toner, pelo modelo ("M6530cdn", "IM C3000", "Color LaserJet").
    """
    if leitura and any(v is not None for v in (leitura.toner_c, leitura.toner_m, leitura.toner_y)):
        return True
    campos = " ".join(c for c in (printer.snmp_model, printer.model, printer.driver_name) if c)
    return bool(_COLORIDA_RE.search(campos))


def _replicar_leitura_nas_filas_do_ip(session: Session, printer: Printer) -> None:
    """
    Copia a leitura ao vivo recem-gravada para as outras filas ativas do
    mesmo IP — o mesmo equipamento, o mesmo contador. E o que a coleta da
    frota ja faz (le uma vez por IP, grava em cada fila).

    Sem isto, a leitura ao vivo so existia na fila em que se imprimiu; se
    outra fila do IP tivesse mais historico no mes, era ELA que representava
    o equipamento no relatorio (monthly_report._one_per_device) e a leitura
    nova ficava invisivel ate a proxima coleta agendada. Nao reavalia
    alertas nas copias: a coleta agendada faz isso para todas as filas.
    """
    leitura = session.exec(
        select(PrinterReading).where(PrinterReading.printer_id == printer.id).order_by(PrinterReading.id.desc())
    ).first()
    if not leitura or (datetime.utcnow() - leitura.timestamp) > timedelta(minutes=1):
        return
    irmas = session.exec(
        select(Printer).where(Printer.ip == printer.ip).where(Printer.id != printer.id).where(Printer.active == True)  # noqa: E712
    ).all()
    for irma in irmas:
        session.add(
            PrinterReading(
                printer_id=irma.id,
                status=leitura.status,
                page_count=leitura.page_count,
                toner_k=leitura.toner_k,
                toner_c=leitura.toner_c,
                toner_m=leitura.toner_m,
                toner_y=leitura.toner_y,
                uptime=leitura.uptime,
                device_status=leitura.device_status,
                printer_state=leitura.printer_state,
                error_states=leitura.error_states,
                timestamp=leitura.timestamp,
            )
        )
    if irmas:
        session.commit()


@router.post("/{printer_id}/test-print", response_model=TestPrintResponse)
def test_print(
    printer_id: RecursoId,
    session: Session = Depends(get_session),
    user: User = Depends(rate_limited_action("test_print", require=require_operator)),
):
    """
    Envia uma pagina de teste PCL direto ao IP da impressora (porta 9100).

    So laser — etiquetadora recebe 422, porque PCL nela imprime lixo (ver
    services/test_print.py, onde mora a regra e o porque de nao ir pela fila
    do print server). Operador pode disparar; o limite por usuario e o mesmo
    das outras acoes de rede, e cada disparo fica na trilha de auditoria —
    imprimir gasta papel num lugar fisico, entao "quem mandou" importa.

    `sent=True` quer dizer que o equipamento aceitou os dados na porta RAW;
    nao ha como saber, por este caminho, se o papel de fato saiu.
    """
    printer = session.get(Printer, printer_id)
    if not printer:
        raise HTTPException(status_code=404, detail="Impressora não encontrada")
    if not printer.active:
        raise HTTPException(status_code=409, detail="Impressora inativa: ela sumiu do Print Server no último sync.")
    if not is_test_print_supported(
        ip=printer.ip,
        name=printer.name,
        model=printer.model,
        driver_name=printer.driver_name,
        printer_type=printer.printer_type,
        snmp_model=printer.snmp_model,
        snmp_description=printer.snmp_description,
    ):
        raise HTTPException(
            status_code=422,
            detail=(
                "Impressão de teste disponível só para impressoras laser (PCL). "
                "Esta parece ser uma etiquetadora ou um modelo não reconhecido."
            ),
        )

    # Leitura AO VIVO antes de montar a folha (21/09/2026). A coleta agendada
    # roda a cada 5 minutos; sem isto, varias folhas seguidas saiam todas com
    # o mesmo contador e o mesmo total do mes, porque nenhuma coleta tinha
    # passado entre elas. A leitura e gravada como qualquer outra, entao o
    # relatorio mensal tambem fica em dia. So em coleta real: em modo
    # simulado ela gravaria contador inventado no banco. Nunca impede a folha
    # — se a impressora nao responder ao SNMP, vale a ultima leitura boa.
    if settings.collection_mode == "real":
        try:
            PrinterCollector(mode="real").collect_and_save(printer.id, session)
            _replicar_leitura_nas_filas_do_ip(session, printer)
            data_version.bump()
        except Exception:
            logger.exception("Leitura ao vivo antes da pagina de teste falhou (printer_id=%s)", printer.id)

    ultima = session.exec(
        select(PrinterReading).where(PrinterReading.printer_id == printer.id).order_by(PrinterReading.id.desc())
    ).first()
    # Contador e toner da ultima leitura COM contador: uma leitura em que o
    # SNMP nao respondeu nao pode zerar a folha.
    ultima_valida = session.exec(
        select(PrinterReading)
        .where(PrinterReading.printer_id == printer.id)
        .where(PrinterReading.page_count > 0)
        .order_by(PrinterReading.id.desc())
    ).first() or ultima
    toner = None
    if ultima_valida:
        toner = [
            (TONER_LABELS[cor], valor)
            for cor, valor in (
                ("K", ultima_valida.toner_k),
                ("C", ultima_valida.toner_c),
                ("M", ultima_valida.toner_m),
                ("Y", ultima_valida.toner_y),
            )
            if valor is not None
        ]
    # Sem nivel: pergunta a impressora por que, para a folha explicar em vez
    # de so dizer "nao informado" (cartucho nao original, nivel sem numero).
    toner_note = None
    if not toner and settings.collection_mode == "real":
        try:
            toner_note = SNMPClient(
                community=settings.snmp_community,
                timeout=settings.snmp_timeout,
                retries=settings.snmp_retries,
            ).diagnostico_toner(printer.ip)
        except Exception:
            logger.exception("Diagnostico de toner falhou (printer_id=%s)", printer.id)
    documento = build_test_page(
        TestPageInfo(
            printer_name=printer.name,
            ip=printer.ip,
            requested_by=f"{user.name} ({user.email})",
            # O que o equipamento diz ser (SNMP) vale mais que o derivado do driver.
            model=printer.snmp_model or printer.model,
            serial=printer.serial_number,
            department=printer.department,
            location=printer.snmp_location,
            server=printer.server,
            share_name=printer.share_name or printer.name,
            driver=printer.driver_name,
            status=ultima.status if ultima else None,
            page_count=ultima_valida.page_count if ultima_valida else None,
            toner=toner or None,
            toner_note=toner_note,
            colorida=_e_colorida(printer, ultima_valida),
            # timestamp e UTC ingenuo; a folha mostra a hora local de Brasilia.
            last_reading=(ultima_valida.timestamp - timedelta(hours=3)) if ultima_valida else None,
            # Mesmo historico do relatorio mensal, do equipamento inteiro.
            monthly=device_monthly_history(session, printer.id) or None,
        )
    )
    resultado = send_raw(printer.ip, documento)

    audit_log.record(
        session,
        user,
        "printer.test_print",
        "printer",
        printer.id,
        after={"ip": printer.ip, "sent": resultado.sent, "detail": resultado.detail},
    )
    session.commit()

    return TestPrintResponse(printer_id=printer.id, ip=printer.ip, sent=resultado.sent, detail=resultado.detail)
