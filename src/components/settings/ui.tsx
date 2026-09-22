"use client";

/**
 * Peças visuais compartilhadas pelas seções de Configurações.
 *
 * Todas usam o mesmo CSS module do SettingsView: a página é uma superfície
 * só, e manter um arquivo de estilo evita que as seções divirjam entre si.
 */
import { useId, type ReactNode } from "react";
import { cn } from "../../lib/cn";
import styles from "../SettingsView.module.css";

/** Painel de uma seção (o conteúdo de uma aba da navegação lateral). */
export function SettingsPanel({
  id,
  title,
  description,
  active,
  children,
}: {
  id: string;
  title: string;
  description: string;
  active: boolean;
  children: ReactNode;
}) {
  return (
    <section
      id={`painel-${id}`}
      role="tabpanel"
      aria-labelledby={`aba-${id}`}
      hidden={!active}
      className={styles.panel}
    >
      <header className={styles.panelHeader}>
        <h2 className={styles.panelTitle}>{title}</h2>
        <p className={styles.panelDescription}>{description}</p>
      </header>
      {children}
    </section>
  );
}

/** Cartão dentro de um painel. `readOnly` marca informação que não se edita aqui. */
export function Card({
  title,
  description,
  readOnly,
  children,
  footer,
  className,
}: {
  title: string;
  description?: ReactNode;
  readOnly?: boolean;
  children: ReactNode;
  footer?: ReactNode;
  className?: string;
}) {
  return (
    <div className={cn(styles.card, className)}>
      <div className={styles.cardHeader}>
        <div className={styles.cardHeading}>
          <h3 className={styles.cardTitle}>{title}</h3>
          {description && <p className={styles.cardDescription}>{description}</p>}
        </div>
        {readOnly && <span className={styles.readOnlyTag}>Somente leitura</span>}
      </div>
      <div className={styles.cardBody}>{children}</div>
      {footer && <div className={styles.cardFooter}>{footer}</div>}
    </div>
  );
}

/**
 * Campo de formulário com rótulo, ajuda e erro ligados por aria-describedby.
 * `children` recebe os ids para aplicar no input.
 */
export function Field({
  label,
  hint,
  error,
  children,
}: {
  label: string;
  hint?: ReactNode;
  error?: string | null;
  children: (props: { id: string; "aria-describedby"?: string; "aria-invalid"?: boolean }) => ReactNode;
}) {
  const id = useId();
  const hintId = `${id}-ajuda`;
  const errorId = `${id}-erro`;
  const describedBy = [error ? errorId : null, hint ? hintId : null].filter(Boolean).join(" ") || undefined;

  return (
    <div className={styles.field}>
      <label htmlFor={id} className={styles.label}>
        {label}
      </label>
      {children({ id, "aria-describedby": describedBy, "aria-invalid": error ? true : undefined })}
      {error && (
        <p id={errorId} className={styles.fieldError}>
          {error}
        </p>
      )}
      {hint && (
        <p id={hintId} className={styles.hint}>
          {hint}
        </p>
      )}
    </div>
  );
}

/** Lista de fatos só de leitura (rótulo / valor / explicação). */
export function FactList({ children }: { children: ReactNode }) {
  return <dl className={styles.factList}>{children}</dl>;
}

export function Fact({ label, value, hint }: { label: string; value: ReactNode; hint?: ReactNode }) {
  return (
    <div className={styles.fact}>
      <dt className={styles.factLabel}>{label}</dt>
      <dd className={styles.factValue}>
        {value}
        {hint && <span className={styles.factHint}>{hint}</span>}
      </dd>
    </div>
  );
}

/** Marcador de estado com ponto + texto (nunca só cor). */
export function StatusPill({ tone, children }: { tone: "ok" | "warn" | "danger" | "neutral"; children: ReactNode }) {
  return (
    <span
      className={cn(
        styles.pill,
        tone === "ok" && styles.pillOk,
        tone === "warn" && styles.pillWarn,
        tone === "danger" && styles.pillDanger,
      )}
    >
      <span className={styles.pillDot} aria-hidden="true" />
      {children}
    </span>
  );
}
