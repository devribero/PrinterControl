"use client";

/**
 * Acompanha servidores reais que ainda aguardam o primeiro sync automático
 * (o backend dispara um logo após o cadastro). Enquanto houver algum, relê
 * a lista de servidores a cada 20 s — só com a aba visível — para o cartão
 * sair de "Sincronizando automaticamente…" sozinho. Quando um servidor sai
 * dessa fila, a frota em memória também é relida: ela acabou de ganhar as
 * impressoras dele.
 */
import { useEffect, useMemo, useRef } from "react";
import { useAppData } from "../../lib/app-data";
import { isAutoSyncPending } from "./format";

const INTERVALO_MS = 20_000;

export function useAutoSyncWatcher() {
  const { servers, refreshServers, usingRealData, handleRefresh } = useAppData();

  const pendentes = useMemo(
    () =>
      servers
        .filter(isAutoSyncPending)
        .map((s) => s.id)
        .sort((a, b) => a - b)
        .join(","),
    [servers],
  );

  const refreshFleet = useRef(handleRefresh);
  useEffect(() => {
    refreshFleet.current = handleRefresh;
  }, [handleRefresh]);

  const anterior = useRef(pendentes);
  useEffect(() => {
    const antes = anterior.current;
    anterior.current = pendentes;
    if (!antes || antes === pendentes || !usingRealData) return;
    const agora = new Set(pendentes.split(",").filter(Boolean));
    if (antes.split(",").some((id) => !agora.has(id))) void refreshFleet.current();
  }, [pendentes, usingRealData]);

  useEffect(() => {
    if (!pendentes) return;
    const timer = window.setInterval(() => {
      if (document.visibilityState === "visible") void refreshServers();
    }, INTERVALO_MS);
    return () => window.clearInterval(timer);
  }, [pendentes, refreshServers]);
}
