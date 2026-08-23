"use client";

/**
 * Mapeamento de Rede (rota "/network") — ferramenta operacional sobre o
 * registro de Print Servers da Fase 4.
 *
 * A distinção que esta tela existe para deixar clara:
 *
 *   DESCOBRIR  -> pergunta ao Print Server o que existe AGORA.
 *                 Não grava nada. É seguro repetir à vontade.
 *   SINCRONIZAR -> aplica esse resultado no banco: cria as novas, atualiza
 *                 as existentes e desativa as que sumiram. Muda dados.
 *
 * Por isso são dois blocos visualmente separados, com cores e textos
 * próprios, e o sync passa por confirmação explícita. Nada acontece ao
 * abrir a página — nem descoberta, nem sync.
 *
 * Dependências externas: react e lucide-react. Locais: Modal e
 * DiscoveryResults (reaproveitados), lib/api, lib/adaptApi, lib/apiErrors.
 */
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  RadioTower,
  RefreshCw,
  Loader2,
  Server,
  Database,
  CircleCheck,
  CircleAlert,
  CircleX,
  Info,
  Clock,
} from "lucide-react";
import { discoverServer, fetchPrintServers, syncServer, type ApiDiscoveryResponse } from "../lib/api";
import { adaptPrintServer, adaptSyncResult } from "../lib/adaptApi";
import { useApiErrorReporter } from "../lib/apiErrors";
import { useAppData } from "../lib/app-data";
import { useToast } from "../lib/toast";
import { cn } from "../lib/cn";
import Modal from "./Modal";
import DiscoveryResults from "./DiscoveryResults";
import type { DiscoveredPrinter, PrintServer, SyncResult } from "../types";
import styles from "./NetworkView.module.css";

/** Converte a resposta da API para o tipo que DiscoveryResults já consome. */
function adaptDiscovered(data: ApiDiscoveryResponse): DiscoveredPrinter[] {
  return data.printers.map((p) => ({
    name: p.name,
    server: p.server,
    portName: p.port_name,
    ip: p.ip,
    driverName: p.driver_name,
    source: p.source,
    ipResolution: p.ip_resolution,
    ipGroupSize: p.ip_group_size,
    networkQueryReused: p.network_query_reused,
    reachable: p.reachable,
    snmpResponded: p.snmp_responded,
    status: p.status,
    statusReason: p.status_reason,
    pageCount: p.page_count,
    uptime: p.uptime,
    toners: p.toners.map((t) => ({ color: t.color, percent: t.percent, description: t.description })),
    error: p.error,
  }));
}

