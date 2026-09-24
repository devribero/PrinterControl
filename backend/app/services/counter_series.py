"""
Conta de paginas a partir das leituras do contador (23/09/2026).

Cada leitura guarda dois contadores separados (PrinterReading.counter_vendor
e counter_std). A conta NUNCA mistura os dois:

  - trecho em que o equipamento tem o contador do fabricante: segue so as
    leituras que o tem, ligando uma a outra (leitura em que ele nao
    respondeu e pulada, nao vira ponto de troca);
  - antes da primeira leitura com o do fabricante (historico de antes de
    22/09) e depois da ultima: segue o padrao. A passagem de um para o
    outro acontece numa leitura que tem os dois, sem salto artificial.

Misturar os dois era o que transformava cada troca em "+11 mil paginas"
(FS-4200DN 10.22.0.136: 33.578 paginas em setembro para ~300 por mes).

Leituras antigas (antes das colunas existirem, ou do simulador) so tem
`page_count`: valem como contador padrao ate o reparo (counter_repair.py)
dizer de qual contador vieram.

Trava de plausibilidade: nenhuma impressora da frota passa de 150 paginas
por minuto. Salto maior que isso no intervalo entre as leituras (com folga
de 500) e descartado — sobra de contador trocado, IP reaproveitado por outro
equipamento ou resposta SNMP corrompida.
"""
from __future__ import annotations

from datetime import datetime

PAGINAS_POR_MINUTO_MAX = 150
FOLGA_PAGINAS = 500

Ponto = tuple[tuple[int | None, int | None], datetime]


def ponto(page_count: int | None, vendor: int | None, std: int | None) -> tuple[int | None, int | None]:
    """(fabricante, padrao) efetivos de uma leitura."""
    if std is None and vendor is None:
        std = page_count or None
    return (vendor or None), (std or None)


def salto_plausivel(salto: int, ts_a: datetime, ts_b: datetime) -> bool:
    minutos = max(0.0, (ts_b - ts_a).total_seconds() / 60)
    return salto <= PAGINAS_POR_MINUTO_MAX * minutos + FOLGA_PAGINAS


def _salto(a: int, b: int, ts_a: datetime, ts_b: datetime) -> int:
    salto = b - a
    if salto <= 0 or not salto_plausivel(salto, ts_a, ts_b):
        return 0
    return salto


def paginas_entre(
    a: tuple[int | None, int | None], b: tuple[int | None, int | None], ts_a: datetime, ts_b: datetime
) -> int:
    """Paginas entre duas leituras (fabricante, padrao); 0 se nao ha contador em comum."""
    (va, sa), (vb, sb) = a, b
    if va and vb:
        return _salto(va, vb, ts_a, ts_b)
    if sa and sb:
        return _salto(sa, sb, ts_a, ts_b)
    return 0


def saltos(pontos: list[Ponto]) -> list[tuple[float, datetime, datetime]]:
    """
    (paginas, inicio, fim) de cada trecho da sequencia, sem misturar
    contadores. `pontos` em ordem de tempo.

    Entre a primeira e a ultima leitura com o contador do fabricante vale so
    ele (ligando as leituras que o tem). Fora desse intervalo vale o padrao;
    um trecho do padrao que atravessa a borda conta so a parte de fora,
    proporcional ao tempo — as paginas do trecho de dentro ja estao no do
    fabricante.
    """
    trechos: list[tuple[float, datetime, datetime]] = []

    def cadeia(qual: int) -> list[tuple[int, datetime, datetime]]:
        resultado, anterior = [], None
        for (contadores, ts) in pontos:
            valor = contadores[qual]
            if not valor:
                continue
            if anterior is not None:
                va, ts_a = anterior
                resultado.append((_salto(va, valor, ts_a, ts), ts_a, ts))
            anterior = (valor, ts)
        return resultado

    fabricante = [ts for (v, _), ts in pontos if v]
    if not fabricante:
        return [(float(s), a, b) for s, a, b in cadeia(1)]
    inicio, fim = fabricante[0], fabricante[-1]
    trechos.extend((float(s), a, b) for s, a, b in cadeia(0))
    for salto, ts_a, ts_b in cadeia(1):
        if salto <= 0:
            continue
        duracao = (ts_b - ts_a).total_seconds()
        if duracao <= 0:
            if ts_a < inicio or ts_a > fim:
                trechos.append((float(salto), ts_a, ts_b))
            continue
        if ts_a < inicio:
            corte = min(ts_b, inicio)
            trechos.append((salto * (corte - ts_a).total_seconds() / duracao, ts_a, corte))
        if ts_b > fim:
            corte = max(ts_a, fim)
            trechos.append((salto * (ts_b - corte).total_seconds() / duracao, corte, ts_b))
    return trechos
