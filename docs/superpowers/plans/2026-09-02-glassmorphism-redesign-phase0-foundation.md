# Glassmorphism Redesign — Phase 0 (Foundation) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Introduce the glassmorphism design system (tokens, aurora background, glass shell) into the existing Next.js frontend and restyle the app shell (Sidebar, Topbar, root layout) and Login screen to match the handoff — without touching business logic, data flow, or the existing 3-state theme system.

**Architecture:** Purely additive CSS-token layer on top of the existing CSS-Modules + CSS-custom-properties setup (`src/app/globals.css`, `html.dark` selector, `useTheme()` in `src/lib/theme.tsx`). New tokens live alongside the old `--color-*` tokens (not replacing them yet) so unmigrated screens (Phase 1+) keep working unchanged. Structural JSX changes are kept minimal — Sidebar/Login are already close to the handoff's structure; only Topbar loses its greeting text in favor of the new page-header pattern (built here, wired into individual pages during later phases).

**Tech Stack:** Next.js (App Router), React, CSS Modules, `next/font` (Public Sans / IBM Plex Mono already loaded in `layout.tsx`), lucide-react icons.

**Spec:** `design_handoff_printercontrol/README.md`, `design_handoff_printercontrol/PrinterControl v2.dc.html` (lines 1–225: tokens + shell), `design_handoff_printercontrol/Login v2.dc.html` (full file). This plan implements the "Layout structure" and "Design Tokens" sections of the README; screen-specific sections (Dashboard, Impressoras, etc.) are out of scope — later phases.

## Global Constraints

- Never hardcode a hex color in a component — always reference a CSS var token (README "Design Tokens").
- Standard glass card recipe (border + radius 14px + `--glass-bg-elevated` + `--glass-blur` + `--glass-shadow`) is the only "glass" treatment used for shell surfaces in this phase (Sidebar, Header) — don't invent a variant.
- Any `:hover` inside a glass surface uses `--glass-hover` (translucent), never an opaque background token — this was a real bug in the handoff session, don't reintroduce it.
- All numeric values (IP, version, counts, timestamps) render in `'IBM Plex Mono', var(--font-ibm-plex-mono)`.
- Hover/focus transitions: `background-color 0.12s ease-out` (or `border-color`/`color` alongside) only — no transform/scale/shadow-pop.
- Must NOT regress: 3-state theme preference (`light`/`dark`/`system`, `src/lib/theme.tsx`) and `--font-scale` accessibility multiplier (`src/app/globals.css:46`). Both are absent from the handoff (which only has a 2-state toggle) — keep the existing logic, only swap visual token values.
- Business logic, data fetching, permissions (`useAppData`, `lib/auth.ts`, `lib/permissions.ts`) are untouched — this phase is presentation-only.

---

## File Structure

| File | Change |
|---|---|
| `src/app/globals.css` | Modify — add new token block (additive) under `:root` and `html.dark` |
| `src/components/AppShell.tsx` | Modify — add aurora background layer |
| `src/components/AppShell.module.css` | Modify — add `.aurora`/`.auroraBlob*` classes, make `.shell` `position: relative` |
| `src/components/PageHeader.tsx` | Create — reusable breadcrumb + title + subtitle + accent bar + actions slot |
| `src/components/PageHeader.module.css` | Create |
| `src/components/Sidebar.module.css` | Modify — glass-elevated aside, tint-link active state, glass-hover hover state |
| `src/components/Topbar.tsx` | Modify — drop greeting block, add avatar-initials chip matching handoff |
| `src/components/Topbar.module.css` | Modify — glass-elevated header, restyle search/icon buttons/avatar |
| `src/components/Login.module.css` | Modify — swap hero panel navy + form panel tokens to match handoff exactly (structure in `Login.tsx` already matches, no TSX changes needed) |

---

### Task 1: Design tokens

**Files:**
- Modify: `src/app/globals.css:1-38` (root token block) and `:49-80` (`html.dark` block)

**Interfaces:**
- Produces: CSS custom properties consumed by every later task and every later phase — `--bg-page`, `--bg-surface`, `--border`, `--divider`, `--track`, `--border-strong`, `--text-primary`, `--text-secondary`, `--text-muted`, `--link`, `--link-hover`, `--success`, `--warning`, `--danger`, `--danger-bg`, `--navy`, `--navy-text`, `--sidebar-bg`, `--tint-success`, `--tint-warning`, `--tint-link`, `--tint-plum`, `--glass-bg`, `--glass-bg-elevated`, `--glass-bg-floating`, `--glass-border`, `--glass-highlight`, `--glass-shadow`, `--glass-hover`, `--glass-blur`.

