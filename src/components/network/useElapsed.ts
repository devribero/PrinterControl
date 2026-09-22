"use client";

import { useEffect, useState } from "react";

/**
 * Tempo decorrido desde `startedAt`, atualizado a cada segundo enquanto
 * `finishedAt` for null. Quem usa monta um componente por execução (key =
 * id do job), então o relógio sempre começa do zero.
 */
export function useElapsed(startedAt: number, finishedAt: number | null): number {
  const [now, setNow] = useState(() => Date.now());
  const running = finishedAt === null;

  useEffect(() => {
    if (!running) return;
    const timer = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(timer);
  }, [running]);

  return Math.max(0, (finishedAt ?? now) - startedAt);
}
