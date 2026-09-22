"use client";

/**
 * Resumo por faixa que também é o filtro da lista: clicar numa faixa mostra
 * só ela; clicar de novo volta para todas. `aria-pressed` diz o estado.
 */
import type { TonerBand } from "./tonerModel";
import { CRITICAL_MAX, LOW_MAX } from "./tonerModel";
import { cn } from "../../lib/cn";
import styles from "./Toner.module.css";

const ITEMS: { band: TonerBand; label: string; hint: string; tone: string }[] = [
  { band: "critical", label: "Críticos", hint: `≤ ${CRITICAL_MAX}%`, tone: styles.toneCritical },
  { band: "low", label: "Baixos", hint: `≤ ${LOW_MAX}%`, tone: styles.toneLow },
  { band: "ok", label: "OK", hint: `> ${LOW_MAX}%`, tone: styles.toneOk },
  { band: "none", label: "Sem leitura", hint: "de toner", tone: styles.toneNone },
];

interface TonerSummaryProps {
  counts: Record<TonerBand, number>;
  active: TonerBand | null;
  onToggle: (band: TonerBand) => void;
}

export default function TonerSummary({ counts, active, onToggle }: TonerSummaryProps) {
  return (
    <div className={styles.summary} role="group" aria-label="Filtrar por nível de toner">
      {ITEMS.map((item) => (
        <button
          key={item.band}
          type="button"
          aria-pressed={active === item.band}
          onClick={() => onToggle(item.band)}
          className={cn(styles.summaryItem, active === item.band && styles.summaryItemActive)}
        >
          <span className={cn(styles.summaryMark, item.tone)} aria-hidden="true" />
          <span className={styles.summaryValue}>{counts[item.band]}</span>
          <span className={styles.summaryText}>
            <span className={styles.summaryLabel}>{item.label}</span>
            <span className={styles.summaryHint}>{item.hint}</span>
          </span>
        </button>
      ))}
    </div>
  );
}
