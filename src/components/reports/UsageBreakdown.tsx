"use client";

/**
 * Páginas do período por departamento ou por unidade. Os dois saem do
 * mesmo campo do cadastro, "Departamento — Unidade" (ver splitDepartment):
 * agrupar por departamento junta o mesmo setor de unidades diferentes.
 */
import { useState } from "react";
import { breakdown, formatInt, formatPct, type RankedRow } from "./reportModel";
import styles from "./Reports.module.css";

const TOP_N = 12;

interface UsageBreakdownProps {
  ranked: RankedRow[];
}

export default function UsageBreakdown({ ranked }: UsageBreakdownProps) {
  const [by, setBy] = useState<"department" | "unit">("department");
  const [showAll, setShowAll] = useState(false);

  const items = breakdown(ranked, by);
  const grandTotal = items.reduce((s, i) => s + i.total, 0);
  const max = Math.max(1, ...items.map((i) => i.total));
  const visible = showAll ? items : items.slice(0, TOP_N);

  return (
    <section className={styles.card} aria-labelledby="breakdown-title">
      <header className={styles.cardHeader}>
        <h2 id="breakdown-title" className={styles.cardTitle}>
          Páginas por {by === "department" ? "departamento" : "unidade"}
        </h2>
        <div className={styles.segmented} role="group" aria-label="Agrupar por">
          <button
            type="button"
            className={styles.segment}
            aria-pressed={by === "department"}
            onClick={() => setBy("department")}
          >
            Departamento
          </button>
          <button type="button" className={styles.segment} aria-pressed={by === "unit"} onClick={() => setBy("unit")}>
            Unidade
          </button>
        </div>
      </header>

      {items.length === 0 ? (
        <p className={styles.empty}>Sem páginas no período.</p>
      ) : (
        <ul className={styles.breakdownList}>
          {visible.map((i) => (
            <li key={i.key} className={styles.breakdownRow}>
              <span className={styles.breakdownName} title={i.key}>
                {i.key}
                <span className={styles.breakdownDevices}>{i.devices} equip.</span>
              </span>
              <span className={styles.breakdownTrack} aria-hidden="true">
                <span className={styles.breakdownFill} style={{ width: `${(i.total / max) * 100}%` }} />
              </span>
              <span className={styles.breakdownTotal}>{formatInt(i.total)}</span>
              <span className={styles.breakdownPct}>{formatPct(grandTotal > 0 ? (i.total / grandTotal) * 100 : 0)}</span>
            </li>
          ))}
        </ul>
      )}

      {items.length > TOP_N && (
        <footer className={styles.cardFooter}>
          <button type="button" className={styles.textButton} onClick={() => setShowAll((v) => !v)}>
            {showAll ? `Mostrar só os ${TOP_N} maiores` : `Mostrar todos (${items.length})`}
          </button>
        </footer>
      )}
    </section>
  );
}
