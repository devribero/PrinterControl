/**
 * Sessão real contra o FastAPI: `POST /api/auth/login` para entrar e
 * `GET /api/auth/me` para restaurar/confirmar a sessão a cada abertura.
 *
 * O backend é a fonte de verdade da identidade e do papel. O que fica em
 * localStorage/sessionStorage é apenas o token (credencial) e uma CÓPIA da
 * conta usada só como último recurso quando o servidor está fora do ar —
 * nunca como fonte do `role` numa sessão verificada.
 */
import { api, ApiError, clearToken, getToken, isTokenPersistent, setToken } from "./api";
import { parseRole, type Role } from "./permissions";

/** Conta logada, no formato que a UI consome (Topbar, AuthGate, Sidebar). */
export interface Account {
  /** Id da linha em `users`. Identidade exata — a UI usa para reconhecer
   * "sou eu" sem depender do e-mail, que aqui vem truncado. */
  id: number;
  /** Parte antes do @ — a Topbar exibe `${email}@elgin.com`. */
  email: string;
  name: string;
  /** Papel vindo do backend. Governa o que a UI oferece (não o que autoriza). */
  role: Role;
  isActive: boolean;
}

const ACCOUNT_KEY = "elgin_auth_account";

/** `UserResponse` do backend (app/schemas/user.py). */
interface ApiUser {
  id: number;
  email: string;
  name: string;
  role: string;
  is_active: boolean;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
  user?: ApiUser | null;
}

function toAccount(user: ApiUser): Account {
  return {
    id: user.id,
    email: user.email.split("@")[0],
    name: user.name,
    role: parseRole(user.role),
    isActive: user.is_active,
  };
}

function cacheAccount(account: Account, remember: boolean) {
  if (typeof window === "undefined") return;
  (remember ? localStorage : sessionStorage).setItem(ACCOUNT_KEY, JSON.stringify(account));
}

/** Conta guardada localmente. Só é usada quando o backend está inacessível. */
function readCachedAccount(): Account | null {
  if (typeof window === "undefined") return null;

  const raw = localStorage.getItem(ACCOUNT_KEY) ?? sessionStorage.getItem(ACCOUNT_KEY);
  if (!raw) return null;

  try {
    const parsed = JSON.parse(raw) as Partial<Account>;
    if (typeof parsed.email !== "string" || typeof parsed.name !== "string") return null;
    return {
      // Cache gravado antes desta versao nao tem id; 0 nunca casa com um id
      // real, entao o pior caso e a UI nao reconhecer "sou eu" ate o /me
      // responder e substituir o cache.
      id: typeof parsed.id === "number" ? parsed.id : 0,
      email: parsed.email,
      name: parsed.name,
      role: parseRole(parsed.role),
      isActive: parsed.isActive !== false,
    };
  } catch {
    return null;
  }
}

/** Faz login e persiste token + conta. Lanca ApiError em credencial invalida. */
export async function login(email: string, password: string, remember: boolean): Promise<Account> {
  const data = await api.post<LoginResponse>(
    "/api/auth/login",
    { email: email.trim(), password },
    { auth: false },
  );

  setToken(data.access_token, remember);

  // O backend devolve o usuário completo no login desde a Fase 1. Se um dia
  // não devolver, confirmamos com /api/auth/me em vez de inventar um papel.
  const account = data.user ? toAccount(data.user) : toAccount(await fetchCurrentUser());
  cacheAccount(account, remember);
  return account;
}

/** `GET /api/auth/me` — usuário do token, direto do backend. */
export function fetchCurrentUser(signal?: AbortSignal): Promise<ApiUser> {
  return api.get<ApiUser>("/api/auth/me", { signal });
}

export type SessionState =
  /** Sem token, ou token recusado pelo backend. */
  | { status: "anonymous"; reason?: "invalid" | "disabled" }
  /** Token confirmado agora por /api/auth/me. */
  | { status: "authenticated"; account: Account }
  /**
   * Existe token e conta em cache, mas o servidor não respondeu para
   * confirmar. A UI segue utilizável em modo demonstração, sinalizando que a
   * sessão não foi verificada — o papel aqui vem do cache, então só serve
   * para não esconder a interface, nunca como garantia.
   */
  | { status: "unverified"; account: Account };

/**
 * Restaura a sessão na abertura do app.
 *
 * - sem token                  -> anonymous
 * - token válido               -> authenticated (dados frescos do backend)
 * - 401 (token inválido/expirado) -> limpa e volta a anonymous
 * - 403 (conta desativada)     -> limpa e volta a anonymous
 * - servidor inacessível       -> unverified (mantém o token, não desloga)
 */
export async function restoreSession(signal?: AbortSignal): Promise<SessionState> {
  if (typeof window === "undefined" || !getToken()) return { status: "anonymous" };

  try {
    const account = toAccount(await fetchCurrentUser(signal));
    // Renova a cópia local no mesmo storage em que o token vive.
    cacheAccount(account, isTokenPersistent());
    return { status: "authenticated", account };
  } catch (error) {
    if (error instanceof ApiError && (error.status === 401 || error.status === 403)) {
      // Token inválido/expirado (401) ou conta desativada (403): a sessão
      // acabou de fato — não adianta manter o token.
      logout();
      return { status: "anonymous", reason: error.status === 403 ? "disabled" : "invalid" };
    }

    // Falha de rede (ApiError status 0) ou erro do servidor: não dá para
    // afirmar que a sessão morreu, então não deslogamos o usuário.
    const cached = readCachedAccount();
    return cached ? { status: "unverified", account: cached } : { status: "anonymous" };
  }
}

export function logout() {
  clearToken();
  if (typeof window !== "undefined") {
    localStorage.removeItem(ACCOUNT_KEY);
    sessionStorage.removeItem(ACCOUNT_KEY);
  }
}
