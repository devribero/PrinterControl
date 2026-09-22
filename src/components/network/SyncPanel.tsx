"use client";

/**
 * Andamento e resultado de uma sincronização manual. Pequeno de propósito:
 * a sincronização normal é a automática (backend, a cada 6 h); este painel
 * só aparece depois que alguém pede "Sincronizar agora".
 *
 * O pai monta um painel por execução (key = job.id).
 */
import { RefreshCw, X } from "lucide-react";
import { cn } from "../../lib/cn";
import { formatarDuracao } from "./format";
import { useElapsed } from "./useElapsed";
import type { SyncJob } from "./useServerSync";
import shared from "./shared.module.css";
import styles from "./panels.module.css";

interface SyncPanelProps {
  job: SyncJob;
  onDismiss: () => void;
}

export default function SyncPanel({ job, onDismiss }: SyncPanelProps) {
  const elapsed = useElapsed(job.startedAt, job.finishedAt);
  const running = job.status === "running";
  const r = job.result;

  let subtitulo = "";
  if (running) subtitulo = `Aplicando ao cadastro… ${formatarDuracao(elapsed)}`;
  else if (job.status === "busy") subtitulo = "Já havia uma sincronização automática em andamento";
  else if (job.status === "error") subtitulo = `Falhou após ${formatarDuracao(elapsed)}`;
  else if (r) subtitulo = `${r.discovered} fila(s) no servidor · concluída em ${formatarDuracao(elapsed)}`;

  return (
    <section className={shared.card} aria-labelledby={`sync-${job.id}`}>
      <div className={shared.cardHeader}>
        <div className={cn(shared.cardHeaderText, styles.panelHeading)}>
          <RefreshCw size={18} className={cn(styles.panelIcon, running && "animate-spin")} aria-hidden="true" />
          <div className={shared.cardHeaderText}>
            <h2 id={`sync-${job.id}`} className={shared.cardTitle}>
              Sincronização · {job.host}
            </h2>
            <p className={shared.cardSubtitle}>{subtitulo}</p>
          </div>
        </div>
        {!running && (
          <div className={shared.headerActions}>
            <button
              type="button"
              onClick={onDismiss}
              className={cn(shared.iconButton, styles.closeButton)}
              aria-label="Fechar resultado da sincronização"
              title="Fechar"
            >
              <X size={18} />
            </button>
          </div>
        )}
      </div>

      {running && (
        <div className={cn(shared.cardBody, styles.progressBody)}>
          <div className={shared.progressTrack} role="progressbar" aria-label="Sincronização em andamento">
            <div className={shared.progressBar} />
          </div>
          <p className={styles.progressNote}>
            Pode continuar usando a página; um aviso aparece quando terminar.
          </p>
        </div>
      )}

      {job.status === "busy" && (
        <div className={shared.cardBody}>
          <p className={shared.infoBox}>
            {job.error} O cadastro será atualizado quando ela terminar — use Atualizar na lista de servidores
            daqui a alguns minutos.
          </p>
        </div>
      )}

      {job.status === "error" && job.error && (
        <div className={shared.cardBody}>
          <p className={shared.errorBox}>{job.error}</p>
        </div>
      )}

      {job.status === "done" && r && (
        <div className={styles.statGrid}>
          <div className={styles.stat}>
            <span className={styles.statValue}>{r.created}</span>
            <span className={styles.statLabel}>criadas</span>
          </div>
          <div className={styles.stat}>
            <span className={styles.statValue}>{r.updated}</span>
            <span className={styles.statLabel}>atualizadas</span>
          </div>
          <div className={styles.stat}>
            <span className={styles.statValue}>{r.reactivated}</span>
            <span className={styles.statLabel}>reativadas</span>
          </div>
          <div className={styles.stat}>
            <span className={styles.statValue}>{r.deactivated}</span>
            <span className={styles.statLabel}>desativadas</span>
          </div>
        </div>
      )}
    </section>
  );
}
