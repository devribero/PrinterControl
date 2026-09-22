import { ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "../../lib/cn";
import { pageCount } from "./usePagination";
import styles from "./Pagination.module.css";

interface PaginationProps {
  total: number;
  /** Página atual, já limitada a [1, totalPages] pelo chamador. */
  page: number;
  pageSize: number;
  pageSizeOptions: number[];
  onPageChange: (page: number) => void;
  onPageSizeChange: (size: number) => void;
}

/**
 * Números a mostrar: primeira, última e a vizinhança da atual, com
 * reticências no meio — com 14 páginas a lista inteira quebrava em duas
 * linhas no celular.
 */
function pageWindow(current: number, total: number): (number | "gap")[] {
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);
  const pages = new Set([1, total, current - 1, current, current + 1]);
  const sorted = [...pages].filter((n) => n >= 1 && n <= total).sort((a, b) => a - b);
  const out: (number | "gap")[] = [];
  sorted.forEach((n, i) => {
    if (i > 0 && n - sorted[i - 1] > 1) out.push("gap");
    out.push(n);
  });
  return out;
}

export default function Pagination({ total, page, pageSize, pageSizeOptions, onPageChange, onPageSizeChange }: PaginationProps) {
  const totalPages = pageCount(total, pageSize);
  const first = total === 0 ? 0 : (page - 1) * pageSize + 1;
  const last = Math.min(page * pageSize, total);

  return (
    <nav className={styles.pagination} aria-label="Paginação">
      <p className={styles.info}>
        Exibindo{" "}
        <span className={styles.num}>
          {first}–{last}
        </span>{" "}
        de <span className={styles.num}>{total}</span>
      </p>
      <div className={styles.controls}>
        <button
          type="button"
          onClick={() => onPageChange(Math.max(1, page - 1))}
          disabled={page === 1}
          className={styles.arrow}
          aria-label="Página anterior"
        >
          <ChevronLeft size={14} />
        </button>
        {pageWindow(page, totalPages).map((n, i) =>
          n === "gap" ? (
            <span key={`gap-${i}`} className={styles.gap} aria-hidden="true">
              …
            </span>
          ) : (
            <button
              type="button"
              key={n}
              onClick={() => onPageChange(n)}
              aria-current={n === page ? "page" : undefined}
              aria-label={`Página ${n}`}
              className={cn(styles.number, n === page && styles.numberActive)}
            >
              {n}
            </button>
          ),
        )}
        <button
          type="button"
          onClick={() => onPageChange(Math.min(totalPages, page + 1))}
          disabled={page === totalPages}
          className={styles.arrow}
          aria-label="Próxima página"
        >
          <ChevronRight size={14} />
        </button>
        <select
          aria-label="Itens por página"
          value={pageSize}
          onChange={(e) => onPageSizeChange(Number(e.target.value))}
          className={styles.sizeSelect}
        >
          {pageSizeOptions.map((n) => (
            <option key={n} value={n}>
              {n} / página
            </option>
          ))}
        </select>
      </div>
    </nav>
  );
}
