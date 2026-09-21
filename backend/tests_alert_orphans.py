r"""
Alertas de impressoras desativadas (21/09/2026).

O alerta so e reavaliado quando chega leitura nova, e impressora desativada
nao e mais coletada — entao o "offline" aberto no dia em que ela sumiu do
Print Server ficava aberto para sempre. Cobre os dois lados da correcao:

  1. o sync fecha os alertas das impressoras que ele desativa, na mesma
     transacao, e nao toca nos das que continuam ativas;
  2. `resolve_orphan_alerts` (roda na subida do backend) limpa os orfaos
     que ficaram de antes, e e idempotente.

Executar:  .\venv\Scripts\python.exe tests_alert_orphans.py
"""
import os
import tempfile

DB = os.path.join(tempfile.gettempdir(), "test_alert_orphans.db")
if os.path.exists(DB):
    os.remove(DB)
os.environ["DATABASE_URL"] = f"sqlite:///{DB}"

from datetime import datetime  # noqa: E402
from unittest.mock import patch  # noqa: E402

from sqlmodel import Session, SQLModel, create_engine, select  # noqa: E402

from app.models.alert import Alert  # noqa: E402
from app.models.printer import Printer  # noqa: E402
from app.services import printer_sync  # noqa: E402
from app.services.alert_engine import resolve_orphan_alerts  # noqa: E402
from app.services.print_server import DiscoveredPrinter  # noqa: E402

engine = create_engine(f"sqlite:///{DB}", connect_args={"check_same_thread": False})
SQLModel.metadata.create_all(engine)

failures = []


def check(label, got, expected):
    ok = got == expected
    print(f"[{'OK ' if ok else 'FAIL'}] {label}: {got}" + ("" if ok else f" (esperado {expected})"))
    if not ok:
        failures.append(label)


def abertos(session, printer_id):
    return session.exec(
        select(Alert).where(Alert.printer_id == printer_id).where(Alert.resolved_at == None)  # noqa: E711
    ).all()


def fila(nome):
    return DiscoveredPrinter(name=nome, server="srv", port_name=f"IP_{nome}", ip="10.0.0.1", driver_name="drv")


with Session(engine) as s:
    # 5 impressoras ativas no servidor, cada uma com um alerta offline aberto.
    for i in range(1, 6):
        s.add(Printer(id=i, server="srv", name=f"P{i}", ip=f"10.0.0.{i}", model="M", printer_type="mono", active=True))
        s.add(Alert(printer_id=i, alert_type="offline", severity="critical", message="offline"))
    s.commit()

    # O Print Server passa a publicar so P1..P4: P5 sera desativada. (4 de 5 =
    # 20% de queda, exatamente no limite — nao bloqueia.)
    with patch.object(printer_sync, "discover_printers", return_value=[fila(f"P{i}") for i in range(1, 5)]):
        resultado = printer_sync.sync_printers(s, server="srv", mode="mock")

    check("sync desativou uma impressora", resultado.deactivated, 1)
    check("alerta da desativada foi resolvido", len(abertos(s, 5)), 0)
    check("alerta de impressora que continua ativa segue aberto", len(abertos(s, 1)), 1)

    # Orfao de antes da correcao: impressora ja inativa com alerta aberto.
    s.add(Printer(id=6, server="srv", name="P6", ip="10.0.0.6", model="M", printer_type="mono", active=False))
    s.add(Alert(printer_id=6, alert_type="toner:K", severity="critical", message="toner"))
    s.commit()

    check("limpeza da subida fecha o orfao", resolve_orphan_alerts(s), 1)
    check("orfao sem alerta aberto", len(abertos(s, 6)), 0)
    check("limpeza e idempotente", resolve_orphan_alerts(s), 0)
    check("ativas nao sao tocadas pela limpeza", len(abertos(s, 2)), 1)

    resolvido = s.exec(select(Alert).where(Alert.printer_id == 6)).first()
    check("resolved_at preenchido", isinstance(resolvido.resolved_at, datetime), True)

print()
if failures:
    print(f"FALHOU: {len(failures)} verificacao(oes): {failures}")
    raise SystemExit(1)
print("Todos os testes de alertas orfaos passaram.")
