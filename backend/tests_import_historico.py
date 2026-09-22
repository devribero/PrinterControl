"""
Fase 12 - importador de historico de planilha (import_historico_planilha.py).

Nao depende do arquivo .xlsx real (e dado privado da empresa, nao fica no
repositorio) — usa uma estrutura de linhas sintetica, no mesmo formato que
_parse_blocos() espera, pra testar deteccao de bloco/site, validacao de IP,
aviso de total divergente, e o casamento+gravacao contra um banco temporario.

Executar:  .\\venv\\Scripts\\python.exe tests_import_historico.py
"""
import os
import tempfile
from datetime import datetime

DB = os.path.join(tempfile.gettempdir(), "test_import_historico.db")
if os.path.exists(DB):
    os.remove(DB)
os.environ["DATABASE_URL"] = f"sqlite:///{DB}"

from sqlmodel import Session, select  # noqa: E402

from app.database import create_db_and_tables, engine  # noqa: E402
from app.models.printer import Printer, PrinterMonthly  # noqa: E402
from import_historico_planilha import _num, _parse_blocos, importar_para_banco  # noqa: E402

failures = []


def check(label, got, expected):
    ok = got == expected
    print(f"[{'OK ' if ok else 'FAIL'}] {label}: {got}" + ("" if ok else f" (esperado {expected})"))
    if not ok:
        failures.append(label)


print("--- 1. _num: valores validos e invalidos ---")
check("inteiro", _num("162"), 162)
check("decimal vira inteiro arredondado", _num("162.7"), 163)
check("None", _num(None), None)
check("string vazia", _num(""), None)
check("traco (sem dado)", _num("-"), None)
check("zero", _num("0"), 0)

print("\n--- 2. _parse_blocos: dois sites, IP invalido pulado, total OK ---")
linhas_sinteticas = [
    ["Impressões mensais"],
    ["Mês", "Período", "Impressões"],
    ["Janeiro", "x", "999"],
    [None],
    ["SITE TESTE 1"],
    ["IP", "Modelo", "Serial", "Departamento", "Janeiro", "Fevereiro"],
    ["10.1.1.1", "ModeloA", "SER1", "TI", "100", "150"],
    ["10.1.1.2", "ModeloB", "SER2", "RH", "50", "60"],
    ["Estoque", "ModeloC", "SER3", "Backup", "0", "0"],
    ["Total:", "150", "210"],
    [None],
    ["SITE TESTE 2"],
    ["IP", "Modelo", "Serial", "Departamento", "Janeiro", "Fevereiro"],
    ["10.2.2.2", "ModeloD", "SER4", "Automação", "300", "400"],
    ["Total:", "999", "400"],  # Janeiro proposital errado, pra testar o aviso
]
impressoras, avisos = _parse_blocos(linhas_sinteticas)

check("3 impressoras validas (Estoque pulado)", len(impressoras), 3)
check("primeira e do site 1", impressoras[0].site, "SITE TESTE 1")
check("IP da primeira", impressoras[0].ip, "10.1.1.1")
check("meses da primeira", impressoras[0].meses, {"Janeiro": 100, "Fevereiro": 150})
check("terceira e do site 2", impressoras[2].site, "SITE TESTE 2")

skip_avisos = [a for a in avisos if "Estoque" in a]
check("aviso de IP invalido (Estoque) gerado", len(skip_avisos), 1)

total_avisos = [a for a in avisos if "Total de Janeiro" in a and "SITE TESTE 2" in a]
check("aviso de total divergente do site 2 gerado", len(total_avisos), 1)
total_avisos_site1 = [a for a in avisos if "SITE TESTE 1" in a and "Total de" in a]
check("site 1 nao gerou aviso de total (bateu certo)", len(total_avisos_site1), 0)

