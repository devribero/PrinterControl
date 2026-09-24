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
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from sqlmodel import Session, func, or_, select

from app.models.printer import Printer, PrinterMonthly, PrinterReading
from app.services.counter_series import ponto, saltos

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


@dataclass
class MonthPages:
    """
    Paginas de um mes por EQUIPAMENTO (chave = fila representante).

    `pages` ja inclui a parte estimada; `estimated` diz quanto dela e
    estimativa, para o painel poder sinalizar ("inclui N estimadas").
    """

    pages: dict[int, int] = field(default_factory=dict)
    estimated: dict[int, int] = field(default_factory=dict)


# Menor janela medida para extrapolar uma media diaria. Com menos que isso a
# media e ruido (duas leituras com minutos de diferenca viram "paginas por
# dia" absurdas).
_MIN_JANELA_ESTIMATIVA = timedelta(days=1)

# A media diaria da estimativa usa so os primeiros 7 dias de coleta do
# equipamento no mes, e congela depois disso (21/09/2026). Com a media sobre
# o mes inteiro, cada pagina nova aumentava a media e, com ela, a estimativa
# dos dias que JA PASSARAM: numa impressora com estimativa de 0,75x o
# medido, cada folha impressa subia o total em 1,75 — "2 por folha".
_JANELA_MEDIA_ESTIMATIVA = timedelta(days=7)


def month_pages(session: Session, month_start: datetime, month_end: datetime) -> MonthPages:
    """
    Paginas impressas por equipamento dentro de [month_start, month_end).

    SOMA DE SALTOS POSITIVOS (Fase 17)
    ----------------------------------
    Conta o incremento POSITIVO entre leituras consecutivas do contador. No
    caso normal isso e exatamente "maior menos menor"; quando o contador
    RESETA (troca de placa, reset de fabrica), o salto para tras vale zero
    em vez de subtrair errado. Leitura sem contador (offline, etiquetadora)
    nao entra.

    CONTINUIDADE ENTRE MESES (21/09/2026)
    -------------------------------------
    A conta usa tambem a ULTIMA leitura antes do mes e a PRIMEIRA depois
    dele. O salto entre uma leitura de um mes e a primeira do seguinte e
    dividido entre os dois meses na proporcao do tempo que cai em cada um.
    Antes, esse salto nao era de mes nenhum: com o PC desligado na virada
    (fim de semana), as paginas impressas nesse intervalo sumiam do
    relatorio. Agora o mes seguinte "continua a contagem" de onde o anterior
    parou.

    ESTIMATIVA DO INICIO DO MES (21/09/2026)
    ----------------------------------------
    Equipamento SEM nenhuma leitura antes do mes — a coleta comecou no meio
    dele (em setembro/2026 a coleta comecou em 11/09; um Print Server novo
    comeca no dia em que e cadastrado) — nao tem de onde tirar o comeco do
    mes. Esse trecho e estimado pela MEDIA DIARIA medida nos primeiros 7
    dias de coleta do equipamento no mes — depois disso a media congela, e
    cada pagina impressa soma exatamente 1 ao total. A estimativa cobre desde
    o fim do ultimo periodo ja fechado desse equipamento (a planilha fecha
    agosto em 03/09) ou desde o inicio do mes, o que for mais tarde. So
    estima com pelo menos 1 dia medido. A parte estimada volta separada em
    `estimated`.

    POR EQUIPAMENTO (21/09/2026)
    ----------------------------
    Filas que dividem o mesmo IP sao o mesmo contador: so uma, a
    representante, volta no resultado (ver _one_per_device).
    """
    # Leitura com algum contador. Cada ponto e ((fabricante, padrao), ts):
    # a conta entre duas leituras compara sempre o MESMO contador
    # (counter_series.paginas_entre) — ver PrinterReading.counter_vendor.
    com_contador = or_(
        PrinterReading.page_count > 0, PrinterReading.counter_vendor > 0, PrinterReading.counter_std > 0
    )

    def _leituras(filtro):
        linhas = session.exec(
            select(
                PrinterReading.printer_id,
                PrinterReading.page_count,
                PrinterReading.counter_vendor,
                PrinterReading.counter_std,
                PrinterReading.timestamp,
            )
            .where(com_contador)
            .where(filtro)
            .order_by(PrinterReading.printer_id, PrinterReading.id)
        ).all()
        return [(pid, ponto(pc, v, s), ts) for pid, pc, v, s, ts in linhas]

    no_mes = _leituras((PrinterReading.timestamp >= month_start) & (PrinterReading.timestamp < month_end))

    # Ultima leitura valida ANTES do mes e primeira DEPOIS dele, por fila.
    ultimo_antes = (
        select(func.max(PrinterReading.id))
        .where(PrinterReading.timestamp < month_start)
        .where(com_contador)
        .group_by(PrinterReading.printer_id)
    )
    primeiro_depois = (
        select(func.min(PrinterReading.id))
        .where(PrinterReading.timestamp >= month_end)
        .where(com_contador)
        .group_by(PrinterReading.printer_id)
    )
    antes = {pid: (pc, ts) for pid, pc, ts in _leituras(PrinterReading.id.in_(ultimo_antes))}
    depois = {pid: (pc, ts) for pid, pc, ts in _leituras(PrinterReading.id.in_(primeiro_depois))}

    serie: dict[int, list[tuple[int, datetime]]] = {}
    for pid, pc, ts in no_mes:
        serie.setdefault(pid, []).append((pc, ts))

    total: dict[int, float] = {}
    medido_no_mes: dict[int, tuple[float, datetime, datetime]] = {}
    for pid in set(serie) | (set(antes) & set(depois)):
        pontos = ([antes[pid]] if pid in antes else []) + serie.get(pid, []) + ([depois[pid]] if pid in depois else [])
        soma = 0.0
        for salto, ts_a, ts_b in saltos(pontos):
            if salto > 0:
                soma += salto * _fracao_no_mes(ts_a, ts_b, month_start, month_end)
        total[pid] = soma

        # Base da estimativa: so os saltos DENTRO do mes, nos primeiros 7 dias
        # de coleta (ver _JANELA_MEDIA_ESTIMATIVA) — a media congela e as
        # paginas impressas depois somam 1 por 1, sem mexer na estimativa.
        dentro = serie.get(pid, [])
        if dentro:
            limite_janela = dentro[0][1] + _JANELA_MEDIA_ESTIMATIVA
            dentro = [ponto for ponto in dentro if ponto[1] <= limite_janela]
        if pid not in antes and len(dentro) >= 2:
            medido = sum(salto for salto, _, _ in saltos(dentro))
            medido_no_mes[pid] = (medido, dentro[0][1], dentro[-1][1])

    representantes = _one_per_device(session, total)

    fim_anterior = _fim_do_periodo_anterior(session, list(representantes.values()), month_start)
    resultado = MonthPages()
    for chave, pid in representantes.items():
        estimado = 0.0
        if pid in medido_no_mes:
            medido, primeira, ultima = medido_no_mes[pid]
            janela = ultima - primeira
            inicio_estimativa = max(month_start, fim_anterior.get(chave, month_start))
            lacuna = primeira - inicio_estimativa
            if janela >= _MIN_JANELA_ESTIMATIVA and lacuna > timedelta(0):
                estimado = medido / janela.total_seconds() * lacuna.total_seconds()
        resultado.pages[pid] = round(total[pid] + estimado)
        if estimado >= 0.5:
            resultado.estimated[pid] = round(estimado)
    return resultado


