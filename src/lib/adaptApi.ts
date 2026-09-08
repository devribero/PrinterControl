/**
 * Traducao entre os contratos do backend (snake_case, ids numericos) e os
 * tipos que a UI ja consumia (src/types.ts). Fica isolado aqui para que
 * nenhum componente precise conhecer o formato da API.
 */
import {
  api,
  type ApiAlert,
  type ApiNotification,
  type ApiPrintServer,
  type ApiPrinterWithStatus,
  type ApiSyncResult,
  type ApiTonerLevel,
} from "./api";
import type { Alert, MonthlyReport, Notification, Printer, PrintServer, PrinterStatus, SyncResult, TonerLevel } from "../types";

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

/**
 * Converte um timestamp da API em `Date`, tratando data sem fuso como UTC.
 *
 * QA-09: o backend grava com `datetime.utcnow()`, que produz um datetime
 * "ingênuo" — sem fuso. Serializado, ele sai como `2026-09-08T12:25:00` sem
 * o `Z` final, e `new Date(...)` de uma string sem designador de fuso a
 * interpreta como HORA LOCAL. Em America/Sao_Paulo (UTC-3) isso adiantava
 * tudo em três horas: uma sincronização das 08:25 aparecia como 11:25, e
 * uma leitura de uma hora atrás aparecia como "agora".
 *
 * A correção é aqui, e não em cada componente, porque o defeito estava na
 * leitura da string — todo lugar que faz `new Date` em campo vindo da API
 * tinha o mesmo erro.
 */
export function parseApiDate(iso: string | null | undefined): Date | null {
  if (!iso) return null;

  // Já tem fuso declarado (`Z`, `+03:00`, `-0300`)? Respeita o que veio.
  // O teste procura o designador DEPOIS do "T", para não confundir com os
  // hífens da própria data.
  const parteHora = iso.includes("T") ? iso.slice(iso.indexOf("T")) : "";
  const temFuso = /(?:Z|[+-]\d{2}:?\d{2})$/.test(parteHora);

  const date = new Date(temFuso ? iso : `${iso}Z`);
  return Number.isNaN(date.getTime()) ? null : date;
}

/** "agora", "há 12 min", "há 3 h", "12/08 14:30" — mesmo tom dos dados de demo. */
export function formatLastSeen(iso: string | null): string {
  if (!iso) return "Nunca coletada";

  const date = parseApiDate(iso);
  if (!date) return "Desconhecido";

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

/**
 * Quantas vezes o intervalo de coleta uma leitura pode ter antes de ser
 * considerada velha. 3 dá margem para dois ciclos perdidos (rede instável,
 * reinício do serviço) sem alarme falso.
 */
const STALE_FACTOR = 3;

/** Piso do limite, para intervalos muito curtos (o padrão de demo é 1 min). */
const STALE_MINIMO_MINUTOS = 15;

/** Limite, em minutos, a partir do qual uma leitura deixa de descrever o presente. */
export function limiteLeituraVelha(intervaloColetaMinutos: number | null): number {
  if (!intervaloColetaMinutos || intervaloColetaMinutos <= 0) return STALE_MINIMO_MINUTOS;
  return Math.max(intervaloColetaMinutos * STALE_FACTOR, STALE_MINIMO_MINUTOS);
}

/**
 * A leitura é velha o bastante para não descrever mais o estado atual?
 *
 * QA-02: a auditoria encontrou impressoras exibindo "normal, toner 65%" a
 * partir de uma leitura de 21/08 — o painel reaproveitava a última leitura
 * conhecida sem nenhuma regra de validade, então um estado antigo era
 * apresentado com a mesma confiança de um recém-coletado.
 */
export function leituraVelha(lastSeenIso: string | null, intervaloColetaMinutos: number | null): boolean {
  const date = parseApiDate(lastSeenIso);
  if (!date) return true; // nunca coletada: o estado nunca foi observado
  const minutos = (Date.now() - date.getTime()) / 60000;
  return minutos > limiteLeituraVelha(intervaloColetaMinutos);
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
    updatedAt: p.updated_at,
    status: toStatus(p.status),
    toner: toToner(p.toner),
    pagesPrinted: p.page_count ?? 0,
    // ISO cru, além do texto já formatado: só com ele dá para decidir a
    // idade da leitura mais tarde (QA-02) — `lastSeen` é texto de tela.
    lastSeenAt: p.last_seen ?? null,
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

export function adaptNotification(n: ApiNotification): Notification {
  return {
    id: n.id,
    message: n.message,
    severity: n.severity,
    readAt: n.read_at,
    createdAt: n.created_at,
    alertId: n.alert_id,
    alert: n.alert
      ? {
          id: n.alert.id,
          printerId: n.alert.printer_id,
          alertType: n.alert.alert_type,
          severity: n.alert.severity,
          resolved: n.alert.resolved,
        }
      : null,
  };
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
    id: number;
    ip: string;
    name: string;
    department: string;
    monthly_pages: { month: string; pages: number; period: string }[];
  }[];
  department_usage: {
    department: string;
    monthly: { month: string; pages: number; period: string }[];
    total: number;
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
        id: p.id === undefined ? undefined : String(p.id),
        ip: p.ip,
        name: p.name,
        department: p.department,
        monthlyPages: p.monthly_pages,
      })),
      departmentUsage: data.department_usage,
    };
  } catch {
    return null;
  }
}
