/**
 * Funções puras da tela Mapeamento de Rede: adaptação da resposta de
 * descoberta, textos de status/falha e formatação de datas e durações.
 * Sem React — ficam aqui para os componentes de `network/` compartilharem.
 */
import type { ApiDiscoveryResponse } from "../../lib/api";
import { parseApiDate } from "../../lib/adaptApi";
import type { DiscoveredPrinter, PrintServer } from "../../types";

/** Converte a resposta da API para o tipo que DiscoveryResults consome. */
export function adaptDiscovered(data: ApiDiscoveryResponse): DiscoveredPrinter[] {
  return data.printers.map((p) => ({
    name: p.name,
    server: p.server,
    portName: p.port_name,
    ip: p.ip,
    driverName: p.driver_name,
    source: p.source,
    ipResolution: p.ip_resolution,
    ipGroupSize: p.ip_group_size,
    networkQueryReused: p.network_query_reused,
    reachable: p.reachable,
    snmpResponded: p.snmp_responded,
    status: p.status,
    statusReason: p.status_reason,
    pageCount: p.page_count,
    uptime: p.uptime,
    toners: p.toners.map((t) => ({ color: t.color, percent: t.percent, description: t.description })),
    error: p.error,
  }));
}

/**
 * Motivo legível da última falha. O backend grava "[categoria] mensagem";
 * a mensagem crua continua disponível (title / detalhes) para quem precisar.
 */
const MOTIVOS_FALHA: Record<string, string> = {
  rpc_timeout_or_unavailable: "Não respondeu a tempo: servidor lento ou fora de alcance desta rede",
  dns_resolution_failed: "Nome não encontrado no DNS",
  access_denied: "Acesso negado para o usuário que roda o sistema",
  sync_blocked: "Sync bloqueado: a descoberta trouxe bem menos filas que o cadastro",
};

export function motivoDaFalha(erro: string): string {
  const m = /^\[([a-z_]+)\]\s*(.*)$/.exec(erro);
  if (!m) return erro;
  return MOTIVOS_FALHA[m[1]] ?? (m[2] || erro);
}

export function formatarMomento(iso: string | null): string {
  if (!iso) return "nunca";
  // parseApiDate e nao `new Date` (QA-09): o backend serializa UTC sem
  // fuso, e `new Date` de uma string assim assume hora LOCAL — em
  // America/Sao_Paulo isso adiantava todo horario exibido em 3h.
  const data = parseApiDate(iso);
  if (!data) return "desconhecido";
  return data.toLocaleString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

/** Duração em m:ss (ex.: 1:05). */
export function formatarDuracao(ms: number): string {
  const total = Math.max(0, Math.floor(ms / 1000));
  const min = Math.floor(total / 60);
  const seg = total % 60;
  return `${min}:${String(seg).padStart(2, "0")}`;
}

/**
 * Servidor real, ativo, que ainda não completou o primeiro sync: o backend
 * sincroniza sozinho logo após o cadastro, então a tela mostra isso em vez
 * de "Último sync: nunca".
 */
export function isAutoSyncPending(server: PrintServer): boolean {
  return server.active && server.mode === "real" && !server.lastSyncAt && server.lastStatus !== "error";
}

export type ServerHealth = "online" | "error" | "syncing" | "unknown" | "inactive";

/** Estado principal do cartão — é a primeira coisa que o cartão mostra. */
export function saudeDoServidor(server: PrintServer): { kind: ServerHealth; label: string } {
  if (!server.active) return { kind: "inactive", label: "Desativado" };
  if (server.lastStatus === "error") return { kind: "error", label: "Com falha" };
  if (isAutoSyncPending(server)) return { kind: "syncing", label: "Sincronizando" };
  if (server.lastStatus === "online") return { kind: "online", label: "Online" };
  return { kind: "unknown", label: "Nunca consultado" };
}

/** Plural simples para contagens na interface. */
export function plural(n: number, singular: string, pluralForm: string): string {
  return `${n} ${n === 1 ? singular : pluralForm}`;
}
