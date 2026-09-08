# Handoff: PrinterControl — Glassmorphism UI System

## Overview
Corporate print-fleet management dashboard (11 screens) for Elgin. Redesigned from a generic AI-dashboard look into a professional, minimalist "glassmorphism" system with full light/dark theming.

## About the Design Files
The files in this bundle are **design references built in HTML** (a Design Component runtime with templating) — they show final visual intent, structure, and interaction behavior. They are **not production code to copy verbatim**. Recreate this design in the target codebase's existing stack (React, Vue, etc.) using its own component/state patterns, following the structure, tokens, and behavior documented below.

## Fidelity
**High-fidelity.** Exact colors, spacing, typography, and interaction states are final. Recreate pixel-close using the target codebase's component library, mapping the CSS variables below into its existing token system (or introducing them if none exists).

## Design Tokens (critical — read this first)

Everything is driven by CSS custom properties on `:root` and overridden under `[data-theme="dark"]`. **Never hardcode a hex color in a component** — always reference the token, or the light/dark toggle breaks (this was an actual bug found and fixed during the session: a direct color edit landed as a hardcoded hex and stopped adapting to theme).

### Base tokens
| Token | Light | Dark | Use |
|---|---|---|---|
| `--bg-page` | `#f6f3ee` | `#060607` | page background |
| `--bg-surface` | `#fff` | `#101012` | opaque surfaces (inputs, opaque panels) |
| `--bg-header` | `rgba(255,255,255,.92)` | `rgba(9,9,10,.92)` | (legacy, mostly superseded by glass tokens) |
| `--border` | `#e7dfd2` | `#26272a` | standard 1px borders |
| `--divider` | `#f2ede5` | `#1c1d1f` | row/list dividers |
| `--track` | `#ece5da` | `#26272a` | progress-bar track background |
| `--border-strong` | `#d8cdb9` | `#3a3b3e` | hover border emphasis |
| `--text-primary` | `#26211c` | `#f2f0ec` | primary text |
| `--text-secondary` | `#6f6459` | `#a8a5a0` | secondary text |
| `--text-muted` | `#a79b8b` | `#6f6c68` | tertiary/meta text |
| `--link` / `--link-hover` | `#0a6a9c` / `#0098e0` | `#4ab3e8` / `#7cc9ef` | links, active/interactive accents |
| `--success` / `--warning` / `--danger` | `#3f8f5f` / `#c8862e` / `#c1503d` | `#5cb37f` / `#d9a34f` / `#e2776a` | status semantics |
| `--danger-bg` | `#fbeae6` | `#2a1b19` | danger chip/pill background |
| `--navy` | `#0a4b6e` | `#123a54` | brand navy, used only for background tints (via `color-mix`) |
| `--navy-text` | `#0a4b6e` | `#6fb8dd` | brand navy as **readable text/label** color (separate from `--navy` because navy-as-background needs a lighter text variant in dark mode) |
| `--sidebar-bg` | `#f3efe6` | `#000000` | sidebar surface tint — dark mode sidebar is true black |

### Tint tokens (soft colored surfaces — "color as meaning", not decoration)
| Token | Light | Dark |
|---|---|---|
| `--tint-success` | `#eaf5ee` | `#10201a` |
| `--tint-warning` | `#faf0dd` | `#221c10` |
| `--tint-link` | `#eaf6fb` | `#101c24` |
| `--tint-plum` | `#faf0dd` (yellowed to match warning per latest request) | `rgba(104,45,86,0.26)` (plum/wine, preserves a specific brand-adjacent accent color from a direct edit) |

