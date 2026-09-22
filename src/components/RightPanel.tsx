/**
 * Faixa "Precisa de atenção" do Dashboard: três cards lado a lado — alertas
 * ativos, impressoras offline e toner baixo — cada um com as poucas linhas
 * que pedem ação agora e um link para a lista completa.
 *
 * O arquivo guarda o nome histórico (era a coluna direita, com a lista de
 * toner da frota inteira e "Ações rápidas"). Reorganizado em 22/09/2026:
 * - a lista de toner de TODAS as impressoras repetia a tela Suprimentos; aqui
 *   só entram as que estão baixas, da menor para a maior;
 * - "Ações rápidas" repetia o menu lateral (e "Adicionar impressora" era um
 *   aviso de "em breve") — saiu;
 * - o alerta mais urgente, que ficava na faixa de resumo, virou o card de
 *   alertas, com os primeiros por severidade.
 *
 * Toda linha que fala de uma impressora abre o PrinterDetailsModal (via
 * `onOpenDetails` / `onSelectAlert`, o mesmo mecanismo da tabela).
 */
"use client";

import { ArrowRight } from "lucide-react";
import { tonerChannelColor } from "../lib/tonerColor";
import { CRITICAL_MAX, LOW_MAX, levelBand } from "./toner/tonerModel";
import { useTheme } from "../lib/theme";
import { cn } from "../lib/cn";
import type { Alert, Printer, TonerLevel } from "../types";
import styles from "./RightPanel.module.css";

/** Linhas por card: o bastante para agir, pouco para a faixa não virar lista. */
const LIMITE = 5;
/** Cortes da tela Suprimentos e dos alertas de toner do backend (≤10% / ≤20%). */
const TONER_CRITICO = CRITICAL_MAX;
const TONER_BAIXO = LOW_MAX;

const PESO_SEVERIDADE: Record<Alert["severity"], number> = { critical: 0, warning: 1, info: 2 };

/** Nível que decide a posição da impressora na lista: a cor que acaba primeiro. */
function menorToner(printer: Printer): TonerLevel | null {
  if (!printer.toner || printer.toner.length === 0) return null;
  return printer.toner.reduce((min, t) => (t.percent < min.percent ? t : min));
}

/**
 * Alerta do backend traz ISO (`created_at`); os derivados do conjunto de
 * demonstração trazem texto pronto ("agora", "há 12 min"). ISO vira tempo
 * relativo a `agora` (a última coleta, não o relógio — mantém o render puro);
 * texto passa direto.
 */
