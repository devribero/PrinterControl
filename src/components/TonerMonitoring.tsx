"use client";

/**
 * Dependências externas: react (useMemo/useState), lucide-react (ícones).
 * Dependências locais: PrinterStatusBadge, lib/tonerColor (cor por canal e
 * por faixa de nível), lib/theme (canal K muda de tom no escuro).
 *
 * Área dedicada ao propósito central do sistema: acompanhar o nível de toner
 * de toda a frota num único lugar, com classificação (crítico/baixo/normal),
 * contagem por faixa e a possibilidade de forçar uma nova verificação — sem
 * precisar abrir impressora por impressora. As faixas usam os mesmos limiares
 * de lib/tonerColor.tonerLevelColor (≤15% crítico, ≤35% baixo) pra bater com
 * a cor mostrada em qualquer outro lugar do app.
 *
 * Layout do handoff (`PrinterControl v2.dc.html` L482-553): faixa inline de
 * severidade ("Precisam de intervenção agora") + tabela de suprimentos com
 * barras por canal. O título da página e o controle de verificação ficam no
 * PageHeader da rota, não aqui.
 */
import { useMemo, useState } from "react";
import { CircleCheck, Droplet, Search, TriangleAlert, WifiOff } from "lucide-react";
import type { Printer, TonerLevel } from "../types";
import PrinterStatusBadge from "./PrinterStatusBadge";
import { tonerChannelColor, tonerLevelColor } from "../lib/tonerColor";
import { useTheme } from "../lib/theme";
import { cn } from "../lib/cn";
import styles from "./TonerMonitoring.module.css";

type TonerClass = "critical" | "warning" | "normal" | "none";

function classify(toner: TonerLevel[] | null): TonerClass {
  if (!toner || toner.length === 0) return "none";
  const worst = Math.min(...toner.map((t) => t.percent));
  if (worst <= 15) return "critical";
  if (worst <= 35) return "warning";
  return "normal";
}

interface TonerMonitoringProps {
  printers: Printer[];
  onOpenDetails: (printer: Printer) => void;
}

