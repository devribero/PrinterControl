/**
 * Dependência externa: lucide-react (ícones). Os níveis chegam prontos de
 * lib/deriveFromPrinters.ts: o MENOR nível de cada cor na frota ativa — por
 * isso o subtítulo do card diz isso com todas as letras.
 *
 * Sem leitura nenhuma, o card agora diz que não há leitura. Antes o prop
 * caía no conjunto de demonstração de data/printers.ts e o Dashboard exibia
 * níveis inventados como se fossem da frota real.
 */
"use client";

import { ChevronRight, TriangleAlert, FileBarChart2, History, PlusCircle, Settings, Bell, Droplet } from "lucide-react";
import { tonerChannelColor } from "../lib/tonerColor";
import { useToast } from "../lib/toast";
import { useTheme } from "../lib/theme";
import { cn } from "../lib/cn";
import type { Printer, TonerLevel } from "../types";
import styles from "./RightPanel.module.css";

function QuickAction({
  icon,
  label,
  badge,
  onClick,
}: {
  icon: React.ReactNode;
  label: string;
  badge?: number;
  onClick: () => void;
}) {
  return (
    <button type="button" onClick={onClick} className={styles.quickAction}>
      <span className={styles.quickActionIcon} aria-hidden="true">
        {icon}
      </span>
      <span className={styles.quickActionLabel}>{label}</span>
      {badge ? (
        <span className={styles.quickActionBadge}>{badge}</span>
      ) : (
        <ChevronRight size={15} className={styles.quickActionChevron} aria-hidden="true" />
      )}
    </button>
  );
}

const GAUGE_RADIUS = 24;
const GAUGE_CIRCUMFERENCE = 2 * Math.PI * GAUGE_RADIUS;

function TonerGauge({ level, color }: { level: TonerLevel; color: string }) {
  const percent = Math.max(0, Math.min(100, level.percent));
  const state = percent <= 15 ? styles.gaugeCritical : percent <= 35 ? styles.gaugeLow : "";
  return (
    <div className={cn(styles.gauge, state)} role="img" aria-label={`${level.label}: ${level.percent}%`}>
      <div className={styles.gaugeRingWrap}>
        <svg viewBox="0 0 60 60" className={styles.gaugeRing} aria-hidden="true">
          <circle cx="30" cy="30" r={GAUGE_RADIUS} className={styles.gaugeTrack} />
          <circle
            cx="30"
            cy="30"
            r={GAUGE_RADIUS}
            className={styles.gaugeValue}
            style={{ stroke: color }}
            strokeDasharray={`${(percent / 100) * GAUGE_CIRCUMFERENCE} ${GAUGE_CIRCUMFERENCE}`}
            transform="rotate(-90 30 30)"
          />
        </svg>
        <span className={styles.gaugePercent} aria-hidden="true">
          {level.percent}%
        </span>
      </div>
      <span className={styles.gaugeLabel} aria-hidden="true">
        <span className={styles.gaugeDot} style={{ backgroundColor: color }} />
        {level.label.split(" ")[0]}
      </span>
    </div>
  );
}

interface RightPanelProps {
  alertCount: number;
  globalToner?: TonerLevel[];
  worstPrinter: Printer | null;
  onOpenDetails: (printer: Printer) => void;
  onNavigate: (id: string) => void;
}

export default function RightPanel({ alertCount, globalToner, worstPrinter, onOpenDetails, onNavigate }: RightPanelProps) {
  const { push } = useToast();
  const { theme } = useTheme();
  const toner = globalToner ?? [];

  // O menor nível entre todas as cores — é esse o percentual da impressora
  // `worstPrinter`, então nome e número do card sempre batem. Antes pegava o
  // PRIMEIRO canal abaixo de 20% na ordem K/C/M/Y, que podia ser de outra
  // impressora que não a exibida pelo botão.
  const lowest = toner.length > 0 ? toner.reduce((min, t) => (t.percent < min.percent ? t : min)) : null;
  const critical = lowest && lowest.percent <= 20 ? lowest : null;

  return (
    <div className={styles.root}>
      <section className={styles.tonerCard}>
        <div className={styles.cardHead}>
          <div>
            <h3 className={styles.cardTitle}>Níveis de toner</h3>
            <p className={styles.cardSubtitle}>Menor nível de cada cor na frota</p>
          </div>
          <span className={styles.cardHeadIcon} aria-hidden="true">
            <Droplet size={15} />
          </span>
        </div>

        {toner.length > 0 ? (
          <div className={styles.gaugeGrid}>
            {toner.map((t) => (
              <TonerGauge key={t.color} level={t} color={tonerChannelColor(t.color, theme)} />
            ))}
          </div>
        ) : (
          <p className={styles.emptyText}>Nenhuma impressora ativa informou nível de toner ainda.</p>
        )}

        <button type="button" onClick={() => onNavigate("printers")} className={styles.detailsLink}>
          Ver detalhes
          <ChevronRight size={15} aria-hidden="true" />
        </button>
      </section>

      {critical && (
        <section className={styles.criticalCard}>
          <div className={styles.criticalHeader}>
            <span className={styles.criticalIconWrap} aria-hidden="true">
              <TriangleAlert size={18} />
            </span>
            <div className={styles.criticalHeadText}>
              <p className={styles.criticalLabel}>Toner baixo</p>
              <p className={styles.criticalValue}>
                {critical.percent}%<span className={styles.criticalValueUnit}> restante</span>
              </p>
            </div>
          </div>
          <p className={styles.criticalDesc}>
            {worstPrinter ? (
              <>
                <span className={styles.criticalPrinter}>{worstPrinter.name}</span> · {critical.label}. Considere
                substituir em breve.
              </>
            ) : (
              "Considere substituir em breve."
            )}
          </p>
          <button
            type="button"
            onClick={() => {
              if (worstPrinter) onOpenDetails(worstPrinter);
              else push({ variant: "info", title: "Sem impressora associada a este alerta ainda." });
            }}
            className={styles.criticalButton}
          >
            {worstPrinter ? "Ver impressora" : "Ver recomendações"}
          </button>
        </section>
      )}

      <section className={styles.quickActionsCard}>
        <h3 className={styles.quickActionsTitle}>Ações rápidas</h3>
        <div className={styles.quickActionsList}>
          <QuickAction icon={<FileBarChart2 size={16} />} label="Relatório de Impressoras" onClick={() => onNavigate("reports")} />
          <QuickAction icon={<History size={16} />} label="Histórico de Alertas" badge={alertCount} onClick={() => onNavigate("alerts")} />
          <QuickAction
            icon={<PlusCircle size={16} />}
            label="Adicionar Impressora"
            onClick={() => push({ variant: "info", title: "Em breve", description: "Cadastro manual de impressoras chega numa próxima versão." })}
          />
          <QuickAction icon={<Settings size={16} />} label="Configurações" onClick={() => onNavigate("settings")} />
          <QuickAction icon={<Bell size={16} />} label="Notificações" onClick={() => onNavigate("notifications")} />
        </div>
      </section>
    </div>
  );
}
