// Dependência externa: react (useState), lucide-react (ícones). Tela cheia
// de alertas (rota "alerts") — mesma fonte de dados que a VitalsStrip do
// Dashboard. Layout do handoff `PrinterControl v2.dc.html` L560-583: abas de
// severidade com contagem mono no cabeçalho e lista com trilho colorido por
// linha. O título da página fica no PageHeader da rota.
import { useMemo, useState } from "react";
import { TriangleAlert, CheckCircle2 } from "lucide-react";
import { cn } from "../lib/cn";
import styles from "./AlertsView.module.css";
import type { Alert, Printer } from "../types";

interface AlertsViewProps {
  alerts: Alert[];
  printers: Printer[];
  onSelectPrinter: (printer: Printer) => void;
}

export default function AlertsView({ alerts, printers, onSelectPrinter }: AlertsViewProps) {
  const [severityFilter, setSeverityFilter] = useState<"todos" | Alert["severity"]>("todos");

  const counts = useMemo(() => {
    const c = { critical: 0, warning: 0, info: 0 };
    for (const a of alerts) c[a.severity]++;
    return c;
  }, [alerts]);

  const visible = severityFilter === "todos" ? alerts : alerts.filter((a) => a.severity === severityFilter);

  const tabs: { value: "todos" | Alert["severity"]; label: string; count: number; tone: string; active: string }[] = [
    { value: "todos", label: "Todos", count: alerts.length, tone: styles.tabNeutral, active: styles.tabNeutralActive },
    { value: "critical", label: "Crítico", count: counts.critical, tone: styles.tabCritical, active: styles.tabCriticalActive },
    { value: "warning", label: "Atenção", count: counts.warning, tone: styles.tabWarning, active: styles.tabWarningActive },
  ];

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <div className={styles.tabs}>
          {tabs.map((t) => (
            <button
              key={t.value}
              onClick={() => setSeverityFilter(t.value)}
              className={cn(styles.tab, t.tone, severityFilter === t.value && t.active)}
            >
              {t.label} <span className={styles.tabCount}>{t.count}</span>
            </button>
          ))}
        </div>
        <p className={styles.headerNote}>Derivados automaticamente das leituras da frota</p>
      </div>

      {alerts.length === 0 ? (
        <div className={styles.emptyState}>
          <CheckCircle2 size={32} className={styles.emptyIcon} />
          <p className={styles.emptyTitle}>Tudo certo por aqui</p>
          <p className={styles.emptyText}>Nenhuma impressora precisa de atenção no momento.</p>
        </div>
      ) : visible.length === 0 ? (
        <div className={styles.emptyState}>
          <p className={styles.emptyText}>Nenhum alerta nessa categoria.</p>
        </div>
      ) : (
        <ul className={styles.list}>
          {visible.map((a) => {
            const printer = printers.find((p) => p.id === a.printerId);
            const critical = a.severity === "critical";
            return (
              <li key={a.id} className={cn(styles.listItem, critical ? styles.railCritical : styles.railWarning)}>
                <button onClick={() => printer && onSelectPrinter(printer)} disabled={!printer} className={styles.alertBtn}>
                  <span className={cn(styles.alertIcon, critical ? styles.toneCritical : styles.toneWarning)}>
                    <TriangleAlert size={15} />
                  </span>
                  <span className={styles.alertBody}>
                    <span className={styles.alertMessage}>{a.message}</span>
                  </span>
                  <span className={styles.alertTimestamp}>{a.timestamp}</span>
                  <span className={cn(styles.alertBadge, critical ? styles.toneCritical : styles.toneWarning)}>
                    {critical ? "Crítico" : "Atenção"}
                  </span>
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
