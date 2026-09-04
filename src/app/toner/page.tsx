"use client";

import PageHeader from "../../components/PageHeader";
import ScanBar from "../../components/ScanBar";
import TonerMonitoring from "../../components/TonerMonitoring";
import { useAppData } from "../../lib/app-data";

export default function TonerPage() {
  const { filteredPrinters, setSelectedPrinter, lastChecked, handleRefresh, scanning } = useAppData();

  return (
    <>
      <PageHeader
        section="Monitoramento"
        title="Suprimentos"
        subtitle="Nível de toner de toda a frota, classificado por criticidade."
        actions={<ScanBar lastChecked={lastChecked} scanning={scanning} onRefresh={handleRefresh} label="Atualizar agora" />}
      />

      <TonerMonitoring printers={filteredPrinters} onOpenDetails={setSelectedPrinter} />
    </>
  );
}
