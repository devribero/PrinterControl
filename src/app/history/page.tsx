"use client";

import PageHeader from "../../components/PageHeader";
import ServerSwitcher from "../../components/ServerSwitcher";
import HistoryMatrix from "../../components/HistoryMatrix";
import { useAppData } from "../../lib/app-data";

export default function HistoryPage() {
  const { printers } = useAppData();

  return (
    <>
      <PageHeader
        section="Monitoramento"
        title="Histórico"
        subtitle="Contadores por impressora e por unidade, mês a mês."
        actions={<ServerSwitcher />}
      />

      <HistoryMatrix printers={printers} />
    </>
  );
}
