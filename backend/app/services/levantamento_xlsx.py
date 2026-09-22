"""
Edicao cirurgica de um .xlsx no nivel do XML (so biblioteca padrao).

Usado pelo gerador do levantamento mensal (services/levantamento.py). A
regra e mexer no MINIMO: a planilha da empresa tem 12 graficos,
comentarios encadeados, desenhos, configuracao de impressora e
propriedades personalizadas, e nada disso pode mudar.

Por isso tudo aqui e feito sobre o TEXTO do XML, e nao com ElementTree:
reserializar com ElementTree renomeia os prefixos de namespace e descarta
declaracoes usadas so em mc:Ignorable (x14ac, xr...), e o Excel passa a
dizer que o arquivo esta corrompido. As linhas da planilha que nao foram
tocadas saem byte a byte como entraram; as outras partes do pacote tambem.
"""
import io
import re
import zipfile
from xml.sax.saxutils import escape

from app.services.planilha_levantamento import _coluna, letra_coluna

CT_WORKSHEET = "application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"
REL_WORKSHEET = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"
MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

_ROW_RE = re.compile(r"<row\b[^>]*?/>|<row\b[^>]*>.*?</row>", re.S)
_CELL_RE = re.compile(r"<c\b[^>]*?/>|<c\b[^>]*>.*?</c>", re.S)
_ATTR_RE = re.compile(r'([\w:]+)="([^"]*)"')
_F_RE = re.compile(r"<f\b[^>]*?/>|<f\b[^>]*>.*?</f>", re.S)
# Referencia A1 dentro de uma formula (com $ opcionais). Nao casa nome de
# funcao ("LOG10(") nem pedaco de nome ("ABC1_x"). Suficiente para as
# formulas desta planilha (SUM de intervalos, multiplicacoes).
_REF_RE = re.compile(r"(?<![A-Za-z0-9_.])(\$?)([A-Z]{1,3})(\$?)([0-9]+)(?![0-9A-Za-z_(])")

# Caracteres que o XML 1.0 nao aceita (vem as vezes em nome de fila do Windows).
_INVALIDOS_XML = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def attrs(tag: str) -> dict[str, str]:
    return dict(_ATTR_RE.findall(tag))


def texto_xml(valor) -> str:
    return escape(_INVALIDOS_XML.sub("", str(valor)))


def split_ref(ref: str) -> tuple[int, int]:
    """'M28' -> (12, 28)."""
    m = re.match(r"([A-Z]+)(\d+)$", ref)
    return _coluna(m.group(1)), int(m.group(2))


def deslocar_formula(formula: str, dcol: int, dlin: int) -> str:
    """Formula compartilhada de uma celula-filha: referencias relativas andam (dcol, dlin)."""
    def trocar(m):
        col_abs, letras, lin_abs, numero = m.groups()
        col = _coluna(letras)
        lin = int(numero)
        if not col_abs:
            col += dcol
        if not lin_abs:
            lin += dlin
        return f"{col_abs}{letra_coluna(col)}{lin_abs}{lin}"
    return _REF_RE.sub(trocar, formula)


class _Linha:
    """Uma <row> editavel. So e reserializada se `alterada`."""

    def __init__(self, texto: str):
        self.texto = texto
        self.alterada = False
        m = re.match(r"<row\b[^>]*?(/?)>", texto)
        self.abertura = m.group(0)
        self.autofechada = m.group(1) == "/"
        if self.autofechada:
            self.abertura = self.abertura[:-2].rstrip() + ">"
            self.celulas: list[str] = []
        else:
            miolo = texto[m.end(): texto.rindex("</row>")]
            self.celulas = _CELL_RE.findall(miolo)
            # Algo alem de celulas dentro da row (extLst etc.) — guarda o resto.
            self.resto = _CELL_RE.sub("", miolo)
        if self.autofechada:
            self.resto = ""
        self.numero = int(attrs(self.abertura).get("r", "0"))

    def indice(self, col: int) -> int | None:
        for i, c in enumerate(self.celulas):
            ref = attrs(re.match(r"<c\b[^>]*", c).group(0)).get("r")
            if ref and split_ref(ref)[0] == col:
                return i
        return None

    def celula(self, col: int) -> str | None:
        i = self.indice(col)
        return self.celulas[i] if i is not None else None

    def gravar(self, col: int, xml: str) -> None:
        i = self.indice(col)
        if i is not None:
            self.celulas[i] = xml
        else:
            pos = len(self.celulas)
            for j, c in enumerate(self.celulas):
                ref = attrs(re.match(r"<c\b[^>]*", c).group(0)).get("r")
                if ref and split_ref(ref)[0] > col:
                    pos = j
                    break
            self.celulas.insert(pos, xml)
            self._alargar_spans(col)
        self.alterada = True

    def _alargar_spans(self, col: int) -> None:
        a = attrs(self.abertura)
        spans = a.get("spans")
        if not spans or ":" not in spans:
            return
        ini, fim = (int(x) for x in spans.split(":"))
        novo = f"{min(ini, col + 1)}:{max(fim, col + 1)}"
        if novo != spans:
            self.abertura = self.abertura.replace(f'spans="{spans}"', f'spans="{novo}"')

    def serializar(self) -> str:
        if not self.alterada:
            return self.texto
        return self.abertura + "".join(self.celulas) + self.resto + "</row>"


