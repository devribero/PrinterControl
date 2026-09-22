r"""
Levantamento mensal em Excel (services/levantamento.py, routes/levantamento.py).

Nao depende da planilha real (dado interno da empresa, fora do repositorio):
monta um .xlsx sintetico pequeno com o MESMO desenho da aba "Contabilizacao
mensal" — tabela de periodos no topo, dois blocos de unidade com linha Total
(uma soma que pula linha, uma formula compartilhada, uma celula de Total que
nem existe), uma segunda aba com formulas apontando para a primeira (uma delas
na coluna errada), calcChain e docProps/app.xml com a lista de abas.

Se a planilha real existir em Downloads, roda tambem uma geracao de fumaca de
Setembro/2026 sobre uma COPIA, contra uma copia do banco local, e imprime so
contagens. O original nunca e tocado.

    cd backend
    env -u DATABASE_URL ./venv/Scripts/python.exe tests_levantamento.py
"""
import io
import os
import shutil
import sqlite3
import sys
import tempfile
import zipfile
from datetime import datetime, timedelta
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

_TMP = Path(tempfile.mkdtemp(prefix="printercontrol-levantamento-"))
os.environ["DATABASE_URL"] = f"sqlite:///{(_TMP / 'lev.db').as_posix()}"
os.environ["ENVIRONMENT"] = "development"
os.environ["PRINT_SERVER_MODE"] = "mock"
os.environ["COLLECTION_ENABLED"] = "false"
os.environ["LEVANTAMENTO_DIR"] = str(_TMP / "levantamento")

from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import Session, create_engine, select  # noqa: E402

from app.config import BACKEND_DIR, settings  # noqa: E402
from app.database import create_db_and_tables, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models.audit_log import AuditLog  # noqa: E402
from app.models.printer import Printer, PrinterReading  # noqa: E402
from app.models.user import Role, User  # noqa: E402
from app.services import levantamento as L  # noqa: E402
from app.services.auth import hash_password  # noqa: E402
from app.services.levantamento_xlsx import PlanilhaXml, validar_pacote  # noqa: E402
from app.services.planilha_levantamento import (  # noqa: E402
    blocos_da_aba,
    interpretar_periodo,
    ler_aba,
    resumo_da_aba,
)

SENHA = "senha-de-teste-123"
REAL = Path(r"C:\Users\aprendiz.tijund\Downloads\Levantamento impressões_v8.xlsx")
failures = []


def check(label, got, expected):
    ok = got == expected
    print(f"[{'OK ' if ok else 'FAIL'}] {label}: {got!r}" + ("" if ok else f" (esperado {expected!r})"))
    if not ok:
        failures.append(label)


# ─────────────────────────────────────────────────────────────────────────
#  Planilha sintetica
# ─────────────────────────────────────────────────────────────────────────

MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
MESES = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
         "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
COLS = "EFGHIJKLMNOP"  # Janeiro..Dezembro


def _periodo(i):
    if i == 0:
        return "02/01/26 a 03/02/26"
    if i == 11:
        return "04/12/26 a 03/01/27"
    return f"04/{i + 1:02d}/26 a 03/{i + 2:02d}/26"


