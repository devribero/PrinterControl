/**
 * Vocabulario do escopo do painel (`serverScope` em lib/app-data.tsx).
 *
 *   null          -> todos os servidores
 *   ""            -> sem servidor (impressoras cadastradas a mao)
 *   "unit:<id>"   -> os Print Servers da unidade <id>
 *   qualquer outro -> o host de UM Print Server
 *
 * O prefixo nao colide com host real: host e nome de rede (NetBIOS/DNS) e
 * nao tem ":".
 */
import type { PrintServer, Unit } from "../types";

const PREFIXO_UNIDADE = "unit:";

export function unitScope(unitId: number): string {
  return `${PREFIXO_UNIDADE}${unitId}`;
}

/** Id da unidade quando o escopo e de unidade; null nos demais casos. */
export function parseUnitScope(scope: string | null): number | null {
  if (scope === null || !scope.startsWith(PREFIXO_UNIDADE)) return null;
  const id = Number(scope.slice(PREFIXO_UNIDADE.length));
  return Number.isInteger(id) && id > 0 ? id : null;
}

/** Rotulo curto do escopo, no mesmo vocabulario em todas as telas. */
export function rotularEscopo(scope: string | null, servers: PrintServer[], units: Unit[]): string {
  if (scope === null) return "Todos os servidores";
  if (scope === "") return "Sem servidor";
  const unidade = parseUnitScope(scope);
  if (unidade !== null) return units.find((u) => u.id === unidade)?.name ?? "Unidade";
  return servers.find((s) => s.host === scope)?.name ?? scope;
}

/**
 * Hosts que pertencem a unidade. Une as duas fontes — `server_hosts` da
 * unidade e `unit_id` de cada servidor — porque as listas sao buscadas em
 * momentos diferentes e uma pode estar um passo atras da outra logo depois
 * de uma edicao.
 */
export function hostsDaUnidade(unit: Unit | undefined, unitId: number, servers: PrintServer[]): Set<string> {
  const hosts = new Set<string>(unit?.serverHosts ?? []);
  for (const s of servers) if (s.unitId === unitId) hosts.add(s.host);
  return hosts;
}
