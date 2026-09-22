"use client";

/**
 * Impressoras inativas do escopo (Printer.active=false: sumiram da última
 * sincronização com o Print Server). Informação secundária na tela de
 * relatórios — fica recolhida por padrão. No celular a tabela vira cartões.
 */
import { ChevronDown } from "lucide-react";
import type { DecommissionedPrinter } from "../../types";
import { parseApiDate } from "../../lib/adaptApi";
import styles from "./Reports.module.css";

function formatarData(iso: string | null): string {
  if (!iso) return "—";
  // parseApiDate e nao `new Date` (QA-09): o backend serializa UTC sem fuso.
  const data = parseApiDate(iso);
  if (!data) return "—";
  return data.toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit", year: "numeric" });
}

export default function DecommissionedList({ data }: { data: DecommissionedPrinter[] }) {
  return (
    <details className={`${styles.card} ${styles.collapsible}`}>
      <summary className={styles.collapsibleSummary}>
        <span className={styles.cardTitle}>Impressoras inativas</span>
        <span className={styles.cardCount}>{data.length}</span>
        <ChevronDown size={16} aria-hidden="true" className={styles.collapsibleIcon} />
      </summary>

      {data.length === 0 ? (
        <p className={styles.empty}>Nenhuma impressora inativa no cadastro.</p>
      ) : (
        <table className={styles.cardTable}>
          <thead>
            <tr>
              <th scope="col">Modelo</th>
              <th scope="col">Departamento / origem</th>
              <th scope="col">Endereço</th>
              <th scope="col" className={styles.num}>
                Inativa desde
              </th>
            </tr>
          </thead>
          <tbody>
            {data.map((p, i) => (
              <tr key={`${p.ip}-${i}`}>
                <td className={styles.cardTableLead}>{p.model || "Modelo não informado"}</td>
                <td data-label="Departamento">{p.department || "—"}</td>
                <td data-label="Endereço" className={styles.mono}>
                  {p.ip}
                </td>
                <td data-label="Inativa desde" className={`${styles.num} ${styles.mono}`}>
                  {formatarData(p.deactivatedAt)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </details>
  );
}