def montar_fixture() -> bytes:
    strings: list[str] = []

    def s(texto):
        if texto not in strings:
            strings.append(texto)
        return strings.index(texto)

    def txt(ref, texto, estilo=1):
        return f'<c r="{ref}" s="{estilo}" t="s"><v>{s(texto)}</v></c>'

    def num(ref, valor, estilo=2):
        return f'<c r="{ref}" s="{estilo}"><v>{valor}</v></c>'

    rows = {}
    rows[1] = [txt("D1", "Impressões mensais")]
    rows[2] = [txt("D2", "Mês"), txt("E2", "Período"), txt("F2", "Impressões")]
    for i, mes in enumerate(MESES):
        r = 3 + i
        c = COLS[i]
        # Agosto (linha 10) com o bug de omitir um bloco, como F4/F7 da real.
        soma = f"SUM({c}23)" if mes == "Agosto" else f"SUM({c}23,{c}30)"
        rows[r] = [txt(f"D{r}", mes), txt(f"E{r}", _periodo(i)), f'<c r="F{r}" s="2"><f>{soma}</f><v>0</v></c>']

    # Bloco 1 — linhas 17 (titulo) a 23 (Total).
    rows[17] = [txt("D17", "UNIDADE A")]
    rows[18] = [txt("A18", "IP"), txt("B18", "Modelo", 3), txt("C18", "Serial"), txt("D18", "Departamento")] + [
        txt(f"{COLS[i]}18", MESES[i]) for i in range(12)]
    dispositivos_1 = [
        (19, "10.0.0.1", "Kyocera M1", "SER1", "TI"),        # mudou para 10.0.0.99 (serial via SNMP)
        (20, "10.0.0.2", "Ricoh M2", "-", "RH"),             # so pelo IP
        (21, "10.0.0.3", "Kyocera M3", "SER3", "Financeiro"),  # no banco, sem leitura
        (22, "Estoque", "Kyocera M4", "SER4", "Backup"),     # nao existe no sistema
    ]
    for r, ip, modelo, serial, dep in dispositivos_1:
        celulas = [txt(f"A{r}", ip), txt(f"B{r}", modelo), txt(f"C{r}", serial), txt(f"D{r}", dep)]
        celulas += [num(f"{COLS[i]}{r}", 100 * (i + 1) + r) for i in range(7)]  # Jan..Jul
        if r != 22:  # linha 22 nao tem celula nenhuma de Ago..Dez: o gerador cria
            celulas += [f'<c r="{COLS[i]}{r}" s="2"/>' for i in range(7, 12)]
        rows[r] = celulas
    rows[23] = [txt("D23", "Total")] + [
        f'<c r="{COLS[i]}23" s="2"><f>SUM({COLS[i]}19:{COLS[i]}22)</f><v>1</v></c>' for i in range(7)
    ] + [
        '<c r="L23" s="2"><f>SUM(L19:L21)</f><v>0</v></c>',  # soma que pula a linha 22
        '<c r="M23" s="2"><f>SUM(M19:M20)</f><v>0</v></c>',
        '<c r="N23" s="2"><f t="shared" ref="N23:P23" si="0">SUM(N19:N20)</f><v>0</v></c>',
        '<c r="O23" s="2"><f t="shared" si="0"/><v>0</v></c>',
        '<c r="P23" s="2"><f t="shared" si="0"/><v>0</v></c>',
    ]

    # Bloco 2 — linhas 26 a 30; Total de Ago..Dez inexistente.
    rows[26] = [txt("D26", "UNIDADE B")]
    rows[27] = [txt("A27", "IP"), txt("C27", "Serial"), txt("D27", "Departamento")] + [
        txt(f"{COLS[i]}27", MESES[i]) for i in range(12)]
    for r, ip, modelo, serial, dep in [
        (28, "10.0.1.1", "Kyocera M5", "SER5", "Logística"),
        (29, "10.0.1.2", "Kyocera M6", "SERX", "Qualidade"),  # no IP o SNMP le outro serial
    ]:
        rows[r] = [txt(f"A{r}", ip), txt(f"B{r}", modelo), txt(f"C{r}", serial), txt(f"D{r}", dep)] + [
            num(f"{COLS[i]}{r}", 10 * (i + 1)) for i in range(7)] + [
            f'<c r="{COLS[i]}{r}" s="2"/>' for i in range(7, 12)]
    rows[30] = [txt("D30", "Total:")] + [
        f'<c r="{COLS[i]}30" s="4"><f>SUM({COLS[i]}28:{COLS[i]}29)</f><v>0</v></c>' for i in range(7)]

    sheet_data = "".join(
        f'<row r="{r}" spans="1:16">{"".join(c)}</row>' for r, c in sorted(rows.items())
    )
    sheet1 = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        f'<worksheet xmlns="{MAIN}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" mc:Ignorable="x14ac" '
        'xmlns:x14ac="http://schemas.microsoft.com/office/spreadsheetml/2009/9/ac">'
        '<dimension ref="A1:P30"/><sheetData>' + sheet_data + '</sheetData>'
        '<mergeCells count="1"><mergeCell ref="D17:P17"/></mergeCells></worksheet>'
    )
    ref = "'Contabilização mensal'!"
    sheet2 = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        f'<worksheet xmlns="{MAIN}"><sheetData><row r="2">'
        f'<c r="B2"><f>SUM({ref}E19)</f><v>0</v></c>'
        f'<c r="C2"><f>SUM({ref}F19)</f><v>0</v></c>'
        f'<c r="D2"><f>SUM({ref}J19)</f><v>0</v></c>'  # vizinhas dariam G19
        f'<c r="E2"><f>SUM({ref}H19)</f><v>0</v></c>'
        '</row></sheetData></worksheet>'
    )
    shared = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        f'<sst xmlns="{MAIN}" count="{len(strings)}" uniqueCount="{len(strings)}">'
        + "".join(f"<si><t>{t}</t></si>" for t in strings) + "</sst>"
    )
    styles = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        f'<styleSheet xmlns="{MAIN}"><fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts>'
        '<fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>'
        '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
        '<cellXfs count="5">' + '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>' * 5 + '</cellXfs>'
        '</styleSheet>'
    )
    workbook = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        f'<workbook xmlns="{MAIN}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheets><sheet name="Contabilização mensal" sheetId="1" r:id="rId1"/>'
        '<sheet name="3 meses" sheetId="5" r:id="rId2"/></sheets><calcPr calcId="191028"/></workbook>'
    )
    rel = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    wb_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        f'<Relationship Id="rId1" Type="{rel}/worksheet" Target="worksheets/sheet1.xml"/>'
        f'<Relationship Id="rId2" Type="{rel}/worksheet" Target="worksheets/sheet2.xml"/>'
        f'<Relationship Id="rId3" Type="{rel}/styles" Target="styles.xml"/>'
        f'<Relationship Id="rId4" Type="{rel}/sharedStrings" Target="sharedStrings.xml"/>'
        f'<Relationship Id="rId5" Type="{rel}/calcChain" Target="calcChain.xml"/>'
        '</Relationships>'
    )
    ct_ws = "application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        f'<Override PartName="/xl/worksheets/sheet1.xml" ContentType="{ct_ws}"/>'
        f'<Override PartName="/xl/worksheets/sheet2.xml" ContentType="{ct_ws}"/>'
        '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        '<Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/>'
        '<Override PartName="/xl/calcChain.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.calcChain+xml"/>'
        '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
        '</Types>'
    )
    root_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        f'<Relationship Id="rId1" Type="{rel}/officeDocument" Target="xl/workbook.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
        '</Relationships>'
    )
    app_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
        'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"><Application>Microsoft Excel</Application>'
        '<HeadingPairs><vt:vector size="2" baseType="variant"><vt:variant><vt:lpstr>Worksheets</vt:lpstr></vt:variant>'
        '<vt:variant><vt:i4>2</vt:i4></vt:variant></vt:vector></HeadingPairs>'
        '<TitlesOfParts><vt:vector size="2" baseType="lpstr"><vt:lpstr>Contabilização mensal</vt:lpstr>'
        '<vt:lpstr>3 meses</vt:lpstr></vt:vector></TitlesOfParts></Properties>'
    )
    calc_chain = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        f'<calcChain xmlns="{MAIN}"><c r="E23" i="1"/><c r="L23" i="1"/></calcChain>'
    )
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", root_rels)
        z.writestr("docProps/app.xml", app_xml)
        z.writestr("xl/workbook.xml", workbook)
        z.writestr("xl/_rels/workbook.xml.rels", wb_rels)
        z.writestr("xl/styles.xml", styles)
        z.writestr("xl/sharedStrings.xml", shared)
        z.writestr("xl/worksheets/sheet1.xml", sheet1)
        z.writestr("xl/worksheets/sheet2.xml", sheet2)
        z.writestr("xl/calcChain.xml", calc_chain)
    return buf.getvalue()


