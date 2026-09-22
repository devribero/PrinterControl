/**
 * Rota "/" — Dashboard. Equivalente ao bloco `activeNav === "dashboard"` que
 * antes vivia em App.tsx; os dados vêm do AppDataProvider (lib/app-data.tsx),
 * já recortados pelo seletor global de servidor/unidade (ServerSwitcher).
 *
 * Ordem da tela = ordem das perguntas de quem opera a frota (22/09/2026):
 * 1. faixa de resumo — quantas estão online / em atenção / offline;
 * 2. "precisa de atenção" — alertas ativos, offline e toner baixo, cada um
 *    com as poucas linhas que pedem ação (RightPanel);
 * 3. a frota inteira (tabela) ao lado do volume de impressão mensal.
 * Toda linha que cita uma impressora abre o PrinterDetailsModal global
 * (`setSelectedPrinter` / `handleAlertSelect`).
 */
"use client";

import { useRef } from "react";
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
import { rotularEscopo } from "../lib/serverScope";
import { cn } from "../lib/cn";
import styles from "./page.module.css";

export default function DashboardPage() {
  const router = useRouter();
  const fleetRef = useRef<HTMLDivElement>(null);
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
    monthlyUsage,
    usingRealMonthlyReport,
    handleRefresh,
    servers,
    serverScope,
    scopeUnit,
    units,
  } = useAppData();

  // O subtitulo precisa dizer de QUAL frota estes numeros falam: com um
  // escopo de servidor ativo, "estado consolidado da frota" descreveria algo
  // que a tela nao esta mostrando.
  const subtitulo =
    serverScope === null
      ? "Estado consolidado da frota, suprimentos e consumo de páginas."
      : serverScope === ""
        ? "Impressoras cadastradas à mão, fora de qualquer Print Server."
        : scopeUnit
          ? `Frota da unidade ${scopeUnit.name} — suprimentos e consumo de páginas.`
          : `Frota de ${rotularEscopo(serverScope, servers, units)} — suprimentos e consumo de páginas.`;

  /** Card "Offline" → filtra a tabela e rola até ela. */
  function mostrarOfflineNaTabela() {
    updateFilter("status", stats.offline > 0 ? "offline" : "Todos");
    const reduzirMovimento =
      typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    fleetRef.current?.scrollIntoView({ behavior: reduzirMovimento ? "auto" : "smooth", block: "start" });
  }

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
        <div className={cn(styles.skeletonCard, styles.skeletonCardStrip, "animate-pulse")} aria-hidden="true" />
      ) : (
        <VitalsStrip
          total={stats.total}
          online={stats.online}
          offline={stats.offline}
          attention={stats.attention}
          stale={stats.stale}
          activeStatus={filters.status === "Todos" ? "Todos" : filters.status}
          onSelectStatus={(s) => updateFilter("status", s)}
        />
      )}

      <RightPanel
        loading={initialLoading}
        alerts={alerts}
        printers={printers}
        fleet={activeFleet}
        now={lastChecked}
        onOpenDetails={setSelectedPrinter}
        onSelectAlert={handleAlertSelect}
        onViewAlerts={() => router.push(NAV_ROUTES.alerts ?? "/alerts")}
        onViewToner={() => router.push(NAV_ROUTES.toner ?? "/toner")}
        onShowOffline={mostrarOfflineNaTabela}
      />

      <div className={styles.mainGrid}>
        <div ref={fleetRef} className={styles.fleet}>
          {initialLoading ? (
            <div className={cn(styles.skeletonCard, styles.skeletonCardTable, "animate-pulse")} aria-hidden="true" />
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
            />
          )}
        </div>

        <BottomCharts
          loading={initialLoading}
          monthlyUsage={monthlyUsage}
          monthlyFicticio={!usingRealMonthlyReport && monthlyUsage.length > 0}
        />
      </div>
    </>
  );
}
