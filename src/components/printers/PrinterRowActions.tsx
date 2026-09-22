"use client";

import { Globe, Printer as PrinterIcon } from "lucide-react";
import type { Printer } from "../../types";
import { useAppData } from "../../lib/app-data";
import { testPrintBlockReason } from "../../lib/testPrint";
import styles from "./Fleet.module.css";

/**
 * Ações da linha. Detalhes = clique na própria linha (PrinterDetailsModal).
 * A página de teste só é PEDIDA aqui: confirmação e envio ficam no
 * TestPrintDialog global, o mesmo que o modal de detalhes usa.
 */
export default function PrinterRowActions({ printer }: { printer: Printer }) {
  const { can, usingRealData, requestTestPrint } = useAppData();
  const blocked = testPrintBlockReason(printer, { canOperate: can.canOperate, usingRealData });

  return (
    <div className={styles.actions}>
      <a
        href={`http://${printer.ip}`}
        target="_blank"
        rel="noopener noreferrer"
        onClick={(e) => e.stopPropagation()}
        className={styles.actionButton}
        title="Abrir a página web da impressora"
        aria-label={`Abrir a página web de ${printer.name}`}
      >
        <Globe size={15} aria-hidden="true" />
      </a>
      <button
        type="button"
        onClick={(e) => {
          e.stopPropagation();
          requestTestPrint(printer);
        }}
        disabled={blocked !== null}
        className={styles.actionButton}
        title={blocked ?? "Imprimir página de teste"}
        aria-label={blocked ? `Página de teste indisponível: ${blocked}` : `Imprimir página de teste em ${printer.name}`}
      >
        <PrinterIcon size={15} aria-hidden="true" />
      </button>
    </div>
  );
}
