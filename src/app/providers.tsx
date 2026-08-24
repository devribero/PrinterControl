"use client";

import type { ReactNode } from "react";
import { ThemeProvider } from "../lib/theme";
import { PreferencesProvider } from "../lib/preferences";
import { ToastProvider } from "../lib/toast";
import { AppDataProvider } from "../lib/app-data";
import AuthGate from "../components/AuthGate";

export default function Providers({ children }: { children: ReactNode }) {
  return (
    <ThemeProvider>
      {/* Acessibilidade envolve tudo e nao depende de sessao: as
          preferencias valem inclusive na tela de login. */}
      <PreferencesProvider>
        <ToastProvider>
          <AppDataProvider>
            <AuthGate>{children}</AuthGate>
          </AppDataProvider>
        </ToastProvider>
      </PreferencesProvider>
    </ThemeProvider>
  );
}
