"use client";

/**
 * Filtros de /printers na URL (useSearchParams + router.replace, sem entrada
 * nova no histórico a cada clique). Quem usa este hook precisa estar dentro
 * de um <Suspense> — exigência do useSearchParams em rota pré-renderizada.
 *
 * A busca é a exceção: a barra superior (Topbar) já tem uma busca global
 * (`filters.query` no AppDataProvider) e ela precisa continuar funcionando
 * nesta tela. Então a busca da página LÊ e ESCREVE a busca global, e a URL
 * só a espelha (`?q=`): ao abrir um link com `?q=`, o valor semeia a busca
 * global; ao digitar, o `?q=` acompanha com um pequeno atraso.
 */
import { useCallback, useEffect, useMemo, useRef } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useAppData } from "../../lib/app-data";
import { parseFleetParams, serializeFleetParams, type FleetParams } from "./fleetModel";

const URL_QUERY_DELAY_MS = 300;

export function useFleetParams() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { filters, updateFilter } = useAppData();
  const query = filters.query;

  const fromUrl = useMemo(() => parseFleetParams(searchParams), [searchParams]);
  const params: FleetParams = useMemo(() => ({ ...fromUrl, q: query }), [fromUrl, query]);

  /** Mescla sobre a URL do momento (não a do último render: o `?q=` atrasado pode ter mudado). */
  const update = useCallback(
    (patch: Partial<FleetParams>) => {
      const current = window.location.search;
      const next = serializeFleetParams({ ...parseFleetParams(new URLSearchParams(current)), ...patch }, current);
      if (`?${next}` === current || (next === "" && current === "")) return;
      router.replace(next ? `${pathname}?${next}` : pathname, { scroll: false });
    },
    [router, pathname],
  );

  // Semeia a busca global com o `?q=` do link aberto — só na montagem.
  const pendingSeed = useRef<string | null>(null);
  const seeded = useRef(false);
  useEffect(() => {
    const urlQ = new URLSearchParams(window.location.search).get("q") ?? "";
    if (urlQ && urlQ !== query) {
      pendingSeed.current = urlQ;
      updateFilter("query", urlQ);
    }
    seeded.current = true;
    // Dependências vazias de propósito: semear só na montagem.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Busca global → `?q=`.
  useEffect(() => {
    if (!seeded.current) return;
    if (pendingSeed.current !== null) {
      if (query === pendingSeed.current) pendingSeed.current = null;
      return;
    }
    const t = window.setTimeout(() => update({ q: query }), URL_QUERY_DELAY_MS);
    return () => window.clearTimeout(t);
  }, [query, update]);

  const setQuery = (value: string) => updateFilter("query", value);

  /** Volta ao padrão: sem busca, sem filtros (a ordem escolhida fica). */
  const clearFilters = () => {
    updateFilter("query", "");
    update({ q: "", status: null, tipo: null, servidor: null, tonerBaixo: false });
  };

  return { params, update, setQuery, clearFilters };
}
