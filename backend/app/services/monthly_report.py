"""
Calculo de paginas por mes, compartilhado entre tres consumidores (Fase 12):

  - GET /api/printers/monthly-report (routes/printers.py) — mes em
    andamento, calculado ao vivo a partir de PrinterReading.
  - Fechamento automatico mensal (services/scheduler.py) — roda no ultimo
    dia do mes, congela o resultado em PrinterMonthly.
  - Importador de historico (import_historico_planilha.py) — grava direto
    em PrinterMonthly, sem passar por aqui (a planilha ja traz o total
    pronto), mas usa o mesmo MONTH_LABELS para consistencia de rotulo.

Extraido do que antes vivia dentro de routes/printers.py, para que os tres
lugares nao arrisquem calcular a mesma coisa de tres formas diferentes.
"""
from datetime import datetime

from sqlmodel import Session, func, select

from app.models.printer import PrinterMonthly, PrinterReading

MONTH_LABELS = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]


def month_period(dt: datetime) -> str:
    """'2026-08' — chave de mes usada em PrinterMonthly.month e nas respostas da API."""
    return dt.strftime("%Y-%m")


def month_label(period: str) -> str:
    """'2026-08' -> 'Ago'."""
    return MONTH_LABELS[int(period[5:]) - 1]


def month_bounds(dt: datetime) -> tuple[datetime, datetime]:
    """Primeiro instante do mes de `dt` e primeiro instante do mes seguinte (limite exclusivo)."""
    inicio = datetime(dt.year, dt.month, 1)
    if dt.month == 12:
        fim = datetime(dt.year + 1, 1, 1)
    else:
        fim = datetime(dt.year, dt.month + 1, 1)
    return inicio, fim


def pages_from_readings(
    session: Session, month_start: datetime, month_end: datetime
) -> dict[int, int]:
    """
    Paginas impressas por impressora dentro de [month_start, month_end),
    somando o incremento POSITIVO entre leituras consecutivas (ordenadas por
    id — mesma ordem de insercao/coleta).

    Fase 17: antes disto era "maior contador observado menos o menor". Isso
    assume que o contador so cresce dentro do mes — quebra quando ele
    RESETA (troca de placa formatadora, reset de fabrica; o proprio projeto
    ja simula esse cenario em snmp_fleet_mock.counter_reset). Com reset no
    meio do mes, "maior menos menor" pega o pico ANTES do reset e o vale
    DEPOIS dele, superestimando o total de forma grosseira (contador vai de
    50000 para 12, o calculo antigo relataria ~50238 paginas em vez das
    ~538 realmente impressas).

    Somar so os saltos POSITIVOS entre leituras consecutivas da o mesmo
    resultado no caso normal (contador sempre subindo — a soma telescopa
    exatamente para maior-menor) e ignora corretamente o salto para tras de
    um reset, em vez de subtrair errado.

    Leitura sem contador valido (impressora offline no momento) nao entra
    na conta. Impressora sem nenhuma leitura no periodo nao aparece no
    dict retornado.
    """
    # So as duas colunas usadas, e sem as leituras sem contador (offline,
    # etiquetadora): esta consulta roda a cada carga do painel e a tabela
    # cresce ~1,4 milhao de linhas por mes com a frota atual. Carregar cada
    # linha como objeto ORM completo custava ~1s a cada 6 dias de leitura —
    # uns 25s por chamada no fim do mes. O resultado e identico.
    readings = session.exec(
        select(PrinterReading.printer_id, PrinterReading.page_count)
        .where(PrinterReading.timestamp >= month_start)
        .where(PrinterReading.timestamp < month_end)
        .where(PrinterReading.page_count > 0)
        .order_by(PrinterReading.printer_id, PrinterReading.id)
    ).all()

    total: dict[int, int] = {}
    ultimo_contador: dict[int, int] = {}
    for printer_id, page_count in readings:
        anterior = ultimo_contador.get(printer_id)
        if anterior is not None and page_count > anterior:
            total[printer_id] = total.get(printer_id, 0) + (page_count - anterior)
        elif printer_id not in total:
            # Primeira leitura valida da impressora no mes: ainda nao ha
            # "salto" para somar, so o registro do ponto de partida.
            total[printer_id] = 0
        ultimo_contador[printer_id] = page_count

    return total


