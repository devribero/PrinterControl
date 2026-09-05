/**
 * Sem libs externas — barras horizontais em CSS puro (sem recharts aqui,
 * dataset pequeno). Dados vêm do backend (Fase 12, GET /api/printers/
 * monthly-report → department_usage, real) quando disponível, senão do
 * conjunto de demonstração (data/printers.ts). Cada mês já carrega seu
 * próprio rótulo (`month`) — não há mais um array de meses fixo, porque a
 * janela real cresce mês a mês em vez de ficar travada em Jan–Jun.
 *
 * Layout do handoff (`PrinterControl v2.dc.html` L599-613): card de vidro
 * dominante, uma linha por departamento com barra fina, total e percentual
 * em monospace; o detalhamento mês a mês (expansão) é funcionalidade do app
 * e continua aqui, ausente do handoff.
 */
import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";
import type { DepartmentUsage } from "../types";
import styles from "./DepartmentBreakdown.module.css";

interface DepartmentBreakdownProps {
  data: DepartmentUsage[];
}

export default function DepartmentBreakdown({ data }: DepartmentBreakdownProps) {
  const [expanded, setExpanded] = useState<string | null>(null);
  const sorted = [...data].sort((a, b) => b.total - a.total);
  const grandTotal = sorted.reduce((sum, d) => sum + d.total, 0);
  const maxTotal = Math.max(1, ...sorted.map((d) => d.total));

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <h3 className={styles.title}>Consumo por departamento</h3>
        <span className={styles.headerNote}>Todas as unidades</span>
      </div>

      <div className={styles.list}>
        {sorted.map((d) => {
          const pct = grandTotal > 0 ? Math.round((d.total / grandTotal) * 100) : 0;
          const isOpen = expanded === d.department;
          const maxMonth = Math.max(1, ...d.monthly.map((m) => m.pages));
          return (
            <div key={d.department} className={styles.row}>
              <button onClick={() => setExpanded(isOpen ? null : d.department)} className={styles.rowButton}>
                <span className={styles.deptName} title={d.department}>
                  {d.department}
                </span>
                <span className={styles.barTrack}>
                  <span className={styles.barFill} style={{ width: `${(d.total / maxTotal) * 100}%` }} />
                </span>
                <span className={styles.total}>{d.total.toLocaleString("pt-BR")}</span>
                <span className={styles.pct}>{pct}%</span>
                <span className={styles.chevron}>{isOpen ? <ChevronUp size={15} /> : <ChevronDown size={15} />}</span>
              </button>

              {isOpen && (
                <div className={styles.monthly}>
                  {d.monthly.map((m) => (
                    <div key={m.period} className={styles.monthCol}>
                      <span className={styles.monthValue}>{m.pages.toLocaleString("pt-BR")}</span>
                      <div className={styles.monthBar} style={{ height: `${8 + (m.pages / maxMonth) * 56}px` }} />
                      <span className={styles.monthLabel}>{m.month}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
