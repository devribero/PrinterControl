"use client";

/**
 * Card "Volume de impressão" do Dashboard: páginas por mês, com o mês
 * corrente e o último mês fechado em destaque.
 *
 * Eram três cards (22/09/2026): o gráfico de área, "Impressões totais" (a
 * soma da janela + mini-barras que redesenhavam o mesmo gráfico) e um donut
 * "Dispositivos com alerta" que repetia o número "Atenção" da faixa de
 * resumo. Ficou um card só.
 *
 * Barras em vez de área: cada mês é um total fechado, não uma série
 * contínua, e a barra do mês EM ANDAMENTO sai mais clara — no dia 21 ele tem
 * só parte do mês, e desenhá-lo igual aos outros sugeriria queda. Pelo mesmo
 * motivo a variação percentual compara os dois últimos meses FECHADOS.
 *
 * `monthlyUsage` chega via prop (relatório real do backend, GET
 * /api/printers/monthly-report, ou o conjunto de demonstração — nesse caso
 * `monthlyFicticio` liga o selo). Cores dos gráficos vêm de
 * lib/chartColors.ts: recharts recebe cor como string, não lê os tokens CSS.
 */
import { BarChart, Bar, Cell, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip } from "recharts";
import type { MonthlyUsageEntry } from "../types";
import { useTheme } from "../lib/theme";
import { getChartColors } from "../lib/chartColors";
import { cn } from "../lib/cn";
import DemoDataBadge from "./DemoDataBadge";
import styles from "./BottomCharts.module.css";

const MOTIVO_FICTICIO =
  "O servidor ainda não tem leituras suficientes para fechar o mês, então o consumo mensal exibido é de demonstração.";

function fmt(n: number): string {
  return n.toLocaleString("pt-BR");
}

function formatTick(v: number): string {
  if (v >= 1_000_000) return `${(v / 1_000_000).toFixed(1).replace(".", ",")}M`;
  if (v >= 1000) return `${Math.round(v / 1000)}k`;
  return String(v);
}

interface BottomChartsProps {
  monthlyUsage: MonthlyUsageEntry[];
  /** True quando `monthlyUsage` veio do conjunto de demonstração (Fase 9). */
  monthlyFicticio?: boolean;
  loading?: boolean;
}

export default function BottomCharts({ monthlyUsage, monthlyFicticio = false, loading = false }: BottomChartsProps) {
  const { theme } = useTheme();
  const c = getChartColors(theme);

  const atual = monthlyUsage[monthlyUsage.length - 1];
  const fechados = monthlyUsage.filter((m) => !m.inProgress);
  const ultimoFechado = fechados[fechados.length - 1];
  const penultimoFechado = fechados[fechados.length - 2];
  const variacao =
    ultimoFechado && penultimoFechado && penultimoFechado.pages > 0
      ? ((ultimoFechado.pages - penultimoFechado.pages) / penultimoFechado.pages) * 100
      : null;
  // Com o mês corrente fechado (ou sem mês em andamento), os dois destaques
  // seriam o mesmo mês — mostra só um.
  const mostrarFechado = ultimoFechado && ultimoFechado !== atual;

  return (
    <section className={styles.card} aria-busy={loading || undefined}>
      <header className={styles.header}>
        <h3 className={styles.title}>Volume de impressão</h3>
        <DemoDataBadge ficticio={monthlyFicticio && !loading} motivo={MOTIVO_FICTICIO} />
        <span className={styles.headerMeta}>Páginas por mês</span>
      </header>

      {loading ? (
        <div className={styles.body} aria-hidden="true">
          <span className={cn(styles.skeletonFigures, "animate-pulse")} />
          <span className={cn(styles.skeletonChart, "animate-pulse")} />
        </div>
      ) : !atual ? (
        <p className={styles.empty}>
          Ainda sem histórico mensal. O relatório se acumula a partir das leituras coletadas — o primeiro mês aparece aqui
          assim que houver dados.
        </p>
      ) : (
        <div className={styles.body}>
          <dl className={styles.figures}>
            <div className={styles.figure}>
              <dt className={styles.figureLabel}>
                {atual.month}
                {atual.inProgress ? " · em andamento" : ""}
              </dt>
              <dd className={styles.figureValue}>{fmt(atual.pages)}</dd>
            </div>
            {mostrarFechado && (
              <div className={styles.figure}>
                <dt className={styles.figureLabel}>{ultimoFechado.month} · fechado</dt>
                <dd className={styles.figureValue}>
                  {fmt(ultimoFechado.pages)}
                  {variacao !== null && (
                    <span
                      className={styles.delta}
                      title={`Comparado a ${penultimoFechado.month} (${fmt(penultimoFechado.pages)})`}
                    >
                      {variacao >= 0 ? "+" : "−"}
                      {Math.abs(variacao).toFixed(1).replace(".", ",")}%
                    </span>
                  )}
                </dd>
              </div>
            )}
          </dl>

          <div className={styles.chartWrap}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={monthlyUsage} margin={{ top: 4, right: 0, left: 0, bottom: 0 }}>
                <CartesianGrid stroke={c.grid} vertical={false} />
                <XAxis
                  dataKey="month"
                  stroke={c.axis}
                  tick={{ fill: c.tickText, fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                  interval="preserveStartEnd"
                />
                <YAxis
                  stroke={c.axis}
                  tick={{ fill: c.tickText, fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                  width={36}
                  tickFormatter={formatTick}
                />
                <Tooltip
                  cursor={{ fill: c.grid, opacity: 0.4 }}
                  contentStyle={{
                    background: c.tooltipBg,
                    border: `1px solid ${c.tooltipBorder}`,
                    borderRadius: 8,
                    fontSize: 12,
                  }}
                  labelStyle={{ color: c.tooltipLabel }}
                  itemStyle={{ color: c.tooltipLabel }}
                  formatter={(value) => [fmt(Number(value)), "Páginas"]}
                  labelFormatter={(label) => {
                    const entry = monthlyUsage.find((m) => m.month === label);
                    if (!entry) return String(label ?? "");
                    const extras = [
                      entry.inProgress ? "em andamento" : null,
                      entry.estimated ? `${fmt(entry.estimated)} estimadas` : null,
                      entry.devices ? `${entry.devices} equip.` : null,
                    ].filter(Boolean);
                    return `${entry.period || label}${extras.length ? ` · ${extras.join(", ")}` : ""}`;
                  }}
                />
                <Bar dataKey="pages" radius={[3, 3, 0, 0]} maxBarSize={36}>
                  {monthlyUsage.map((m) => (
                    <Cell key={m.period || m.month} fill={c.brand} fillOpacity={m.inProgress ? 0.35 : 0.85} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <p className={styles.meta}>
            {atual.period}
            {atual.devices ? ` · ${atual.devices} equipamentos` : ""}
            {/* Parte estimada: dias sem coleta no começo do mês, pela média
                diária medida (backend, monthly_report.month_pages). */}
            {atual.estimated ? ` · inclui ${fmt(atual.estimated)} estimadas` : ""}
          </p>
        </div>
      )}
    </section>
  );
}
