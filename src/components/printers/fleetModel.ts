/**
 * Regras da lista de impressoras (rota /printers), sem React: leitura e
 * escrita dos filtros na URL, busca, filtros e ordenação. Separado dos
 * componentes para que a regra fique num lugar só.
 *
 * A URL é a fonte da verdade dos filtros desta tela (link compartilhável):
 *   ?q=         busca (espelha a busca global da barra superior)
 *   ?status=    online | atencao | offline
 *   ?tipo=      a4 | etiqueta | portatil
 *   ?servidor=  host do Print Server; "-" = cadastradas à mão (sem servidor)
 *   ?toner=     baixo  → menor canal ≤ 20% (inclui o crítico)
 *   ?ordem=     nome | status | toner | leitura | departamento
 * Valor ausente ou inválido = padrão (sem filtro, ordem por nome).
 */
import type { Printer, PrinterStatus, TonerLevel } from "../../types";
import type { PrinterType } from "../../lib/printerType";
import { parseApiDate } from "../../lib/adaptApi";
import { LOW_MAX, printerKind } from "../toner/tonerModel";

export type SortKey = "nome" | "status" | "toner" | "leitura" | "departamento";

export interface FleetParams {
  q: string;
  status: PrinterStatus | null;
  tipo: PrinterType | null;
  /** Host do servidor; "" = sem servidor; null = todos. */
  servidor: string | null;
  tonerBaixo: boolean;
  ordem: SortKey;
}

export const DEFAULT_SORT: SortKey = "nome";

export const STATUS_LABEL: Record<PrinterStatus, string> = {
  online: "Online",
  atencao: "Atenção",
  offline: "Offline",
};

export const TYPE_LABEL: Record<PrinterType, string> = {
  A4: "A4",
  Etiqueta: "Etiqueta",
  Portatil: "Portátil",
};

export const SORT_LABEL: Record<SortKey, string> = {
  nome: "Nome",
  status: "Status (problemas primeiro)",
  toner: "Menor toner primeiro",
  leitura: "Leitura mais antiga primeiro",
  departamento: "Departamento",
};

const STATUSES: PrinterStatus[] = ["online", "atencao", "offline"];
const TYPE_BY_PARAM: Record<string, PrinterType> = { a4: "A4", etiqueta: "Etiqueta", portatil: "Portatil" };
const SORTS = Object.keys(SORT_LABEL) as SortKey[];
const SEM_SERVIDOR = "-";
const KEYS = ["q", "status", "tipo", "servidor", "toner", "ordem"] as const;

interface ReadableParams {
  get(name: string): string | null;
}

export function parseFleetParams(sp: ReadableParams): FleetParams {
  const status = sp.get("status");
  const tipo = sp.get("tipo");
  const servidor = sp.get("servidor");
  const ordem = sp.get("ordem");
  return {
    q: sp.get("q") ?? "",
    status: STATUSES.includes(status as PrinterStatus) ? (status as PrinterStatus) : null,
    tipo: (tipo && TYPE_BY_PARAM[tipo]) || null,
    servidor: servidor === null || servidor === "" ? null : servidor === SEM_SERVIDOR ? "" : servidor,
    tonerBaixo: sp.get("toner") === "baixo",
    ordem: SORTS.includes(ordem as SortKey) ? (ordem as SortKey) : DEFAULT_SORT,
  };
}

/** Query string com só o que difere do padrão; preserva parâmetros alheios. */
export function serializeFleetParams(params: FleetParams, current: string): string {
  const out = new URLSearchParams(current);
  for (const k of KEYS) out.delete(k);
  const q = params.q.trim();
  if (q) out.set("q", q);
  if (params.status) out.set("status", params.status);
  if (params.tipo) out.set("tipo", params.tipo.toLowerCase());
  if (params.servidor !== null) out.set("servidor", params.servidor === "" ? SEM_SERVIDOR : params.servidor);
  if (params.tonerBaixo) out.set("toner", "baixo");
  if (params.ordem !== DEFAULT_SORT) out.set("ordem", params.ordem);
  return out.toString();
}

/** Algum filtro que reduz a lista (a ordem não conta). */
export function hasActiveFilters(p: FleetParams): boolean {
  return p.q.trim() !== "" || p.status !== null || p.tipo !== null || p.servidor !== null || p.tonerBaixo;
}

