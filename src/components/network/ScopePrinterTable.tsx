"use client";

/**
 * Impressoras cadastradas no escopo selecionado. `printers` JÁ vem escopado
 * pelo AppDataProvider (Todos = frota inteira; servidor = só as dele) — não
 * há filtro a aplicar aqui, e aplicar um segundo arriscaria divergir do
 * resto do painel.
 */
import { Printer as PrinterIcon } from "lucide-react";
import { cn } from "../../lib/cn";
import type { Printer, PrintServer, Unit } from "../../types";
import shared from "./shared.module.css";
import styles from "./tables.module.css";

const ESTADO: Record<string, { label: string; dot: string }> = {
  online: { label: "Online", dot: styles.stateOnline },
  atencao: { label: "Atenção", dot: styles.stateWarning },
  offline: { label: "Offline", dot: styles.stateOffline },
};

interface ScopePrinterTableProps {
  printers: Printer[];
  selected: PrintServer | null;
  serverScope: string | null;
  scopeUnit: Unit | null;
  usingRealData: boolean;
}

export default function ScopePrinterTable({
  printers,
  selected,
  serverScope,
  scopeUnit,
  usingRealData,
}: ScopePrinterTableProps) {
  // Escopo com mais de um servidor (todos, ou uma unidade): a tabela precisa
  // dizer de onde veio cada impressora.
  const mostrarServidor = serverScope === null || scopeUnit !== null;

  const titulo = selected
    ? `Impressoras em ${selected.host}`
    : serverScope === ""
      ? "Impressoras sem Print Server"
      : scopeUnit
        ? `Impressoras da unidade ${scopeUnit.name}`
        : "Impressoras de todos os servidores";

  const ativas = printers.filter((p) => p.active).length;

  let vazio: string;
  if (selected && !selected.active) vazio = "Nenhuma impressora cadastrada. O servidor está desativado.";
  else if (selected && selected.mode === "real" && !selected.lastSyncAt && selected.lastStatus !== "error")
    vazio = "A primeira sincronização automática ainda está rodando. As impressoras aparecem aqui quando ela terminar.";
  else if (selected)
    vazio = "Nenhuma impressora cadastrada neste servidor. Use Descobrir filas para ver o que ele publica.";
  else if (scopeUnit && scopeUnit.serverCount === 0)
    vazio = "Esta unidade ainda não tem Print Server. Associe um pela opção Editar no menu do servidor.";
  else vazio = "Nenhuma impressora no cadastro.";

  return (
    <section className={shared.card} aria-labelledby="network-printers-title">
      <div className={shared.cardHeader}>
        <div className={shared.cardHeaderText}>
          <h2 id="network-printers-title" className={shared.cardTitle}>
            {titulo}
          </h2>
          <p className={shared.cardSubtitle}>
            {ativas} ativa(s) de {printers.length} no cadastro
            {usingRealData ? "" : " · dados de demonstração"}
          </p>
        </div>
      </div>

      {printers.length === 0 ? (
        <div className={shared.emptyState}>
          <PrinterIcon size={28} className={shared.emptyIcon} />
          <span>{vazio}</span>
        </div>
      ) : (
        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <thead>
              <tr className={styles.theadRow}>
                <th className={styles.thFirst}>Nome</th>
                {mostrarServidor && <th className={styles.th}>Servidor</th>}
                <th className={styles.th}>IP</th>
                <th className={styles.th}>Modelo</th>
                <th className={styles.th}>Departamento</th>
                <th className={styles.th}>Estado</th>
                <th className={styles.th}>Cadastro</th>
              </tr>
            </thead>
            <tbody>
              {printers.map((printer) => {
                const estado = ESTADO[printer.status] ?? { label: printer.status, dot: "" };
                return (
                  <tr key={printer.id} className={cn(styles.row, !printer.active && styles.inactive)}>
                    <td className={styles.tdFirst}>{printer.name}</td>
                    {mostrarServidor && (
                      <td className={styles.td} data-label="Servidor">
                        {printer.server || "—"}
                      </td>
                    )}
                    <td className={cn(styles.td, styles.mono)} data-label="IP">
                      {printer.ip}
                    </td>
                    <td className={styles.td} data-label="Modelo">
                      {printer.model}
                    </td>
                    <td className={styles.td} data-label="Departamento">
                      {printer.department || "—"}
                    </td>
                    <td className={styles.td} data-label="Estado">
                      <span className={styles.state}>
                        <span className={cn(styles.stateDot, estado.dot)} aria-hidden="true" />
                        {estado.label}
                      </span>
                    </td>
                    <td className={styles.td} data-label="Cadastro">
                      {printer.active ? "Ativa" : "Inativa"}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
