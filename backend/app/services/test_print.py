"""
Pagina de teste enviada direto ao IP da impressora (porta 9100, RAW).

POR QUE DIRETO NO IP, E NAO PELA FILA DO PRINT SERVER
-----------------------------------------------------
Analise de 21/09/2026: imprimir a pagina de teste do Windows pela fila
(`Win32_Printer.PrintTestPage`) exige WMI no print server, e a conta de
servico recebeu "Acesso negado" — nao e admin la, e nao deveria ser. Ja a
porta 9100 respondeu em 34 de 39 lasers a partir da maquina do backend, nao
precisa de driver nem de permissao, e funciona igual rodando como SYSTEM.

O que isso testa: que o EQUIPAMENTO recebe trabalho pela rede e imprime. O
que NAO testa: a fila do print server nem o driver. A pagina diz isso
impressa, para ninguem concluir que "a fila esta ok" a partir dela.

SO LASER, POR ENQUANTO
----------------------
A pagina e PCL (com cabecalho PJL), que praticamente todo laser entende —
Kyocera, Ricoh, Pantum, Brother, HP. Etiquetadora fala outra lingua (ZPL,
PPLA, Fingerprint...), e PCL nela imprime lixo, as vezes ao longo de
dezenas de etiquetas. Por isso a elegibilidade e uma LISTA POSITIVA: so
recebe o teste quem parece laser de marca conhecida E nao parece
etiquetadora por nenhum dos campos que temos.
"""
from __future__ import annotations

import re
import socket
from dataclasses import dataclass
from datetime import datetime

RAW_PORT = 9100
CONNECT_TIMEOUT_SECONDS = 4.0

# Marcas cujos lasers falam PCL. Casada contra modelo, driver e SNMP.
# Canon fica de fora de proposito: a da frota e jato de tinta (MAXIFY
# MB5300, sem PCL), e boa parte das Canon laser usa UFR II.
_LASER_RE = re.compile(r"kyocera|ecosys|ricoh|pantum|brother|lexmark|xerox|samsung|\bhp\b|laserjet|\bpcl", re.I)
# Qualquer sinal de etiquetadora/portatil vence o sinal de laser.
_LABEL_RE = re.compile(r"tt042|elgin|zebra|argox|honeywell|rp4f|sewoo|etiqueta|label|bar ?code|generic\s*/\s*text", re.I)
_IP_RE = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")


def is_supported(
    *,
    ip: str | None,
    name: str | None,
    model: str | None,
    driver_name: str | None,
    printer_type: str | None,
    snmp_model: str | None = None,
    snmp_description: str | None = None,
) -> bool:
    """A impressora pode receber a pagina de teste PCL com seguranca?"""
    if not ip or not _IP_RE.match(ip.strip()):
        return False
    if (printer_type or "").strip() in ("Etiqueta", "Portatil"):
        return False
    campos = " | ".join(c for c in (name, model, driver_name, snmp_model, snmp_description) if c)
    if _LABEL_RE.search(campos):
        return False
    return bool(_LASER_RE.search(campos))


@dataclass
class TestPrintResult:
    sent: bool
    # "enviado", "porta_fechada", "sem_resposta", "erro_de_rede"
    detail: str
    bytes_sent: int = 0


def _latin1(texto: str) -> bytes:
    # Symbol set ISO 8859-1 e selecionado no documento (ESC ( 0 N), entao
    # acento sai certo; o que nao couber em Latin-1 vira "?" em vez de erro.
    return texto.encode("latin-1", errors="replace")


