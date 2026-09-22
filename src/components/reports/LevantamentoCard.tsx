"use client";

/**
 * "Levantamento mensal (Excel)" — gera a planilha de levantamento da empresa
 * com o mês escolhido preenchido pelas leituras do sistema (backend:
 * services/levantamento.py). Tudo o que não é o mês gerado continua igual à
 * planilha base.
 *
 * Gerar e trocar a base são ações de admin (o backend confere; aqui só não
 * oferecemos o botão). Baixar e ver o relatório: qualquer sessão.
 */
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { ChevronDown, Download, FileSpreadsheet, TriangleAlert, Upload } from "lucide-react";
import { parseApiDate } from "../../lib/adaptApi";
import { ApiError } from "../../lib/api";
import { useAppData } from "../../lib/app-data";
import {
  baixarArquivoLevantamento,
  enviarBaseLevantamento,
  fetchLevantamento,
  fetchRelatorioLevantamento,
  gerarLevantamento,
  type LevantamentoEstado,
  type LevantamentoRelatorio,
} from "../../lib/levantamento";
import { useToast } from "../../lib/toast";
import styles from "./Reports.module.css";
import own from "./LevantamentoCard.module.css";

const MESES = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"];

function rotuloMes(mes: string | null): string {
  if (!mes) return "—";
  const [ano, m] = mes.split("-");
  return `${MESES[Number(m) - 1] ?? m}/${ano}`;
}