function formatarMomento(iso: string | null): string {
  if (!iso) return "nunca";
  const data = new Date(iso);
  if (Number.isNaN(data.getTime())) return "desconhecido";
  return data.toLocaleString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

const STATUS_SERVIDOR: Record<PrintServer["lastStatus"], string> = {
  unknown: "Nunca consultado",
  online: "Respondeu",
  error: "Falhou",
};

export default function NetworkView() {
  const { can, printers, usingRealData, handleRefresh } = useAppData();
  const { push } = useToast();
  const relatarErro = useApiErrorReporter();

  const [servers, setServers] = useState<PrintServer[] | null>(null);
  const [loadingServers, setLoadingServers] = useState(true);
  const [serversError, setServersError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<number | null>(null);

  // Descoberta — transitória, nunca persistida.
  const [discovering, setDiscovering] = useState(false);
  const [discovery, setDiscovery] = useState<ApiDiscoveryResponse | null>(null);
  const [discoveryError, setDiscoveryError] = useState<string | null>(null);

  // Sync — muda o banco, por isso passa por confirmação.
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [syncResult, setSyncResult] = useState<SyncResult | null>(null);
  const [syncError, setSyncError] = useState<string | null>(null);

  const carregarServidores = useCallback(async () => {
    setLoadingServers(true);
    try {
      const data = (await fetchPrintServers()).map(adaptPrintServer);
      setServers(data);
      setServersError(null);
      // Seleciona o padrão na primeira carga, só para a tela não abrir vazia.
      // Isto NÃO dispara descoberta nem sync — apenas escolhe o servidor.
      setSelectedId((atual) => {
        if (atual !== null && data.some((s) => s.id === atual)) return atual;
        return (data.find((s) => s.isDefault) ?? data[0])?.id ?? null;
      });
    } catch (error) {
      setServers(null);
      setServersError(relatarErro(error, "Falha ao carregar os Print Servers"));
    } finally {
      setLoadingServers(false);
    }
  }, [relatarErro]);

  useEffect(() => {
    void carregarServidores();
  }, [carregarServidores]);

  const selected = useMemo(
    () => (servers ?? []).find((s) => s.id === selectedId) ?? null,
    [servers, selectedId],
  );

  /** Impressoras já cadastradas neste servidor — a relação servidor↔frota. */
  const printersDoServidor = useMemo(() => {
    if (!selected) return [];
    return printers.filter((p) => p.server === selected.host);
  }, [printers, selected]);

  /** Contagem por estado do que a descoberta encontrou. */
  const resumoDescoberta = useMemo(() => {
    if (!discovery) return null;
    const contagem = { online: 0, atencao: 0, offline: 0 };
    for (const p of discovery.printers) {
      if (p.status === "online") contagem.online++;
      else if (p.status === "atencao") contagem.atencao++;
      else contagem.offline++;
    }
    return contagem;
  }, [discovery]);

  // Trocar de servidor descarta o resultado anterior: mostrar a descoberta de
  // um servidor sob o cabeçalho de outro seria mentir para o usuário.
  function selecionar(id: number) {
    if (id === selectedId) return;
    setSelectedId(id);
    setDiscovery(null);
    setDiscoveryError(null);
    setSyncResult(null);
    setSyncError(null);
  }

  async function executarDescoberta() {
    if (!selected) return;
    setDiscovering(true);
    setDiscoveryError(null);
    try {
      const data = await discoverServer(selected.id);
      setDiscovery(data);
      push({
        variant: "success",
        title: "Descoberta concluída",
        description: `${data.count} fila(s) encontrada(s) em ${selected.host}. Nada foi gravado.`,
      });
      // O servidor guarda o desfecho (last_status/last_seen_at) — relê para
      // o cartão refletir o que acabou de acontecer.
      void carregarServidores();
    } catch (error) {
      setDiscovery(null);
      setDiscoveryError(relatarErro(error, "Falha na descoberta"));
      void carregarServidores();
    } finally {
      setDiscovering(false);
    }
  }

  async function executarSync() {
    if (!selected) return;
    setSyncing(true);
    setSyncError(null);
    try {
      const resultado = adaptSyncResult(await syncServer(selected.id));
      setSyncResult(resultado);
      setConfirmOpen(false);
      push({
        variant: "success",
        title: "Sincronização concluída",
        description:
          `${resultado.created} criada(s), ${resultado.updated} atualizada(s), ` +
          `${resultado.deactivated} desativada(s).`,
      });
      void carregarServidores();
      // A frota em memória ficou desatualizada depois de gravar no banco.
      if (usingRealData) void handleRefresh();
    } catch (error) {
      setSyncError(relatarErro(error, "Falha na sincronização"));
      setConfirmOpen(false);
      void carregarServidores();
    } finally {
      setSyncing(false);
    }
  }

  return (
    <div className={styles.page}>
      {/* ── Servidores ──────────────────────────────────────────────── */}
      <section className={styles.card}>
        <div className={styles.cardHeader}>
          <div>
            <h2 className={styles.cardTitle}>Print Servers</h2>
            <p className={styles.cardSubtitle}>
              {servers
                ? `${servers.length} servidor(es) registrado(s). Selecione um para operar.`
                : "Carregando servidores..."}
            </p>
          </div>
          <button onClick={() => void carregarServidores()} disabled={loadingServers} className={styles.secondaryButton}>
            <RefreshCw size={15} className={loadingServers ? "animate-spin" : ""} />
            Atualizar
          </button>
        </div>

        {serversError && !loadingServers && <p className={styles.errorBox}>{serversError}</p>}

        {loadingServers && !servers && (
          <p className={styles.emptyState}>
            <Loader2 size={16} className="animate-spin" /> Carregando Print Servers...
          </p>
        )}

        {servers && servers.length === 0 && (
          <p className={styles.emptyState}>Nenhum Print Server registrado.</p>
        )}

        {servers && servers.length > 0 && (
          <div className={styles.serverGrid}>
            {servers.map((server) => (
              <button
                key={server.id}
                onClick={() => selecionar(server.id)}
                className={cn(styles.serverCard, server.id === selectedId && styles.serverCardActive)}
                aria-pressed={server.id === selectedId}
              >
                <div className={styles.serverCardTop}>
                  <Server size={16} className={styles.serverIcon} />
                  <span className={styles.serverHost}>{server.host}</span>
                  {server.isDefault && <span className={styles.tagNeutral}>padrão</span>}
                </div>
                <p className={styles.serverName}>{server.name}</p>
                <div className={styles.serverTags}>
                  <span className={cn(styles.tag, server.mode === "real" ? styles.tagReal : styles.tagMock)}>
                    {server.mode === "real" ? "real" : "simulado"}
                  </span>
                  {!server.active && <span className={styles.tagOff}>desativado</span>}
                  <span
                    className={cn(
                      styles.tag,
                      server.lastStatus === "online" && styles.tagOk,
                      server.lastStatus === "error" && styles.tagErro,
                      server.lastStatus === "unknown" && styles.tagNeutral,
                    )}
                  >
                    {STATUS_SERVIDOR[server.lastStatus]}
                  </span>
                </div>
                <p className={styles.serverCounts}>
                  <strong>{server.activePrinterCount}</strong> ativa(s) de{" "}
                  <strong>{server.printerCount}</strong> cadastrada(s)
                </p>
                <p className={styles.serverMeta}>
                  <Clock size={12} /> Último sync: {formatarMomento(server.lastSyncAt)}
                </p>
              </button>
            ))}
          </div>
        )}
      </section>

      {selected && (
        <>
          {/* ── Ações: descobrir ≠ sincronizar ────────────────────────── */}
          <section className={styles.actionsGrid}>
            <div className={cn(styles.actionCard, styles.actionDiscover)}>
              <div className={styles.actionHeader}>
                <RadioTower size={18} className={styles.actionIconDiscover} />
                <h3 className={styles.actionTitle}>Descobrir</h3>
                <span className={styles.badgeSafe}>não grava nada</span>
              </div>
              <p className={styles.actionText}>
                Pergunta ao Print Server <strong>{selected.host}</strong> quais filas existem agora e
                consulta o estado de cada uma. O resultado é temporário: nada é criado, alterado ou
                removido no banco. Pode repetir à vontade.
              </p>
              {can.canAdmin ? (
                <button
                  onClick={() => void executarDescoberta()}
                  disabled={discovering || !selected.active}
                  className={styles.discoverButton}
                  title={selected.active ? undefined : "Servidor desativado"}
                >
                  {discovering ? <Loader2 size={15} className="animate-spin" /> : <RadioTower size={15} />}
                  {discovering ? "Consultando..." : "Descobrir agora"}
                </button>
              ) : (
                <p className={styles.permissionNote}>
                  <Info size={14} /> Ação exclusiva de administradores.
                </p>
              )}
            </div>

            <div className={cn(styles.actionCard, styles.actionSync)}>
              <div className={styles.actionHeader}>
                <Database size={18} className={styles.actionIconSync} />
                <h3 className={styles.actionTitle}>Sincronizar</h3>
                <span className={styles.badgeWrite}>grava no banco</span>
              </div>
              <p className={styles.actionText}>
                Aplica o que o Print Server informa ao cadastro: <strong>cria</strong> as filas novas,{" "}
                <strong>atualiza</strong> as existentes e <strong>desativa</strong> as que sumiram.
                Nada é apagado — leituras e alertas são preservados. Afeta apenas{" "}
                <strong>{selected.host}</strong>.
              </p>
              {can.canAdmin ? (
                <button
                  onClick={() => setConfirmOpen(true)}
                  disabled={syncing || !selected.active}
                  className={styles.syncButton}
                  title={selected.active ? undefined : "Servidor desativado"}
                >
                  {syncing ? <Loader2 size={15} className="animate-spin" /> : <Database size={15} />}
                  {syncing ? "Sincronizando..." : "Sincronizar..."}
                </button>
              ) : (
                <p className={styles.permissionNote}>
                  <Info size={14} /> Ação exclusiva de administradores.
                </p>
              )}
            </div>
          </section>

          {!selected.active && (
            <p className={styles.warnBox}>
              Este Print Server está desativado: descobrir e sincronizar ficam bloqueados aqui, e
              o backend também os recusa. A reativação é feita no registro de servidores, que ainda
              não tem tela própria — por ora, só pela API.
            </p>
          )}

          {selected.lastStatus === "error" && selected.lastError && (
            <p className={styles.errorBox}>
              <strong>Última tentativa falhou:</strong> {selected.lastError}
            </p>
          )}

          {/* ── Resultado do sync ──────────────────────────────────────── */}
          {syncError && <p className={styles.errorBox}>{syncError}</p>}

          {syncResult && (
            <section className={styles.card}>
              <div className={styles.cardHeader}>
                <div>
                  <h2 className={styles.cardTitle}>O que a sincronização mudou</h2>
                  <p className={styles.cardSubtitle}>
                    {syncResult.server} · {syncResult.discovered} fila(s) encontrada(s) no servidor
                  </p>
                </div>
              </div>
              <div className={styles.resultGrid}>
                <div className={styles.resultItem}>
                  <span className={styles.resultValue}>{syncResult.created}</span>
                  <span className={styles.resultLabel}>criadas</span>
                </div>
                <div className={styles.resultItem}>
                  <span className={styles.resultValue}>{syncResult.updated}</span>
                  <span className={styles.resultLabel}>atualizadas</span>
                </div>
                <div className={styles.resultItem}>
                  <span className={styles.resultValue}>{syncResult.reactivated}</span>
                  <span className={styles.resultLabel}>reativadas</span>
                </div>
                <div className={styles.resultItem}>
                  <span className={styles.resultValue}>{syncResult.deactivated}</span>
                  <span className={styles.resultLabel}>desativadas</span>
                </div>
              </div>
            </section>
          )}

          {/* ── Resultado da descoberta ────────────────────────────────── */}
          {discoveryError && <p className={styles.errorBox}>{discoveryError}</p>}

          {discovery && resumoDescoberta && (
            <>
              <section className={styles.card}>
                <div className={styles.cardHeader}>
                  <div>
                    <h2 className={styles.cardTitle}>Estado das filas descobertas</h2>
                    <p className={styles.cardSubtitle}>
                      {discovery.count} fila(s) · {discovery.unique_ips} IP(s) distinto(s) ·{" "}
                      {discovery.mode === "real" ? "consulta real" : "simulação"}
                    </p>
                  </div>
                </div>
                <div className={styles.statusGrid}>
                  <div className={cn(styles.statusItem, styles.statusOnline)}>
                    <CircleCheck size={18} />
                    <span className={styles.statusValue}>{resumoDescoberta.online}</span>
                    <span className={styles.statusLabel}>online</span>
                  </div>
                  <div className={cn(styles.statusItem, styles.statusAtencao)}>
                    <CircleAlert size={18} />
                    <span className={styles.statusValue}>{resumoDescoberta.atencao}</span>
                    <span className={styles.statusLabel}>atenção</span>
                  </div>
                  <div className={cn(styles.statusItem, styles.statusOffline)}>
                    <CircleX size={18} />
                    <span className={styles.statusValue}>{resumoDescoberta.offline}</span>
                    <span className={styles.statusLabel}>offline</span>
                  </div>
                </div>
                <p className={styles.footnote}>
                  Este resultado é uma fotografia do servidor, não o cadastro. Para gravá-lo, use
                  Sincronizar.
                </p>
              </section>

              <DiscoveryResults
                printers={adaptDiscovered(discovery)}
                source={discovery.source}
                server={discovery.server}
              />
            </>
          )}

          {/* ── Relação servidor ↔ impressoras cadastradas ─────────────── */}
          <section className={styles.card}>
            <div className={styles.cardHeader}>
              <div>
                <h2 className={styles.cardTitle}>Impressoras cadastradas em {selected.host}</h2>
                <p className={styles.cardSubtitle}>
                  {printersDoServidor.length} no cadastro
                  {usingRealData ? "" : " · dados de demonstração"}
                </p>
              </div>
            </div>

            <div className={styles.tableWrap}>
              <table className={styles.table}>
                <thead>
                  <tr className={styles.theadRow}>
                    <th className={styles.thFirst}>Nome</th>
                    <th className={styles.th}>IP</th>
                    <th className={styles.th}>Modelo</th>
                    <th className={styles.th}>Departamento</th>
                    <th className={styles.th}>Estado</th>
                    <th className={styles.th}>Cadastro</th>
                  </tr>
                </thead>
                <tbody>
                  {printersDoServidor.map((printer) => (
                    <tr key={printer.id} className={styles.row}>
                      <td className={styles.tdFirst}>{printer.name}</td>
                      <td className={styles.td}>{printer.ip}</td>
                      <td className={styles.td}>{printer.model}</td>
                      <td className={styles.td}>{printer.department || "—"}</td>
                      <td className={styles.td}>
                        <span
                          className={cn(
                            styles.pill,
                            printer.status === "online" && styles.pillOnline,
                            printer.status === "atencao" && styles.pillAtencao,
                            printer.status === "offline" && styles.pillOffline,
                          )}
                        >
                          {printer.status}
                        </span>
                      </td>
                      <td className={styles.td}>
                        <span className={cn(styles.pill, printer.active ? styles.pillAtivo : styles.pillInativo)}>
                          {printer.active ? "ativa" : "inativa"}
                        </span>
                      </td>
                    </tr>
                  ))}

                  {printersDoServidor.length === 0 && (
                    <tr>
                      <td colSpan={6} className={styles.emptyState}>
                        Nenhuma impressora cadastrada neste servidor. Use Descobrir para ver o que ele
                        publica e Sincronizar para trazê-las ao cadastro.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}

      <Modal
        open={confirmOpen}
        onClose={() => (syncing ? undefined : setConfirmOpen(false))}
        title="Sincronizar este Print Server?"
        subtitle={selected?.host}
        maxWidth="28rem"
        footer={
          <div className={styles.dialogFooter}>
            <button onClick={() => setConfirmOpen(false)} disabled={syncing} className={styles.secondaryButton}>
              Cancelar
            </button>
            <button onClick={() => void executarSync()} disabled={syncing} className={styles.syncButton}>
              {syncing ? <Loader2 size={15} className="animate-spin" /> : <Database size={15} />}
              Sincronizar
            </button>
          </div>
        }
      >
        <p className={styles.confirmText}>
          Esta ação <strong>altera o cadastro</strong>: filas novas serão criadas, as existentes
          atualizadas e as que não aparecerem mais no servidor serão marcadas como inativas.
        </p>
        <p className={styles.confirmText}>
          Nada é apagado — leituras e alertas são preservados, e uma impressora inativa volta a ficar
          ativa se reaparecer. Apenas <strong>{selected?.host}</strong> é afetado; impressoras de
          outros servidores não são tocadas.
        </p>

        {/* Sincronizar um servidor em modo simulado contra um cadastro real
            desativa tudo que o simulador não publica. O dado volta com o
            próximo sync real, mas o painel fica vazio nesse meio-tempo — o
            usuário precisa saber ANTES de clicar. */}
        {selected?.mode === "mock" && printersDoServidor.length > 0 && (
          <p className={styles.confirmWarn}>
            <strong>Atenção:</strong> este servidor está em modo <strong>simulado</strong>. O
            simulador publica uma frota fictícia, então as{" "}
            <strong>{printersDoServidor.length}</strong> impressoras já cadastradas que não
            aparecerem nele serão marcadas como <strong>inativas</strong> e sumirão do painel. Elas
            voltam ao sincronizar com o servidor em modo real.
          </p>
        )}
      </Modal>
    </div>
  );
}