def aba1(dados: bytes) -> PlanilhaXml:
    with zipfile.ZipFile(io.BytesIO(dados)) as z:
        return PlanilhaXml(z.read("xl/worksheets/sheet1.xml").decode("utf-8"))


def parte(dados: bytes, nome: str) -> str | None:
    with zipfile.ZipFile(io.BytesIO(dados)) as z:
        return z.read(nome).decode("utf-8") if nome in z.namelist() else None


def valor(celulas, ref):
    from app.services.levantamento_xlsx import split_ref
    col, lin = split_ref(ref)
    return celulas.get(lin, {}).get(col)


# ─────────────────────────────────────────────────────────────────────────
#  Banco: impressoras e leituras
# ─────────────────────────────────────────────────────────────────────────

AGORA = datetime(2026, 9, 22, 15, 0)  # UTC; agosto (04/08-03/09) fechado, setembro aberto


def leituras(s, printer, inicio, fim, contador_inicial, por_dia):
    """Uma leitura por dia de `inicio` a `fim` (inclusive), contador crescendo por_dia."""
    t, pc = inicio, contador_inicial
    while t <= fim:
        s.add(PrinterReading(printer_id=printer.id, status="online", page_count=pc, timestamp=t))
        t += timedelta(days=1)
        pc += por_dia


