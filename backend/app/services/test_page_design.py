"""
Pagina de teste "moderna" (22/09/2026): logo Elgin, cartoes de informacao,
contador em destaque e, na impressora colorida, uma versao propria em cor.

A pagina "classica" (test_print.build_test_page_classica) continua existindo
como reserva: TEST_PAGE_STYLE=classica no .env volta para ela.

DUAS VERSOES
------------
Monocromatica — PCL5 basico, igual a classica: texto posicionado, retangulo
solido e hachurado, e a logo como raster de 1 bit (preto).

Colorida — PCL5c. Uma paleta de 16 cores e configurada no comeco
(Configure Image Data, ESC * v 6 W, RGB indexado por plano, 4 bits) e cada
elemento escolhe a sua (ESC * v # S). Texto, retangulo e raster usam a cor
selecionada. A logo sai no azul Elgin mandando o bitmap no plano 1 e zeros
nos outros tres: indice 1 da paleta. Impressora sem PCL5c ignora os comandos
de cor e imprime a mesma pagina em preto — nao quebra.

Economia de toner (22/09/2026): na colorida so a logo e as barras de toner
saem em cor; o resto e preto puro (tons de cinza por hachura), e o teste de
cores saiu. As duas versoes terminam com o teste de nitidez: linhas de
espessura crescente e texto de 6 a 14 pt. Nenhuma tem escala de cinza.
"""
from __future__ import annotations

import textwrap
from datetime import datetime

from app.services import test_page_logo
from app.services.test_print import (
    _LARGURA,
    _NAO_INFORMADO,
    TestPageInfo,
    _Pagina,
    _separar_departamento,
    _valor,
    envelope_pjl,
)

_ESC = "\x1b"

# Paleta da versao colorida (indice -> RGB). O indice 0 e o papel.
_BRANCO, _ELGIN, _PRETO, _TEXTO, _CINZA, _FUNDO, _ELGIN_CLARO = 0, 1, 2, 3, 4, 5, 6
_CIANO, _MAGENTA, _AMARELO = 7, 8, 9
_PALETA = {
    _BRANCO: (255, 255, 255),
    _ELGIN: (0, 159, 255),  # azul da logo (#009FFF)
    _PRETO: (0, 0, 0),
    _TEXTO: (38, 42, 50),
    _CINZA: (120, 126, 136),
    _FUNDO: (238, 242, 246),
    _ELGIN_CLARO: (222, 241, 255),
    _CIANO: (0, 174, 239),
    _MAGENTA: (236, 0, 140),
    _AMARELO: (255, 222, 0),
}
_COR_DO_TONER = {"Preto": _PRETO, "Ciano": _CIANO, "Magenta": _MAGENTA, "Amarelo": _AMARELO}
# Unicas cores que saem como cor na versao colorida (22/09/2026: a primeira
# versao, com titulos, cartoes e grafico em azul e o teste de cores, gastava
# toner colorido demais). Todo o resto vira preto puro: cinza feito em RGB
# costuma ser composto com ciano+magenta+amarelo pela impressora, entao os
# tons de cinza saem por hachura do preto, como na monocromatica — so toner K.
# (O azul da logo vai direto pelo indice da paleta no raster; texto e
# retangulos nunca saem em azul.)
_CORES_PERMITIDAS = {_CIANO, _MAGENTA, _AMARELO, _PRETO}


