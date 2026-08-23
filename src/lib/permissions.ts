/**
 * Espelho, no frontend, do RBAC definido em `backend/app/models/user.py`.
 *
 * A hierarquia é a MESMA do backend (`ROLE_IMPLIES`): admin herda operator,
 * que herda viewer. Se um papel novo for adicionado lá, ele precisa ser
 * adicionado aqui — este arquivo é a única cópia da regra no frontend.
 *
 * IMPORTANTE: isto é experiência de uso, não segurança. Esconder um botão
 * não autoriza nada; quem autoriza é o backend (`require_admin` e cia.). O
 * objetivo aqui é só não oferecer ao usuário uma ação que vai voltar 403.
 */

export const ROLES = ["admin", "operator", "viewer"] as const;

export type Role = (typeof ROLES)[number];

/** Papéis que cada papel satisfaz (mesma tabela do backend). */
const ROLE_IMPLIES: Record<Role, readonly Role[]> = {
  admin: ["admin", "operator", "viewer"],
  operator: ["operator", "viewer"],
  viewer: ["viewer"],
};

/** Converte um valor vindo da API num Role conhecido; desconhecido = viewer. */
export function parseRole(value: unknown): Role {
  return ROLES.includes(value as Role) ? (value as Role) : "viewer";
}

/** True se `role` satisfaz `required`, respeitando a herança. */
export function hasRole(role: Role, required: Role): boolean {
  return ROLE_IMPLIES[role].includes(required);
}

/** Permissões derivadas do papel — o que a UI consulta. */
export interface Permissions {
  /** Leitura do painel. Todo usuário autenticado tem. */
  canView: boolean;
  /** Ações operacionais: coleta, resolver alerta, notificar. */
  canOperate: boolean;
  /** Ações administrativas: discovery, sync, usuários, mock, configurações. */
  canAdmin: boolean;
}

export function permissionsFor(role: Role | null): Permissions {
  if (!role) return { canView: false, canOperate: false, canAdmin: false };
  return {
    canView: hasRole(role, "viewer"),
    canOperate: hasRole(role, "operator"),
    canAdmin: hasRole(role, "admin"),
  };
}

/** Rótulo exibível do papel. */
export const ROLE_LABELS: Record<Role, string> = {
  admin: "Administrador",
  operator: "Operador",
  viewer: "Visualização",
};