def pages_from_readings(session: Session, month_start: datetime, month_end: datetime) -> dict[int, int]:
    """Paginas do mes por equipamento, estimativa incluida (ver month_pages)."""
    return month_pages(session, month_start, month_end).pages


def _fracao_no_mes(ts_a: datetime, ts_b: datetime, month_start: datetime, month_end: datetime) -> float:
    """Fracao do intervalo [ts_a, ts_b] que cai dentro de [month_start, month_end)."""
    if ts_b <= ts_a:
        return 1.0 if month_start <= ts_a < month_end else 0.0
    sobreposicao = (min(ts_b, month_end) - max(ts_a, month_start)).total_seconds()
    return max(0.0, sobreposicao) / (ts_b - ts_a).total_seconds()


def _device_key(printer_id: int, ip: str | None) -> str:
    """
    Chave do EQUIPAMENTO fisico. O IP identifica a impressora na rede; sem
    IP utilizavel (fila local, porta USB, nome em vez de endereco) cada fila
    conta como um equipamento proprio, que e o comportamento antigo.
    """
    ip = (ip or "").strip()
    partes = ip.split(".")
    if len(partes) == 4 and all(p.isdigit() for p in partes):
        return ip
    return f"fila:{printer_id}"


def _one_per_device(session: Session, por_fila: dict[int, float]) -> dict[str, int]:
    """
    Escolhe UMA fila por equipamento. Devolve {chave_do_equipamento: fila}.

    Um equipamento pode ter varias filas no print server (29 IPs da frota
    tem de 2 a 4). A coleta le o equipamento uma vez por IP e grava a mesma
    leitura em cada fila — somar por fila contava o mesmo contador 2, 3, 4
    vezes (setembro/2026: 57.635 paginas onde os equipamentos imprimiram
    32.544).

    A representante e a de MAIOR total no periodo (as filas do mesmo IP leem
    o mesmo contador; a que tem menos foi cadastrada depois). Empate fica
    com o menor id, para o resultado ser estavel entre chamadas.
    """
    if not por_fila:
        return {}
    ips = dict(session.exec(select(Printer.id, Printer.ip).where(Printer.id.in_(list(por_fila)))).all())
    representante: dict[str, int] = {}
    for printer_id in sorted(por_fila):
        chave = _device_key(printer_id, ips.get(printer_id))
        atual = representante.get(chave)
        if atual is None or por_fila[printer_id] > por_fila[atual]:
            representante[chave] = printer_id
    return representante


