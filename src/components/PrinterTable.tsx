"use client";

/**
 * Dependências externas: react (paginação/view state) e lucide-react
 * (ícones). Dependências locais: PrinterStatusBadge, lib/tonerColor,
 * lib/filterPrinters (tipo do estado de filtro, controlado pelo pai),
 * lib/printerType (pills "Tipo"). Paginação e visão lista/grade são estado
 * PRÓPRIO deste componente (não sobem para o AppDataProvider) — só os filtros
 * globais (busca/status/tipo/departamento) vêm de fora via props.
 *
 * Duas apresentações do mesmo componente (handoff `PrinterControl v2.dc.html`):
 * - completa (rota /printers, L392-479): abas de status no cabeçalho;
 * - `compact` (card embutido no Dashboard, L220-300): título + busca curta.
 * O corpo da tabela e a paginação são idênticos nas duas no handoff, então
 * ficam compartilhados aqui.
 */
import { useMemo, useState } from "react";
import {
  Search,
  SlidersHorizontal,
  Rows3,
  LayoutGrid,
  FileText,
  Globe,
  Printer as PrinterIcon,
  Settings,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import type { Printer } from "../types";
import PrinterStatusBadge from "./PrinterStatusBadge";
import { tonerChannelColor, tonerLevelColor } from "../lib/tonerColor";
import type { PrinterFilters } from "../lib/filterPrinters";
import type { PrinterStatus } from "../types";
import type { PrinterType } from "../lib/printerType";
import { useToast } from "../lib/toast";
import { useTheme } from "../lib/theme";
import { cn } from "../lib/cn";
import styles from "./PrinterTable.module.css";

interface PrinterTableProps {
  printers: Printer[];
  totalCount: number;
  /** Contagens da frota INTEIRA (não da lista filtrada) — alimentam as abas de
   * status, que precisam continuar mostrando o total de cada status mesmo
   * quando um filtro está ativo. Ausente no modo compact, que não tem abas. */
  statusCounts?: { online: number; offline: number; atencao: number };
  filters: PrinterFilters;
  onFilterChange: <K extends keyof PrinterFilters>(key: K, value: PrinterFilters[K]) => void;
  onOpenDetails: (printer: Printer) => void;
  /** Esconde as colunas Modelo/Ações — usado no card embutido do Dashboard,
   * onde a tabela divide espaço com o painel lateral e não cabem todas as
   * colunas sem rolagem horizontal. A página "Impressoras" continua completa. */
  compact?: boolean;
}

const PAGE_SIZE_OPTIONS = [10, 20, 50];

export default function PrinterTable({
  printers,
  totalCount,
  statusCounts,
  filters,
  onFilterChange,
  onOpenDetails,
  compact = false,
}: PrinterTableProps) {
  const [pageSize, setPageSize] = useState(10);
  const [page, setPage] = useState(1);
  const [view, setView] = useState<"list" | "grid">("list");
  const [showFilters, setShowFilters] = useState(false);
  const { push } = useToast();
  const { theme } = useTheme();

  const totalPages = Math.max(1, Math.ceil(printers.length / pageSize));
  const currentPage = Math.min(page, totalPages);
  const pageItems = useMemo(
    () => printers.slice((currentPage - 1) * pageSize, currentPage * pageSize),
    [printers, currentPage, pageSize]
  );

  function handleTestPage(p: Printer, e: React.MouseEvent) {
    e.stopPropagation();
    push({ variant: "success", title: "Página de teste enviada", description: `Job enfileirado para ${p.name}.` });
  }

  function handleWebAccess(p: Printer, e: React.MouseEvent) {
    e.stopPropagation();
    window.open(`http://${p.ip}`, "_blank", "noopener");
  }

  function handleSettings(p: Printer, e: React.MouseEvent) {
    e.stopPropagation();
    push({ variant: "info", title: "Gerenciamento remoto", description: `Configurações avançadas de ${p.name} chegam em breve.` });
  }

  const statusTabs: { label: string; value: "Todos" | PrinterStatus; count: number; tone: string }[] = [
    { label: "Todas", value: "Todos", count: totalCount, tone: styles.tabToneNeutral },
    { label: "Online", value: "online", count: statusCounts?.online ?? 0, tone: styles.tabToneOnline },
    { label: "Offline", value: "offline", count: statusCounts?.offline ?? 0, tone: styles.tabToneOffline },
    { label: "Atenção", value: "atencao", count: statusCounts?.atencao ?? 0, tone: styles.tabToneAttention },
  ];
  const typeOptions: { label: string; value: "Todos" | PrinterType }[] = [
    { label: "Todos", value: "Todos" },
    { label: "A4", value: "A4" },
    { label: "Etiqueta", value: "Etiqueta" },
    { label: "Portátil", value: "Portatil" },
  ];

  function selectStatus(value: "Todos" | PrinterStatus) {
    onFilterChange("status", value);
    setPage(1);
  }

  const searchBox = (
    <div className={cn(styles.searchBox, compact && styles.searchBoxCompact)}>
      <Search size={14} />
      <input
        value={filters.query}
        onChange={(e) => {
          onFilterChange("query", e.target.value);
          setPage(1);
        }}
        placeholder={compact ? "Buscar..." : "Nome, IP ou modelo"}
        className={styles.searchInput}
      />
    </div>
  );

  const filtersButton = (
    <button
      onClick={() => setShowFilters((s) => !s)}
      className={cn(styles.filterButton, (showFilters || filters.type !== "Todos") && styles.filterButtonActive)}
    >
      <SlidersHorizontal size={14} />
      Filtros
    </button>
  );

  return (
    <div className={styles.root}>
      <div className={cn(styles.headerRow, compact && styles.headerRowCompact)}>
        {compact ? (
          <div className={styles.titleBlock}>
            <h3 className={styles.title}>Frota de impressoras</h3>
            <span className={styles.titleCount}>{totalCount} equipamentos</span>
          </div>
        ) : (
          <div className={styles.tabs}>
            {statusTabs.map((tab) => (
              <button
                key={tab.value}
                onClick={() => selectStatus(tab.value)}
                className={cn(styles.tab, filters.status === tab.value ? styles.tabActive : tab.tone)}
              >
                {tab.label} <span className={styles.tabCount}>{tab.count}</span>
              </button>
            ))}
          </div>
        )}

        <div className={styles.controls}>
          {searchBox}
          {filtersButton}
          {!compact && (
            <div className={styles.viewToggle}>
              <button
                onClick={() => setView("list")}
                className={cn(styles.viewButton, view === "list" && styles.viewButtonActive)}
                title="Visão em lista"
              >
                <Rows3 size={15} />
              </button>
              <button
                onClick={() => setView("grid")}
                className={cn(styles.viewButton, view === "grid" && styles.viewButtonActive)}
                title="Visão em grade"
              >
                <LayoutGrid size={15} />
              </button>
            </div>
          )}
        </div>
      </div>

      {showFilters && (
        <div className={styles.filtersPanel}>
          <div className={styles.filterGroup}>
            <span className={styles.filterLabel}>Tipo</span>
            <div className={styles.filterPillRow}>
              {typeOptions.map((opt) => (
                <button
                  key={opt.value}
                  onClick={() => {
                    onFilterChange("type", opt.value);
                    setPage(1);
                  }}
                  className={cn(styles.filterPill, filters.type === opt.value && styles.filterPillActive)}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {view === "list" ? (
        <div className={styles.tableWrap}>
          <table className={cn(styles.table, compact && styles.tableCompact)}>
            <thead>
              <tr className={styles.theadRow}>
                <th className={styles.thFirst}>Impressora</th>
                <th className={styles.th}>Endereço</th>
                {!compact && <th className={styles.th}>Modelo</th>}
                <th className={styles.th}>Departamento</th>
                <th className={cn(styles.th, styles.thRight)}>Toner</th>
                <th className={styles.th}>Status</th>
                {!compact && <th className={cn(styles.thLast, styles.thRight)}>Ações</th>}
              </tr>
            </thead>
            <tbody>
              {pageItems.map((p) => (
                <tr key={p.id} onClick={() => onOpenDetails(p)} className={styles.row}>
                  <td className={styles.tdFirst}>{p.name}</td>
                  <td className={cn(styles.td, styles.tdIp)}>{p.ip}</td>
                  {!compact && (
                    <td className={cn(styles.td, styles.tdModel)} title={p.model}>
                      {p.model}
                    </td>
                  )}
                  <td className={cn(styles.td, styles.tdDept, compact ? styles.tdDeptCompact : styles.tdDeptFull)} title={p.department}>
                    {p.department}
                  </td>
                  <td className={cn(styles.td, styles.tdRight)}>
                    {p.toner ? (
                      <div className={styles.tonerCell} title={`${p.toner[0].label}: ${p.toner[0].percent}%`}>
                        <div className={styles.tonerTrack}>
                          <div
                            className={styles.tonerFill}
                            style={{ width: `${p.toner[0].percent}%`, backgroundColor: tonerLevelColor(p.toner[0].percent) }}
                          />
                        </div>
                        <span className={styles.tonerPercent} style={{ color: tonerLevelColor(p.toner[0].percent) }}>
                          {p.toner[0].percent}%
                        </span>
                      </div>
                    ) : (
                      <span className={styles.naText}>—</span>
                    )}
                  </td>
                  <td className={styles.td}>
                    <PrinterStatusBadge status={p.status} />
                  </td>
                  {!compact && (
                    <td className={cn(styles.tdLast, styles.tdRight)}>
                      <div className={styles.actionsRow}>
                        <button onClick={() => onOpenDetails(p)} className={styles.actionButton} title="Detalhes">
                          <FileText size={14} />
                        </button>
                        <button onClick={(e) => handleWebAccess(p, e)} className={styles.actionButton} title="Acessar via web">
                          <Globe size={14} />
                        </button>
                        <button onClick={(e) => handleTestPage(p, e)} className={styles.actionButton} title="Imprimir teste">
                          <PrinterIcon size={14} />
                        </button>
                        <button onClick={(e) => handleSettings(p, e)} className={styles.actionButton} title="Configurações">
                          <Settings size={14} />
                        </button>
                      </div>
                    </td>
                  )}
                </tr>
              ))}
              {pageItems.length === 0 && (
                <tr>
                  <td colSpan={compact ? 5 : 7} className={styles.emptyState}>
                    Nenhuma impressora encontrada com esses filtros.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      ) : (
        <div className={styles.gridView}>
          {pageItems.map((p) => (
            <button key={p.id} onClick={() => onOpenDetails(p)} className={styles.gridCard}>
              <div className={styles.gridCardHead}>
                <div className={styles.gridCardHeadLeft}>
                  <p className={styles.gridCardName}>{p.name}</p>
                </div>
                <PrinterStatusBadge status={p.status} />
              </div>
              <div className={styles.gridCardMeta}>
                <p>
                  <span className={styles.gridCardIp}>{p.ip}</span> · {p.model}
                </p>
                <p>{p.department}</p>
              </div>
              {p.toner && (
                <div className={styles.gridCardToner}>
                  <div className={styles.gridCardTonerTrack}>
                    <div
                      className={styles.gridCardTonerFill}
                      style={{ width: `${p.toner[0].percent}%`, backgroundColor: tonerChannelColor(p.toner[0].color, theme) }}
                    />
                  </div>
                  <p className={styles.gridCardTonerLabel} style={{ color: tonerLevelColor(p.toner[0].percent) }}>
                    {p.toner[0].label}: {p.toner[0].percent}%
                  </p>
                </div>
              )}
            </button>
          ))}
          {pageItems.length === 0 && <p className={styles.emptyState}>Nenhuma impressora encontrada com esses filtros.</p>}
        </div>
      )}

      <div className={styles.pagination}>
        <p className={styles.paginationInfo}>
          Exibindo{" "}
          <span className={styles.paginationNum}>
            {printers.length === 0 ? 0 : (currentPage - 1) * pageSize + 1}–{Math.min(currentPage * pageSize, printers.length)}
          </span>{" "}
          de <span className={styles.paginationNum}>{printers.length}</span>
        </p>
        <div className={styles.paginationControls}>
          <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={currentPage === 1} className={styles.pageArrow}>
            <ChevronLeft size={14} />
          </button>
          {Array.from({ length: totalPages }, (_, i) => i + 1).map((n) => (
            <button
              key={n}
              onClick={() => setPage(n)}
              className={cn(styles.pageNumber, n === currentPage && styles.pageNumberActive)}
            >
              {n}
            </button>
          ))}
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={currentPage === totalPages}
            className={styles.pageArrow}
          >
            <ChevronRight size={14} />
          </button>
          <select
            value={pageSize}
            onChange={(e) => {
              setPageSize(Number(e.target.value));
              setPage(1);
            }}
            className={styles.pageSizeSelect}
          >
            {PAGE_SIZE_OPTIONS.map((n) => (
              <option key={n} value={n}>
                {n} / página
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
}