def preparar_banco():
    create_db_and_tables()
    with Session(engine) as s:
        for papel, role in (("admin", Role.ADMIN.value), ("viewer", Role.VIEWER.value)):
            s.add(User(email=f"{papel}@teste-lev.com", password_hash=hash_password(SENHA), name=papel, role=role,
                       is_active=True))
        confirmado = datetime(2026, 9, 20)
        p_movida = Printer(server="", name="A_movida", ip="10.0.0.99", model="Kyocera M1", serial_number="SER1",
                           snmp_updated_at=confirmado, active=True)
        p_ip = Printer(server="", name="A_rh", ip="10.0.0.2", model="Ricoh M2", active=True)
        p_ip_2 = Printer(server="", name="A_rh_fila2", ip="10.0.0.2", model="Ricoh M2", active=True)
        p_sem = Printer(server="", name="A_fin", ip="10.0.0.3", model="Kyocera M3", serial_number="SER3", active=True)
        p_b1 = Printer(server="", name="B_log", ip="10.0.1.1", model="Kyocera M5", active=True)
        p_troc = Printer(server="", name="B_troc", ip="10.0.1.2", model="Kyocera M9", serial_number="OUTRO9",
                         snmp_updated_at=confirmado, active=True, department="Qualidade — Unidade B")
        p_novo = Printer(server="", name="Nova_X", ip="10.0.9.9", model="HP Nova", serial_number="NOVO1",
                         snmp_updated_at=confirmado, active=True, printer_type="A4")
        for p in (p_movida, p_ip, p_ip_2, p_sem, p_b1, p_troc, p_novo):
            s.add(p)
        s.commit()
        # Leituras de 01/08 00:00 UTC a 21/09 00:00 UTC, uma por dia, 10 paginas/dia
        # (80/dia na movida, 20/dia na do IP). A fila 2 do mesmo IP recebe a mesma
        # leitura (mesmo contador): o equipamento conta uma vez so.
        ini, fim = datetime(2026, 8, 1), datetime(2026, 9, 21)
        leituras(s, p_movida, ini, fim, 1000, 80)
        leituras(s, p_ip, ini, fim, 5000, 20)
        leituras(s, p_ip_2, ini, fim, 5000, 20)
        leituras(s, p_b1, ini, fim, 300, 10)
        leituras(s, p_troc, ini, fim, 700, 5)
        leituras(s, p_novo, ini, fim, 50, 3)
        s.commit()
        return {p.name: p.id for p in (p_movida, p_ip, p_ip_2, p_sem, p_b1, p_troc, p_novo)}


# ─────────────────────────────────────────────────────────────────────────
#  Testes
# ─────────────────────────────────────────────────────────────────────────