print("\n--- 3. importar_para_banco: casamento por IP, ambiguidade, gravacao ---")
with Session(engine) as s:
    create_db_and_tables()
    p_ok = Printer(server="x", name="Financeiro_A", ip="10.1.1.1", model="M", department="TI", active=True)
    p_dup1 = Printer(server="x", name="RH_A", ip="10.1.1.2", model="M", department="RH", active=True)
    p_dup2 = Printer(server="x", name="RH_A_dup", ip="10.1.1.2", model="M", department="RH", active=True)
    s.add(p_ok)
    s.add(p_dup1)
    s.add(p_dup2)
    s.commit()
    s.refresh(p_ok)

    # 10.2.2.2 (site teste 2) propositalmente NAO existe no banco.
    # 21/09/2026: 10.1.1.2 com duas filas deixou de ser "ambiguo" — um IP e
    # UM equipamento, e o historico vai para uma fila so (a de menor id).
    resultado = importar_para_banco(s, impressoras, ano=2026, aplicar=False)
    check("2 equipamentos casados (10.1.1.1 e o de duas filas)", resultado["importados"], 2)
    check("1 IP nao encontrado (10.2.2.2)", len(resultado["nao_encontrados"]), 1)
    check("nenhum ambiguo", len(resultado["ambiguos"]), 0)
    check("equipamento de duas filas listado", len(resultado["multiplas_filas"]), 1)
    check("simulacao nao grava nada no banco", s.exec(select(PrinterMonthly)).all(), [])

    resultado2 = importar_para_banco(s, impressoras, ano=2026, aplicar=True)
    s.commit()
    check("com --aplicar, grava 2 meses x 2 equipamentos", len(s.exec(select(PrinterMonthly)).all()), 4)
    hist_dup = {
        m.printer_id for m in s.exec(select(PrinterMonthly).where(PrinterMonthly.printer_id.in_([p_dup1.id, p_dup2.id])))
    }
    check("historico do IP de duas filas so na de menor id", hist_dup, {p_dup1.id})
    s.refresh(p_dup2)
    check("departamento vai para as duas filas do equipamento", p_dup2.department, "RH — Site Teste 1")
    check("serial preenchido onde o banco nao tinha", p_dup2.serial_number, "SER2")
    jan = s.exec(
        select(PrinterMonthly).where(PrinterMonthly.printer_id == p_ok.id).where(PrinterMonthly.month == "2026-01")
    ).first()
    check("Janeiro/26 de 10.1.1.1 gravado com o valor certo", jan.pages_printed if jan else None, 100)

    print("\n--- 4. rodar de novo (planilha atualizada) sobrescreve, nao duplica ---")
    linhas_atualizadas = [
        ["SITE TESTE 1"],
        ["IP", "Modelo", "Serial", "Departamento", "Janeiro", "Fevereiro"],
        ["10.1.1.1", "ModeloA", "SER1", "TI", "888", "150"],
        ["Total:", "888", "150"],
    ]
    impressoras2, _ = _parse_blocos(linhas_atualizadas)
    importar_para_banco(s, impressoras2, ano=2026, aplicar=True)
    s.commit()
    linhas_jan = s.exec(
        select(PrinterMonthly).where(PrinterMonthly.printer_id == p_ok.id).where(PrinterMonthly.month == "2026-01")
    ).all()
    check("continua 1 linha so (upsert)", len(linhas_jan), 1)
    check("valor atualizado pro novo numero da planilha", linhas_jan[0].pages_printed, 888)

print("\n--- 5. v8: serial primeiro, conflito de SNMP, mes nao fechado, MAC, Total na coluna D ---")
with Session(engine) as s:
    # Equipamento que MUDOU de IP: o SNMP ja o conhece (serial) no IP novo.
    movida = Printer(server="x", name="Colorida_nova", ip="10.9.9.6", model="M", department="", active=True,
                     serial_number="V9Z5Y00033")
    # No IP antigo hoje ha outro equipamento, identificado pelo SNMP.
    outra = Printer(server="x", name="Etiqueta_no_ip_antigo", ip="10.9.9.254", model="M", department="", active=True,
                    serial_number="99001007")
    # IP cujo SNMP diz um serial que a planilha nao conhece em lugar nenhum.
    trocada = Printer(server="x", name="Trocada", ip="10.9.9.7", model="M", department="", active=True,
                      serial_number="AAA111")
    pantum = Printer(server="x", name="Pantum_VLO", ip="10.9.9.40", model="M", department="", active=True)
    for p in (movida, outra, trocada, pantum):
        s.add(p)
    s.commit()

    # Leitura com posicao de coluna: rotulo "Total" na coluna D, como na planilha real.
    linhas_v8 = [
        ["COLORIDAS"],
        ["IP", "Modelo", "Serial", "Departamento", "Janeiro", "Fevereiro", "Março"],
        ["10.9.9.254", "Kyocera M6530cdn", "V9Z5Y00033", "Logística Jundiaí", "10", "20", "0"],
        ["10.9.9.7", "Kyocera M2040", "ZZZ999", "Qualidade", "5", "5", "0"],
        ["10.9.9.40", "SP_BM5100ADW", "84:BA:3B:05:B7:FC", "Diretoria (P&B)", "7", "8", "0"],
        [None, None, None, "Total", "22", "33", "0"],
    ]
    itens, avisos_v8 = _parse_blocos(linhas_v8)
    check("Total na coluna D reconhecido (sem aviso de IP invalido)", [a for a in avisos_v8 if "None" in a], [])
    r = importar_para_banco(s, itens, ano=2026, aplicar=True)
    s.commit()

    check("so meses com dado na frota (Marco zerado fica de fora)", r["meses"], ["Janeiro", "Fevereiro"])
    check("casado pelo serial, no IP novo", len(r["casados_por_serial"]), 1)
    hist_movida = s.exec(select(PrinterMonthly).where(PrinterMonthly.printer_id == movida.id)).all()
    check("historico da colorida foi para o equipamento certo (IP novo)", len(hist_movida), 2)
    check("nada para quem esta no IP antigo", s.exec(select(PrinterMonthly).where(PrinterMonthly.printer_id == outra.id)).all(), [])
    check("conflito de SNMP nao importado", len(r["conflitos"]), 1)
    check("nada gravado na trocada", s.exec(select(PrinterMonthly).where(PrinterMonthly.printer_id == trocada.id)).all(), [])
    s.refresh(movida)
    s.refresh(pantum)
    check("departamento com unidade no equipamento movido", movida.department, "Logística Jundiaí — Coloridas (multi-site)")
    check("MAC nao vira serial", pantum.serial_number, None)
    check("MAC listado como ignorado", len(r["seriais_ignorados"]), 1)

