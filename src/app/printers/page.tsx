"use client";

import PageHeader from "../../components/PageHeader";
import PrinterTable from "../../components/PrinterTable";
import { useAppData } from "../../lib/app-data";

export default function PrintersPage() {
  const { filteredPrinters, printers, stats, filters, updateFilter, setSelectedPrinter } = useAppData();

  return (
    <>
      <PageHeader
        section="Monitoramento"
        title="Impressoras"
        subtitle="Cadastro completo da frota monitorada, com status e nível de suprimento."
      />

      <PrinterTable
        printers={filteredPrinters}
        totalCount={printers.length}
        statusCounts={{ online: stats.online, offline: stats.offline, atencao: stats.attention }}
        filters={filters}
        onFilterChange={updateFilter}
        onOpenDetails={setSelectedPrinter}
      />
    </>
  );
}
