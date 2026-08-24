/**
 * Camada unica de comunicacao com o backend FastAPI.
 *
 * Resolve a URL base, serializa/desserializa JSON, anexa o JWT quando existe
 * e normaliza erros em ApiError. Todo fetch para a API deve passar por aqui.
 */
export const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL?.trim() || "http://127.0.0.1:8000").replace(/\/$/, "");

const TOKEN_KEY = "elgin_auth_token";

/**
 * Identificacao do ambiente do BACKEND (Fase 9).
 *
 * Vem de GET /health, e nao de uma NEXT_PUBLIC_* embutida no build: a
 * variavel de build descreve o bundle, nao o servidor a que ele acabou se
 * conectando. Um painel compilado como "production" e apontado para o
 * backend de demonstracao mentiria com toda a confianca.
 */
export interface BackendEnvironment {
  environment: "development" | "demo" | "production";
  is_demo: boolean;
  is_production: boolean;
  mock_collect_enabled: boolean;
  print_server_mode: "mock" | "real";
}

/**
 * Le o ambiente do backend. Publica: nao exige token, porque a tela de login
 * de uma instancia de demonstracao ja precisa se anunciar como tal.
 *
 * Devolve null quando o backend nao responde. Quem chama NAO deve tratar
 * null como producao nem como demo — e "desconhecido", e nesse caso o painel
 * ja esta exibindo a faixa de servidor indisponivel.
 */
