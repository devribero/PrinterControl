"""
Fase 12 - importa o historico de paginas por impressora (Jan-Jun/2026,
ou o que a planilha tiver) da planilha "Levantamento impressoes" para
PrinterMonthly — a mesma tabela que o fechamento automatico do scheduler
usa (services/scheduler.py). E o que faz GET /monthly-report mostrar
consumo real nos meses anteriores a existencia do backend, em vez de cair
no conjunto de demonstracao.

So biblioteca padrao do Python (zipfile + xml.etree) — sem openpyxl nem
pandas. E um script de uso unico/esporadico (roda de novo quando um mes
novo da planilha ficar pronto), entao nao vale adicionar uma dependencia
permanente ao requirements.txt so por causa dele.

FORMATO ESPERADO DA PLANILHA (aba "Contabilizacao mensal")
------------------------------------------------------------
Blocos por site (um "ELGIN MC", "MANAUS 1 - ...", etc. por bloco), cada um
com uma linha "IP, Modelo, Serial, Departamento, Janeiro..Dezembro" seguida
de uma linha por impressora e uma linha "Total:" no fim. Um bloco e
reconhecido assim: a linha do cabecalho de site tem EXATAMENTE UMA celula
preenchida (o nome do site); a linha seguinte comeca com "IP"; dali em
diante, toda linha com IP valido na primeira coluna e uma impressora, ate
a linha "Total:"/"Total".

Impressoras cujo identificador nao e um IPv4 valido (ex.: "Estoque",
"Backup", "-") sao PULADAS e listadas no relatorio, nunca adivinhadas.

CASAMENTO COM O BANCO
----------------------
So por IP. Quando o IP nao existe no banco, ou existe em mais de uma
impressora (ha duplicidade real na base), a linha fica de fora e aparece
no relatorio "NAO IMPORTADO" — nunca escolhe automaticamente qual
impressora e a certa.

USO
----
    # sempre roda em modo simulacao primeiro — nao grava nada, so mostra
    # o que seria importado e o que ficaria de fora
    .\\venv\\Scripts\\python.exe import_historico_planilha.py "Levantamento impressoes_v6.xlsx"

    # depois de revisar o relatorio, grava de verdade
    .\\venv\\Scripts\\python.exe import_historico_planilha.py "Levantamento impressoes_v6.xlsx" --aplicar

    # planilha de outro ano (padrao: 2026, o ano dos meses da aba)
    .\\venv\\Scripts\\python.exe import_historico_planilha.py planilha.xlsx --ano 2027 --aplicar

Idempotente: rodar de novo (planilha atualizada, com Julho preenchido por
exemplo) so sobrescreve os meses que a nova planilha tiver — mesma chave
(impressora, mes) de upsert_printer_monthly(), nunca duplica.
"""
import argparse
import os
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

SHEET_NAME = "Contabilização mensal"
MONTH_COLUMNS = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
IPV4_RE = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")


class PlanilhaError(Exception):
    pass


def _cell_value(cell, shared):
    t = cell.get("t")
    v = cell.find("m:v", NS)
    if v is None:
        inline = cell.find("m:is/m:t", NS)
        return inline.text if inline is not None else None
    if t == "s":
        return shared[int(v.text)]
    return v.text


def _ler_planilha(caminho: str):
    """Devolve {nome_da_aba: [[celula, ...], ...]} — so a aba SHEET_NAME de fato."""
    if not os.path.exists(caminho):
        raise PlanilhaError(f"Arquivo nao encontrado: {caminho}")

    z = zipfile.ZipFile(caminho)

    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        for si in root.findall("m:si", NS):
            shared.append("".join(t.text or "" for t in si.findall(".//m:t", NS)))

    wb_root = ET.fromstring(z.read("xl/workbook.xml"))
    rels_root = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rid_to_target = {rel.get("Id"): rel.get("Target") for rel in rels_root}

    alvo = None
    for sheet in wb_root.findall(".//m:sheets/m:sheet", NS):
        if sheet.get("name") == SHEET_NAME:
            rid = sheet.get(f"{{{NS_R}}}id")
            alvo = "xl/" + rid_to_target[rid]
            break
    if alvo is None:
        nomes = [s.get("name") for s in wb_root.findall(".//m:sheets/m:sheet", NS)]
        raise PlanilhaError(f"Aba {SHEET_NAME!r} nao encontrada. Abas disponiveis: {nomes}")

    sroot = ET.fromstring(z.read(alvo))
    linhas = []
    for row in sroot.findall(".//m:sheetData/m:row", NS):
        cells = row.findall("m:c", NS)
        linhas.append([_cell_value(c, shared) for c in cells])
    return linhas


def _e_cabecalho_de_site(linha: list) -> bool:
    """Uma linha de cabecalho de site tem EXATAMENTE uma celula preenchida (o nome)."""
    preenchidas = [v for v in linha if v not in (None, "")]
    return len(preenchidas) == 1 and isinstance(preenchidas[0], str)


def _e_linha_ip(linha: list) -> bool:
    return bool(linha) and linha[0] == "IP"


def _e_linha_total(linha: list) -> bool:
    return bool(linha) and isinstance(linha[0], str) and linha[0].strip().lower().startswith("total")


