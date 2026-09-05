"use client";

/**
 * Sem libs externas. Recria a estrutura original da planilha (uma tabela
 * IP/Modelo/Departamento + coluna por mês, agrupada por unidade) dentro do
 * painel — é a visão "Histórico" completa, impressora a impressora, mês a
 * mês. Dependência local: lib/site.ts (separa "Depto — Unidade").
 *
 * Layout do handoff (`PrinterControl v2.dc.html` L668-762): linha de resumo
 * com total mono e os controles de expandir/recolher, tabela de totais por
 * mês e um card sanfona por unidade. O título da página fica no PageHeader
 * da rota.
 */
import { useState } from "react";
import { ChevronDown, ChevronRight, Maximize2, Minimize2 } from "lucide-react";
import type { Printer } from "../types";
import { getPrinterSite, getDepartmentLabel } from "../lib/site";
import styles from "./HistoryMatrix.module.css";

interface HistoryMatrixProps {
  printers: Printer[];
}

export default function HistoryMatrix({ printers }: HistoryMatrixProps) {
  const withHistory = printers.filter((p) => p.monthlyPages && p.monthlyPages.length > 0);
  const months = withHistory[0]?.monthlyPages?.map((m) => m.month) ?? [];

  const bySite = new Map<string, Printer[]>();
  for (const p of withHistory) {
    const site = getPrinterSite(p);
    if (!bySite.has(site)) bySite.set(site, []);
    bySite.get(site)!.push(p);
  }
  const sites = Array.from(bySite.keys()).sort();

  const [openSites, setOpenSites] = useState<Set<string>>(new Set(sites.slice(0, 1)));

  function toggleSite(site: string) {
    setOpenSites((prev) => {
      const next = new Set(prev);
      if (next.has(site)) next.delete(site);
      else next.add(site);
      return next;
    });
  }

  const grandTotals = months.map((_, i) => withHistory.reduce((sum, p) => sum + (p.monthlyPages?.[i]?.pages ?? 0), 0));
  const grandTotal = grandTotals.reduce((a, b) => a + b, 0);

  if (months.length === 0) {
    return (
      <div className={styles.emptyCard}>
        <p className={styles.emptyText}>Ainda sem contadores mensais para exibir.</p>
      </div>
    );
  }

  return (
    <div className={styles.root}>
      <div className={styles.summaryRow}>
        <div className={styles.summaryLeft}>
          <h2 className={styles.summaryTitle}>Histórico de impressão</h2>
          <span className={styles.summaryMeta}>
            {grandTotal.toLocaleString("pt-BR")} páginas · {months.length} meses · {sites.length} unidades
          </span>
        </div>
        <div className={styles.actionsRow}>
          <button onClick={() => setOpenSites(new Set(sites))} className={styles.actionButton}>
            <Maximize2 size={13} />
            Expandir tudo
          </button>
          <button onClick={() => setOpenSites(new Set())} className={styles.actionButton}>
            <Minimize2 size={13} />
            Recolher
          </button>
        </div>
      </div>

      <div className={styles.card}>
        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <thead>
              <tr className={styles.theadRow}>
                <th className={styles.thFirst}>Período</th>
                {months.map((m) => (
                  <th key={m} className={styles.thMonth}>
                    {m}
                  </th>
                ))}
                <th className={styles.thTotal}>Total</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className={styles.tdLabel}>Páginas impressas</td>
                {grandTotals.map((t, i) => (
                  <td key={i} className={styles.tdMonth}>
                    {t.toLocaleString("pt-BR")}
                  </td>
                ))}
                <td className={styles.tdGrandTotal}>{grandTotal.toLocaleString("pt-BR")}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {sites.map((site) => {
        const sitePrinters = bySite.get(site)!;
        const isOpen = openSites.has(site);
        const siteMonthTotals = months.map((_, i) => sitePrinters.reduce((sum, p) => sum + (p.monthlyPages?.[i]?.pages ?? 0), 0));
        const siteTotal = siteMonthTotals.reduce((a, b) => a + b, 0);

        return (
          <div key={site} className={styles.card}>
            <button onClick={() => toggleSite(site)} className={styles.siteToggle}>
              <span className={styles.siteToggleLeft}>
                <span className={styles.chevron}>{isOpen ? <ChevronDown size={15} /> : <ChevronRight size={15} />}</span>
                <span className={styles.siteTitle}>{site}</span>
                <span className={styles.siteCount}>
                  {sitePrinters.length} impressora{sitePrinters.length !== 1 ? "s" : ""}
                </span>
              </span>
              <span className={styles.siteTotal}>{siteTotal.toLocaleString("pt-BR")} páginas</span>
            </button>

            {isOpen && (
              <div className={styles.siteTableWrap}>
                <table className={styles.siteTable}>
                  <thead>
                    <tr className={styles.theadRow}>
                      <th className={styles.thFirst}>Impressora</th>
                      <th className={styles.th}>Endereço</th>
                      <th className={styles.th}>Departamento</th>
                      {months.map((m) => (
                        <th key={m} className={styles.thMonth}>
                          {m}
                        </th>
                      ))}
                      <th className={styles.thTotalPlain}>Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sitePrinters.map((p) => {
                      const total = p.monthlyPages!.reduce((sum, m) => sum + m.pages, 0);
                      return (
                        <tr key={p.id} className={styles.bodyRow}>
                          <td className={styles.nameCell}>{p.name}</td>
                          <td className={styles.ipCell}>{p.ip}</td>
                          <td className={styles.deptCell} title={getDepartmentLabel(p)}>
                            {getDepartmentLabel(p)}
                          </td>
                          {p.monthlyPages!.map((m) => (
                            <td key={m.month} className={styles.monthCell}>
                              {m.pages.toLocaleString("pt-BR")}
                            </td>
                          ))}
                          <td className={styles.rowTotalCell}>{total.toLocaleString("pt-BR")}</td>
                        </tr>
                      );
                    })}
                    <tr className={styles.subtotalRow}>
                      <td className={styles.subtotalLabelCell} colSpan={3}>
                        Subtotal
                      </td>
                      {siteMonthTotals.map((t, i) => (
                        <td key={i} className={styles.subtotalMonthCell}>
                          {t.toLocaleString("pt-BR")}
                        </td>
                      ))}
                      <td className={styles.subtotalTotalCell}>{siteTotal.toLocaleString("pt-BR")}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
