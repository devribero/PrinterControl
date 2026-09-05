"use client";

import PageHeader from "../../components/PageHeader";
import AlertsView from "../../components/AlertsView";
import { useAppData } from "../../lib/app-data";

export default function AlertsPage() {
  const { alerts, printers, setSelectedPrinter } = useAppData();

  return (
    <>
      <PageHeader
        section="Monitoramento"
        title="Alertas"
        subtitle="Eventos técnicos derivados das leituras — toner baixo e equipamentos fora do ar."
      />

      <AlertsView alerts={alerts} printers={printers} onSelectPrinter={setSelectedPrinter} />
    </>
  );
}
