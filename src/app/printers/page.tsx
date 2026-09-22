"use client";

import { Suspense } from "react";
import PageHeader from "../../components/PageHeader";
import ServerSwitcher from "../../components/ServerSwitcher";
import ScanBar from "../../components/ScanBar";
import PrinterFleet from "../../components/printers/PrinterFleet";
import { useAppData } from "../../lib/app-data";

export default function PrintersPage() {
  const { lastChecked, scanning, handleRefresh } = useAppData();

  return (
    <>
      <PageHeader
        section="Monitoramento"
        title="Impressoras"
        subtitle="Cadastro completo da frota monitorada: status, suprimento e última leitura."
        actions={
          <>
            <ServerSwitcher />
            <ScanBar lastChecked={lastChecked} scanning={scanning} onRefresh={handleRefresh} />
          </>
        }
      />

      {/* PrinterFleet lê os filtros da URL (useSearchParams): precisa de Suspense. */}
      <Suspense fallback={null}>
        <PrinterFleet />
      </Suspense>
    </>
  );
}
