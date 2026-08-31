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
    resultado = importar_para_banco(s, impressoras, ano=2026, aplicar=False)
    check("1 impressora casada (so 10.1.1.1 e unica)", resultado["importados"], 1)
    check("1 IP nao encontrado (10.2.2.2)", len(resultado["nao_encontrados"]), 1)
    check("1 IP ambiguo (10.1.1.2, duas impressoras)", len(resultado["ambiguos"]), 1)
    check("simulacao nao grava nada no banco", s.exec(select(PrinterMonthly)).all(), [])

    resultado2 = importar_para_banco(s, impressoras, ano=2026, aplicar=True)
    s.commit()
    check("com --aplicar, grava de verdade", len(s.exec(select(PrinterMonthly)).all()), 2)
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

print(f"\nBanco de teste: {DB}")
print("RESULTADO:", "TODOS OS TESTES PASSARAM" if not failures else f"FALHAS: {failures}")
raise SystemExit(1 if failures else 0)
