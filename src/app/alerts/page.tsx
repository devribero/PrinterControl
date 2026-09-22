"use client";

import PageHeader from "../../components/PageHeader";
import ServerSwitcher from "../../components/ServerSwitcher";
import AlertsView from "../../components/AlertsView";
import { useAppData } from "../../lib/app-data";

export default function AlertsPage() {
  const { alerts, printers, setSelectedPrinter, setAlertsRead } = useAppData();

  return (
    <>
      <PageHeader
        section="Monitoramento"
        title="Alertas"
        subtitle="Eventos técnicos derivados das leituras — toner baixo e equipamentos fora do ar."
        actions={<ServerSwitcher />}
      />

      <AlertsView alerts={alerts} printers={printers} onSelectPrinter={setSelectedPrinter} onSetRead={setAlertsRead} />
    </>
  );
}
