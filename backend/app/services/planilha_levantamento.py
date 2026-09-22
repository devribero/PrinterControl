"""
Leitura da planilha "Levantamento impressoes" (aba "Contabilizacao mensal").

Compartilhado por dois consumidores:

  - import_historico_planilha.py — importa os meses ja fechados da planilha
    para PrinterMonthly (Fase 12);
  - services/levantamento.py — gera a planilha do mes seguinte a partir da
    ultima gerada (22/09/2026).

Antes vivia dentro do importador; foi extraido para que os dois leiam a
planilha, reconhecam os blocos e casem linha <-> equipamento do mesmo jeito.

So biblioteca padrao (zipfile + xml.etree): sem openpyxl no venv.
"""
import os
import re
import xml.etree.ElementTree as ET
import zipfile
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

SHEET_NAME = "Contabilização mensal"
MONTH_COLUMNS = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
IPV4_RE = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")

# A coluna "Serial" do bloco da Vila Olimpia traz o MAC de algumas Pantum,
# nao o numero de serie: gravar isso como serial enganaria quem le.
MAC_RE = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$")


class PlanilhaError(Exception):
    pass


# ─────────────────────────────────────────────────────────────────────────
#  Leitura crua
# ─────────────────────────────────────────────────────────────────────────

def _cell_value(cell, shared):
    t = cell.get("t")
    v = cell.find("m:v", NS)
    if v is None:
        inline = cell.find("m:is/m:t", NS)
        return inline.text if inline is not None else None
    if t == "s":
        return shared[int(v.text)]
    return v.text


def _coluna(ref: str) -> int:
    """'D19' -> 3 (A=0)."""
    letras = re.match(r"[A-Z]+", ref).group(0)
    n = 0
    for ch in letras:
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def letra_coluna(idx: int) -> str:
    """3 -> 'D' (A=0)."""
    letras = ""
    n = idx + 1
    while n:
        n, resto = divmod(n - 1, 26)
        letras = chr(65 + resto) + letras
    return letras


def caminho_da_aba(z: zipfile.ZipFile, nome: str = SHEET_NAME) -> str:
    """'xl/worksheets/sheet1.xml' da aba `nome`; PlanilhaError se nao existir."""
    wb_root = ET.fromstring(z.read("xl/workbook.xml"))
    rels_root = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rid_to_target = {rel.get("Id"): rel.get("Target") for rel in rels_root}
    for sheet in wb_root.findall(".//m:sheets/m:sheet", NS):
        if sheet.get("name") == nome:
            alvo = rid_to_target[sheet.get(f"{{{NS_R}}}id")]
            return alvo.lstrip("/") if alvo.startswith("/") else "xl/" + alvo
    nomes = [s.get("name") for s in wb_root.findall(".//m:sheets/m:sheet", NS)]
    raise PlanilhaError(f"Aba {nome!r} nao encontrada. Abas disponiveis: {nomes}")


def textos_compartilhados(z: zipfile.ZipFile) -> list[str]:
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        for si in root.findall("m:si", NS):
            # So os <t> do texto; os de <rPh> (guia fonetica) nao entram.
            partes = [t.text or "" for t in si.findall("m:t", NS)]
            partes += [t.text or "" for t in si.findall("m:r/m:t", NS)]
            shared.append("".join(partes))
    return shared


def ler_aba(fonte, nome: str = SHEET_NAME) -> "OrderedDict[int, dict[int, object]]":
    """
    {numero_da_linha: {coluna: valor}} da aba, na ordem do XML. Toda <row>
    entra, mesmo sem celula; celula sem valor entra como None.

    Cada celula vai para a COLUNA da sua referencia (A1, D19...), nao para
    a proxima posicao da lista. O XML so traz as celulas preenchidas: ler
    em sequencia fazia uma celula vazia no meio da linha (um serial em
    branco) escorregar todos os meses seguintes uma coluna para a
    esquerda — Marco virava Fevereiro sem erro nenhum. Corrigido em
    21/09/2026, junto com a v8 da planilha.

    `fonte`: caminho, bytes ou arquivo aberto.
    """
    if isinstance(fonte, (bytes, bytearray)):
        import io
        fonte = io.BytesIO(fonte)
    elif isinstance(fonte, (str, os.PathLike)) and not os.path.exists(fonte):
        raise PlanilhaError(f"Arquivo nao encontrado: {fonte}")
    try:
        z = zipfile.ZipFile(fonte)
    except zipfile.BadZipFile as e:
        raise PlanilhaError("O arquivo nao e um .xlsx valido (nao abriu como zip).") from e

    with z:
        try:
            shared = textos_compartilhados(z)
            alvo = caminho_da_aba(z, nome)
            sroot = ET.fromstring(z.read(alvo))
        except (KeyError, ET.ParseError) as e:
            raise PlanilhaError(f"O arquivo nao tem a estrutura de uma planilha do Excel ({e}).") from e

    linhas: "OrderedDict[int, dict[int, object]]" = OrderedDict()
    for posicao, row in enumerate(sroot.findall(".//m:sheetData/m:row", NS), start=1):
        numero = int(row.get("r") or posicao)
        valores: dict[int, object] = {}
        for c in row.findall("m:c", NS):
            ref = c.get("r")
            col = _coluna(ref) if ref else len(valores)
            valores[col] = _cell_value(c, shared)
        linhas[numero] = valores
    return linhas


