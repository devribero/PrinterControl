/**
 * Dependência externa: react (Context API, mesmo padrão de lib/toast.tsx).
 * Alterna a classe `dark` na tag <html> (ver .dark em app/globals.css) e
 * persiste a escolha em localStorage.
 *
 * Fase 8 — a preferência passou a ter TRÊS estados, não dois:
 *
 *   "light" | "dark" -> escolha explícita, fixa.
 *   "system"         -> acompanha o prefers-color-scheme, e continua
 *                       acompanhando quando o sistema muda (ex.: modo escuro
 *                       automático ao anoitecer).
 *
 * Antes só existiam os dois primeiros: o sistema era consultado apenas na
 * primeira visita e, ao tocar no botão do cabeçalho uma única vez, a escolha
 * virava fixa para sempre — não havia volta para "seguir o sistema".
 *
 * `theme` continua sendo o tema RESOLVIDO (o que está de fato aplicado), para
 * quem só quer saber se está claro ou escuro — como o botão do Topbar.
 */
"use client";

import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";

type Theme = "light" | "dark";
export type ThemePreference = Theme | "system";

const STORAGE_KEY = "elgin_theme";
const CONSULTA_ESCURO = "(prefers-color-scheme: dark)";

interface ThemeContextValue {
  /** Tema aplicado agora. Com preferência "system", é o que o SO pede. */
  theme: Theme;
  /** O que a pessoa escolheu — inclui "system". */
  preference: ThemePreference;
  setPreference: (preference: ThemePreference) => void;
  /** Alterna claro/escuro de forma explícita (botão do cabeçalho). */
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

function sistemaEscuro(): boolean {
  if (typeof window === "undefined") return false;
  return window.matchMedia?.(CONSULTA_ESCURO).matches ?? false;
}

function lerPreferencia(): ThemePreference {
  if (typeof window === "undefined") return "system";
  const salvo = localStorage.getItem(STORAGE_KEY);
  // "light"/"dark" cobrem também o que ficou gravado antes da Fase 8, quando
  // só existiam esses dois valores — nada a migrar.
  if (salvo === "light" || salvo === "dark" || salvo === "system") return salvo;
  return "system";
}

function resolver(preference: ThemePreference): Theme {
  if (preference === "system") return sistemaEscuro() ? "dark" : "light";
  return preference;
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  // Sem localStorage no servidor: começa em "system" e lê depois de montar,
  // para o HTML do servidor bater com o do cliente na hidratação.
  const [preference, setPreferenceState] = useState<ThemePreference>("system");
  const [theme, setTheme] = useState<Theme>("light");

  useEffect(() => {
    const inicial = lerPreferencia();
    setPreferenceState(inicial);
    setTheme(resolver(inicial));
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
  }, [theme]);

  // Só com "system" o SO manda; nos modos fixos o listener nem é registrado.
  useEffect(() => {
    if (preference !== "system") return;
    const mq = window.matchMedia?.(CONSULTA_ESCURO);
    if (!mq) return;

    function aoMudar(e: MediaQueryListEvent) {
      setTheme(e.matches ? "dark" : "light");
    }
    mq.addEventListener("change", aoMudar);
    return () => mq.removeEventListener("change", aoMudar);
  }, [preference]);

  const setPreference = useCallback((nova: ThemePreference) => {
    setPreferenceState(nova);
    setTheme(resolver(nova));
    try {
      localStorage.setItem(STORAGE_KEY, nova);
    } catch {
      // Storage bloqueado: a escolha vale para esta aba.
    }
  }, []);

  const toggleTheme = useCallback(() => {
    // O botão do cabeçalho é um interruptor: escolhe explicitamente o oposto
    // do que está na tela. Sair de "system" por aqui é intencional — quem
    // aperta quer aquele tema agora, não "às vezes".
    setPreference(theme === "dark" ? "light" : "dark");
  }, [theme, setPreference]);

  return (
    <ThemeContext.Provider value={{ theme, preference, setPreference, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme(): ThemeContextValue {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error("useTheme must be used within ThemeProvider");
  return ctx;
}
