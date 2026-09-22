"use client";

/**
 * Uma impressora da lista: identificação à esquerda, uma barra por canal na
 * cor física do toner (lib/tonerColor) e, sem leitura, uma linha dizendo por
 * quê. A linha inteira é um botão que abre o PrinterDetailsModal do AppShell.
 */
import type { TonerLevel } from "../../types";
import type { TonerEntry } from "./tonerModel";
import { levelBand } from "./tonerModel";
import PrinterStatusBadge from "../PrinterStatusBadge";
import { tonerChannelColor } from "../../lib/tonerColor";
import { cn } from "../../lib/cn";
import styles from "./Toner.module.css";

const PERCENT_TONE = {
  critical: styles.percentCritical,
  low: styles.percentLow,
  ok: styles.percentOk,
} as const;

function ChannelBar({ level, theme }: { level: TonerLevel; theme: "light" | "dark" }) {
  const color = tonerChannelColor(level.color, theme);
  const pct = Math.max(0, Math.min(100, level.percent));
  return (
    <li className={styles.channel} title={`${level.label}: ${level.percent}%`}>
      <span className={styles.channelCode}>{level.color}</span>
      <span
        className={styles.channelTrack}
        role="meter"
        aria-label={level.label}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={pct}
      >
        <span className={styles.channelFill} style={{ width: `${pct}%`, backgroundColor: color }} />
      </span>
      <span className={cn(styles.channelPercent, PERCENT_TONE[levelBand(level.percent)])}>{level.percent}%</span>
    </li>
  );
}

interface TonerRowProps {
  entry: TonerEntry;
  theme: "light" | "dark";
  /** Nome do servidor para exibir; null quando o escopo já é um servidor só. */
  serverLabel: string | null;
  onOpen: () => void;
}

export default function TonerRow({ entry, theme, serverLabel, onOpen }: TonerRowProps) {
  const { printer: p, band, reason } = entry;
  const meta = [p.department, p.ip, serverLabel].filter(Boolean).join(" · ");

  return (
    <li>
      <button
        type="button"
        onClick={onOpen}
        className={cn(styles.row, band === "critical" && styles.rowCritical, band === "low" && styles.rowLow)}
      >
        <span className={styles.identity}>
          <span className={styles.nameLine}>
            <span className={styles.name}>{p.name}</span>
            {p.status !== "online" && <PrinterStatusBadge status={p.status} />}
          </span>
          <span className={styles.model}>{p.model || "Modelo não informado"}</span>
          <span className={styles.meta}>{meta}</span>
        </span>

        <span className={styles.levels}>
          {p.toner && p.toner.length > 0 ? (
            <ul className={styles.channels}>
              {p.toner.map((t) => (
                <ChannelBar key={t.color} level={t} theme={theme} />
              ))}
            </ul>
          ) : (
            <span className={styles.noReading}>{reason}</span>
          )}
          {p.status === "offline" && p.toner && p.toner.length > 0 && (
            <span className={styles.lastReading}>Última leitura {p.lastSeen}</span>
          )}
        </span>
      </button>
    </li>
  );
}
