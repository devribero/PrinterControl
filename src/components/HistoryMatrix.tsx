"use client";

/**
 * Histórico: páginas impressas por mês das impressoras com contador de
 * páginas do escopo, agrupadas por unidade.
 *
 * Refeito em 22/09/2026. A versão anterior:
 *   - só listava impressora com histórico próprio — sumiam as sem contador e
 *     as outras filas do mesmo equipamento (o relatório conta cada IP uma
 *     vez, pela fila representante);
 *   - alinhava os meses pela POSIÇÃO no array: impressora com menos meses
 *     jogava o número na coluna errada e somava errado nos totais;
 *   - usava `printers` (com os filtros do Dashboard) em vez da frota do escopo.
 *
 * Agora: uma linha por EQUIPAMENTO (IP), com as outras filas dele citadas
 * embaixo do nome — somar filas contaria o mesmo contador duas vezes. Os
 * meses são casados pelo período ("2026-08"). Só entram equipamentos COM
 * contador de páginas (histórico mensal ou contador lido por SNMP):
 * etiquetadora, portátil e impressora que nunca informou contador ficam de
 * fora — não têm o que mostrar aqui. Unidade = a do print server (cadastro
 * de Unidades); sem ela, a unidade da planilha ("Departamento — Unidade").
 */
import { useMemo, useState } from "react";
import { ChevronDown, ChevronRight, Maximize2, Minimize2, Search } from "lucide-react";
import type { MonthlyPageCount, Printer, PrintServer } from "../types";
import { getDepartmentLabel, getPrinterSite } from "../lib/site";
import { cn } from "../lib/cn";
import styles from "./HistoryMatrix.module.css";

interface HistoryMatrixProps {
  printers: Printer[];
  servers: PrintServer[];
  onSelectPrinter: (printer: Printer) => void;
}

type Janela = 6 | 12 | 0; // 0 = todos os meses

interface Linha {
  chave: string;
  impressora: Printer;
  outrasFilas: string[];
  porPeriodo: Map<string, number>;
  total: number;
  motivo: string | null;
}

interface Grupo {
  unidade: string;
  daPlanilha: boolean;
  linhas: Linha[];
}

const IPV4 = /^(\d{1,3}\.){3}\d{1,3}$/;
const SEM_UNIDADE = "Sem unidade";

function historicoDe(p: Printer): MonthlyPageCount[] {
  if (p.monthlyPages?.length) return p.monthlyPages;
  return p.deviceMonthlyPages ?? [];
}

function rotuloDoPeriodo(periodo: string, historico: MonthlyPageCount[]): string {
  return historico.find((m) => m.period === periodo)?.month ?? periodo;
}

function formatar(n: number): string {
  return n.toLocaleString("pt-BR");
}