@dataclass
class TestPageInfo:
    """
    Tudo o que a pagina de teste imprime sobre o equipamento. So `printer_name`,
    `ip` e `requested_by` sao obrigatorios; o resto sai como "nao informado"
    quando o banco nao tem — melhor dizer isso na folha do que omitir a linha
    e deixar quem le achando que o campo nao existe.
    """

    printer_name: str
    ip: str
    requested_by: str
    model: str | None = None
    serial: str | None = None
    # "Departamento — Unidade", como o banco guarda; a pagina separa os dois.
    department: str | None = None
    location: str | None = None
    server: str | None = None
    share_name: str | None = None
    driver: str | None = None
    status: str | None = None
    page_count: int | None = None
    # [("Preto", 45), ("Ciano", 77), ...]
    toner: list[tuple[str, int]] | None = None
    #: Por que nao ha nivel de toner (SNMPClient.diagnostico_toner), quando nao ha.
    toner_note: str | None = None
    last_reading: datetime | None = None
    # Paginas por mes do equipamento, do mais antigo ao mais recente:
    # [("Ago/26", paginas, estimadas, em_andamento), ...]
    monthly: list[tuple[str, int, int, bool]] | None = None
    when: datetime | None = None
    #: Impressora colorida: a pagina moderna sai na versao em cor (PCL5c).
    colorida: bool = False


_NAO_INFORMADO = "não informado"

# Unidades PCL: 300 por polegada (ESC & u 300 D). A4 retrato tem ~2300 de
# area util na horizontal; tudo abaixo e posicionado em coordenadas absolutas,
# nunca por quebra de linha — o layout sai igual em qualquer marca.
_LARGURA = 2300
_ESC = "\x1b"


class _Pagina:
    """Monta a pagina PCL5: texto posicionado, retangulos solidos e hachurados."""

    def __init__(self) -> None:
        self.buf = bytearray()
        # Transformacao do layout para a folha: x_papel = dx + x * escala,
        # y_papel = dy + y. Identidade na classica; a moderna centraliza.
        self.escala = 1.0
        self.dx = 0
        self.dy = 0

    def _cmd(self, texto: str) -> None:
        self.buf += texto.encode("ascii")

    def _x(self, x: float) -> int:
        return round(self.dx + x * self.escala)

    def _y(self, y: float) -> int:
        return round(self.dy + y)

    def _w(self, largura: float) -> int:
        return max(1, round(largura * self.escala))

    def texto(self, x: int, y: int, conteudo: str, pt: float = 10, negrito: bool = False, limite: int | None = None) -> None:
        """`y` e a linha de base do texto. `limite` corta em N caracteres com reticencias."""
        if limite and len(conteudo) > limite:
            # "..." e nao "…": o simbolo unico nao existe em Latin-1 e sairia "?".
            conteudo = conteudo[: limite - 3] + "..."
        self._cmd(f"{_ESC}*p{self._x(x)}x{self._y(y)}Y")
        # Univers proporcional (typeface 4148): presente em Kyocera, Ricoh,
        # Pantum e Brother; se faltar, a impressora escolhe a mais proxima.
        self._cmd(f"{_ESC}(s1p{pt:g}v0s{3 if negrito else 0}b4148T")
        self.buf += _latin1(conteudo)

    def retangulo(self, x: int, y: int, largura: int, altura: int, cinza: int = 100) -> None:
        """Retangulo a partir do canto superior esquerdo. cinza=100 e preto solido."""
        largura, altura = self._w(largura), max(1, int(altura))
        self._cmd(f"{_ESC}*p{self._x(x)}x{self._y(y)}Y")
        if cinza >= 100:
            self._cmd(f"{_ESC}*c{largura}a{altura}b0P")
        else:
            self._cmd(f"{_ESC}*c{largura}a{altura}b{max(1, cinza)}g2P")

    def linha(self, y: int, espessura: int = 3) -> None:
        self.retangulo(0, y, _LARGURA, espessura)

    def moldura(self, x: int, y: int, largura: int, altura: int, espessura: int = 3) -> None:
        self.retangulo(x, y, largura, espessura)
        self.retangulo(x, y + altura - espessura, largura, espessura)
        self.retangulo(x, y, espessura, altura)
        self.retangulo(x + largura - espessura, y, espessura, altura)