class _PaginaModerna(_Pagina):
    """_Pagina com cor (PCL5c) opcional e a logo em raster."""

    def __init__(self, colorida: bool) -> None:
        super().__init__()
        self.colorida = colorida
        # Centraliza o layout (2300 de largura) no A4. O PCL conta x a partir
        # da borda da area imprimivel (~50 unidades = 4 mm da borda do papel
        # num A4 de 2480), nao do papel: sem isto sobravam 4 mm a esquerda e
        # 11 mm a direita, e em Ricoh/Kyocera, cuja area imprimivel e um pouco
        # diferente, a folha saia deslocada e a logo, colada na borda, fora do
        # lugar (22/09/2026). Com 95% da largura e o deslocamento abaixo
        # sobram ~12 mm de cada lado e ~12 mm no topo — folga para a diferenca
        # entre marcas sem cortar nada.
        self.escala = 0.95
        self.dx = 97
        self.dy = 110
        if colorida:
            # RGB (0), indexado por plano (0), 4 bits por indice, 8 bits por primaria.
            self._cmd(f"{_ESC}*v6W")
            self.buf += bytes([0, 0, 4, 8, 8, 8])
            for indice, (r, g, b) in _PALETA.items():
                self._cmd(f"{_ESC}*v{r}a{g}b{b}c{indice}I")
            self.cor(_TEXTO)

    def cor(self, indice: int) -> None:
        """
        Cor dos proximos textos e retangulos. Sem efeito na monocromatica; na
        colorida, qualquer cor fora de _CORES_PERMITIDAS vira preto.
        """
        if self.colorida:
            self._cmd(f"{_ESC}*v{indice if indice in _CORES_PERMITIDAS else _PRETO}S")

    def bloco(self, x: int, y: int, largura: int, altura: int, cor: int, cinza_mono: int) -> None:
        """
        Retangulo cheio. Na colorida so o azul da logo e as cores de toner saem
        em cor; o resto, e a monocromatica inteira, sai em preto hachurado
        `cinza_mono`%.
        """
        if self.colorida and cor in _CORES_PERMITIDAS - {_PRETO}:
            self.cor(cor)
            self.retangulo(x, y, largura, altura)
            self.cor(_PRETO)
        else:
            self.cor(_PRETO)
            self.retangulo(x, y, largura, altura, cinza=cinza_mono)

    def logo(self, x: int, y: int) -> None:
        """Logo Elgin com o canto superior esquerdo em (x, y), 300 dpi."""
        linhas = test_page_logo.linhas()
        n = test_page_logo.BYTES_POR_LINHA
        self._cmd(f"{_ESC}*p{self._x(x)}x{self._y(y)}Y")
        self._cmd(f"{_ESC}*r0F{_ESC}*t300R{_ESC}*r{test_page_logo.LARGURA}S{_ESC}*b0M{_ESC}*r1A")
        zeros = bytes(n)
        for linha in linhas:
            if self.colorida:
                # Indice 1 (azul Elgin): bit no plano 1, zero nos planos 2 a 4.
                self._cmd(f"{_ESC}*b{n}V")
                self.buf += linha
                for plano in (2, 3):
                    self._cmd(f"{_ESC}*b{n}V")
                    self.buf += zeros
                self._cmd(f"{_ESC}*b{n}W")
                self.buf += zeros
            else:
                self._cmd(f"{_ESC}*b{n}W")
                self.buf += linha
        self._cmd(f"{_ESC}*rC")

    def titulo_secao(self, x: int, y: int, texto: str, largura: int) -> None:
        self.cor(_ELGIN if self.colorida else _TEXTO)
        self.texto(x, y, texto, pt=9, negrito=True)
        self.retangulo(x, y + 16, largura, 4 if self.colorida else 2)
        self.cor(_TEXTO)

    def rotulo(self, x: int, y: int, texto: str, pt: float = 8.5) -> None:
        self.cor(_CINZA)
        self.texto(x, y, texto, pt=pt)
        self.cor(_TEXTO)