def _ler_planilha(caminho: str):
    """Linhas da aba SHEET_NAME como listas ([[celula, ...], ...]), na ordem do XML."""
    linhas = []
    for valores in ler_aba(caminho).values():
        largura = max(valores) + 1 if valores else 0
        linhas.append([valores.get(i) for i in range(largura)])
    return linhas


# ─────────────────────────────────────────────────────────────────────────
#  Reconhecimento de linhas
# ─────────────────────────────────────────────────────────────────────────

def _e_cabecalho_de_site(linha: list) -> bool:
    """Uma linha de cabecalho de site tem EXATAMENTE uma celula preenchida (o nome)."""
    preenchidas = [v for v in linha if v not in (None, "")]
    return len(preenchidas) == 1 and isinstance(preenchidas[0], str)


def _e_linha_ip(linha: list) -> bool:
    return bool(linha) and linha[0] == "IP"


def _posicao_total(linha: list) -> int | None:
    """
    Coluna do rotulo "Total"/"Total:" nas primeiras 4 celulas, ou None.

    Na planilha real o rotulo fica na coluna do Departamento (D) e os meses
    comecam na seguinte; numa leitura sem posicao (linhas de teste) ele fica
    na primeira. Em ambos os casos os meses comecam logo depois do rotulo.
    """
    for i, v in enumerate(linha[:4]):
        if isinstance(v, str) and v.strip().lower().startswith("total"):
            return i
    return None


def _e_linha_total(linha: list) -> bool:
    return _posicao_total(linha) is not None


def _num(valor) -> int | None:
    if valor in (None, "", "-"):
        return None
    try:
        return int(round(float(valor)))
    except (TypeError, ValueError):
        return None


def limpar(valor) -> str:
    """Texto de celula sem espacos nas pontas (inclui o \\xa0 que vem colado em alguns seriais)."""
    return str(valor).strip() if valor is not None else ""


class LinhaImpressora:
    __slots__ = ("site", "ip", "modelo", "serial", "departamento", "meses", "linha_num")

    def __init__(self, site, ip, modelo, serial, departamento, meses, linha_num):
        self.site = site
        self.ip = ip
        self.modelo = modelo
        self.serial = serial
        self.departamento = departamento
        self.meses = meses  # {"Janeiro": 162, ...} so os preenchidos
        self.linha_num = linha_num


