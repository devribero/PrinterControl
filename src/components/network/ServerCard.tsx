"use client";

/**
 * Cartão de um Print Server. Lê de cima para baixo na ordem do que importa:
 * estado (com o motivo da falha, quando houver), identificação, contagens e
 * situação do sync. Clicar no cartão seleciona o servidor para o painel
 * inteiro; as demais ações ficam no menu "⋯" (só admin).
 *
 * O cartão é um <div> com o botão de seleção e o menu como irmãos:
 * <button> dentro de <button> é HTML inválido. Por isso o conteúdo do botão
 * usa só <span>.
 */
import { Clock, Layers, Loader2, Unplug } from "lucide-react";
import { cn } from "../../lib/cn";
import type { PrintServer } from "../../types";
import ServerActionsMenu, { type ServerAction } from "./ServerActionsMenu";
import { formatarMomento, isAutoSyncPending, motivoDaFalha, saudeDoServidor } from "./format";
import styles from "./ServerGrid.module.css";

const DOT_CLASS = {
  online: styles.dotOnline,
  error: styles.dotError,
  syncing: styles.dotSyncing,
  unknown: styles.dotUnknown,
  inactive: styles.dotInactive,
} as const;

interface ServerCardProps {
  server: PrintServer;
  selected: boolean;
  canAdmin: boolean;
  onSelect: (host: string) => void;
  onAction: (action: ServerAction, server: PrintServer) => void;
  /** Operação manual em andamento neste servidor. */
  activity: "discovering" | "syncing" | null;
  discoverBlocked: string | null;
  syncBlocked: string | null;
}

export function ServerCard({
  server,
  selected,
  canAdmin,
  onSelect,
  onAction,
  activity,
  discoverBlocked,
  syncBlocked,
}: ServerCardProps) {
  const saude = saudeDoServidor(server);
  const pendente = isAutoSyncPending(server);
  const temRotulo = server.name !== "" && server.name !== server.host;

  return (
    <div className={cn(styles.serverCard, selected && styles.serverCardActive, !server.active && styles.serverCardOff)}>
      <button
        type="button"
        onClick={() => onSelect(server.host)}
        className={cn(styles.serverSelect, canAdmin && styles.serverSelectWithMenu)}
        aria-pressed={selected}
      >
        <span className={styles.statusRow}>
          <span className={cn(styles.dot, DOT_CLASS[saude.kind])} aria-hidden="true" />
          <span className={styles.statusLabel}>{saude.label}</span>
        </span>

        <span className={styles.serverHost}>{server.host}</span>
        {temRotulo && <span className={styles.serverName}>{server.name}</span>}

        {saude.kind === "error" && server.lastError && (
          <span className={styles.failure} title={server.lastError}>
            {motivoDaFalha(server.lastError)}
          </span>
        )}

        <span className={styles.chips}>
          <span className={styles.chip}>{server.mode === "real" ? "Real" : "Simulado"}</span>
          {server.unitName && <span className={styles.chip}>{server.unitName}</span>}
          {server.isDefault && <span className={styles.chip}>Padrão</span>}
        </span>

        <span className={styles.cardFooter}>
          <span className={styles.counts}>
            <strong>{server.activePrinterCount}</strong> ativa(s) · {server.printerCount} cadastrada(s)
          </span>
          <span
            className={styles.meta}
            title={server.mode === "real" ? "Servidores reais sincronizam sozinhos a cada 6 h." : undefined}
          >
            {activity ? (
              <>
                <Loader2 size={12} className="animate-spin" />
                {activity === "discovering" ? "Descobrindo filas…" : "Sincronizando…"}
              </>
            ) : pendente ? (
              <>
                <Loader2 size={12} className="animate-spin" />
                Sincronizando automaticamente…
              </>
            ) : (
              <>
                <Clock size={12} />
                Último sync: {formatarMomento(server.lastSyncAt)}
              </>
            )}
          </span>
        </span>
      </button>

      {canAdmin && (
        <div className={styles.cardMenu}>
          <ServerActionsMenu
            server={server}
            onAction={onAction}
            discoverBlocked={discoverBlocked}
            syncBlocked={syncBlocked}
          />
        </div>
      )}
    </div>
  );
}

interface ScopeCardProps {
  kind: "all" | "none";
  count: number;
  selected: boolean;
  onSelect: () => void;
}

/**
 * Escopos que não são um Print Server: "Todos os servidores" (a única vista
 * que junta origens diferentes) e "Sem servidor" (cadastradas à mão, que
 * nenhum sync cria ou desativa).
 */
export function ScopeCard({ kind, count, selected, onSelect }: ScopeCardProps) {
  const Icon = kind === "all" ? Layers : Unplug;
  return (
    <div className={cn(styles.serverCard, styles.scopeCard, selected && styles.serverCardActive)}>
      <button type="button" onClick={onSelect} className={styles.serverSelect} aria-pressed={selected}>
        <span className={styles.statusRow}>
          <Icon size={14} className={styles.scopeIcon} aria-hidden="true" />
          <span className={styles.statusLabel}>{kind === "all" ? "Escopo geral" : "Cadastro manual"}</span>
        </span>
        <span className={styles.serverHost}>{kind === "all" ? "Todos os servidores" : "Sem servidor"}</span>
        <span className={styles.serverName}>
          {kind === "all" ? "Frota inteira, sem separar por origem" : "Fora de qualquer Print Server"}
        </span>
        <span className={styles.cardFooter}>
          <span className={styles.counts}>
            <strong>{count}</strong> ativa(s){kind === "all" ? " no total" : ""}
          </span>
          <span className={styles.meta}>
            {kind === "all" ? "Descobrir e sincronizar exigem um servidor" : "Nenhum sync as cria ou desativa"}
          </span>
        </span>
      </button>
    </div>
  );
}