export default function TonerMonitoring({ printers, onOpenDetails }: TonerMonitoringProps) {
  const { theme } = useTheme();
  const [filter, setFilter] = useState<"todos" | TonerClass>("todos");
  const [query, setQuery] = useState("");

  const classified = useMemo(() => printers.map((p) => ({ printer: p, cls: classify(p.toner) })), [printers]);

  const counts = useMemo(() => {
    const c = { critical: 0, warning: 0, normal: 0, none: 0 };
    for (const { cls } of classified) c[cls]++;
    return c;
  }, [classified]);

  const offlineCount = useMemo(() => printers.filter((p) => p.status === "offline").length, [printers]);

  const rows = useMemo(() => {
    const q = query.trim().toLowerCase();
    return classified
      .filter(({ cls }) => filter === "todos" || cls === filter)
      .filter(({ printer }) => !q || printer.name.toLowerCase().includes(q) || printer.ip.toLowerCase().includes(q))
      .sort((a, b) => {
        const order: Record<TonerClass, number> = { critical: 0, warning: 1, none: 2, normal: 3 };
        if (order[a.cls] !== order[b.cls]) return order[a.cls] - order[b.cls];
        const aWorst = a.printer.toner ? Math.min(...a.printer.toner.map((t) => t.percent)) : 999;
        const bWorst = b.printer.toner ? Math.min(...b.printer.toner.map((t) => t.percent)) : 999;
        return aWorst - bWorst;
      });
  }, [classified, filter, query]);

  /** Faixa de severidade: os três primeiros itens alternam o filtro; "Sem
   * comunicação" conta impressoras offline, que não são uma faixa de toner e
   * portanto não filtram a tabela (mesmo comportamento da versão anterior). */
  const severity: { key: TonerClass | "offline"; label: string; value: number; icon: React.ReactNode; tone: string }[] = [
    { key: "critical", label: "Crítico ≤15%", value: counts.critical, icon: <TriangleAlert size={14} />, tone: styles.toneCritical },
    { key: "warning", label: "Baixo ≤35%", value: counts.warning, icon: <Droplet size={14} />, tone: styles.toneWarning },
    { key: "normal", label: "Normal >35%", value: counts.normal, icon: <CircleCheck size={14} />, tone: styles.toneSuccess },
    { key: "offline", label: "Sem comunicação", value: offlineCount, icon: <WifiOff size={14} />, tone: styles.toneFaint },
  ];

  const pills: { value: "todos" | TonerClass; label: string }[] = [
    { value: "todos", label: "Todos" },
    { value: "critical", label: `Crítico · ${counts.critical}` },
    { value: "warning", label: `Baixo · ${counts.warning}` },
    { value: "normal", label: `Normal · ${counts.normal}` },
    { value: "none", label: `Sem dados · ${counts.none}` },
  ];

  return (
    <div className={styles.page}>
      <div className={styles.severityStrip}>
        <p className={styles.severityLead}>Precisam de intervenção agora:</p>
        {severity.map((s) => (
          <button
            key={s.key}
            onClick={() => s.key !== "offline" && setFilter(filter === s.key ? "todos" : (s.key as TonerClass))}
            disabled={s.key === "offline"}
            className={cn(
              styles.severityItem,
              s.key === "critical" && styles.severityItemCritical,
              filter === s.key && styles.severityItemActive
            )}
          >
            <span className={cn(styles.severityIcon, s.tone)}>{s.icon}</span>
            <span className={styles.severityValue}>{s.value}</span>
            <span className={styles.severityLabel}>{s.label}</span>
          </button>
        ))}
      </div>

      <div className={styles.tableCard}>
        <div className={styles.filterBar}>
          <div className={styles.filterPills}>
            {pills.map((p) => (
              <button
                key={p.value}
                onClick={() => setFilter(p.value)}
                className={cn(styles.filterPill, filter === p.value && styles.filterPillActive)}
              >
                {p.label}
              </button>
            ))}
          </div>
          <div className={styles.searchBox}>
            <Search size={14} />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Nome ou IP"
              className={styles.searchInput}
            />
          </div>
        </div>

        <div className={styles.tableScroll}>
          <table className={styles.table}>
            <thead>
              <tr className={styles.theadRow}>
                <th className={styles.thFirst}>Impressora</th>
                <th className={styles.th}>Endereço</th>
                <th className={styles.th}>Status</th>
                <th className={styles.th}>Níveis por canal</th>
                <th className={cn(styles.thLast, styles.thRight)}>Atividade</th>
              </tr>
            </thead>
            <tbody>
              {rows.map(({ printer: p, cls }) => (
                <tr
                  key={p.id}
                  onClick={() => onOpenDetails(p)}
                  className={cn(styles.row, cls === "critical" && styles.rowCritical)}
                >
                  <td className={styles.tdFirst}>
                    <p className={styles.printerName}>{p.name}</p>
                    <p className={styles.printerDept}>{p.department}</p>
                  </td>
                  <td className={cn(styles.td, styles.tdIp)}>{p.ip}</td>
                  <td className={styles.td}>
                    <PrinterStatusBadge status={p.status} />
                  </td>
                  <td className={styles.td}>
                    {p.toner && p.toner.length > 0 ? (
                      <div className={styles.channelList}>
                        {p.toner.map((t) => (
                          <div key={t.color} className={styles.channelItem} title={`${t.label}: ${t.percent}%`}>
                            <span className={styles.channelDot} style={{ backgroundColor: tonerChannelColor(t.color, theme) }} />
                            <div className={styles.channelTrack}>
                              <div
                                className={styles.channelFill}
                                style={{ width: `${t.percent}%`, backgroundColor: tonerChannelColor(t.color, theme) }}
                              />
                            </div>
                            <span className={styles.channelPercent} style={{ color: tonerLevelColor(t.percent) }}>
                              {t.percent}%
                            </span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <span className={styles.noToner}>Sem leitura de toner</span>
                    )}
                  </td>
                  <td className={cn(styles.tdLast, styles.tdRight)}>{p.lastSeen}</td>
                </tr>
              ))}
              {rows.length === 0 && (
                <tr>
                  <td colSpan={5} className={styles.emptyCell}>
                    Nenhuma impressora encontrada com esses filtros.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <div className={styles.footer}>
          Exibindo <span className={styles.footerNum}>{rows.length}</span> de{" "}
          <span className={styles.footerNum}>{printers.length}</span> impressoras · ordenadas por criticidade
        </div>
      </div>
    </div>
  );
}
