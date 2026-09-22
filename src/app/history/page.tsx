"use client";

import PageHeader from "../../components/PageHeader";
import ServerSwitcher from "../../components/ServerSwitcher";
import HistoryMatrix from "../../components/HistoryMatrix";
import { useAppData } from "../../lib/app-data";

export default function HistoryPage() {
  const { activeFleet, servers, setSelectedPrinter } = useAppData();

  return (
    <>
      <PageHeader
        section="Monitoramento"
        title="Histórico"
        subtitle="Páginas impressas por mês, de todas as impressoras, agrupadas por unidade."
        actions={<ServerSwitcher />}
      />

      <HistoryMatrix printers={activeFleet} servers={servers} onSelectPrinter={setSelectedPrinter} />
    </>
  );
}
