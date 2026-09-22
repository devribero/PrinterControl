"use client";

/**
 * Ranking de impressoras no período — as que mais (ou menos) imprimiram,
 * com departamento e unidade. Clicar no nome abre os detalhes da impressora.
 * No celular cada linha vira um cartão.
 */
import { useState } from "react";
import type { Printer } from "../../types";
import { formatInt, formatPct, type RankedRow } from "./reportModel";
import styles from "./Reports.module.css";

const TOP_N = 10;

interface PrinterRankingProps {
  ranked: RankedRow[];
  onOpenDetails: (printer: Printer) => void;
}

export default function PrinterRanking({ ranked, onOpenDetails }: PrinterRankingProps) {
  const [order, setOrder] = useState<"most" | "least">("most");
  const [showAll, setShowAll] = useState(false);

  const grandTotal = ranked.reduce((s, r) => s + r.total, 0);
  const max = Math.max(1, ...ranked.map((r) => r.total));
  const ordered = order === "most" ? ranked : [...ranked].reverse();
  const visible = showAll ? ordered : ordered.slice(0, TOP_N);

  return (
    <section className={styles.card} aria-labelledby="ranking-title">
      <header className={styles.cardHeader}>
        <div className={styles.cardHeading}>
          <h2 id="ranking-title" className={styles.cardTitle}>
            Ranking de impressoras
          </h2>
          <span className={styles.cardCount}>{ranked.length} com dado</span>
        </div>
        <div className={styles.segmented} role="group" aria-label="Ordem do ranking">
          <button type="button" className={styles.segment} aria-pressed={order === "most"} onClick={() => setOrder("most")}>
            Mais imprimem
          </button>
          <button
            type="button"
            className={styles.segment}
            aria-pressed={order === "least"}
            onClick={() => setOrder("least")}
          >
            Menos imprimem
          </button>
        </div>
      </header>

      {ranked.length === 0 ? (
        <p className={styles.empty}>Nenhuma impressora com páginas no período.</p>
      ) : (
        <table className={styles.rankTable}>
          <thead>
            <tr>
              <th scope="col" className={styles.rankPos}>
                #
              </th>
              <th scope="col">Impressora</th>
              <th scope="col">Departamento</th>
              <th scope="col">Unidade</th>
              <th scope="col" className={styles.num}>
                Páginas
              </th>
              <th scope="col" className={styles.num}>
                Participação
              </th>
            </tr>
          </thead>
          <tbody>
            {visible.map((r, idx) => {
              const pos = order === "most" ? idx + 1 : ranked.length - idx;
              return (
                <tr key={r.printer.id}>
                  <td className={styles.rankPos}>{pos}</td>
                  <td className={styles.rankName}>
                    <button type="button" className={styles.linkButton} onClick={() => onOpenDetails(r.printer)}>
                      {r.printer.name}
                    </button>
                    <span className={styles.rankMeta}>
                      {r.printer.ip}
                      {r.printer.model && ` · ${r.printer.model}`}
                      {!r.printer.active && <span className={styles.tag}>inativa</span>}
                    </span>
                  </td>
                  <td data-label="Departamento">{r.department}</td>
                  <td data-label="Unidade">{r.unit}</td>
                  <td data-label="Páginas" className={styles.num}>
                    <span className={styles.numStrong}>{formatInt(r.total)}</span>
                  </td>
                  <td data-label="Participação" className={styles.num}>
                    <span className={styles.shareCell}>
                      <span className={styles.shareTrack} aria-hidden="true">
                        <span className={styles.shareFill} style={{ width: `${(r.total / max) * 100}%` }} />
                      </span>
                      {formatPct(grandTotal > 0 ? (r.total / grandTotal) * 100 : 0)}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}

      {ranked.length > TOP_N && (
        <footer className={styles.cardFooter}>
          <button type="button" className={styles.textButton} onClick={() => setShowAll((v) => !v)}>
            {showAll ? `Mostrar só as ${TOP_N} primeiras` : `Mostrar todas (${ranked.length})`}
          </button>
        </footer>
      )}
    </section>
  );
}
