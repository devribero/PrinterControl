/**
 * Modelo da tela de Relatórios — funções puras, sem React.
 *
 * Duas fontes, uma regra:
 *
 * - `monthlyUsage` (GET /api/printers/monthly-report → monthly_usage) é o
 *   total OFICIAL por mês da frota inteira, com `estimated`, `inProgress` e
 *   `devices`. Não conhece escopo: é sempre "todos os servidores".
 * - `printers[].monthlyPages` já vem filtrado pelo escopo global
 *   (ServerSwitcher, ver `printers` em lib/app-data.tsx).
 *
 * Sem escopo, os totais mensais vêm de `monthlyUsage` (o mesmo número do
 * painel). Com escopo, são somados das impressoras do escopo — e aí a parte
 * estimada não é conhecida (o backend só a informa agregada), então fica
 * `null` e a tela diz isso em vez de mostrar zero.
 *
 * Ranking e quebra por departamento/unidade saem sempre das impressoras, que
 * é a única fonte com essa granularidade.
 */
import type { MonthlyPageCount, MonthlyUsageEntry, Printer } from "../../types";

/**
 * Primeiro mês de coleta automática (SNMP). Os meses anteriores vieram da
 * importação da planilha histórica (backend/import_historico_planilha.py).
 */
export const SNMP_START_PERIOD = "2026-09";

const PERIOD_RE = /^(\d{4})-(\d{2})$/;
const MONTHS_SHORT = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];

/** Separador de "Departamento — Unidade" no cadastro. */
const DEPT_UNIT_SEPARATOR = " — ";

export const NO_DEPARTMENT = "Sem departamento";
export const NO_UNIT = "Unidade não informada";

export interface ReportMonth {
  period: string;
  /** Rótulo curto do eixo ("Ago"). */
  label: string;
  /** Rótulo com ano quando o período permite ("ago/2026"). */
  longLabel: string;
  pages: number;
  /** Parte estimada de `pages`; null = desconhecida (visão com escopo). */
  estimated: number | null;
  inProgress: boolean;
  /** Equipamentos com dado no mês. */
  devices: number;
  /** "planilha" | "snmp" quando o período é "AAAA-MM"; null no conjunto de demonstração. */
  source: "planilha" | "snmp" | null;
}

export interface PrinterRow {
  printer: Printer;
  department: string;
  unit: string;
  /** Páginas por período — já sem os meses copiados de cadastro inativo. */
  byPeriod: Map<string, number>;
}

export interface ReportData {
  months: ReportMonth[];
  rows: PrinterRow[];
  /** True quando os totais foram somados das impressoras do escopo. */
  scoped: boolean;
}

export type PeriodSelection = { kind: "last"; count: number } | { kind: "month"; period: string };

export const LAST_OPTIONS = [3, 6, 12] as const;

export function monthLongLabel(period: string, fallback: string): string {
  const m = PERIOD_RE.exec(period);
  if (!m) return fallback;
  return `${MONTHS_SHORT[Number(m[2]) - 1] ?? fallback}/${m[1]}`;
}

function monthSource(period: string): ReportMonth["source"] {
  if (!PERIOD_RE.test(period)) return null;
  return period >= SNMP_START_PERIOD ? "snmp" : "planilha";
}

/** "TI — Manaus" → { department: "TI", unit: "Manaus" }. */
export function splitDepartment(raw: string): { department: string; unit: string } {
  const text = raw.trim();
  if (!text) return { department: NO_DEPARTMENT, unit: NO_UNIT };
  const idx = text.lastIndexOf(DEPT_UNIT_SEPARATOR);
  if (idx === -1) return { department: text, unit: NO_UNIT };
  const department = text.slice(0, idx).trim() || NO_DEPARTMENT;
  const unit = text.slice(idx + DEPT_UNIT_SEPARATOR.length).trim() || NO_UNIT;
  return { department, unit };
}

