"use client";

/**
 * Filas encontradas por uma descoberta. Só exibição — o cabeçalho, o resumo
 * e as ações ficam no DiscoveryPanel que envolve esta tabela.
 */
import { cn } from "../../lib/cn";
import type { DiscoveredPrinter } from "../../types";
import shared from "./shared.module.css";
import styles from "./tables.module.css";

function estado(printer: DiscoveredPrinter): { label: string; dot: string } {
  if (printer.statusReason === "invalid_or_missing_ip") return { label: "Sem IP", dot: styles.stateWarning };
  if (printer.reachable === false) return { label: "Offline", dot: styles.stateOffline };
  if (printer.snmpResponded) return { label: "SNMP OK", dot: styles.stateOnline };
  return { label: "Ping OK, SNMP sem resposta", dot: styles.stateWarning };
}

export default function DiscoveryResults({ printers }: { printers: DiscoveredPrinter[] }) {
  if (printers.length === 0) {
    return <p className={shared.emptyState}>O servidor não publicou nenhuma fila de impressão.</p>;
  }

  return (
    <div className={styles.tableWrap}>
      <table className={styles.table} aria-label="Filas encontradas na descoberta">
        <thead>
          <tr className={styles.theadRow}>
            <th className={styles.thFirst}>Fila</th>
            <th className={styles.th}>IP</th>
            <th className={styles.th}>Driver</th>
            <th className={styles.th}>Estado</th>
            <th className={cn(styles.th, styles.numeric)}>Contador</th>
          </tr>
        </thead>
        <tbody>
          {printers.map((printer) => {
            const e = estado(printer);
            return (
              <tr key={`${printer.server}:${printer.name}`} className={styles.row}>
                <td className={styles.tdFirst}>
                  {printer.name}
                  {printer.portName && <span className={styles.sub}>{printer.portName}</span>}
                </td>
                <td className={cn(styles.td, styles.mono)} data-label="IP">
                  {printer.ip ?? "Não encontrado"}
                </td>
                <td className={styles.td} data-label="Driver">
                  {printer.driverName || "Não informado"}
                </td>
                <td className={styles.td} data-label="Estado">
                  <span className={styles.state}>
                    <span className={cn(styles.stateDot, e.dot)} aria-hidden="true" />
                    {e.label}
                  </span>
                </td>
                <td className={cn(styles.td, styles.numeric)} data-label="Contador">
                  {printer.snmpResponded ? (printer.pageCount?.toLocaleString("pt-BR") ?? "Sem contador") : "—"}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
