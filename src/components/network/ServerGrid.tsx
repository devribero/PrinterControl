"use client";

/**
 * Seção "Print Servers": resumo de estado no cabeçalho, ações gerais
 * (Atualizar, Novo) e a grade de escopos — "Todos", um cartão por servidor
 * e "Sem servidor" quando existir.
 */
import { Loader2, Plus, RefreshCw, Server } from "lucide-react";
import { cn } from "../../lib/cn";
import type { PrintServer } from "../../types";
import { ScopeCard, ServerCard } from "./ServerCard";
import type { ServerAction } from "./ServerActionsMenu";
import { plural, saudeDoServidor } from "./format";
import shared from "./shared.module.css";
import styles from "./ServerGrid.module.css";

interface ServerGridProps {
  servers: PrintServer[];
  loading: boolean;
  error: string | null;
  serverScope: string | null;
  canAdmin: boolean;
  allActiveCount: number;
  unassignedCount: number;
  onSelect: (scope: string | null) => void;
  onRefresh: () => void;
  onCreate: () => void;
  onAction: (action: ServerAction, server: PrintServer) => void;
  discoveringServerId: number | null;
  syncingServerId: number | null;
}

function resumo(servers: PrintServer[]): string {
  const contagem = { online: 0, error: 0, syncing: 0, inactive: 0 };
  for (const s of servers) {
    const k = saudeDoServidor(s).kind;
    if (k in contagem) contagem[k as keyof typeof contagem]++;
  }
  const partes = [plural(servers.length, "servidor", "servidores")];
  if (contagem.online) partes.push(`${contagem.online} online`);
  if (contagem.error) partes.push(`${contagem.error} com falha`);
  if (contagem.syncing) partes.push(`${contagem.syncing} sincronizando`);
  if (contagem.inactive) partes.push(plural(contagem.inactive, "desativado", "desativados"));
  return partes.join(" · ");
}

export default function ServerGrid({
  servers,
  loading,
  error,
  serverScope,
  canAdmin,
  allActiveCount,
  unassignedCount,
  onSelect,
  onRefresh,
  onCreate,
  onAction,
  discoveringServerId,
  syncingServerId,
}: ServerGridProps) {
  const carregandoPrimeiraVez = loading && servers.length === 0;

  function bloqueio(server: PrintServer, emAndamento: number | null, texto: string): string | null {
    if (!server.active) return "Servidor desativado.";
    if (emAndamento === server.id) return `${texto} em andamento neste servidor.`;
    if (emAndamento !== null) return `Aguarde: ${texto.toLowerCase()} em andamento em outro servidor.`;
    return null;
  }

  return (
    <section className={cn(shared.card, shared.cardOpen)} aria-labelledby="network-servers-title">
      <div className={shared.cardHeader}>
        <div className={shared.cardHeaderText}>
          <h2 id="network-servers-title" className={shared.cardTitle}>
            Print Servers
          </h2>
          <p className={shared.cardSubtitle}>
            {carregandoPrimeiraVez ? "Carregando servidores…" : servers.length > 0 ? resumo(servers) : "Nenhum servidor registrado"}
          </p>
          {servers.length > 0 && (
            <p className={styles.headerNote}>
              Servidores reais sincronizam sozinhos ao cadastrar e a cada 6 h. O selecionado vale para o
              painel inteiro.
            </p>
          )}
        </div>
        <div className={shared.headerActions}>
          <button type="button" onClick={onRefresh} disabled={loading} className={shared.secondaryButton}>
            <RefreshCw size={15} className={loading ? "animate-spin" : ""} />
            Atualizar
          </button>
          {canAdmin && (
            <button type="button" onClick={onCreate} className={shared.primaryButton}>
              <Plus size={15} />
              Novo Print Server
            </button>
          )}
        </div>
      </div>

      {error && !loading && (
        <div className={shared.cardBody}>
          <p className={shared.errorBox}>{error}</p>
        </div>
      )}

      {carregandoPrimeiraVez && (
        <div className={shared.emptyState}>
          <Loader2 size={20} className="animate-spin" />
          Carregando Print Servers…
        </div>
      )}

      {!loading && !error && servers.length === 0 && (
        <div className={shared.emptyState}>
          <Server size={28} className={shared.emptyIcon} />
          <span className={shared.emptyTitle}>Nenhum Print Server registrado</span>
          <span>
            {canAdmin
              ? "Cadastre o primeiro para o painel começar a acompanhar as filas dele."
              : "Peça a um administrador para cadastrar um."}
          </span>
          {canAdmin && (
            <button type="button" onClick={onCreate} className={shared.primaryButton}>
              <Plus size={15} />
              Novo Print Server
            </button>
          )}
        </div>
      )}

      {servers.length > 0 && (
        <div className={styles.grid}>
          <ScopeCard kind="all" count={allActiveCount} selected={serverScope === null} onSelect={() => onSelect(null)} />

          {servers.map((server) => (
            <ServerCard
              key={server.id}
              server={server}
              selected={server.host === serverScope}
              canAdmin={canAdmin}
              onSelect={onSelect}
              onAction={onAction}
              activity={
                discoveringServerId === server.id
                  ? "discovering"
                  : syncingServerId === server.id
                    ? "syncing"
                    : null
              }
              discoverBlocked={bloqueio(server, discoveringServerId, "Descoberta")}
              syncBlocked={bloqueio(server, syncingServerId, "Sincronização")}
            />
          ))}

          {unassignedCount > 0 && (
            <ScopeCard kind="none" count={unassignedCount} selected={serverScope === ""} onSelect={() => onSelect("")} />
          )}
        </div>
      )}
    </section>
  );
}
