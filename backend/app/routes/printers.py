from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, func, select
from app.database import get_session
from app.dependencies import require_active_user, require_admin, require_operator
from app.models.user import User
from datetime import datetime

from app.models.printer import Printer, PrinterMonthly, PrinterReading
from app.services.environment_guard import bloquear_mock_em_producao
from app.services.monthly_report import month_bounds, month_label, month_period, pages_from_readings
from app.schemas.printer import (
    PrinterCreate,
    PrinterUpdate,
    PrinterResponse,
    PrinterReadingCreate,
    PrinterWithStatus,
    TonerLevel,
)
from typing import List

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


TONER_LABELS = {"K": "Preto", "C": "Ciano", "M": "Magenta", "Y": "Amarelo"}


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

    fechados = session.exec(
        select(PrinterMonthly).where(PrinterMonthly.month_start >= inicio)
    ).all()
    for row in fechados:
        por_impressora_periodo[(row.printer_id, row.month)] = row.pages_printed

    hoje = datetime.utcnow()
    periodo_atual = month_period(hoje)
    if periodo_atual >= month_period(inicio):
        mes_ini, mes_fim = month_bounds(hoje)
        for printer_id, pages in pages_from_readings(session, mes_ini, mes_fim).items():
            por_impressora_periodo.setdefault((printer_id, periodo_atual), pages)

    if not por_impressora_periodo:
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "monthly_usage": [],
            "printers": [],
            "department_usage": [],
        }

    per_printer: dict[int, list[dict]] = {}
    per_month: dict[str, int] = {}
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

        departamento = printer.department or "Sem departamento"
        per_department.setdefault(departamento, {})
        per_department[departamento][period] = per_department[departamento].get(period, 0) + pages

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
            {"month": month_label(period), "pages": pages, "period": period}
            for period, pages in sorted(per_month.items())
        ],
        "printers": [
            {
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
def get_printer(printer_id: int, session: Session = Depends(get_session)):
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
    printer_id: int,
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
    printer_id: int,
    # Teto explicito (Fase 10): sem ele, `?limit=99999999` carregava o
    # historico inteiro da impressora em memoria e no JSON de resposta.
    # Mesmo padrao ja usado em /api/notifications.
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_session),
):
    readings = session.exec(
        select(PrinterReading)
        .where(PrinterReading.printer_id == printer_id)
        .order_by(PrinterReading.timestamp.desc())
        .limit(limit)
    ).all()
    return readings


@router.post("/{printer_id}/readings")
def create_printer_reading(
    printer_id: int,
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
    session.commit()
    session.refresh(reading)
    return reading