class PlanilhaXml:
    """
    sheetN.xml como texto, com edicao por celula. Linhas nao tocadas saem
    identicas ao original.
    """

    def __init__(self, xml: str):
        m = re.search(r"<sheetData\s*>(.*)</sheetData>", xml, re.S)
        if not m:
            raise ValueError("sheetData nao encontrado na aba")
        self.prefixo = xml[: m.start(1)]
        self.sufixo = xml[m.end(1):]
        miolo = m.group(1)
        self.pedacos: list = []
        self.linhas: dict[int, _Linha] = {}
        pos = 0
        for rm in _ROW_RE.finditer(miolo):
            if rm.start() > pos:
                self.pedacos.append(miolo[pos: rm.start()])
            linha = _Linha(rm.group(0))
            self.pedacos.append(linha)
            self.linhas[linha.numero] = linha
            pos = rm.end()
        if pos < len(miolo):
            self.pedacos.append(miolo[pos:])

    # ── leitura ──────────────────────────────────────────────────────────
    def celula(self, ref: str) -> str | None:
        col, lin = split_ref(ref)
        linha = self.linhas.get(lin)
        return linha.celula(col) if linha else None

    def estilo(self, ref: str) -> str | None:
        xml = self.celula(ref)
        if xml is None:
            return None
        return attrs(re.match(r"<c\b[^>]*", xml).group(0)).get("s")

    def formula(self, ref: str) -> str | None:
        """Texto da formula (ja expandida, se era filha de formula compartilhada)."""
        xml = self.celula(ref)
        if xml is None:
            return None
        f = _F_RE.search(xml)
        if not f:
            return None
        fa = attrs(re.match(r"<f\b[^>]*", f.group(0)).group(0))
        texto = re.sub(r"^<f\b[^>]*>|</f>$", "", f.group(0)) if not f.group(0).endswith("/>") else ""
        if fa.get("t") == "shared" and not texto:
            mestre = self._mestre_compartilhada(fa.get("si"))
            if mestre is None:
                return None
            ref_mestre, texto_mestre = mestre
            c0, l0 = split_ref(ref_mestre)
            c1, l1 = split_ref(ref)
            return deslocar_formula(texto_mestre, c1 - c0, l1 - l0)
        return texto

    def tem_valor(self, ref: str) -> bool:
        xml = self.celula(ref)
        return bool(xml) and ("<v>" in xml or "<v " in xml or "<is>" in xml)

    # ── formulas compartilhadas ──────────────────────────────────────────
    def _membros_compartilhada(self, si: str) -> list[tuple[_Linha, int, str]]:
        membros = []
        for linha in self.linhas.values():
            for i, c in enumerate(linha.celulas):
                if f'si="{si}"' not in c:
                    continue
                f = _F_RE.search(c)
                if f and attrs(re.match(r"<f\b[^>]*", f.group(0)).group(0)).get("si") == si:
                    ref = attrs(re.match(r"<c\b[^>]*", c).group(0))["r"]
                    membros.append((linha, i, ref))
        return membros

    def _mestre_compartilhada(self, si: str | None) -> tuple[str, str] | None:
        if si is None:
            return None
        for linha, i, ref in self._membros_compartilhada(si):
            f = _F_RE.search(linha.celulas[i]).group(0)
            if not f.endswith("/>"):
                texto = re.sub(r"^<f\b[^>]*>|</f>$", "", f)
                if texto:
                    return ref, texto
        return None

    def descompartilhar(self, ref: str) -> None:
        """
        Se a celula faz parte de uma formula compartilhada, transforma TODO o
        grupo em formulas normais (cada uma com o texto que o Excel ja
        calculava para ela). Sem isto, reescrever a celula-mestra deixaria as
        filhas sem formula, e reescrever uma filha deixaria o `ref` da mestra
        apontando para uma celula que nao e mais do grupo.
        """
        xml = self.celula(ref)
        if not xml:
            return
        f = _F_RE.search(xml)
        if not f:
            return
        fa = attrs(re.match(r"<f\b[^>]*", f.group(0)).group(0))
        if fa.get("t") != "shared":
            return
        si = fa.get("si")
        mestre = self._mestre_compartilhada(si)
        if mestre is None:
            return
        ref_mestre, texto_mestre = mestre
        c0, l0 = split_ref(ref_mestre)
        for linha, i, ref_membro in self._membros_compartilhada(si):
            c1, l1 = split_ref(ref_membro)
            texto = deslocar_formula(texto_mestre, c1 - c0, l1 - l0)
            antigo = linha.celulas[i]
            fm = _F_RE.search(antigo)
            linha.celulas[i] = antigo[: fm.start()] + f"<f>{texto}</f>" + antigo[fm.end():]
            linha.alterada = True

    # ── escrita ──────────────────────────────────────────────────────────
    def _estilo_para(self, col: int, lin: int, vizinhas: list[int]) -> str | None:
        s = self.estilo(f"{letra_coluna(col)}{lin}")
        if s is not None:
            return s
        for v in vizinhas:
            s = self.estilo(f"{letra_coluna(v)}{lin}")
            if s is not None:
                return s
        return None

    def _gravar(self, ref: str, miolo: str | None, vizinhas: list[int]) -> None:
        col, lin = split_ref(ref)
        linha = self.linhas.get(lin)
        if linha is None:
            raise ValueError(f"Linha {lin} nao existe na aba — nada a gravar em {ref}")
        s = self._estilo_para(col, lin, vizinhas)
        estilo = f' s="{s}"' if s is not None else ""
        xml = f'<c r="{ref}"{estilo}/>' if miolo is None else f'<c r="{ref}"{estilo}>{miolo}</c>'
        linha.gravar(col, xml)

    def gravar_numero(self, ref: str, valor: int, vizinhas: list[int] = ()) -> None:
        self.descompartilhar(ref)
        self._gravar(ref, f"<v>{int(valor)}</v>", list(vizinhas))

    def limpar(self, ref: str, vizinhas: list[int] = ()) -> None:
        self.descompartilhar(ref)
        self._gravar(ref, None, list(vizinhas))

    def gravar_formula(self, ref: str, formula: str, vizinhas: list[int] = ()) -> None:
        """Formula nova SEM valor em cache: o Excel recalcula ao abrir (fullCalcOnLoad)."""
        self.descompartilhar(ref)
        self._gravar(ref, f"<f>{texto_xml(formula)}</f>", list(vizinhas))

    def serializar(self) -> str:
        return self.prefixo + "".join(
            p.serializar() if isinstance(p, _Linha) else p for p in self.pedacos
        ) + self.sufixo


