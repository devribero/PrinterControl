# Glassmorphism Redesign — Phase 2 (Impressoras) Implementation Plan

**Goal:** Bring the Impressoras screen (`/printers`) to the handoff design: page header, status tabs, compact search, segmented list/grid toggle, and the handoff's table row anatomy (mono IP, toner mini-bar, tighter density). The same `PrinterTable` is embedded in the Dashboard in `compact` mode, so the shared row/pagination anatomy is fixed here for both — the handoff uses the identical row markup on both screens (`PrinterControl v2.dc.html` L249-278 dashboard, L427-457 printers).

**Spec:** `design_handoff_printercontrol/PrinterControl v2.dc.html` L220-300 (dashboard fleet table) and L392-479 (Impressoras screen); README L105 ("filterable/searchable fleet table with status tabs"), L1129 (page header copy).

## Global Constraints (unchanged from Phases 0/1)

- No hardcoded hex in components — always a CSS var token.
- Glass card recipe for the table container is already in place (Phase 1 Task 4) — don't re-invent it.
- Any `:hover` inside the glass container uses `--glass-hover`, never an opaque token.
- All numerics (IP, counts, percentages, page numbers) in `var(--font-mono)`.
- Transitions: `background-color 0.12s ease-out` (or `border-color`/`color` alongside) only.
- Business logic untouched — filters, pagination state, toasts, `useAppData` all keep their current behavior.

## Deliberate deviations from the handoff (documented, not silent)

1. **"Tipo" filter kept.** The handoff has no printer-type filter; the app has one (`lib/printerType`) and it is real functionality. Status moves out of the filters panel into the tabs; the `Filtros` button stays and now carries only Tipo.
2. **Grid view kept.** The handoff only mocks the list view, but the toggle exists in its header, and the app's grid view is working functionality. Kept, restyled with the same tokens.
3. **Printer icon chip dropped from the name cell.** The handoff's name cell is plain bold text; the chip belongs to the pre-redesign v1.
4. **Toner warning triangle dropped.** The handoff conveys severity through `tonerLevelColor` on the bar + percentage alone.

---

### Task 1: Wire `PageHeader` into `/printers`

- `src/app/printers/page.tsx`: wrap `PrinterTable` in a fragment under `<PageHeader section="Monitoramento" title="Impressoras" subtitle="Cadastro completo da frota monitorada, com status e nível de suprimento." />` (copy from handoff L1129).
- No `actions` slot — the screen's controls live in the table card header (handoff L393-407).
- Commit: `feat: wire PageHeader into Impressoras route`

### Task 2: Table card header — status tabs + compact controls

`PrinterTable.tsx` / `PrinterTable.module.css`.

- **Full (non-compact) header** (handoff L394-407): left = status tabs `Todas / Online / Offline / Atenção`, each `label + mono count`, active tab = `--tint-link` bg + `--link` fg (Todas) or its own semantic fg, hover `--divider`; right = compact search box (`--bg-page`, 6px radius, placeholder "Nome, IP ou modelo", 11rem) + `Filtros` button + joined segmented list/grid toggle (6px radius, 1px `--border`, divider between, active = `--divider` bg + `--text-primary`).
- **Compact header** (handoff L221-234): title `Frota de impressoras` + mono `N equipamentos`, then the same small search ("Buscar...", 7rem) and `Filtros` button; no tabs, no view toggle.
- Status counts derive from the *unfiltered* `printers` prop... note: the component only receives the filtered list plus `totalCount`. Add a `statusCounts` prop (`{ online, offline, atencao }`) supplied by the route from `useAppData().stats`, so tab counts don't collapse to the current filter.
- Clicking a tab calls `onFilterChange("status", value)` and resets `page` to 1.
- Filters panel keeps only the Tipo group.
- Commit: `feat: status tabs and compact controls in Impressoras table header`

### Task 3: Row anatomy per handoff

- Column headers: `Impressora | Endereço | Modelo | Departamento | Toner (right) | Status | Ações (right)`; compact drops Modelo and Ações.
- `.theadRow`: drop the `--divider` background, `font-size: 0.625rem`, `font-weight: 700`, `letter-spacing: 0.1em`, bottom border `--border`.
- Rows: `border-bottom: 1px solid var(--divider)` (not `border-top: --border`), cell padding `0.6875rem 1.25rem` / `0.6875rem 0.75rem`, table `font-size: 0.8125rem`.
- Name cell: plain `font-weight: 600; color: var(--text-primary)` — drop `.iconWrap`.
- IP cell: `var(--font-mono)`, `0.75rem`, `--text-secondary` (this closes Phase 1 Task 4's noted follow-up).
- Toner cell: right-aligned; `2.5rem × 3px` track (`--track`, radius 1px) filled to `percent` with `tonerLevelColor(percent)`, then a `min-width: 2.25rem` right-aligned mono percentage in the same color. No toner → mono `—` in `--text-muted`.
- Actions: 5px radius, `--text-muted`, hover `background: var(--track); color: var(--link)`.
- Commit: `feat: restyle Impressoras table rows to handoff anatomy`

### Task 4: Pagination per handoff

- Info line: `Exibindo <mono>A–B</mono> de <mono>N</mono>` in `--text-muted` with mono spans in `--text-secondary`.
- Arrows: `1.75rem` square, 5px radius, `--border`, disabled `opacity: 0.5`.
- Page numbers: `min-width 1.75rem`, height `1.75rem`, mono `0.75rem`, active = `--link` bg + `--bg-surface` fg, hover `--divider`.
- Page-size select: 5px radius, `--bg-surface`, `0.75rem`, label `N / página`.
- Commit: `feat: restyle Impressoras pagination to handoff spec`

### Task 5: Verify

- `npx tsc --noEmit` clean, `npm run build` green.
- Manual check both themes: `/printers` and `/` (compact table must not regress).

---

## Roadmap

Phase 3 — Toner: inline severity strip + full supply table with per-channel bars (handoff README L106).
