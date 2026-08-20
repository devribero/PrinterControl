"""
Etapa 11 - coleta simulada da frota inteira, ponta a ponta.

Copia o banco real para um temporario e roda duas coletas completas nele, de
modo que o banco de trabalho nao seja alterado pelo teste.

Executar:  .\\venv\\Scripts\\python.exe tests_fleet.py
"""
import os
import shutil
import tempfile

SOURCE_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "printer_control.db")
TEST_DB = os.path.join(tempfile.gettempdir(), "test_fleet.db")

if os.path.exists(TEST_DB):
    os.remove(TEST_DB)
shutil.copyfile(SOURCE_DB, TEST_DB)
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.replace(os.sep, '/')}"

from sqlmodel import Session, create_engine, func, select  # noqa: E402

from app.database import create_db_and_tables  # noqa: E402
from app.models.alert import Alert  # noqa: E402
from app.models.printer import Printer, PrinterReading  # noqa: E402
from app.services.printer_collector import PrinterCollector  # noqa: E402
from app.services.snmp_fleet_mock import profile_for  # noqa: E402

# Aplica migracoes aditivas (ex.: printer_readings.uptime, Etapa 7) na copia
# antes de usa-la — o copyfile traz o schema exato do arquivo original, que
# pode ser anterior a uma migracao aditiva ainda nao rodada nele.
create_db_and_tables()

engine = create_engine(f"sqlite:///{TEST_DB.replace(os.sep, '/')}", connect_args={"check_same_thread": False})

failures = []


def check(label, got, expected):
    ok = got == expected
    print(f"[{'OK ' if ok else 'FAIL'}] {label}: {got}" + ("" if ok else f" (esperado {expected})"))
    if not ok:
        failures.append(label)


def check_true(label, condition, detail=""):
    print(f"[{'OK ' if condition else 'FAIL'}] {label}" + (f": {detail}" if detail else ""))
    if not condition:
        failures.append(label)


def collect_fleet(session) -> dict:
    """Uma coleta completa. Devolve resumo por status."""
    collector = PrinterCollector(mode="fleet")
    ids = session.exec(select(Printer.id)).all()
    summary = {"ok": 0, "fail": 0, "status": {}}
    for pid in ids:
        r = collector.collect_and_save(pid, session)
        if r["success"]:
            summary["ok"] += 1
            summary["status"][r["status"]] = summary["status"].get(r["status"], 0) + 1
        else:
            summary["fail"] += 1
    return summary


with Session(engine) as s:
    total_printers = s.exec(select(func.count()).select_from(Printer)).one()
    readings_before = s.exec(select(func.count()).select_from(PrinterReading)).one()

    print("--- 1. frota cadastrada ---")
    check("impressoras no banco", total_printers, 73)

    print("\n--- 2. primeira coleta completa ---")
    first = collect_fleet(s)
    check("coletadas com sucesso", first["ok"], 73)
    check("falhas", first["fail"], 0)
    print("     por status:", first["status"])

    readings_after_1 = s.exec(select(func.count()).select_from(PrinterReading)).one()
    check("uma leitura nova por impressora", readings_after_1 - readings_before, 73)

    print("\n--- 3. nenhuma impressora perdida ---")
    covered = s.exec(
        select(func.count(func.distinct(PrinterReading.printer_id)))
        .where(PrinterReading.id > readings_before)
    ).one()
    check("impressoras distintas na coleta", covered, 73)

    print("\n--- 4. persistencia (status, contador, toner) ---")
    online_ids = [p for p in s.exec(select(Printer.id)) if profile_for(p) == "online"]
    sample = s.exec(
        select(PrinterReading)
        .where(PrinterReading.printer_id == online_ids[0])
        .order_by(PrinterReading.id.desc())
    ).first()
    check("status persistido", sample.status, "online")
    check_true("page_count persistido", sample.page_count > 0, str(sample.page_count))
    check_true("toner K persistido", sample.toner_k is not None, str(sample.toner_k))

    offline_id = next(p for p in s.exec(select(Printer.id)) if profile_for(p) == "offline")
    off = s.exec(
        select(PrinterReading).where(PrinterReading.printer_id == offline_id).order_by(PrinterReading.id.desc())
    ).first()
    check("impressora offline persistida como offline", off.status, "offline")

    print("\n--- 5. alertas apos a primeira coleta ---")
    active_alerts = s.exec(select(Alert).where(Alert.resolved_at == None)).all()  # noqa: E711
    offline_alerts = [a for a in active_alerts if a.alert_type == "offline"]
    critical = [a for a in active_alerts if a.alert_type.startswith("toner") and a.severity == "critical"]
    warning = [a for a in active_alerts if a.alert_type.startswith("toner") and a.severity == "warning"]
    print(f"     ativos={len(active_alerts)} offline={len(offline_alerts)} critical={len(critical)} warning={len(warning)}")
    check_true("gerou alertas de offline", len(offline_alerts) > 0)
    check_true("gerou alertas de toner critico", len(critical) > 0)
    check_true("gerou alertas de toner baixo", len(warning) > 0)

    offline_with_toner = [
        a for a in active_alerts
        if a.alert_type.startswith("toner") and profile_for(a.printer_id) == "offline"
    ]
    check("offline nao gera falso alerta de toner", len(offline_with_toner), 0)

    print("\n--- 6. segunda coleta: contador cresce, alertas nao duplicam ---")
    before_counts = {
        pid: s.exec(
            select(PrinterReading.page_count)
            .where(PrinterReading.printer_id == pid)
            .order_by(PrinterReading.id.desc())
        ).first()
        for pid in online_ids
    }

    second = collect_fleet(s)
    check("coletadas na segunda rodada", second["ok"], 73)

    readings_after_2 = s.exec(select(func.count()).select_from(PrinterReading)).one()
    check("mais 73 leituras", readings_after_2 - readings_after_1, 73)

    decreased = []
    grew = 0
    for pid, before in before_counts.items():
        after = s.exec(
            select(PrinterReading.page_count)
            .where(PrinterReading.printer_id == pid)
            .order_by(PrinterReading.id.desc())
        ).first()
        if after < before:
            decreased.append((pid, before, after))
        elif after > before:
            grew += 1
    check("nenhum contador diminuiu", len(decreased), 0)
    check("todos os contadores cresceram", grew, len(before_counts))

    active_after = s.exec(select(Alert).where(Alert.resolved_at == None)).all()  # noqa: E711
    check("alertas ativos nao duplicaram", len(active_after), len(active_alerts))

    pairs = [(a.printer_id, a.alert_type) for a in active_after]
    check("um alerta ativo por (impressora, condicao)", len(pairs), len(set(pairs)))

    print("\n--- 7. relatorio mensal consistente ---")
    readings = s.exec(select(PrinterReading)).all()
    bounds = {}
    for r in readings:
        if not r.page_count:
            continue
        key = (r.printer_id, r.timestamp.strftime("%Y-%m"))
        lo, hi = bounds.get(key, (r.page_count, r.page_count))
        bounds[key] = (min(lo, r.page_count), max(hi, r.page_count))
    negatives = [k for k, (lo, hi) in bounds.items() if hi - lo < 0]
    check("nenhuma diferenca negativa no mes", len(negatives), 0)
    total_pages = sum(hi - lo for lo, hi in bounds.values())
    check_true("total de paginas do mes e plausivel", total_pages >= 0, str(total_pages))

print(f"\nBanco de teste: {TEST_DB}")
print("RESULTADO:", "TODOS OS TESTES PASSARAM" if not failures else f"FALHAS: {failures}")
raise SystemExit(1 if failures else 0)