# ─────────────────────────────────────────────────────────────────────────
#  Pacote (zip)
# ─────────────────────────────────────────────────────────────────────────

class Pacote:
    """
    Um .xlsx aberto para edicao. `partes` guarda so o que mudou; o resto e
    copiado do zip original sem descompactar/recompactar o conteudo.
    """

    def __init__(self, dados: bytes):
        self.original = dados
        self.zin = zipfile.ZipFile(io.BytesIO(dados))
        self.nomes = self.zin.namelist()
        self.alteradas: dict[str, bytes] = {}
        self.removidas: set[str] = set()
        self.novas: dict[str, bytes] = {}

    def ler(self, nome: str) -> bytes:
        if nome in self.novas:
            return self.novas[nome]
        if nome in self.alteradas:
            return self.alteradas[nome]
        return self.zin.read(nome)

    def texto(self, nome: str) -> str:
        return self.ler(nome).decode("utf-8")

    def existe(self, nome: str) -> bool:
        if nome in self.removidas:
            return False
        return nome in self.nomes or nome in self.novas

    def gravar(self, nome: str, conteudo: str | bytes) -> None:
        dados = conteudo.encode("utf-8") if isinstance(conteudo, str) else conteudo
        self.removidas.discard(nome)
        if nome in self.nomes:
            self.alteradas[nome] = dados
        else:
            self.novas[nome] = dados

    def remover(self, nome: str) -> None:
        self.removidas.add(nome)
        self.alteradas.pop(nome, None)
        self.novas.pop(nome, None)

    def salvar(self) -> bytes:
        saida = io.BytesIO()
        with zipfile.ZipFile(saida, "w", zipfile.ZIP_DEFLATED) as zout:
            for info in self.zin.infolist():
                if info.filename in self.removidas:
                    continue
                dados = self.alteradas.get(info.filename)
                if dados is None:
                    dados = self.zin.read(info.filename)
                novo = zipfile.ZipInfo(info.filename, date_time=info.date_time)
                novo.compress_type = zipfile.ZIP_DEFLATED
                novo.external_attr = info.external_attr
                zout.writestr(novo, dados)
            for nome, dados in self.novas.items():
                zout.writestr(nome, dados, compress_type=zipfile.ZIP_DEFLATED)
        return saida.getvalue()