/**
 * Linhas por impressora, sem contar mês duas vezes.
 *
 * O backend copia para a impressora ATIVA os meses do cadastro INATIVO do
 * mesmo equipamento (mudou de IP; mesmo número de série). A cópia é idêntica
 * — mesmo período, mesmas páginas —, então somar as duas filas dobraria o
 * mês. Aqui o mês fica com a ativa (é ela que o usuário reconhece) e sai da
 * inativa.
 */
function buildRows(printers: Printer[]): PrinterRow[] {
  const withData = printers.filter((p) => p.monthlyPages && p.monthlyPages.length > 0);
  const activeKeys = new Set<string>();
  for (const p of withData) {
    if (!p.active) continue;
    for (const m of p.monthlyPages as MonthlyPageCount[]) activeKeys.add(`${m.period}|${m.pages}`);
  }

  const rows: PrinterRow[] = [];
  for (const p of withData) {
    const byPeriod = new Map<string, number>();
    for (const m of p.monthlyPages as MonthlyPageCount[]) {
      if (!p.active && activeKeys.has(`${m.period}|${m.pages}`)) continue;
      byPeriod.set(m.period, (byPeriod.get(m.period) ?? 0) + m.pages);
    }
    if (byPeriod.size === 0) continue;
    rows.push({ printer: p, ...splitDepartment(p.department), byPeriod });
  }
  return rows;
}

export function buildReport(printers: Printer[], monthlyUsage: MonthlyUsageEntry[], scoped: boolean): ReportData {
  const rows = buildRows(printers);

  const derived = new Map<string, { pages: number; devices: number; label: string }>();
  for (const r of rows) {
    for (const m of r.printer.monthlyPages ?? []) {
      if (!r.byPeriod.has(m.period) || derived.has(m.period)) continue;
      derived.set(m.period, { pages: 0, devices: 0, label: m.month });
    }
    for (const [period, pages] of r.byPeriod) {
      const cur = derived.get(period)!;
      cur.pages += pages;
      cur.devices += 1;
    }
  }

  const official = new Map(monthlyUsage.map((m) => [m.period, m]));
  // Ordem: a do relatório oficial (o backend ordena por período); períodos
  // que só as impressoras conhecem entram depois, em ordem de texto.
  const order = monthlyUsage.map((m) => m.period);
  for (const period of [...derived.keys()].sort()) if (!official.has(period)) order.push(period);

  const months: ReportMonth[] = [];
  for (const period of order) {
    const off = official.get(period);
    const der = derived.get(period);
    const label = off?.month ?? der?.label ?? period;
    const inProgress = off?.inProgress === true;
    if (scoped) {
      if (!der) continue;
      months.push({
        period,
        label,
        longLabel: monthLongLabel(period, label),
        pages: der.pages,
        estimated: null,
        inProgress,
        devices: der.devices,
        source: monthSource(period),
      });
    } else if (off) {
      months.push({
        period,
        label,
        longLabel: monthLongLabel(period, label),
        pages: off.pages,
        estimated: off.estimated ?? null,
        inProgress,
        devices: off.devices ?? der?.devices ?? 0,
        source: monthSource(period),
      });
    }
  }

  return { months, rows, scoped };
}

/** Períodos selecionados, em ordem cronológica. */
export function selectPeriods(months: ReportMonth[], sel: PeriodSelection): ReportMonth[] {
  if (months.length === 0) return [];
  if (sel.kind === "month") {
    const found = months.find((m) => m.period === sel.period);
    return found ? [found] : [months[months.length - 1]];
  }
  return months.slice(-sel.count);
}

export function selectionLabel(selected: ReportMonth[]): string {
  if (selected.length === 0) return "—";
  if (selected.length === 1) return selected[0].longLabel;
  return `${selected[0].longLabel} a ${selected[selected.length - 1].longLabel}`;
}

/* ── KPIs ───────────────────────────────────────────────────────────────── */

export interface ReportKpis {
  total: number;
  /** Soma das partes estimadas; null quando alguma é desconhecida. */
  estimated: number | null;
  inProgressMonth: ReportMonth | null;
  /** Média dos meses FECHADOS do período; null se não há mês fechado. */
  average: number | null;
  closedCount: number;
  variation: {
    current: ReportMonth;
    previous: ReportMonth;
    pct: number;
    /** Variação de páginas por equipamento — só quando a cobertura difere. */
    perDevicePct: number | null;
  } | null;
  /** Motivo de não haver variação, para a tela explicar. */
  variationMissing: string | null;
  devicesLast: number;
  devicesMin: number;
  devicesMax: number;
}

