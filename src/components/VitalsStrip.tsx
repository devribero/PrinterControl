"use client";

import { Activity, ArrowRight, CircleCheck, Clock, TriangleAlert, WifiOff, type LucideIcon } from "lucide-react";
import type { Alert } from "../types";
import { cn } from "../lib/cn";
import styles from "./VitalsStrip.module.css";

type StatusFilter = "Todos" | "online" | "offline" | "atencao";

interface VitalsStripProps {
  total: number;
  online: number;
  attention: number;
  offline: number;
  /** Ativas cuja última leitura é velha demais para descrever o presente (`stats.stale`). */
  stale?: number;
  activeStatus: StatusFilter;
  onSelectStatus: (status: StatusFilter) => void;
  topAlert: Alert | null;
  /** Nome da impressora do alerta — a mensagem do backend nem sempre o traz. */
  topAlertPrinter?: string | null;
  alertsRest: number;
  onViewAlerts: () => void;
  onSelectAlert?: (alert: Alert) => void;
}

function percentOf(value: number, total: number): number {
  return total > 0 ? Math.round((value / total) * 100) : 0;
}

const RING_RADIUS = 30;
const RING_CIRCUMFERENCE = 2 * Math.PI * RING_RADIUS;

/** Anel de disponibilidade: fatia online da frota ativa. */
function HealthRing({ percent }: { percent: number }) {
  const tone = percent >= 90 ? styles.ringGood : percent >= 70 ? styles.ringFair : styles.ringPoor;
  return (
    <svg className={cn(styles.ring, tone)} viewBox="0 0 72 72" aria-hidden="true">
      <circle className={styles.ringTrack} cx="36" cy="36" r={RING_RADIUS} />
      <circle
        className={styles.ringValue}
        cx="36"
        cy="36"
        r={RING_RADIUS}
        strokeDasharray={`${(percent / 100) * RING_CIRCUMFERENCE} ${RING_CIRCUMFERENCE}`}
        transform="rotate(-90 36 36)"
      />
      <text className={styles.ringText} x="36" y="34" textAnchor="middle">
        {percent}%
      </text>
      <text className={styles.ringCaption} x="36" y="46" textAnchor="middle">
        online
      </text>
    </svg>
  );
}

export default function VitalsStrip({
  total,
  online,
  attention,
  offline,
  stale = 0,
  activeStatus,
  onSelectStatus,
  topAlert,
  topAlertPrinter,
  alertsRest,
  onViewAlerts,
  onSelectAlert,
}: VitalsStripProps) {
  const tiles: { status: Exclude<StatusFilter, "Todos">; label: string; value: number; icon: LucideIcon; tone: string }[] = [
    { status: "online", label: "Online", value: online, icon: Activity, tone: styles.toneOnline },
    { status: "atencao", label: "Atenção", value: attention, icon: TriangleAlert, tone: styles.toneAttention },
    { status: "offline", label: "Offline", value: offline, icon: WifiOff, tone: styles.toneOffline },
  ];

  return (
    <section className={styles.strip} aria-label="Resumo da frota">
      <div className={styles.fleet}>
        <button
          type="button"
          onClick={() => onSelectStatus("Todos")}
          aria-pressed={activeStatus === "Todos"}
          className={cn(styles.fleetButton, activeStatus === "Todos" && styles.fleetButtonActive)}
        >
          <HealthRing percent={percentOf(online, total)} />
          <span className={styles.fleetText}>
            <span className={styles.eyebrow}>Frota monitorada</span>
            <span className={styles.totalValue}>{total}</span>
            {stale > 0 ? (
              <span className={cn(styles.fleetHint, styles.staleNote)}>
                <Clock size={12} aria-hidden="true" />
                {stale} sem coleta recente
              </span>
            ) : (
              <span className={styles.fleetHint}>impressoras ativas</span>
            )}
          </span>
        </button>

        <div
          className={styles.distribution}
          role="img"
          aria-label={`Distribuição: ${online} online, ${attention} em atenção, ${offline} offline`}
        >
          {online > 0 && <span className={styles.segOnline} style={{ flexGrow: online }} />}
          {attention > 0 && <span className={styles.segAttention} style={{ flexGrow: attention }} />}
          {offline > 0 && <span className={styles.segOffline} style={{ flexGrow: offline }} />}
        </div>
      </div>

      <div className={styles.statusGroup}>
        {tiles.map(({ status, label, value, icon: Icon, tone }) => {
          const active = activeStatus === status;
          const pct = percentOf(value, total);
          return (
            <button
              key={status}
              type="button"
              // Clicar de novo no filtro ativo volta para a frota inteira.
              onClick={() => onSelectStatus(active ? "Todos" : status)}
              aria-pressed={active}
              className={cn(styles.statusTile, tone, active && styles.statusTileActive)}
            >
              <span className={styles.statusHead}>
                <span className={styles.statusIcon}>
                  <Icon size={15} aria-hidden="true" />
                </span>
                {label}
              </span>
              <span className={styles.statusValueRow}>
                <span className={styles.statusValue}>{value}</span>
                <span className={styles.statusPct}>{pct}%</span>
              </span>
              <span className={styles.statusBar} aria-hidden="true">
                <span className={styles.statusBarFill} style={{ width: `${pct}%` }} />
              </span>
            </button>
          );
        })}
      </div>

      {topAlert ? (
        <div className={styles.alertPanel}>
          <div className={styles.alertHead}>
            <span className={styles.alertIcon}>
              <TriangleAlert size={15} aria-hidden="true" />
            </span>
            <p className={styles.alertEyebrow}>Mais urgente agora</p>
            {alertsRest > 0 && <span className={styles.alertCount}>+{alertsRest} outros</span>}
          </div>
          <button type="button" onClick={() => onSelectAlert?.(topAlert)} className={styles.alertMessage}>
            {topAlertPrinter && <span className={styles.alertPrinter}>{topAlertPrinter}</span>}
            <span className={styles.alertText}>{topAlert.message}</span>
          </button>
          <button type="button" onClick={onViewAlerts} className={styles.alertLink}>
            Ver todos os alertas
            <ArrowRight size={14} aria-hidden="true" />
          </button>
        </div>
      ) : (
        <div className={cn(styles.alertPanel, styles.clearPanel)}>
          <div className={styles.alertHead}>
            <span className={styles.alertIcon}>
              <CircleCheck size={15} aria-hidden="true" />
            </span>
            <p className={styles.alertEyebrow}>Tudo em ordem</p>
          </div>
          <p className={styles.clearText}>Nenhum alerta ativo na frota agora.</p>
        </div>
      )}
    </section>
  );
}