def _parse_blocos(linhas: list) -> tuple[list[LinhaImpressora], list[str]]:
    """
    Percorre a planilha inteira e devolve (linhas_de_impressora, avisos).
    avisos inclui: linhas com identificador que nao e IPv4 (puladas), e
    blocos cujo somatorio calculado diverge da linha "Total:" da propria
    planilha (possivel erro de transcricao — nao impede a importacao,
    so avisa).
    """
    resultado: list[LinhaImpressora] = []
    avisos: list[str] = []

    site_atual = None
    dentro_do_bloco = False
    soma_bloco: dict[str, int] = {}

    for i, linha in enumerate(linhas, start=1):
        if not linha or all(v in (None, "") for v in linha):
            continue

        if _e_cabecalho_de_site(linha):
            site_atual = next(v for v in linha if v not in (None, ""))
            dentro_do_bloco = False
            soma_bloco = {}
            continue

        if _e_linha_ip(linha):
            dentro_do_bloco = True
            soma_bloco = {mes: 0 for mes in MONTH_COLUMNS}
            continue

        if not dentro_do_bloco:
            continue

        if _e_linha_total(linha):
            inicio_meses = _posicao_total(linha) + 1
            for idx, mes in enumerate(MONTH_COLUMNS):
                col = inicio_meses + idx
                if col < len(linha):
                    total_planilha = _num(linha[col])
                    if total_planilha is not None and total_planilha != soma_bloco[mes]:
                        avisos.append(
                            f"[{site_atual}] Total de {mes} na planilha ({total_planilha}) "
                            f"difere da soma das impressoras que importei ({soma_bloco[mes]}) — confira a linha {i}."
                        )
            dentro_do_bloco = False
            continue

        ip_bruto = (linha[0] or "").strip() if isinstance(linha[0], str) else linha[0]
        if not ip_bruto or not IPV4_RE.match(str(ip_bruto)):
            avisos.append(f"[{site_atual}] linha {i}: identificador {ip_bruto!r} nao e um IP valido — pulada.")
            continue

        modelo = linha[1] if len(linha) > 1 else None
        serial = linha[2] if len(linha) > 2 else None
        departamento = linha[3] if len(linha) > 3 else None

        meses = {}
        for idx, mes in enumerate(MONTH_COLUMNS):
            col = 4 + idx
            if col >= len(linha):
                continue
            valor = _num(linha[col])
            if valor is not None:
                meses[mes] = valor
                soma_bloco[mes] += valor

        resultado.append(LinhaImpressora(site_atual, str(ip_bruto), modelo, serial, departamento, meses, i))

    return resultado, avisos


# ─────────────────────────────────────────────────────────────────────────
#  Blocos com posicao real (para escrever de volta na planilha)
# ─────────────────────────────────────────────────────────────────────────

@dataclass
class Bloco:
    """Um bloco de unidade: titulo, cabecalho (IP...), impressoras, Total."""

    titulo: str
    linha_titulo: int | None
    linha_cabecalho: int
    linha_total: int | None
    colunas_mes: dict[str, int]  # {"Setembro": 12} (A=0)
    itens: list[LinhaImpressora] = field(default_factory=list)

    @property
    def primeira_linha(self) -> int:
        return self.linha_cabecalho + 1

    @property
    def ultima_linha(self) -> int | None:
        return self.linha_total - 1 if self.linha_total else None


def blocos_da_aba(celulas: "OrderedDict[int, dict[int, object]]") -> list[Bloco]:
    """
    Blocos da aba com o NUMERO DE LINHA real de cada coisa (ler_aba).

    Diferente de _parse_blocos (que e do importador e pula o que nao tem IP),
    aqui entra TODA linha preenchida entre o cabecalho e o Total — inclusive
    "Estoque", "Backup", "-" e IP em branco: elas existem na planilha e o
    gerador precisa saber que ficaram sem valor. As colunas dos meses vem do
    proprio cabecalho do bloco ("Janeiro".."Dezembro"), nao de posicao fixa.
    """
    blocos: list[Bloco] = []
    titulo_atual: tuple[str, int] | None = None
    atual: Bloco | None = None

    for numero, valores in celulas.items():
        preenchidas = {c: v for c, v in valores.items() if v not in (None, "")}
        if not preenchidas:
            continue
        largura = max(valores) + 1 if valores else 0
        linha = [valores.get(i) for i in range(largura)]

        if atual is None:
            if _e_cabecalho_de_site(linha):
                titulo_atual = (limpar(next(iter(preenchidas.values()))), numero)
                continue
            if _e_linha_ip(linha):
                colunas_mes = {
                    limpar(v): c for c, v in preenchidas.items() if limpar(v) in MONTH_COLUMNS
                }
                titulo, linha_titulo = titulo_atual or ("(sem titulo)", None)
                atual = Bloco(titulo, linha_titulo, numero, None, colunas_mes)
                titulo_atual = None
            continue

        # Dentro de um bloco.
        if _e_linha_total(linha):
            atual.linha_total = numero
            blocos.append(atual)
            atual = None
            continue
        if _e_linha_ip(linha):  # cabecalho novo sem Total no anterior
            blocos.append(atual)
            colunas_mes = {limpar(v): c for c, v in preenchidas.items() if limpar(v) in MONTH_COLUMNS}
            atual = Bloco("(sem titulo)", None, numero, None, colunas_mes)
            continue

        meses = {}
        for mes, col in atual.colunas_mes.items():
            n = _num(valores.get(col))
            if n is not None:
                meses[mes] = n
        atual.itens.append(LinhaImpressora(
            atual.titulo,
            limpar(valores.get(0)),
            limpar(valores.get(1)) or None,
            limpar(valores.get(2)) or None,
            limpar(valores.get(3)) or None,
            meses,
            numero,
        ))

    if atual is not None:
        blocos.append(atual)
    return blocos


