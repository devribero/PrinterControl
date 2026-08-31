/**
 * Sem libs externas — barras horizontais em CSS puro (sem recharts aqui,
 * dataset pequeno). Dados vêm do backend (Fase 12, GET /api/printers/
 * monthly-report → department_usage, real) quando disponível, senão do
 * conjunto de demonstração (data/printers.ts). Cada mês já carrega seu
 * próprio rótulo (`month`) — não há mais um array de meses fixo, porque a
 * janela real cresce mês a mês em vez de ficar travada em Jan–Jun.
 */
import { useState } from "react";
import { ChevronDown, ChevronUp, Building2 } from "lucide-react";
import type { DepartmentUsage } from "../types";
import styles from "./DepartmentBreakdown.module.css";

interface DepartmentBreakdownProps {
  data: DepartmentUsage[];
}

export default function DepartmentBreakdown({ data }: DepartmentBreakdownProps) {
  const [expanded, setExpanded] = useState<string | null>(null);
  const sorted = [...data].sort((a, b) => b.total - a.total);
  const grandTotal = sorted.reduce((sum, d) => sum + d.total, 0);
  const maxTotal = Math.max(...sorted.map((d) => d.total));

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <div className={styles.iconWrap}>
          <Building2 size={17} />
        </div>
        <div>
          <h2 className={styles.title}>Consumo por Departamento</h2>
          <p className={styles.subtitle}>Total de páginas por área, todas as unidades.</p>
        </div>
      </div>

      <div className={styles.list}>
        {sorted.map((d) => {
          const pct = grandTotal > 0 ? Math.round((d.total / grandTotal) * 100) : 0;
          const isOpen = expanded === d.department;
          const maxMonth = Math.max(1, ...d.monthly.map((m) => m.pages));
          return (
            <div key={d.department} className={styles.row}>
              <button
                onClick={() => setExpanded(isOpen ? null : d.department)}
                className={styles.rowButton}
              >
                <div className={styles.deptName} title={d.department}>
                  {d.department}
                </div>
                <div className={styles.barTrack}>
                  <div
                    className={styles.barFill}
                    style={{ width: `${(d.total / maxTotal) * 100}%` }}
                  />
                </div>
                <div className={styles.total}>
                  {d.total.toLocaleString("pt-BR")}
                </div>
                <div className={styles.pct}>{pct}%</div>
                {isOpen ? <ChevronUp size={16} className={styles.chevron} /> : <ChevronDown size={16} className={styles.chevron} />}
              </button>

              {isOpen && (
                <div className={styles.monthly}>
                  {d.monthly.map((m) => (
                    <div key={m.period} className={styles.monthCol}>
                      <span className={styles.monthValue}>{m.pages.toLocaleString("pt-BR")}</span>
                      <div
                        className={styles.monthBar}
                        style={{ height: `${8 + (m.pages / maxMonth) * 56}px` }}
                      />
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
