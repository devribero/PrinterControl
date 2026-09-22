"use client";

/**
 * Drivers em uso nas filas ATIVAS do escopo, do mais usado para o menos.
 * Leitura pura do que o sync já grava (Get-Printer DriverName) — nada é
 * instalado nem alterado nos print servers por aqui: instalar driver lá
 * exige admin no servidor, e um driver ruim derruba o spooler do site.
 */
import { useMemo } from "react";
import { cn } from "../../lib/cn";
import { isGenericDriver } from "../../lib/printerInstall";
import type { Printer } from "../../types";
import shared from "./shared.module.css";
import styles from "./tables.module.css";

interface DriversCardProps {
  printers: Printer[];
  /** Complemento do subtítulo, ex.: " de SRV01". */
  scopeLabel: string;
}

export default function DriversCard({ printers, scopeLabel }: DriversCardProps) {
  const drivers = useMemo(() => {
    const contagem = new Map<string, number>();
    for (const p of printers) {
      if (!p.active || !p.driverName) continue;
      contagem.set(p.driverName, (contagem.get(p.driverName) ?? 0) + 1);
    }
    return [...contagem.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
  }, [printers]);

  if (drivers.length === 0) return null;

  return (
    <section className={shared.card} aria-labelledby="network-drivers-title">
      <div className={shared.cardHeader}>
        <div className={shared.cardHeaderText}>
          <h2 id="network-drivers-title" className={shared.cardTitle}>
            Drivers em uso
          </h2>
          <p className={shared.cardSubtitle}>
            {drivers.length} driver(es) nas filas ativas{scopeLabel}. Só leitura: instalar driver no servidor
            exige administrador do print server.
          </p>
        </div>
      </div>
      <div className={styles.tableWrap}>
        <table className={styles.table}>
          <thead>
            <tr className={styles.theadRow}>
              <th className={styles.thFirst}>Driver</th>
              <th className={cn(styles.th, styles.numeric)}>Filas</th>
            </tr>
          </thead>
          <tbody>
            {drivers.map(([driver, filas]) => (
              <tr key={driver} className={styles.row}>
                <td className={styles.tdFirst}>
                  {driver}
                  {isGenericDriver(driver) && (
                    <span
                      className={styles.tag}
                      title="Só repassa texto cru: normal para etiquetadora que recebe comandos prontos, suspeito para impressora A4."
                    >
                      genérico
                    </span>
                  )}
                </td>
                <td className={cn(styles.td, styles.numeric)} data-label="Filas">
                  {filas}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