def _num(valor) -> int | None:
    if valor in (None, "", "-"):
        return None
    try:
        return int(round(float(valor)))
    except (TypeError, ValueError):
        return None


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
            for idx, mes in enumerate(MONTH_COLUMNS):
                col = 1 + idx  # "Total:" ocupa a coluna do IP; os meses comecam na coluna seguinte
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


def importar_para_banco(session, impressoras: list[LinhaImpressora], ano: int, aplicar: bool) -> dict:
    """
    Casa cada LinhaImpressora por IP contra o banco e grava (se aplicar=True)
    em PrinterMonthly via upsert_printer_monthly(). Nao commita — quem chama
    decide (main() so commita quando aplicar=True).

    Devolve um dict com as mesmas chaves usadas no relatorio do main(), para
    que o teste automatizado possa checar sem precisar rodar o CLI inteiro.
    """
    from sqlmodel import select

    from app.models.printer import Printer
    from app.services.monthly_report import upsert_printer_monthly

    por_ip: dict[str, list] = {}
    for p in session.exec(select(Printer)).all():
        por_ip.setdefault(p.ip, []).append(p)

    importados = 0
    nao_encontrados: list[str] = []
    ambiguos: list[str] = []
    linhas_gravadas = 0

    for item in impressoras:
        candidatos = por_ip.get(item.ip, [])
        if len(candidatos) == 0:
            nao_encontrados.append(
                f"[{item.site}] linha {item.linha_num}: IP {item.ip} ({item.modelo}, {item.departamento}) "
                f"nao encontrado no banco."
            )
            continue
        if len(candidatos) > 1:
            nomes = ", ".join(f"{p.name} (id={p.id})" for p in candidatos)
            ambiguos.append(
                f"[{item.site}] linha {item.linha_num}: IP {item.ip} bate em {len(candidatos)} "
                f"impressoras no banco ({nomes}) — decida manualmente qual e a certa."
            )
            continue

        printer = candidatos[0]
        importados += 1
        for idx, mes_nome in enumerate(MONTH_COLUMNS, start=1):
            if mes_nome not in item.meses:
                continue
            period = f"{ano}-{idx:02d}"
            mes_inicio = datetime(ano, idx, 1)
            mes_fim = datetime(ano + 1, 1, 1) if idx == 12 else datetime(ano, idx + 1, 1)
            if aplicar:
                upsert_printer_monthly(session, printer.id, period, item.meses[mes_nome], mes_inicio, mes_fim)
            linhas_gravadas += 1

    return {
        "importados": importados,
        "nao_encontrados": nao_encontrados,
        "ambiguos": ambiguos,
        "linhas_gravadas": linhas_gravadas,
    }


def main() -> int:
    # Console do Windows costuma abrir em cp1252/850, nao UTF-8 — sem isto,
    # nomes de site com acento (ex.: "Vila Olimpia") saem como lixo no
    # relatorio, mesmo com o dado lido corretamente.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("planilha", help="Caminho do arquivo .xlsx")
    parser.add_argument("--aplicar", action="store_true", help="Grava de verdade no banco (padrao: so simula)")
    parser.add_argument("--ano", type=int, default=2026, help="Ano dos meses da planilha (padrao: 2026)")
    args = parser.parse_args()

    try:
        linhas = _ler_planilha(args.planilha)
    except PlanilhaError as e:
        print(f"[ERRO] {e}")
        return 1

    impressoras, avisos = _parse_blocos(linhas)

    if not impressoras:
        print("[ERRO] Nenhuma linha de impressora encontrada — formato da planilha mudou?")
        return 1

    # So importa aqui para nao exigir DATABASE_URL/venv soh para --help.
    from sqlmodel import Session

    from app.database import engine

    with Session(engine) as session:
        resultado = importar_para_banco(session, impressoras, args.ano, args.aplicar)
        if args.aplicar:
            session.commit()

    print(f"\n{'=' * 70}")
    print(f"Linhas de impressora lidas na planilha: {len(impressoras)}")
    print(f"Casadas por IP e {'gravadas' if args.aplicar else 'que SERIAM gravadas'}: {resultado['importados']}")
    print(f"Meses/impressora {'gravados' if args.aplicar else 'que SERIAM gravados'}: {resultado['linhas_gravadas']}")

    if resultado["nao_encontrados"]:
        print(f"\n--- IP nao encontrado no banco ({len(resultado['nao_encontrados'])}) ---")
        for msg in resultado["nao_encontrados"]:
            print(f"  {msg}")

    if resultado["ambiguos"]:
        print(f"\n--- IP ambiguo, bate em mais de uma impressora ({len(resultado['ambiguos'])}) ---")
        for msg in resultado["ambiguos"]:
            print(f"  {msg}")

    if avisos:
        print(f"\n--- Avisos ({len(avisos)}) ---")
        for msg in avisos:
            print(f"  {msg}")

    print(f"\n{'=' * 70}")
    if args.aplicar:
        print("GRAVADO no banco.")
    else:
        print("SIMULACAO — nada foi gravado. Revise o relatorio acima e rode de novo com --aplicar.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