print("\n--- 6. periodos da planilha e autocorrecao de historico em registro velho ---")
from import_historico_planilha import periodos_da_planilha  # noqa: E402

tabela = [
    [None, None, None, "Mês", "Período", "Impressões"],
    [None, None, None, "Agosto", "04/08/26 a 03/09/26", "183250"],
]
per = periodos_da_planilha(tabela, 2026)
check("agosto comeca 04/08", per["Agosto"][0], datetime(2026, 8, 4))
check("agosto termina (exclusivo) em 04/09", per["Agosto"][1], datetime(2026, 9, 4))

with Session(engine) as s:
    # Registro velho, INATIVO, no IP antigo: recebeu historico e serial numa
    # importacao anterior que casou pelo IP. Depois o SNMP leu o mesmo serial
    # no equipamento ativo, no IP novo.
    velho = Printer(server="", name="Velho_IP_antigo", ip="10.7.7.251", model="M", department="X", active=False,
                    serial_number="5875Z710245")
    novo = Printer(server="srv", name="Novo_IP_atual", ip="10.7.7.108", model="M", department="", active=True,
                   serial_number="5875Z710245", snmp_updated_at=datetime(2026, 9, 21))
    s.add(velho)
    s.add(novo)
    s.commit()
    s.add(PrinterMonthly(printer_id=velho.id, month="2026-08", pages_printed=500,
                          month_start=datetime(2026, 8, 1), month_end=datetime(2026, 9, 1)))
    s.commit()

    itens_v, _ = _parse_blocos([
        ["JUNDIAÍ - LOGÍSTICA"],
        ["IP", "Modelo", "Serial", "Departamento", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto"],
        ["10.7.7.251", "Ricoh P311", "5875Z710245", "Operação Solar", "0", "0", "0", "0", "0", "0", "0", "500"],
        ["Total:", "0", "0", "0", "0", "0", "0", "0", "500"],
    ])
    r6 = importar_para_banco(s, itens_v, ano=2026, aplicar=True, periodos=per)
    s.commit()
    s.refresh(velho)
    s.refresh(novo)
    ago_novo = s.exec(select(PrinterMonthly).where(PrinterMonthly.printer_id == novo.id)
                      .where(PrinterMonthly.month == "2026-08")).first()
    ago_velho = s.exec(select(PrinterMonthly).where(PrinterMonthly.printer_id == velho.id)
                       .where(PrinterMonthly.month == "2026-08")).first()

check("historico foi para o equipamento ativo (serial via SNMP)", ago_novo.pages_printed if ago_novo else None, 500)
check("fim do periodo = o da planilha (04/09)", ago_novo.month_end if ago_novo else None, datetime(2026, 9, 4))
check("historico saiu do registro velho", ago_velho, None)
check("serial duplicado saiu do registro velho inativo", velho.serial_number, None)
check("departamento foi para o equipamento ativo", novo.department, "Operação Solar — Jundiaí")
check("autocorrecao listada no relatorio", len(r6["realocados"]) >= 1, True)

print(f"\nBanco de teste: {DB}")
print("RESULTADO:", "TODOS OS TESTES PASSARAM" if not failures else f"FALHAS: {failures}")
raise SystemExit(1 if failures else 0)
