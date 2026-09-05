/**
 * Rota "/" — Dashboard. Equivalente ao bloco `activeNav === "dashboard"` que
 * antes vivia em App.tsx; os dados vêm do AppDataProvider (lib/app-data.tsx).
 */
"use client";

import { useRouter } from "next/navigation";
import PageHeader from "../components/PageHeader";
import ScanBar from "../components/ScanBar";
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
    setSelectedPrinter,
    globalToner,
    worstPrinter,
    monthlyUsage,
    usingRealMonthlyReport,
    handleRefresh,
  } = useAppData();

  return (
    <>
      <PageHeader
        section="Monitoramento"
        title="Visão geral"
        subtitle="Estado consolidado da frota, suprimentos e consumo de páginas."
        actions={<ScanBar lastChecked={lastChecked} scanning={scanning} onRefresh={handleRefresh} />}
      />

      {initialLoading ? (
        <div className={cn(styles.skeletonCard, styles.skeletonCardStrip, "animate-pulse")} />
      ) : (
        <VitalsStrip
          total={stats.total}
          online={stats.online}
          offline={stats.offline}
          attention={stats.attention}
          activeStatus={filters.status === "Todos" ? "Todos" : filters.status}
          onSelectStatus={(s) => updateFilter("status", s)}
          topAlert={alerts[0] ?? null}
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
            totalCount={printers.length}
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