# ─────────────────────────────────────────────────────────────────────────
#  Tabela de periodos do topo ("Mes | Periodo | Impressoes")
# ─────────────────────────────────────────────────────────────────────────

_PERIODO_RE = re.compile(r"(\d{2})/(\d{2})/(\d{2,4})\s*a\s*(\d{2})/(\d{2})/(\d{2,4})")


def interpretar_periodo(texto) -> tuple[datetime, datetime] | None:
    """
    "04/09/26 a 03/10/26" -> (2026-09-04, 2026-10-04). Fim EXCLUSIVO (dia
    seguinte ao ultimo). Datas locais, sem fuso. None se nao der para ler.
    """
    m = _PERIODO_RE.search(str(texto or ""))
    if not m:
        return None
    d1, m1, a1, d2, m2, a2 = (int(x) for x in m.groups())
    a1 = a1 + 2000 if a1 < 100 else a1
    a2 = a2 + 2000 if a2 < 100 else a2
    try:
        inicio = datetime(a1, m1, d1)
        fim = datetime(a2, m2, d2) + timedelta(days=1)
    except ValueError:
        return None
    if fim <= inicio:
        return None
    return inicio, fim


def periodos_da_planilha(linhas: list, ano: int) -> dict[str, tuple[datetime, datetime]]:
    """
    Tabela "Mes | Periodo | Impressoes" do topo da aba: {"Agosto": (04/08, 04/09)}.

    A planilha fecha cada mes no dia 3 do seguinte ("04/08/26 a 03/09/26").
    O fim devolvido e EXCLUSIVO (dia seguinte ao ultimo), no mesmo formato
    dos meses do sistema. Mes sem periodo legivel fica de fora e usa o mes
    do calendario.
    """
    resultado: dict[str, tuple[datetime, datetime]] = {}
    for linha in linhas:
        valores = [str(v).strip() for v in linha if v not in (None, "")]
        mes = next((v for v in valores if v in MONTH_COLUMNS), None)
        periodo = next((p for v in valores if (p := interpretar_periodo(v))), None)
        if not mes or not periodo:
            continue
        inicio, fim = periodo
        if inicio.year == ano or fim.year == ano:
            resultado.setdefault(mes, (inicio, fim))
    return resultado


@dataclass
class ResumoMes:
    """Uma linha da tabela do topo: onde fica o mes, o texto do periodo e a celula de total."""

    mes: str
    linha: int
    coluna_total: int | None
    texto_periodo: str | None
    periodo: tuple[datetime, datetime] | None


def resumo_da_aba(celulas: "OrderedDict[int, dict[int, object]]") -> dict[str, ResumoMes]:
    """
    Tabela do topo com posicao: {"Setembro": ResumoMes(linha=11, coluna_total=5, ...)}.

    A coluna do total vem do cabecalho "Impressoes" da tabela; o periodo, da
    celula da mesma linha que parece "dd/mm/aa a dd/mm/aa". So a PRIMEIRA
    ocorrencia de cada mes conta — os cabecalhos dos blocos tambem tem
    "Janeiro".."Dezembro", mas em linha, nao um por linha com periodo.
    """
    coluna_total = None
    resultado: dict[str, ResumoMes] = {}
    for numero, valores in celulas.items():
        textos = {c: limpar(v) for c, v in valores.items() if v not in (None, "")}
        if coluna_total is None:
            for c, v in textos.items():
                if v.lower().startswith("impress") and any(t == "Mês" or t == "Mes" for t in textos.values()):
                    coluna_total = c
        meses = [(c, v) for c, v in textos.items() if v in MONTH_COLUMNS]
        if len(meses) != 1:
            continue
        mes = meses[0][1]
        if mes in resultado:
            continue
        texto = next((v for v in textos.values() if _PERIODO_RE.search(v)), None)
        if texto is None and coluna_total is None:
            continue
        resultado[mes] = ResumoMes(mes, numero, coluna_total, texto, interpretar_periodo(texto))
        if len(resultado) == 12:
            break
    return resultado


