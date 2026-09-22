"use client";

/**
 * Páginas por mês — colunas em CSS puro (série única, até 12 meses).
 *
 * Mostra todo o histórico disponível; os meses fora do período escolhido
 * ficam em cinza, como contexto. Codificação:
 *   - medido: cor de marca sólida;
 *   - estimado (dias sem coleta): hachura no topo da coluna;
 *   - em andamento: coluna vazada — o total ainda cresce até o fechamento.
 * Uma linha vertical marca onde termina a planilha histórica e começa a
 * coleta automática (SNMP).
 *
 * Tooltip por coluna (hover ou toque) e a tabela "Ver dados mensais" logo
 * abaixo — o gráfico nunca é a única forma de ler o número.
 */
import { useState } from "react";
import { cn } from "../../lib/cn";
import DemoDataBadge from "../DemoDataBadge";
import { formatCompact, formatInt, formatPct, type ReportMonth } from "./reportModel";
import styles from "./Reports.module.css";

interface MonthlyChartProps {
  months: ReportMonth[];
  selected: Set<string>;
  ficticio: boolean;
  scoped: boolean;
}

/** Máximo "redondo" do eixo e o passo entre as linhas de grade. */
function niceScale(max: number): { top: number; step: number } {
  if (max <= 0) return { top: 1, step: 1 };
  const rough = max / 4;
  const mag = 10 ** Math.floor(Math.log10(rough));
  const norm = rough / mag;
  const step = (norm <= 1 ? 1 : norm <= 2 ? 2 : norm <= 2.5 ? 2.5 : norm <= 5 ? 5 : 10) * mag;
  return { top: Math.ceil(max / step) * step, step };
}

function sourceLabel(m: ReportMonth): string | null {
  if (m.source === "planilha") return "Importado da planilha histórica";
  if (m.source === "snmp") return "Coleta automática (SNMP)";
  return null;
}