def _fim_do_periodo_anterior(session: Session, filas: list[int], month_start: datetime) -> dict[str, datetime]:
    """
    Onde terminou o ultimo periodo JA FECHADO de cada equipamento, antes
    deste mes — e dali que a estimativa do comeco do mes parte. Olha todas
    as filas do equipamento (o fechamento pode estar gravado em outra fila
    do mesmo IP). A planilha fecha cada mes no dia 3 do seguinte, entao em
    setembro isso evita estimar de novo os dias 1 a 3, que agosto ja contou.
    """
    if not filas:
        return {}
    ips_rep = dict(session.exec(select(Printer.id, Printer.ip).where(Printer.id.in_(filas))).all())
    chaves = {_device_key(pid, ips_rep.get(pid)) for pid in filas}
    todas = session.exec(select(Printer.id, Printer.ip)).all()
    chave_da_fila = {pid: _device_key(pid, ip) for pid, ip in todas}
    fins = session.exec(
        select(PrinterMonthly.printer_id, func.max(PrinterMonthly.month_end))
        .where(PrinterMonthly.month_start < month_start)
        .group_by(PrinterMonthly.printer_id)
    ).all()
    resultado: dict[str, datetime] = {}
    for pid, fim in fins:
        chave = chave_da_fila.get(pid)
        if chave not in chaves or fim is None:
            continue
        if isinstance(fim, str):
            fim = datetime.fromisoformat(fim)
        if chave not in resultado or fim > resultado[chave]:
            resultado[chave] = fim
    return resultado


def filas_com_o_mesmo_serial(session: Session, printer: Printer, somente_inativas: bool = False) -> list[int]:
    """
    Outros cadastros do MESMO equipamento em outro IP, pelo numero de serie.

    So vale quando o serie desta fila foi lido por SNMP (snmp_updated_at): ai
    ele identifica o aparelho fisico. Caso de 22/09/2026: equipamentos que
    mudaram de IP depois da planilha ficaram com o historico no cadastro do
    IP antigo (ex.: LVK6X54346 em 10.22.2.30, hoje em 10.22.3.68), e a folha
    de teste mostrava so setembro.
    """
    serial = (printer.serial_number or "").strip().upper()
    if not serial or printer.snmp_updated_at is None:
        return []
    consulta = select(Printer.id, Printer.ip, Printer.serial_number, Printer.active).where(Printer.id != printer.id)
    return [
        pid for pid, ip, outro_serial, ativa in session.exec(consulta).all()
        if (outro_serial or "").strip().upper() == serial and ip != printer.ip and not (somente_inativas and ativa)
    ]