/** Canal mais baixo: é ele que decide a troca. */
export function lowestToner(p: Pick<Printer, "toner">): TonerLevel | null {
  if (!p.toner || p.toner.length === 0) return null;
  return p.toner.reduce((min, t) => (t.percent < min.percent ? t : min));
}

/**
 * Busca por nome, IP, modelo, departamento, servidor e compartilhamento.
 * Número de série não entra: o cadastro não o coleta (ver
 * DecommissionedPrinter em types.ts).
 */
export function matchesQuery(p: Printer, q: string): boolean {
  if (!q) return true;
  return [p.name, p.ip, p.model, p.department, p.server, p.shareName ?? ""].some((f) => f.toLowerCase().includes(q));
}

/**
 * Aplica os filtros. `servidor` só vale se existir na frota do escopo atual
 * (`serverHosts`): trocar o escopo no seletor global não deve deixar a lista
 * vazia por causa de um servidor que nem aparece mais nas opções.
 */
export function filterFleet(printers: Printer[], p: FleetParams, serverHosts: Set<string>): Printer[] {
  const q = p.q.trim().toLowerCase();
  const servidor = p.servidor !== null && serverHosts.has(p.servidor) ? p.servidor : null;
  return printers.filter((printer) => {
    if (p.status && printer.status !== p.status) return false;
    if (p.tipo && printerKind(printer) !== p.tipo) return false;
    if (servidor !== null && printer.server !== servidor) return false;
    if (p.tonerBaixo) {
      const worst = lowestToner(printer);
      if (!worst || worst.percent > LOW_MAX) return false;
    }
    return matchesQuery(printer, q);
  });
}

/**
 * "agora", "há 12 min", "há 3 h", "há 2 dias" em relação a `now` (a última
 * coleta, não o relógio — mantém o render puro). Sem instante cru (dado de
 * demonstração), usa o texto pronto `lastSeen`.
 */
export function relativeReading(p: Printer, now: Date): string {
  if (p.lastSeenAt === null) return "Nunca coletada";
  const date = parseApiDate(p.lastSeenAt);
  if (!date) return p.lastSeen || "—";
  const min = Math.max(0, Math.floor((now.getTime() - date.getTime()) / 60000));
  if (min < 1) return "agora";
  if (min < 60) return `há ${min} min`;
  if (min < 24 * 60) return `há ${Math.floor(min / 60)} h`;
  const days = Math.floor(min / (24 * 60));
  return days === 1 ? "há 1 dia" : `há ${days} dias`;
}

/** Data/hora absoluta da leitura, para o title da célula. */
export function absoluteReading(p: Printer): string | undefined {
  const date = parseApiDate(p.lastSeenAt);
  return date
    ? date.toLocaleString("pt-BR", { day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit" })
    : undefined;
}

const collator = new Intl.Collator("pt-BR", { sensitivity: "base", numeric: true });
const STATUS_RANK: Record<PrinterStatus, number> = { offline: 0, atencao: 1, online: 2 };

/**
 * Instante da última leitura. `null` explícito = nunca coletada, a leitura
 * "mais antiga" possível; `undefined` (demonstração) = não se sabe.
 */
function readingTime(p: Printer): number | null {
  if (p.lastSeenAt === null) return Number.MIN_SAFE_INTEGER;
  return parseApiDate(p.lastSeenAt)?.getTime() ?? null;
}

/** Nulos (sem leitura/sem toner) sempre por último: não há o que comparar. */
function nullsLast(a: number | null, b: number | null): number {
  if (a === null && b === null) return 0;
  if (a === null) return 1;
  if (b === null) return -1;
  return a - b;
}

export function sortFleet(printers: Printer[], key: SortKey): Printer[] {
  const byName = (a: Printer, b: Printer) => collator.compare(a.name, b.name);
  const compare: Record<SortKey, (a: Printer, b: Printer) => number> = {
    nome: byName,
    status: (a, b) => STATUS_RANK[a.status] - STATUS_RANK[b.status] || byName(a, b),
    toner: (a, b) => nullsLast(lowestToner(a)?.percent ?? null, lowestToner(b)?.percent ?? null) || byName(a, b),
    leitura: (a, b) => nullsLast(readingTime(a), readingTime(b)) || byName(a, b),
    departamento: (a, b) => collator.compare(a.department, b.department) || byName(a, b),
  };
  return [...printers].sort(compare[key]);
}
