/**
 * Rota "/" — Dashboard. Equivalente ao bloco `activeNav === "dashboard"` que
 * antes vivia em App.tsx; os dados vêm do AppDataProvider (lib/app-data.tsx).
 */
"use client";

import { useRouter } from "next/navigation";
import PageHeader from "../components/PageHeader";
import ScanBar from "../components/ScanBar";
import ServerSwitcher from "../components/ServerSwitcher";
import VitalsStrip from "../components/VitalsStrip";
import PrinterTable from "../components/PrinterTable";
import RightPanel from "../components/RightPanel";
import BottomCharts from "../components/BottomCharts";
import { useAppData } from "../lib/app-data";
import { NAV_ROUTES } from "../lib/routes";
import { cn } from "../lib/cn";
import styles from "./page.module.css";

export default function DashboardPage() {
  const router = useRouter();
  const {
    lastChecked,
    scanning,
    initialLoading,
    stats,
    filters,
    updateFilter,
    alerts,
    handleAlertSelect,
    filteredPrinters,
    printers,
    activeFleet,
    setSelectedPrinter,
    globalToner,
    worstPrinter,
    monthlyUsage,
    usingRealMonthlyReport,
    handleRefresh,
    servers,
    serverScope,
  } = useAppData();

  // O subtitulo precisa dizer de QUAL frota estes numeros falam: com um
  // escopo de servidor ativo, "estado consolidado da frota" descreveria algo
  // que a tela nao esta mostrando.
  const servidorEmFoco = servers.find((s) => s.host === serverScope) ?? null;
  const subtitulo =
    serverScope === null
      ? "Estado consolidado da frota, suprimentos e consumo de páginas."
      : serverScope === ""
        ? "Impressoras cadastradas à mão, fora de qualquer Print Server."
        : `Frota de ${servidorEmFoco?.name ?? serverScope} — suprimentos e consumo de páginas.`;

  const topAlert = alerts[0] ?? null;
  // A mensagem do backend nem sempre cita a impressora ("Impressora offline
  // (sem resposta na última coleta)"), então o nome é resolvido à parte.
  const topAlertPrinter = topAlert ? (printers.find((p) => p.id === topAlert.printerId)?.name ?? null) : null;

  return (
    <>
      <PageHeader
        section="Monitoramento"
        title="Visão geral"
        subtitle={subtitulo}
        actions={
          <>
            <ServerSwitcher />
            <ScanBar lastChecked={lastChecked} scanning={scanning} onRefresh={handleRefresh} />
          </>
        }
      />

      {initialLoading ? (
        <div className={cn(styles.skeletonCard, styles.skeletonCardStrip, "animate-pulse")} />
      ) : (
        <VitalsStrip
          total={stats.total}
          online={stats.online}
          offline={stats.offline}
          attention={stats.attention}
          stale={stats.stale}
          activeStatus={filters.status === "Todos" ? "Todos" : filters.status}
          onSelectStatus={(s) => updateFilter("status", s)}
          topAlert={topAlert}
          topAlertPrinter={topAlertPrinter}
          alertsRest={Math.max(alerts.length - 1, 0)}
          onViewAlerts={() => router.push("/alerts")}
          onSelectAlert={handleAlertSelect}
        />
      )}

      <div className={styles.mainGrid}>
        {initialLoading ? (
          <div className={cn(styles.skeletonCard, styles.skeletonCardTable, "animate-pulse")} />
        ) : (
          <PrinterTable
            printers={filteredPrinters}
            // Frota ativa, como o card "Frota monitorada" e a rota /printers.
            // Com `printers.length` a tabela dizia "278 equipamentos" ao lado
            // de um total de 134, contando as que sumiram do Print Server.
            totalCount={activeFleet.length}
            filters={filters}
            onFilterChange={updateFilter}
            onOpenDetails={setSelectedPrinter}
            compact
          />
        )}
        <RightPanel
          alertCount={alerts.length}
          globalToner={globalToner}
          worstPrinter={worstPrinter}
          onOpenDetails={setSelectedPrinter}
          onNavigate={(id) => router.push(NAV_ROUTES[id] ?? "/")}
        />
      </div>

      <BottomCharts
        attention={stats.attention}
        total={stats.total}
        monthlyUsage={monthlyUsage}
        monthlyFicticio={!usingRealMonthlyReport && monthlyUsage.length > 0}
        onViewAlerts={() => router.push("/alerts")}
      />
    </>
  );
}
