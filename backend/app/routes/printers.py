from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.dependencies import require_admin, require_operator, require_user
from app.models.user import User
from datetime import datetime

from app.models.printer import Printer, PrinterReading
from app.schemas.printer import (
    PrinterCreate,
    PrinterUpdate,
    PrinterResponse,
    PrinterReadingCreate,
    PrinterWithStatus,
    TonerLevel,
)
from typing import List

# Fase 2: TODA rota de impressoras exige sessao. A dependencia fica no
# router para que nenhuma rota nova nasca publica por esquecimento; as rotas
# de escrita continuam declarando o papel exigido (require_admin/operator),
# que roda alem desta.
router = APIRouter(
    prefix="/printers",
    tags=["printers"],
    dependencies=[Depends(require_user)],
)


@router.get("", response_model=List[PrinterResponse])
def list_printers(session: Session = Depends(get_session)):
    printers = session.exec(select(Printer)).all()
    return printers


TONER_LABELS = {"K": "Preto", "C": "Ciano", "M": "Magenta", "Y": "Amarelo"}

MONTH_LABELS = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]


# Precisa vir antes de /{printer_id}, senao "with-status" e lido como id.
@router.get("/with-status", response_model=List[PrinterWithStatus])
def list_printers_with_status(session: Session = Depends(get_session)):
    """
    Impressoras + ultima leitura de cada uma, em uma unica chamada.

    E o que o painel consome: sem isto o frontend precisaria de 1 request
    por impressora. Sem leitura registrada, a impressora vem como "offline"
    com last_seen nulo.
    """
    printers = session.exec(select(Printer)).all()

    # Ultima leitura por impressora (id maior = mais recente).
    latest: dict[int, PrinterReading] = {}
    for reading in session.exec(select(PrinterReading).order_by(PrinterReading.id.desc())):
        latest.setdefault(reading.printer_id, reading)

    result = []
    for printer in printers:
        reading = latest.get(printer.id)
        toner = None
        if reading:
            levels = [
                TonerLevel(color=color, label=TONER_LABELS[color], percent=value)
                for color, value in (
                    ("K", reading.toner_k),
                    ("C", reading.toner_c),
                    ("M", reading.toner_m),
                    ("Y", reading.toner_y),
                )
                if value is not None
            ]
            toner = levels or None

        result.append(
            PrinterWithStatus(
                **PrinterResponse.model_validate(printer).model_dump(),
                status=reading.status if reading else "offline",
                page_count=reading.page_count if reading else 0,
                toner=toner,
                last_seen=reading.timestamp.isoformat() if reading else None,
                uptime=reading.uptime if reading else None,
            )
        )

    return result


@router.get("/monthly-report")
def monthly_report(session: Session = Depends(get_session)):
    """
    Contagem mensal por impressora, derivada de PrinterReading.

    Paginas do mes = maior contador do mes - menor contador do mes, ou seja o
    incremento REALMENTE observado nas leituras daquele mes. Nada e estimado:
    impressora com uma unica leitura no mes fica com 0, e mes sem leitura nao
    aparece. Sem leituras no banco, devolve listas vazias e o painel segue
    exibindo o relatorio de demonstracao (sinalizado no cabecalho).
    """
    readings = session.exec(
        select(PrinterReading).order_by(PrinterReading.timestamp)
    ).all()
    if not readings:
        return {"generated_at": datetime.utcnow().isoformat(), "monthly_usage": [], "printers": []}

    printers = {p.id: p for p in session.exec(select(Printer))}

    # (printer_id, period) -> [menor contador, maior contador]
    bounds: dict[tuple[int, str], list[int]] = {}
    for r in readings:
        # Leitura sem contador valido (impressora offline) nao entra na conta.
        if not r.page_count:
            continue
        key = (r.printer_id, r.timestamp.strftime("%Y-%m"))
        if key not in bounds:
            bounds[key] = [r.page_count, r.page_count]
        else:
            bounds[key][0] = min(bounds[key][0], r.page_count)
            bounds[key][1] = max(bounds[key][1], r.page_count)

    per_printer: dict[int, list[dict]] = {}
    per_month: dict[str, int] = {}
    for (printer_id, period), (lowest, highest) in sorted(bounds.items(), key=lambda kv: kv[0][1]):
        pages = highest - lowest
        per_printer.setdefault(printer_id, []).append(
            {"month": MONTH_LABELS[int(period[5:]) - 1], "pages": pages, "period": period}
        )
        per_month[period] = per_month.get(period, 0) + pages

    month_label = {m["period"]: m["month"] for months in per_printer.values() for m in months}

    return {
        "generated_at": datetime.utcnow().isoformat(),
        "monthly_usage": [
            {"month": month_label.get(period, period), "pages": pages, "period": period}
            for period, pages in sorted(per_month.items())
        ],
        "printers": [
            {
                "ip": printers[pid].ip,
                "name": printers[pid].name,
                "department": printers[pid].department,
                "monthly_pages": months,
            }
            for pid, months in per_printer.items()
            if pid in printers
        ],
    }


