"use client";

/**
 * Cartões de resumo do Dashboard: frota, online, atenção e offline.
 *
 * Estilo de 22/09/2026 (referência enviada pelo usuário): cartões de vidro
 * separados, cada um com borda e brilho suave na cor do status, ícone grande
 * num quadrado à esquerda e, à direita, rótulo, número e legenda; o
 * percentual da frota fica num selo no canto. A cor identifica o status de
 * relance sem pintar o número.
 *
 * Os cartões são botões: filtram a tabela "Frota de impressoras". Clicar de
 * novo no filtro ativo volta para a frota inteira.
 */

import { AlertTriangle, Printer, Wifi, WifiOff, type LucideIcon } from "lucide-react";
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
}

interface StatusCard {
  key: Exclude<StatusFilter, "Todos">;
  label: string;
  value: number;
  icon: LucideIcon;
  tone: string;
  vazio: string;
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
}: VitalsStripProps) {
  const cards: StatusCard[] = [
    { key: "online", label: "Online", value: online, icon: Wifi, tone: styles.toneOnline, vazio: "nenhuma respondendo" },
    { key: "atencao", label: "Atenção", value: attention, icon: AlertTriangle, tone: styles.toneAttention, vazio: "tudo em ordem" },
    { key: "offline", label: "Offline", value: offline, icon: WifiOff, tone: styles.toneOffline, vazio: "nenhuma fora do ar" },
  ];

  return (
    <section className={styles.cards} aria-label="Resumo da frota">
      <button
        type="button"
        onClick={() => onSelectStatus("Todos")}
        aria-pressed={activeStatus === "Todos"}
        title="Mostrar a frota inteira na tabela"
        className={cn(styles.card, styles.toneFleet, activeStatus === "Todos" && styles.cardActive)}
      >
        <span className={styles.icon} aria-hidden="true">
          <Printer size={22} />
        </span>
        <span className={styles.body}>
          <span className={styles.head}>
            <span className={styles.label}>Frota monitorada</span>
          </span>
          <span className={styles.value}>{total}</span>
          {stale > 0 ? (
            <span className={cn(styles.sub, styles.subWarn)}>{stale} sem coleta recente</span>
          ) : (
            <span className={styles.sub}>{total === 1 ? "impressora ativa" : "impressoras ativas"}</span>
          )}
        </span>
      </button>

      {cards.map(({ key, label, value, icon: Icon, tone, vazio }) => {
        const active = activeStatus === key;
        return (
          <button
            key={key}
            type="button"
            onClick={() => onSelectStatus(active ? "Todos" : key)}
            aria-pressed={active}
            title={active ? "Limpar filtro da tabela" : `Filtrar a tabela por ${label.toLowerCase()}`}
            className={cn(styles.card, tone, active && styles.cardActive)}
          >
            <span className={styles.icon} aria-hidden="true">
              <Icon size={22} />
            </span>
            <span className={styles.body}>
              <span className={styles.head}>
                <span className={styles.label}>{label}</span>
                <span className={styles.pct}>{percentOf(value, total)}%</span>
              </span>
              <span className={styles.value}>{value}</span>
              <span className={styles.sub}>
                {value === 0 ? vazio : `${value === 1 ? "impressora" : "impressoras"} de ${total}`}
              </span>
            </span>
          </button>
        );
      })}
    </section>
  );
}
