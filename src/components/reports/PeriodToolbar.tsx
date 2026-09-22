"use client";

import { LAST_OPTIONS, type PeriodSelection, type ReportMonth } from "./reportModel";
import styles from "./Reports.module.css";

interface PeriodToolbarProps {
  months: ReportMonth[];
  selection: PeriodSelection;
  onChange: (sel: PeriodSelection) => void;
  scopeLabel: string;
  periodLabel: string;
}

export default function PeriodToolbar({ months, selection, onChange, scopeLabel, periodLabel }: PeriodToolbarProps) {
  const newestFirst = [...months].reverse();

  return (
    <div className={styles.toolbar}>
      <div className={styles.toolbarControls}>
        <div className={styles.segmented} role="group" aria-label="Período">
          {LAST_OPTIONS.map((n) => (
            <button
              key={n}
              type="button"
              className={styles.segment}
              aria-pressed={selection.kind === "last" && selection.count === n}
              onClick={() => onChange({ kind: "last", count: n })}
            >
              {n} meses
            </button>
          ))}
        </div>

        <label className={styles.monthField}>
          <span className={styles.srOnly}>Mês específico</span>
          <select
            className={styles.select}
            value={
              selection.kind === "month" && months.some((m) => m.period === selection.period) ? selection.period : ""
            }
            onChange={(e) => {
              if (e.target.value) onChange({ kind: "month", period: e.target.value });
            }}
          >
            <option value="">Mês específico…</option>
            {newestFirst.map((m) => (
              <option key={m.period} value={m.period}>
                {m.longLabel}
                {m.inProgress ? " (em andamento)" : ""}
              </option>
            ))}
          </select>
        </label>
      </div>

      <p className={styles.toolbarContext}>
        <span>{scopeLabel}</span>
        <span aria-hidden="true" className={styles.dotSep}>·</span>
        <span>{periodLabel}</span>
      </p>
    </div>
  );
}
