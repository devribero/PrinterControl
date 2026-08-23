/**
 * Contratos de dados compartilhados entre frontend e os coletores PowerShell
 * (scripts/Coletar-Impressoras.ps1 e scripts/Relatorio-Mensal.ps1). Mudar um
 * campo aqui exige mudar o `ConvertTo-*Json` correspondente no script — são
 * a mesma "API" só que sem servidor no meio (arquivo JSON estático).
 */
export type PrinterStatus = "online" | "offline" | "atencao";

export interface TonerLevel {
  color: "K" | "C" | "M" | "Y";
  label: string;
  percent: number;
}

export interface MonthlyPageCount {
  month: string;
  pages: number;
  period: string;
}

export interface Printer {
  id: string;
  name: string;
  ip: string;
  model: string;
  department: string;
  /** Print Server de origem; "" quando cadastrada a mao (Fase 4/5). */
  server: string;
  /** false = sumiu do Print Server no ultimo sync; o registro e preservado. */
  active: boolean;
  status: PrinterStatus;
  toner: TonerLevel[] | null;
  pagesPrinted: number;
  lastSeen: string;
  monthlyPages?: MonthlyPageCount[];
}

export interface DiscoveredPrinter {
  name: string;
  server: string;
  portName: string;
  ip: string | null;
  driverName: string;
  source: "print_server_real" | "print_server_mock";
  ipResolution: "resolved" | "unresolved";
  ipGroupSize: number;
  networkQueryReused: boolean;
  reachable: boolean | null;
  snmpResponded: boolean;
  status: string;
  statusReason: string;
  pageCount: number | null;
  uptime: string | null;
  toners: { color: string; percent: number; description: string }[];
  error: string | null;
}

/** Print Server registrado, no formato que a UI consome (Fase 5). */
export interface PrintServer {
  id: number;
  host: string;
  name: string;
  mode: "mock" | "real";
  active: boolean;
  lastStatus: "unknown" | "online" | "error";
  lastError: string | null;
  lastSeenAt: string | null;
  lastSyncAt: string | null;
  printerCount: number;
  activePrinterCount: number;
  isDefault: boolean;
}

/** Resultado de um sync — o que efetivamente mudou no banco. */
export interface SyncResult {
  server: string;
  discovered: number;
  created: number;
  updated: number;
  reactivated: number;
  deactivated: number;
}

export interface Alert {
  id: string;
  severity: "critical" | "warning" | "info";
  message: string;
  printerId: string;
  timestamp: string;
}

export interface MonthlyUsage {
  month: string;
  pages: number;
}

export interface MonthlyUsageEntry extends MonthlyUsage {
  period: string;
}

/**
 * Shape written by scripts/Relatorio-Mensal.ps1 to public/data/monthly-report.json.
 * Optional/real: only present once that script has been deployed and scheduled —
 * see src/lib/fetchMonthlyReport.ts for the loader and its mock fallback.
 */
export interface MonthlyReport {
  generatedAt: string;
  monthlyUsage: MonthlyUsageEntry[];
  printers: {
    ip: string;
    name: string;
    department: string;
    monthlyPages: MonthlyPageCount[];
  }[];
}
