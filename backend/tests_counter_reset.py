"""
Fase 17 - pages_from_readings() soma saltos positivos entre leituras
consecutivas, em vez de "maior contador menos o menor" (que superestimava
o total quando o contador reseta no meio do mes — troca de placa
formatadora, reset de fabrica).

Executar:  .\\venv\\Scripts\\python.exe tests_counter_reset.py
"""
import os
import tempfile
from datetime import datetime, timedelta

DB = os.path.join(tempfile.gettempdir(), "test_counter_reset.db")
if os.path.exists(DB):
    os.remove(DB)
os.environ["DATABASE_URL"] = f"sqlite:///{DB}"

from sqlmodel import Session  # noqa: E402

from app.database import create_db_and_tables, engine  # noqa: E402
from app.models.printer import Printer, PrinterReading  # noqa: E402
from app.services.monthly_report import month_bounds, pages_from_readings  # noqa: E402

failures = []


def check(label, got, expected):
    ok = got == expected
    print(f"[{'OK ' if ok else 'FAIL'}] {label}: {got}" + ("" if ok else f" (esperado {expected})"))
    if not ok:
        failures.append(label)


create_db_and_tables()

MES = datetime(2026, 5, 1)
mes_ini, mes_fim = month_bounds(MES)


def gravar(session, printer_id, contadores):
    """Uma leitura por valor, em ordem, minutos entre elas."""
    for i, valor in enumerate(contadores):
        session.add(PrinterReading(
            printer_id=printer_id, status="online", page_count=valor,
            timestamp=MES + timedelta(hours=i),
        ))
    session.commit()


with Session(engine) as s:
    p_normal = Printer(server="x", name="Normal", ip="10.7.1.1", model="M", department="TI", active=True)
    p_reset = Printer(server="x", name="ComReset", ip="10.7.1.2", model="M", department="TI", active=True)
    p_unica = Printer(server="x", name="UmaLeituraSo", ip="10.7.1.3", model="M", department="TI", active=True)
    p_reset_no_fim = Printer(server="x", name="ResetNoFim", ip="10.7.1.4", model="M", department="TI", active=True)
    s.add(p_normal)
    s.add(p_reset)
    s.add(p_unica)
    s.add(p_reset_no_fim)
    s.commit()
    s.refresh(p_normal)
    s.refresh(p_reset)
    s.refresh(p_unica)
    s.refresh(p_reset_no_fim)

    print("--- 1. contador so cresce: mesmo resultado de sempre (maior-menor) ---")
    gravar(s, p_normal.id, [40000, 40100, 40250, 40500])
    resultado = pages_from_readings(s, mes_ini, mes_fim)
    check("500 paginas (40500-40000, igual ao calculo antigo)", resultado[p_normal.id], 500)

    print("\n--- 2. reset no meio do mes: soma saltos positivos, NAO maior-menos-menor ---")
    # 40000 -> 40500 (+500) -> 100 (RESET, ignorado) -> 300 (+200). Total real: 700.
    # Formula antiga (maior-menor) daria 40500-100=40400 — 57x maior que o real.
    gravar(s, p_reset.id, [40000, 40500, 100, 300])
    resultado = pages_from_readings(s, mes_ini, mes_fim)
    check("700 paginas (500 antes do reset + 200 depois)", resultado[p_reset.id], 700)
    check("NAO e o resultado errado do calculo antigo (40400)", resultado[p_reset.id] != 40400, True)

    print("\n--- 3. impressora com uma unica leitura no mes: fica em 0 (sem salto pra medir) ---")
    gravar(s, p_unica.id, [12345])
    resultado = pages_from_readings(s, mes_ini, mes_fim)
    check("0 paginas (nao ha segunda leitura pra comparar)", resultado[p_unica.id], 0)

    print("\n--- 4. reset bem no fim do mes: ainda soma certo o que veio antes ---")
    gravar(s, p_reset_no_fim.id, [5000, 5200, 5400, 10])
    resultado = pages_from_readings(s, mes_ini, mes_fim)
    check("400 paginas (200+200 antes do reset, o salto pra 10 e ignorado)", resultado[p_reset_no_fim.id], 400)

print(f"\nBanco de teste: {DB}")
print("RESULTADO:", "TODOS OS TESTES PASSARAM" if not failures else f"FALHAS: {failures}")
raise SystemExit(1 if failures else 0)
