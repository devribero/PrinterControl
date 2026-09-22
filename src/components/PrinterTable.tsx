"use client";

/**
 * Tabela compacta da frota, embutida no Dashboard (rota "/"). A lista
 * completa, com filtros na URL, ordenação e ações por linha, é a rota
 * /printers (components/printers/PrinterFleet); o link "Ver todas" leva para
 * lá com a mesma busca/status/tipo aplicados.
 *
 * Os filtros são os globais do AppDataProvider (busca da barra superior,
 * status vindo da faixa de resumo), recebidos por props. Paginação é estado
 * próprio. Abaixo de 640px cada linha vira um cartão.
 */
import { useState } from "react";
import Link from "next/link";
import { Search, SlidersHorizontal, Printer as PrinterIcon, X, ArrowRight } from "lucide-react";
import type { Printer, PrinterStatus } from "../types";
import PrinterStatusBadge from "./PrinterStatusBadge";
import type { PrinterFilters } from "../lib/filterPrinters";
import type { PrinterType } from "../lib/printerType";
import { cn } from "../lib/cn";
import TonerCell from "./printers/TonerCell";
import Pagination from "./printers/Pagination";
import { usePagination } from "./printers/usePagination";
import { DEFAULT_SORT, STATUS_LABEL, TYPE_LABEL, serializeFleetParams } from "./printers/fleetModel";
import styles from "./PrinterTable.module.css";

interface PrinterTableProps {
  printers: Printer[];
  totalCount: number;
  filters: PrinterFilters;
  onFilterChange: <K extends keyof PrinterFilters>(key: K, value: PrinterFilters[K]) => void;
  onOpenDetails: (printer: Printer) => void;
}

const PAGE_SIZES = [10, 20, 50];

const ICON_TONE: Record<PrinterStatus, string> = {
  online: styles.nameIconOnline,
  atencao: styles.nameIconAttention,
  offline: styles.nameIconOffline,
};

/** Mesma visão em /printers: busca, status e tipo viram parâmetros da URL. */
function fullListHref(filters: PrinterFilters): string {
  const qs = serializeFleetParams(
    {
      q: filters.query,
      status: filters.status === "Todos" ? null : filters.status,
      tipo: filters.type === "Todos" ? null : filters.type,
      servidor: null,
      tonerBaixo: false,
      ordem: DEFAULT_SORT,
    },
    "",
  );
  return qs ? `/printers?${qs}` : "/printers";
}