def main():
    print("--- 1. periodo da planilha ---")
    check("setembro", interpretar_periodo("04/09/26 a 03/10/26"), (datetime(2026, 9, 4), datetime(2026, 10, 4)))
    check("janeiro comeca dia 2", interpretar_periodo("02/01/26 a 03/02/26"), (datetime(2026, 1, 2), datetime(2026, 2, 4)))
    check("dezembro vira o ano", interpretar_periodo("04/12/26 a 03/01/27")[1], datetime(2027, 1, 4))
    check("texto ilegivel", interpretar_periodo("setembro"), None)
    check("meia-noite de SP = 03:00 UTC", L._para_utc(datetime(2026, 9, 4)), datetime(2026, 9, 4, 3, 0))

    fixture = montar_fixture()
    celulas = ler_aba(fixture)
    blocos = blocos_da_aba(celulas)
    resumo = resumo_da_aba(celulas)
    check("dois blocos", [b.titulo for b in blocos], ["UNIDADE A", "UNIDADE B"])
    check("bloco A: linhas 19-22 (inclui Estoque)", [i.linha_num for i in blocos[0].itens], [19, 20, 21, 22])
    check("bloco A: Total na linha 23", blocos[0].linha_total, 23)
    check("bloco B: coluna de Setembro = M", blocos[1].colunas_mes["Setembro"], 12)
    check("resumo: Setembro na linha 11, total na coluna F", (resumo["Setembro"].linha, resumo["Setembro"].coluna_total), (11, 5))

    ids = preparar_banco()
    settings.levantamento_dir = str(_TMP / "levantamento")
    L.substituir_base(fixture, "fixture.xlsx", origem="semente")
    base_antes = L.caminho_base().read_bytes()

    print("\n--- 2. gerar Agosto (periodo fechado) ---")
    with Session(engine) as s:
        rel = L.gerar(s, "2026-08", agora=AGORA)
    check("nao e previa", rel["previa"], False)
    check("nome do arquivo", rel["arquivo"], "Levantamento impressões_Agosto_2026.xlsx")
    check("periodo", (rel["periodo"]["inicio"], rel["periodo"]["fim"]), ("2026-08-04", "2026-09-03"))
    saida = (L.pasta_gerados() / rel["arquivo"]).read_bytes()
    check("pacote valido (zip + XML + rels)", validar_pacote(saida), [])
    cel = ler_aba(saida)

    # 04/08 03:00 UTC -> 04/09 03:00 UTC = 31 dias; leituras diarias a 00:00.
    esperado_movida = round(80 * 31)
    esperado_ip = round(20 * 31)
    check("L19: casado pelo serial (IP mudou)", valor(cel, "L19"), str(esperado_movida))
    check("L20: casado pelo IP, duas filas contam uma vez", valor(cel, "L20"), str(esperado_ip))
    check("L21: no banco sem leitura -> vazia", valor(cel, "L21"), None)
    check("L22: Estoque -> vazia", valor(cel, "L22"), None)
    check("L28: bloco B pelo IP", valor(cel, "L28"), str(10 * 31))
    check("L29: SNMP le outro equipamento -> vazia", valor(cel, "L29"), None)
    check("K19 (mes passado) intacto", valor(cel, "K19"), "719")
    check("preenchidas", rel["preenchidas"]["linhas"], 3)
    motivos = {v["linha"]: v["motivo"] for v in rel["vazias"]}
    check("vazias: linhas 21, 22, 29", sorted(motivos), [21, 22, 29])
    check("motivo sem leitura", motivos[21], "sem leitura no período")
    check("motivo nao encontrado", motivos[22], "não encontrado no sistema (sem IP na planilha)")
    check("motivo conflito", motivos[29].startswith("no IP da planilha o sistema lê outro equipamento"), True)
    novos = sorted(n["ip"] for n in rel["novos"])
    check("novos: o do IP trocado e o que nao esta na planilha", novos, ["10.0.1.2", "10.0.9.9"])

    x = aba1(saida)
    check("L22 criada com o estilo da vizinha (K22)", x.estilo("L22"), "2")
    check("Total L23 corrigido", x.formula("L23"), "SUM(L19:L22)")
    check("Total L23 sem valor em cache", "<v>" in x.celula("L23"), False)
    check("Total M23 (mes seguinte vazio) corrigido", x.formula("M23"), "SUM(M19:M22)")
    check("Total O23 (era filha de formula compartilhada)", x.formula("O23"), "SUM(O19:O22)")
    check("sem formula compartilhada orfa na linha 23", 't="shared"' in x.linhas[23].serializar(), False)
    check("Total M30 criado (nao existia)", x.formula("M30"), "SUM(M28:M29)")
    check("Total M30 com estilo da vizinha (L30)", x.estilo("M30"), "4")
    check("Total K23 (mes passado) intacto", x.celula("K23"), '<c r="K23" s="2"><f>SUM(K19:K22)</f><v>1</v></c>')
    check("resumo F10 (Agosto) soma os dois blocos", x.formula("F10"), "SUM(L23,L30)")
    check("resumo F9 (Julho) intacto", x.formula("F9"), "SUM(K23,K30)")
    corrigidas = {c["celula"] for c in rel["correcoes_formula"]}
    check("correcoes listam L23, M30 e F10", {"L23", "M30", "F10"} <= corrigidas, True)
    check("correcoes nao tocam meses passados", any(c.startswith("K") for c in corrigidas), False)

    wb = parte(saida, "xl/workbook.xml")
    check("fullCalcOnLoad", 'fullCalcOnLoad="1"' in wb, True)
    check("calcChain removido do zip", parte(saida, "xl/calcChain.xml"), None)
    check("calcChain fora do [Content_Types]", "calcChain" in parte(saida, "[Content_Types].xml"), False)
    check("calcChain fora do workbook.xml.rels", "calcChain" in parte(saida, "xl/_rels/workbook.xml.rels"), False)
    check("aba nova registrada no workbook", 'name="Novos no sistema"' in wb, True)
    app_xml = parte(saida, "docProps/app.xml")
    check("app.xml lista a aba nova", "<vt:lpstr>Novos no sistema</vt:lpstr>" in app_xml, True)
    check("app.xml conta 3 abas", "<vt:i4>3</vt:i4>" in app_xml, True)
    novos_aba = ler_aba(saida, "Novos no sistema")
    ips_aba = sorted(v.get(0) for n, v in novos_aba.items() if n > 3 and v.get(0))
    check("aba 'Novos no sistema' com os IPs", ips_aba, ["10.0.1.2", "10.0.9.9"])
    check("aba '3 meses' intacta", parte(saida, "xl/worksheets/sheet2.xml"), parte(fixture, "xl/worksheets/sheet2.xml"))
    check("aviso da formula na coluna errada ('3 meses' D2)",
          any("'3 meses' D2" in a for a in rel["avisos"]), True)
    check("periodo fechado atualiza a base", rel["base_atualizada"], True)
    check("base = arquivo gerado", L.caminho_base().read_bytes(), saida)
    check("base anterior guardada como backup",
          [a["tipo"] for a in L.estado(AGORA)["arquivos"]].count("base_anterior"), 1)

    print("\n--- 3. gerar Setembro (em andamento) = previa ---")
    base_agosto = L.caminho_base().read_bytes()
    with Session(engine) as s:
        rel9 = L.gerar(s, "2026-09", agora=AGORA)
    check("previa", rel9["previa"], True)
    check("nome com (prévia)", rel9["arquivo"], "Levantamento impressões_Setembro_2026 (prévia).xlsx")
    check("previa nao atualiza a base", rel9["base_atualizada"], False)
    check("base continua a de agosto", L.caminho_base().read_bytes(), base_agosto)
    s9 = (L.pasta_gerados() / rel9["arquivo"]).read_bytes()
    x9 = aba1(s9)
    check("setembro preenchido na coluna M", ler_aba(s9)[19].get(12) is not None, True)
    check("agosto continua la (veio da base)", valor(ler_aba(s9), "L19"), str(esperado_movida))
    check("Total L23 de agosto nao e reescrito de novo", x9.celula("L23"), aba1(base_agosto).celula("L23"))
    check("uma aba 'Novos no sistema' so (recriada)", parte(s9, "xl/workbook.xml").count('name="Novos no sistema"'), 1)
    check("pacote da previa valido", validar_pacote(s9), [])

    print("\n--- 4. estado, mes invalido, ano diferente ---")
    est = L.estado(AGORA)
    check("meses preenchidos na base", est["base"]["meses_preenchidos"][-1], "2026-08")
    check("proximo mes", est["proximo_mes"], "2026-09")
    check("ultimo mes fechado", est["ultimo_mes_fechado"], "2026-08")
    for mes, trecho in (("2026-13", "invalido"), ("2027-01", "base e de 2026"), ("2026-11", "ainda nao comecou")):
        try:
            with Session(engine) as s:
                L.gerar(s, mes, agora=AGORA)
            check(f"{mes} recusado", False, True)
        except L.LevantamentoError as e:
            check(f"{mes} recusado ({trecho})", trecho in str(e), True)

    print("\n--- 5. nome de arquivo para download ---")
    for ruim in ("../base.xlsx", "..\\base.xlsx", "base.xlsx", "index.json", "/etc/passwd", "", "Levantamento.xlsx"):
        try:
            L.arquivo_para_download(ruim)
            check(f"{ruim!r} recusado", False, True)
        except L.LevantamentoError:
            check(f"{ruim!r} recusado", True, True)
    check("nome da lista aceito", L.arquivo_para_download(rel["arquivo"]).name, rel["arquivo"])

    print("\n--- 6. geracao automatica do periodo fechado ---")
    depois = datetime(2026, 10, 5, 12, 0)
    check("setembro pendente em 05/10", L.mes_fechado_pendente(depois), "2026-09")
    with Session(engine) as s:
        check("sem leitura depois do fim do periodo, espera", L.gerar_pendente(s, depois), None)
        p = s.get(Printer, ids["Nova_X"])
        s.add(PrinterReading(printer_id=p.id, status="online", page_count=999, timestamp=datetime(2026, 10, 4, 5)))
        s.commit()
        auto = L.gerar_pendente(s, depois)
    check("gerado automaticamente", (auto or {}).get("automatico"), True)
    check("fechado -> base atualizada", (auto or {}).get("base_atualizada"), True)
    check("nada mais pendente", L.mes_fechado_pendente(depois), None)

    print("\n--- 7. API ---")
    client = TestClient(app)

    def token(papel):
        r = client.post("/api/auth/login", json={"email": f"{papel}@teste-lev.com", "password": SENHA})
        return {"Authorization": f"Bearer {r.json()['access_token']}"}

    admin, viewer = token("admin"), token("viewer")
    L_agora_original = L._agora_utc
    L._agora_utc = lambda: AGORA
    try:
        check("sem token 401", client.get("/api/levantamento").status_code, 401)
        r = client.get("/api/levantamento", headers=viewer)
        check("viewer le o estado", r.status_code, 200)
        check("estado traz arquivos", len(r.json()["arquivos"]) >= 3, True)
        check("viewer nao gera (403)", client.post("/api/levantamento/gerar", json={"mes": "2026-09"}, headers=viewer).status_code, 403)
        check("mes mal formatado (422)", client.post("/api/levantamento/gerar", json={"mes": "set/26"}, headers=admin).status_code, 422)
        r = client.post("/api/levantamento/gerar", json={"mes": "2026-10"}, headers=admin)
        check("mes que nao comecou (400)", r.status_code, 400)
        r = client.post("/api/levantamento/gerar", json={"mes": "2026-09"}, headers=admin)
        check("admin gera (200)", r.status_code, 200)
        nome = r.json().get("arquivo", "")
        r = client.get(f"/api/levantamento/arquivos/{nome}", headers=viewer)
        check("viewer baixa um arquivo da lista", (r.status_code, r.content[:2]), (200, b"PK"))
        check("download com tipo xlsx", r.headers["content-type"].startswith("application/vnd.openxmlformats"), True)
        check("download fora da lista (404)", client.get("/api/levantamento/arquivos/base.xlsx", headers=viewer).status_code, 404)
        check("download com ..%2F (404)", client.get("/api/levantamento/arquivos/..%2Fbase.xlsx", headers=viewer).status_code, 404)
        check("relatorio guardado", client.get(f"/api/levantamento/relatorio/{nome}", headers=viewer).json().get("mes"), "2026-09")

        arq = {"arquivo": ("x.xlsx", b"nao e zip", "application/octet-stream")}
        check("viewer nao envia base (403)", client.post("/api/levantamento/base", files=arq, headers=viewer).status_code, 403)
        check("base que nao e xlsx (400)", client.post("/api/levantamento/base", files=arq, headers=admin).status_code, 400)
        outra = io.BytesIO()
        with zipfile.ZipFile(outra, "w") as z:
            z.writestr("xl/workbook.xml", "<workbook/>")
        arq = {"arquivo": ("outra.xlsx", outra.getvalue(), "application/octet-stream")}
        check("zip sem a aba esperada (400)", client.post("/api/levantamento/base", files=arq, headers=admin).status_code, 400)
        arq = {"arquivo": ("Levantamento v9.xlsx", fixture, "application/octet-stream")}
        r = client.post("/api/levantamento/base", files=arq, headers=admin)
        check("admin envia base valida", r.status_code, 200)
        check("backup da base anterior", bool(r.json().get("backup")), True)
        check("base trocada", L.caminho_base().read_bytes(), fixture)
        est = client.get("/api/levantamento", headers=viewer).json()
        check("base enviada por upload", est["base"]["origem"], "upload")
        check("proximo mes volta a agosto", est["proximo_mes"], "2026-08")
    finally:
        L._agora_utc = L_agora_original

    with Session(engine) as s:
        acoes = sorted({a.action for a in s.exec(select(AuditLog)).all()})
    check("trilha de auditoria", acoes, ["levantamento.generate", "levantamento.upload_base"])
    check("base original intacta nos testes", base_antes == fixture, True)

    fumaca_planilha_real()