def forcar_recalculo(pacote: Pacote) -> None:
    """
    <calcPr fullCalcOnLoad="1"> no workbook.xml: o Excel recalcula tudo ao
    abrir — totais, as outras abas e os graficos. As celulas gravadas pelo
    gerador ficam sem valor em cache de proposito.
    """
    wb = pacote.texto("xl/workbook.xml")
    m = re.search(r"<calcPr\b[^>]*?/?>", wb)
    if m:
        tag = m.group(0)
        if "fullCalcOnLoad=" in tag:
            nova = re.sub(r'fullCalcOnLoad="[^"]*"', 'fullCalcOnLoad="1"', tag)
        else:
            fim = "/>" if tag.endswith("/>") else ">"
            nova = tag[: -len(fim)].rstrip() + ' fullCalcOnLoad="1"' + fim
        wb = wb[: m.start()] + nova + wb[m.end():]
    else:
        ancora = "</definedNames>" if "</definedNames>" in wb else "</sheets>"
        wb = wb.replace(ancora, ancora + '<calcPr fullCalcOnLoad="1"/>', 1)
    pacote.gravar("xl/workbook.xml", wb)


def remover_calc_chain(pacote: Pacote) -> None:
    """
    Tira o calcChain.xml (e a referencia a ele no [Content_Types] e no
    workbook.xml.rels). Ele lista as celulas com formula; com formulas
    novas, um calcChain desatualizado faz o Excel "reparar" o arquivo. Sem
    ele, o Excel monta um novo ao salvar.
    """
    rels_nome = "xl/_rels/workbook.xml.rels"
    rels = pacote.texto(rels_nome)
    alvo = None
    for rel in re.findall(r"<Relationship\b[^>]*/>", rels):
        a = attrs(rel)
        if a.get("Type", "").endswith("/calcChain"):
            alvo = a.get("Target")
            rels = rels.replace(rel, "")
    if alvo is None:
        return
    pacote.gravar(rels_nome, rels)
    parte = alvo.lstrip("/") if alvo.startswith("/") else "xl/" + alvo
    pacote.remover(parte)
    ct = pacote.texto("[Content_Types].xml")
    ct = re.sub(r'<Override\b[^>]*PartName="/' + re.escape(parte) + r'"[^>]*/>', "", ct)
    pacote.gravar("[Content_Types].xml", ct)


def _abas(pacote: Pacote) -> list[dict]:
    wb = pacote.texto("xl/workbook.xml")
    rels = pacote.texto("xl/_rels/workbook.xml.rels")
    alvo_por_id = {attrs(r).get("Id"): attrs(r).get("Target") for r in re.findall(r"<Relationship\b[^>]*/>", rels)}
    abas = []
    for tag in re.findall(r"<sheet\b[^>]*/>", wb):
        a = attrs(tag)
        abas.append({"tag": tag, "nome": a.get("name"), "sheetId": a.get("sheetId"),
                     "rid": a.get("r:id"), "alvo": alvo_por_id.get(a.get("r:id"))})
    return abas


def nomes_das_abas(pacote: Pacote) -> list[str]:
    return [_desescapar(a["nome"]) for a in _abas(pacote)]


def _desescapar(texto: str | None) -> str:
    from xml.sax.saxutils import unescape
    return unescape(texto or "", {"&quot;": '"', "&apos;": "'"})


