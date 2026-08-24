"use client";

import type { ReactNode } from "react";
import { useAppData } from "../lib/app-data";
import Login from "./Login";
import AppShell from "./AppShell";
import MustChangePasswordGate from "./MustChangePasswordGate";
import styles from "./AuthGate.module.css";

/**
 * Decide entre tela de login, troca de senha obrigatória e painel. Enquanto
 * a sessão guardada está sendo confirmada no backend (`GET /api/auth/me`),
 * mostra um estado de espera em vez do formulário de login — sem isso, quem
 * já está logado veria a tela de login piscar a cada abertura do app.
 *
 * A troca obrigatória (`account.mustChangePassword`) entra ANTES do
 * `AppShell`: nenhuma tela do painel — nem a Sidebar, nem os dados — chega a
 * renderizar enquanto a flag estiver ligada. É reforço de UX, não a
 * proteção real: o backend recusa as mesmas rotas de qualquer forma
 * (`require_active_user`), então mesmo pulando esta checagem o painel
 * ficaria vazio, cheio de 403.
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

  if (account.mustChangePassword) {
    return <MustChangePasswordGate />;
  }

  return <AppShell>{children}</AppShell>;
}