export default function MonthlyChart({ months, selected, ficticio, scoped }: MonthlyChartProps) {
  const [active, setActive] = useState<number | null>(null);
  const { top, step } = niceScale(Math.max(0, ...months.map((m) => m.pages)));
  const ticks: number[] = [];
  for (let v = 0; v <= top + step / 2; v += step) ticks.push(v);

  const hasEstimated = months.some((m) => (m.estimated ?? 0) > 0);
  const hasInProgress = months.some((m) => m.inProgress);
  const boundary = months.findIndex((m, i) => i > 0 && m.source === "snmp" && months[i - 1].source === "planilha");
  const n = months.length;
  const current = active !== null ? months[active] : null;

  return (
    <section className={styles.card} aria-labelledby="chart-title">
      <header className={styles.cardHeader}>
        <div className={styles.cardHeading}>
          <h2 id="chart-title" className={styles.cardTitle}>
            Páginas por mês
          </h2>
          <DemoDataBadge
            ficticio={ficticio}
            motivo="O servidor ainda não tem leituras suficientes para fechar o mês, então o consumo mensal exibido é de demonstração."
          />
        </div>
        <ul className={styles.legend}>
          <li>
            <span className={cn(styles.swatch, styles.swatchMeasured)} aria-hidden="true" />
            Medido
          </li>
          {hasEstimated && (
            <li>
              <span className={cn(styles.swatch, styles.swatchEstimated)} aria-hidden="true" />
              Estimado
            </li>
          )}
          {hasInProgress && (
            <li>
              <span className={cn(styles.swatch, styles.swatchProgress)} aria-hidden="true" />
              Em andamento
            </li>
          )}
          <li>
            <span className={cn(styles.swatch, styles.swatchOut)} aria-hidden="true" />
            Fora do período
          </li>
        </ul>
      </header>

      <div className={styles.chartBody}>
        <div className={styles.chart} aria-hidden="true" onMouseLeave={() => setActive(null)}>
          <div className={styles.yAxis}>
            {ticks.map((t) => (
              <span key={t} className={styles.yTick} style={{ bottom: `${(t / top) * 100}%` }}>
                {formatCompact(t)}
              </span>
            ))}
          </div>

          <div className={styles.plot}>
            {ticks.map((t) => (
              <span key={t} className={styles.gridLine} style={{ bottom: `${(t / top) * 100}%` }} />
            ))}

            {boundary > 0 && (
              <span className={styles.boundary} style={{ left: `${(boundary / n) * 100}%` }}>
                <span className={styles.boundaryLabel}>SNMP</span>
              </span>
            )}

            <div className={styles.columns}>
              {months.map((m, i) => {
                const est = m.estimated ?? 0;
                const estPct = m.pages > 0 ? Math.min(100, (est / m.pages) * 100) : 0;
                return (
                  <div
                    key={m.period}
                    className={cn(
                      styles.column,
                      !selected.has(m.period) && styles.columnOut,
                      m.inProgress && styles.columnProgress,
                      active === i && styles.columnActive,
                    )}
                    onMouseEnter={() => setActive(i)}
                    onClick={() => setActive(active === i ? null : i)}
                  >
                    <span className={styles.bar} style={{ height: `${(m.pages / top) * 100}%` }}>
                      {est > 0 && <span className={styles.barEstimated} style={{ height: `max(2px, ${estPct}%)` }} />}
                      <span className={styles.barMeasured} />
                    </span>
                  </div>
                );
              })}
            </div>

            {current && active !== null && (
              <div
                className={styles.tooltip}
                style={{
                  left: `${((active + 0.5) / n) * 100}%`,
                  transform: `translateX(${active < n / 3 ? "-12%" : active >= (2 * n) / 3 ? "-88%" : "-50%"})`,
                }}
              >
                <p className={styles.tooltipTitle}>
                  {current.longLabel}
                  {current.inProgress && " · em andamento"}
                </p>
                <p className={styles.tooltipValue}>{formatInt(current.pages)} páginas</p>
                {(current.estimated ?? 0) > 0 && (
                  <p className={styles.tooltipMeta}>
                    {formatInt(current.estimated ?? 0)} estimadas (
                    {formatPct(((current.estimated ?? 0) / Math.max(1, current.pages)) * 100)})
                  </p>
                )}
                <p className={styles.tooltipMeta}>{current.devices} equipamentos com dado</p>
                {sourceLabel(current) && <p className={styles.tooltipMeta}>{sourceLabel(current)}</p>}
              </div>
            )}
          </div>

          <div className={styles.xAxis}>
            {months.map((m, i) => {
              const year = /^\d{4}/.exec(m.period)?.[0];
              const showYear = year && (i === 0 || m.period.endsWith("-01"));
              return (
                <span key={m.period} className={cn(styles.xTick, !selected.has(m.period) && styles.xTickOut)}>
                  {m.label}
                  {showYear && <span className={styles.xYear}>{year}</span>}
                </span>
              );
            })}
          </div>
        </div>

        <p className={styles.footnote}>
          {boundary > 0 && "Até a linha SNMP os meses vêm da planilha histórica importada; depois, da coleta automática. "}
          {hasEstimated &&
            "A parte hachurada é estimativa dos dias sem coleta no início do mês (média diária medida). "}
          {scoped && "Com um servidor ou unidade em foco, a parte estimada não é informada pelo servidor. "}
          Um equipamento por IP — filas duplicadas não somam em dobro.
        </p>

        <details className={styles.details}>
          <summary className={styles.detailsSummary}>Ver dados mensais</summary>
          <div className={styles.scrollX}>
            <table className={styles.miniTable}>
              <thead>
                <tr>
                  <th scope="col">Mês</th>
                  <th scope="col" className={styles.num}>
                    Páginas
                  </th>
                  <th scope="col" className={styles.num}>
                    Estimadas
                  </th>
                  <th scope="col" className={styles.num}>
                    Equip.
                  </th>
                  <th scope="col">Origem</th>
                </tr>
              </thead>
              <tbody>
                {[...months].reverse().map((m) => (
                  <tr key={m.period} className={cn(!selected.has(m.period) && styles.rowOut)}>
                    <td>
                      {m.longLabel}
                      {m.inProgress && <span className={styles.tag}>em andamento</span>}
                    </td>
                    <td className={styles.num}>{formatInt(m.pages)}</td>
                    <td className={styles.num}>{m.estimated === null ? "—" : formatInt(m.estimated)}</td>
                    <td className={styles.num}>{m.devices}</td>
                    <td>{m.source === "planilha" ? "Planilha" : m.source === "snmp" ? "SNMP" : "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </details>
      </div>
    </section>
  );
}