def meses_preenchidos(impressoras: list["LinhaImpressora"]) -> list[str]:
    """
    Meses que a planilha JA fechou: os que somam mais que zero na frota.

    Os meses futuros vem zerados ou com "-" (em 21/09/2026, Setembro a
    Dezembro). Importar esses zeros congelaria "0 paginas" por cima do mes
    que o sistema ainda esta calculando ao vivo pelas leituras. Dentro de um
    mes preenchido, zero de UMA impressora e dado real (ela nao imprimiu) e
    entra normalmente.
    """
    soma = {mes: 0 for mes in MONTH_COLUMNS}
    for item in impressoras:
        for mes, valor in item.meses.items():
            soma[mes] += valor
    return [mes for mes in MONTH_COLUMNS if soma[mes] > 0]


# ─────────────────────────────────────────────────────────────────────────
#  Casamento linha da planilha <-> equipamento do banco
# ─────────────────────────────────────────────────────────────────────────

def serial_da_linha(item: LinhaImpressora) -> tuple[str, bool]:
    """(serial limpo, valido?). Invalido: vazio, "-" ou MAC no lugar do serial."""
    serial = limpar(item.serial)
    valido = bool(serial) and serial != "-" and not MAC_RE.match(serial)
    return serial, valido


def indices_do_banco(printers) -> tuple[dict[str, list], dict[str, list]]:
    """(por_ip, por_serial) — por_serial com a chave em maiusculas."""
    por_ip: dict[str, list] = {}
    por_serial: dict[str, list] = {}
    for p in printers:
        por_ip.setdefault(p.ip, []).append(p)
        if (p.serial_number or "").strip():
            por_serial.setdefault(p.serial_number.strip().upper(), []).append(p)
    return por_ip, por_serial


@dataclass
class Casamento:
    """
    Resultado de localizar_equipamento. `situacao`:
      "ok"             -> `filas` sao as filas do equipamento (mesmo IP);
      "nao_encontrado" -> nem serial nem IP levam a um equipamento;
      "ambiguo"        -> IP repetido na planilha e sem serial que resolva;
      "conflito"       -> no IP da planilha o SNMP identifica outro equipamento.
    """

    situacao: str
    filas: list = field(default_factory=list)
    serial: str = ""
    serial_valido: bool = False
    ip_real: str | None = None  # IP onde o serial foi achado, quando difere da planilha
    seriais_no_ip: list[str] = field(default_factory=list)


def localizar_equipamento(item: LinhaImpressora, por_ip: dict, por_serial: dict, repeticoes_ip: dict) -> Casamento:
    """
    Primeiro pelo SERIAL, depois pelo IP. O serial identifica o equipamento
    fisico; o IP muda — na v8, 13 equipamentos ja estavam em outro endereco.
    Em 21/09/2026 a M6530cdn V9Z5Y00033 saiu de 10.2.0.254 (hoje uma
    etiquetadora) para 10.2.0.6: so por IP, as paginas da colorida iriam
    parar numa etiquetadora.

    Mais de um registro com o serial: vale o equipamento ATIVO e confirmado
    por SNMP. Os outros sao copias velhas — em geral deixadas por uma
    importacao anterior que casou pelo IP antigo.

    Pelo IP, fica de fora: IP repetido na propria planilha (nao da para
    saber qual linha e a certa) e IP em que o SNMP le um serial que a
    planilha nao tem em lugar nenhum (equipamento trocado).
    """
    serial, serial_valido = serial_da_linha(item)
    base = {"serial": serial, "serial_valido": serial_valido}

    if serial_valido and serial.upper() in por_serial:
        donos = sorted(
            por_serial[serial.upper()],
            key=lambda p: (not p.active, p.snmp_updated_at is None, p.id),
        )
        ip_real = donos[0].ip
        return Casamento("ok", list(por_ip.get(ip_real, donos)), ip_real=ip_real if ip_real != item.ip else None, **base)

    ip = limpar(item.ip)
    if not ip or not IPV4_RE.match(ip):
        return Casamento("nao_encontrado", **base)
    if repeticoes_ip.get(ip, 0) > 1:
        return Casamento("ambiguo", **base)
    filas = por_ip.get(ip, [])
    if not filas:
        return Casamento("nao_encontrado", **base)
    seriais_no_ip = sorted({(p.serial_number or "").strip().upper() for p in filas} - {""})
    if serial_valido and seriais_no_ip:
        return Casamento("conflito", list(filas), seriais_no_ip=seriais_no_ip, **base)
    return Casamento("ok", list(filas), **base)
