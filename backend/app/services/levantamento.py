"""
Levantamento mensal em Excel (22/09/2026).

Todo mes a equipe entrega a planilha "Levantamento impressoes" IDENTICA a
da empresa, so com o mes novo preenchido. Este modulo gera esse arquivo a
partir das leituras do sistema.

BASE E HISTORICO
----------------
    backend/data/levantamento/          (fora do git; ver .gitignore)
        base.xlsx       planilha de partida do proximo mes
        base.json       quando/como a base chegou ali
        gerados/        cada arquivo gerado + base anterior (backup)
        gerados/index.json

A base comeca com a planilha enviada pelo admin — pela tela de Relatorios
ou, a primeira vez (a v8 foi semeada assim em 22/09/2026), pela linha de
comando (ver o bloco __main__ no fim deste arquivo):

    .\\venv\\Scripts\\python.exe -m app.services.levantamento "C:\\...\\Levantamento impressões_v8.xlsx"

Cada mes o
arquivo novo e gerado A PARTIR DA BASE, e quando o periodo ja fechou ele
vira a base do mes seguinte. Periodo em andamento gera uma "previa", que
nunca substitui a base. O admin pode reenviar uma base editada a mano a
qualquer momento (a anterior fica em gerados/ como backup).

O QUE MUDA NO ARQUIVO
---------------------
So a aba "Contabilizacao mensal", e nela so:
  - a coluna do mes gerado, nas linhas de impressora (numero de paginas;
    celula VAZIA quando o sistema nao mediu o equipamento no periodo);
  - as celulas "Total" de cada bloco e a celula do resumo do topo, na
    coluna do mes gerado e nas dos meses seguintes ainda vazios: a planilha
    tinha somas que pulavam linhas (ex.: M28 =SUM(M20:M25) num bloco que vai
    ate a linha 27). Meses passados nao sao tocados.
Mais a aba "Novos no sistema" (recriada a cada geracao): equipamentos que o
sistema mediu e que nao estao em linha nenhuma da planilha. O workbook
passa a pedir recalculo completo ao abrir (fullCalcOnLoad), que atualiza
totais, as outras abas e os 12 graficos.

PERIODO
-------
O da tabela do topo da aba ("04/09/26 a 03/10/26": do dia 4 ao dia 3 do mes
seguinte; janeiro comeca dia 02/01). Datas locais de Sao Paulo; as leituras
estao em UTC sem fuso, entao o limite vira 03:00 UTC. Paginas por
equipamento: monthly_report.month_pages (mesma conta do relatorio mensal:
dedupe por IP, rateio do salto que atravessa o limite, estimativa do
inicio quando a coleta comecou no meio do periodo).
"""
import json
import logging
import re
import shutil
import threading
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from sqlmodel import Session, func, select

from app.config import BACKEND_DIR, settings
from app.models.print_server import PrintServer
from app.models.printer import Printer, PrinterReading
from app.models.unit import Unit
from app.services.levantamento_xlsx import (
    Pacote,
    PlanilhaXml,
    adicionar_aba,
    forcar_recalculo,
    montar_aba_simples,
    remover_aba,
    remover_calc_chain,
    split_ref,
    validar_pacote,
)
from app.services.monthly_report import _device_key, month_pages
from app.services.planilha_levantamento import (
    IPV4_RE,
    MONTH_COLUMNS,
    SHEET_NAME,
    PlanilhaError,
    blocos_da_aba,
    caminho_da_aba,
    indices_do_banco,
    letra_coluna,
    ler_aba,
    limpar,
    localizar_equipamento,
    meses_preenchidos,
    resumo_da_aba,
)

logger = logging.getLogger("printercontrol.levantamento")

FUSO = ZoneInfo("America/Sao_Paulo")
ABA_NOVOS = "Novos no sistema"
PREFIXO_ARQUIVO = "Levantamento impressões"
SUFIXO_PREVIA = " (prévia)"
TAMANHO_MAXIMO_BASE = 20 * 1024 * 1024

_lock = threading.Lock()


class LevantamentoError(Exception):
    """Erro que vira 400/404 na API (mensagem para o usuario)."""


# ─────────────────────────────────────────────────────────────────────────
#  Pastas e indice
# ─────────────────────────────────────────────────────────────────────────

def pasta() -> Path:
    return Path(settings.levantamento_dir) if settings.levantamento_dir else BACKEND_DIR / "data" / "levantamento"


def pasta_gerados() -> Path:
    return pasta() / "gerados"


def caminho_base() -> Path:
    return pasta() / "base.xlsx"


def _ler_json(caminho: Path, padrao):
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return padrao


