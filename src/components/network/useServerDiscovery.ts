"use client";

/**
 * Descoberta de UM Print Server (POST /api/servers/{id}/discover).
 *
 * Não grava nada — é uma fotografia do que o servidor publica agora. Em
 * servidor remoto pode levar 1–2 min, por isso roda "em segundo plano": o
 * estado vive aqui (e não no painel que a exibe), o usuário pode trocar de
 * escopo e continuar usando a página, e um toast avisa quando termina.
 *
 * Uma descoberta por vez. "Descartar" não cancela o backend (não há como);
 * só faz a tela ignorar a resposta quando ela chegar.
 */
import { useCallback, useRef, useState } from "react";
import { discoverServer, type ApiDiscoveryResponse } from "../../lib/api";
import { useApiErrorReporter } from "../../lib/apiErrors";
import { useAppData } from "../../lib/app-data";
import { useToast } from "../../lib/toast";
import type { PrintServer } from "../../types";

export interface DiscoveryJob {
  /** Sequencial local: distingue a execução atual de uma descartada. */
  id: number;
  serverId: number;
  host: string;
  startedAt: number;
  finishedAt: number | null;
  status: "running" | "done" | "error";
  result: ApiDiscoveryResponse | null;
  error: string | null;
}

export function useServerDiscovery() {
  const { refreshServers } = useAppData();
  const { push } = useToast();
  const relatarErro = useApiErrorReporter();
  const [job, setJob] = useState<DiscoveryJob | null>(null);
  const seq = useRef(0);

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
      try {
        const data = await discoverServer(server.id);
        if (seq.current !== id) return;
        setJob((j) => (j && j.id === id ? { ...j, status: "done", result: data, finishedAt: Date.now() } : j));
        push({
          variant: "success",
          title: "Descoberta concluída",
          description: `${data.count} fila(s) encontrada(s) em ${server.host}. Nada foi gravado.`,
        });
      } catch (error) {
        if (seq.current !== id) return;
        const mensagem = relatarErro(error, `Falha na descoberta em ${server.host}`);
        setJob((j) => (j && j.id === id ? { ...j, status: "error", error: mensagem, finishedAt: Date.now() } : j));
      } finally {
        // O backend guarda o desfecho (last_status/last_seen_at) — relê para
        // o cartão refletir o que acabou de acontecer.
        void refreshServers();
      }
    },
    [push, relatarErro, refreshServers],
  );

  const dismiss = useCallback(() => {
    seq.current++;
    setJob(null);
  }, []);

  return { job, running: job?.status === "running", start, dismiss };
}