def _milhar(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def build_test_page_moderna(info: TestPageInfo, colorida: bool) -> bytes:
    """Documento PJL + PCL de UMA pagina A4 no layout novo."""
    when = info.when or datetime.now()
    departamento, unidade = _separar_departamento(info.department)
    compartilhamento = f"\\\\{info.server}\\{info.share_name}" if info.server and info.share_name else None
    coleta = info.last_reading.strftime("%d/%m/%Y %H:%M:%S") if info.last_reading else None

    p = _PaginaModerna(colorida)

    # ── Cabecalho: logo a esquerda, titulo e data a direita ──────────────
    p.logo(0, 30)
    p.texto(1330, 120, "Página de teste", pt=20, negrito=True)
    p.rotulo(1330, 180, "Impressão colorida" if colorida else "Impressão monocromática", pt=10)
    p.texto(1330, 240, when.strftime("%d/%m/%Y  ·  %H:%M:%S"), pt=10, negrito=True)
    p.bloco(0, 320, _LARGURA, 10, _ELGIN, 100)

    # ── Fila em destaque + status ────────────────────────────────────────
    p.texto(0, 450, info.printer_name, pt=22, negrito=True, limite=34)
    linha_rede = "   ·   ".join(v for v in (info.ip, info.server or "sem servidor", info.model) if v)
    p.rotulo(0, 515, linha_rede, pt=11)
    status = (info.status or "").strip()
    if status:
        p.bloco(1850, 380, 450, 90, _ELGIN_CLARO, 12)
        p.cor(_ELGIN if colorida else _TEXTO)
        p.texto(1890, 440, status.upper(), pt=12, negrito=True, limite=12)
        p.cor(_TEXTO)

    # ── Cartoes: equipamento | rede ──────────────────────────────────────
    y_cartao, altura_cartao, largura_cartao = 590, 470, 1120
    cartoes = [
        (0, "EQUIPAMENTO", [
            ("Modelo", info.model),
            ("Nº de série", info.serial),
            ("Departamento", departamento),
            ("Unidade", unidade),
            ("Localização", info.location),
        ]),
        (1180, "REDE E SERVIDOR", [
            ("IP", info.ip),
            ("Servidor", info.server or "sem servidor"),
            ("Compartilhamento", compartilhamento),
            ("Driver", info.driver),
            ("Envio", "direto ao IP, porta 9100"),
        ]),
    ]
    for x, titulo, campos in cartoes:
        p.bloco(x, y_cartao, largura_cartao, altura_cartao, _FUNDO, 6)
        p.bloco(x, y_cartao, 12, altura_cartao, _ELGIN, 100)
        p.cor(_ELGIN if colorida else _TEXTO)
        p.texto(x + 60, y_cartao + 80, titulo, pt=9, negrito=True)
        p.cor(_TEXTO)
        for i, (rotulo, valor) in enumerate(campos):
            y = y_cartao + 165 + i * 66
            p.rotulo(x + 60, y, rotulo)
            p.texto(x + 400, y, _valor(valor), pt=10, negrito=valor not in (None, ""), limite=31)

    # ── Contador e toner ─────────────────────────────────────────────────
    y = y_cartao + altura_cartao + 130
    p.titulo_secao(0, y, "CONTADOR E TONER", _LARGURA)
    y_bloco = y + 110
    p.rotulo(0, y_bloco, "Contador total")
    if info.page_count:
        p.texto(0, y_bloco + 120, _milhar(info.page_count), pt=30, negrito=True)
        p.rotulo(0, y_bloco + 180, "páginas", pt=10)
    else:
        p.texto(0, y_bloco + 100, _NAO_INFORMADO, pt=14, negrito=True)
    p.rotulo(0, y_bloco + 250, f"Lido em {coleta}" if coleta else "Sem leitura registrada", pt=8.5)
    # A impressora so soma a pagina quando ela SAI (21/09/2026).
    p.rotulo(0, y_bloco + 295, "Lido antes desta folha sair; ela entra na próxima leitura.", pt=7)

    x_toner, largura_barra, altura_barra = 1180, 760, 46
    if info.toner:
        for i, (nome, pct) in enumerate(info.toner[:4]):
            yb = y_bloco - 20 + i * 92
            pct = max(0, min(100, int(pct)))
            p.texto(x_toner, yb + 36, nome, pt=10)
            x_barra = x_toner + 250
            p.bloco(x_barra, yb, largura_barra, altura_barra, _FUNDO, 8)
            if pct:
                p.bloco(x_barra, yb, largura_barra * pct / 100, altura_barra, _COR_DO_TONER.get(nome, _PRETO), 100)
            p.texto(x_barra + largura_barra + 30, yb + 36, f"{pct}%", pt=11, negrito=True)
    else:
        p.rotulo(x_toner, y_bloco, "Toner")
        p.texto(x_toner, y_bloco + 70, _NAO_INFORMADO, pt=12, negrito=True)
        if info.toner_note:
            for i, trecho in enumerate(textwrap.wrap(info.toner_note, 60)[:3]):
                p.rotulo(x_toner, y_bloco + 130 + i * 40, trecho, pt=8)
    y = y_bloco + 450

    # ── Paginas por mes ──────────────────────────────────────────────────
    if info.monthly:
        p.titulo_secao(0, y, "PÁGINAS POR MÊS", _LARGURA)
        meses = info.monthly[-12:]
        coluna, largura_col, altura_max = _LARGURA // 12, 130, 230
        base = y + 90 + altura_max
        maior = max(paginas for _, paginas, _, _ in meses) or 1
        for i, (rotulo, paginas, estimadas, em_andamento) in enumerate(meses):
            x = i * coluna + 20
            altura = max(6, round(altura_max * paginas / maior)) if paginas else 4
            if em_andamento:
                p.bloco(x, base - altura, largura_col, altura, _ELGIN_CLARO, 25)
                p.moldura(x, base - altura, largura_col, altura, espessura=3)
            else:
                p.bloco(x, base - altura, largura_col, altura, _ELGIN, 70)
            p.texto(x, base - altura - 20, _milhar(paginas) + ("*" if estimadas else ""), pt=8, negrito=True)
            p.rotulo(x, base + 45, rotulo, pt=8)
        p.bloco(0, base, _LARGURA, 3, _CINZA, 100)
        y = base + 100
        notas = []
        if any(e for _, _, e, _ in meses):
            notas.append("* inclui estimativa dos dias sem coleta no começo do mês.")
        if any(a for _, _, _, a in meses):
            notas.append("Barra vazada: mês em andamento.")
        if notas:
            p.rotulo(0, y, "   ".join(notas), pt=7.5)
        y += 90

    # ── Teste de nitidez (as duas versoes; so preto) ────────────────────
    y += 40
    p.titulo_secao(0, y, "TESTE DE NITIDEZ", _LARGURA)
    for i, espessura in enumerate((1, 2, 3, 5, 8, 12)):
        x = i * 385
        p.retangulo(x, y + 90, 340, espessura)
        p.retangulo(x, y + 130, 340, espessura)
        p.rotulo(x, y + 200, f"{espessura} px", pt=7.5)
    x = 0
    for pt in (6, 8, 10, 12, 14):
        p.texto(x, y + 320, f"Elgin {pt} pt", pt=pt, negrito=pt >= 12)
        x += 180 + pt * 22
    p.retangulo(0, y + 360, _LARGURA, 40)
    y += 460

    # ── Rodape ───────────────────────────────────────────────────────────
    y = max(y + 30, 2920)
    p.bloco(0, y, _LARGURA, 3, _CINZA, 100)
    p.texto(0, y + 60, f"Solicitado por {info.requested_by}", pt=9, negrito=True, limite=90)
    p.rotulo(0, y + 110, "Se esta folha saiu, o equipamento recebe trabalhos pela rede. O teste não passa pelo servidor", pt=8)
    p.rotulo(0, y + 150, "de impressão nem pelo driver: não confirma a fila do Windows.", pt=8)
    p.cor(_ELGIN if colorida else _TEXTO)
    p.texto(1900, y + 60, "PrinterControl", pt=9, negrito=True)
    p.cor(_TEXTO)
    p.rotulo(1900, y + 110, "Elgin · TI", pt=8)

    return envelope_pjl(bytes(p.buf), "PrinterControl - pagina de teste")