- [ ] **Step 1: Add the new token block to `:root` in `src/app/globals.css`**

Insert immediately after the existing `--shadow-lg` line (end of the current `:root` block, before its closing `}`):

```css
  /* Fase de redesign glassmorphism (handoff design_handoff_printercontrol/).
     Tokens NOVOS, adicionados ao lado dos --color-* existentes — nao
     substituem nada ainda. Telas migradas passam a usar estes; telas nao
     migradas continuam com --color-* ate a fase delas. */
  --bg-page: #f6f3ee;
  --bg-surface: #fff;
  --border: #e7dfd2;
  --divider: #f2ede5;
  --track: #ece5da;
  --border-strong: #d8cdb9;
  --text-primary: #26211c;
  --text-secondary: #6f6459;
  --text-muted: #a79b8b;
  --link: #0a6a9c;
  --link-hover: #0098e0;
  --success: #3f8f5f;
  --warning: #c8862e;
  --danger: #c1503d;
  --danger-bg: #fbeae6;
  --navy: #0a4b6e;
  --navy-text: #0a4b6e;
  --sidebar-bg: #f3efe6;

  --tint-success: #eaf5ee;
  --tint-warning: #faf0dd;
  --tint-link: #eaf6fb;
  --tint-plum: #faf0dd;

  --glass-bg: rgba(255, 255, 255, 0.62);
  --glass-bg-elevated: rgba(255, 255, 255, 0.86);
  --glass-bg-floating: rgba(255, 255, 255, 0.94);
  --glass-border: rgba(20, 30, 45, 0.12);
  --glass-highlight: rgba(255, 255, 255, 0.45);
  --glass-shadow: 0 20px 50px -28px rgba(20, 30, 45, 0.22), inset 0 1px 0 rgba(255, 255, 255, 0.35);
  --glass-hover: rgba(20, 30, 45, 0.05);
  --glass-blur: blur(18px) saturate(140%);
```

- [ ] **Step 2: Add the dark-mode overrides to `html.dark` in `src/app/globals.css`**

