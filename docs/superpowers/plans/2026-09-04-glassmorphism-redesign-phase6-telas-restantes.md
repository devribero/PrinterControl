# Glassmorphism Redesign — Phase 6 (remaining screens) Implementation Plan

Closes the redesign: Histórico, Integrações, Rede, Notificações, Usuários, Configurações — plus the retirement of the legacy `--color-*` token layer.

**Spec:** `design_handoff_printercontrol/PrinterControl v2.dc.html` — Histórico L668-762, Integrações L899-907, Rede L765-..., Configurações L909-..., page-header copy at L1126-1139.

## Scope decision

Histórico and Integrações are restyled to the handoff structure. Rede (981 lines), Usuários (554), Notificações (499) and Configurações (469) carry far more functionality than the handoff mocks — the handoff shows an empty state or a partial slice of each. Rewriting them from a mock would delete working behavior, so they get the page header plus a full token migration onto the redesign palette, and keep their own structure. Their handoff-specific structures (role tabs on Usuários, the Print-Server error banner, the settings section nav) are left as follow-ups.

### Task 1: Histórico

- `src/app/history/page.tsx`: `PageHeader` ("Monitoramento" / "Histórico" / "Contadores por impressora e por unidade, mês a mês.").
- `HistoryMatrix`: header card with icon → the handoff's summary row (`Histórico de impressão` + mono `N páginas · N meses · N unidades`, expand/collapse buttons on the right). Totals table becomes `Período | months | Total` with the grand total in `--link`. Site accordions become glass cards: toggle row with chevron + site + count + mono total; open panel is the printer table with a `--bg-page` subtotal row.

### Task 2: Integrações

- `ComingSoon` stops being a centered dashed hero and becomes the handoff's inline glass notice row (icon + title + one-line description). The handoff is explicit that this screen is deliberately minimal.
- `src/app/integrations/page.tsx`: `PageHeader` ("Administração" / "Integrações").

### Task 3: Page headers on the four functional screens

`/network`, `/notifications`, `/users`, `/settings` get `PageHeader` with the handoff copy. `UsersView`'s card header loses its duplicated "Usuários" title (the count line stays as the card's meta); the other three only had card-level titles, which the handoff also has, so they stay.

### Task 4: Retire the legacy token layer

Every remaining `var(--color-*)` in the app migrates to the redesign tokens, including the `var(--color-x, fallback)` form Phase 0 introduced for unmigrated screens, `lib/tonerColor.ts`'s returned colors, and `globals.css`'s own base rules (body, scrollbars, selection, focus ring). Mapping:

| legacy | redesign |
|---|---|
| `--color-canvas` | `--bg-page` |
| `--color-surface` | `--bg-surface` |
| `--color-surface-2` | `--divider` |
| `--color-surface-sunken` | `--track` |
| `--color-border` / `--color-border-strong` | `--border` / `--border-strong` |
| `--color-ink` / `-soft` / `-faint` | `--text-primary` / `--text-secondary` / `--text-muted` |
| `--color-brand-700` / `--color-brand` / `--color-brand-600` | `--link` / `--link-hover` |
| `--color-brand-tint` / `--color-info-tint` | `--tint-link` |
| `--color-success` / `-tint` | `--success` / `--tint-success` |
| `--color-warning` / `-tint` | `--warning` / `--tint-warning` |
| `--color-critical` / `-tint` | `--danger` / `--danger-bg` |
| `--color-info` | `--link` |

Two tokens referenced only through fallbacks never existed (`--color-brand-border`, `--color-success-border`, `--color-warning-border`) — they resolve to `--border-strong` now instead of silently falling through.

With no usages left, the 42 `--color-*` definitions are deleted from `globals.css`'s `:root` and `html.dark` blocks. The dark palette shifts from the old warm browns to the redesign's neutral darks, which is the intended change.

### Task 5: Verify

`npx tsc --noEmit` clean, `npm run build` green, lint warning count unchanged (7, all pre-existing `only-export-components`).

---

## Follow-ups (not done here)

- Usuários: handoff's role-filter tabs (Todos/Administradores/Operadores/Inativos) and the backend-error state inside the table header.
- Rede: handoff's error banner and empty state styling.
- Configurações: handoff's sticky section nav on the left.
- Visual pass in the browser on both themes across all 12 routes — nothing in this redesign has been verified visually yet.
