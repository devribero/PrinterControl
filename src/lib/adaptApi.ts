/**
 * Traducao entre os contratos do backend (snake_case, ids numericos) e os
 * tipos que a UI ja consumia (src/types.ts). Fica isolado aqui para que
 * nenhum componente precise conhecer o formato da API.
 */
import {
  api,
  type ApiAlert,
  type ApiPrintServer,
  type ApiPrinterWithStatus,
  type ApiSyncResult,
  type ApiTonerLevel,
} from "./api";
import type { Alert, MonthlyReport, Printer, PrintServer, PrinterStatus, SyncResult, TonerLevel } from "../types";

const VALID_STATUS: PrinterStatus[] = ["online", "offline", "atencao"];
const VALID_COLORS = ["K", "C", "M", "Y"] as const;

function toStatus(value: string): PrinterStatus {
  return (VALID_STATUS as string[]).includes(value) ? (value as PrinterStatus) : "offline";
}

function toToner(levels: ApiTonerLevel[] | null): TonerLevel[] | null {
  if (!levels || levels.length === 0) return null;
  const mapped = levels
    .filter((t): t is ApiTonerLevel & { color: TonerLevel["color"] } =>
      (VALID_COLORS as readonly string[]).includes(t.color),
    )
    .map((t) => ({ color: t.color, label: t.label, percent: t.percent }));
  return mapped.length > 0 ? mapped : null;
}

/** "agora", "há 12 min", "há 3 h", "12/08 14:30" — mesmo tom dos dados de demo. */
export function formatLastSeen(iso: string | null): string {
  if (!iso) return "Nunca coletada";

  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "Desconhecido";

  const minutes = Math.floor((Date.now() - date.getTime()) / 60000);
  if (minutes < 1) return "agora";
  if (minutes < 60) return `há ${minutes} min`;
  if (minutes < 24 * 60) return `há ${Math.floor(minutes / 60)} h`;

  return date.toLocaleString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function adaptPrinter(p: ApiPrinterWithStatus): Printer {
  return {
    id: String(p.id),
    name: p.name,
    ip: p.ip,
    model: p.model,
    department: p.department,
    server: p.server ?? "",
    active: p.active !== false,
    status: toStatus(p.status),
    toner: toToner(p.toner),
    pagesPrinted: p.page_count ?? 0,
    lastSeen: formatLastSeen(p.last_seen),
  };
}

export function adaptPrintServer(s: ApiPrintServer): PrintServer {
  return {
    id: s.id,
    host: s.host,
    name: s.name || s.host,
    mode: s.mode,
    active: s.active,
    lastStatus: s.last_status,
    lastError: s.last_error,
    lastSeenAt: s.last_seen_at,
    lastSyncAt: s.last_sync_at,
    printerCount: s.printer_count,
    activePrinterCount: s.active_printer_count,
    isDefault: s.is_default,
  };
}

export function adaptSyncResult(r: ApiSyncResult): SyncResult {
  return { ...r };
}

export function adaptAlert(a: ApiAlert): Alert {
  const severity: Alert["severity"] =
    a.severity === "critical" || a.severity === "warning" ? a.severity : "info";

  return {
    id: String(a.id),
    severity,
    message: a.message,
    printerId: String(a.printer_id),
    timestamp: a.created_at,
  };
}

/* ── Relatório mensal ────────────────────────────────────────────────────── */

interface ApiMonthlyReport {
  generated_at: string;
  monthly_usage: { month: string; pages: number; period: string }[];
  printers: {
    ip: string;
    name: string;
    department: string;
    monthly_pages: { month: string; pages: number; period: string }[];
  }[];
}

/**
 * Relatório mensal do backend, já no formato MonthlyReport da UI.
 * Devolve null quando a API falha ou ainda não há dados mensais, para o
 * chamador cair nas fontes anteriores.
 */
export async function loadMonthlyReportFromApi(): Promise<MonthlyReport | null> {
  try {
    const data = await api.get<ApiMonthlyReport>("/api/printers/monthly-report");
    if (!data.monthly_usage?.length) return null;

    return {
      generatedAt: data.generated_at,
      monthlyUsage: data.monthly_usage,
      printers: data.printers.map((p) => ({
        ip: p.ip,
        name: p.name,
        department: p.department,
        monthlyPages: p.monthly_pages,
      })),
    };
  } catch {
    return null;
  }
}