function quando(ts: string, agora: Date): string {
  const d = new Date(ts);
  if (!/^\d{4}-\d{2}-\d{2}/.test(ts) || Number.isNaN(d.getTime())) return ts;
  const min = Math.floor((agora.getTime() - d.getTime()) / 60000);
  if (min < 1) return "agora";
  if (min < 60) return `há ${min} min`;
  if (min < 24 * 60) return `há ${Math.floor(min / 60)} h`;
  return d.toLocaleString("pt-BR", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
}

function Card({
  title,
  count,
  tone,
  meta,
  loading,
  footer,
  children,
}: {
  title: string;
  count: number;
  /** Cor do contador quando há itens; zero fica sempre neutro. */
  tone: "danger" | "warning" | "neutral";
  meta?: string;
  loading: boolean;
  footer: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <section className={styles.card} aria-busy={loading || undefined}>
      <header className={styles.cardHeader}>
        <h3 className={styles.cardTitle}>{title}</h3>
        {!loading && (
          <span
            className={cn(
              styles.count,
              count > 0 && tone === "danger" && styles.countDanger,
              count > 0 && tone === "warning" && styles.countWarning,
            )}
          >
            {count}
          </span>
        )}
        {!loading && meta && <span className={styles.cardMeta}>{meta}</span>}
      </header>
      <div className={styles.cardBody}>
        {loading ? (
          <div className={styles.skeleton} aria-hidden="true">
            {[0, 1, 2].map((i) => (
              <span key={i} className={cn(styles.skeletonRow, "animate-pulse")} />
            ))}
          </div>
        ) : (
          children
        )}
      </div>
      {!loading && <footer className={styles.cardFooter}>{footer}</footer>}
    </section>
  );
}

function FooterLink({ label, onClick, rest }: { label: string; onClick: () => void; rest?: number }) {
  return (
    <>
      {(rest ?? 0) > 0 ? <span className={styles.rest}>e mais {rest}</span> : <span />}
      <button type="button" onClick={onClick} className={styles.footerLink}>
        {label}
        <ArrowRight size={14} aria-hidden="true" />
      </button>
    </>
  );
}

function Empty({ children }: { children: React.ReactNode }) {
  return (
    <p className={styles.empty}>
      <span className={styles.emptyDot} aria-hidden="true" />
      {children}
    </p>
  );
}

interface RightPanelProps {
  loading: boolean;
  alerts: Alert[];
  /** Todas as impressoras do escopo (inclui desativadas) — resolve o nome do alerta. */
  printers: Printer[];
  /** Frota ativa (já no escopo de servidor). Base de "offline" e "toner baixo". */
  fleet: Printer[];
  /** Referência de "agora" para o tempo relativo dos alertas (última coleta). */
  now: Date;
  onOpenDetails: (printer: Printer) => void;
  onSelectAlert: (alert: Alert) => void;
  onViewAlerts: () => void;
  onViewToner: () => void;
  onShowOffline: () => void;
}

export default function RightPanel({
  loading,
  alerts,
  printers,
  fleet,
  now,
  onOpenDetails,
  onSelectAlert,
  onViewAlerts,
  onViewToner,
  onShowOffline,
}: RightPanelProps) {
  const { theme } = useTheme();
  const nomes = new Map(printers.map((p) => [p.id, p.name]));

  // sort é estável: dentro da mesma severidade vale a ordem do backend.
  const alertas = [...alerts].sort((a, b) => PESO_SEVERIDADE[a.severity] - PESO_SEVERIDADE[b.severity]);
  const criticos = alerts.filter((a) => a.severity === "critical").length;

  // Quem caiu por último primeiro: é a queda que ainda dá para investigar.
  const offline = fleet
    .filter((p) => p.status === "offline")
    .sort((a, b) => (b.lastSeenAt ?? "").localeCompare(a.lastSeenAt ?? ""));

  const comToner = fleet.filter((p) => p.toner && p.toner.length > 0).length;
  const tonerBaixo = fleet
    .map((printer) => ({ printer, nivel: menorToner(printer) }))
    .filter((item): item is { printer: Printer; nivel: TonerLevel } => item.nivel !== null && levelBand(item.nivel.percent) !== "ok")
    .sort((a, b) => a.nivel.percent - b.nivel.percent);
  const tonerCritico = tonerBaixo.filter((t) => levelBand(t.nivel.percent) === "critical").length;

  return (
    <div className={styles.grid} role="region" aria-label="Precisa de atenção">
      <Card
        title="Alertas ativos"
        count={alerts.length}
        tone={criticos > 0 ? "danger" : "warning"}
        meta={criticos > 0 ? `${criticos} ${criticos === 1 ? "crítico" : "críticos"}` : undefined}
        loading={loading}
        footer={<FooterLink label="Ver alertas" onClick={onViewAlerts} rest={alertas.length - LIMITE} />}
      >
        {alertas.length === 0 ? (
          <Empty>Nenhum alerta ativo.</Empty>
        ) : (
          <ul className={styles.list}>
            {alertas.slice(0, LIMITE).map((a) => {
              const nome = nomes.get(a.printerId);
              return (
                <li key={a.id}>
                  <button type="button" onClick={() => onSelectAlert(a)} className={styles.row} disabled={!nome}>
                    <span
                      className={cn(
                        styles.dot,
                        a.severity === "critical" ? styles.dotDanger : a.severity === "warning" ? styles.dotWarning : styles.dotMuted,
                      )}
                      aria-label={a.severity === "critical" ? "Crítico" : a.severity === "warning" ? "Aviso" : "Informativo"}
                    />
                    <span className={styles.rowMain}>
                      <span className={styles.rowTitle}>{nome ?? "Impressora removida"}</span>
                      <span className={styles.rowSub}>{a.message}</span>
                    </span>
                    <span className={styles.rowAside}>{quando(a.timestamp, now)}</span>
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </Card>

      <Card
        title="Offline"
        count={offline.length}
        tone="neutral"
        meta={offline.length > 0 && fleet.length > 0 ? `${Math.round((offline.length / fleet.length) * 100)}% da frota` : undefined}
        loading={loading}
        footer={
          <FooterLink
            label={offline.length > 0 ? "Filtrar na tabela" : "Ver frota"}
            onClick={onShowOffline}
            rest={offline.length - LIMITE}
          />
        }
      >
        {offline.length === 0 ? (
          <Empty>Todas as impressoras ativas estão respondendo.</Empty>
        ) : (
          <ul className={styles.list}>
            {offline.slice(0, LIMITE).map((p) => (
              <li key={p.id}>
                <button type="button" onClick={() => onOpenDetails(p)} className={styles.row}>
                  <span className={cn(styles.dot, styles.dotMuted)} aria-hidden="true" />
                  <span className={styles.rowMain}>
                    <span className={styles.rowTitle}>{p.name}</span>
                    <span className={styles.rowSub}>
                      <span className={styles.mono}>{p.ip}</span>
                      {p.department ? ` · ${p.department}` : ""}
                    </span>
                  </span>
                  <span className={styles.rowAside} title="Última leitura">
                    {p.lastSeen}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </Card>

      <Card
        title="Toner baixo"
        count={tonerBaixo.length}
        tone={tonerCritico > 0 ? "danger" : "warning"}
        meta={tonerCritico > 0 ? `${tonerCritico} ${tonerCritico === 1 ? "crítica" : "críticas"} (≤ ${TONER_CRITICO}%)` : `≤ ${TONER_BAIXO}%`}
        loading={loading}
        footer={<FooterLink label="Ver suprimentos" onClick={onViewToner} rest={tonerBaixo.length - LIMITE} />}
      >
        {comToner === 0 ? (
          <Empty>Nenhuma impressora ativa informou nível de toner ainda.</Empty>
        ) : tonerBaixo.length === 0 ? (
          <Empty>Nenhum cartucho em {TONER_BAIXO}% ou menos.</Empty>
        ) : (
          <ul className={styles.list}>
            {tonerBaixo.slice(0, LIMITE).map(({ printer, nivel }) => {
              const percent = Math.max(0, Math.min(100, nivel.percent));
              // Em impressora colorida, diz QUAL cor é a mais baixa; em
              // monocromática só existe o preto e a marca seria ruído.
              const colorida = (printer.toner?.length ?? 0) > 1;
              return (
                <li key={printer.id}>
                  <button
                    type="button"
                    onClick={() => onOpenDetails(printer)}
                    className={cn(styles.row, styles.tonerRow, levelBand(percent) === "critical" ? styles.levelCritical : styles.levelLow)}
                    aria-label={`${printer.name}: ${nivel.label} em ${nivel.percent}%`}
                  >
                    <span className={styles.rowMain}>
                      <span className={styles.rowTitle}>{printer.name}</span>
                      <span className={styles.tonerTrack} aria-hidden="true">
                        <span className={styles.tonerFill} style={{ width: `${percent}%` }} />
                      </span>
                    </span>
                    <span className={styles.tonerValue}>
                      {colorida && (
                        <span className={styles.tonerChannel}>
                          <span
                            className={styles.tonerChannelDot}
                            style={{ backgroundColor: tonerChannelColor(nivel.color, theme) }}
                          />
                          {nivel.color}
                        </span>
                      )}
                      {nivel.percent}%
                    </span>
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </Card>
    </div>
  );
}
