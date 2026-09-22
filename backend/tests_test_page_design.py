r"""
Pagina de teste moderna x classica, mono x colorida (22/09/2026).

Sem rede: so monta os documentos e confere os comandos PCL.

    .\venv\Scripts\python.exe tests_test_page_design.py
"""
import os
from datetime import datetime
from unittest.mock import patch

os.environ.setdefault("ENVIRONMENT", "development")

from app.config import settings  # noqa: E402
from app.models.printer import Printer, PrinterReading  # noqa: E402
from app.routes.printers import _e_colorida  # noqa: E402
from app.services import test_page_logo  # noqa: E402
from app.services.test_print import TestPageInfo, build_test_page  # noqa: E402

failures = []


def check(label, got, expected):
    ok = got == expected
    print(f"[{'OK ' if ok else 'FAIL'}] {label}: {got!r}" + ("" if ok else f" (esperado {expected!r})"))
    if not ok:
        failures.append(label)


base = dict(
    printer_name="FILA_TESTE", ip="10.0.0.9", requested_by="Fulano (f@x.test)", model="ECOSYS M6530cdn",
    serial="VCF1", department="Fiscal — Jundiaí", server="srv", share_name="FILA_TESTE", driver="KX",
    status="online", page_count=167673, last_reading=datetime(2026, 9, 22, 11, 0, 5),
    monthly=[("Ago/26", 5642, 0, False), ("Set/26", 2381, 320, True)], when=datetime(2026, 9, 22, 11, 0),
)

print("--- 1. logo ---")
linhas = test_page_logo.linhas()
check("altura do bitmap", len(linhas), test_page_logo.ALTURA)
check("bytes por linha", {len(l) for l in linhas}, {test_page_logo.BYTES_POR_LINHA})
check("logo tem tinta", sum(bin(b).count("1") for l in linhas for b in l) > 10000, True)

print("\n--- 2. moderna colorida ---")
cor = build_test_page(TestPageInfo(**base, toner=[("Ciano", 77), ("Magenta", 41), ("Amarelo", 8), ("Preto", 26)],
                                   colorida=True), estilo="moderna")
check("configura paleta PCL5c (ESC*v6W, 4 bits)", b"\x1b*v6W\x00\x00\x04\x08\x08\x08" in cor, True)
check("azul Elgin na paleta (0,159,255 no indice 1)", b"\x1b*v0a159b255c1I" in cor, True)
check("logo em 4 planos (3x V + 1x W por linha)", cor.count(b"\x1b*b75V") >= 3 * test_page_logo.ALTURA, True)
check("sem teste de cores (economia de toner)", b"TESTE DE CORES" in cor, False)
check("so cores de toner selecionadas para texto/retangulo (7, 8, 9) e preto (2)",
      set(__import__("re").findall(rb"\*v(\d+)S", cor)) <= {b"2", b"7", b"8", b"9"}, True)
check("sem escala de cinza", b"ESCALA DE CINZA" in cor, False)
check("barras de toner nas cores", all(c.encode() in cor for c in ("Ciano", "Magenta", "Amarelo", "77%")), True)

print("\n--- 3. moderna mono ---")
mono = build_test_page(TestPageInfo(**base, toner=[("Preto", 36)]), estilo="moderna")
check("sem comandos de cor", b"\x1b*v" in mono, False)
check("logo em 1 plano", mono.count(b"\x1b*b75W"), test_page_logo.ALTURA)
check("teste de nitidez nas duas versoes", (b"TESTE DE NITIDEZ" in mono, b"TESTE DE NITIDEZ" in cor), (True, True))
sem_toner = build_test_page(TestPageInfo(**base, toner=None, toner_note="A impressora não identifica o cartucho (não original ou sem chip) e não informa o nível."), estilo="moderna")
check("explica toner nao informado (quebra por palavra)", "não original ou sem".encode("latin-1") in sem_toner or "identifica o cartucho".encode("latin-1") in sem_toner, True)

print("\n--- 4. classica continua de reserva ---")
classica = build_test_page(TestPageInfo(**base, toner=[("Preto", 36)]), estilo="classica")
check("classica tem escala de cinza e nao tem logo", (b"ESCALA DE CINZA" in classica, b"\x1b*r600S" in classica), (True, False))
with patch.object(settings, "test_page_style", "classica"):
    check("TEST_PAGE_STYLE=classica escolhe a classica", b"ESCALA DE CINZA" in build_test_page(TestPageInfo(**base)), True)
with patch.object(settings, "test_page_style", "moderna"):
    check("TEST_PAGE_STYLE=moderna escolhe a moderna", b"\x1b*r600S" in build_test_page(TestPageInfo(**base)), True)

print("\n--- 5. quem e colorida ---")
leitura_cor = PrinterReading(printer_id=1, status="online", toner_k=20, toner_c=50)
leitura_mono = PrinterReading(printer_id=1, status="online", toner_k=20)
check("leitura com ciano", _e_colorida(Printer(server="s", name="a", ip="1", model="X"), leitura_cor), True)
for modelo, esperado in [("ECOSYS M6530cdn", True), ("RICOH IM C3000", True), ("HP Color LaserJet Pro", True),
                         ("ECOSYS P3055dn", False), ("RICOH P 311", False), ("ECOSYS M3040idn", False)]:
    check(f"modelo {modelo}", _e_colorida(Printer(server="s", name="a", ip="1", model=modelo), leitura_mono), esperado)

print()
if failures:
    print(f"FALHOU: {failures}")
    raise SystemExit(1)
print("Todos os testes da pagina de teste moderna passaram.")