function formatarDataHora(iso: string | null): string {
  const data = parseApiDate(iso);
  if (!data) return "—";
  return data.toLocaleString("pt-BR", { day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit" });
}

function formatarTamanho(bytes: number): string {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1).replace(".", ",")} MB`;
}

const n = (v: number) => v.toLocaleString("pt-BR");

/**
 * Mês sugerido: o último período já fechado. Se ele já está preenchido na
 * base (o normal entre o dia 4 e o fechamento seguinte), o próximo a
 * preencher — gerado como prévia enquanto o período corre.
 */
function mesPadrao(dados: LevantamentoEstado): string {
  const fechado = dados.meses.find((m) => m.mes === dados.ultimo_mes_fechado);
  if (fechado && !fechado.preenchido) return fechado.mes;
  const proximo = dados.meses.find((m) => m.mes === dados.proximo_mes);
  if (proximo && (proximo.fechado || proximo.em_andamento)) return proximo.mes;
  return dados.ultimo_mes_fechado ?? "";
}

function mensagemDeErro(e: unknown): string {
  return e instanceof ApiError ? e.message : "Erro inesperado. Tente novamente.";
}

export default function LevantamentoCard() {
  const { can } = useAppData();
  const { push } = useToast();
  const [estado, setEstado] = useState<LevantamentoEstado | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [mes, setMes] = useState<string>("");
  const [gerando, setGerando] = useState(false);
  const [relatorio, setRelatorio] = useState<LevantamentoRelatorio | null>(null);
  const [baixando, setBaixando] = useState<string | null>(null);
  const [arquivoBase, setArquivoBase] = useState<File | null>(null);
  const [enviando, setEnviando] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const carregar = useCallback(async (signal?: AbortSignal) => {
    try {
      const dados = await fetchLevantamento(signal);
      setEstado(dados);
      setErro(null);
      setMes((atual) => atual || mesPadrao(dados));
    } catch (e) {
      if (signal?.aborted) return;
      setErro(mensagemDeErro(e));
    }
  }, []);

  useEffect(() => {
    const ctrl = new AbortController();
    void carregar(ctrl.signal);
    return () => ctrl.abort();
  }, [carregar]);

  // Só meses cujo período já começou: fechados ou em andamento.
  const opcoes = useMemo(() => (estado?.meses ?? []).filter((m) => m.fechado || m.em_andamento), [estado]);
  const escolhido = opcoes.find((m) => m.mes === mes);
  const geradosArquivos = estado?.arquivos ?? [];

  async function handleGerar() {
    if (!mes) return;
    setGerando(true);
    try {
      const r = await gerarLevantamento(mes);
      setRelatorio(r);
      push({
        variant: r.previa ? "info" : "success",
        title: r.previa ? "Prévia gerada" : "Planilha gerada",
        description: `${r.mes_nome}/${r.ano}: ${r.preenchidas.linhas} linhas preenchidas, ${r.vazias.length} vazias.`,
      });
      await carregar();
    } catch (e) {
      push({ variant: "warning", title: "Não foi possível gerar", description: mensagemDeErro(e) });
    } finally {
      setGerando(false);
    }
  }

  async function handleBaixar(nome: string) {
    setBaixando(nome);
    try {
      await baixarArquivoLevantamento(nome);
    } catch (e) {
      push({ variant: "warning", title: "Download falhou", description: mensagemDeErro(e) });
    } finally {
      setBaixando(null);
    }
  }

  async function handleVerRelatorio(nome: string) {
    try {
      setRelatorio(await fetchRelatorioLevantamento(nome));
    } catch (e) {
      push({ variant: "warning", title: "Relatório indisponível", description: mensagemDeErro(e) });
    }
  }

  async function handleEnviarBase() {
    if (!arquivoBase) return;
    setEnviando(true);
    try {
      const r = await enviarBaseLevantamento(arquivoBase);
      push({
        variant: "success",
        title: "Planilha base substituída",
        description: `${r.linhas} linhas de impressora em ${r.blocos} blocos; preenchida até ${rotuloMes(r.meses_preenchidos.at(-1) ?? null)}.`,
      });
      setArquivoBase(null);
      if (inputRef.current) inputRef.current.value = "";
      setMes("");
      await carregar();
    } catch (e) {
      push({ variant: "warning", title: "Planilha recusada", description: mensagemDeErro(e) });
    } finally {
      setEnviando(false);
    }
  }

  const base = estado?.base ?? null;
  const ultimoPreenchido = base?.meses_preenchidos.at(-1) ?? null;

  return (
    <section className={styles.card} aria-labelledby="levantamento-titulo">
      <header className={styles.cardHeader}>
        <div className={styles.cardHeading}>
          <FileSpreadsheet size={16} aria-hidden="true" className={own.headingIcon} />
          <h2 id="levantamento-titulo" className={styles.cardTitle}>
            Levantamento mensal (Excel)
          </h2>
        </div>
        {base && (
          <p className={own.baseInfo}>
            Base preenchida até <strong>{rotuloMes(ultimoPreenchido)}</strong>
            <span className={styles.dotSep}> · </span>
            atualizada em {formatarDataHora(base.atualizada_em)}
          </p>
        )}
      </header>

      <div className={own.body}>
        {erro && <p className={own.error}>{erro}</p>}
        {estado?.erro_base && <p className={own.error}>A planilha base não pode ser lida: {estado.erro_base}</p>}

        {estado && !base && !estado.erro_base && (
          <p className={own.note}>
            Nenhuma planilha base cadastrada.{" "}
            {can.canAdmin ? "Envie o levantamento atual abaixo para começar." : "Peça a um administrador para enviá-la."}
          </p>
        )}

        {base && (
          <div className={own.generate}>
            <p className={own.lead}>
              Gera a planilha idêntica à base com o mês escolhido preenchido pelas leituras do sistema. Equipamento
              sem leitura no período fica com a célula vazia; equipamento que o sistema mede e a planilha não tem vai
              para a aba “Novos no sistema”. Período ainda em andamento gera uma <strong>prévia</strong>, que não altera
              a base.
            </p>
            <div className={own.controls}>
              <label className={own.monthField}>
                <span className={styles.srOnly}>Mês do levantamento</span>
                <select className={styles.select} value={mes} onChange={(e) => setMes(e.target.value)}>
                  {opcoes.length === 0 && <option value="">Nenhum período iniciado</option>}
                  {opcoes.map((m) => (
                    <option key={m.mes} value={m.mes}>
                      {m.nome}/{m.mes.slice(0, 4)} · {m.periodo}
                      {m.em_andamento ? " · em andamento" : m.preenchido ? " · já na base" : ""}
                    </option>
                  ))}
                </select>
              </label>
              {can.canAdmin ? (
                <button type="button" className={own.primaryButton} onClick={handleGerar} disabled={!mes || gerando}>
                  <FileSpreadsheet size={14} aria-hidden="true" />
                  {gerando ? "Gerando…" : escolhido?.em_andamento ? "Gerar prévia" : "Gerar planilha"}
                </button>
              ) : (
                <span className={own.note}>Só administradores geram a planilha.</span>
              )}
            </div>
            {estado?.proximo_mes && estado.proximo_mes !== mes && (
              <p className={own.hint}>Próximo mês a preencher na base: {rotuloMes(estado.proximo_mes)}.</p>
            )}
            {escolhido?.preenchido && !escolhido.em_andamento && (
              <p className={own.hint}>
                {escolhido.nome} já está preenchido na base: gerar de novo substitui os valores pelos do sistema e
                mantém os da base nas linhas que o sistema não mediu.
              </p>
            )}
          </div>
        )}

        {relatorio && <Resultado relatorio={relatorio} onBaixar={handleBaixar} baixando={baixando} />}

        <div className={own.section}>
          <h3 className={own.sectionTitle}>Arquivos gerados</h3>
          {geradosArquivos.length === 0 ? (
            <p className={own.note}>Nenhum arquivo gerado ainda.</p>
          ) : (
            <table className={styles.cardTable}>
              <thead>
                <tr>
                  <th scope="col">Arquivo</th>
                  <th scope="col">Gerado em</th>
                  <th scope="col" className={styles.num}>
                    Tamanho
                  </th>
                  <th scope="col">
                    <span className={styles.srOnly}>Ações</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {geradosArquivos.map((a) => (
                  <tr key={a.nome}>
                    <td className={styles.cardTableLead}>
                      <span className={own.fileName}>{a.nome}</span>
                      {a.tipo === "base_anterior" && <span className={styles.tag}>base anterior</span>}
                      {a.previa && <span className={styles.tag}>prévia</span>}
                      {a.automatico && <span className={styles.tag}>automático</span>}
                    </td>
                    <td data-label="Gerado em" className={styles.mono}>
                      {formatarDataHora(a.gerado_em)}
                    </td>
                    <td data-label="Tamanho" className={`${styles.num} ${styles.mono}`}>
                      {formatarTamanho(a.tamanho)}
                    </td>
                    <td className={own.actions}>
                      {a.tipo === "gerado" && (
                        <button type="button" className={styles.textButton} onClick={() => handleVerRelatorio(a.nome)}>
                          Relatório
                        </button>
                      )}
                      <button
                        type="button"
                        className={own.secondaryButton}
                        onClick={() => handleBaixar(a.nome)}
                        disabled={baixando === a.nome}
                        aria-label={`Baixar ${a.nome}`}
                      >
                        <Download size={14} aria-hidden="true" />
                        {baixando === a.nome ? "Baixando…" : "Baixar"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {can.canAdmin && (
          <div className={own.section}>
            <h3 className={own.sectionTitle}>Enviar planilha base</h3>
            <p className={own.note}>
              Use quando a planilha for editada fora do sistema (impressora nova, linha corrigida, ano novo). As próximas
              gerações partem dela. A base atual fica guardada na lista acima como “base anterior”.
            </p>
            <div className={own.controls}>
              <input
                ref={inputRef}
                type="file"
                accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                className={styles.srOnly}
                id="levantamento-base"
                onChange={(e) => setArquivoBase(e.target.files?.[0] ?? null)}
              />
              <label htmlFor="levantamento-base" className={own.secondaryButton}>
                <Upload size={14} aria-hidden="true" />
                Escolher arquivo .xlsx
              </label>
              {arquivoBase && (
                <>
                  <span className={own.fileName}>{arquivoBase.name}</span>
                  <button type="button" className={own.primaryButton} onClick={handleEnviarBase} disabled={enviando}>
                    {enviando ? "Enviando…" : "Substituir base"}
                  </button>
                  <button
                    type="button"
                    className={styles.textButton}
                    onClick={() => {
                      setArquivoBase(null);
                      if (inputRef.current) inputRef.current.value = "";
                    }}
                  >
                    Cancelar
                  </button>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </section>
  );
}

function Resultado({
  relatorio: r,
  onBaixar,
  baixando,
}: {
  relatorio: LevantamentoRelatorio;
  onBaixar: (nome: string) => void;
  baixando: string | null;
}) {
  return (
    <div className={own.result} aria-live="polite">
      <div className={own.resultHeader}>
        <div>
          <p className={own.resultTitle}>
            {r.mes_nome}/{r.ano}
            {r.previa && <span className={styles.tag}>prévia</span>}
            {r.base_atualizada && <span className={styles.tag}>base atualizada</span>}
          </p>
          <p className={own.hint}>
            Período {r.periodo.texto} · gerado em {formatarDataHora(r.gerado_em)}
          </p>
        </div>
        <button
          type="button"
          className={own.secondaryButton}
          onClick={() => onBaixar(r.arquivo)}
          disabled={baixando === r.arquivo}
        >
          <Download size={14} aria-hidden="true" />
          {baixando === r.arquivo ? "Baixando…" : "Baixar arquivo"}
        </button>
      </div>

      <dl className={own.stats}>
        <div>
          <dt>Linhas preenchidas</dt>
          <dd>{n(r.preenchidas.linhas)}</dd>
        </div>
        <div>
          <dt>Páginas</dt>
          <dd>{n(r.preenchidas.paginas)}</dd>
          {r.preenchidas.estimadas > 0 && <p className={own.statSub}>{n(r.preenchidas.estimadas)} estimadas</p>}
        </div>
        <div>
          <dt>Deixadas vazias</dt>
          <dd>{n(r.vazias.length)}</dd>
        </div>
        <div>
          <dt>Novos no sistema</dt>
          <dd>{n(r.novos.length)}</dd>
        </div>
      </dl>

      {r.avisos.length > 0 && (
        <ul className={own.warnings}>
          {r.avisos.map((a) => (
            <li key={a}>
              <TriangleAlert size={14} aria-hidden="true" className={styles.kpiCaveatIcon} />
              <span>{a}</span>
            </li>
          ))}
        </ul>
      )}

      {r.vazias.length > 0 && (
        <details className={own.details}>
          <summary className={own.detailsSummary}>
            Linhas deixadas vazias <span className={styles.cardCount}>{r.vazias.length}</span>
            <ChevronDown size={16} aria-hidden="true" className={own.detailsIcon} />
          </summary>
          <table className={styles.cardTable}>
            <thead>
              <tr>
                <th scope="col">Unidade</th>
                <th scope="col">IP / célula</th>
                <th scope="col">Modelo · serial</th>
                <th scope="col">Motivo</th>
              </tr>
            </thead>
            <tbody>
              {r.vazias.map((v) => (
                <tr key={v.celula}>
                  <td className={styles.cardTableLead}>{v.unidade}</td>
                  <td data-label="IP / célula" className={styles.mono}>
                    {v.ip || "—"} · {v.celula}
                  </td>
                  <td data-label="Modelo · serial">
                    {v.modelo || "—"}
                    {v.serial ? ` · ${v.serial}` : ""}
                  </td>
                  <td data-label="Motivo">{v.motivo}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </details>
      )}

      {r.mantidas.length > 0 && (
        <details className={own.details}>
          <summary className={own.detailsSummary}>
            Valores mantidos da base <span className={styles.cardCount}>{r.mantidas.length}</span>
            <ChevronDown size={16} aria-hidden="true" className={own.detailsIcon} />
          </summary>
          <table className={styles.cardTable}>
            <tbody>
              {r.mantidas.map((v) => (
                <tr key={v.celula}>
                  <td className={styles.cardTableLead}>{v.unidade}</td>
                  <td data-label="IP / célula" className={styles.mono}>
                    {v.ip || "—"} · {v.celula}
                  </td>
                  <td data-label="Valor da base" className={styles.num}>
                    {v.valor}
                  </td>
                  <td data-label="Sistema">{v.motivo}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </details>
      )}

      {r.novos.length > 0 && (
        <details className={own.details}>
          <summary className={own.detailsSummary}>
            Novos no sistema <span className={styles.cardCount}>{r.novos.length}</span>
            <ChevronDown size={16} aria-hidden="true" className={own.detailsIcon} />
          </summary>
          <table className={styles.cardTable}>
            <thead>
              <tr>
                <th scope="col">Fila</th>
                <th scope="col">IP</th>
                <th scope="col">Modelo · serial</th>
                <th scope="col">Unidade / servidor</th>
                <th scope="col" className={styles.num}>
                  Páginas
                </th>
              </tr>
            </thead>
            <tbody>
              {r.novos.map((d) => (
                <tr key={`${d.ip}-${d.fila}`}>
                  <td className={styles.cardTableLead}>{d.fila}</td>
                  <td data-label="IP" className={styles.mono}>
                    {d.ip}
                  </td>
                  <td data-label="Modelo · serial">
                    {d.modelo || "—"}
                    {d.serial ? ` · ${d.serial}` : ""}
                  </td>
                  <td data-label="Unidade / servidor">{[d.unidade, d.servidor].filter(Boolean).join(" / ") || "—"}</td>
                  <td data-label="Páginas" className={`${styles.num} ${styles.mono}`}>
                    {n(d.paginas)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </details>
      )}

      {r.correcoes_formula.length > 0 && (
        <details className={own.details}>
          <summary className={own.detailsSummary}>
            Fórmulas de total corrigidas <span className={styles.cardCount}>{r.correcoes_formula.length}</span>
            <ChevronDown size={16} aria-hidden="true" className={own.detailsIcon} />
          </summary>
          <p className={own.note}>
            Somas que pulavam linhas do bloco, só no mês gerado e nos meses seguintes ainda vazios. Meses passados não
            foram alterados.
          </p>
          <table className={styles.cardTable}>
            <tbody>
              {r.correcoes_formula.map((c) => (
                <tr key={c.celula}>
                  <td className={styles.cardTableLead}>
                    {c.celula} <span className={own.muted}>· {c.bloco}</span>
                  </td>
                  <td data-label="Antes" className={styles.mono}>
                    {c.antes ?? "(vazia)"}
                  </td>
                  <td data-label="Depois" className={styles.mono}>
                    {c.depois}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </details>
      )}
    </div>
  );
}
