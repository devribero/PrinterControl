/**
 * Dependências: nenhuma lib externa — só `fetch` nativo do browser e o tipo
 * `MonthlyReport` (src/types.ts). Sem imports de outros módulos locais.
 *
 * `loadMonthlyReport()` é o fallback de ÚLTIMA instância, usado só quando a
 * API está fora do ar (ver lib/app-data.tsx) — tenta ler um
 * /data/monthly-report.json estático que, hoje, nada gera mais (os antigos
 * scripts PowerShell de coleta foram removidos; a fonte real é o backend,
 * GET /api/printers/monthly-report). Na prática este fetch sempre falha
 * (404) e cai direto nos números extraídos da planilha (src/data/printers.ts)
 * como demonstração — mantido porque a falha já era tratada como esperada,
 * não um bug a corrigir.
 */
import type { MonthlyReport } from "../types";

function isValidReport(value: unknown): value is MonthlyReport {
  if (typeof value !== "object" || value === null) return false;
  const r = value as Record<string, unknown>;
  return (
    typeof r.generatedAt === "string" &&
    Array.isArray(r.monthlyUsage) &&
    Array.isArray(r.printers) &&
    Array.isArray(r.departmentUsage)
  );
}

/**
 * Fallback de desenvolvimento: só é chamado quando a API está indisponível
 * (ver lib/app-data.tsx). Com a API no ar, o relatório mensal vem dela e
 * apenas dela — misturar as duas fontes esconderia de qual delas veio cada
 * número.
 */
export async function loadMonthlyReport(): Promise<MonthlyReport | null> {
  try {
    const res = await fetch("/data/monthly-report.json", { cache: "no-store" });
    if (!res.ok) return null;

    const data: unknown = await res.json();
    if (!isValidReport(data)) return null;

    return data;
  } catch {
    return null;
  }
}

/**
 * Mescla o relatório mensal nos objetos Printer já carregados, preenchendo
 * `monthlyPages`. Impressoras sem correspondência no relatório (ainda sem
 * histórico suficiente) mantêm o que já tinham.
 *
 * Casa por `id` quando o relatório traz id, e só cai no IP quando não traz
 * (relatório de demonstração e o /data/monthly-report.json legado).
 *
 * QA-03: casar por IP era errado desde a Etapa 4, quando a identidade da
 * impressora passou a ser (servidor, nome) e duas filas do mesmo Print
 * Server puderam dividir um endereço. Com IP como chave, a segunda fila
 * sobrescrevia a primeira no mapa e AS DUAS passavam a exibir o total da
 * última — 100 e 250 viravam 250 e 250. O erro não aparecia como falha:
 * aparecia como um número mensal plausível e errado.
 */
export function mergeMonthlyReport<T extends { id?: string; ip: string; monthlyPages?: unknown }>(
  printers: T[],
  report: MonthlyReport | null
): T[] {
  if (!report) return printers;

  const byId = new Map(
    report.printers.filter((p) => p.id !== undefined).map((p) => [p.id, p.monthlyPages])
  );
  // Só as entradas SEM id caem no mapa por IP, para que um relatório misto
  // nunca reintroduza a colisão nas que já têm identidade estável.
  const byIp = new Map(
    report.printers.filter((p) => p.id === undefined).map((p) => [p.ip, p.monthlyPages])
  );

  return printers.map((p) => {
    const monthlyPages = (p.id !== undefined ? byId.get(p.id) : undefined) ?? byIp.get(p.ip);
    return monthlyPages ? { ...p, monthlyPages } : p;
  });
}