def close_pending_months(session: Session, now: datetime | None = None) -> dict[str, int]:
    """
    Congela em PrinterMonthly todo mes JA TERMINADO que tem leitura e ainda
    nao foi fechado. Devolve {periodo: impressoras_fechadas}; faz commit.

    POR QUE EXISTE (21/09/2026)
    ---------------------------
    O fechamento dependia de um unico disparo, no ultimo dia do mes as
    23:50, e isso falhava de dois jeitos:

      1. Mes errado. O scheduler roda no fuso de Sao Paulo, mas a conta de
         mes e em UTC (`utcnow`, como todo timestamp de leitura). 23:50 em
         Brasilia ja e 02:50 do DIA 1 em UTC — o job congelava o mes que
         estava COMECANDO, quase vazio, e o que terminou nunca era gravado.

      2. Maquina desligada. O backend roda num PC de mesa. Desligado na
         virada, nada fechava — e como GET /monthly-report so calcula ao
         vivo o mes CORRENTE, o mes anterior sumia do relatorio inteiro,
         embora as leituras continuassem no banco.

    Rodar "feche o que falta" em vez de "feche o mes de agora" resolve os
    dois: nao importa em que fuso nem com quantos dias de atraso roda.

    QUANDO UM MES CONTA COMO FECHADO
    --------------------------------
    Qualquer linha em PrinterMonthly para o periodo. Mes fechado nunca e
    recalculado — nem o importado de planilha (import_historico_planilha.py),
    que e a fonte oficial dos meses antigos, nem o congelado aqui. Isso
    tambem mantem a funcao barata: cada mes custa uma leitura das leituras
    uma unica vez na vida, e nas chamadas seguintes e so a consulta de
    periodos ja fechados.
    """
    now = now or datetime.utcnow()
    atual = month_period(now)

    primeira = session.exec(select(func.min(PrinterReading.timestamp))).one()
    if primeira is None:
        return {}
    if isinstance(primeira, str):  # SQLite pode devolver o agregado cru
        primeira = datetime.fromisoformat(primeira)

    ja_fechados = set(session.exec(select(PrinterMonthly.month).distinct()).all())

    fechados: dict[str, int] = {}
    cursor = datetime(primeira.year, primeira.month, 1)
    while month_period(cursor) < atual:
        inicio, fim = month_bounds(cursor)
        periodo = month_period(cursor)
        if periodo not in ja_fechados:
            paginas = pages_from_readings(session, inicio, fim)
            for printer_id, total in paginas.items():
                upsert_printer_monthly(session, printer_id, periodo, total, inicio, fim)
            if paginas:
                fechados[periodo] = len(paginas)
        cursor = fim

    if fechados:
        session.commit()
    return fechados


def upsert_printer_monthly(
    session: Session,
    printer_id: int,
    period: str,
    pages_printed: int,
    month_start: datetime,
    month_end: datetime,
) -> None:
    """
    Grava ou atualiza o total de UM mes de UMA impressora — chave e
    (printer_id, period). Usado pelo fechamento automatico (scheduler.py)
    e pelo importador de historico (import_historico_planilha.py), para
    que os dois nunca dupliquem uma linha do mesmo mes. Nao commita: quem
    chama decide quando (import faz varias upsert antes de um commit so).
    """
    existing = session.exec(
        select(PrinterMonthly)
        .where(PrinterMonthly.printer_id == printer_id)
        .where(PrinterMonthly.month == period)
    ).first()
    if existing:
        existing.pages_printed = pages_printed
        existing.month_end = month_end
        session.add(existing)
    else:
        session.add(
            PrinterMonthly(
                printer_id=printer_id,
                month=period,
                pages_printed=pages_printed,
                month_start=month_start,
                month_end=month_end,
            )
        )