def _gravar_json(caminho: Path, dados) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    tmp = caminho.with_suffix(caminho.suffix + ".tmp")
    tmp.write_text(json.dumps(dados, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    tmp.replace(caminho)


def _indice() -> list[dict]:
    return _ler_json(pasta_gerados() / "index.json", [])


def _gravar_indice(itens: list[dict]) -> None:
    _gravar_json(pasta_gerados() / "index.json", itens)


def _registrar_arquivo(entrada: dict) -> None:
    itens = [i for i in _indice() if i.get("nome") != entrada["nome"]]
    itens.append(entrada)
    _gravar_indice(itens)


def _agora_utc() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _iso(dt: datetime | None) -> str | None:
    return dt.isoformat(timespec="seconds") if dt else None


# ─────────────────────────────────────────────────────────────────────────
#  Leitura da base
# ─────────────────────────────────────────────────────────────────────────

class _Base:
    """A planilha lida: celulas, blocos, tabela de periodos e ano."""

    def __init__(self, dados: bytes):
        self.dados = dados
        self.celulas = ler_aba(dados)
        self.blocos = blocos_da_aba(self.celulas)
        self.resumo = resumo_da_aba(self.celulas)
        if not self.blocos:
            raise PlanilhaError(f"Nenhum bloco de impressoras (linha 'IP, Modelo, Serial...') na aba {SHEET_NAME!r}.")
        if not self.resumo:
            raise PlanilhaError(f"Tabela 'Mês | Período | Impressões' nao encontrada no topo da aba {SHEET_NAME!r}.")
        self.ano = self._ano()

    def _ano(self) -> int:
        for mes in ("Janeiro", "Fevereiro", "Dezembro"):
            r = self.resumo.get(mes)
            if r and r.periodo:
                return r.periodo[0].year
        anos = [r.periodo[0].year for r in self.resumo.values() if r.periodo]
        if anos:
            return Counter(anos).most_common(1)[0][0]
        return _agora_utc().year

    @property
    def itens(self):
        return [item for bloco in self.blocos for item in bloco.itens]

    def meses_preenchidos(self) -> list[str]:
        return meses_preenchidos(self.itens)

    def periodo_local(self, mes_nome: str) -> tuple[datetime, datetime, str | None, bool]:
        """(inicio, fim_exclusivo, texto, veio_da_planilha) em hora local."""
        idx = MONTH_COLUMNS.index(mes_nome) + 1
        r = self.resumo.get(mes_nome)
        if r and r.periodo:
            return r.periodo[0], r.periodo[1], r.texto_periodo, True
        inicio = datetime(self.ano, idx, 4)
        fim = datetime(self.ano + 1, 1, 4) if idx == 12 else datetime(self.ano, idx + 1, 4)
        return inicio, fim, r.texto_periodo if r else None, False


def _para_utc(local: datetime) -> datetime:
    """Meia-noite de Sao Paulo -> UTC sem fuso (formato dos timestamps do banco)."""
    return local.replace(tzinfo=FUSO).astimezone(timezone.utc).replace(tzinfo=None)


def validar_planilha(dados: bytes) -> "_Base":
    """Levanta PlanilhaError se nao for o levantamento esperado."""
    if not dados[:4] == b"PK\x03\x04":
        raise PlanilhaError("O arquivo nao e um .xlsx (nao comeca como zip).")
    return _Base(dados)


def _ler_base() -> _Base:
    caminho = caminho_base()
    if not caminho.exists():
        raise LevantamentoError(
            "Nenhuma planilha base cadastrada. Envie o levantamento atual em 'Enviar planilha base'."
        )
    try:
        return _Base(caminho.read_bytes())
    except PlanilhaError as e:
        raise LevantamentoError(f"A planilha base nao pode ser lida: {e}") from e


def _chave_mes(ano: int, mes_nome: str) -> str:
    return f"{ano}-{MONTH_COLUMNS.index(mes_nome) + 1:02d}"


def nome_arquivo(mes_nome: str, ano: int, previa: bool) -> str:
    return f"{PREFIXO_ARQUIVO}_{mes_nome}_{ano}{SUFIXO_PREVIA if previa else ''}.xlsx"


# ─────────────────────────────────────────────────────────────────────────
#  Estado (GET /api/levantamento)
# ─────────────────────────────────────────────────────────────────────────

def estado(agora: datetime | None = None) -> dict:
    agora = agora or _agora_utc()
    meta = _ler_json(pasta() / "base.json", {})
    arquivos = sorted(_indice(), key=lambda i: i.get("gerado_em") or "", reverse=True)
    lista = []
    for item in arquivos:
        caminho = pasta_gerados() / item["nome"]
        if not caminho.exists():
            continue
        lista.append({
            "nome": item["nome"],
            "mes": item.get("mes"),
            "gerado_em": item.get("gerado_em"),
            "previa": bool(item.get("previa")),
            "tipo": item.get("tipo", "gerado"),
            "automatico": bool(item.get("automatico")),
            "tamanho": caminho.stat().st_size,
        })

    base_info = None
    meses = []
    proximo = None
    ultimo_fechado = None
    erro_base = None
    if caminho_base().exists():
        try:
            base = _Base(caminho_base().read_bytes())
        except PlanilhaError as e:
            base = None
            erro_base = str(e)
        if base:
            preenchidos = base.meses_preenchidos()
            base_info = {
                "enviada_em": meta.get("enviada_em"),
                "atualizada_em": meta.get("atualizada_em") or meta.get("enviada_em"),
                "origem": meta.get("origem"),
                "nome_original": meta.get("nome_original"),
                "ano": base.ano,
                "meses_preenchidos": [_chave_mes(base.ano, m) for m in preenchidos],
            }
            for mes_nome in MONTH_COLUMNS:
                inicio, fim, texto, _ = base.periodo_local(mes_nome)
                chave = _chave_mes(base.ano, mes_nome)
                fechado = _para_utc(fim) <= agora
                meses.append({
                    "mes": chave,
                    "nome": mes_nome,
                    "periodo": texto or f"{inicio:%d/%m/%y} a {(fim - timedelta(days=1)):%d/%m/%y}",
                    "fechado": fechado,
                    "em_andamento": _para_utc(inicio) <= agora < _para_utc(fim),
                    "preenchido": mes_nome in preenchidos,
                })
                if fechado:
                    ultimo_fechado = chave
            ultimo_preenchido = max((MONTH_COLUMNS.index(m) for m in preenchidos), default=-1)
            if ultimo_preenchido < 11:
                proximo = _chave_mes(base.ano, MONTH_COLUMNS[ultimo_preenchido + 1])

    return {
        "base": base_info,
        "erro_base": erro_base,
        "arquivos": lista,
        "meses": meses,
        "proximo_mes": proximo,
        "ultimo_mes_fechado": ultimo_fechado,
    }


def arquivo_para_download(nome: str) -> Path:
    """
    Caminho de um arquivo da lista — e SO da lista. O nome tem de ser
    exatamente um dos registrados no indice e o arquivo tem de estar direto
    em gerados/ (nada de "..", barra ou caminho absoluto).
    """
    if not nome or "/" in nome or "\\" in nome or nome.startswith(".") or ".." in nome:
        raise LevantamentoError("Arquivo nao encontrado.")
    if nome not in {i.get("nome") for i in _indice()}:
        raise LevantamentoError("Arquivo nao encontrado.")
    raiz = pasta_gerados().resolve()
    caminho = (raiz / nome).resolve()
    if caminho.parent != raiz or not caminho.is_file():
        raise LevantamentoError("Arquivo nao encontrado.")
    return caminho


# ─────────────────────────────────────────────────────────────────────────
#  Base: envio / substituicao
# ─────────────────────────────────────────────────────────────────────────

def _backup_da_base(motivo: str) -> str | None:
    """Copia a base atual para gerados/ antes de substitui-la. Devolve o nome."""
    atual = caminho_base()
    if not atual.exists():
        return None
    agora = _agora_utc()
    local = agora.replace(tzinfo=timezone.utc).astimezone(FUSO)
    nome = f"Base anterior_{local:%Y-%m-%d_%H%M%S}.xlsx"
    pasta_gerados().mkdir(parents=True, exist_ok=True)
    shutil.copyfile(atual, pasta_gerados() / nome)
    _registrar_arquivo({"nome": nome, "mes": None, "gerado_em": _iso(agora), "previa": False,
                        "tipo": "base_anterior", "motivo": motivo})
    return nome


def substituir_base(dados: bytes, nome_original: str | None = None, origem: str = "upload") -> dict:
    """
    Troca a planilha base. Valida antes (zip + aba + blocos + tabela de
    periodos); a base anterior vai para gerados/ como "Base anterior_...".
    Usado pelo POST /api/levantamento/base e para semear a base inicial:

        from app.services.levantamento import substituir_base
        substituir_base(open(r"...\\Levantamento impressões_v8.xlsx", "rb").read(),
                        "Levantamento impressões_v8.xlsx", origem="semente")
    """
    if len(dados) > TAMANHO_MAXIMO_BASE:
        raise LevantamentoError("Arquivo grande demais para ser o levantamento (limite de 20 MB).")
    try:
        base = validar_planilha(dados)
    except PlanilhaError as e:
        raise LevantamentoError(f"Planilha recusada: {e}") from e

    with _lock:
        pasta().mkdir(parents=True, exist_ok=True)
        backup = _backup_da_base("substituida por envio de nova base")
        tmp = caminho_base().with_suffix(".tmp")
        tmp.write_bytes(dados)
        tmp.replace(caminho_base())
        agora = _iso(_agora_utc())
        meta = {"enviada_em": agora, "atualizada_em": agora, "origem": origem, "nome_original": nome_original}
        _gravar_json(pasta() / "base.json", meta)
    return {
        "ano": base.ano,
        "meses_preenchidos": [_chave_mes(base.ano, m) for m in base.meses_preenchidos()],
        "blocos": len(base.blocos),
        "linhas": len(base.itens),
        "backup": backup,
    }


# ─────────────────────────────────────────────────────────────────────────
#  Geracao
# ─────────────────────────────────────────────────────────────────────────

def _interpretar_mes(mes: str) -> tuple[int, int]:
    m = re.fullmatch(r"(\d{4})-(\d{2})", (mes or "").strip())
    if not m or not 1 <= int(m.group(2)) <= 12:
        raise LevantamentoError("Mes invalido: use o formato AAAA-MM (ex.: 2026-09).")
    return int(m.group(1)), int(m.group(2))


def _unidade_do_departamento(dep: str | None) -> str:
    partes = (dep or "").rsplit(" — ", 1)
    return partes[1].strip() if len(partes) == 2 else ""


def _anomalias_de_referencia(pacote: Pacote) -> list[str]:
    """
    Formulas das OUTRAS abas que apontam para a Contabilizacao numa coluna
    diferente das vizinhas da mesma linha (ex.: '3 meses'!H3 soma M49
    enquanto as vizinhas andam uma coluna por mes e dariam K49). Nao sao
    corrigidas — so avisadas.
    """
    import xml.etree.ElementTree as ET

    from app.services.planilha_levantamento import NS, NS_R, _coluna

    avisos = []
    wb = ET.fromstring(pacote.ler("xl/workbook.xml"))
    rels = ET.fromstring(pacote.ler("xl/_rels/workbook.xml.rels"))
    alvos = {r.get("Id"): r.get("Target") for r in rels}
    ref_re = re.compile(r"'?" + re.escape(SHEET_NAME) + r"'?!\$?([A-Z]{1,3})\$?\d+")
    for sheet in wb.findall(".//m:sheets/m:sheet", NS):
        nome = sheet.get("name")
        if nome in (SHEET_NAME, ABA_NOVOS):
            continue
        alvo = alvos.get(sheet.get(f"{{{NS_R}}}id"), "")
        parte = alvo.lstrip("/") if alvo.startswith("/") else "xl/" + alvo
        if not pacote.existe(parte):
            continue
        root = ET.fromstring(pacote.ler(parte))
        por_linha: dict[int, list[tuple[str, int]]] = {}
        for c in root.iter(f"{{{NS['m']}}}c"):
            f = c.find("m:f", NS)
            if f is None or not f.text:
                continue
            cols = {_coluna(x) for x in ref_re.findall(f.text)}
            if len(cols) != 1:
                continue
            col_celula, linha = split_ref(c.get("r"))
            por_linha.setdefault(linha, []).append((c.get("r"), cols.pop() - col_celula))
        for linha, celulas in por_linha.items():
            if len(celulas) < 3:
                continue
            comum, vezes = Counter(d for _, d in celulas).most_common(1)[0]
            if vezes < len(celulas) - 1 or vezes == len(celulas):
                continue
            for ref, desloc in celulas:
                if desloc != comum:
                    col_celula = split_ref(ref)[0]
                    avisos.append(
                        f"Aba '{nome}' {ref}: aponta para a coluna {letra_coluna(col_celula + desloc)} da "
                        f"'{SHEET_NAME}', mas as vizinhas da linha dariam a coluna "
                        f"{letra_coluna(col_celula + comum)}. Fórmula não alterada — confira na planilha."
                    )
    return avisos


def gerar(session: Session, mes: str, agora: datetime | None = None, automatico: bool = False) -> dict:
    """
    Gera o levantamento do mes `mes` ("2026-09") a partir da base. Devolve
    o relatorio (e grava o arquivo em gerados/). Periodo fechado substitui a
    base; periodo em andamento gera previa.
    """
    with _lock:
        return _gerar(session, mes, agora or _agora_utc(), automatico)


def _gerar(session: Session, mes: str, agora: datetime, automatico: bool) -> dict:
    ano_pedido, idx_mes = _interpretar_mes(mes)
    base = _ler_base()
    if ano_pedido != base.ano:
        raise LevantamentoError(
            f"A planilha base e de {base.ano}; para gerar {mes} envie a planilha base de {ano_pedido}."
        )
    mes_nome = MONTH_COLUMNS[idx_mes - 1]
    inicio_local, fim_local, texto_periodo, do_resumo = base.periodo_local(mes_nome)
    inicio, fim = _para_utc(inicio_local), _para_utc(fim_local)
    fechado = fim <= agora
    previa = not fechado
    if inicio > agora:
        raise LevantamentoError(f"O periodo de {mes_nome} ({texto_periodo or inicio_local.date()}) ainda nao comecou.")

    avisos: list[str] = []
    if not do_resumo:
        avisos.append(
            f"Periodo de {mes_nome} nao encontrado na tabela do topo da planilha — usado do dia 4 ao dia 3 "
            f"({inicio_local:%d/%m/%y} a {fim_local - timedelta(days=1):%d/%m/%y})."
        )
    if previa:
        avisos.append(
            f"Periodo em andamento (fecha em {fim_local - timedelta(days=1):%d/%m/%Y}): arquivo gerado como prévia, "
            "a planilha base nao foi alterada."
        )
    preenchidos = base.meses_preenchidos()
    vazios_antes = [m for m in MONTH_COLUMNS[: idx_mes - 1] if m not in preenchidos]
    if vazios_antes and preenchidos:
        ultimo = max(MONTH_COLUMNS.index(m) for m in preenchidos)
        pulados = [m for m in vazios_antes if MONTH_COLUMNS.index(m) > ultimo]
        if pulados:
            avisos.append(f"Meses anteriores ainda vazios na base: {', '.join(pulados)}.")

    # Paginas por equipamento no periodo.
    mp = month_pages(session, inicio, fim)
    printers = session.exec(select(Printer)).all()
    por_id = {p.id: p for p in printers}
    por_ip, por_serial = indices_do_banco(printers)
    medidos: dict[str, int] = {}
    for pid in mp.pages:
        p = por_id.get(pid)
        medidos[_device_key(pid, p.ip if p else None)] = pid

    primeira_leitura = session.exec(select(func.min(PrinterReading.timestamp))).one()
    if isinstance(primeira_leitura, str):
        primeira_leitura = datetime.fromisoformat(primeira_leitura)
    if primeira_leitura and primeira_leitura > inicio:
        local = primeira_leitura.replace(tzinfo=timezone.utc).astimezone(FUSO)
        avisos.append(
            f"A coleta do sistema comecou em {local:%d/%m/%Y}, depois do inicio do periodo: o trecho anterior foi "
            "estimado pela media diaria de cada equipamento (ver 'estimadas')."
        )

    pacote = Pacote(base.dados)
    parte_aba = caminho_da_aba(pacote.zin, SHEET_NAME)
    aba = PlanilhaXml(pacote.texto(parte_aba))

    itens = base.itens
    repeticoes = Counter(limpar(i.ip) for i in itens if IPV4_RE.match(limpar(i.ip)))
    usados: dict[str, int] = {}
    preenchidas = 0
    total_paginas = 0
    total_estimadas = 0
    vazias: list[dict] = []
    mantidas: list[dict] = []
    blocos_sem_coluna = []

    for bloco in base.blocos:
        col = bloco.colunas_mes.get(mes_nome)
        if col is None:
            blocos_sem_coluna.append(bloco.titulo)
            continue
        letra = letra_coluna(col)
        vizinhas = [c for c in (col - 1, col + 1, col - 2) if c >= 0]
        for item in bloco.itens:
            ref = f"{letra}{item.linha_num}"
            linha_info = {
                "unidade": bloco.titulo,
                "linha": item.linha_num,
                "celula": ref,
                "ip": item.ip or None,
                "modelo": item.modelo,
                "serial": item.serial,
                "departamento": item.departamento,
            }
            cas = localizar_equipamento(item, por_ip, por_serial, repeticoes)
            motivo = None
            pid = None
            if cas.situacao == "ok" and cas.filas:
                chaves = _chaves_do_equipamento(cas, por_serial)
                ja = next((k for k in chaves if k in usados), None)
                if ja is not None:
                    motivo = f"o mesmo equipamento ja preencheu a linha {usados[ja]}"
                else:
                    for k in chaves:
                        usados[k] = item.linha_num
                    # O mesmo serial lido em mais de um IP no periodo (em
                    # 22/09/2026 a TASKalfa L7S5612329 respondia em 10.22.0.73
                    # e 10.20.7.220 ao mesmo tempo): e UM contador — vale o de
                    # maior total, como em monthly_report._one_per_device.
                    medidas = [medidos[k] for k in chaves if k in medidos]
                    if medidas:
                        pid = max(medidas, key=lambda x: (mp.pages[x], -x))
                        if len(medidas) > 1:
                            ips = ", ".join(sorted(por_id[x].ip for x in medidas if x in por_id))
                            avisos.append(
                                f"Serial {cas.serial} lido em mais de um IP no período ({ips}): linha {item.linha_num} "
                                "usa o de maior contagem, sem somar."
                            )
                    else:
                        motivo = _motivo_sem_leitura(session, cas.filas)
            elif cas.situacao == "ambiguo":
                motivo = "IP repetido na planilha e sem serial que identifique o equipamento"
            elif cas.situacao == "conflito":
                # O equipamento do IP e outro: ele entra em "Novos no sistema".
                motivo = f"no IP da planilha o sistema lê outro equipamento (serial {', '.join(cas.seriais_no_ip)})"
            else:
                sem_ip = not IPV4_RE.match(limpar(item.ip))
                motivo = "não encontrado no sistema" + (" (sem IP na planilha)" if sem_ip else "")

            if pid is not None:
                paginas = mp.pages[pid]
                aba.gravar_numero(ref, paginas, vizinhas)
                preenchidas += 1
                total_paginas += paginas
                total_estimadas += mp.estimated.get(pid, 0)
                continue

            valor_base = base.celulas.get(item.linha_num, {}).get(col)
            if valor_base not in (None, ""):
                # Valor digitado na base para este mes (base editada e
                # reenviada): o sistema nao tem nada melhor, fica o da base.
                mantidas.append({**linha_info, "valor": valor_base, "motivo": motivo})
                continue
            aba.limpar(ref, vizinhas)
            vazias.append({**linha_info, "motivo": motivo})

    if blocos_sem_coluna:
        avisos.append(f"Blocos sem a coluna '{mes_nome}' no cabecalho (nao preenchidos): {', '.join(blocos_sem_coluna)}.")

    # Formulas: Total de cada bloco e resumo do topo, no mes gerado e nos
    # meses seguintes ainda vazios.
    com_dado = set(preenchidos) | {m for i in itens for m in i.meses}
    meses_formula = [mes_nome] + [m for m in MONTH_COLUMNS[idx_mes:] if m not in com_dado]
    correcoes: list[dict] = []
    for m in meses_formula:
        totais = []
        for bloco in base.blocos:
            col = bloco.colunas_mes.get(m)
            if col is None or bloco.linha_total is None or bloco.ultima_linha < bloco.primeira_linha:
                continue
            letra = letra_coluna(col)
            ref = f"{letra}{bloco.linha_total}"
            nova = f"SUM({letra}{bloco.primeira_linha}:{letra}{bloco.ultima_linha})"
            antes = aba.formula(ref)
            aba.gravar_formula(ref, nova, [c for c in (col - 1, col + 1) if c >= 0])
            if antes != nova:
                correcoes.append({"celula": ref, "bloco": bloco.titulo, "antes": f"={antes}" if antes else None,
                                  "depois": f"={nova}"})
            totais.append(ref)
        r = base.resumo.get(m)
        if r and r.coluna_total is not None and totais:
            ref = f"{letra_coluna(r.coluna_total)}{r.linha}"
            nova = f"SUM({','.join(totais)})"
            antes = aba.formula(ref)
            aba.gravar_formula(ref, nova, [r.coluna_total - 1])
            if antes != nova:
                correcoes.append({"celula": ref, "bloco": "Resumo do topo", "antes": f"={antes}" if antes else None,
                                  "depois": f"={nova}"})

    pacote.gravar(parte_aba, aba.serializar())

    # Aba "Novos no sistema".
    servidores = {s.host: s for s in session.exec(select(PrintServer)).all()}
    unidades = {u.id: u.name for u in session.exec(select(Unit)).all()}
    novos = []
    for chave, pid in medidos.items():
        if chave in usados:
            continue
        p = por_id.get(pid)
        if p is None:
            continue
        srv = servidores.get(p.server)
        unidade = (unidades.get(srv.unit_id) if srv and srv.unit_id else None) or _unidade_do_departamento(p.department)
        novos.append({
            "ip": p.ip,
            "modelo": p.snmp_model or p.model,
            "serial": p.serial_number,
            "servidor": (srv.name or srv.host) if srv else (p.server or None),
            "unidade": unidade or None,
            "departamento": p.department or None,
            "tipo": p.printer_type,
            "fila": p.name,
            "ativa": p.active,
            "paginas": mp.pages[pid],
            "estimadas": mp.estimated.get(pid, 0),
        })
    novos.sort(key=lambda n: (n["unidade"] or "~", n["servidor"] or "", n["ip"] or ""))

    remover_aba(pacote, ABA_NOVOS)
    estilo_cab = None
    primeiro = base.blocos[0]
    estilo_cab = aba.estilo(f"A{primeiro.linha_cabecalho}")
    periodo_txt = texto_periodo or f"{inicio_local:%d/%m/%y} a {fim_local - timedelta(days=1):%d/%m/%y}"
    linhas_novos = [
        [f"Equipamentos medidos pelo sistema que não estão na aba '{SHEET_NAME}' — {mes_nome}/{base.ano} "
         f"(período {periodo_txt}){' — PRÉVIA' if previa else ''}"],
        [],
        ["IP", "Modelo", "Serial", "Unidade / servidor", "Departamento", "Tipo", "Fila", "Páginas do mês",
         "Estimadas"],
    ]
    for n in novos:
        unidade_srv = " / ".join(x for x in (n["unidade"], n["servidor"]) if x)
        linhas_novos.append([n["ip"], n["modelo"], n["serial"], unidade_srv, n["departamento"], n["tipo"],
                             n["fila"], n["paginas"], n["estimadas"] or None])
    if not novos:
        linhas_novos.append(["Nenhum — todo equipamento medido no período está na planilha."])
    adicionar_aba(pacote, ABA_NOVOS, montar_aba_simples(
        linhas_novos, estilo_cab, 3, larguras=[15, 26, 16, 32, 36, 10, 30, 14, 10]))

    forcar_recalculo(pacote)
    remover_calc_chain(pacote)
    saida = pacote.salvar()

    # Conferencia: o arquivo abre, cada XML parseia, e relendo a aba os
    # valores sao os que acabamos de gravar.
    problemas = validar_pacote(saida)
    try:
        relida = _Base(saida)
        ler_aba(saida, ABA_NOVOS)
    except PlanilhaError as e:
        problemas.append(f"releitura falhou: {e}")
        relida = None
    if relida is not None:
        soma = sum(i.meses.get(mes_nome, 0) for i in relida.itens)
        esperado = total_paginas + sum(int(float(v["valor"])) for v in mantidas if _e_numero(v["valor"]))
        if soma != esperado:
            problemas.append(f"releitura: {mes_nome} soma {soma}, esperado {esperado}")
        if len(relida.itens) != len(itens):
            problemas.append(f"releitura: {len(relida.itens)} linhas de impressora, esperado {len(itens)}")
    if problemas:
        logger.error("Levantamento %s descartado: %s", mes, problemas)
        raise LevantamentoError("O arquivo gerado nao passou na conferencia: " + "; ".join(problemas[:5]))

    avisos.extend(_anomalias_de_referencia(pacote))
    if total_estimadas:
        avisos.append(f"{total_estimadas} das {total_paginas} páginas são estimadas (início do período sem leitura).")

    nome = nome_arquivo(mes_nome, base.ano, previa)
    pasta_gerados().mkdir(parents=True, exist_ok=True)
    destino = pasta_gerados() / nome
    tmp = destino.with_name(destino.name + ".tmp")
    tmp.write_bytes(saida)
    tmp.replace(destino)

    base_atualizada = False
    if fechado:
        meta = _ler_json(pasta() / "base.json", {})
        if meta.get("origem") != "gerado":
            _backup_da_base(f"substituida pelo levantamento de {mes_nome}/{base.ano}")
        shutil.copyfile(destino, caminho_base())
        meta.update({"atualizada_em": _iso(agora), "origem": "gerado", "arquivo": nome, "mes": mes})
        meta.setdefault("enviada_em", _iso(agora))
        _gravar_json(pasta() / "base.json", meta)
        base_atualizada = True

    relatorio = {
        "mes": mes,
        "mes_nome": mes_nome,
        "ano": base.ano,
        "arquivo": nome,
        "previa": previa,
        "automatico": automatico,
        "gerado_em": _iso(agora),
        "periodo": {
            "texto": periodo_txt,
            "inicio": inicio_local.date().isoformat(),
            "fim": (fim_local - timedelta(days=1)).date().isoformat(),
            "inicio_utc": _iso(inicio),
            "fim_utc_exclusivo": _iso(fim),
            "fechado": fechado,
        },
        "preenchidas": {"linhas": preenchidas, "paginas": total_paginas, "estimadas": total_estimadas},
        "vazias": vazias,
        "mantidas": mantidas,
        "novos": novos,
        "correcoes_formula": correcoes,
        "base_atualizada": base_atualizada,
        "avisos": avisos,
    }
    _registrar_arquivo({"nome": nome, "mes": mes, "gerado_em": _iso(agora), "previa": previa,
                        "tipo": "gerado", "automatico": automatico, "relatorio": relatorio})
    logger.info(
        "Levantamento gerado | %s | previa=%s preenchidas=%s paginas=%s vazias=%s novos=%s base_atualizada=%s",
        nome, previa, preenchidas, total_paginas, len(vazias), len(novos), base_atualizada,
    )
    return relatorio


def _motivo_sem_leitura(session: Session, filas: list) -> str:
    """
    Por que o equipamento da linha nao tem numero no periodo, dito de um
    jeito que ajude a decidir o que fazer (23/09/2026): nunca respondeu,
    parou de responder em tal dia, ou saiu dos print servers.
    """
    ids = [f.id for f in filas]
    ultima = session.exec(
        select(func.max(PrinterReading.timestamp))
        .where(PrinterReading.printer_id.in_(ids))
        .where((PrinterReading.counter_std > 0) | (PrinterReading.counter_vendor > 0) | (PrinterReading.page_count > 0))
    ).first()
    fora_dos_servidores = all(not f.active for f in filas)
    if ultima:
        quando = (ultima - timedelta(hours=3)).strftime("%d/%m/%Y")
        texto = f"sem leitura no período (último contador lido em {quando})"
    else:
        texto = "não responde na rede a partir do servidor do sistema (nunca lida)"
    if fora_dos_servidores:
        texto += "; fila não existe mais nos print servers"
    return texto


def _chaves_do_equipamento(cas, por_serial: dict) -> list[str]:
    """
    Chaves de equipamento (monthly_report._device_key) de uma linha casada:
    a do IP casado e, quando o serial e valido, a de todo cadastro com o
    mesmo serial confirmado por SNMP — o aparelho pode ter mudado de IP ou
    responder em dois. Nenhuma delas pode ir para outra linha nem para
    "Novos no sistema".
    """
    chaves = [_device_key(cas.filas[0].id, cas.filas[0].ip)]
    if cas.serial_valido:
        for p in por_serial.get(cas.serial.upper(), []):
            if p.snmp_updated_at is None:
                continue
            k = _device_key(p.id, p.ip)
            if k not in chaves:
                chaves.append(k)
    return chaves


def _e_numero(valor) -> bool:
    try:
        float(valor)
        return True
    except (TypeError, ValueError):
        return False


def relatorio_do_arquivo(nome: str) -> dict | None:
    for item in _indice():
        if item.get("nome") == nome:
            return item.get("relatorio")
    return None


# ─────────────────────────────────────────────────────────────────────────
#  Geracao automatica (scheduler)
# ─────────────────────────────────────────────────────────────────────────

def _pendente(agora: datetime) -> tuple[str, datetime] | None:
    if not caminho_base().exists():
        return None
    try:
        base = _Base(caminho_base().read_bytes())
    except PlanilhaError:
        return None
    ultimo = None
    fim_ultimo = None
    for mes_nome in MONTH_COLUMNS:
        _, fim, _, _ = base.periodo_local(mes_nome)
        if _para_utc(fim) <= agora:
            ultimo, fim_ultimo = mes_nome, _para_utc(fim)
    if ultimo is None or ultimo in base.meses_preenchidos():
        return None
    chave = _chave_mes(base.ano, ultimo)
    ja = {i.get("mes") for i in _indice() if i.get("tipo", "gerado") == "gerado" and not i.get("previa")}
    if chave in ja:
        return None
    return chave, fim_ultimo


def mes_fechado_pendente(agora: datetime | None = None) -> str | None:
    """
    O ultimo periodo JA FECHADO da base, se ainda nao foi gerado (nem esta
    preenchido na base). None quando nao ha nada a fazer ou nao ha base.
    """
    pendente = _pendente(agora or _agora_utc())
    return pendente[0] if pendente else None


def gerar_pendente(session: Session, agora: datetime | None = None) -> dict | None:
    """
    Gera o periodo fechado pendente (mes_fechado_pendente), se houver.

    Espera existir leitura DEPOIS do fim do periodo — e ela que da o pedaco
    final (rateio do salto que atravessa o limite, ver month_pages). Na
    subida de uma maquina que ficou desligada, a primeira coleta ainda nao
    rodou: a geracao fica para o proximo disparo, como o fechamento mensal
    (monthly_report.close_pending_months).
    """
    agora = agora or _agora_utc()
    pendente = _pendente(agora)
    if pendente is None:
        return None
    mes, fim = pendente
    ultima = session.exec(select(func.max(PrinterReading.timestamp))).one()
    if isinstance(ultima, str):
        ultima = datetime.fromisoformat(ultima)
    if ultima is None or ultima < fim:
        logger.info("Levantamento %s aguardando a primeira leitura depois do fim do periodo", mes)
        return None
    return gerar(session, mes, agora=agora, automatico=True)


if __name__ == "__main__":
    # Semear/trocar a base pela linha de comando (a mesma validacao do upload):
    #   .\venv\Scripts\python.exe -m app.services.levantamento "C:\...\Levantamento impressões_v8.xlsx"
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) != 2:
        print("uso: python -m app.services.levantamento <planilha.xlsx>")
        raise SystemExit(2)
    origem_arquivo = Path(sys.argv[1])
    print(substituir_base(origem_arquivo.read_bytes(), origem_arquivo.name, origem="semente"))
    print(f"Base gravada em {caminho_base()}")
