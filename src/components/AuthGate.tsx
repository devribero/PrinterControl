"use client";

import type { ReactNode } from "react";
import { useAppData } from "../lib/app-data";
import Login from "./Login";
import AppShell from "./AppShell";
import LoadingScreen from "./LoadingScreen";
import MustChangePasswordGate from "./MustChangePasswordGate";

/**
 * Decide entre tela de login, troca de senha obrigatória e painel. Enquanto
 * a sessão guardada está sendo confirmada no backend (`GET /api/auth/me`),
 * nenhuma das três é renderizada — sem isso, quem já está logado veria a
 * tela de login piscar a cada abertura do app. A LoadingScreen cobre esse
 * intervalo e a primeira carga da frota, e dissolve revelando o que vier.
 *
 * A troca obrigatória (`account.mustChangePassword`) entra ANTES do
 * `AppShell`: nenhuma tela do painel — nem a Sidebar, nem os dados — chega a
 * renderizar enquanto a flag estiver ligada. É reforço de UX, não a
 * proteção real: o backend recusa as mesmas rotas de qualquer forma
 * (`require_active_user`), então mesmo pulando esta checagem o painel
 * ficaria vazio, cheio de 403.
 */
export default function AuthGate({ children }: { children: ReactNode }) {
  const { account, sessionLoading, initialLoading, handleLoginSuccess } = useAppData();

  // Pronto: sessão resolvida e, havendo conta, a primeira carga da frota decidida (real ou demonstração).
  const ready = !sessionLoading && (!account || !initialLoading);
  const progress = sessionLoading ? 0.1 : ready ? 1 : 0.6;

  let content: ReactNode = null;
  if (!sessionLoading) {
    if (!account) content = <Login onSuccess={handleLoginSuccess} />;
    else if (account.mustChangePassword) content = <MustChangePasswordGate />;
    else content = <AppShell>{children}</AppShell>;
  }

  return (
    <>
      {content}
      <LoadingScreen progress={progress} done={ready} />
    </>
  );
}
