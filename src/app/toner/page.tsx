"use client";

import { useMemo } from "react";
import PageHeader from "../../components/PageHeader";
import ServerSwitcher from "../../components/ServerSwitcher";
import ScanBar from "../../components/ScanBar";
import TonerMonitoring from "../../components/TonerMonitoring";
import { useAppData } from "../../lib/app-data";

export default function TonerPage() {
  // `activeFleet`, e não `filteredPrinters`: este último carrega os filtros
  // do Dashboard (busca, status, tipo), que não têm controle nesta tela. O
  // escopo de servidor já vem aplicado em `activeFleet`.
  const { activeFleet, servers, serverScope, setSelectedPrinter, lastChecked, handleRefresh, scanning } = useAppData();

  const serverNames = useMemo(() => Object.fromEntries(servers.map((s) => [s.host, s.name || s.host])), [servers]);
  const showServer = serverScope === null || serverScope.startsWith("unit:");

  return (
    <>
      <PageHeader
        section="Monitoramento"
        title="Suprimentos"
        subtitle="Nível de toner das impressoras A4, do menor para o maior."
        actions={
          <>
            <ServerSwitcher />
            <ScanBar lastChecked={lastChecked} scanning={scanning} onRefresh={handleRefresh} label="Atualizar agora" />
          </>
        }
      />

      <TonerMonitoring
        printers={activeFleet}
        serverNames={serverNames}
        showServer={showServer}
        onOpenDetails={setSelectedPrinter}
      />
    </>
  );
}