export default function HistoryMatrix({ printers, servers, onSelectPrinter }: HistoryMatrixProps) {
  const [janela, setJanela] = useState<Janela>(12);
  const [busca, setBusca] = useState("");
  const [fechadas, setFechadas] = useState<Set<string>>(new Set());

  const unidadeDoServidor = useMemo(() => {
    const mapa = new Map<string, string>();
    for (const s of servers) if (s.unitName) mapa.set(s.host.toLowerCase(), s.unitName);
    return mapa;
  }, [servers]);

  // Uma linha por equipamento (IP). Filas sem IP ficam cada uma na sua linha.
  const { linhas, periodos, rotulos } = useMemo(() => {
    const porEquipamento = new Map<string, Printer[]>();
    for (const p of printers) {
      const chave = IPV4.test(p.ip) ? p.ip : `fila:${p.id}`;
      const lista = porEquipamento.get(chave);
      if (lista) lista.push(p);
      else porEquipamento.set(chave, [p]);
    }

    const todosPeriodos = new Set<string>();
    const rotulosPorPeriodo = new Map<string, string>();
    const resultado: Linha[] = [];
    for (const [chave, filas] of porEquipamento) {
      // Representante: a fila com histórico próprio; senão a de histórico herdado; senão a primeira.
      const rep = filas.find((f) => f.monthlyPages?.length) ?? filas.find((f) => f.deviceMonthlyPages?.length) ?? filas[0];
      const historico = historicoDe(rep);
      // Sem histórico e sem contador lido: não é impressora com contador de páginas.
      if (!historico.length && !filas.some((f) => f.pagesPrinted > 0)) continue;
      const porPeriodo = new Map<string, number>();
      for (const m of historico) {
        porPeriodo.set(m.period, m.pages);
        todosPeriodos.add(m.period);
        if (!rotulosPorPeriodo.has(m.period)) rotulosPorPeriodo.set(m.period, rotuloDoPeriodo(m.period, historico));
      }
      resultado.push({
        chave,
        impressora: rep,
        outrasFilas: filas.filter((f) => f !== rep).map((f) => f.name),
        porPeriodo,
        total: 0,
        // Contador lido, mas nenhum mês calculado ainda (coleta começou agora).
        motivo: historico.length ? null : "contador lido, sem mês fechado ainda",
      });
    }
    return { linhas: resultado, periodos: [...todosPeriodos].sort(), rotulos: rotulosPorPeriodo };
  }, [printers]);

  const meses = janela === 0 ? periodos : periodos.slice(-janela);

  const grupos = useMemo(() => {
    const termo = busca.trim().toLowerCase();
    const mapa = new Map<string, Grupo>();
    for (const linha of linhas) {
      const p = linha.impressora;
      if (
        termo &&
        ![p.name, p.ip, p.model, p.department, ...linha.outrasFilas].some((c) => c?.toLowerCase().includes(termo))
      ) {
        continue;
      }
      const doServidor = p.server ? unidadeDoServidor.get(p.server.toLowerCase()) : undefined;
      const daPlanilha = !doServidor && p.department.includes(" — ");
      const unidade = doServidor ?? (daPlanilha ? getPrinterSite(p) : SEM_UNIDADE);
      const total = meses.reduce((soma, periodo) => soma + (linha.porPeriodo.get(periodo) ?? 0), 0);
      const grupo = mapa.get(unidade) ?? { unidade, daPlanilha, linhas: [] };
      grupo.linhas.push({ ...linha, total });
      mapa.set(unidade, grupo);
    }
    for (const g of mapa.values()) {
      // Quem mais imprimiu primeiro; empate (ou sem mês ainda) por nome.
      g.linhas.sort((a, b) => b.total - a.total || a.impressora.name.localeCompare(b.impressora.name, "pt-BR"));
    }
    return [...mapa.values()].sort((a, b) =>
      a.unidade === SEM_UNIDADE ? 1 : b.unidade === SEM_UNIDADE ? -1 : a.unidade.localeCompare(b.unidade, "pt-BR"),
    );
  }, [linhas, meses, busca, unidadeDoServidor]);

  const somaPorMes = (lista: Linha[]) => meses.map((periodo) => lista.reduce((s, l) => s + (l.porPeriodo.get(periodo) ?? 0), 0));
  const todasAsLinhas = grupos.flatMap((g) => g.linhas);
  const totaisGerais = somaPorMes(todasAsLinhas);
  const totalGeral = totaisGerais.reduce((a, b) => a + b, 0);

  function alternar(unidade: string) {
    setFechadas((prev) => {
      const next = new Set(prev);
      if (next.has(unidade)) next.delete(unidade);
      else next.add(unidade);
      return next;
    });
  }

  if (linhas.length === 0) {
    return (
      <div className={styles.emptyCard}>
        <p className={styles.emptyText}>Nenhuma impressora com contador de páginas neste escopo.</p>
      </div>
    );
  }

  return (
    <div className={styles.root}>
      {/* ── Controles ─────────────────────────────────────────────── */}
      <div className={styles.toolbar}>
        <label className={styles.search}>
          <Search size={15} aria-hidden="true" />
          <input
            type="search"
            value={busca}
            onChange={(e) => setBusca(e.target.value)}
            placeholder="Buscar impressora, IP, modelo ou departamento"
            aria-label="Buscar no histórico"
          />
        </label>
        <div className={styles.segmented} role="group" aria-label="Período">
          {([6, 12, 0] as Janela[]).map((j) => (
            <button
              key={j}
              type="button"
              onClick={() => setJanela(j)}
              aria-pressed={janela === j}
              className={cn(styles.segment, janela === j && styles.segmentActive)}
            >
              {j === 0 ? "Tudo" : `${j} meses`}
            </button>
          ))}
        </div>
        <div className={styles.actionsRow}>
          <button type="button" onClick={() => setFechadas(new Set())} className={styles.actionButton}>
            <Maximize2 size={13} /> Expandir
          </button>
          <button type="button" onClick={() => setFechadas(new Set(grupos.map((g) => g.unidade)))} className={styles.actionButton}>
            <Minimize2 size={13} /> Recolher
          </button>
        </div>
      </div>

      <p className={styles.summaryMeta}>
        {grupos.length} {grupos.length === 1 ? "unidade" : "unidades"} · {todasAsLinhas.length} equipamentos ·{" "}
        {formatar(totalGeral)} páginas no período
      </p>

      {meses.length > 0 && (
        <div className={styles.card}>
          <div className={styles.tableWrap}>
            <table className={styles.table}>
              <thead>
                <tr className={styles.theadRow}>
                  <th className={styles.thFirst}>Todas as unidades</th>
                  {meses.map((m) => (
                    <th key={m} className={styles.thMonth}>
                      {rotulos.get(m) ?? m}
                    </th>
                  ))}
                  <th className={styles.thTotal}>Total</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className={styles.tdLabel}>Páginas impressas</td>
                  {totaisGerais.map((t, i) => (
                    <td key={meses[i]} className={styles.tdMonth}>
                      {formatar(t)}
                    </td>
                  ))}
                  <td className={styles.tdGrandTotal}>{formatar(totalGeral)}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}

      {grupos.length === 0 && (
        <div className={styles.emptyCard}>
          <p className={styles.emptyText}>Nenhuma impressora encontrada com esses filtros.</p>
        </div>
      )}

      {grupos.map((grupo) => {
        const aberta = !fechadas.has(grupo.unidade);
        const totaisDaUnidade = somaPorMes(grupo.linhas);
        const totalDaUnidade = totaisDaUnidade.reduce((a, b) => a + b, 0);

        return (
          <section key={grupo.unidade} className={styles.card}>
            <button type="button" onClick={() => alternar(grupo.unidade)} className={styles.siteToggle} aria-expanded={aberta}>
              <span className={styles.siteToggleLeft}>
                <span className={styles.chevron}>{aberta ? <ChevronDown size={15} /> : <ChevronRight size={15} />}</span>
                <span className={styles.siteTitle}>{grupo.unidade}</span>
                <span className={styles.siteCount}>
                  {grupo.linhas.length} {grupo.linhas.length === 1 ? "equipamento" : "equipamentos"}
                  {grupo.daPlanilha && " · unidade da planilha"}
                </span>
              </span>
              <span className={styles.siteTotal}>{formatar(totalDaUnidade)} páginas</span>
            </button>

            {aberta && (
              <div className={styles.siteTableWrap}>
                <table className={styles.siteTable}>
                  <thead>
                    <tr className={styles.theadRow}>
                      <th className={styles.thFirst}>Impressora</th>
                      <th className={styles.th}>Endereço</th>
                      <th className={styles.th}>Departamento</th>
                      {meses.map((m) => (
                        <th key={m} className={styles.thMonth}>
                          {rotulos.get(m) ?? m}
                        </th>
                      ))}
                      <th className={styles.thTotalPlain}>Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {grupo.linhas.map((linha) => {
                      const p = linha.impressora;
                      return (
                        <tr key={linha.chave} className={cn(styles.bodyRow, linha.motivo && styles.rowMuted)}>
                          <td className={styles.nameCell}>
                            <button type="button" className={styles.nameButton} onClick={() => onSelectPrinter(p)}>
                              {p.name}
                            </button>
                            <span className={styles.nameMeta}>
                              {p.model}
                              {linha.outrasFilas.length > 0 &&
                                ` · +${linha.outrasFilas.length} ${linha.outrasFilas.length === 1 ? "fila" : "filas"}`}
                            </span>
                            {linha.motivo && <span className={styles.reason}>{linha.motivo}</span>}
                          </td>
                          <td className={styles.ipCell}>{p.ip}</td>
                          <td className={styles.deptCell} title={getDepartmentLabel(p)}>
                            {getDepartmentLabel(p) || "—"}
                          </td>
                          {meses.map((periodo) => {
                            const v = linha.porPeriodo.get(periodo);
                            return (
                              <td key={periodo} className={cn(styles.monthCell, v === undefined && styles.cellEmpty)}>
                                {v === undefined ? "—" : formatar(v)}
                              </td>
                            );
                          })}
                          <td className={styles.rowTotalCell}>{linha.motivo ? "—" : formatar(linha.total)}</td>
                        </tr>
                      );
                    })}
                    <tr className={styles.subtotalRow}>
                      <td className={styles.subtotalLabelCell} colSpan={3}>
                        Subtotal {grupo.unidade}
                      </td>
                      {totaisDaUnidade.map((t, i) => (
                        <td key={meses[i]} className={styles.subtotalMonthCell}>
                          {formatar(t)}
                        </td>
                      ))}
                      <td className={styles.subtotalTotalCell}>{formatar(totalDaUnidade)}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            )}
          </section>
        );
      })}

      <p className={styles.footnote}>
        Só impressoras com contador de páginas (etiquetadoras e quem nunca informou contador ficam de fora). Uma linha
        por equipamento (IP): filas do mesmo equipamento dividem o contador e aparecem como &quot;+N filas&quot;.
        &quot;—&quot; = mês sem dado. Unidade vem do cadastro do print server; sem ela, da planilha.
      </p>
    </div>
  );
}