export default function PrinterTable({ printers, totalCount, filters, onFilterChange, onOpenDetails }: PrinterTableProps) {
  const [showFilters, setShowFilters] = useState(false);
  const { page, pageSize, pageItems, setPage, setPageSize } = usePagination(
    printers,
    `${filters.query}|${filters.status}|${filters.type}|${filters.department}`,
    PAGE_SIZES[0],
  );

  return (
    <div className={styles.root}>
      <div className={styles.headerRow}>
        <div className={styles.titleBlock}>
          <h3 className={styles.title}>Frota de impressoras</h3>
          <span className={styles.titleCount}>
            {printers.length === totalCount ? `${totalCount} equipamentos` : `${printers.length} de ${totalCount}`}
          </span>
          {/* O filtro de status vem de fora (faixa de resumo, card Offline):
              sem este aviso a tabela "encolhia" sem dizer por quê. */}
          {filters.status !== "Todos" && (
            <button type="button" onClick={() => onFilterChange("status", "Todos")} className={styles.activeFilter}>
              {STATUS_LABEL[filters.status]}
              <X size={12} aria-hidden="true" />
              <span className={styles.srOnly}>Limpar filtro de status</span>
            </button>
          )}
        </div>

        <div className={styles.controls}>
          <label className={styles.searchBox}>
            <Search size={14} aria-hidden="true" />
            <input
              type="search"
              aria-label="Buscar impressora"
              value={filters.query}
              onChange={(e) => onFilterChange("query", e.target.value)}
              placeholder="Buscar..."
              className={styles.searchInput}
            />
          </label>
          <button
            type="button"
            onClick={() => setShowFilters((s) => !s)}
            aria-expanded={showFilters}
            className={cn(styles.filterButton, (showFilters || filters.type !== "Todos") && styles.filterButtonActive)}
          >
            <SlidersHorizontal size={14} aria-hidden="true" />
            Filtros
          </button>
          <Link href={fullListHref(filters)} className={styles.viewAll}>
            Ver todas
            <ArrowRight size={13} aria-hidden="true" />
          </Link>
        </div>
      </div>

      {showFilters && (
        <div className={styles.filtersPanel}>
          <span className={styles.filterLabel} id="printer-table-type">
            Tipo
          </span>
          <div className={styles.filterPillRow} role="group" aria-labelledby="printer-table-type">
            {(["Todos", ...Object.keys(TYPE_LABEL)] as ("Todos" | PrinterType)[]).map((value) => (
              <button
                type="button"
                key={value}
                aria-pressed={filters.type === value}
                onClick={() => onFilterChange("type", value)}
                className={cn(styles.filterPill, filters.type === value && styles.filterPillActive)}
              >
                {value === "Todos" ? "Todos" : TYPE_LABEL[value]}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className={styles.tableWrap}>
        <table className={styles.table}>
          <thead>
            <tr className={styles.theadRow}>
              <th className={styles.thFirst}>Impressora</th>
              <th className={styles.th}>Endereço</th>
              <th className={styles.th}>Departamento</th>
              <th className={cn(styles.th, styles.thRight)}>Toner</th>
              <th className={styles.th}>Status</th>
            </tr>
          </thead>
          <tbody>
            {pageItems.map((p) => (
              <tr
                key={p.id}
                onClick={() => onOpenDetails(p)}
                onKeyDown={(e) => {
                  if (e.target !== e.currentTarget) return;
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    onOpenDetails(p);
                  }
                }}
                tabIndex={0}
                aria-label={`${p.name}, ${STATUS_LABEL[p.status]} — abrir detalhes`}
                className={styles.row}
              >
                <td className={styles.tdFirst}>
                  <div className={styles.nameCell}>
                    <span className={cn(styles.nameIcon, ICON_TONE[p.status])} aria-hidden="true">
                      <PrinterIcon size={15} />
                    </span>
                    <span className={styles.nameText}>
                      <span className={styles.nameMain} title={p.name}>
                        {p.name}
                      </span>
                      {p.model && (
                        <span className={styles.nameSub} title={p.model}>
                          {p.model}
                        </span>
                      )}
                      {/* Só no celular, onde as colunas Endereço/Departamento somem. */}
                      <span className={styles.nameMeta}>
                        <span className={styles.nameMetaIp}>{p.ip}</span>
                        {p.department ? ` · ${p.department}` : ""}
                      </span>
                    </span>
                  </div>
                </td>
                <td className={cn(styles.td, styles.tdIp)}>{p.ip}</td>
                <td className={cn(styles.td, styles.tdDept)} title={p.department}>
                  {p.department}
                </td>
                <td className={cn(styles.td, styles.tdRight, styles.tdToner)}>
                  <TonerCell toner={p.toner} />
                </td>
                <td className={cn(styles.td, styles.tdStatus)}>
                  <PrinterStatusBadge status={p.status} />
                </td>
              </tr>
            ))}
            {pageItems.length === 0 && (
              <tr className={styles.emptyRow}>
                <td colSpan={5} className={styles.emptyState}>
                  {totalCount === 0 ? "Nenhuma impressora ativa neste escopo." : "Nenhuma impressora encontrada com esses filtros."}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <Pagination
        total={printers.length}
        page={page}
        pageSize={pageSize}
        pageSizeOptions={PAGE_SIZES}
        onPageChange={setPage}
        onPageSizeChange={setPageSize}
      />
    </div>
  );
}
