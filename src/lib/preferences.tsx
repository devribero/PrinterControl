"use client";

/**
 * Preferências de acessibilidade (Fase 8).
 *
 * Separado de lib/theme.tsx de propósito: tema é uma escolha estética que já
 * tinha dono e um atalho no cabeçalho; isto aqui é acessibilidade, muda o
 * comportamento da interface e pertence a Configurações.
 *
 * Guardado em localStorage, por dispositivo — e não na conta. Duas razões:
 * quem usa um leitor de tela na estação de trabalho não necessariamente
 * precisa do mesmo no notebook, e persistir no servidor exigiria uma tabela
 * de preferências que nada mais nesta fase justifica.
 *
 * A aplicação é por classe/variável na <html>, no mesmo padrão que
 * lib/theme.tsx já usava para o modo escuro (ver app/globals.css).
 */
import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";

const STORAGE_KEY = "elgin_a11y";

/** Multiplicadores da escala de texto. 1 = tamanho padrão do navegador. */
export const ESCALAS = [
  { value: 1, label: "Padrão" },
  { value: 1.15, label: "Grande" },
  { value: 1.3, label: "Maior" },
] as const;

export interface Preferences {
  /** Corta animações e transições, somando-se ao prefers-reduced-motion do SO. */
  reduceMotion: boolean;
  /** Anel de foco mais grosso, para navegação por teclado em telas densas. */
  strongFocus: boolean;
  fontScale: number;
}

export const PREFERENCIAS_PADRAO: Preferences = {
  reduceMotion: false,
  strongFocus: false,
  fontScale: 1,
};

interface PreferencesContextValue {
  preferences: Preferences;
  setPreference: <K extends keyof Preferences>(key: K, value: Preferences[K]) => void;
  reset: () => void;
  /** true quando alguma preferência difere do padrão — habilita "Restaurar". */
  modificado: boolean;
}

const PreferencesContext = createContext<PreferencesContextValue | null>(null);

function ler(): Preferences {
  if (typeof window === "undefined") return PREFERENCIAS_PADRAO;
  try {
    const bruto = localStorage.getItem(STORAGE_KEY);
    if (!bruto) return PREFERENCIAS_PADRAO;
    const salvo = JSON.parse(bruto) as Partial<Preferences>;
    return {
      reduceMotion: salvo.reduceMotion === true,
      strongFocus: salvo.strongFocus === true,
      // Só aceita um valor da lista: um número arbitrário vindo de
      // localStorage adulterado deixaria a interface ilegível.
      fontScale: ESCALAS.some((e) => e.value === salvo.fontScale) ? salvo.fontScale! : 1,
    };
  } catch {
    // JSON corrompido ou storage bloqueado (modo privativo, política de
    // cookies): cai no padrão em vez de derrubar a aplicação.
    return PREFERENCIAS_PADRAO;
  }
}

export function PreferencesProvider({ children }: { children: ReactNode }) {
  // Começa no padrão e lê o storage só depois de montar: no servidor não há
  // localStorage, e divergir do HTML renderizado quebraria a hidratação.
  const [preferences, setPreferences] = useState<Preferences>(PREFERENCIAS_PADRAO);

  useEffect(() => {
    setPreferences(ler());
  }, []);

  useEffect(() => {
    const raiz = document.documentElement;
    raiz.classList.toggle("reduce-motion", preferences.reduceMotion);
    raiz.classList.toggle("strong-focus", preferences.strongFocus);
    raiz.style.setProperty("--font-scale", String(preferences.fontScale));
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(preferences));
    } catch {
      // Storage indisponível: a preferência vale para esta aba e pronto.
    }
  }, [preferences]);

  const setPreference = useCallback(
    <K extends keyof Preferences>(key: K, value: Preferences[K]) => {
      setPreferences((p) => ({ ...p, [key]: value }));
    },
    [],
  );

  const reset = useCallback(() => setPreferences(PREFERENCIAS_PADRAO), []);

  const modificado =
    preferences.reduceMotion !== PREFERENCIAS_PADRAO.reduceMotion ||
    preferences.strongFocus !== PREFERENCIAS_PADRAO.strongFocus ||
    preferences.fontScale !== PREFERENCIAS_PADRAO.fontScale;

  return (
    <PreferencesContext.Provider value={{ preferences, setPreference, reset, modificado }}>
      {children}
    </PreferencesContext.Provider>
  );
}

export function usePreferences(): PreferencesContextValue {
  const ctx = useContext(PreferencesContext);
  if (!ctx) throw new Error("usePreferences must be used within PreferencesProvider");
  return ctx;
}