def remover_aba(pacote: Pacote, nome: str) -> bool:
    """Tira uma aba inteira (sheet, rel, content type, parte e _rels dela)."""
    for aba in _abas(pacote):
        if _desescapar(aba["nome"]) != nome:
            continue
        wb = pacote.texto("xl/workbook.xml").replace(aba["tag"], "")
        pacote.gravar("xl/workbook.xml", wb)
        rels = pacote.texto("xl/_rels/workbook.xml.rels")
        rels = re.sub(r'<Relationship\b[^>]*Id="' + re.escape(aba["rid"]) + r'"[^>]*/>', "", rels)
        pacote.gravar("xl/_rels/workbook.xml.rels", rels)
        alvo = aba["alvo"] or ""
        parte = alvo.lstrip("/") if alvo.startswith("/") else "xl/" + alvo
        pacote.remover(parte)
        pasta, arquivo = parte.rsplit("/", 1)
        rel_da_aba = f"{pasta}/_rels/{arquivo}.rels"
        if pacote.existe(rel_da_aba):
            pacote.remover(rel_da_aba)
        ct = pacote.texto("[Content_Types].xml")
        ct = re.sub(r'<Override\b[^>]*PartName="/' + re.escape(parte) + r'"[^>]*/>', "", ct)
        pacote.gravar("[Content_Types].xml", ct)
        _titulos_app(pacote, remover=nome)
        return True
    return False


def adicionar_aba(pacote: Pacote, nome: str, sheet_xml: str) -> str:
    """Acrescenta uma aba no FIM (nenhuma aba existente muda de posicao). Devolve a parte criada."""
    abas = _abas(pacote)
    n = 1
    while pacote.existe(f"xl/worksheets/sheet{n}.xml"):
        n += 1
    parte = f"xl/worksheets/sheet{n}.xml"
    pacote.gravar(parte, sheet_xml)

    rels = pacote.texto("xl/_rels/workbook.xml.rels")
    ids = {int(x) for x in re.findall(r'Id="rId(\d+)"', rels)}
    rid = f"rId{max(ids, default=0) + 1}"
    rels = rels.replace(
        "</Relationships>",
        f'<Relationship Id="{rid}" Type="{REL_WORKSHEET}" Target="worksheets/sheet{n}.xml"/></Relationships>',
    )
    pacote.gravar("xl/_rels/workbook.xml.rels", rels)

    sheet_id = max((int(a["sheetId"]) for a in abas if a["sheetId"]), default=0) + 1
    wb = pacote.texto("xl/workbook.xml")
    wb = wb.replace("</sheets>", f'<sheet name="{texto_xml(nome)}" sheetId="{sheet_id}" r:id="{rid}"/></sheets>', 1)
    pacote.gravar("xl/workbook.xml", wb)

    ct = pacote.texto("[Content_Types].xml")
    ct = ct.replace("</Types>", f'<Override PartName="/{parte}" ContentType="{CT_WORKSHEET}"/></Types>')
    pacote.gravar("[Content_Types].xml", ct)
    _titulos_app(pacote, adicionar=nome)
    return parte


def _titulos_app(pacote: Pacote, adicionar: str | None = None, remover: str | None = None) -> None:
    """Mantem docProps/app.xml (TitlesOfParts/HeadingPairs) coerente, quando ele lista as abas."""
    if not pacote.existe("docProps/app.xml"):
        return
    app = pacote.texto("docProps/app.xml")
    m = re.search(r"<TitlesOfParts>\s*<vt:vector\b([^>]*)>(.*?)</vt:vector>\s*</TitlesOfParts>", app, re.S)
    if not m:
        return
    itens = re.findall(r"<vt:lpstr>(.*?)</vt:lpstr>", m.group(2), re.S)
    delta = 0
    if remover is not None and texto_xml(remover) in itens:
        itens.remove(texto_xml(remover))
        delta = -1
    if adicionar is not None:
        # Abas vem primeiro no vetor, antes dos intervalos nomeados: a nova
        # entra logo depois da ultima aba (ver o contador em HeadingPairs).
        hp = re.search(r"<vt:lpstr>(Worksheets|Planilhas)</vt:lpstr>\s*</vt:variant>\s*<vt:variant>\s*<vt:i4>(\d+)</vt:i4>", app)
        pos = int(hp.group(2)) if hp else len(itens)
        itens.insert(pos, texto_xml(adicionar))
        delta = 1
    if delta == 0:
        return
    vetor = f'<TitlesOfParts><vt:vector size="{len(itens)}" baseType="lpstr">' + "".join(
        f"<vt:lpstr>{i}</vt:lpstr>" for i in itens) + "</vt:vector></TitlesOfParts>"
    app = app[: m.start()] + vetor + app[m.end():]
    app = re.sub(
        r"(<vt:lpstr>(?:Worksheets|Planilhas)</vt:lpstr>\s*</vt:variant>\s*<vt:variant>\s*<vt:i4>)(\d+)(</vt:i4>)",
        lambda x: f"{x.group(1)}{int(x.group(2)) + delta}{x.group(3)}", app, count=1,
    )
    pacote.gravar("docProps/app.xml", app)


