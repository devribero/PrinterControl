"use client";

import type { KeyboardEvent } from "react";
import type { Printer } from "../../types";
import PrinterStatusBadge from "../PrinterStatusBadge";
import { cn } from "../../lib/cn";
import TonerCell from "./TonerCell";
import PrinterRowActions from "./PrinterRowActions";
import { STATUS_LABEL, absoluteReading, relativeReading } from "./fleetModel";
import styles from "./Fleet.module.css";

interface FleetTableProps {
  printers: Printer[];
  onOpenDetails: (printer: Printer) => void;
  /** Coluna Servidor: só quando o escopo tem mais de um servidor. */
  showServer: boolean;
  serverLabel: (host: string) => string;
  /** Unidade do servidor (sob o departamento); null quando não há. */
  unitLabel: (host: string) => string | null;
  /** Referência do "há X min": a última coleta (render puro). */
  now: Date;
  isStale: (printer: Printer) => boolean;
  emptyMessage: string;
}

const numberFormat = new Intl.NumberFormat("pt-BR");

/**
 * Tabela da frota. Colunas somem por largura (Servidor/Contador < 1280px,
 * IP/Departamento < 1024px — IP e departamento passam para baixo do nome) e,
 * abaixo de 640px, cada linha vira um cartão (Fleet.module.css). Assim a
 * página nunca rola na horizontal.
 */
export default function FleetTable({
  printers,
  onOpenDetails,
  showServer,
  serverLabel,
  unitLabel,
  now,
  isStale,
  emptyMessage,
}: FleetTableProps) {
  function onRowKeyDown(e: KeyboardEvent<HTMLTableRowElement>, p: Printer) {
    if (e.target !== e.currentTarget) return;
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      onOpenDetails(p);
    }
  }

  const columns = showServer ? 9 : 8;

  return (
    <div className={styles.tableWrap}>
      <table className={styles.table}>
        <thead>
          <tr>
            <th scope="col">Impressora</th>
            <th scope="col">Status</th>
            <th scope="col" className={styles.colIp}>
              IP
            </th>
            <th scope="col" className={styles.colDept}>
              Departamento
            </th>
            {showServer && (
              <th scope="col" className={styles.colServer}>
                Servidor
              </th>
            )}
            <th scope="col">Toner</th>
            <th scope="col" className={cn(styles.colCounter, styles.alignRight)}>
              Contador
            </th>
            <th scope="col">Última leitura</th>
            <th scope="col">
              <span className={styles.srOnly}>Ações</span>
            </th>
          </tr>
        </thead>
        <tbody>
          {printers.map((p) => {
            const unit = unitLabel(p.server);
            const stale = isStale(p);
            return (
              <tr
                key={p.id}
                onClick={() => onOpenDetails(p)}
                onKeyDown={(e) => onRowKeyDown(e, p)}
                tabIndex={0}
                aria-label={`${p.name}, ${STATUS_LABEL[p.status]} — abrir detalhes`}
                className={styles.row}
              >
                <td className={styles.cellName}>
                  <span className={styles.name} title={p.name}>
                    {p.name}
                  </span>
                  {p.model && (
                    <span className={styles.sub} title={p.model}>
                      {p.model}
                    </span>
                  )}
                  {/* IP · departamento · servidor quando as colunas não cabem. */}
                  <span className={styles.meta}>
                    <span className={styles.mono}>{p.ip}</span>
                    {p.department && ` · ${p.department}`}
                    {showServer && <span className={styles.metaServer}> · {serverLabel(p.server)}</span>}
                  </span>
                </td>
                <td className={styles.cellStatus}>
                  <PrinterStatusBadge status={p.status} />
                </td>
                <td className={cn(styles.colIp, styles.mono)}>{p.ip}</td>
                <td className={styles.colDept}>
                  <span className={styles.clip} title={p.department}>
                    {p.department || "—"}
                  </span>
                  {unit && <span className={styles.sub}>{unit}</span>}
                </td>
                {showServer && (
                  <td className={styles.colServer}>
                    <span className={styles.clip} title={p.server || undefined}>
                      {serverLabel(p.server)}
                    </span>
                  </td>
                )}
                <td className={styles.cellToner}>
                  <TonerCell toner={p.toner} />
                </td>
                <td className={cn(styles.colCounter, styles.alignRight, styles.mono)}>
                  {p.pagesPrinted > 0 ? numberFormat.format(p.pagesPrinted) : "—"}
                </td>
                <td className={styles.cellReading}>
                  <span
                    className={cn(styles.reading, stale && styles.readingStale)}
                    title={[absoluteReading(p), stale ? "Leitura antiga: pode não refletir o estado atual" : null]
                      .filter(Boolean)
                      .join(" — ") || undefined}
                  >
                    {relativeReading(p, now)}
                  </span>
                </td>
                <td className={styles.cellActions}>
                  <PrinterRowActions printer={p} />
                </td>
              </tr>
            );
          })}
          {printers.length === 0 && (
            <tr className={styles.emptyRow}>
              <td colSpan={columns} className={styles.empty}>
                {emptyMessage}
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
