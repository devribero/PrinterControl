/**
 * Sem libs externas além de lucide-react (ícones). Ordena as impressoras que
 * têm histórico mensal (printer.monthlyPages, ver lib/fetchMonthlyReport.ts)
 * pelo total de páginas no período e mostra as 5 que mais e as 5 que menos
 * imprimem — pensado pra achar rápido quem precisa de upgrade de capacidade
 * ou quem talvez nem devesse estar mais em operação.
 *
 * Layout do handoff (`PrinterControl v2.dc.html` L616-635): coluna lateral de
 * 300px, cada ranking é uma seção sem card — cabeçalho com ícone colorido
 * sobre linha divisória e itens "N. Nome" com total mono e barra de 2px.
 */
import { ArrowDownWideNarrow, ArrowUpWideNarrow } from "lucide-react";
import { cn } from "../lib/cn";
import styles from "./PrinterRanking.module.css";
import type { Printer } from "../types";

interface RankedPrinter {
  printer: Printer;
  total: number;
}

function rankPrinters(printers: Printer[]): RankedPrinter[] {
  return printers
    .filter((p) => p.monthlyPages && p.monthlyPages.length > 0)
    .map((p) => ({ printer: p, total: p.monthlyPages!.reduce((sum, m) => sum + m.pages, 0) }))
    .sort((a, b) => b.total - a.total);
}

function RankList({ title, icon, items, tone, onOpenDetails }: {
  title: string;
  icon: React.ReactNode;
  items: RankedPrinter[];
  tone: "brand" | "faint";
  onOpenDetails: (p: Printer) => void;
}) {
  const max = Math.max(1, ...items.map((i) => i.total));
  return (
    <section className={styles.section}>
      <div className={styles.header}>
        <span className={cn(styles.icon, tone === "brand" ? styles.iconBrand : styles.iconFaint)}>{icon}</span>
        <h3 className={styles.title}>{title}</h3>
      </div>
      <div className={styles.list}>
        {items.map(({ printer, total }, i) => (
          <button key={printer.id} onClick={() => onOpenDetails(printer)} className={styles.item}>
            <span className={styles.itemTop}>
              <span className={styles.name}>
                {i + 1}. {printer.name}
              </span>
              <span className={styles.total}>{total.toLocaleString("pt-BR")}</span>
            </span>
            <span className={styles.barTrack}>
              <span
                className={cn(styles.barFill, tone === "brand" ? styles.barFillBrand : styles.barFillFaint)}
                style={{ width: `${(total / max) * 100}%` }}
              />
            </span>
          </button>
        ))}
        {items.length === 0 && <p className={styles.empty}>Sem dados suficientes.</p>}
      </div>
    </section>
  );
}

interface PrinterRankingProps {
  printers: Printer[];
  onOpenDetails: (printer: Printer) => void;
}

export default function PrinterRanking({ printers, onOpenDetails }: PrinterRankingProps) {
  const ranked = rankPrinters(printers);
  const top = ranked.slice(0, 5);
  const bottom = ranked.slice(-5).reverse();

  if (ranked.length === 0) return null;

  return (
    <div className={styles.stack}>
      <RankList
        title="Impressoras que mais imprimem"
        icon={<ArrowUpWideNarrow size={14} />}
        items={top}
        tone="brand"
        onOpenDetails={onOpenDetails}
      />
      <RankList
        title="Impressoras que menos imprimem"
        icon={<ArrowDownWideNarrow size={14} />}
        items={bottom}
        tone="faint"
        onOpenDetails={onOpenDetails}
      />
    </div>
  );
}
