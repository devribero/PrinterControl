"""
Reparo das leituras gravadas antes de os contadores serem separados
(23/09/2026).

Ate 22/09 a coluna `page_count` recebia um contador so. Nas Kyocera, depois
da mudanca para o contador do fabricante, ela passou a alternar entre os
dois — o do fabricante quando respondia a tempo, o padrao quando nao — e o
relatorio contava cada troca como milhares de paginas (FS-4200DN
10.22.0.136: 900.7 mil <-> 911.8 mil, "+33 mil paginas" em setembro).

Aqui cada leitura antiga (counter_vendor e counter_std vazios) ganha o
contador de onde veio:

  - equipamento que nao tem contador do fabricante: tudo e o padrao;
  - Kyocera: cada leitura recebe o rotulo que deixa a sequencia com o
    menor crescimento (ver _rotular), usando a diferenca entre os dois
    contadores medida numa leitura que ja tem os dois (a primeira coleta
    depois desta correcao grava os dois).

Kyocera ainda sem leitura com os dois contadores e com leitura recente fica
para depois: a coleta seguinte traz a referencia. Parada ha mais de um dia
(offline) e reparada por aproximacao: a serie mais antiga e a do padrao,
que era o unico contador lido ate 22/09.

Idempotente: so mexe em leitura com os dois campos vazios. Roda depois de
cada ciclo de coleta.
"""
from __future__ import annotations

import logging
import re
from datetime import datetime, timedelta

from sqlmodel import Session, select

from app.models.printer import Printer, PrinterReading
from app.services.counter_series import salto_plausivel

logger = logging.getLogger("printercontrol.counter_repair")

_IPV4 = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")
_KYOCERA = re.compile(r"kyocera|ecosys|taskalfa|\bfs-\d", re.IGNORECASE)
_ESPERA_REFERENCIA = timedelta(days=1)
_TOLERANCIA_RETROCESSO = 5


def _chave(printer: Printer) -> str:
    return printer.ip if _IPV4.match(printer.ip or "") else f"fila:{printer.id}"


def _rotular(
    leituras: list[PrinterReading], diferenca: int, ancora: tuple[int, datetime] | None
) -> tuple[list[str], float]:
    """
    Rotula cada leitura como "fabricante" ou "padrao" pela sequencia de menor
    crescimento. `diferenca` = padrao - fabricante (quase constante: os dois
    contam as mesmas folhas). Em "contador do fabricante equivalente", um
    rotulo errado sempre cria um salto do tamanho da diferenca; o caminho
    certo e o que cresce so o que foi impresso. `ancora` = (fabricante, ts)
    de uma leitura com os dois contadores, depois das antigas.

    Programacao dinamica em dois estados; devolve (rotulos, custo).
    """
    GRANDE = 1e12
    estados = ("fabricante", "padrao")

    def equivalente(valor: int, estado: str) -> int:
        return valor if estado == "fabricante" else valor - diferenca

    def custo(a: int, ts_a: datetime, b: int, ts_b: datetime) -> float:
        salto = b - a
        if salto < -_TOLERANCIA_RETROCESSO:
            return GRANDE + abs(salto)
        if not salto_plausivel(salto, ts_a, ts_b):
            return GRANDE + salto
        return max(0, salto)

    custo_ate = {e: 0.0 for e in estados}
    volta: list[dict[str, str]] = []  # volta[i][estado de i+1] = estado de i
    for anterior, atual in zip(leituras, leituras[1:]):
        novo, ponteiros = {}, {}
        for e in estados:
            b = equivalente(atual.page_count, e)
            f = min(
                estados,
                key=lambda f: custo_ate[f] + custo(equivalente(anterior.page_count, f), anterior.timestamp, b, atual.timestamp),
            )
            novo[e] = custo_ate[f] + custo(equivalente(anterior.page_count, f), anterior.timestamp, b, atual.timestamp)
            ponteiros[e] = f
        custo_ate = novo
        volta.append(ponteiros)
    if ancora is not None:
        valor, ts = ancora
        ultima = leituras[-1]
        custo_ate = {
            e: c + custo(equivalente(ultima.page_count, e), ultima.timestamp, valor, ts) for e, c in custo_ate.items()
        }
    estado = min(estados, key=lambda e: custo_ate[e])
    total = custo_ate[estado]
    caminho = [estado]
    for ponteiros in reversed(volta):
        estado = ponteiros[estado]
        caminho.append(estado)
    caminho.reverse()
    return caminho, total