export async function fetchBackendEnvironment(): Promise<BackendEnvironment | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/health`, { cache: "no-store" });
    if (!res.ok) return null;
    const data = (await res.json()) as Partial<BackendEnvironment>;
    if (data.environment !== "development" && data.environment !== "demo" && data.environment !== "production") {
      return null;
    }
    return {
      environment: data.environment,
      is_demo: data.is_demo === true,
      is_production: data.is_production === true,
      mock_collect_enabled: data.mock_collect_enabled === true,
      print_server_mode: data.print_server_mode === "real" ? "real" : "mock",
    };
  } catch {
    return null;
  }
}

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

/** True quando o token foi guardado com "lembrar de mim" (localStorage). */
export function isTokenPersistent(): boolean {
  if (typeof window === "undefined") return false;
  return localStorage.getItem(TOKEN_KEY) !== null;
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

/** Item do 422 do FastAPI: `{loc: [...], msg: "..."}`. */
interface ValidationDetail {
  loc?: unknown[];
  msg?: string;
}

/**
 * Transforma o `detail` do FastAPI em uma frase exibivel.
 *
 * Erros de validacao (422) vem como LISTA de objetos, nao string — sem este
 * tratamento a UI cairia no generico "Erro 422 na requisicao" e esconderia
 * exatamente a informacao de que o usuario precisa ("senha: deve ter ao
 * menos 8 caracteres").
 */
function describeDetail(detail: unknown): string | null {
  if (typeof detail === "string") return detail;

  if (Array.isArray(detail)) {
    const mensagens = (detail as ValidationDetail[])
      .map((item) => {
        if (!item?.msg) return null;
        // `loc` costuma ser ["body", "campo"]; interessa o ultimo trecho.
        const campo = Array.isArray(item.loc) ? item.loc[item.loc.length - 1] : null;
        return typeof campo === "string" && campo !== "body" ? `${campo}: ${item.msg}` : item.msg;
      })
      .filter((m): m is string => !!m);

    if (mensagens.length > 0) return mensagens.join(" | ");
  }

  return null;
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
    throw new ApiError(res.status, describeDetail(detail) ?? `Erro ${res.status} na requisicao.`);
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
  /** Print Server de origem; "" em impressoras cadastradas a mao. */
  server: string;
  ip: string;
  name: string;
  model: string;
  department: string;
  /** false = sumiu do Print Server no ultimo sync (nunca e apagada). */
  active: boolean;
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

/* ── Gestao de contas (/api/users) — somente admin ───────────────────────── */

/** `UserResponse` do backend. Nunca traz hash de senha. */
export interface ApiUser {
  id: number;
  email: string;
  /** Segunda porta de login, opcional; null quando a conta so entra por e-mail. */
  username: string | null;
  name: string;
  role: string;
  is_active: boolean;
  /** Troca de senha pendente — ver Account.mustChangePassword em lib/auth.ts. */
  must_change_password: boolean;
  created_at: string;
}

export interface UserCreateInput {
  email: string;
  /** Opcional; backend valida formato (3-32, minusculas, `._-`) e unicidade. */
  username?: string;
  name: string;
  password: string;
  role: string;
}

/** Campos que o admin pode alterar. Todos opcionais (PATCH parcial). */
export interface UserUpdateInput {
  name?: string;
  username?: string;
  role?: string;
  is_active?: boolean;
  /** Redefinicao de senha pelo admin; enviada em claro e hasheada no backend.
   * Liga `must_change_password` na conta alterada. */
  password?: string;
}

export const fetchUsers = (signal?: AbortSignal) => api.get<ApiUser[]>("/api/users", { signal });

/* ── Print Servers (/api/servers) ────────────────────────────────────────── */

/** `PrintServerResponse` do backend (Fase 4). */
export interface ApiPrintServer {
  id: number;
  host: string;
  name: string;
  mode: "mock" | "real";
  active: boolean;
  last_status: "unknown" | "online" | "error";
  last_error: string | null;
  last_seen_at: string | null;
  last_sync_at: string | null;
  created_at: string;
  printer_count: number;
  active_printer_count: number;
  is_default: boolean;
}

/** O que o sync mudou no banco. */
export interface ApiSyncResult {
  server: string;
  discovered: number;
  created: number;
  updated: number;
  reactivated: number;
  deactivated: number;
}

/** Servidores registrados. Leitura — qualquer papel autenticado. */
export const fetchPrintServers = (signal?: AbortSignal) =>
  api.get<ApiPrintServer[]>("/api/servers", { signal });

/**
 * Descoberta de UM servidor: consulta o Print Server e devolve o que existe
 * agora. NAO grava nada no banco — o par disto e `syncServer`, que grava.
 * Exige admin.
 */
export const discoverServer = (serverId: number) =>
  api.post<ApiDiscoveryResponse>(`/api/servers/${serverId}/discover`);

/**
 * Sincroniza UM servidor com o banco: cria as novas, atualiza as existentes
 * e desativa as que sumiram. Nunca apaga. Escopado ao servidor — impressoras
 * de outros servidores nao sao tocadas. Exige admin.
 */
export const syncServer = (serverId: number) =>
  api.post<ApiSyncResult>(`/api/servers/${serverId}/sync`);

/** Corpo de `POST /api/servers` (`PrintServerCreate` no backend). */
export interface PrintServerCreateInput {
  host: string;
  /** Rotulo legivel. Vazio faz o backend cair no proprio host. */
  name?: string;
  mode?: "mock" | "real";
}

/**
 * Corpo de `PATCH /api/servers/{id}` (`PrintServerUpdate` no backend).
 *
 * `host` NAO entra, e nao e esquecimento: e a chave natural que aparece em
 * `printers.server` e no UniqueConstraint (server, name). Renomea-lo
 * orfanaria em silencio todas as impressoras do servidor, entao o backend
 * tambem o recusa (Fase 4).
 */
export interface PrintServerUpdateInput {
  name?: string;
  mode?: "mock" | "real";
  /** false = exclusao logica: o registro e o historico ficam, a operacao para. */
  active?: boolean;
}

/** Registra um Print Server. O host e unico — 409 se ja existir. Exige admin. */
export const createPrintServer = (data: PrintServerCreateInput) =>
  api.post<ApiPrintServer>("/api/servers", data);

/** Altera rotulo, modo ou ativacao de um servidor registrado. Exige admin. */
export const updatePrintServer = (serverId: number, data: PrintServerUpdateInput) =>
  api.patch<ApiPrintServer>(`/api/servers/${serverId}`, data);

/* -- Notificacoes internas (/api/notifications) --------------------------- */

/** Referencia ao alerta de origem, quando houver (`AlertRef` no backend). */
export interface ApiNotificationAlertRef {
  id: number;
  printer_id: number;
  alert_type: string | null;
  severity: string;
  resolved: boolean;
}

/** `NotificationResponse` do backend (Fase 7). */
export interface ApiNotification {
  id: number;
  message: string;
  severity: "info" | "warning" | "critical";
  read_at: string | null;
  created_at: string;
  alert_id: number | null;
  alert: ApiNotificationAlertRef | null;
}

export interface NotificationCreateInput {
  user_ids: number[];
  message: string;
  severity?: "info" | "warning" | "critical";
  alert_id?: number | null;
}

/**
 * Caixa do usuario LOGADO. Nao existe parametro de destinatario: o backend
 * sempre filtra pela sessao, entao nao ha como pedir a caixa de outra pessoa.
 */
export const fetchNotifications = (
  options: { unreadOnly?: boolean; limit?: number } = {},
  signal?: AbortSignal,
) => {
  const params = new URLSearchParams();
  if (options.unreadOnly) params.set("unread_only", "true");
  if (options.limit) params.set("limit", String(options.limit));
  const qs = params.toString();
  return api.get<ApiNotification[]>(`/api/notifications${qs ? `?${qs}` : ""}`, { signal });
};

/** Contador para o badge, sem trazer a lista inteira. */
export const fetchUnreadNotificationCount = (signal?: AbortSignal) =>
  api.get<{ unread: number }>("/api/notifications/unread-count", { signal });

/** Idempotente: reler nao reescreve o `read_at` da primeira leitura. */
export const markNotificationRead = (notificationId: number) =>
  api.patch<ApiNotification>(`/api/notifications/${notificationId}/read`);

/**
 * Marca TODAS as nao lidas da caixa do usuario logado, num unico instante.
 * Idempotente: sem pendencias devolve `marked: 0`, e nunca reescreve o
 * `read_at` de uma que ja estava lida.
 */
export const markAllNotificationsRead = () =>
  api.post<{ marked: number }>("/api/notifications/read-all");

/** Envia para N destinatarios — uma notificacao por pessoa. Exige admin. */
export const createNotifications = (data: NotificationCreateInput) =>
  api.post<ApiNotification[]>("/api/notifications", data);

export const createUser = (data: UserCreateInput) => api.post<ApiUser>("/api/users", data);

export const updateUser = (userId: number, data: UserUpdateInput) =>
  api.patch<ApiUser>(`/api/users/${userId}`, data);
