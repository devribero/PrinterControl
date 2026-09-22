"use client";

/**
 * Tela de Suprimentos: nível de toner das impressoras A4 do escopo atual.
 *
 * Composição (peças em components/toner/):
 * - TonerSummary: contagem por faixa, que também filtra a lista;
 * - TonerToolbar: busca (nome/IP/modelo/departamento) e ordenação;
 * - TonerRow: uma impressora, com uma barra por canal ou o motivo de não
 *   haver leitura.
 * Regras (faixas, motivos, ordenação) ficam em toner/tonerModel.ts.
 *
 * Etiquetadoras e portáteis não usam toner: ficam fora da lista e aparecem
 * só numa nota no rodapé, para ninguém achar que sumiram.
 */
import { useMemo, useState } from "react";
import type { Printer } from "../types";
import { useTheme } from "../lib/theme";
import TonerSummary from "./toner/TonerSummary";
import TonerToolbar from "./toner/TonerToolbar";
import TonerRow from "./toner/TonerRow";
import { matchesQuery, printerKind, sortEntries, toEntry, type SortKey, type TonerBand } from "./toner/tonerModel";
import styles from "./toner/Toner.module.css";

const BAND_LABEL: Record<TonerBand, string> = {
  critical: "críticos",
  low: "baixos",
  ok: "OK",
  none: "sem leitura",
};

interface TonerMonitoringProps {
  /** Frota ativa do escopo de servidor em vigor (useAppData().activeFleet). */
  printers: Printer[];
  /** host -> nome amigável do Print Server. */
  serverNames: Record<string, string>;
  /** true quando o escopo abrange mais de um servidor: mostra o servidor em cada linha. */
  showServer: boolean;
  onOpenDetails: (printer: Printer) => void;
}

function plural(n: number, one: string, many: string) {
  return `${n} ${n === 1 ? one : many}`;
}

export default function TonerMonitoring({ printers, serverNames, showServer, onOpenDetails }: TonerMonitoringProps) {
  const { theme } = useTheme();
  const [band, setBand] = useState<TonerBand | null>(null);
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState<SortKey>("level");

  const { entries, labelCount, portableCount } = useMemo(() => {
    let label = 0;
    let portable = 0;
    const a4: Printer[] = [];
    for (const p of printers) {
      const kind = printerKind(p);
      if (kind === "Etiqueta") label++;
      else if (kind === "Portatil") portable++;
      else a4.push(p);
    }
    return { entries: a4.map(toEntry), labelCount: label, portableCount: portable };
  }, [printers]);

  const counts = useMemo(() => {
    const c: Record<TonerBand, number> = { critical: 0, low: 0, ok: 0, none: 0 };
    for (const e of entries) c[e.band]++;
    return c;
  }, [entries]);

  const multipleServers = useMemo(() => new Set(entries.map((e) => e.printer.server)).size > 1, [entries]);
  const effectiveSort: SortKey = sort === "server" && !multipleServers ? "level" : sort;

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase();
    const filtered = entries.filter((e) => (band === null || e.band === band) && matchesQuery(e.printer, q));
    return sortEntries(filtered, effectiveSort);
  }, [entries, band, query, effectiveSort]);

  const serverLabel = (host: string) => {
    if (!showServer || !multipleServers) return null;
    return host ? (serverNames[host] ?? host) : "Cadastro manual";
  };

  const excludedNote = [
    labelCount > 0 ? plural(labelCount, "etiquetadora", "etiquetadoras") : null,
    portableCount > 0 ? plural(portableCount, "portátil", "portáteis") : null,
  ]
    .filter(Boolean)
    .join(" e ");

  return (
    <div className={styles.page}>
      <TonerSummary counts={counts} active={band} onToggle={(b) => setBand((cur) => (cur === b ? null : b))} />

      <section className={styles.card} aria-label="Impressoras A4">
        <TonerToolbar
          query={query}
          onQueryChange={setQuery}
          sort={effectiveSort}
          onSortChange={setSort}
          allowServerSort={multipleServers}
        />

        <div className={styles.resultBar}>
          <span>
            {visible.length === entries.length
              ? plural(entries.length, "impressora A4", "impressoras A4")
              : `${visible.length} de ${entries.length} impressoras A4`}
          </span>
          {band !== null && (
            <button type="button" className={styles.resetButton} onClick={() => setBand(null)}>
              Mostrar todas (filtro: {BAND_LABEL[band]})
            </button>
          )}
        </div>

        {visible.length > 0 ? (
          <ul className={styles.list}>
            {visible.map((entry) => (
              <TonerRow
                key={entry.printer.id}
                entry={entry}
                theme={theme}
                serverLabel={serverLabel(entry.printer.server)}
                onOpen={() => onOpenDetails(entry.printer)}
              />
            ))}
          </ul>
        ) : (
          <p className={styles.empty}>
            {entries.length === 0
              ? "Nenhuma impressora A4 neste escopo."
              : "Nenhuma impressora encontrada com esses filtros."}
          </p>
        )}

        {excludedNote && (
          <p className={styles.footnote}>
            {excludedNote} {labelCount + portableCount === 1 ? "não aparece" : "não aparecem"} aqui: não usam toner.
          </p>
        )}
      </section>
    </div>
  );
}
