// Dependência externa: react (useState), lucide-react (ícones). Tela cheia
// de alertas (rota "alerts") — mesma fonte de dados que a VitalsStrip do
// Dashboard. Layout do handoff `PrinterControl v2.dc.html` L560-583: abas de
// severidade com contagem mono no cabeçalho e lista com trilho colorido por
// linha. O título da página fica no PageHeader da rota.
//
// "Marcar como lido" (22/09/2026): estado compartilhado pela equipe e só
// informativo — o alerta continua ativo até a condição sumir. Não confundir
// com a caixa pessoal (NotificationsView), que tem lido por usuário.
import { useMemo, useState } from "react";
import { TriangleAlert, CheckCircle2, Check, CheckCheck, Undo2 } from "lucide-react";
import { cn } from "../lib/cn";
import { parseApiDate } from "../lib/adaptApi";
import styles from "./AlertsView.module.css";
import type { Alert, Printer } from "../types";

interface AlertsViewProps {
  alerts: Alert[];
  printers: Printer[];
  onSelectPrinter: (printer: Printer) => void;
  /** Sem isto (ou em alerta de demonstração) as ações de leitura somem. */
  onSetRead?: (alerts: Alert[], read: boolean) => Promise<void>;
}

type SeverityFilter = "todos" | Alert["severity"];

function mesmoDia(a: Date, b: Date) {
  return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate();
}

/** "14:32" hoje, "21/09 14:32" em outro dia. Texto cru se não for data da API. */
function formatarHora(iso: string): string {
  const data = parseApiDate(iso);
  if (!data) return iso;
  const hora = data.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
  if (mesmoDia(data, new Date())) return hora;
  return `${data.toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit" })} ${hora}`;
}

/** "Lido por Ana às 14:32" / "Lido por Ana em 21/09 às 14:32". */
function textoLido(a: Alert): string {
  const data = parseApiDate(a.readAt);
  let momento = "";
  if (data) {
    const hora = data.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
    momento = mesmoDia(data, new Date())
      ? ` às ${hora}`
      : ` em ${data.toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit" })} às ${hora}`;
  }
  return a.readBy ? `Lido por ${a.readBy}${momento}` : `Lido${momento}`;
}

export default function AlertsView({ alerts, printers, onSelectPrinter, onSetRead }: AlertsViewProps) {
  const [severityFilter, setSeverityFilter] = useState<SeverityFilter>("todos");
  const [onlyUnread, setOnlyUnread] = useState(false);

  // Alertas derivados da demonstração não têm readAt (undefined): sem ação.
  const podeMarcar = (a: Alert) => onSetRead !== undefined && a.readAt !== undefined;
  const lido = (a: Alert) => Boolean(a.readAt);

  const counts = useMemo(() => {
    const c = { critical: 0, warning: 0, info: 0, unread: 0 };
    for (const a of alerts) {
      c[a.severity]++;
      if (!a.readAt) c.unread++;
    }
    return c;
  }, [alerts]);

  const visible = alerts.filter(
    (a) => (severityFilter === "todos" || a.severity === severityFilter) && (!onlyUnread || !lido(a)),
  );
  const visiveisNaoLidos = visible.filter((a) => podeMarcar(a) && !lido(a));
  const temAcaoDeLeitura = alerts.some(podeMarcar);

  const tabs: { value: SeverityFilter; label: string; count: number; tone: string; active: string }[] = [
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
              type="button"
              aria-pressed={severityFilter === t.value}
              onClick={() => setSeverityFilter(t.value)}
              className={cn(styles.tab, t.tone, severityFilter === t.value && t.active)}
            >
              {t.label} <span className={styles.tabCount}>{t.count}</span>
            </button>
          ))}
          {temAcaoDeLeitura && (
            <>
              <span className={styles.tabDivider} aria-hidden="true" />
              <button
                type="button"
                aria-pressed={onlyUnread}
                onClick={() => setOnlyUnread((v) => !v)}
                className={cn(styles.tab, styles.tabNeutral, onlyUnread && styles.tabNeutralActive)}
              >
                Não lidos <span className={styles.tabCount}>{counts.unread}</span>
              </button>
            </>
          )}
        </div>
        {temAcaoDeLeitura ? (
          <button
            type="button"
            className={styles.markAllBtn}
            disabled={visiveisNaoLidos.length === 0}
            onClick={() => onSetRead?.(visiveisNaoLidos, true)}
            title={
              visiveisNaoLidos.length === 0
                ? "Nenhum alerta não lido nesta lista"
                : `Marca os ${visiveisNaoLidos.length} alertas não lidos exibidos`
            }
          >
            <CheckCheck size={15} aria-hidden="true" />
            Marcar todos como lidos
          </button>
        ) : (
          <p className={styles.headerNote}>Derivados automaticamente das leituras da frota</p>
        )}
      </div>

      {alerts.length === 0 ? (
        <div className={styles.emptyState}>
          <CheckCircle2 size={32} className={styles.emptyIcon} />
          <p className={styles.emptyTitle}>Tudo certo por aqui</p>
          <p className={styles.emptyText}>Nenhuma impressora precisa de atenção no momento.</p>
        </div>
      ) : visible.length === 0 ? (
        <div className={styles.emptyState}>
          <p className={styles.emptyText}>
            {onlyUnread ? "Nenhum alerta não lido nessa categoria." : "Nenhum alerta nessa categoria."}
          </p>
        </div>
      ) : (
        <ul className={styles.list}>
          {visible.map((a) => {
            const printer = printers.find((p) => p.id === a.printerId);
            const critical = a.severity === "critical";
            const marcavel = podeMarcar(a);
            const naoLido = marcavel && !lido(a);
            return (
              <li
                key={a.id}
                className={cn(styles.listItem, critical ? styles.railCritical : styles.railWarning, naoLido && styles.unread)}
              >
                <button
                  type="button"
                  onClick={() => printer && onSelectPrinter(printer)}
                  disabled={!printer}
                  className={styles.alertBtn}
                >
                  <span className={cn(styles.alertIcon, critical ? styles.toneCritical : styles.toneWarning)}>
                    <TriangleAlert size={15} />
                  </span>
                  <span className={styles.alertBody}>
                    <span className={styles.alertMessage}>
                      {naoLido && <span className={styles.unreadDot} aria-hidden="true" />}
                      {naoLido && <span className={styles.srOnly}>Não lido: </span>}
                      {a.message}
                    </span>
                    <span className={styles.alertMeta}>
                      <span className={cn(styles.alertBadge, critical ? styles.toneCritical : styles.toneWarning)}>
                        {critical ? "Crítico" : "Atenção"}
                      </span>
                      <span className={styles.alertTimestamp}>{formatarHora(a.timestamp)}</span>
                      {marcavel && lido(a) && <span className={styles.readInfo}>{textoLido(a)}</span>}
                    </span>
                  </span>
                </button>
                {marcavel && (
                  <button
                    type="button"
                    className={styles.readBtn}
                    onClick={() => onSetRead?.([a], !lido(a))}
                    aria-label={lido(a) ? `Marcar como não lido: ${a.message}` : `Marcar como lido: ${a.message}`}
                    title={lido(a) ? "Marcar como não lido" : "Marcar como lido"}
                  >
                    {lido(a) ? <Undo2 size={15} aria-hidden="true" /> : <Check size={15} aria-hidden="true" />}
                    <span className={styles.readBtnLabel}>{lido(a) ? "Marcar como não lido" : "Marcar como lido"}</span>
                  </button>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
