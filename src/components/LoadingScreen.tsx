"use client";

import { useEffect, useState } from "react";
import styles from "./LoadingScreen.module.css";

const MIN_VISIBLE_MS = 700;
const HOLD_FULL_MS = 320;
const FADE_MS = 900;
const CREEP_STEP = 0.02;
const CREEP_INTERVAL_MS = 120;
const CREEP_CAP = 0.9;

interface LoadingScreenProps {
  /** 0..1 — etapas reais já concluídas do carregamento inicial. */
  progress: number;
  /** true quando o carregamento inicial terminou. */
  done: boolean;
}

type Phase = "loading" | "revealed" | "gone";

/**
 * Tela de carregamento da abertura do painel (design_handoff_loading_screen).
 * Só anda para a frente: depois de dissolver, não volta a aparecer nesta
 * carga da página, mesmo que outra carga comece (ex.: login).
 */
export default function LoadingScreen({ progress, done }: LoadingScreenProps) {
  const [phase, setPhase] = useState<Phase>("loading");
  const [creep, setCreep] = useState(0);

  useEffect(() => {
    if (done || phase !== "loading") return;
    const id = window.setInterval(() => setCreep((c) => Math.min(CREEP_CAP, c + CREEP_STEP)), CREEP_INTERVAL_MS);
    return () => window.clearInterval(id);
  }, [done, phase]);

  useEffect(() => {
    if (!done || phase !== "loading") return;
    // performance.now() conta desde a navegação: a tela já está pintada desde o HTML do servidor.
    const wait = Math.max(0, MIN_VISIBLE_MS - performance.now()) + HOLD_FULL_MS;
    const id = window.setTimeout(() => setPhase("revealed"), wait);
    return () => window.clearTimeout(id);
  }, [done, phase]);

  useEffect(() => {
    if (phase !== "revealed") return;
    // transitionend não dispara com a aba em segundo plano; o prazo garante a desmontagem.
    const id = window.setTimeout(() => setPhase("gone"), FADE_MS + 100);
    return () => window.clearTimeout(id);
  }, [phase]);

  useEffect(() => {
    if (phase !== "loading") return;
    document.body.setAttribute("aria-busy", "true");
    return () => document.body.removeAttribute("aria-busy");
  }, [phase]);

  if (phase === "gone") return null;

  const fill = done ? 1 : Math.max(progress, creep);

  return (
    <div
      role="status"
      aria-live="polite"
      aria-label="Carregando"
      className={phase === "revealed" ? `${styles.overlay} ${styles.revealed}` : styles.overlay}
      onTransitionEnd={(event) => {
        if (event.target === event.currentTarget && event.propertyName === "opacity" && phase === "revealed") {
          setPhase("gone");
        }
      }}
    >
      <div className={styles.inner}>
        <img
          src="/logo-elgin-trim.png"
          alt="Elgin"
          width={3097}
          height={1278}
          fetchPriority="high"
          className={styles.logo}
        />
        <div className={styles.track}>
          <div className={styles.bar} style={{ width: `${(fill * 100).toFixed(1)}%` }} />
        </div>
      </div>
    </div>
  );
}
