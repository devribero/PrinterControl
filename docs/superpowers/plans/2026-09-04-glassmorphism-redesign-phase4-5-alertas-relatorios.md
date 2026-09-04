# Glassmorphism Redesign — Phases 4 & 5 (Alertas, Relatórios)

**Spec:** `design_handoff_printercontrol/PrinterControl v2.dc.html` — Alertas L560-583, Relatórios L586-666; page-header copy at L1131-1132.

**Global constraints:** unchanged from Phases 0-3 (token-only colors, glass recipe, `--glass-hover` inside glass surfaces, mono numerics, 0.12s color/border transitions, no business-logic changes).

---

## Phase 4 — Alertas

- `src/app/alerts/page.tsx`: `PageHeader` ("Monitoramento" / "Alertas" / "Eventos técnicos derivados das leituras — toner baixo e equipamentos fora do ar.").
- `AlertsView`: internal title/subtitle removed (now the page header). Header becomes severity tabs `Todos / Crítico / Atenção` with mono counts, each tinted with its own semantics (`--tint-link`, `--danger-bg`, `--tint-warning`), plus the note "Derivados automaticamente das leituras da frota".
- List: 2px left rail per row (`--danger` / `--warning`) replaces the round icon chip; single-line message, timestamp, and an uppercase severity badge on the right.
- Empty states preserved (both "no alerts at all" and "none in this category").

## Phase 5 — Relatórios

- `src/app/reports/page.tsx`: `PageHeader` ("Monitoramento" / "Relatórios" / "Contadores mensais, ranking de uso e consumo por departamento.") with the CSV export in `actions`. Layout becomes strip → `minmax(0,1fr) 300px` grid (departments dominant + rankings sidebar, single column under 1024px) → inactive-printers table.
- `MonthlyCounters`: card + inner card grid → one glass strip, months side by side, current month tinted `--tint-link`, values mono with the delta inline.
- `DepartmentBreakdown`: header simplified to title + "Todas as unidades"; rows become `name (12rem) | 4px bar | mono total (5.5rem) | mono pct (2.5rem) | chevron`. The month-by-month expansion is app functionality absent from the handoff and is kept.
- `PrinterRanking`: two cards → two card-less sections in the sidebar; header is icon + title over a divider, items are `N. Name` + mono total + 2px bar.
- `DecommissionedList`: glass card, mono count in the header, four columns with mono IP/date, plus an empty-row state the old version lacked.

### Deliberate deviation

The old Relatórios summary block (TOTAL / ONLINE / OFFLINE / ATENÇÃO cards + "Relatório de Impressoras" title) is **dropped**: the handoff's Relatórios screen has no such block, and those four numbers are exactly what the Dashboard's `VitalsStrip` already shows. The CSV export that lived next to it is preserved, moved into the page header's actions slot. Flagged for review — if the numbers are wanted on this screen, the strip can come back above the month row.

---

## Roadmap

Phase 6 — Histórico (handoff L668+): page-header total, totals table, then per-site accordion. Then Rede, Notificações, Integrações, Usuários, Configurações.
