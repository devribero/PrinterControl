/**
 * Regras da tela de Suprimentos, sem React: faixa de cada impressora, motivo
 * de "sem leitura", busca e ordenação. Separado dos componentes para que a
 * regra fique num lugar só e seja lida sem o JSX em volta.
 *
 * Limiares (≤10% crítico, ≤20% baixo) são os mesmos dos alertas de toner
 * (backend/app/services/alert_engine.py TONER_ALERT_THRESHOLD e
 * lib/deriveFromPrinters.ts): a contagem daqui precisa bater com o sino.
 */
import type { Printer, TonerLevel } from "../../types";
import { getPrinterType, type PrinterType } from "../../lib/printerType";

export const CRITICAL_MAX = 10;
export const LOW_MAX = 20;

export type TonerBand = "critical" | "low" | "ok" | "none";
export type SortKey = "level" | "name" | "department" | "server";

export interface TonerEntry {
  printer: Printer;
  band: TonerBand;
  /** Menor percentual entre os canais; null sem leitura. */
  worst: number | null;
  /** Explicação curta quando band === "none". */
  reason: string | null;
}

export function levelBand(percent: number): Exclude<TonerBand, "none"> {
  if (percent <= CRITICAL_MAX) return "critical";
  if (percent <= LOW_MAX) return "low";
  return "ok";
}

/** Tipo vindo do sync quando existe; senão, a mesma regex do resto do app. */
export function printerKind(p: Printer): PrinterType {
  if (p.printerType === "A4" || p.printerType === "Etiqueta" || p.printerType === "Portatil") return p.printerType;
  return getPrinterType(p);
}

function noReadingReason(p: Printer): string {
  if (p.status === "offline") return "Offline: não respondeu à última verificação.";
  // `lastSeenAt` só existe no dado real; undefined (demonstração) não quer dizer "nunca".
  if (p.lastSeenAt === null) return "Ainda não foi coletada.";
  return "Responde, mas não informa o nível (cartucho não original ou sem suporte SNMP).";
}

function hasReading(toner: TonerLevel[] | null): toner is TonerLevel[] {
  return !!toner && toner.length > 0;
}

export function toEntry(printer: Printer): TonerEntry {
  if (!hasReading(printer.toner)) {
    return { printer, band: "none", worst: null, reason: noReadingReason(printer) };
  }
  const worst = Math.min(...printer.toner.map((t) => t.percent));
  return { printer, band: levelBand(worst), worst, reason: null };
}

export function matchesQuery(p: Printer, q: string): boolean {
  if (!q) return true;
  return [p.name, p.ip, p.model, p.department].some((field) => field.toLowerCase().includes(q));
}

const collator = new Intl.Collator("pt-BR", { sensitivity: "base", numeric: true });

/** Sem leitura sempre por último na ordem por nível: não há o que comparar. */
function byLevel(a: TonerEntry, b: TonerEntry): number {
  if (a.worst === null && b.worst === null) return 0;
  if (a.worst === null) return 1;
  if (b.worst === null) return -1;
  return a.worst - b.worst;
}

export function sortEntries(entries: TonerEntry[], key: SortKey): TonerEntry[] {
  const byName = (a: TonerEntry, b: TonerEntry) => collator.compare(a.printer.name, b.printer.name);
  const compare: Record<SortKey, (a: TonerEntry, b: TonerEntry) => number> = {
    level: (a, b) => byLevel(a, b) || byName(a, b),
    name: byName,
    department: (a, b) => collator.compare(a.printer.department, b.printer.department) || byLevel(a, b) || byName(a, b),
    server: (a, b) => collator.compare(a.printer.server, b.printer.server) || byLevel(a, b) || byName(a, b),
  };
  return [...entries].sort(compare[key]);
}
