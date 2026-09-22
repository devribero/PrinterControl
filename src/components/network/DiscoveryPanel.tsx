"use client";

/**
 * Painel da descoberta (pré-visualização, não grava nada).
 *
 * Mostra o andamento com tempo decorrido enquanto o servidor responde — em
 * servidor remoto a consulta leva 1–2 min — e o resultado quando chega.
 * A execução mora em useServerDiscovery, então o painel pode ser recolhido
 * (outro escopo selecionado) sem perder nada: ele volta a abrir ao
 * selecionar o servidor de novo.
 *
 * O pai monta um painel por execução (key = job.id).
 */
import { useMemo } from "react";
import { RadioTower, RotateCw, X } from "lucide-react";
import { cn } from "../../lib/cn";
import DiscoveryResults from "./DiscoveryResults";
import { adaptDiscovered, formatarDuracao } from "./format";
import { useElapsed } from "./useElapsed";
import type { DiscoveryJob } from "./useServerDiscovery";
import shared from "./shared.module.css";
import styles from "./panels.module.css";

/** A partir daqui a consulta já passou do tempo normal de um servidor remoto. */
const LENTO_MS = 100_000;

interface DiscoveryPanelProps {
  job: DiscoveryJob;
  /** true quando o servidor da descoberta é o escopo selecionado. */
  isCurrent: boolean;
  /** false quando o servidor sumiu ou foi desativado — sem "Repetir". */
  canRetry: boolean;
  onShow: () => void;
  onRetry: () => void;
  onDismiss: () => void;
}

export default function DiscoveryPanel({ job, isCurrent, canRetry, onShow, onRetry, onDismiss }: DiscoveryPanelProps) {
  const elapsed = useElapsed(job.startedAt, job.finishedAt);
  const running = job.status === "running";

  const resumo = useMemo(() => {
    if (!job.result) return null;
    const contagem = { online: 0, atencao: 0, offline: 0 };
    for (const p of job.result.printers) {
      if (p.status === "online") contagem.online++;
      else if (p.status === "atencao") contagem.atencao++;
      else contagem.offline++;
    }
    return contagem;
  }, [job.result]);

  const printers = useMemo(() => (job.result ? adaptDiscovered(job.result) : []), [job.result]);

  let subtitulo: string;
  if (running) subtitulo = `Consultando o servidor… ${formatarDuracao(elapsed)}`;
  else if (job.status === "error") subtitulo = `Falhou após ${formatarDuracao(elapsed)}`;
  else if (job.result)
    subtitulo =
      `${job.result.count} fila(s) · ${job.result.unique_ips} IP(s) distinto(s) · ` +
      `${job.result.mode === "real" ? "consulta real" : "simulação"} · ${formatarDuracao(elapsed)}`;
  else subtitulo = "";

  return (
    <section className={shared.card} aria-labelledby={`discovery-${job.id}`}>
      <div className={shared.cardHeader}>
        <div className={cn(shared.cardHeaderText, styles.panelHeading)}>
          <RadioTower size={18} className={styles.panelIcon} aria-hidden="true" />
          <div className={shared.cardHeaderText}>
            <h2 id={`discovery-${job.id}`} className={shared.cardTitle}>
              Descoberta · {job.host}
            </h2>
            <p className={shared.cardSubtitle}>{subtitulo}</p>
          </div>
        </div>
        <div className={shared.headerActions}>
          {!isCurrent && (
            <button type="button" onClick={onShow} className={shared.secondaryButton}>
              Ver servidor
            </button>
          )}
          {!running && canRetry && isCurrent && (
            <button type="button" onClick={onRetry} className={shared.secondaryButton}>
              <RotateCw size={15} />
              Repetir
            </button>
          )}
          {running ? (
            <button type="button" onClick={onDismiss} className={shared.secondaryButton}>
              Parar de esperar
            </button>
          ) : (
            <button
              type="button"
              onClick={onDismiss}
              className={cn(shared.iconButton, styles.closeButton)}
              aria-label="Fechar resultado da descoberta"
              title="Fechar"
            >
              <X size={18} />
            </button>
          )}
        </div>
      </div>

      {running && (
        <div className={cn(shared.cardBody, styles.progressBody)}>
          <div className={shared.progressTrack} role="progressbar" aria-label="Descoberta em andamento">
            <div className={shared.progressBar} />
          </div>
          <p className={styles.progressNote}>
            {elapsed > LENTO_MS
              ? "Está demorando mais que o normal — o servidor pode estar lento ou fora de alcance. Você pode esperar ou parar de acompanhar."
              : "Servidores remotos costumam levar de 1 a 2 minutos. Pode continuar usando a página; um aviso aparece quando terminar."}
          </p>
        </div>
      )}

      {job.status === "error" && job.error && (
        <div className={shared.cardBody}>
          <p className={shared.errorBox}>{job.error}</p>
        </div>
      )}

      {job.status === "done" && !isCurrent && (
        <p className={shared.footnote}>Selecione o servidor para ver as filas encontradas.</p>
      )}

      {job.status === "done" && isCurrent && resumo && (
        <>
          <div className={styles.statGrid}>
            <div className={styles.stat}>
              <span className={cn(styles.statDot, styles.dotOnline)} aria-hidden="true" />
              <span className={styles.statValue}>{resumo.online}</span>
              <span className={styles.statLabel}>online</span>
            </div>
            <div className={styles.stat}>
              <span className={cn(styles.statDot, styles.dotWarning)} aria-hidden="true" />
              <span className={styles.statValue}>{resumo.atencao}</span>
              <span className={styles.statLabel}>atenção</span>
            </div>
            <div className={styles.stat}>
              <span className={cn(styles.statDot, styles.dotError)} aria-hidden="true" />
              <span className={styles.statValue}>{resumo.offline}</span>
              <span className={styles.statLabel}>offline</span>
            </div>
          </div>

          <DiscoveryResults printers={printers} />

          <p className={shared.footnote}>
            Fotografia do servidor, não o cadastro — nada foi gravado. Para aplicar ao cadastro, use
            Sincronizar agora no menu do servidor.
          </p>
        </>
      )}
    </section>
  );
}
