"use client";

/**
 * Sem libs externas. Um bloco por mês (a janela cresce mês a mês) com o total
 * de páginas daquele ciclo — a mesma soma que alimenta o gráfico "Consumo de
 * páginas", só que aqui cada mês vira um indicador próprio, fácil de comparar
 * de relance.
 *
 * Layout do handoff (`PrinterControl v2.dc.html` L588-596): uma faixa única de
 * vidro com os meses lado a lado, mês corrente destacado em `--tint-link` —
 * não mais um card com título e grade de cards internos.
 */
import type { MonthlyUsageEntry } from "../types";
import { cn } from "../lib/cn";
import DemoDataBadge from "./DemoDataBadge";
import styles from "./MonthlyCounters.module.css";

interface MonthlyCountersProps {
  data: MonthlyUsageEntry[];
  /** True quando `data` veio do conjunto de demonstração, não do backend. */
  ficticio?: boolean;
}

export default function MonthlyCounters({ data, ficticio = false }: MonthlyCountersProps) {
  if (data.length === 0) return null;

  return (
    <div className={styles.strip}>
      {data.map((m, i) => {
        const prev = data[i - 1];
        const delta = prev && prev.pages > 0 ? ((m.pages - prev.pages) / prev.pages) * 100 : null;
        const deltaTone = delta === null ? styles.deltaFaint : delta >= 0 ? styles.deltaSuccess : styles.deltaCritical;
        const current = i === data.length - 1;
        return (
          <div key={m.month} className={cn(styles.month, current && styles.monthCurrent)} title={m.period}>
            <p className={styles.monthLabel}>{m.month}</p>
            <p className={styles.monthValue}>
              {m.pages.toLocaleString("pt-BR")}{" "}
              <span className={cn(styles.delta, deltaTone)}>
                {delta === null ? "referência" : `${delta >= 0 ? "+" : ""}${delta.toFixed(1)}%`}
              </span>
            </p>
          </div>
        );
      })}
      {ficticio && (
        <div className={styles.badgeSlot}>
          <DemoDataBadge
            ficticio={ficticio}
            motivo="O servidor ainda não tem leituras suficientes para fechar o mês, então o consumo mensal exibido é de demonstração."
          />
        </div>
      )}
    </div>
  );
}