def _valor(valor) -> str:
    return _NAO_INFORMADO if valor in (None, "") else str(valor)


def _separar_departamento(department: str | None) -> tuple[str | None, str | None]:
    """'HDB - QLD — MC' -> ('HDB - QLD', 'MC'). Sem ' — ', e tudo departamento."""
    if not department:
        return None, None
    if " — " in department:
        dep, unidade = department.rsplit(" — ", 1)
        return dep.strip() or None, unidade.strip() or None
    return department.strip(), None


def build_test_page(info: TestPageInfo, estilo: str | None = None) -> bytes:
    """
    Pagina de teste no estilo configurado (TEST_PAGE_STYLE): "moderna" (logo
    Elgin, versao colorida para impressora colorida — test_page_design.py)
    ou "classica" (a pagina de 21/09/2026, mantida como reserva).
    """
    from app.config import settings

    estilo = (estilo or settings.test_page_style or "moderna").strip().lower()
    if estilo == "classica":
        return build_test_page_classica(info)
    from app.services.test_page_design import build_test_page_moderna

    return build_test_page_moderna(info, colorida=info.colorida)


def envelope_pjl(pcl: bytes, nome_do_trabalho: str) -> bytes:
    """
    Envolve o corpo PCL de uma pagina: PJL, reset, A4 retrato sem margens,
    unidade 1/300 pol, Latin-1; no fim form feed e reset. Mesmo que a
    impressora ignore o PJL, o PCL sozinho imprime, e o reset no fim devolve
    o equipamento ao estado padrao para o proximo trabalho.
    """
    esc = b"\x1b"
    uel = esc + b"%-12345X"  # Universal Exit Language (PJL)
    return b"".join(
        [
            uel,
            b'@PJL JOB NAME="' + _latin1(nome_do_trabalho) + b'"\r\n',
            b"@PJL ENTER LANGUAGE=PCL\r\n",
            esc + b"E",  # reset
            esc + b"&l26A",  # papel A4
            esc + b"&l0O",  # retrato
            esc + b"&l0E",  # margem superior zero: o layout e absoluto
            esc + b"&l0L",  # sem pulo de perfuracao
            esc + b"&u300D",  # unidade PCL = 1/300 pol
            esc + b"(0N",  # symbol set ISO 8859-1 (Latin-1)
            pcl,
            b"\x0c",  # form feed: ejeta a pagina
            esc + b"E",  # reset para o proximo trabalho
            uel,
            b"@PJL EOJ\r\n",
            uel,
        ]
    )


