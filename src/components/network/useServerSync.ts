"use client";

/**
 * Sincronização manual de UM Print Server (POST /api/servers/{id}/sync).
 *
 * Muda o cadastro (cria, atualiza, desativa), então quem chama passa antes
 * por confirmação. Servidores reais já sincronizam sozinhos ao serem
 * cadastrados e a cada 6 h; se um desses ciclos estiver rodando, o backend
 * responde 409 — isso não é erro do usuário, vira aviso neutro.
 */
import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError, syncServer } from "../../lib/api";
import { adaptSyncResult } from "../../lib/adaptApi";
import { useApiErrorReporter } from "../../lib/apiErrors";
import { useAppData } from "../../lib/app-data";
import { useToast } from "../../lib/toast";
import type { PrintServer, SyncResult } from "../../types";

export interface SyncJob {
  id: number;
  serverId: number;
  host: string;
  startedAt: number;
  finishedAt: number | null;
  /** `busy` = 409: já havia uma sincronização automática em andamento. */
  status: "running" | "done" | "error" | "busy";
  result: SyncResult | null;
  error: string | null;
}

export function useServerSync() {
  const { refreshServers, usingRealData, handleRefresh } = useAppData();
  const { push } = useToast();
  const relatarErro = useApiErrorReporter();
  const [job, setJob] = useState<SyncJob | null>(null);
  const seq = useRef(0);

  // handleRefresh não é estável (função recriada a cada render do provider);
  // a ref evita recriar `start` por causa dela.
  const refreshFleet = useRef(handleRefresh);
  useEffect(() => {
    refreshFleet.current = handleRefresh;
  }, [handleRefresh]);

  const start = useCallback(
    async (server: PrintServer) => {
      const id = ++seq.current;
      setJob({
        id,
        serverId: server.id,
        host: server.host,
        startedAt: Date.now(),
        finishedAt: null,
        status: "running",
        result: null,
        error: null,
      });
      const concluir = (patch: Partial<SyncJob>) =>
        setJob((j) => (j && j.id === id ? { ...j, ...patch, finishedAt: Date.now() } : j));

      try {
        const resultado = adaptSyncResult(await syncServer(server.id));
        concluir({ status: "done", result: resultado });
        push({
          variant: "success",
          title: "Sincronização concluída",
          description:
            `${server.host}: ${resultado.created} criada(s), ${resultado.updated} atualizada(s), ` +
            `${resultado.deactivated} desativada(s).`,
        });
        // A frota em memória ficou desatualizada depois de gravar no banco.
        if (usingRealData) void refreshFleet.current();
      } catch (error) {
        if (error instanceof ApiError && error.status === 409) {
          const mensagem = error.message || "Uma sincronização automática já está em andamento.";
          concluir({ status: "busy", error: mensagem });
          push({
            variant: "info",
            title: "Sincronização automática em andamento",
            description: `${server.host} já está sendo sincronizado. Aguarde alguns minutos.`,
          });
        } else {
          concluir({ status: "error", error: relatarErro(error, `Falha na sincronização de ${server.host}`) });
        }
      } finally {
        void refreshServers();
      }
    },
    [push, relatarErro, refreshServers, usingRealData],
  );

  const dismiss = useCallback(() => {
    seq.current++;
    setJob(null);
  }, []);

  return { job, running: job?.status === "running", start, dismiss };
}
