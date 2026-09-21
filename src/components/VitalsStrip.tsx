"use client";

/**
 * Faixa de resumo do Dashboard.
 *
 * DECISÕES DE VISUALIZAÇÃO (e o que elas substituíram)
 * ----------------------------------------------------
 * - O total da frota é a ÚNICA figura grande da tela, em sans e com os
 *   algarismos proporcionais da fonte. Era mono a 42px: `tabular-nums` dá a
 *   todo dígito a largura de um zero, e em corpo grande o número fica solto.
 *
 * - A proporção online/atenção/offline é dita UMA vez, pela barra empilhada.
 *   Antes era dita três vezes — anel de rosca, barra de distribuição e uma
 *   mini-barra dentro de cada cartão de status —, três desenhos para o mesmo
 *   fato. O anel também era uma rosca de duas fatias, que é a forma errada
 *   para uma razão única.
 *
 * - Os status são linhas com marcador colorido, não cartões preenchidos. O
 *   número fica em cor de texto: quem carrega a identidade é o ponto ao
 *   lado, nunca o texto. Um "0" em laranja e um "24" em verde sobre blocos
 *   tingidos é ruído de cor sobre informação que os rótulos já dão.
 *
 * Os três status continuam clicáveis: filtram a tabela do Dashboard.
 */

import { ArrowRight, CircleCheck, Clock, TriangleAlert } from "lucide-react";
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
  const rows: { status: Exclude<StatusFilter, "Todos">; label: string; value: number; tone: string }[] = [
    { status: "online", label: "Online", value: online, tone: styles.toneOnline },
    { status: "atencao", label: "Atenção", value: attention, tone: styles.toneAttention },
    { status: "offline", label: "Offline", value: offline, tone: styles.toneOffline },
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
          <span className={styles.eyebrow}>Frota monitorada</span>
          <span className={styles.heroValue}>{total}</span>
          <span className={styles.fleetHint}>
            {total === 1 ? "impressora ativa" : "impressoras ativas"}
          </span>
        </button>

        {/* Parte-do-todo, dita uma vez só. A identidade de cada faixa vem dos
            marcadores da lista ao lado — a barra nunca é o único rótulo. */}
        <div
          className={styles.distribution}
          role="img"
          aria-label={`Distribuição: ${online} online, ${attention} em atenção, ${offline} offline`}
        >
          {online > 0 && <span className={styles.segOnline} style={{ flexGrow: online }} />}
          {attention > 0 && <span className={styles.segAttention} style={{ flexGrow: attention }} />}
          {offline > 0 && <span className={styles.segOffline} style={{ flexGrow: offline }} />}
        </div>

        {stale > 0 && (
          <p className={styles.staleNote}>
            <Clock size={12} aria-hidden="true" />
            {stale} sem coleta recente
          </p>
        )}
      </div>

      <div className={styles.statusGroup}>
        {rows.map(({ status, label, value, tone }) => {
          const active = activeStatus === status;
          return (
            <button
              key={status}
              type="button"
              // Clicar de novo no filtro ativo volta para a frota inteira.
              onClick={() => onSelectStatus(active ? "Todos" : status)}
              aria-pressed={active}
              className={cn(styles.statusRow, tone, active && styles.statusRowActive)}
            >
              <span className={styles.statusDot} aria-hidden="true" />
              <span className={styles.statusLabel}>{label}</span>
              <span className={styles.statusValue}>{value}</span>
              <span className={styles.statusPct}>{percentOf(value, total)}%</span>
            </button>
          );
        })}
      </div>

      {topAlert ? (
        <div className={styles.alertPanel}>
          <div className={styles.alertHead}>
            <TriangleAlert size={14} className={styles.alertHeadIcon} aria-hidden="true" />
            <p className={styles.alertEyebrow}>Mais urgente agora</p>
            {alertsRest > 0 && <span className={styles.alertCount}>+{alertsRest}</span>}
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
            <CircleCheck size={14} className={styles.alertHeadIcon} aria-hidden="true" />
            <p className={styles.alertEyebrow}>Tudo em ordem</p>
          </div>
          <p className={styles.clearText}>Nenhum alerta ativo na frota agora.</p>
        </div>
      )}
    </section>
  );
}
