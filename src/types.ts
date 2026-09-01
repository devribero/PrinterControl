/**
 * Contratos de dados compartilhados entre frontend e backend. Mudar um campo
 * aqui costuma exigir mudar o schema Pydantic correspondente
 * (backend/app/schemas/) — são a mesma "API", só que descrita duas vezes,
 * uma em cada linguagem.
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
  /**
   * Atualizado no momento em que `active` vira false — "desde quando"
   * ficou inativa. Opcional: o conjunto de demonstração (data/printers.ts)
   * não carrega esse campo, só o real (backend) o preenche.
   */
  updatedAt?: string;
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

/**
 * Referencia ao alerta que originou a notificacao (Fase 7/8).
 *
 * E um LINK, nao o conteudo: a notificacao ja traz a propria `message`. Vem
 * null quando nao ha vinculo ou quando o alerta nao existe mais — nos dois
 * casos a notificacao continua legivel.
 */
export interface NotificationAlertRef {
  id: number;
  printerId: number;
  alertType: string | null;
  severity: string;
  /** true = o alerta ja foi resolvido; false = ainda esta aberto. */
  resolved: boolean;
}

/** Notificacao da caixa pessoal do usuario logado. */
export interface Notification {
  id: number;
  message: string;
  severity: "info" | "warning" | "critical";
  /** null = nao lida. Quando preenchido, e o instante da PRIMEIRA leitura. */
  readAt: string | null;
  createdAt: string;
  alertId: number | null;
  alert: NotificationAlertRef | null;
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
 * Shape of GET /api/printers/monthly-report (backend). Optional/real: only
 * present once the backend has enough readings accumulated — see
 * src/lib/fetchMonthlyReport.ts for the loader and its demo fallback.
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
  departmentUsage: DepartmentUsage[];
}

/** Consumo por departamento — real (backend, Fase 12) ou de demonstração (data/printers.ts). */
export interface DepartmentUsage {
  department: string;
  monthly: MonthlyPageCount[];
  total: number;
}

/**
 * Impressora inativa — real (Printer.active=false, Fase 18) ou de
 * demonstração (data/printers.ts). Sem `serial`: o cadastro real nunca
 * coletou número de série (não vem do Print Server); mostrar essa coluna
 * sempre vazia pra dado real seria pior que não ter a coluna.
 */
export interface DecommissionedPrinter {
  ip: string;
  model: string;
  department: string;
  /** Quando ficou inativa (Printer.updatedAt) — null só no conjunto de demonstração antigo. */
  deactivatedAt: string | null;
}
