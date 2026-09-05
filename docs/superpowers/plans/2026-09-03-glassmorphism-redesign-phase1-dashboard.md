# Glassmorphism Redesign — Phase 1 (Dashboard) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restyle the Dashboard screen (`/`) to match the glassmorphism handoff — vitals strip, fleet table, toner/quick-actions rail, and the 3-way analysis row — and wire it up as the first consumer of Phase 0's `PageHeader` component.

**Architecture:** Consumes the token layer, aurora, glass shell, and `PageHeader` component built in Phase 0 (already committed on this branch, `de54f48..bd45748`). No new tokens are introduced. Two Dashboard-only components (`StatCards.tsx`, `AlertBanner.tsx`) are replaced by one new component (`VitalsStrip.tsx`) that matches the handoff's single tinted strip; every other file is a targeted CSS-token restyle of existing components, no structural rewrites. `PrinterTable.module.css` is shared with the future Impressoras screen (Phase 2) — this phase applies only the screen-agnostic glass/token/mono changes the handoff specifies identically for both screens; status-tab/filter-panel work specific to Impressoras stays out of scope for Phase 2.

**Tech Stack:** Next.js (App Router), React, CSS Modules, `recharts` (BottomCharts' area/pie charts, untouched by this phase), lucide-react icons.

**Spec:** `design_handoff_printercontrol/README.md`, `design_handoff_printercontrol/PrinterControl v2.dc.html:184-391` (Dashboard screen block, `isDashboard`). Also `design_handoff_printercontrol/PrinterControl v2.dc.html:1128` for the exact page-header copy (`PAGE.dashboard`).

## Global Constraints

- Never hardcode a hex color in a component — always reference a CSS var token.
- Standard glass card recipe (`border: 1px solid var(--glass-border); border-radius: 14px; background: var(--glass-bg-elevated); backdrop-filter: var(--glass-blur); -webkit-backdrop-filter: var(--glass-blur); box-shadow: var(--glass-shadow);`) is the only "glass" treatment used for elevated cards/panels/tables in this phase — don't invent a variant. **Not every panel is glass**: the handoff uses solid/tinted (non-glass) backgrounds for the vitals strip, the "Níveis de toner" card, the "Reposição urgente" card, and the "Saúde da frota" card — follow the handoff's per-panel choice exactly rather than defaulting everything to glass.
- Any `:hover` inside a glass surface uses `--glass-hover` (translucent), never an opaque background token. Non-glass tinted panels (vitals strip, toner card) use a subtle `color-mix()` tint hover instead, matching their own background family — never `--glass-hover` on a non-glass surface.
- All numeric values (IP addresses, counts, percentages, timestamps) render in `var(--font-mono)` (already defined in `globals.css:6` as `var(--font-ibm-plex-mono), ui-monospace, "SFMono-Regular", Menlo, monospace` — use this token, don't restate the font stack).
- Hover/focus transitions: `background-color 0.12s ease-out` (or `border-color`/`color` alongside) only — no transform/scale/shadow-pop. (This removes the pre-existing `transform: translateY(-2px)` hover on stat cards and the `box-shadow` hover-pop on printer-table grid cards — both are being replaced by this phase anyway.)
- Must NOT regress: 3-state theme preference (`light`/`dark`/`system`, `src/lib/theme.tsx`) and `--font-scale` accessibility multiplier (`src/app/globals.css:46`).
- Business logic, data fetching, permissions (`useAppData`, `lib/auth.ts`, `lib/permissions.ts`) are untouched. Purely client-side derived presentation values (e.g. computing `topAlert`/`alertsRest` from the existing `alerts` array) are in scope; no new API calls, no backend changes, no change to `useAppData`'s return shape.
- Do not add `overflow: hidden` (or any property that creates a new scroll/stacking context) to an ancestor of a `position: sticky` element. This exact mistake regressed the Topbar/Sidebar in Phase 0's final review — don't repeat it.
- Before rewriting any container-level rule in an existing CSS module, read the whole file first and check every rule that implicitly depends on the old layout (Phase 0's review found collateral damage — dead rules, orphaned `order`/`width` hacks — from skipping this).
- Status semantics (used identically across Dashboard/Impressoras/Toner, README "Status semantics"): **Online** = `--success` dot with a `soft-pulse 3s ease-in-out infinite` animation, no colored pill background. **Offline** = `--text-muted` dot, no animation, no colored pill background. **Atenção** = `--warning` dot/icon **and** a `--tint-warning` pill background — the only status with a colored surface.

---

## File Structure

| File | Change |
|---|---|
| `src/app/globals.css` | Modify — add shared `@keyframes soft-pulse` (used by the status dot and the vitals strip's online indicator) |
| `src/app/page.tsx` | Modify — wire in `PageHeader`, replace `StatCards`+`AlertBanner` with `VitalsStrip` |
| `src/app/page.module.css` | Modify — retire the skeleton/grid rules made obsolete by `VitalsStrip`, adjust `.mainGrid` to the handoff's `minmax(0,1fr) 320px` |
| `src/components/VitalsStrip.tsx` | Create — single tinted strip (total / online / attention / offline / top alert), replaces `StatCards` + `AlertBanner` on the Dashboard |
| `src/components/VitalsStrip.module.css` | Create |
| `src/components/StatCards.tsx` | Delete — fully replaced by `VitalsStrip`, confirmed unused elsewhere |
| `src/components/StatCards.module.css` | Delete |
| `src/components/AlertBanner.tsx` | Delete — fully replaced by `VitalsStrip`, confirmed unused elsewhere |
| `src/components/AlertBanner.module.css` | Delete |
| `src/components/PrinterStatusBadge.tsx` | Modify — drop the pill background for Online/Offline, keep it only for Atenção |
| `src/components/PrinterStatusBadge.module.css` | Modify — token/semantics fix, `soft-pulse` on the online dot |
| `src/components/PrinterTable.module.css` | Modify — glass card recipe, `--glass-hover` row hover, `var(--font-mono)` on IP/toner/pagination, token swap (shared with Phase 2's Impressoras screen — screen-agnostic changes only) |
| `src/components/RightPanel.module.css` | Modify — `--tint-link` toner card, `--tint-plum` critical card, glass quick-actions card |
| `src/components/BottomCharts.module.css` | Modify — glass cards, navy-tinted header strip on the pages-chart card, `var(--font-mono)` on all numeric values |

---

### Task 1: Wire `PageHeader` into the Dashboard route

**Files:**
- Modify: `src/app/page.tsx:40-50` (the return block's opening)

**Interfaces:**
- Consumes: `PageHeader` from Phase 0 Task 3 (`section`, `title`, `subtitle`, `actions` props — see `src/components/PageHeader.tsx`).
- No CSS changes in this task — `PageHeader.module.css` already exists from Phase 0.

- [ ] **Step 1: Import `PageHeader` in `page.tsx`**

Add to the imports at the top of `src/app/page.tsx`:

```tsx
import PageHeader from "../components/PageHeader";
```

- [ ] **Step 2: Replace the standalone scan-bar row with `PageHeader`, moving the scan bar into its `actions` slot**

Replace this block (currently the first thing inside the returned `<>`):

```tsx
      <div className={styles.scanBar}>
        <p>
          Última verificação: <span className={styles.scanBarStrong}>{lastChecked.toLocaleTimeString("pt-BR")}</span>
        </p>
        <button onClick={handleRefresh} disabled={scanning} className={styles.scanButton}>
          <RefreshCw size={13} className={scanning ? "animate-spin" : ""} />
          {scanning ? "Verificando..." : "Verificar agora"}
        </button>
      </div>
```

with:

```tsx
      <PageHeader
        section="Monitoramento"
        title="Visão geral"
        subtitle="Estado consolidado da frota, suprimentos e consumo de páginas."
        actions={
          <div className={styles.scanBar}>
            <p>
              Última verificação: <span className={styles.scanBarStrong}>{lastChecked.toLocaleTimeString("pt-BR")}</span>
            </p>
            <button onClick={handleRefresh} disabled={scanning} className={styles.scanButton}>
              <RefreshCw size={13} className={scanning ? "animate-spin" : ""} />
              {scanning ? "Verificando..." : "Verificar agora"}
            </button>
          </div>
        }
      />
```

`section`/`title`/`subtitle` come verbatim from the handoff's `PAGE.dashboard` entry (`PrinterControl v2.dc.html:1128`) — note the title is **"Visão geral"**, not "Dashboard" (that word is only used as the internal route id, `screen: "dashboard"`).

- [ ] **Step 3: Verify**

Run: `npm run dev`, open `/`.
Expected: a breadcrumb ("Monitoramento / Visão geral"), an `<h1>Visão geral</h1>` with the left accent bar, a subtitle, and the "Última verificação / Verificar agora" control right-aligned on the same row (per `PageHeader`'s `.actions` slot). Clicking "Verificar agora" still triggers a refresh (unchanged `handleRefresh`).

- [ ] **Step 4: Commit**

```bash
git add src/app/page.tsx
git commit -m "feat: wire PageHeader into Dashboard route"
```

---

### Task 2: Status dot semantics — `soft-pulse` keyframe + `PrinterStatusBadge` token fix

**Files:**
- Modify: `src/app/globals.css` (add one `@keyframes` block)
- Modify: `src/components/PrinterStatusBadge.tsx`
- Modify: `src/components/PrinterStatusBadge.module.css`

**Interfaces:**
- Produces: `soft-pulse` keyframe (global, in `globals.css`) — consumed by this task's `.dotSuccess` and by Task 3's `VitalsStrip` online indicator.
- No prop/type changes — `PrinterStatusBadge`'s public signature (`{ status: PrinterStatus }`) is unchanged.

- [ ] **Step 1: Add the `soft-pulse` keyframe to `globals.css`**

Insert immediately after the existing `@keyframes pulse { ... }` block (right before `.animate-pulse { ... }`, currently around line 261-265 — confirm the exact line with `grep -n "@keyframes pulse" src/app/globals.css` first):

```css
@keyframes soft-pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.55;
    transform: scale(0.85);
  }
}
```

- [ ] **Step 2: Rewrite `PrinterStatusBadge.module.css`**

Replace the entire file with:

```css
.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  border-radius: 999px;
  padding: 0.25rem 0.625rem;
  font-size: 0.8125rem;
  font-weight: 500;
}

.dot {
  height: 0.5rem;
  width: 0.5rem;
  border-radius: 999px;
}

.dotSuccess {
  background: var(--success);
  animation: soft-pulse 3s ease-in-out infinite;
}

.dotFaint {
  background: var(--text-muted);
}

.dotWarning {
  background: var(--warning);
}

.textSuccess {
  color: var(--success);
}

.textSoft {
  color: var(--text-secondary);
}

.textWarning {
  color: var(--warning);
}

.bgWarning {
  background: var(--tint-warning);
}
```

(`.bgSuccess`/`.bgSurface` are removed — Online and Offline no longer get a pill background, per the Global Constraints status-semantics rule.)

- [ ] **Step 3: Update `PrinterStatusBadge.tsx` to drop the background for Online/Offline**

Replace the file's content with:

```tsx
import { TriangleAlert } from "lucide-react";
import type { PrinterStatus } from "../types";
import { cn } from "../lib/cn";
import styles from "./PrinterStatusBadge.module.css";

const config: Record<PrinterStatus, { label: string; dot: string; text: string; bg?: string }> = {
  online: { label: "Online", dot: styles.dotSuccess, text: styles.textSuccess },
  offline: { label: "Offline", dot: styles.dotFaint, text: styles.textSoft },
  atencao: { label: "Atenção", dot: styles.dotWarning, text: styles.textWarning, bg: styles.bgWarning },
};

export default function PrinterStatusBadge({ status }: { status: PrinterStatus }) {
  const c = config[status];
  return (
    <span className={cn(styles.badge, c.text, c.bg)}>
      {status === "atencao" ? (
        <TriangleAlert size={12} />
      ) : (
        <span className={cn(styles.dot, c.dot)} />
      )}
      {c.label}
    </span>
  );
}
```

`cn()` (`src/lib/cn.ts:1`) already filters falsy args (`string | false | null | undefined`), so passing `c.bg` (`undefined` for online/offline) is safe — no signature change needed. The online dot's animation now lives permanently on `.dotSuccess` in CSS, so the old `status === "online" && "animate-pulse"` conditional class is removed as dead code.

- [ ] **Step 4: Verify**

Run: `npm run dev`, open `/printers` (fastest place to see many badges at once) or `/`.
Expected: Online badges show a breathing (soft-pulse) green dot with no background pill. Offline badges show a static muted dot, no background. Atenção badges keep the triangle-alert icon on a `--tint-warning` pill, unchanged in appearance. Toggle dark mode — colors adapt via the existing tokens.

- [ ] **Step 5: Commit**

```bash
git add src/app/globals.css src/components/PrinterStatusBadge.tsx src/components/PrinterStatusBadge.module.css
git commit -m "fix: status dot semantics (soft-pulse online, no pill bg for online/offline)"
```

---

### Task 3: Vitals strip (`VitalsStrip`, replaces `StatCards` + `AlertBanner`)

**Files:**
- Create: `src/components/VitalsStrip.tsx`
- Create: `src/components/VitalsStrip.module.css`
- Delete: `src/components/StatCards.tsx`, `src/components/StatCards.module.css`
- Delete: `src/components/AlertBanner.tsx`, `src/components/AlertBanner.module.css`
- Modify: `src/app/page.tsx` (swap the two old components for the one new one)
- Modify: `src/app/page.module.css` (skeleton adjustment)

**Interfaces:**
- Consumes: `soft-pulse` keyframe from Task 2 (online dot).
- Produces: `export default function VitalsStrip(props: VitalsStripProps)`:
  ```ts
  interface VitalsStripProps {
    total: number;
    online: number;
    attention: number;
    offline: number;
    activeStatus: "Todos" | "online" | "offline" | "atencao";
    onSelectStatus: (status: "Todos" | "online" | "offline" | "atencao") => void;
    topAlert: Alert | null;      // from "../types"
    alertsRest: number;          // count of remaining alerts beyond topAlert
    onViewAlerts: () => void;
    onSelectAlert?: (alert: Alert) => void;
  }
  ```
- `StatCards.tsx`/`AlertBanner.tsx` and their CSS modules are confirmed used only by `src/app/page.tsx` (verified via `grep -rn "StatCards\|AlertBanner" src` before writing this plan) — safe to delete once `page.tsx` no longer imports them.

- [ ] **Step 1: Create `src/components/VitalsStrip.tsx`**

```tsx
"use client";

import { ArrowRight, TriangleAlert } from "lucide-react";
import type { Alert } from "../types";
import { cn } from "../lib/cn";
import styles from "./VitalsStrip.module.css";

type StatusFilter = "Todos" | "online" | "offline" | "atencao";

interface VitalsStripProps {
  total: number;
  online: number;
  attention: number;
  offline: number;
  activeStatus: StatusFilter;
  onSelectStatus: (status: StatusFilter) => void;
  topAlert: Alert | null;
  alertsRest: number;
  onViewAlerts: () => void;
  onSelectAlert?: (alert: Alert) => void;
}

export default function VitalsStrip({
  total,
  online,
  attention,
  offline,
  activeStatus,
  onSelectStatus,
  topAlert,
  alertsRest,
  onViewAlerts,
  onSelectAlert,
}: VitalsStripProps) {
  return (
    <div className={styles.strip}>
      <button
        onClick={() => onSelectStatus("Todos")}
        className={cn(styles.totalCell, activeStatus === "Todos" && styles.cellActive)}
      >
        <p className={styles.totalLabel}>Frota monitorada</p>
        <p className={styles.totalValue}>{total}</p>
      </button>

      <div className={styles.countsCell}>
        <button
          onClick={() => onSelectStatus("online")}
          className={cn(styles.countItem, activeStatus === "online" && styles.cellActive)}
        >
          <p className={styles.countLabel}>
            <span className={cn(styles.dot, styles.dotSuccess)} />
            Online
          </p>
          <p className={cn(styles.countValue, styles.countValueSuccess)}>{online}</p>
        </button>
        <button
          onClick={() => onSelectStatus("atencao")}
          className={cn(styles.countItem, activeStatus === "atencao" && styles.cellActive)}
        >
          <p className={styles.countLabel}>
            <span className={cn(styles.dot, styles.dotWarning)} />
            Atenção
          </p>
          <p className={cn(styles.countValue, styles.countValueWarning)}>{attention}</p>
        </button>
        <button
          onClick={() => onSelectStatus("offline")}
          className={cn(styles.countItem, activeStatus === "offline" && styles.cellActive)}
        >
          <p className={styles.countLabel}>
            <span className={cn(styles.dot, styles.dotMuted)} />
            Offline
          </p>
          <p className={styles.countValue}>{offline}</p>
        </button>
      </div>

      {topAlert && (
        <div className={styles.alertCell}>
          <TriangleAlert size={18} className={styles.alertIcon} />
          <div className={styles.alertBody}>
            <p className={styles.alertLabel}>Mais urgente agora</p>
            <button onClick={() => onSelectAlert?.(topAlert)} className={styles.alertMessage}>
              {topAlert.message}
              {alertsRest > 0 && <span className={styles.alertRest}> · +{alertsRest} outros</span>}
            </button>
          </div>
          <button onClick={onViewAlerts} className={styles.alertLink}>
            Ver alertas
            <ArrowRight size={14} />
          </button>
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Create `src/components/VitalsStrip.module.css`**

```css
.strip {
  display: flex;
  flex-wrap: wrap;
  align-items: stretch;
  border-radius: 12px;
  overflow: hidden;
  background: color-mix(in srgb, var(--navy) 7%, var(--bg-surface));
  box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--navy) 18%, var(--border));
}

.totalCell {
  flex: 1 1 11rem;
  min-width: 11rem;
  padding: 1.5rem 1.75rem;
  border-right: 1px solid color-mix(in srgb, var(--navy) 14%, var(--border));
  text-align: left;
  transition: background-color 0.12s ease-out;
}

.totalCell:hover {
  background: color-mix(in srgb, var(--navy) 5%, transparent);
}

.totalLabel {
  font-size: 0.625rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--navy-text);
}

.totalValue {
  margin-top: 0.625rem;
  font-family: var(--font-mono);
  font-size: 2.75rem;
  font-weight: 500;
  letter-spacing: -0.03em;
  line-height: 1;
  color: var(--text-primary);
}

.countsCell {
  flex: 1 1 14rem;
  min-width: 14rem;
  display: flex;
  align-items: stretch;
  border-right: 1px solid color-mix(in srgb, var(--navy) 14%, var(--border));
}

.countItem {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 1.5rem 0.875rem;
  text-align: left;
  transition: background-color 0.12s ease-out;
}

.countItem:hover {
  background: color-mix(in srgb, var(--navy) 5%, transparent);
}

.cellActive {
  background: var(--tint-link);
}

.countLabel {
  display: flex;
  align-items: center;
  gap: 0.4375rem;
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.dot {
  height: 6px;
  width: 6px;
  border-radius: 999px;
  flex-shrink: 0;
}

.dotSuccess {
  background: var(--success);
  animation: soft-pulse 3s ease-in-out infinite;
}

.dotWarning {
  background: var(--warning);
}

.dotMuted {
  background: var(--text-muted);
}

.countValue {
  margin-top: 0.4375rem;
  font-family: var(--font-mono);
  font-size: 1.375rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.countValueSuccess {
  color: var(--success);
}

.countValueWarning {
  color: var(--warning);
}

.alertCell {
  padding: 1.5rem 1.75rem;
  flex: 2 1 22rem;
  min-width: 22rem;
  display: flex;
  align-items: center;
  gap: 0.875rem;
  background: var(--tint-plum);
}

.alertIcon {
  flex-shrink: 0;
  color: var(--danger);
}

.alertBody {
  min-width: 0;
  flex: 1;
}

.alertLabel {
  font-size: 0.625rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--danger);
}

.alertMessage {
  margin-top: 0.25rem;
  display: block;
  width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  text-align: left;
  font-size: 0.8125rem;
  color: var(--text-primary);
}

.alertRest {
  color: var(--text-secondary);
}

.alertLink {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--link);
  transition: color 0.12s ease-out;
}

.alertLink:hover {
  color: var(--link-hover);
}
```

- [ ] **Step 3: Wire `VitalsStrip` into `page.tsx`, remove `StatCards`/`AlertBanner`**

In `src/app/page.tsx`, replace the import lines:

```tsx
import StatCards from "../components/StatCards";
import AlertBanner from "../components/AlertBanner";
```

with:

```tsx
import VitalsStrip from "../components/VitalsStrip";
```

Replace this block (the `initialLoading ? <skeleton> : <StatCards .../>` plus the following `AlertBanner` block):

```tsx
      {initialLoading ? (
        <div className={styles.statsSkeletonGrid}>
          {Array.from({ length: 4 }, (_, i) => (
            <div key={i} className={cn(styles.skeletonCard, styles.skeletonCardStats, "animate-pulse")} />
          ))}
        </div>
      ) : (
        <StatCards
          total={stats.total}
          online={stats.online}
          offline={stats.offline}
          attention={stats.attention}
          activeStatus={filters.status === "Todos" ? "Todos" : filters.status}
          onSelectStatus={(s) => updateFilter("status", s)}
        />
      )}

      {!initialLoading && alerts.length > 0 && (
        <AlertBanner alerts={alerts} onViewAll={() => router.push("/alerts")} onSelectAlert={handleAlertSelect} />
      )}
```

with:

```tsx
      {initialLoading ? (
        <div className={cn(styles.skeletonCard, styles.skeletonCardStrip, "animate-pulse")} />
      ) : (
        <VitalsStrip
          total={stats.total}
          online={stats.online}
          offline={stats.offline}
          attention={stats.attention}
          activeStatus={filters.status === "Todos" ? "Todos" : filters.status}
          onSelectStatus={(s) => updateFilter("status", s)}
          topAlert={alerts[0] ?? null}
          alertsRest={Math.max(alerts.length - 1, 0)}
          onViewAlerts={() => router.push("/alerts")}
          onSelectAlert={handleAlertSelect}
        />
      )}
```

- [ ] **Step 4: Update `page.module.css`'s skeleton rules**

Replace the `.statsSkeletonGrid` block (and its `@media (min-width: 1024px)` override) with a single strip-shaped skeleton:

```css
.skeletonCardStrip {
  height: 108px;
}
```

(Delete the old `.statsSkeletonGrid` rule and its media-query override entirely — nothing else references it once Step 3 lands. Keep `.skeletonCard`, `.skeletonCardTable`, `.mainGrid` as-is; only `.statsSkeletonGrid` goes away.)

- [ ] **Step 5: Delete the now-unused files**

```bash
git rm src/components/StatCards.tsx src/components/StatCards.module.css
git rm src/components/AlertBanner.tsx src/components/AlertBanner.module.css
```

- [ ] **Step 6: Verify**

Run: `npx tsc --noEmit` (confirm no dangling imports/type errors), then `npm run dev`, open `/`.
Expected: one navy-tinted strip (not glass — no blur/backdrop) with 4 sections: total (big mono number), online/atenção/offline (small mono numbers with colored dots, online dot breathing), and — when there are alerts — a plum-tinted "Mais urgente agora" segment with the top alert message and a "Ver alertas" link. Clicking total/online/atenção/offline still filters the fleet table below (unchanged `updateFilter` behavior). Clicking the alert message opens that alert's printer detail (`handleAlertSelect`, unchanged). With zero alerts, the strip still renders with just 2 sections (no plum segment) — confirm by temporarily filtering to an empty result or checking the `topAlert && (...)` guard covers it. Toggle dark mode.

- [ ] **Step 7: Commit**

```bash
git add src/components/VitalsStrip.tsx src/components/VitalsStrip.module.css src/app/page.tsx src/app/page.module.css
git commit -m "feat: replace StatCards+AlertBanner with glassmorphism VitalsStrip"
```

---

### Task 4: Fleet table glass restyle (`PrinterTable.module.css`)

**Files:**
- Modify: `src/components/PrinterTable.module.css`

**Interfaces:**
- Consumes: tokens from Phase 0 (`--glass-*`, `--font-mono`, `--border`, `--divider`, `--text-*`, `--track`).
- No TSX changes — `PrinterTable.tsx` markup is unchanged; only its CSS module's color/effect declarations change.
- Shared file: also renders on `/printers` (Phase 2, full mode) — this task only applies the glass/token/mono changes the handoff specifies identically for the table container and rows on every screen; status-tab and filter-panel restyling specific to Impressoras is Phase 2's job.

- [ ] **Step 1: Read the current file to confirm line numbers before editing**

Run: `grep -n "^\." src/components/PrinterTable.module.css` (line numbers below were confirmed against the version read while writing this plan; re-check before editing in case Phase 0/earlier tasks shifted them).

- [ ] **Step 2: Replace `.root` (table container) with the glass recipe**

```css
.root {
  min-width: 0;
  overflow: hidden;
  border: 1px solid var(--glass-border);
  border-radius: 14px;
  background: var(--glass-bg-elevated);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  box-shadow: var(--glass-shadow);
}
```

- [ ] **Step 3: Swap `--color-*` tokens for the new tokens throughout the file**

Apply this replacement table to every remaining rule in the file (search-and-replace each old token for its new equivalent; do not change any non-color property):

| Old token | New token |
|---|---|
| `var(--color-border)` | `var(--border)` |
| `var(--color-surface)` | `var(--bg-surface)` |
| `var(--color-surface-2)` | `var(--divider)` |
| `var(--color-surface-sunken)` | `var(--track)` |
| `var(--color-canvas)` | `var(--bg-page)` |
| `var(--color-ink)` | `var(--text-primary)` |
| `var(--color-ink-soft)` | `var(--text-secondary)` |
| `var(--color-ink-faint)` | `var(--text-muted)` |
| `var(--color-brand)` / `var(--color-brand-600)` / `var(--color-brand-700)` | `var(--link-hover)` (interactive/active state) or `var(--link)` (static accent) — use `--link-hover` for anything currently `-brand`/`-brand-600` (hover/active), `--link` for anything currently `-brand-700` (static text-on-tint) |
| `var(--color-brand-tint)` | `var(--tint-link)` |
| `var(--shadow-sm)` on `.root`/`.card` | removed — the glass recipe's own `box-shadow: var(--glass-shadow)` (Step 2) replaces it; do not keep both |

- [ ] **Step 4: Fix the two hover states that use an opaque background inside this now-glass container**

`.row:hover` (table row hover) and `.filterButton:hover`/`.filterPill:hover`-adjacent rules that currently target `--color-surface-2`/`--color-surface-sunken` must use `--glass-hover` instead, since they're hovers *inside* the now-glass `.root`:

```css
.row:hover {
  background: var(--glass-hover);
}
```

Leave `.gridCard:hover`'s box-shadow-ring effect — remove it per the Global Constraint (no shadow-pop hover); replace with a `border-color` transition instead:

```css
.gridCard {
  border-radius: 1rem;
  border: 1px solid var(--border);
  background: var(--bg-page);
  padding: 1.25rem;
  text-align: left;
  transition: border-color 0.12s ease-out;
  cursor: pointer;
}

.gridCard:hover {
  border-color: var(--link-hover);
}
```

- [ ] **Step 5: Apply `var(--font-mono)` to numeric/IP columns**

Add `font-family: var(--font-mono);` to `.td` cells that render the IP address (the plain `{p.ip}` cell — currently no dedicated class; wrap it isn't needed, just add the property to `.td` is too broad since `.td` is reused for text columns too). Instead, confirm in `PrinterTable.tsx` whether the IP `<td>` has its own class — it currently uses the shared `.td` for department/toner/status too, so **do not** add `font-family` to `.td` itself. Add it narrowly to `.tonerPercent` (already exists) and `.pageSizeSelect`'s options are not numeric-critical; the two genuinely numeric, mono-worthy spots in this file's CSS are `.tonerPercent` and `.pageNumber`:

```css
.tonerPercent {
  font-family: var(--font-mono);
  font-size: 0.875rem;
  font-weight: 600;
}
```

```css
.pageNumber {
  font-family: var(--font-mono);
  min-width: 2rem;
  height: 2rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
  transition: background-color 0.12s ease-out;
  display: flex;
  align-items: center;
  justify-content: center;
}
```

(The IP address cell itself has no dedicated CSS class today — adding one is a structural TSX change outside this CSS-only task's scope. Note it in the task report as a follow-up for Phase 2, when Impressoras' full (non-compact) table gets its own pass — the IP column is visible on both screens today without mono styling, which is a pre-existing gap, not a regression introduced here.)

- [ ] **Step 6: Verify**

Run: `npm run dev`, open `/` (compact table) and `/printers` (full table).
Expected: the table container reads as frosted glass over the aurora, row hover shows a translucent (not opaque) highlight, toner percentages and pagination numbers use the monospace font, active filter pills/buttons use the link-blue tint instead of the old brand color. No `--color-*`-token console warnings (all resolved). Toggle dark mode on both routes.

- [ ] **Step 7: Commit**

```bash
git add src/components/PrinterTable.module.css
git commit -m "feat: restyle fleet table with glassmorphism tokens"
```

---

### Task 5: Toner/quick-actions rail restyle (`RightPanel.module.css`)

**Files:**
- Modify: `src/components/RightPanel.module.css`

**Interfaces:**
- Consumes: tokens from Phase 0 (`--tint-link`, `--tint-plum`, `--glass-*`, `--link`, `--danger`, `--font-mono`).
- No TSX changes.

- [ ] **Step 1: Restyle the toner-levels card (`.card` — first occurrence, "Níveis de toner") as a non-glass tinted panel**

The handoff (`PrinterControl v2.dc.html:292`) uses a flat tinted card here, not glass. Since `.card` in the current file is shared by both the toner-levels card and the quick-actions card (which the handoff does use glass for — line 324), split it into two classes. Rename the first usage's class in `RightPanel.tsx` from `styles.card` to `styles.tonerCard` (the "Níveis de toner" `<div className={styles.card}>` at line 56 of `RightPanel.tsx`), and add:

```css
.tonerCard {
  border-radius: 10px;
  background: var(--tint-link);
  box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--link) 20%, var(--border));
  padding: 1.25rem;
}
```

- [ ] **Step 2: Restyle the quick-actions card (`.card` — second occurrence) as a glass card**

Rename that second `<div className={styles.card}>` (the "Ações rápidas" one, `RightPanel.tsx` line 104) to `styles.quickActionsCard` and add:

```css
.quickActionsCard {
  border: 1px solid var(--glass-border);
  border-radius: 14px;
  background: var(--glass-bg-elevated);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  box-shadow: var(--glass-shadow);
  padding: 1.25rem;
}
```

Delete the old shared `.card` rule once both usages are renamed.

- [ ] **Step 3: Update `.criticalCard` (Reposição urgente / low-toner alert) to the tinted-plum treatment**

```css
.criticalCard {
  border-radius: 10px;
  background: var(--tint-plum);
  box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--danger) 22%, var(--border));
  padding: 1.25rem;
}
```

Update `.criticalIconWrap`, `.criticalLabel`, `.criticalValue`, `.criticalDesc`, `.criticalButton` to swap `--color-critical*`/`--color-ink*` for `--danger`/`--text-*` (same token-mapping table as Task 4 Step 3, plus `--color-critical` → `--danger`, `--color-critical-tint` → not needed here since the card itself is now the tint).

- [ ] **Step 4: Apply `var(--glass-hover)` to `.quickAction:hover` (it's inside the now-glass quick-actions card) and `var(--font-mono)` to the toner percentages**

```css
.quickAction:hover {
  background: var(--glass-hover);
}
```

```css
.tonerPercentValue {
  font-family: var(--font-mono);
  font-weight: 600;
  color: var(--text-primary);
}
```

- [ ] **Step 5: Swap every remaining `--color-*` token in the file** per Task 4 Step 3's mapping table (`--color-ink` → `--text-primary`, `--color-ink-soft` → `--text-secondary`, `--color-ink-faint` → `--text-muted`, `--color-brand-700` → `--link`, `--color-brand-600` → `--link-hover`, `--color-surface-sunken` → `--track`).

- [ ] **Step 6: Verify**

Run: `npm run dev`, open `/`.
Expected: "Níveis de toner" renders as a light-blue tinted panel (not glass — no blur), "Reposição urgente" (when a toner channel is ≤20%) renders as a plum-tinted panel, "Ações rápidas" renders as a frosted glass panel with translucent row hovers. Percentages use the monospace font. Toggle dark mode.

- [ ] **Step 7: Commit**

```bash
git add src/components/RightPanel.tsx src/components/RightPanel.module.css
git commit -m "feat: restyle toner/quick-actions rail with glassmorphism tokens"
```

---

### Task 6: Analysis row restyle (`BottomCharts.module.css`)

**Files:**
- Modify: `src/components/BottomCharts.module.css`

**Interfaces:**
- Consumes: tokens from Phase 0 (`--glass-*`, `--navy`, `--tint-success`, `--font-mono`).
- No TSX changes, no chart-data changes.

**Ruling — third card content (donut vs. "Saúde da frota"):** the handoff's third analysis-row card (`PrinterControl v2.dc.html:369-388`) is "Saúde da frota" — a list of named health-metric bars (`healthBars`, e.g. per-department or per-category percentages) — not an alerts donut chart. The current codebase's third card, `AlertsDonutCard`, shows a donut of attention-vs-ok devices instead. Building genuine "Saúde da frota" content requires a new derived metric (which categories? computed how, from what data?) that doesn't exist in `useAppData()` today and is a product decision, not a restyle decision — out of scope for a presentation-only phase per the Global Constraints. **Decision: keep `AlertsDonutCard`'s existing content and behavior, restyle it to the glass recipe only.** This is a documented deviation from the handoff's card content (not its container styling) — flag it as a candidate for a future phase once real per-category health data exists.

- [ ] **Step 1: Restyle `.card` (all three analysis cards) to the glass recipe**

```css
.card {
  border: 1px solid var(--glass-border);
  border-radius: 14px;
  background: var(--glass-bg-elevated);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  box-shadow: var(--glass-shadow);
  padding: 1.25rem;
}
```

- [ ] **Step 2: Add the navy-tinted header strip to the "Consumo de páginas" card**

The handoff (`PrinterControl v2.dc.html:343`) gives this card's header row its own tinted background, distinct from the card body. In `BottomCharts.tsx`'s `PagesConsumedCard`, the `.headerRow` div (line 54) needs its own header-strip treatment separate from the card's padding — add a new class:

```css
.pagesHeaderRow {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  margin: -1.25rem -1.25rem 1rem;
  padding: 0.875rem 1.25rem;
  background: color-mix(in srgb, var(--navy) 6%, var(--bg-surface));
  border-bottom: 1px solid var(--glass-border);
  border-radius: 14px 14px 0 0;
}
```

In `BottomCharts.tsx`, change the `PagesConsumedCard`'s header `<div className={styles.headerRow}>` to `<div className={styles.pagesHeaderRow}>` (only this one usage — `TotalPrintsCard` and `AlertsDonutCard` don't have this tinted-header treatment per the handoff, they keep the plain glass card padding). Keep `.periodBadge` using `var(--tint-link)`/`var(--link)` instead of `--color-brand-tint`/`--color-brand-700`.

- [ ] **Step 3: Swap remaining `--color-*` tokens** per Task 4 Step 3's mapping table, plus: `--color-success` → `--success`, `--color-critical` → `--danger`, `--color-warning` → `--warning`.

- [ ] **Step 4: Apply `var(--font-mono)` to the numeric displays**

```css
.totalValue {
  font-family: var(--font-mono);
  margin-top: 0.75rem;
  font-size: 2.25rem;
  font-weight: 800;
  line-height: 1;
  letter-spacing: -0.025em;
  color: var(--text-primary);
}
```

```css
.attentionValue {
  font-family: var(--font-mono);
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--warning);
}
```

Also add `font-family: var(--font-mono);` to `.periodBadge` (renders `{last.month}: {last.pages}` — a numeric-bearing label) and to `.growthRow` (renders the `±N.N%` figure).

- [ ] **Step 5: Verify**

Run: `npm run dev`, open `/`, scroll to the bottom row.
Expected: all three cards read as frosted glass; "Consumo de páginas" has a subtle navy-tinted header strip above its chart; big numbers (total impressions, alert count) use the monospace font; the third card is still the donut-of-alerts (unchanged data/behavior, glass container only). Toggle dark mode — recharts' own colors come from `lib/chartColors.ts` and are untouched by this task, confirm they still look correct against the new glass background.

- [ ] **Step 6: Commit**

```bash
git add src/components/BottomCharts.tsx src/components/BottomCharts.module.css
git commit -m "feat: restyle analysis row with glassmorphism tokens (donut card content deviation documented)"
```

---

## Self-Review

**Spec coverage:** README's Dashboard line ("vitals strip → fleet table + toner/quick-actions rail → 3-way analysis row") — all three sections covered (Tasks 3, 4+2, 5, 6). Page-header wiring (Task 1) is Phase 0's PageHeader's first real consumer, per Phase 0's roadmap note. Status semantics (README "Status semantics") — Task 2. Typography rule (IBM Plex Mono for numerics) — applied in Tasks 3, 4, 5, 6 wherever this screen renders a number; two pre-existing gaps (the fleet table's un-classed IP `<td>`, and any numeric text inside `PrinterTable.tsx`'s grid-view cards not covered above) are explicitly noted as Phase 2 follow-ups rather than silently dropped. Glass-vs-non-glass per-panel treatment — explicitly matched to the handoff panel-by-panel in Tasks 3 and 5 rather than defaulting everything to glass. The one deliberate content deviation (donut vs. "Saúde da frota") is ruled and documented in Task 6, not silently ignored.

**Placeholder scan:** none found — every step has literal, complete code (component bodies, full CSS blocks, exact token-mapping tables) rather than descriptions of what to write.

**Type consistency:** `VitalsStripProps` (Task 3) is the only new exported interface; its `StatusFilter` union (`"Todos" | "online" | "offline" | "atencao"`) matches `page.tsx`'s existing `filters.status`/`updateFilter("status", ...)` usage exactly (checked against the current `page.tsx` read while writing this plan — `activeStatus={filters.status === "Todos" ? "Todos" : filters.status}` already narrows to this same union before Task 3 touches it). `PrinterStatusBadge`'s `config` type (Task 2) gains an optional `bg?: string` — checked against `cn()`'s actual signature (`Array<string | false | null | undefined>`) to confirm passing `undefined` compiles and filters correctly, not assumed.

---

## Roadmap (unchanged from Phase 0's plan)

Phase 2 — Impressoras is next: filterable/searchable fleet table (the same `PrinterTable.tsx` this phase restyled, now in its full non-compact form), status tabs, and — per Task 4's noted follow-up — the IP column's missing monospace styling.
