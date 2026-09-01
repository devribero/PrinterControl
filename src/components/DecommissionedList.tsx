/**
 * Sem libs externas. Fase 18: passou a aceitar tanto o conjunto de
 * demonstração (data/printers.ts) quanto o real (Printer.active=false do
 * backend — impressoras que sumiram da última sincronização com o Print
 * Server). Não é exatamente "devolvida/baixada" no sentido formal, mas é o
 * dado real mais próximo que o cadastro atual tem — daí o título e a
 * legenda mais neutros que a versão anterior (que só existia com dado de
 * demonstração e falava em "devolvida").
 */
import { ArchiveRestore } from "lucide-react";
import type { DecommissionedPrinter } from "../types";
import styles from "./DecommissionedList.module.css";

interface DecommissionedListProps {
  data: DecommissionedPrinter[];
}

function formatarData(iso: string | null): string {
  if (!iso) return "—";
  const data = new Date(iso);
  if (Number.isNaN(data.getTime())) return "—";
  return data.toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit", year: "numeric" });
}

export default function DecommissionedList({ data }: DecommissionedListProps) {
  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <div className={styles.iconWrap}>
          <ArchiveRestore size={17} />
        </div>
        <div>
          <h2 className={styles.title}>Impressoras Inativas</h2>
          <p className={styles.subtitle}>
            {data.length} equipamentos — não apareceram na última sincronização com o Print Server.
          </p>
        </div>
      </div>

      <div className={styles.tableWrap}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th className={styles.th}>Modelo</th>
              <th className={styles.th}>Departamento / Origem</th>
              <th className={styles.th}>IP</th>
              <th className={styles.th}>Inativa desde</th>
            </tr>
          </thead>
          <tbody>
            {data.map((p, i) => (
              <tr key={`${p.ip}-${i}`} className={styles.tr}>
                <td className={`${styles.td} ${styles.tdModel}`}>{p.model}</td>
                <td className={`${styles.td} ${styles.tdSoft}`}>{p.department}</td>
                <td className={`${styles.td} ${styles.tdSoft}`}>{p.ip}</td>
                <td className={`${styles.td} ${styles.tdFaint}`}>{formatarData(p.deactivatedAt)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
