/**
 * Camada unica de comunicacao com o backend FastAPI.
 *
 * Resolve a URL base, serializa/desserializa JSON, anexa o JWT quando existe
 * e normaliza erros em ApiError. Todo fetch para a API deve passar por aqui.
 */
export const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL?.trim() || "http://127.0.0.1:8000").replace(/\/$/, "");

const TOKEN_KEY = "elgin_auth_token";

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/** Token do usuario logado — localStorage (lembrar) ou sessionStorage. */
export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY) ?? sessionStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string, remember: boolean) {
  clearToken();
  (remember ? localStorage : sessionStorage).setItem(TOKEN_KEY, token);
}

export function clearToken() {
  if (typeof window === "undefined") return;
  localStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem(TOKEN_KEY);
}

interface RequestOptions {
  method?: string;
  body?: unknown;
  /** Envia o Authorization: Bearer quando ha token. Padrao: true. */
  auth?: boolean;
  signal?: AbortSignal;
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, auth = true, signal } = options;

  const headers: Record<string, string> = {};
  if (body !== undefined) headers["Content-Type"] = "application/json";

  if (auth) {
    const token = getToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  let res: Response;
  try {
    res = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
      signal,
    });
  } catch {
    throw new ApiError(0, "Nao foi possivel conectar ao servidor. Verifique se o backend esta rodando.");
  }

  if (res.status === 204) return undefined as T;

  const raw = await res.text();
  let data: unknown = null;
  if (raw) {
    try {
      data = JSON.parse(raw);
    } catch {
      data = null;
    }
  }

  if (!res.ok) {
    const detail = (data as { detail?: unknown } | null)?.detail;
    throw new ApiError(res.status, typeof detail === "string" ? detail : `Erro ${res.status} na requisicao.`);
  }

  return data as T;
}

/* ── Contratos do backend (snake_case, como o FastAPI devolve) ───────────── */

export interface ApiTonerLevel {
  color: string;
  label: string;
  percent: number;
}

export interface ApiPrinterWithStatus {
  id: number;
  ip: string;
  name: string;
  model: string;
  department: string;
  created_at: string;
  status: string;
  page_count: number;
  toner: ApiTonerLevel[] | null;
  last_seen: string | null;
}

export interface ApiAlert {
  id: number;
  printer_id: number;
  alert_type: string | null;
  severity: string;
  message: string;
  created_at: string;
  resolved_at: string | null;
}

export interface ApiPrinterReading {
  id: number;
  printer_id: number;
  status: string;
  page_count: number;
  toner_k: number | null;
  toner_c: number | null;
  toner_m: number | null;
  toner_y: number | null;
  timestamp: string;
}

export interface ApiDiscoveredToner {
  color: string;
  percent: number;
  index: number;
  maximum: number;
  description: string;
}

export interface ApiDiscoveredPrinter {
  name: string;
  server: string;
  port_name: string;
  ip: string | null;
  driver_name: string;
  model: string | null;
  printer_type: string | null;
  source: "print_server_real" | "print_server_mock";
  ip_resolution: "resolved" | "unresolved";
  ip_group_size: number;
  network_query_reused: boolean;
  reachable: boolean | null;
  snmp_responded: boolean;
  status: string;
  status_reason: string;
  page_count: number | null;
  uptime: string | null;
  toners: ApiDiscoveredToner[];
  error: string | null;
}

export interface ApiDiscoveryResponse {
  server: string;
  mode: "mock" | "real";
  source: "print_server_real" | "print_server_mock";
  count: number;
  unique_ips: number;
  printers: ApiDiscoveredPrinter[];
}

export const api = {
  get: <T>(path: string, options?: Omit<RequestOptions, "method" | "body">) =>
    apiRequest<T>(path, { ...options, method: "GET" }),
  post: <T>(path: string, body?: unknown, options?: Omit<RequestOptions, "method" | "body">) =>
    apiRequest<T>(path, { ...options, method: "POST", body }),
  patch: <T>(path: string, body?: unknown, options?: Omit<RequestOptions, "method" | "body">) =>
    apiRequest<T>(path, { ...options, method: "PATCH", body }),
};

/* ── Endpoints usados pelo painel ────────────────────────────────────────── */

/** Impressoras + ultima leitura de cada uma (uma unica chamada). */
export const fetchPrintersWithStatus = (signal?: AbortSignal) =>
  api.get<ApiPrinterWithStatus[]>("/api/printers/with-status", { signal });

/** Alertas. `resolved=false` (padrao do backend) devolve so os ativos. */
export const fetchAlerts = (resolved = false, signal?: AbortSignal) =>
  api.get<ApiAlert[]>(`/api/alerts?resolved=${resolved}`, { signal });

/** Historico de leituras de uma impressora, mais recentes primeiro. */
export const fetchPrinterReadings = (printerId: string | number, limit = 100, signal?: AbortSignal) =>
  api.get<ApiPrinterReading[]>(`/api/printers/${printerId}/readings?limit=${limit}`, { signal });

/** Descoberta transitória via Print Server + enriquecimento SNMP. */
export const discoverPrinters = () => api.post<ApiDiscoveryResponse>("/api/servers/discover");

/** Campos editáveis de uma impressora (cadastro, não leitura). */
export interface PrinterInput {
  ip: string;
  name: string;
  model: string;
  department: string;
}

/**
 * Cadastro de impressoras. Exigem JWT — o token é anexado automaticamente
 * por apiRequest. Erros de validação chegam como ApiError com a mensagem do
 * backend (IP inválido, IP duplicado, campo obrigatório) pronta para exibir.
 */
export const createPrinter = (data: PrinterInput) =>
  api.post<ApiPrinterWithStatus>("/api/printers", data);

export const updatePrinter = (printerId: string | number, data: Partial<PrinterInput>) =>
  api.patch<ApiPrinterWithStatus>(`/api/printers/${printerId}`, data);