Insert immediately after the existing `--color-info: ...` line inside the `html.dark { ... }` block (right before its closing `}`, check exact line with `--color-info` dark value first — it's around line 80-85):

```css
  --bg-page: #060607;
  --bg-surface: #101012;
  --border: #26272a;
  --divider: #1c1d1f;
  --track: #26272a;
  --border-strong: #3a3b3e;
  --text-primary: #f2f0ec;
  --text-secondary: #a8a5a0;
  --text-muted: #6f6c68;
  --link: #4ab3e8;
  --link-hover: #7cc9ef;
  --success: #5cb37f;
  --warning: #d9a34f;
  --danger: #e2776a;
  --danger-bg: #2a1b19;
  --navy: #123a54;
  --navy-text: #6fb8dd;
  --sidebar-bg: #000000;

  --tint-success: #10201a;
  --tint-warning: #221c10;
  --tint-link: #101c24;
  --tint-plum: rgba(104, 45, 86, 0.26);

  --glass-bg: rgba(20, 21, 23, 0.55);
  --glass-bg-elevated: rgba(16, 16, 18, 0.78);
  --glass-bg-floating: rgba(14, 14, 16, 0.9);
  --glass-border: rgba(255, 255, 255, 0.07);
  --glass-highlight: rgba(255, 255, 255, 0.05);
  --glass-shadow: 0 20px 55px -26px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.04);
  --glass-hover: rgba(255, 255, 255, 0.05);
  --glass-blur: blur(20px) saturate(130%);
```

- [ ] **Step 3: Verify — run the dev server and confirm no CSS errors**

Run: `npm run dev` (project root), open `http://127.0.0.1:3000`
Expected: app renders exactly as before (tokens are additive/unused so far — zero visual change). Check the browser console has no CSS parse warnings.

- [ ] **Step 4: Commit**

```bash
git add src/app/globals.css
git commit -m "feat: add glassmorphism design tokens (additive, unused yet)"
```

---

### Task 2: Aurora background

**Files:**
- Modify: `src/components/AppShell.tsx`
- Modify: `src/components/AppShell.module.css`

**Interfaces:**
- Consumes: `--link`, `--navy`, `--link-hover` tokens from Task 1.
- Produces: `.aurora` wrapper rendered once in `AppShell`, positioned behind the sidebar/content (z-index 0) — later phases rely on `.shell` having `position: relative` and each glass surface having `z-index: 1`+ to sit above it.

- [ ] **Step 1: Add aurora markup to `AppShell.tsx`**

In `src/components/AppShell.tsx`, insert as the first child inside the root `<div className={styles.shell}>` (i.e. immediately after line 38, before `<Sidebar`):

```tsx
      <div className={styles.aurora} aria-hidden="true">
        <div className={styles.auroraBlobA} />
        <div className={styles.auroraBlobB} />
        <div className={styles.auroraBlobC} />
      </div>

```

- [ ] **Step 2: Add aurora CSS to `AppShell.module.css`**

Change `.shell` (line 1) to add `position: relative; overflow: hidden;`:

```css
.shell {
  position: relative;
  overflow: hidden;
  display: flex;
  min-height: 100vh;
  background: var(--bg-page, var(--color-canvas));
}
```

Append at the end of the file:

```css
.aurora {
  position: fixed;
  inset: 0;
  z-index: 0;
  overflow: hidden;
  pointer-events: none;
}

.auroraBlobA,
.auroraBlobB,
.auroraBlobC {
  position: absolute;
  border-radius: 50%;
  filter: blur(10px);
}

.auroraBlobA {
  top: -14%;
  left: -8%;
  width: 48rem;
  height: 48rem;
  background: radial-gradient(circle, color-mix(in srgb, var(--link) 34%, transparent) 0%, transparent 70%);
}

.auroraBlobB {
  bottom: -20%;
  right: -10%;
  width: 50rem;
  height: 50rem;
  background: radial-gradient(circle, color-mix(in srgb, var(--navy) 30%, transparent) 0%, transparent 70%);
}

.auroraBlobC {
  top: 22%;
  right: 8%;
  width: 34rem;
  height: 34rem;
  background: radial-gradient(circle, color-mix(in srgb, var(--link-hover) 20%, transparent) 0%, transparent 70%);
}
```

- [ ] **Step 3: Give the shell's non-aurora children a stacking context above it**

Still in `AppShell.module.css`, add `position: relative; z-index: 1;` to `.main` (so Sidebar/Topbar/content render above the aurora once they get glass backgrounds in later tasks):

```css
.main {
  position: relative;
  z-index: 1;
  display: flex;
  min-height: 100vh;
  flex: 1;
  min-width: 0;
  flex-direction: column;
}
```

- [ ] **Step 4: Verify**

Run: `npm run dev`, open the dashboard.
Expected: three large soft blue-toned blurred circles visible behind the (still-opaque) sidebar/content, most visible near the page edges. Toggle dark mode (existing toggle in Topbar) — blobs should recolor via the dark token values from Task 1. No layout shift, no horizontal scrollbar introduced.

- [ ] **Step 5: Commit**

```bash
git add src/components/AppShell.tsx src/components/AppShell.module.css
git commit -m "feat: add aurora background layer to app shell"
```

---

### Task 3: Reusable PageHeader component

**Files:**
- Create: `src/components/PageHeader.tsx`
- Create: `src/components/PageHeader.module.css`

**Interfaces:**
- Consumes: nothing from earlier tasks besides tokens.
- Produces: `export default function PageHeader(props: PageHeaderProps)` with:
  ```ts
  interface PageHeaderProps {
    section: string;      // small uppercase crumb, e.g. "Monitoramento"
    title: string;        // e.g. "Dashboard"
    subtitle?: string;
    actions?: React.ReactNode; // right-aligned buttons/status, optional
  }
  ```
  Later phases (per-screen) import this and pass their own `actions` (e.g. "Exportar CSV" on Dashboard, "Sincronizar"/"Descobrir" on Rede) — not wired into any page in this task, just built and ready.

- [ ] **Step 1: Create `src/components/PageHeader.tsx`**

```tsx
import type { ReactNode } from "react";
import styles from "./PageHeader.module.css";

interface PageHeaderProps {
  section: string;
  title: string;
  subtitle?: string;
  actions?: ReactNode;
}

export default function PageHeader({ section, title, subtitle, actions }: PageHeaderProps) {
  return (
    <div className={styles.header}>
      <div className={styles.titleBlock}>
        <span className={styles.accentBar} aria-hidden="true" />
        <div>
          <div className={styles.crumb}>
            <span>{section}</span>
            <span className={styles.crumbSep}>/</span>
            <span className={styles.crumbCurrent}>{title}</span>
          </div>
          <h1 className={styles.title}>{title}</h1>
          {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
        </div>
      </div>
      {actions && <div className={styles.actions}>{actions}</div>}
    </div>
  );
}
```

- [ ] **Step 2: Create `src/components/PageHeader.module.css`**

```css
.header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 2rem;
  flex-wrap: wrap;
  border-bottom: 1px solid var(--border);
  padding: 2.25rem 0 1.5rem;
}

.titleBlock {
  display: flex;
  gap: 0.75rem;
}

.accentBar {
  width: 3px;
  border-radius: 2px;
  background: var(--link-hover);
  flex-shrink: 0;
}

.crumb {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-muted);
}

.crumbSep {
  color: var(--border-strong);
}

.crumbCurrent {
  color: var(--text-secondary);
}

.title {
  margin-top: 0.375rem;
  font-size: 1.375rem;
  font-weight: 700;
  letter-spacing: -0.015em;
  color: var(--text-primary);
}

.subtitle {
  margin-top: 0.25rem;
  font-size: 0.8125rem;
  color: var(--text-secondary);
}

.actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}
```

- [ ] **Step 3: Verify**

`PageHeader` isn't imported anywhere yet, so there's nothing to visually check — verify it type-checks and lints clean:

Run: `npx tsc --noEmit` (frontend project root)
Expected: no new errors from `PageHeader.tsx`.

- [ ] **Step 4: Commit**

```bash
git add src/components/PageHeader.tsx src/components/PageHeader.module.css
git commit -m "feat: add reusable PageHeader component (unwired, for later phases)"
```

---

### Task 4: Sidebar glass restyle

**Files:**
- Modify: `src/components/Sidebar.module.css`

**Interfaces:**
- Consumes: tokens from Task 1 (`--glass-bg-elevated`, `--glass-border`, `--glass-blur`, `--glass-shadow`, `--glass-hover`, `--tint-link`, `--link-hover`, `--text-*`).
- No TSX changes — `Sidebar.tsx` markup already matches the handoff structure (logo, two nav groups, network card, help button); only `.aside`/`.navItem*` CSS values change.

- [ ] **Step 1: Replace `.aside` in `Sidebar.module.css` (lines 15-26) with the glass recipe**

```css
.aside {
  position: fixed;
  z-index: 50;
  display: flex;
  height: 100vh;
  width: 248px;
  flex-shrink: 0;
  flex-direction: column;
  border-right: 1px solid var(--glass-border);
  background: var(--glass-bg-elevated);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  box-shadow: var(--glass-shadow);
  transition: transform 0.2s ease;
}
```

(Only `width` 272→248, `border-right`/`background`/`box-shadow` swapped for glass tokens, and two `backdrop-filter` lines added — everything else in the block stays.)

- [ ] **Step 2: Update nav item active/hover states (lines 122-149)**

Replace `.navItemActive`:

```css
.navItemActive {
  background: var(--tint-link);
  color: var(--link-hover);
  box-shadow: inset 2px 0 0 var(--link-hover);
}
```

Replace `.navItemInactive:hover`:

```css
.navItemInactive:hover {
  background: var(--glass-hover);
}
```

Update `.navIconActive` color to match (it currently hardcodes `#fff`, which was correct for the old solid-brand active background but is wrong against the new light tint background):

```css
.navIconActive {
  color: var(--link-hover);
  display: flex;
}
```

- [ ] **Step 3: Verify**

Run: `npm run dev`, open the dashboard, look at the sidebar.
Expected: sidebar reads as frosted glass (background blurs the aurora blobs behind it from Task 2), active nav item shows a light-blue tint background with a thin blue left rail (not a solid blue pill), hovering an inactive item shows a faint translucent highlight (not a flat opaque one). Toggle dark mode: sidebar becomes near-black glass, active tint still legible.

- [ ] **Step 4: Commit**

```bash
git add src/components/Sidebar.module.css
git commit -m "feat: restyle Sidebar with glassmorphism tokens"
```

---

### Task 5: Topbar glass restyle + header simplification

**Files:**
- Modify: `src/components/Topbar.tsx`
- Modify: `src/components/Topbar.module.css`

**Interfaces:**
- Consumes: tokens from Task 1.
- Behavior change: the "Olá, {firstName} / Aqui está o status..." greeting block is removed from the header — the handoff replaces it with the per-page breadcrumb+title pattern (`PageHeader`, Task 3), which gets wired into each screen during its own phase. Until a page adopts `PageHeader`, that page will temporarily have no title area — acceptable for this foundation phase since no screen phase has shipped yet.

- [ ] **Step 1: Remove the greeting block from `Topbar.tsx`**

Delete lines 67-70:

```tsx
      <div className={styles.greeting}>
        <h1 className={styles.greetingTitle}>Olá, {firstName}</h1>
        <p className={styles.greetingSubtitle}>Aqui está o status das impressoras da sua rede</p>
      </div>

```

`firstName` becomes unused in the component — also delete line 52 (`const firstName = ...`) since nothing else in the file references it. Confirm with a search before deleting: `grep -n "firstName" src/components/Topbar.tsx` should return only that declaration line after Step 1's markup deletion.

- [ ] **Step 2: Replace the avatar chip's initials box with the handoff's flat rounded-square style**

Locate the `.avatar` div (line 177, `<div className={styles.avatar}>{initials}</div>`) — no TSX change needed here, only the CSS in Step 4 (`.avatar` currently likely renders as a circle; handoff uses a 4px-radius square). Leave TSX as-is.

- [ ] **Step 3: Replace `.header` in `Topbar.module.css` with the glass recipe**

```css
.header {
  position: sticky;
  top: 0;
  z-index: 30;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  border-bottom: 1px solid var(--glass-border);
  background: var(--glass-bg-elevated);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  padding: 0 2.5rem;
  height: 60px;
}
```

- [ ] **Step 4: Update icon buttons, search box, and avatar to use the new tokens**

Replace `.iconButton` hover/base rule (find its current selector in the file) so hover uses `var(--divider)` (opaque header is fine here per README — header's own hover doesn't sit *inside* a translucent card, it's a direct child of the glass header, and the handoff itself uses `var(--divider)` for these, not `--glass-hover`):

```css
.iconButton {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  padding: 0.4375rem;
  color: var(--text-secondary);
  transition: background-color 0.12s ease-out;
}

.iconButton:hover {
  background: var(--divider);
}
```

Update `.searchBox` (border/background/focus):

```css
.searchBox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--bg-page);
  padding: 0.4375rem 0.625rem;
  width: 22rem;
  max-width: 32vw;
  color: var(--text-muted);
  transition: border-color 0.12s ease-out;
}

.searchBox:focus-within {
  border-color: var(--link-hover);
}
```

Update `.avatar` to the flat rounded-square from the handoff:

```css
.avatar {
  display: flex;
  height: 1.75rem;
  width: 1.75rem;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  background: var(--link);
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  color: var(--bg-surface);
}
```

- [ ] **Step 5: Verify**

Run: `npm run dev`.
Expected: header is a sticky frosted glass bar with search box + bell/theme/inbox icons + a small square blue avatar chip with initials, no greeting text. Every page currently has a blank gap where the greeting used to be — expected until per-screen phases add `PageHeader`. Search, notification dropdown, account menu, CSV export, discovery scan all still function (no logic touched).

- [ ] **Step 6: Commit**

```bash
git add src/components/Topbar.tsx src/components/Topbar.module.css
git commit -m "feat: restyle Topbar with glassmorphism tokens, drop greeting for PageHeader pattern"
```

---

### Task 6: Login screen token restyle

**Files:**
- Modify: `src/components/Login.module.css`

**Interfaces:**
- Consumes: a **separate, self-contained** token subset matching `Login v2.dc.html`'s own `:root`/`[data-theme="dark"]` block (the login screen intentionally has simpler tokens than the app shell — no glass, brand-navy hero panel fixed regardless of theme, per README "own token subset"). Do not reuse `--glass-*` tokens here.
- No TSX changes — `Login.tsx` structure (hero panel with `NetworkMap`, blobs, features, status card; form panel with card/inputs/error box) already matches the handoff 1:1.

- [ ] **Step 1: Read the current file to get exact class list before editing**

Run: `grep -n "^\." src/components/Login.module.css`

- [ ] **Step 2: Update color declarations to the handoff's Login-specific values**

For each of these existing rules in `Login.module.css`, replace hardcoded/old-token colors with the new light-mode values (add a `:global(html.dark)` override block, or extend the existing dark rules if the file already has a dark section — check Step 1's output first to match the file's existing selector convention for dark mode, e.g. `html.dark &` via CSS nesting or a duplicated dark class):

| Element (class) | Light | Dark |
|---|---|---|
| form panel background (`.formPanel`) | `#fff` | `#1e2124` |
| form panel page bg / `.page` | `#f6f3ee` | `#16181b` |
| borders (`.inputWrap`, `.card` if bordered) | `#e7dfd2` | `#34383c` |
| `.label`, primary text | `#26211c` | `#ece9e3` |
| `.cardSubtitle`, secondary text | `#6f6459` | `#a5a19a` |
| link/button brand (`.forgotLink`, `.submitButton` bg) | `#0a6a9c` / hover `#0098e0` | `#4ab3e8` / hover `#7cc9ef` |
| `.errorBox` accent | `#c1503d` | `#e2776a` |
| hero panel (`.heroPanel`) background | `#0a4b6e` (fixed, same in both themes per README) | `#0a4b6e` |

Apply these using the exact selectors already present in the file from Step 1 — this task does not restructure the CSS file, only swaps color values to match the table.

- [ ] **Step 3: Verify**

Run: `npm run dev`, navigate to the login screen (log out first, or open in an incognito window).
Expected: form panel colors match the handoff (warm off-white light background, near-black dark background), hero panel stays solid navy in both themes, submit button uses the new link-blue. Submit with wrong credentials — shake animation and error box still work (untouched logic). Toggle dark mode via the login's own theme button (top-right, existing) — only the form panel recolors, hero panel stays navy, matching README "brand navy panel is fixed regardless of theme".

- [ ] **Step 4: Commit**

```bash
git add src/components/Login.module.css
git commit -m "feat: restyle Login screen tokens to match glassmorphism handoff"
```

---

## Self-Review

**Spec coverage:** README sections "Design Tokens" (Task 1), "Background aurora" (Task 2), "Layout structure" sidebar+header (Tasks 4-5), "Theme toggle" (verified unchanged, no task needed — already attribute/class-based), Login screen (Task 6). Page-header "signature" detail (Task 3, built but unwired — first consumer is Phase 1/Dashboard). Screens 2-11 (Dashboard through Configurações), glass card recipe applied to content cards, status semantics, typography rule for all screens, and interaction rules for content (not just shell) are **out of scope** — each becomes its own phase plan, per the user's "mais usadas primeiro" ordering: Dashboard → Impressoras → Toner → Alertas → Relatórios → Histórico → Rede → Notificações → Usuários → Configurações → Integrações.

**Placeholder scan:** none found — every step has literal code.

**Type consistency:** `PageHeaderProps` (Task 3) is the only new exported interface; no other task references it yet, so nothing to cross-check until Phase 1 imports it.

---

## Roadmap (subsequent phases, planned individually before execution)

1. **Phase 1 — Dashboard**: vitals strip, fleet table + toner rail, 3-way analysis row; first consumer of `PageHeader`.
2. **Phase 2 — Impressoras**: filterable/searchable fleet table, status tabs, glass card recipe on table container.
3. **Phase 3 — Toner**: severity strip + supply table with per-channel bars.
4. **Phase 4 — Alertas**: severity-ordered list, tabs, colored left-rail rows.
5. **Phase 5 — Relatórios**: 6-month strip, department consumption, rankings sidebar, decommissioned table.
6. **Phase 6 — Histórico**: totals table + accordion site list.
7. **Phase 7 — Rede**: Print Server list/empty state, Sincronizar/Descobrir actions.
8. **Phase 8 — Notificações**: inbox pattern + context panel.
9. **Phase 9 — Usuários**: role tabs + table with inline error state.
10. **Phase 10 — Configurações**: stacked settings cards (Perfil, Senha, Aparência, Acessibilidade, Administração) — must preserve `--font-scale` accessibility control (Global Constraints).
11. **Phase 11 — Integrações**: minimal "in development" notice row.

Each phase plan should, per the Scope Check, stand alone as working/testable software — no phase depends on a later one, and the app is fully functional (old + new styling coexisting) after every single phase.
