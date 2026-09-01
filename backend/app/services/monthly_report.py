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

from sqlmodel import Session, select

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
    readings = session.exec(
        select(PrinterReading)
        .where(PrinterReading.timestamp >= month_start)
        .where(PrinterReading.timestamp < month_end)
        .order_by(PrinterReading.printer_id, PrinterReading.id)
    ).all()

    total: dict[int, int] = {}
    ultimo_contador: dict[int, int] = {}
    for r in readings:
        if not r.page_count:
            continue
        anterior = ultimo_contador.get(r.printer_id)
        if anterior is not None and r.page_count > anterior:
            total[r.printer_id] = total.get(r.printer_id, 0) + (r.page_count - anterior)
        elif r.printer_id not in total:
            # Primeira leitura valida da impressora no mes: ainda nao ha
            # "salto" para somar, so o registro do ponto de partida.
            total[r.printer_id] = 0
        ultimo_contador[r.printer_id] = r.page_count

    return total


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