def montar_aba_simples(linhas: list[list], estilo_cabecalho: str | None = None,
                       linha_cabecalho: int | None = None, larguras: list[float] | None = None) -> str:
    """
    sheetN.xml com texto em linha (inlineStr) — nao mexe no sharedStrings.
    `linhas`: lista de listas (str | int | None). `linha_cabecalho` (1-based)
    recebe `estilo_cabecalho`, um indice de estilo ja existente no styles.xml.
    """
    partes = []
    for i, valores in enumerate(linhas, start=1):
        celulas = []
        estilo = f' s="{estilo_cabecalho}"' if estilo_cabecalho is not None and i == linha_cabecalho else ""
        for j, v in enumerate(valores):
            if v is None or v == "":
                continue
            ref = f"{letra_coluna(j)}{i}"
            if isinstance(v, bool):
                v = str(v)
            if isinstance(v, (int, float)):
                celulas.append(f'<c r="{ref}"{estilo}><v>{v}</v></c>')
            else:
                celulas.append(f'<c r="{ref}"{estilo} t="inlineStr"><is><t xml:space="preserve">{texto_xml(v)}</t></is></c>')
        partes.append(f'<row r="{i}">{"".join(celulas)}</row>' if celulas else f'<row r="{i}"/>')
    cols = ""
    if larguras:
        cols = "<cols>" + "".join(
            f'<col min="{k}" max="{k}" width="{w}" customWidth="1"/>' for k, w in enumerate(larguras, start=1)
        ) + "</cols>"
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        f'<worksheet xmlns="{MAIN_NS}" xmlns:r="{REL_NS}">'
        '<sheetViews><sheetView workbookViewId="0"/></sheetViews>'
        '<sheetFormatPr defaultRowHeight="15"/>'
        f"{cols}<sheetData>{''.join(partes)}</sheetData>"
        '<pageMargins left="0.7" right="0.7" top="0.75" bottom="0.75" header="0.3" footer="0.3"/>'
        "</worksheet>"
    )


def validar_pacote(dados: bytes) -> list[str]:
    """Problemas encontrados: zip que nao abre, parte XML que nao parseia, rel apontando para o nada."""
    import xml.etree.ElementTree as ET

    problemas = []
    try:
        z = zipfile.ZipFile(io.BytesIO(dados))
    except zipfile.BadZipFile:
        return ["o arquivo gerado nao abre como zip"]
    with z:
        ruim = z.testzip()
        if ruim:
            problemas.append(f"CRC invalido em {ruim}")
        nomes = set(z.namelist())
        for nome in nomes:
            if nome.endswith((".xml", ".rels", ".vml")):
                try:
                    ET.fromstring(z.read(nome))
                except ET.ParseError as e:
                    if not nome.endswith(".vml"):  # VML do Excel nem sempre e XML bem formado
                        problemas.append(f"{nome}: XML invalido ({e})")
        if "[Content_Types].xml" in nomes:
            ct = z.read("[Content_Types].xml").decode("utf-8")
            for parte in re.findall(r'PartName="/([^"]+)"', ct):
                if parte not in nomes:
                    problemas.append(f"[Content_Types].xml cita /{parte}, que nao existe")
        if "xl/_rels/workbook.xml.rels" in nomes:
            rels = z.read("xl/_rels/workbook.xml.rels").decode("utf-8")
            for rel in re.findall(r"<Relationship\b[^>]*/>", rels):
                a = attrs(rel)
                if a.get("TargetMode") == "External":
                    continue
                alvo = a.get("Target", "")
                parte = alvo.lstrip("/") if alvo.startswith("/") else "xl/" + alvo
                if parte not in nomes:
                    problemas.append(f"workbook.xml.rels aponta para {parte}, que nao existe")
    return problemas