@router.get("/{printer_id}", response_model=PrinterResponse)
def get_printer(printer_id: int, session: Session = Depends(get_session)):
    printer = session.get(Printer, printer_id)
    if not printer:
        raise HTTPException(status_code=404, detail="Impressora não encontrada")
    return printer


@router.post("", response_model=PrinterResponse)
def create_printer(
    printer_data: PrinterCreate,
    session: Session = Depends(get_session),
    _user: User = Depends(require_admin),
):
    # Etapa 4: identidade e (server, name) — IP pode repetir (varias
    # impressoras no mesmo Print Server compartilham porta/endereco).
    server = printer_data.server or ""
    existing = session.exec(
        select(Printer).where(Printer.server == server, Printer.name == printer_data.name)
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Já existe uma impressora '{printer_data.name}' no servidor '{server or '(nenhum)'}'.",
        )

    printer = Printer(**printer_data.model_dump(exclude={"server"}), server=server)
    session.add(printer)
    session.commit()
    session.refresh(printer)
    return printer


@router.patch("/{printer_id}", response_model=PrinterResponse)
def update_printer(
    printer_id: int,
    printer_data: PrinterUpdate,
    session: Session = Depends(get_session),
    _user: User = Depends(require_admin),
):
    printer = session.get(Printer, printer_id)
    if not printer:
        raise HTTPException(status_code=404, detail="Impressora não encontrada")

    update_data = printer_data.model_dump(exclude_unset=True)

    # Etapa 4: IP nao e mais identidade — so o par (server, name) precisa
    # continuar unico se o nome for alterado.
    novo_nome = update_data.get("name")
    if novo_nome and novo_nome != printer.name:
        em_uso = session.exec(
            select(Printer).where(Printer.server == printer.server, Printer.name == novo_nome)
        ).first()
        if em_uso:
            raise HTTPException(
                status_code=400,
                detail=f"Já existe uma impressora '{novo_nome}' no servidor '{printer.server or '(nenhum)'}'.",
            )

    for field, value in update_data.items():
        setattr(printer, field, value)
    printer.updated_at = datetime.utcnow()

    session.add(printer)
    session.commit()
    session.refresh(printer)
    return printer


@router.get("/{printer_id}/readings")
def get_printer_readings(printer_id: int, limit: int = 100, session: Session = Depends(get_session)):
    readings = session.exec(
        select(PrinterReading)
        .where(PrinterReading.printer_id == printer_id)
        .order_by(PrinterReading.timestamp.desc())
        .limit(limit)
    ).all()
    return readings


@router.post("/{printer_id}/readings")
def create_printer_reading(
    printer_id: int,
    reading_data: PrinterReadingCreate,
    session: Session = Depends(get_session),
    _user: User = Depends(require_operator),
):
    printer = session.get(Printer, printer_id)
    if not printer:
        raise HTTPException(status_code=404, detail="Impressora não encontrada")

    reading = PrinterReading(
        printer_id=printer_id,
        status=reading_data.status,
        page_count=reading_data.page_count,
        toner_k=reading_data.toner_k,
        toner_c=reading_data.toner_c,
        toner_m=reading_data.toner_m,
        toner_y=reading_data.toner_y,
        uptime=reading_data.uptime,
    )
    session.add(reading)
    session.commit()
    session.refresh(reading)
    return reading