`--tint-plum` is a special case worth explaining to the implementer: it started life as a one-off hardcoded color (`#682D5641`) from a manual color edit on two specific components (the Dashboard's "Mais urgente agora" alert strip and "Reposição urgente" card). The user wanted that *specific* hue kept, but theme-adaptive — so it became a token with **different light/dark values by design** (light reuses the warning-yellow tint; dark keeps the original plum hue at higher opacity for visibility against near-black). Don't unify it with `--tint-warning` — keep it a separate token in case the two are asked to diverge again.

### Glassmorphism tokens
| Token | Light | Dark |
|---|---|---|
| `--glass-bg` | `rgba(255,255,255,0.62)` | `rgba(20,21,23,0.55)` |
| `--glass-bg-elevated` | `rgba(255,255,255,0.86)` | `rgba(16,16,18,0.78)` |
| `--glass-bg-floating` | `rgba(255,255,255,0.94)` | `rgba(14,14,16,0.9)` |
| `--glass-border` | `rgba(20,30,45,0.12)` | `rgba(255,255,255,0.07)` |
| `--glass-highlight` | `rgba(255,255,255,0.45)` | `rgba(255,255,255,0.05)` |
| `--glass-shadow` | `0 20px 50px -28px rgba(20,30,45,0.22), inset 0 1px 0 rgba(255,255,255,0.35)` | `0 20px 55px -26px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.04)` |
| `--glass-hover` | `rgba(20,30,45,0.05)` | `rgba(255,255,255,0.05)` |
| `--glass-blur` | `blur(18px) saturate(140%)` | `blur(20px) saturate(130%)` |

**Glass levels** (apply consistently, don't invent a 4th):
1. **Glass Base** (`--glass-bg`) — rarely used standalone; mostly a fallback/base layer.
2. **Glass Elevated** (`--glass-bg-elevated` + `--glass-border` + `--glass-blur` + `--glass-shadow`) — the standard treatment for **every card/panel/table container** in the app (sidebar, header, and all ~23 content cards use this exact recipe).
3. **Glass Floating** (`--glass-bg-floating`) — reserved for modals/menus/floating overlays (not yet built in this prototype, but the token exists and should be used when those are implemented — more opaque than Elevated for legibility over arbitrary content).

**Standard glass card recipe** (copy this combination exactly, it's used ~23 times identically):
```css
border: 1px solid var(--glass-border);
border-radius: 14px;
background: var(--glass-bg-elevated);
backdrop-filter: var(--glass-blur);
-webkit-backdrop-filter: var(--glass-blur);
box-shadow: var(--glass-shadow);
```

**Important gotcha already fixed once — don't reintroduce it:** any `:hover` state on a row/button *inside* a glass card must use `--glass-hover` (translucent), never `--bg-page` or any opaque background token. An opaque hover background inside a translucent glass parent renders as a jarring solid patch that "cuts through" the glass effect. This was found as a real bug across 11 hover states (table rows, nav items, quick actions, department rows, etc.) and fixed by introducing `--glass-hover`.

## Background aurora
Behind everything (`position:fixed; inset:0; z-index:0`) sit 3 large soft radial-gradient blobs (blue-toned: `--link`, `--navy`, `--link-hover` mixed via `color-mix()` at 20-34% into transparent, `filter:blur(10px)`, `pointer-events:none`). Purpose: give the glass surfaces something to visually refract — without this, backdrop-filter has nothing "behind" it to blur and the glass effect is invisible on a flat page background. Keep these subtle and blue — an earlier version used blue/green/amber and was changed to all-blue per explicit direction.

## Layout structure (applies to every screen)
- **Sidebar**: fixed 248px, `position:sticky; top:0; height:100vh`, glass-elevated treatment, brand logo + two nav groups ("Monitoramento", "Administração"). Active nav item gets `background: var(--tint-link)` (not the neutral divider color — color is used for orientation, not decoration) plus a `box-shadow: inset 2px 0 0 var(--link-hover)` left rail.
- **Header**: `position:sticky; top:0; z-index:30; height:60px`, glass-elevated, contains global search, notification bell, theme toggle (moon/sun icon button), inbox icon, user menu.
- **Page header** (per-screen, not sticky): breadcrumb (`crumbSection / pageTitle`) + `<h1>` + subtitle, with a small vertical accent bar (`3px`, `var(--link-hover)`) to the left of the title block — a deliberate "signature" detail requested during a "give it personality" round.
- **Main content**: everything below page header uses the standard glass card recipe for every distinct panel (tables, KPI clusters, sidebars-within-content, etc). Grids are typically `minmax(0,1fr) <fixed-px>` (content + narrow context rail) or `1.6fr 1fr 1fr` (dominant chart + two narrower stat cards) — deliberately asymmetric, not a uniform card grid.

## Theme toggle
- State: `theme: "light" | "dark"`, persisted to `localStorage` under key `pc-theme`, read on mount with a `light` fallback.
- Applied via `data-theme="{{ theme }}"` attribute on the outermost layout `<div>` — **all theming is attribute-scoped CSS variable overrides**, no class-swapping, no JS-computed colors.
- Toggle button renders a `moon` icon in light mode / `sun` icon in dark mode (lucide icon names), positioned in the header (Dashboard-style pages) or as an absolutely-positioned button top-right of the form panel (Login page, which has its own simpler token subset — no glass/aurora treatment, brand navy panel is fixed regardless of theme).

## Status semantics (used identically across Dashboard/Impressoras/Toner tables)
- **Online**: `--success` dot with a `soft-pulse 3s ease-in-out infinite` CSS animation (subtle breathing opacity/scale, defined once in a shared `@keyframes` block) — the only place continuous animation is used.
- **Offline**: `--text-muted` dot, no animation, no colored pill background.
- **Atenção** (warning/needs-attention): `--warning` dot **and** a pill background of `--tint-warning` — the one status that gets a colored surface, reinforcing it needs action.

## Typography
- Font: "Public Sans" for UI text; `'IBM Plex Mono', monospace` for **all numeric values** (counts, percentages, IPs, currency-like figures) — this is a strict rule applied everywhere for alignment/scanability, not just decoration.
- Headings: 600-700 weight max (the redesign explicitly walked back 800-weight/oversized type from an earlier "generic AI dashboard" version).

## Interaction/animation rules
- All hover/focus transitions: `transition: background-color 0.12s ease-out` (or `border-color`/`color` alongside) — short, subtle, color/border only. No transform/scale hover effects, no shadow-pop.
- No animation library — plain CSS transitions and one shared `@keyframes soft-pulse`.

## Screens
1. **Login** (separate file, `Login v2.dc.html`) — solid navy brand panel (fixed, non-themed) + light form panel with theme toggle. Success on password `elgin`; error otherwise with a single 360ms shake per attempt. Collapses to single column under 940px.
2. **Dashboard** — vitals strip (fleet total / online / attention / offline / top-alert, single glass-free tinted strip with navy-tinted background via `color-mix`) → fleet table + toner/quick-actions rail → 3-way analysis row (pages chart / total impressions / fleet health).
3. **Impressoras** — filterable/searchable fleet table with status tabs.
4. **Toner** — inline severity strip ("precisam de intervenção agora") + full supply table with per-channel bars.
5. **Alertas** — severity-ordered list, critical/warning tabs with tinted counts, colored left-rail per row.
6. **Relatórios** — inline 6-month strip (current month highlighted with `--tint-link`) + department consumption list (dominant) + rankings sidebar + decommissioned-printers table.
7. **Histórico** — page-header total, then a totals table, then an accordion list of sites (expand/collapse per site).
8. **Rede** — Print Server list/empty-state + Sincronizar (primary, writes to DB) / Descobrir (secondary, read-only) actions.
9. **Notificações** — personal inbox pattern (empty state) + a context panel explaining scope vs. Alertas.
10. **Integrações** — single inline "in development" notice row (deliberately minimal, not a big centered hero).
11. **Usuários** — role-filter tabs (Todos/Administradores/Operadores/Inativos) + user table with backend-error state built into the table header area (not a separate banner).
12. **Configurações** — stacked settings sections (Perfil, Senha, Aparência, Acessibilidade, Administração), each its own glass card.

## Files
- `PrinterControl v2.dc.html` — main app, all 11 screens, nav, theming, data mocks.
- `Login v2.dc.html` — login screen, own token subset.
- `data/printers.js` — mock printer fleet dataset consumed via `window.PRINTER_DATA`.
- `assets/logo-elgin.webp` — brand logo.

Reference `PrinterControl.dc.html` (the pre-redesign v1) only if you need to see "before" state for comparison — do not build from it.
