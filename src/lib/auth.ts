/**
 * Autenticacao real contra POST /api/auth/login do FastAPI.
 * Substitui a validacao client-side que vivia em data/accounts.ts.
 */
import { api, clearToken, getToken, setToken } from "./api";

/** Conta logada, no formato que a UI ja consumia (Topbar, AuthGate). */
export interface Account {
  /** Parte antes do @ — a Topbar exibe `${email}@elgin.com`. */
  email: string;
  name: string;
}

const ACCOUNT_KEY = "elgin_auth_account";

interface LoginResponse {
  access_token: string;
  token_type: string;
  user?: { id: number; email: string; name: string };
}

function toAccount(user: { email: string; name: string }): Account {
  return { email: user.email.split("@")[0], name: user.name };
}

/** Faz login e persiste token + conta. Lanca ApiError em credencial invalida. */
export async function login(email: string, password: string, remember: boolean): Promise<Account> {
  const data = await api.post<LoginResponse>(
    "/api/auth/login",
    { email: email.trim(), password },
    { auth: false },
  );

  setToken(data.access_token, remember);

  const account = toAccount(data.user ?? { email: email.trim(), name: email.trim() });
  (remember ? localStorage : sessionStorage).setItem(ACCOUNT_KEY, JSON.stringify(account));
  return account;
}

/** Sessao persistida: so vale se token E conta estiverem presentes. */
export function readStoredAccount(): Account | null {
  if (typeof window === "undefined") return null;
  if (!getToken()) return null;

  const raw = localStorage.getItem(ACCOUNT_KEY) ?? sessionStorage.getItem(ACCOUNT_KEY);
  if (!raw) return null;

  try {
    const parsed = JSON.parse(raw) as Partial<Account>;
    if (typeof parsed.email !== "string" || typeof parsed.name !== "string") return null;
    return { email: parsed.email, name: parsed.name };
  } catch {
    return null;
  }
}

export function logout() {
  clearToken();
  if (typeof window !== "undefined") {
    localStorage.removeItem(ACCOUNT_KEY);
    sessionStorage.removeItem(ACCOUNT_KEY);
  }
}