def _diferenca_pelos_dados(leituras: list[PrinterReading]) -> int | None:
    """Tamanho tipico das quedas bruscas (trocas de contador), sem sinal."""
    quedas = sorted(
        a.page_count - b.page_count for a, b in zip(leituras, leituras[1:]) if a.page_count - b.page_count > 500
    )
    return quedas[len(quedas) // 2] if quedas else None


def reparar_leituras(
    session: Session,
    referencias: dict[str, tuple[int, int]] | None = None,
    agora: datetime | None = None,
) -> dict[str, int]:
    """
    Classifica as leituras antigas. `referencias` (ip -> (fabricante,
    padrao) lidos agora) substitui a leitura dupla do banco quando dada.
    Devolve {"padrao": n, "fabricante": n, "adiadas": equipamentos}.
    """
    agora = agora or datetime.utcnow()
    legado = session.exec(
        select(PrinterReading, Printer)
        .join(Printer, Printer.id == PrinterReading.printer_id)
        .where(PrinterReading.counter_vendor == None)  # noqa: E711
        .where(PrinterReading.counter_std == None)  # noqa: E711
        .where(PrinterReading.page_count > 0)
        .order_by(PrinterReading.timestamp, PrinterReading.id)
    ).all()
    if not legado:
        return {"padrao": 0, "fabricante": 0, "adiadas": 0}

    por_equipamento: dict[str, list[PrinterReading]] = {}
    impressoras: dict[str, list[Printer]] = {}
    for leitura, printer in legado:
        chave = _chave(printer)
        por_equipamento.setdefault(chave, []).append(leitura)
        impressoras.setdefault(chave, []).append(printer)

    contagem = {"padrao": 0, "fabricante": 0, "adiadas": 0}
    for chave, leituras in por_equipamento.items():
        filas = impressoras[chave]
        ids = sorted({p.id for p in filas})
        # Referencia: a primeira leitura com os dois contadores (logo depois
        # das antigas), ou a lida agora quando o chamador passou uma.
        dupla = session.exec(
            select(PrinterReading.counter_vendor, PrinterReading.counter_std, PrinterReading.timestamp)
            .where(PrinterReading.printer_id.in_(ids))
            .where(PrinterReading.counter_vendor != None)  # noqa: E711
            .where(PrinterReading.counter_std != None)  # noqa: E711
            .order_by(PrinterReading.id)
        ).first()
        if referencias and chave in referencias:
            dupla = (*referencias[chave], agora)
        textos = " ".join(f"{p.model} {p.snmp_model or ''} {p.snmp_description or ''} {p.driver_name}" for p in filas)
        tem_fabricante = dupla is not None or bool(_KYOCERA.search(textos))

        if not tem_fabricante:
            for leitura in leituras:
                leitura.counter_std = leitura.page_count
                session.add(leitura)
            contagem["padrao"] += len(leituras)
            continue

        if dupla is None and agora - leituras[-1].timestamp < _ESPERA_REFERENCIA:
            contagem["adiadas"] += 1
            continue

        if dupla is not None:
            fabricante_ref, padrao_ref, ts_ref = dupla
            diferenca = padrao_ref - fabricante_ref
            if abs(diferenca) < 50:
                rotulos = ["padrao"] * len(leituras)  # contadores praticamente iguais
            else:
                ancora = (fabricante_ref, ts_ref) if ts_ref >= leituras[-1].timestamp else None
                rotulos, _ = _rotular(leituras, diferenca, ancora)
        else:
            # Sem referencia (parada ha mais de um dia): a diferenca sai das
            # proprias quedas, e a primeira leitura e do padrao — o unico
            # contador lido ate 22/09. O sinal e o que der menor crescimento.
            tamanho = _diferenca_pelos_dados(leituras)
            if tamanho is None:
                rotulos = ["padrao"] * len(leituras)
            else:
                candidatos = []
                for diferenca in (tamanho, -tamanho):
                    r, total = _rotular(leituras, diferenca, None)
                    if r[0] == "padrao":
                        candidatos.append((total, r))
                rotulos = min(candidatos)[1] if candidatos else ["padrao"] * len(leituras)

        for leitura, rotulo in zip(leituras, rotulos):
            if rotulo == "fabricante":
                leitura.counter_vendor = leitura.page_count
            else:
                leitura.counter_std = leitura.page_count
            session.add(leitura)
            contagem[rotulo] += 1

    session.commit()
    if contagem["padrao"] or contagem["fabricante"]:
        logger.info(
            "Leituras antigas classificadas | padrao=%s fabricante=%s equipamentos_adiados=%s",
            contagem["padrao"], contagem["fabricante"], contagem["adiadas"],
        )
    return contagem
