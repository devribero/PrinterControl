"use client";

/**
 * Rota "/reports" — Relatórios.
 *
 * Período (últimos 3/6/12 meses ou um mês) → indicadores → páginas por mês →
 * ranking de impressoras + quebra por departamento/unidade → inativas
 * (recolhido). Tudo respeita o escopo global do ServerSwitcher: `printers`
 * já chega filtrado de useAppData; o total mensal oficial (`monthlyUsage`)
 * só é usado sem escopo — ver components/reports/reportModel.ts.
 *
 * O CSV exporta exatamente o que está na tela: período e escopo atuais,
 * uma linha por equipamento, uma coluna por mês.
 *
 * "Levantamento mensal (Excel)" gera a planilha oficial do mês (a mesma da
 * empresa, com o mês novo preenchido) — ver components/reports/LevantamentoCard.
 */
import { useMemo, useState } from "react";
import { Download } from "lucide-react";
import PageHeader from "../../components/PageHeader";
import ServerSwitcher from "../../components/ServerSwitcher";
import PeriodToolbar from "../../components/reports/PeriodToolbar";
import ReportKpis from "../../components/reports/ReportKpis";
import MonthlyChart from "../../components/reports/MonthlyChart";
import PrinterRanking from "../../components/reports/PrinterRanking";
import UsageBreakdown from "../../components/reports/UsageBreakdown";
import DecommissionedList from "../../components/reports/DecommissionedList";
import LevantamentoCard from "../../components/reports/LevantamentoCard";
import {
  buildReport,
  computeKpis,
  rankRows,
  selectPeriods,
  selectionLabel,
  type PeriodSelection,
} from "../../components/reports/reportModel";
import { useAppData } from "../../lib/app-data";
import { useToast } from "../../lib/toast";
import { exportMonthlyReportCsv } from "../../lib/exportCsv";
import { rotularEscopo } from "../../lib/serverScope";
import styles from "./page.module.css";

export default function ReportsPage() {
  const {
    printers,
    monthlyUsage,
    usingRealData,
    usingRealMonthlyReport,
    decommissionedPrinters,
    setSelectedPrinter,
    serverScope,
    servers,
    units,
  } = useAppData();
  const { push } = useToast();
  const [selection, setSelection] = useState<PeriodSelection>({ kind: "last", count: 6 });

  // Mesma regra de app-data: o escopo só vale sobre a frota real (a de
  // demonstração não tem servidor de origem).
  const scope = usingRealData ? serverScope : null;
  const scoped = scope !== null;
  const scopeLabel = rotularEscopo(scope, servers, units);

  const report = useMemo(() => buildReport(printers, monthlyUsage, scoped), [printers, monthlyUsage, scoped]);
  const selected = useMemo(() => selectPeriods(report.months, selection), [report.months, selection]);
  const selectedSet = useMemo(() => new Set(selected.map((m) => m.period)), [selected]);
  const kpis = useMemo(() => computeKpis(report.months, selected), [report.months, selected]);
  const ranked = useMemo(() => rankRows(report.rows, selected.map((m) => m.period)), [report.rows, selected]);
  const periodLabel = selectionLabel(selected);
  const last = selected[selected.length - 1];

  function handleExport() {
    exportMonthlyReportCsv({
      scopeLabel,
      periodLabel,
      months: selected.map((m) => ({
        period: m.period,
        label: m.longLabel,
        inProgress: m.inProgress,
        pages: m.pages,
        estimated: m.estimated,
        devices: m.devices,
      })),
      rows: ranked.map((r) => ({
        name: r.printer.name,
        ip: r.printer.ip,
        model: r.printer.model,
        department: r.department,
        unit: r.unit,
        server: r.printer.server,
        active: r.printer.active,
        byPeriod: r.byPeriod,
        total: r.total,
      })),
    });
    push({
      variant: "success",
      title: "CSV exportado",
      description: `${ranked.length} equipamento(s), ${periodLabel}.`,
    });
  }

  return (
    <>
      <PageHeader
        section="Monitoramento"
        title="Relatórios"
        subtitle="Páginas impressas por mês, por equipamento, departamento e unidade."
        actions={
          <>
            <ServerSwitcher />
            <button type="button" onClick={handleExport} className={styles.exportButton} disabled={selected.length === 0}>
              <Download size={14} aria-hidden="true" />
              Exportar CSV
            </button>
          </>
        }
      />

      {report.months.length === 0 ? (
        <div className={styles.emptyState}>
          <p className={styles.emptyTitle}>Sem dados mensais · {scopeLabel}</p>
          <p className={styles.emptyText}>
            Os totais aparecem assim que houver leituras de contador para as impressoras deste escopo.
          </p>
        </div>
      ) : (
        <>
          <PeriodToolbar
            months={report.months}
            selection={selection}
            onChange={setSelection}
            scopeLabel={scopeLabel}
            periodLabel={periodLabel}
          />

          <ReportKpis kpis={kpis} monthCount={selected.length} lastLabel={last?.longLabel ?? "—"} scoped={scoped} />

          <MonthlyChart
            months={report.months}
            selected={selectedSet}
            ficticio={!usingRealMonthlyReport}
            scoped={scoped}
          />

          <div className={styles.mainGrid}>
            <PrinterRanking ranked={ranked} onOpenDetails={setSelectedPrinter} />
            <UsageBreakdown ranked={ranked} />
          </div>
        </>
      )}

      <LevantamentoCard />

      <DecommissionedList data={decommissionedPrinters} />
    </>
  );
}