def build_test_page_classica(info: TestPageInfo) -> bytes:
    """
    Documento PJL + PCL5 de UMA pagina A4 — a pagina de 21/09/2026, reserva
    da moderna (TEST_PAGE_STYLE=classica).

    Layout (de cima para baixo): faixa de cabecalho com titulo, data e quem
    pediu; nome da fila em destaque; duas colunas — equipamento (modelo,
    serie, departamento, unidade, localizacao) e rede (IP, servidor,
    compartilhamento, driver); a ultima coleta com status, contador e uma
    barra por cor de toner; uma escala de cinza de 10% a 100% para avaliar a
    qualidade de impressao; e o rodape dizendo o que o teste prova e o que
    nao prova.

    So recursos basicos de PCL5 (texto posicionado, retangulo solido e
    hachurado), que todo laser PCL entende. Terminado em form feed e reset:
    mesmo que a impressora ignore o PJL, o PCL sozinho imprime; e o reset no
    fim devolve o equipamento ao estado padrao para o proximo trabalho.
    """
    when = info.when or datetime.now()
    departamento, unidade = _separar_departamento(info.department)
    compartilhamento = f"\\\\{info.server}\\{info.share_name}" if info.server and info.share_name else None
    contador = f"{info.page_count:,}".replace(",", ".") + " páginas" if info.page_count else None
    # Com segundos: a leitura e feita na hora do envio, e duas folhas seguidas
    # precisam mostrar que foram lidas em momentos diferentes.
    coleta = info.last_reading.strftime("%d/%m/%Y %H:%M:%S") if info.last_reading else None

    p = _Pagina()

    # Cabecalho: faixa cinza clara com titulo a esquerda e data a direita.
    p.retangulo(0, 40, _LARGURA, 200, cinza=12)
    p.retangulo(0, 40, 18, 200)  # filete preto na borda esquerda da faixa
    p.texto(60, 135, "PrinterControl", pt=22, negrito=True)
    p.texto(60, 200, "Página de teste de impressão", pt=11)
    p.texto(1450, 135, when.strftime("%d/%m/%Y  %H:%M:%S"), pt=11, negrito=True)
    p.texto(1450, 200, "Envio direto ao IP · porta 9100", pt=9)

    # Fila em destaque e a linha de rede logo abaixo.
    p.texto(0, 370, info.printer_name, pt=20, negrito=True, limite=40)
    p.texto(0, 430, f"{info.ip}   ·   {info.server or 'sem servidor'}", pt=11)
    p.linha(470, espessura=6)

    # Duas colunas: equipamento | rede.
    y0, passo = 560, 62
    colunas = [
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
        ]),
    ]
    for x, titulo, campos in colunas:
        p.texto(x, y0, titulo, pt=9, negrito=True)
        p.retangulo(x, y0 + 14, 1080, 2)
        for i, (rotulo, valor) in enumerate(campos, start=1):
            y = y0 + 20 + i * passo
            p.texto(x, y, rotulo, pt=9)
            # 370: "Compartilhamento", o rotulo mais longo, cabe sem encostar.
            p.texto(x + 370, y, _valor(valor), pt=10, negrito=valor not in (None, ""), limite=34)

    # Ultima coleta: status/contador e uma barra por cor de toner. Comeca
    # abaixo da coluna mais longa (5 linhas) com uma folga de secao.
    y = y0 + 20 + 5 * passo + 130
    p.texto(0, y, f"ÚLTIMA COLETA{f'  ·  {coleta}' if coleta else ''}", pt=9, negrito=True)
    p.retangulo(0, y + 14, _LARGURA, 2)
    y += 90
    p.texto(0, y, "Status", pt=9)
    p.texto(330, y, _valor(info.status), pt=10, negrito=bool(info.status))
    p.texto(1180, y, "Contador total", pt=9)
    p.texto(1510, y, _valor(contador), pt=10, negrito=bool(contador))
    y += 50
    # A impressora so soma a pagina quando ela SAI: folha pedida enquanto a
    # anterior ainda imprime pega o mesmo contador (21/09/2026, duas folhas
    # com 2s de diferenca sairam com o mesmo numero; a coleta seguinte contou
    # as duas).
    p.texto(0, y, "Contador lido antes desta folha sair. Folhas que ainda estavam imprimindo entram na próxima leitura.", pt=7)
    y += 10
    barra_x, barra_w, barra_h = 330, 1500, 44
    if info.toner:
        for cor, pct in info.toner:
            y += 72
            pct = max(0, min(100, int(pct)))
            p.texto(0, y, cor, pt=10)
            p.moldura(barra_x, y - barra_h + 6, barra_w, barra_h)
            # Preto solido para o preto; cinza medio para as cores — a pagina
            # e a mesma em impressora monocromatica.
            p.retangulo(barra_x, y - barra_h + 6, barra_w * pct / 100, barra_h, cinza=100 if cor == "Preto" else 45)
            p.texto(barra_x + barra_w + 40, y, f"{pct}%", pt=10, negrito=True)
    else:
        y += 72
        p.texto(0, y, "Toner", pt=9)
        p.texto(330, y, _NAO_INFORMADO, pt=10, negrito=True)
        if info.toner_note:
            y += 45
            p.texto(330, y, info.toner_note, pt=8)

    # Paginas por mes: uma barra por mes (ate 12), valor em cima, mes embaixo.
    # Mes em andamento sai mais claro e marcado "parcial"; mes com parte
    # estimada ganha "*" e a nota explica.
    if info.monthly:
        y += 130
        p.texto(0, y, "PÁGINAS POR MÊS", pt=9, negrito=True)
        p.retangulo(0, y + 14, _LARGURA, 2)
        meses = info.monthly[-12:]
        coluna, largura_barra, altura_max = _LARGURA // 12, 140, 260
        base = y + 90 + altura_max
        maior = max(paginas for _, paginas, _, _ in meses) or 1
        for i, (rotulo, paginas, estimadas, em_andamento) in enumerate(meses):
            x = i * coluna
            altura = max(4, round(altura_max * paginas / maior)) if paginas else 3
            p.retangulo(x + 10, base - altura, largura_barra, altura, cinza=25 if em_andamento else 70)
            valor = f"{paginas:,}".replace(",", ".") + ("*" if estimadas else "")
            p.texto(x + 10, base - altura - 18, valor, pt=8, negrito=True)
            p.texto(x + 10, base + 45, rotulo, pt=8)
            if em_andamento:
                p.texto(x + 10, base + 85, "parcial", pt=7)
        y = base + 130
        if any(estimadas for _, _, estimadas, _ in meses):
            p.texto(0, y, "* inclui estimativa dos dias sem coleta no começo do mês, pela média diária medida.", pt=8)
            y += 45
        if any(em_andamento for _, _, _, em_andamento in meses):
            p.texto(0, y, "Mês parcial: ainda em andamento, o total cresce até o fechamento.", pt=8)
            y += 45
        y -= 45  # a proxima secao ja soma a propria folga

    # Escala de cinza: falha, listra ou mancha aqui aponta problema de
    # cilindro/toner, coisa que so texto nao mostra.
    y += 130
    p.texto(0, y, "ESCALA DE CINZA", pt=9, negrito=True)
    p.retangulo(0, y + 14, _LARGURA, 2)
    y += 50
    caixa, espaco = 206, 22
    for i in range(10):
        x = i * (caixa + espaco)
        p.retangulo(x, y, caixa, 150, cinza=(i + 1) * 10)
        p.texto(x + 60, y + 200, f"{(i + 1) * 10}%", pt=9)

    # Rodape: o que o teste prova e o que nao prova.
    y += 330
    p.linha(y, espessura=3)
    # Largura inteira: nome + e-mail de quem pediu nunca e cortado aqui.
    p.texto(0, y + 60, f"Solicitado por {info.requested_by}", pt=9, negrito=True, limite=110)
    p.texto(0, y + 115, "Se esta página saiu, o equipamento recebe trabalhos pela rede (envio direto ao IP, porta 9100).", pt=9)
    p.texto(0, y + 165, "Este teste não passa pelo servidor de impressão nem pelo driver: não confirma a fila do Windows.", pt=9)
    p.texto(0, y + 235, "ABCDEFGHIJKLMNOPQRSTUVWXYZ  abcdefghijklmnopqrstuvwxyz  0123456789  áéíóú âêô ãõ ç", pt=10)

    return envelope_pjl(bytes(p.buf), "PrinterControl - pagina de teste")


def send_raw(ip: str, payload: bytes, port: int = RAW_PORT, timeout: float = CONNECT_TIMEOUT_SECONDS) -> TestPrintResult:
    """Abre TCP na porta RAW e envia o documento. Nunca levanta excecao."""
    try:
        with socket.create_connection((ip, port), timeout=timeout) as sock:
            sock.sendall(payload)
        return TestPrintResult(sent=True, detail="enviado", bytes_sent=len(payload))
    except ConnectionRefusedError:
        return TestPrintResult(sent=False, detail="porta_fechada")
    except (socket.timeout, TimeoutError):
        return TestPrintResult(sent=False, detail="sem_resposta")
    except OSError:
        return TestPrintResult(sent=False, detail="erro_de_rede")