def device_monthly_history(session: Session, printer_id: int, limite: int = 12) -> list[tuple[str, int, int, bool]]:
    """
    Paginas por mes do EQUIPAMENTO da fila informada, do mais antigo ao mais
    recente: [("Ago/26", paginas, estimadas, em_andamento), ...].

    Olha todas as filas do mesmo IP: o historico (fechado ou importado da
    planilha) fica gravado so na fila representante, que pode nao ser a que
    foi pedida. O mes corrente, ainda sem fechamento, vem ao vivo pela mesma
    conta do relatorio (month_pages). Usado pela pagina de teste.
    """
    printer = session.get(Printer, printer_id)
    if not printer:
        return []
    chave = _device_key(printer.id, printer.ip)
    filas = [pid for pid, ip in session.exec(select(Printer.id, Printer.ip)).all() if _device_key(pid, ip) == chave]

    por_periodo: dict[str, tuple[int, int]] = {}
    for linha in session.exec(select(PrinterMonthly).where(PrinterMonthly.printer_id.in_(filas))).all():
        atual = por_periodo.get(linha.month)
        # Duas filas do mesmo IP com o mesmo mes: e o mesmo contador, vale o maior.
        if atual is None or linha.pages_printed > atual[0]:
            por_periodo[linha.month] = (linha.pages_printed, linha.estimated_pages or 0)
    # O mesmo aparelho em outro IP (pelo serie): so completa meses que faltam.
    outros = filas_com_o_mesmo_serial(session, printer)
    if outros:
        for linha in session.exec(select(PrinterMonthly).where(PrinterMonthly.printer_id.in_(outros))).all():
            por_periodo.setdefault(linha.month, (linha.pages_printed, linha.estimated_pages or 0))

    agora = datetime.utcnow()
    periodo_atual = month_period(agora)
    em_andamento = None
    if periodo_atual not in por_periodo:
        mes = month_pages(session, *month_bounds(agora))
        for pid in filas:
            if pid in mes.pages:
                por_periodo[periodo_atual] = (mes.pages[pid], mes.estimated.get(pid, 0))
                em_andamento = periodo_atual
                break

    historico = [
        (f"{month_label(periodo)}/{periodo[2:4]}", paginas, estimadas, periodo == em_andamento)
        for periodo, (paginas, estimadas) in sorted(por_periodo.items())
    ]
    return historico[-limite:]


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

    SO FECHA DEPOIS QUE A COLETA VOLTOU
    -----------------------------------
    Um mes so e congelado quando ja existe leitura DEPOIS do fim dele: e ela
    que da o pedaco final do mes (a divisao do salto que atravessa a virada,
    ver month_pages). Fechar antes, logo na subida de uma maquina que ficou
    desligada, congelaria o mes sem esse final. Por isso isto roda tambem ao
    fim de cada ciclo de coleta, e nao so nos disparos agendados.

    QUANDO UM MES CONTA COMO FECHADO
    --------------------------------
    Qualquer linha em PrinterMonthly para o periodo. Mes fechado nunca e
    recalculado — nem o importado de planilha (import_historico_planilha.py),
    que e a fonte oficial dos meses antigos, nem o congelado aqui.
    """
    now = now or datetime.utcnow()
    atual = month_period(now)

    primeira, ultima = session.exec(
        select(func.min(PrinterReading.timestamp), func.max(PrinterReading.timestamp))
    ).one()
    if primeira is None:
        return {}
    if isinstance(primeira, str):  # SQLite pode devolver o agregado cru
        primeira = datetime.fromisoformat(primeira)
    if isinstance(ultima, str):
        ultima = datetime.fromisoformat(ultima)

    ja_fechados = set(session.exec(select(PrinterMonthly.month).distinct()).all())

    fechados: dict[str, int] = {}
    cursor = datetime(primeira.year, primeira.month, 1)
    while month_period(cursor) < atual:
        inicio, fim = month_bounds(cursor)
        periodo = month_period(cursor)
        if periodo not in ja_fechados and ultima >= fim:
            mes = month_pages(session, inicio, fim)
            for printer_id, total in mes.pages.items():
                upsert_printer_monthly(
                    session, printer_id, periodo, total, inicio, fim,
                    estimated_pages=mes.estimated.get(printer_id, 0),
                )
            if mes.pages:
                fechados[periodo] = len(mes.pages)
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
    estimated_pages: int = 0,
) -> None:
    """
    Grava ou atualiza o total de UM mes de UMA impressora — chave e
    (printer_id, period). Usado pelo fechamento automatico (scheduler.py)
    e pelo importador de historico (import_historico_planilha.py), para
    que os dois nunca dupliquem uma linha do mesmo mes. Nao commita: quem
    chama decide quando (import faz varias upsert antes de um commit so).

    `estimated_pages`: quanto de `pages_printed` e estimativa (ver
    month_pages); 0 para dado medido ou vindo da planilha.
    """
    existing = session.exec(
        select(PrinterMonthly)
        .where(PrinterMonthly.printer_id == printer_id)
        .where(PrinterMonthly.month == period)
    ).first()
    if existing:
        existing.pages_printed = pages_printed
        existing.month_start = month_start
        existing.month_end = month_end
        existing.estimated_pages = estimated_pages
        session.add(existing)
    else:
        session.add(
            PrinterMonthly(
                printer_id=printer_id,
                month=period,
                pages_printed=pages_printed,
                month_start=month_start,
                month_end=month_end,
                estimated_pages=estimated_pages,
            )
        )
