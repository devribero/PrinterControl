"use client";

/**
 * Lista completa da frota (rota /printers): barra de busca/filtros/ordem,
 * tabela (cartões no celular) e paginação. Os filtros vivem na URL
 * (useFleetParams) para que uma visão filtrada possa ser compartilhada.
 * A base é `activeFleet` — frota ativa, já recortada pelo seletor global de
 * servidor/unidade —, e não `filteredPrinters`, que carrega os filtros do
 * Dashboard (faixa de resumo), sem controle nesta tela.
 */
import { useMemo } from "react";
import type { Printer, PrinterStatus } from "../../types";
import { useAppData } from "../../lib/app-data";
import { limiteLeituraVelha, parseApiDate } from "../../lib/adaptApi";
import { cn } from "../../lib/cn";
import FleetToolbar, { type ServerOption } from "./FleetToolbar";
import FleetTable from "./FleetTable";
import Pagination from "./Pagination";
import { usePagination } from "./usePagination";
import { useFleetParams } from "./useFleetParams";
import { filterFleet, hasActiveFilters, serializeFleetParams, sortFleet } from "./fleetModel";
import styles from "./Fleet.module.css";

const PAGE_SIZES = [25, 50, 100];
const collator = new Intl.Collator("pt-BR", { sensitivity: "base", numeric: true });

export default function PrinterFleet() {
  const { activeFleet, servers, initialLoading, lastChecked, backendEnv, usingRealData, setSelectedPrinter } = useAppData();
  const { params, update, setQuery, clearFilters } = useFleetParams();

  const serverByHost = useMemo(() => new Map(servers.map((s) => [s.host, s])), [servers]);
  const serverLabel = (host: string) => (host === "" ? "Sem servidor" : serverByHost.get(host)?.name || host);
  const unitLabel = (host: string) => serverByHost.get(host)?.unitName ?? null;

  // Servidores presentes na frota do escopo atual (não a lista cadastrada inteira).
  const serverOptions: ServerOption[] = useMemo(() => {
    const hosts = [...new Set(activeFleet.map((p) => p.server))];
    return hosts
      .map((host) => ({ value: host, label: host === "" ? "Sem servidor" : serverByHost.get(host)?.name || host }))
      .sort((a, b) => collator.compare(a.label, b.label));
  }, [activeFleet, serverByHost]);
  const serverHosts = useMemo(() => new Set(serverOptions.map((s) => s.value)), [serverOptions]);
  const activeServer = params.servidor !== null && serverHosts.has(params.servidor) ? params.servidor : null;

  const statusCounts = useMemo(() => {
    const counts: Record<PrinterStatus, number> = { online: 0, atencao: 0, offline: 0 };
    for (const p of activeFleet) counts[p.status] += 1;
    return counts;
  }, [activeFleet]);

  const visible = useMemo(
    () => sortFleet(filterFleet(activeFleet, params, serverHosts), params.ordem),
    [activeFleet, params, serverHosts],
  );

  const { page, pageSize, pageItems, setPage, setPageSize } = usePagination(
    visible,
    serializeFleetParams(params, ""),
    PAGE_SIZES[0],
  );

  // Mesma regra de `stats.stale` (lib/adaptApi leituraVelha), mas medida a
  // partir da última coleta para o render ficar puro. Só com dado real: o
  // conjunto de demonstração não traz o instante da leitura.
  const staleLimitMin = limiteLeituraVelha(backendEnv?.collection_interval_minutes ?? null);
  const isStale = (p: Printer) => {
    if (!usingRealData || p.lastSeenAt === undefined) return false;
    const date = parseApiDate(p.lastSeenAt);
    return !date || (lastChecked.getTime() - date.getTime()) / 60000 > staleLimitMin;
  };

  if (initialLoading) {
    return <div className={cn(styles.card, styles.skeleton, "animate-pulse")} aria-hidden="true" />;
  }

  const filtersActive = hasActiveFilters(params);

  return (
    <section className={styles.card} aria-label="Impressoras da frota">
      <FleetToolbar
        params={params}
        onQueryChange={setQuery}
        onChange={update}
        onClear={clearFilters}
        serverOptions={serverOptions}
        activeServer={activeServer}
        statusCounts={statusCounts}
        resultCount={visible.length}
        totalCount={activeFleet.length}
        filtersActive={filtersActive}
      />

      <FleetTable
        printers={pageItems}
        onOpenDetails={setSelectedPrinter}
        showServer={serverOptions.length > 1}
        serverLabel={serverLabel}
        unitLabel={unitLabel}
        now={lastChecked}
        isStale={isStale}
        emptyMessage={
          activeFleet.length === 0
            ? "Nenhuma impressora ativa neste escopo."
            : "Nenhuma impressora encontrada com esses filtros."
        }
      />

      {visible.length > PAGE_SIZES[0] && (
        <Pagination
          total={visible.length}
          page={page}
          pageSize={pageSize}
          pageSizeOptions={PAGE_SIZES}
          onPageChange={setPage}
          onPageSizeChange={setPageSize}
        />
      )}
    </section>
  );
}
