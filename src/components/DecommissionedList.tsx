/**
 * Sem libs externas. Fase 18: passou a aceitar tanto o conjunto de
 * demonstração (data/printers.ts) quanto o real (Printer.active=false do
 * backend — impressoras que sumiram da última sincronização com o Print
 * Server). Não é exatamente "devolvida/baixada" no sentido formal, mas é o
 * dado real mais próximo que o cadastro atual tem — daí o título e a
 * legenda mais neutros que a versão anterior (que só existia com dado de
 * demonstração e falava em "devolvida").
 *
 * Layout do handoff (`PrinterControl v2.dc.html` L640-666): card de vidro com
 * contagem em monospace no cabeçalho e tabela de quatro colunas.
 */
import type { DecommissionedPrinter } from "../types";
import { parseApiDate } from "../lib/adaptApi";
import styles from "./DecommissionedList.module.css";

interface DecommissionedListProps {
  data: DecommissionedPrinter[];
}

function formatarData(iso: string | null): string {
  if (!iso) return "—";
  // parseApiDate e nao `new Date` (QA-09): o backend serializa UTC sem
  // fuso, e `new Date` de uma string assim assume hora LOCAL — em
  // America/Sao_Paulo isso adiantava todo horario exibido em 3h.
  const data = parseApiDate(iso);
  if (!data) return "—";
  return data.toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit", year: "numeric" });
}

export default function DecommissionedList({ data }: DecommissionedListProps) {
  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <h3 className={styles.title}>Impressoras inativas</h3>
        <span className={styles.count}>{data.length} equipamentos</span>
      </div>

      <div className={styles.tableWrap}>
        <table className={styles.table}>
          <thead>
            <tr className={styles.theadRow}>
              <th className={styles.th}>Modelo</th>
              <th className={styles.th}>Departamento / origem</th>
              <th className={styles.th}>Endereço</th>
              <th className={`${styles.th} ${styles.thRight}`}>Inativa desde</th>
            </tr>
          </thead>
          <tbody>
            {data.map((p, i) => (
              <tr key={`${p.ip}-${i}`} className={styles.tr}>
                <td className={`${styles.td} ${styles.tdModel}`}>{p.model}</td>
                <td className={styles.td}>{p.department}</td>
                <td className={`${styles.td} ${styles.tdMono}`}>{p.ip}</td>
                <td className={`${styles.td} ${styles.tdMono} ${styles.tdRight} ${styles.tdFaint}`}>
                  {formatarData(p.deactivatedAt)}
                </td>
              </tr>
            ))}
            {data.length === 0 && (
              <tr>
                <td colSpan={4} className={styles.empty}>
                  Nenhuma impressora inativa no cadastro.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
