"use client";

import { Search, X } from "lucide-react";
import type { SortKey } from "./tonerModel";
import styles from "./Toner.module.css";

const SORT_OPTIONS: { value: SortKey; label: string }[] = [
  { value: "level", label: "Menor nível primeiro" },
  { value: "name", label: "Nome" },
  { value: "department", label: "Departamento" },
  { value: "server", label: "Servidor" },
];

interface TonerToolbarProps {
  query: string;
  onQueryChange: (value: string) => void;
  sort: SortKey;
  onSortChange: (value: SortKey) => void;
  /** "Servidor" só faz sentido com mais de um servidor na lista. */
  allowServerSort: boolean;
}

export default function TonerToolbar({ query, onQueryChange, sort, onSortChange, allowServerSort }: TonerToolbarProps) {
  const options = allowServerSort ? SORT_OPTIONS : SORT_OPTIONS.filter((o) => o.value !== "server");

  return (
    <div className={styles.toolbar}>
      <label className={styles.searchBox}>
        <Search size={15} aria-hidden="true" />
        <input
          type="search"
          value={query}
          onChange={(e) => onQueryChange(e.target.value)}
          placeholder="Buscar por nome, IP, modelo ou departamento"
          aria-label="Buscar impressora"
          className={styles.searchInput}
        />
        {query && (
          <button type="button" onClick={() => onQueryChange("")} className={styles.clearButton} aria-label="Limpar busca">
            <X size={14} />
          </button>
        )}
      </label>

      <label className={styles.sortField}>
        <span className={styles.sortLabel}>Ordenar</span>
        <select value={sort} onChange={(e) => onSortChange(e.target.value as SortKey)} className={styles.sortSelect}>
          {options.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
      </label>
    </div>
  );
}
