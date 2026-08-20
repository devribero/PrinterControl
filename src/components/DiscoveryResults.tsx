"use client";

import type { DiscoveredPrinter } from "../types";
import styles from "./DiscoveryResults.module.css";

interface DiscoveryResultsProps {
  printers: DiscoveredPrinter[];
  source: string | null;
  server: string | null;
}

function statusLabel(printer: DiscoveredPrinter) {
  if (printer.statusReason === "invalid_or_missing_ip") return "Sem IP";
  if (printer.reachable === false) return "Offline";
  if (printer.snmpResponded) return "SNMP OK";
  return "Ping OK / SNMP sem resposta";
}

export default function DiscoveryResults({ printers, source, server }: DiscoveryResultsProps) {
  return (
    <section className={styles.root} aria-label="Resultado da descoberta">
      <div className={styles.header}>
        <div>
          <p className={styles.eyebrow}>Descoberta temporária</p>
          <h2 className={styles.title}>Resultado do Print Server</h2>
        </div>
        <p className={styles.meta}>{server} · {source === "print_server_real" ? "real" : "mock"}</p>
      </div>
      <div className={styles.tableWrap}>
        <table className={styles.table}>
          <thead>
            <tr><th>Fila</th><th>IP</th><th>Driver</th><th>Estado</th><th>SNMP</th></tr>
          </thead>
          <tbody>
            {printers.map((printer) => (
              <tr key={`${printer.server}:${printer.name}`}>
                <td><strong>{printer.name}</strong><span>{printer.portName}</span></td>
                <td>{printer.ip ?? "Não encontrado"}</td>
                <td>{printer.driverName || "Não informado"}</td>
                <td>{statusLabel(printer)}</td>
                <td>{printer.snmpResponded ? `${printer.pageCount ?? "Sem contador"}` : "Não consultado"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}