"use client";

import { useState } from "react";

export function pageCount(total: number, pageSize: number): number {
  return Math.max(1, Math.ceil(total / pageSize));
}

/**
 * Página e tamanho da página, locais ao componente. `resetKey` muda quando a
 * lista muda de sentido (filtro, busca, ordem): a página volta para 1 sem
 * efeito, comparando a chave guardada com a atual no render.
 */
export function usePagination<T>(items: T[], resetKey: string, initialSize: number) {
  const [pageSize, setPageSizeState] = useState(initialSize);
  const [state, setState] = useState({ key: resetKey, page: 1 });

  const totalPages = pageCount(items.length, pageSize);
  const page = Math.min(state.key === resetKey ? state.page : 1, totalPages);
  const pageItems = items.slice((page - 1) * pageSize, page * pageSize);

  return {
    page,
    pageSize,
    pageItems,
    setPage: (next: number) => setState({ key: resetKey, page: next }),
    setPageSize: (size: number) => {
      setPageSizeState(size);
      setState({ key: resetKey, page: 1 });
    },
  };
}
