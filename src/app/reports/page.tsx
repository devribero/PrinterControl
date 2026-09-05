"use client";

/**
 * Rota "/reports" — Relatórios. Estrutura do handoff (`PrinterControl
 * v2.dc.html` L586-666): faixa mensal → consumo por departamento (dominante)
 * + rankings na coluna lateral → tabela de impressoras inativas.
 */
import { Download } from "lucide-react";
import PageHeader from "../../components/PageHeader";
import MonthlyCounters from "../../components/MonthlyCounters";
import PrinterRanking from "../../components/PrinterRanking";
import DepartmentBreakdown from "../../components/DepartmentBreakdown";
import DecommissionedList from "../../components/DecommissionedList";
import { useAppData } from "../../lib/app-data";
import { useToast } from "../../lib/toast";
import { exportPrintersCsv } from "../../lib/exportCsv";
import styles from "./page.module.css";

export default function ReportsPage() {
  const {
    printers,
    monthlyUsage,
    usingRealMonthlyReport,
    departmentUsage,
    decommissionedPrinters,
    setSelectedPrinter,
  } = useAppData();
  const { push } = useToast();

  return (
    <>
      <PageHeader
        section="Monitoramento"
        title="Relatórios"
        subtitle="Contadores mensais, ranking de uso e consumo por departamento."
        actions={
          <button
            onClick={() => {
              exportPrintersCsv(printers);
              push({ variant: "success", title: "CSV exportado", description: `${printers.length} impressora(s) incluída(s) no arquivo.` });
            }}
            className={styles.exportButton}
          >
            <Download size={14} />
            Exportar relatório (CSV)
          </button>
        }
      />

      <MonthlyCounters data={monthlyUsage} ficticio={!usingRealMonthlyReport} />

      <div className={styles.mainGrid}>
        <DepartmentBreakdown data={departmentUsage} />
        <PrinterRanking printers={printers} onOpenDetails={setSelectedPrinter} />
      </div>

      <DecommissionedList data={decommissionedPrinters} />
    </>
  );
}
