"use client";

import { Search, X } from "lucide-react";
import type { PrinterStatus } from "../../types";
import type { PrinterType } from "../../lib/printerType";
import { cn } from "../../lib/cn";
import { LOW_MAX } from "../toner/tonerModel";
import { SORT_LABEL, STATUS_LABEL, TYPE_LABEL, type FleetParams, type SortKey } from "./fleetModel";
import styles from "./Fleet.module.css";

export interface ServerOption {
  /** Host; "" = sem servidor. */
  value: string;
  label: string;
}

interface FleetToolbarProps {
  params: FleetParams;
  onQueryChange: (value: string) => void;
  onChange: (patch: Partial<FleetParams>) => void;
  onClear: () => void;
  /** Servidores da frota no escopo atual; o filtro só aparece com mais de um. */
  serverOptions: ServerOption[];
  /** Servidor efetivamente aplicado (o da URL, se ainda existir no escopo). */
  activeServer: string | null;
  statusCounts: Record<PrinterStatus, number>;
  resultCount: number;
  totalCount: number;
  filtersActive: boolean;
}

const SERVER_ALL = "__todos__";

export default function FleetToolbar({
  params,
  onQueryChange,
  onChange,
  onClear,
  serverOptions,
  activeServer,
  statusCounts,
  resultCount,
  totalCount,
  filtersActive,
}: FleetToolbarProps) {
  return (
    <>
      <div className={styles.toolbar} role="search">
        <label className={styles.searchBox}>
          <Search size={15} aria-hidden="true" />
          <input
            type="search"
            value={params.q}
            onChange={(e) => onQueryChange(e.target.value)}
            placeholder="Nome, IP, modelo, departamento ou servidor"
            aria-label="Buscar impressora"
            className={styles.searchInput}
          />
          {params.q && (
            <button type="button" onClick={() => onQueryChange("")} className={styles.clearSearch} aria-label="Limpar busca">
              <X size={14} />
            </button>
          )}
        </label>

        <div className={styles.filters}>
          <select
            aria-label="Filtrar por status"
            value={params.status ?? ""}
            onChange={(e) => onChange({ status: (e.target.value || null) as PrinterStatus | null })}
            className={cn(styles.select, params.status && styles.selectActive)}
          >
            <option value="">Todos os status</option>
            {(Object.keys(STATUS_LABEL) as PrinterStatus[]).map((s) => (
              <option key={s} value={s}>
                {STATUS_LABEL[s]} ({statusCounts[s]})
              </option>
            ))}
          </select>

          <select
            aria-label="Filtrar por tipo"
            value={params.tipo ?? ""}
            onChange={(e) => onChange({ tipo: (e.target.value || null) as PrinterType | null })}
            className={cn(styles.select, params.tipo && styles.selectActive)}
          >
            <option value="">Todos os tipos</option>
            {(Object.keys(TYPE_LABEL) as PrinterType[]).map((t) => (
              <option key={t} value={t}>
                {TYPE_LABEL[t]}
              </option>
            ))}
          </select>

          {serverOptions.length > 1 && (
            <select
              aria-label="Filtrar por servidor"
              value={activeServer ?? SERVER_ALL}
              onChange={(e) => onChange({ servidor: e.target.value === SERVER_ALL ? null : e.target.value })}
              className={cn(styles.select, activeServer !== null && styles.selectActive)}
            >
              <option value={SERVER_ALL}>Todos os servidores</option>
              {serverOptions.map((s) => (
                <option key={s.value || "-"} value={s.value}>
                  {s.label}
                </option>
              ))}
            </select>
          )}

          <button
            type="button"
            aria-pressed={params.tonerBaixo}
            onClick={() => onChange({ tonerBaixo: !params.tonerBaixo })}
            className={cn(styles.toggle, params.tonerBaixo && styles.toggleActive)}
          >
            Toner ≤ {LOW_MAX}%
          </button>

          <label className={styles.sortField}>
            <span className={styles.sortLabel}>Ordenar</span>
            <select
              value={params.ordem}
              onChange={(e) => onChange({ ordem: e.target.value as SortKey })}
              className={styles.select}
            >
              {(Object.keys(SORT_LABEL) as SortKey[]).map((k) => (
                <option key={k} value={k}>
                  {SORT_LABEL[k]}
                </option>
              ))}
            </select>
          </label>
        </div>
      </div>

      <div className={styles.resultBar}>
        <span aria-live="polite">
          {resultCount === totalCount ? (
            <>
              <span className={styles.resultNum}>{totalCount}</span> impressora{totalCount === 1 ? "" : "s"}
            </>
          ) : (
            <>
              <span className={styles.resultNum}>{resultCount}</span> de <span className={styles.resultNum}>{totalCount}</span>{" "}
              impressoras
            </>
          )}
        </span>
        {filtersActive && (
          <button type="button" onClick={onClear} className={styles.clearFilters}>
            Limpar filtros
          </button>
        )}
      </div>
    </>
  );
}