def fumaca_planilha_real():
    """Setembro/2026 sobre uma COPIA da v8 e uma COPIA do banco local. So contagens."""
    print("\n--- 8. fumaca com a planilha real (se existir) ---")
    banco = BACKEND_DIR / "printer_control.db"
    if not REAL.exists() or not banco.exists():
        print("  (planilha real ou banco local ausente — pulado)")
        return
    pasta = Path(tempfile.mkdtemp(prefix="lev-fumaca-"))
    copia = pasta / "v8.xlsx"
    shutil.copyfile(REAL, copia)
    copia_banco = pasta / "banco.db"
    origem = sqlite3.connect(f"file:{banco.as_posix()}?mode=ro", uri=True)
    destino = sqlite3.connect(copia_banco)
    origem.backup(destino)
    origem.close()
    destino.close()

    settings.levantamento_dir = str(pasta / "levantamento")
    try:
        L.substituir_base(copia.read_bytes(), copia.name, origem="semente")
        eng = create_engine(f"sqlite:///{copia_banco.as_posix()}")
        with Session(eng) as s:
            rel = L.gerar(s, "2026-09")
        saida = (L.pasta_gerados() / rel["arquivo"]).read_bytes()
        check("fumaca: pacote valido", validar_pacote(saida), [])
        check("fumaca: original intacto", REAL.read_bytes() == copia.read_bytes(), True)
        motivos = {}
        for v in rel["vazias"]:
            chave = v["motivo"].split(" (")[0]
            motivos[chave] = motivos.get(chave, 0) + 1
        print(f"  arquivo: {rel['arquivo']} | previa={rel['previa']} | periodo {rel['periodo']['texto']}")
        print(f"  preenchidas: {rel['preenchidas']['linhas']} linhas, {rel['preenchidas']['paginas']} paginas "
              f"({rel['preenchidas']['estimadas']} estimadas)")
        print(f"  vazias: {len(rel['vazias'])} {motivos}")
        print(f"  novos no sistema: {len(rel['novos'])} | correcoes de formula: {len(rel['correcoes_formula'])} "
              f"| avisos: {len(rel['avisos'])}")
        for a in rel["avisos"]:
            print(f"    - {a}")
    finally:
        settings.levantamento_dir = str(_TMP / "levantamento")
        # Copias da planilha e do banco sao dado interno: nao ficam no %TEMP%.
        try:
            eng.dispose()
        except NameError:
            pass
        shutil.rmtree(pasta, ignore_errors=True)


if __name__ == "__main__":
    main()
    print(f"\nPasta de teste: {_TMP}")
    print("RESULTADO:", "TODOS OS TESTES PASSARAM" if not failures else f"FALHAS: {failures}")
    raise SystemExit(1 if failures else 0)
