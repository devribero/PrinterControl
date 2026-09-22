"use client";

/**
 * Seções de preferência deste dispositivo: Aparência (tema) e
 * Acessibilidade. Nada aqui passa pelo backend — tema e acessibilidade
 * ficam no localStorage (lib/theme, lib/preferences) e valem na hora.
 */
import { Monitor, Moon, RotateCcw, Sun } from "lucide-react";
import { usePreferences, ESCALAS } from "../../lib/preferences";
import { useTheme, type ThemePreference } from "../../lib/theme";
import { useToast } from "../../lib/toast";
import { cn } from "../../lib/cn";
import styles from "../SettingsView.module.css";
import { Card } from "./ui";

const TEMAS: { value: ThemePreference; label: string; icon: typeof Sun; hint: string }[] = [
  { value: "system", label: "Sistema", icon: Monitor, hint: "Acompanha o tema do computador." },
  { value: "light", label: "Claro", icon: Sun, hint: "Sempre claro." },
  { value: "dark", label: "Escuro", icon: Moon, hint: "Sempre escuro." },
];

export function AppearanceSection() {
  const { theme, preference, setPreference } = useTheme();

  return (
    <Card
      title="Tema"
      description={`Vale só neste dispositivo e é aplicado na hora. Agora a tela está no modo ${
        theme === "dark" ? "escuro" : "claro"
      }.`}
    >
      <fieldset className={styles.fieldset}>
        <legend className={styles.srOnly}>Tema</legend>
        <div className={styles.optionGrid}>
          {TEMAS.map((t) => {
            const Icone = t.icon;
            const ativo = preference === t.value;
            return (
              <label key={t.value} className={cn(styles.option, ativo && styles.optionActive)}>
                <input
                  type="radio"
                  name="tema"
                  value={t.value}
                  checked={ativo}
                  onChange={() => setPreference(t.value)}
                  className={styles.srOnly}
                />
                <Icone size={18} aria-hidden="true" />
                <span className={styles.optionLabel}>{t.label}</span>
                <span className={styles.optionHint}>{t.hint}</span>
              </label>
            );
          })}
        </div>
      </fieldset>
      {/* O botão do cabeçalho só alterna claro/escuro; sem esta opção, usá-lo
          uma vez prendia o painel fora do tema do sistema. */}
      <p className={styles.hint}>
        O botão de tema no cabeçalho fixa claro ou escuro. Para voltar a acompanhar o computador, escolha{" "}
        <strong>Sistema</strong> aqui.
      </p>
    </Card>
  );
}

export function AccessibilitySection() {
  const { preferences, setPreference, reset, modificado } = usePreferences();
  const { push } = useToast();

  function restaurar() {
    reset();
    push({ variant: "info", title: "Padrões restaurados", description: "Texto, animações e foco voltaram ao normal." });
  }

  return (
    <>
      <Card
        title="Tamanho do texto"
        description="Soma-se ao zoom do navegador. Vale só neste dispositivo."
      >
        <fieldset className={styles.fieldset}>
          <legend className={styles.srOnly}>Tamanho do texto</legend>
          <div className={styles.optionGrid}>
            {ESCALAS.map((e) => {
              const ativo = preferences.fontScale === e.value;
              return (
                <label key={e.value} className={cn(styles.option, ativo && styles.optionActive)}>
                  <input
                    type="radio"
                    name="escala"
                    value={e.value}
                    checked={ativo}
                    onChange={() => setPreference("fontScale", e.value)}
                    className={styles.srOnly}
                  />
                  {/* Em rem de propósito: a amostra cresce junto com a escala aplicada. */}
                  <span className={styles.escalaAmostra} style={{ fontSize: `${e.value}rem` }} aria-hidden="true">
                    Aa
                  </span>
                  <span className={styles.optionLabel}>{e.label}</span>
                  <span className={styles.optionHint}>
                    {e.value === 1 ? "Tamanho do navegador" : `${Math.round(e.value * 100)}%`}
                  </span>
                </label>
              );
            })}
          </div>
        </fieldset>
      </Card>

      <Card
        title="Movimento e foco"
        description="Guardadas neste dispositivo, não na sua conta."
        footer={
          modificado ? (
            <button type="button" onClick={restaurar} className={styles.secondaryButton}>
              <RotateCcw size={16} />
              Restaurar padrões
            </button>
          ) : undefined
        }
      >
        <label className={styles.switchRow}>
          <span className={styles.switchBody}>
            <span className={styles.switchLabel}>Reduzir animações</span>
            <span className={styles.hint}>
              Corta transições e movimentos. Útil quando você não pode mudar essa opção no sistema operacional.
            </span>
          </span>
          <input
            type="checkbox"
            role="switch"
            checked={preferences.reduceMotion}
            onChange={(e) => setPreference("reduceMotion", e.target.checked)}
            className={styles.switch}
          />
        </label>

        <label className={styles.switchRow}>
          <span className={styles.switchBody}>
            <span className={styles.switchLabel}>Realce de foco reforçado</span>
            <span className={styles.hint}>
              Contorno mais grosso ao navegar pelo teclado, para não perder o cursor em telas cheias como a tabela
              de impressoras.
            </span>
          </span>
          <input
            type="checkbox"
            role="switch"
            checked={preferences.strongFocus}
            onChange={(e) => setPreference("strongFocus", e.target.checked)}
            className={styles.switch}
          />
        </label>
      </Card>
    </>
  );
}
