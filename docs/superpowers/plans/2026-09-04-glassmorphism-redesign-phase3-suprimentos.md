# Glassmorphism Redesign — Phase 3 (Suprimentos / Toner) Implementation Plan

**Goal:** Bring `/toner` to the handoff design: page header + inline severity strip ("Precisam de intervenção agora") + supply table with per-channel bars, replacing the old title card and 4-card summary grid.

**Spec:** `design_handoff_printercontrol/PrinterControl v2.dc.html` L482-553 (screen), L1130 (page-header copy: section "Monitoramento", title "Suprimentos", subtitle "Nível de toner de toda a frota, classificado por criticidade." — the Sidebar already labels this route "Suprimentos", so the breadcrumb matches).

**Global constraints:** unchanged from Phases 0-2 (token-only colors, glass recipe, `--glass-hover` inside glass, mono numerics, 0.12s color/border transitions, no business-logic changes).

---

### Task 1: Extract `ScanBar`

The "Última verificação · Verificar agora" control is now needed by two routes (Dashboard and Suprimentos), and the Dashboard's copy of it still carried legacy `--color-*` tokens in `app/page.module.css`.

- Create `src/components/ScanBar.tsx` + `ScanBar.module.css` — glass tokens, mono timestamp, optional `label` prop ("Verificar agora" on the Dashboard, "Atualizar agora" on Suprimentos).
- `src/app/page.tsx`: use it in `PageHeader`'s `actions`; drop the inline block and the `RefreshCw` import.
- `src/app/page.module.css`: delete the now-dead `.scanBar`/`.scanBarStrong`/`.scanButton` rules and migrate the two remaining legacy tokens in the skeleton rules (`--color-border` → `--border`, `--color-surface-2` → `--bg-surface`). This closes the leftover flagged after Phase 1.

### Task 2: Page header on `/toner`

- `src/app/toner/page.tsx`: wrap `TonerMonitoring` in `PageHeader` (copy above) with `ScanBar` in `actions`.
- `TonerMonitoring` loses its `lastChecked`/`onRefresh`/`refreshing` props — the control moved to the header, so the component no longer owns it.

### Task 3: Severity strip replaces the summary grid

- Single glass row (handoff L484-493): lead text "Precisam de intervenção agora:" then four items — `Crítico ≤15%`, `Baixo ≤35%`, `Normal >35%`, `Sem comunicação` — each `icon + mono value + label`.
- Only the critical item gets a surface (`--tint-warning` + `inset 2px 0 0 var(--danger)`), consistent with the README's status-semantics rule that a colored surface means "needs action".
- Keeps the existing click-to-filter behavior; "Sem comunicação" counts offline printers, which are not a toner band, so it stays non-interactive as before.

### Task 4: Table per handoff

- Filter pills row (`Todos / Crítico · N / Baixo · N / Normal · N / Sem dados · N`, active = `--divider` + `--text-primary`) + compact search ("Nome ou IP", 9rem).
- Columns: `Impressora` (name + department line) | `Endereço` (mono) | `Status` | `Níveis por canal` | `Atividade` (right).
- Channel item: 7px square dot (radius 2px) + `2.75rem × 3px` track + mono `0.6875rem` percentage colored by `tonerLevelColor`.
- Critical rows get `inset 2px 0 0 var(--danger)` instead of the old inline alert icon.
- Footer: `Exibindo N de M impressoras · ordenadas por criticidade`, numbers mono.

### Task 5: Verify

- `npx tsc --noEmit` clean, `npm run build` green, no new lint warnings.

---

## Roadmap

Phase 4 — Alertas: severity-ordered list, critical/warning tabs with tinted counts, colored left rail per row (handoff README L107).
