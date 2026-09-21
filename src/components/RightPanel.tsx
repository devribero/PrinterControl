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

/** Uma cor de toner: ponto de identidade, barra de severidade, valor. */
function TonerRow({ level, color }: { level: TonerLevel; color: string }) {
  const percent = Math.max(0, Math.min(100, level.percent));
  const state = percent <= 15 ? styles.tonerCritical : percent <= 35 ? styles.tonerLow : "";
  return (
    <div
      className={cn(styles.tonerRow, state)}
      role="img"
      aria-label={`${level.label}: ${level.percent}%`}
    >
      <span className={styles.tonerDot} style={{ backgroundColor: color }} aria-hidden="true" />
      <span className={styles.tonerLabel} aria-hidden="true">
        {level.label.split(" ")[0]}
      </span>
      <span className={styles.tonerTrack} aria-hidden="true">
        <span className={styles.tonerFill} style={{ width: `${percent}%` }} />
      </span>
      <span className={styles.tonerValue} aria-hidden="true">
        {percent <= 15 && <TriangleAlert size={13} className={styles.tonerWarnIcon} />}
        {level.percent}%
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
  // Do menor para o maior: a cor que vai acabar primeiro fica no topo, que e
  // a unica ordem util aqui. Copia antes de ordenar — `sort` altera o array
  // no lugar, e este vem do provider, que outras telas consomem na ordem
  // K/C/M/Y.
  const tonerOrdenado = [...toner].sort((a, b) => a.percent - b.percent);
  const lowest = tonerOrdenado[0] ?? null;
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
          <div className={styles.tonerList}>
            {tonerOrdenado.map((t) => (
              <TonerRow key={t.color} level={t} color={tonerChannelColor(t.color, theme)} />
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
