r"""
Contadores separados e reparo das leituras antigas (23/09/2026).

Caso real: FS-4200DN 10.22.0.136 alternava entre o contador do fabricante
(911,8 mil) e o padrao (900,7 mil); o relatorio de setembro deu 33.578
paginas para um equipamento que imprime ~300 por mes.

  1. paginas_entre compara sempre o mesmo contador; mistura = 0;
  2. trava de plausibilidade descarta salto impossivel;
  3. month_pages com leituras novas (dois contadores) nao conta as trocas;
  4. reparo das leituras antigas separa as duas series e o mes volta ao real;
  5. equipamento sem contador do fabricante: tudo vira padrao;
  6. Kyocera recente sem referencia fica para depois.

    .\venv\Scripts\python.exe tests_counter_series.py
"""
import os
import tempfile
from datetime import datetime, timedelta

DB = os.path.join(tempfile.gettempdir(), "test_counter_series.db")
if os.path.exists(DB):
    os.remove(DB)
os.environ["DATABASE_URL"] = f"sqlite:///{DB}"
os.environ["ENVIRONMENT"] = "development"

from sqlmodel import Session, select  # noqa: E402

from app.database import create_db_and_tables, engine  # noqa: E402
from app.models.printer import Printer, PrinterReading  # noqa: E402
from app.services.counter_repair import reparar_leituras  # noqa: E402
from app.services.counter_series import paginas_entre  # noqa: E402
from app.services.monthly_report import month_pages  # noqa: E402

failures = []


def check(label, got, expected):
    ok = got == expected
    print(f"[{'OK ' if ok else 'FAIL'}] {label}: {got!r}" + ("" if ok else f" (esperado {expected!r})"))
    if not ok:
        failures.append(label)


T0 = datetime(2026, 9, 11, 13, 0)
MES = (datetime(2026, 9, 1), datetime(2026, 10, 1))

print("--- 1/2. paginas_entre ---")
check("fabricante com fabricante", paginas_entre((1000, 1100), (1010, 1111), T0, T0 + timedelta(hours=1)), 10)
check("padrao quando so ele existe nas duas", paginas_entre((None, 1100), (1020, 1120), T0, T0 + timedelta(hours=1)), 20)
check("mistura nao conta", paginas_entre((911829, None), (None, 900741), T0, T0 + timedelta(hours=1)), 0)
check("salto impossivel descartado (11 mil em 15 min)",
      paginas_entre((None, 900741), (None, 911836), T0, T0 + timedelta(minutes=15)), 0)
check("salto grande em 11 dias aceito", paginas_entre((None, 900560), (None, 911829), T0, T0 + timedelta(days=11)), 11269)

create_db_and_tables()


def impressora(s, nome, ip, modelo):
    p = Printer(server="srv", name=nome, ip=ip, model=modelo, active=True)
    s.add(p)
    s.commit()
    s.refresh(p)
    return p.id


with Session(engine) as s:
    print("\n--- 3. leituras novas com os dois contadores ---")
    ky = impressora(s, "FS4200", "10.9.0.136", "Kyocera FS-4200DN")
    pontos = [(911800, 900700), (None, 900705), (911810, 900712), (911816, 900718)]
    for i, (v, p) in enumerate(pontos):
        s.add(PrinterReading(printer_id=ky, status="online", page_count=v or 0, counter_vendor=v, counter_std=p,
                             timestamp=T0 + timedelta(hours=i)))
    s.commit()
    mes = month_pages(s, *MES)
    check("16 paginas (fabricante 911800 -> 911816), sem pular", mes.pages.get(ky), 16)

    print("\n--- 4. reparo das leituras antigas (caso real) ---")
    ky2 = impressora(s, "FS4200_legado", "10.9.1.136", "Kyocera FS-4200DN")
    # Padrao antes de 22/09, depois alternando com o do fabricante.
    legado = [
        (900560, T0), (900600, T0 + timedelta(days=1)),
        (911829, T0 + timedelta(days=11)), (911835, T0 + timedelta(days=11, hours=1)),
        (900741, T0 + timedelta(days=11, hours=6)), (911836, T0 + timedelta(days=11, hours=6, minutes=15)),
        (900755, T0 + timedelta(days=12)),
    ]
    for valor, ts in legado:
        s.add(PrinterReading(printer_id=ky2, status="online", page_count=valor, timestamp=ts))
    s.commit()
    antes = month_pages(s, *MES).pages.get(ky2, 0)
    check("antes do reparo o mes estava inflado (> 11 mil)", antes > 11000, True)
    r = reparar_leituras(s, referencias={"10.9.1.136": (911840, 900760)}, agora=T0 + timedelta(days=12, hours=1))
    check("classificadas: 4 padrao, 3 fabricante", (r["padrao"], r["fabricante"]), (4, 3))
    mes2 = month_pages(s, *MES)
    depois = mes2.pages.get(ky2, 0) - mes2.estimated.get(ky2, 0)  # so o medido
    # O padrao sozinho diz 900560 -> 900755 = 195 paginas no periodo. Com o
    # fabricante valendo so no trecho em que foi lido, o total fica ~195, sem
    # nenhum dos saltos de ~11 mil das trocas.
    check("depois do reparo: ~195 paginas, sem o salto da troca", 185 <= depois <= 205, True)

    print("\n--- 5. sem contador do fabricante: tudo padrao ---")
    ri = impressora(s, "RICOH", "10.9.2.1", "RICOH M 320F")
    for i, valor in enumerate((5000, 5010, 5030)):
        s.add(PrinterReading(printer_id=ri, status="online", page_count=valor, timestamp=T0 + timedelta(days=i)))
    s.commit()
    reparar_leituras(s, agora=T0 + timedelta(days=3))
    ult = s.exec(select(PrinterReading).where(PrinterReading.printer_id == ri)).all()
    check("todas com counter_std", [x.counter_std for x in ult], [5000, 5010, 5030])
    mes3 = month_pages(s, *MES)
    check("mes da Ricoh (medido)", mes3.pages.get(ri) - mes3.estimated.get(ri, 0), 30)

    print("\n--- 6. Kyocera recente sem referencia: adiada ---")
    ky3 = impressora(s, "M2040_novo", "10.9.3.1", "ECOSYS M2040dn")
    s.add(PrinterReading(printer_id=ky3, status="online", page_count=344133, timestamp=T0 + timedelta(days=11)))
    s.commit()
    r = reparar_leituras(s, agora=T0 + timedelta(days=11, hours=2))
    check("adiada ate ter leitura com os dois contadores", r["adiadas"], 1)
    check("leitura continua sem classificar",
          s.exec(select(PrinterReading).where(PrinterReading.printer_id == ky3)).first().counter_std, None)

print()
if failures:
    print(f"FALHOU: {failures}")
    raise SystemExit(1)
print("Todos os testes de contadores separados passaram.")