export function computeKpis(all: ReportMonth[], selected: ReportMonth[]): ReportKpis {
  const total = selected.reduce((s, m) => s + m.pages, 0);
  const estimated = selected.some((m) => m.estimated === null)
    ? null
    : selected.reduce((s, m) => s + (m.estimated ?? 0), 0);
  const closed = selected.filter((m) => !m.inProgress);
  const average = closed.length > 0 ? closed.reduce((s, m) => s + m.pages, 0) / closed.length : null;

  let variation: ReportKpis["variation"] = null;
  let variationMissing: string | null = null;
  const current = closed[closed.length - 1];
  if (!current) {
    variationMissing = `${selected[0]?.longLabel ?? "O mês"} ainda está em andamento.`;
  } else {
    const idx = all.findIndex((m) => m.period === current.period);
    const previous = idx > 0 ? all[idx - 1] : undefined;
    if (!previous || previous.pages === 0) {
      variationMissing = "Sem mês anterior para comparar.";
    } else {
      const pct = ((current.pages - previous.pages) / previous.pages) * 100;
      let perDevicePct: number | null = null;
      if (current.devices > 0 && previous.devices > 0 && current.devices !== previous.devices) {
        const a = current.pages / current.devices;
        const b = previous.pages / previous.devices;
        perDevicePct = b > 0 ? ((a - b) / b) * 100 : null;
      }
      variation = { current, previous, pct, perDevicePct };
    }
  }

  const devices = selected.map((m) => m.devices);
  return {
    total,
    estimated,
    inProgressMonth: selected.find((m) => m.inProgress) ?? null,
    average,
    closedCount: closed.length,
    variation,
    variationMissing,
    devicesLast: devices[devices.length - 1] ?? 0,
    devicesMin: devices.length ? Math.min(...devices) : 0,
    devicesMax: devices.length ? Math.max(...devices) : 0,
  };
}

/* ── Ranking e quebras ──────────────────────────────────────────────────── */

export interface RankedRow extends PrinterRow {
  total: number;
}

/** Impressoras com dado em algum dos períodos, da que mais imprimiu à que menos. */
export function rankRows(rows: PrinterRow[], periods: string[]): RankedRow[] {
  const ranked: RankedRow[] = [];
  for (const r of rows) {
    let total = 0;
    let has = false;
    for (const p of periods) {
      const v = r.byPeriod.get(p);
      if (v === undefined) continue;
      has = true;
      total += v;
    }
    if (has) ranked.push({ ...r, total });
  }
  return ranked.sort((a, b) => b.total - a.total || a.printer.name.localeCompare(b.printer.name, "pt-BR"));
}

export interface BreakdownItem {
  key: string;
  total: number;
  devices: number;
}

export function breakdown(ranked: RankedRow[], by: "department" | "unit"): BreakdownItem[] {
  const map = new Map<string, BreakdownItem>();
  for (const r of ranked) {
    const key = r[by];
    const item = map.get(key) ?? { key, total: 0, devices: 0 };
    item.total += r.total;
    item.devices += 1;
    map.set(key, item);
  }
  return [...map.values()].sort((a, b) => b.total - a.total || a.key.localeCompare(b.key, "pt-BR"));
}

/* ── Formatação ─────────────────────────────────────────────────────────── */

const intFmt = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 0 });
const compactFmt = new Intl.NumberFormat("pt-BR", { notation: "compact", maximumFractionDigits: 1 });

export function formatInt(n: number): string {
  return intFmt.format(Math.round(n));
}

export function formatCompact(n: number): string {
  return compactFmt.format(n);
}

export function formatPct(n: number, signed = false): string {
  const s = n.toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
  return signed && n > 0 ? `+${s}%` : `${s}%`;
}
