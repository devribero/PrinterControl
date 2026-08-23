"use client";

import type { ReactNode } from "react";
import { useAppData } from "../lib/app-data";
import Login from "./Login";
import AppShell from "./AppShell";
import styles from "./AuthGate.module.css";

/**
 * Decide entre tela de login e painel. Enquanto a sessão guardada está sendo
 * confirmada no backend (`GET /api/auth/me`), mostra um estado de espera em
 * vez do formulário de login — sem isso, quem já está logado veria a tela de
 * login piscar a cada abertura do app.
 */
export default function AuthGate({ children }: { children: ReactNode }) {
  const { account, sessionLoading, handleLoginSuccess } = useAppData();

  if (sessionLoading) {
    return (
      <div className={styles.wrap} role="status" aria-live="polite">
        <div className={styles.spinner} />
        <p className={styles.text}>Restaurando sessão...</p>
      </div>
    );
  }

  if (!account) {
    return <Login onSuccess={handleLoginSuccess} />;
  }

  return <AppShell>{children}</AppShell>;
}
