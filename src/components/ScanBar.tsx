"use client";

/**
 * Linha "Última verificação: hh:mm:ss · Verificar agora" usada no slot
 * `actions` do PageHeader. Vive num componente próprio porque Dashboard e
 * Suprimentos mostram exatamente o mesmo controle — antes era CSS duplicado
 * em `app/page.module.css`.
 */
import { RefreshCw } from "lucide-react";
import styles from "./ScanBar.module.css";

interface ScanBarProps {
  lastChecked: Date;
  scanning: boolean;
  onRefresh: () => void;
  /** Rótulo do botão em repouso — o Dashboard diz "Verificar agora", a tela
   * de Suprimentos "Atualizar agora". */
  label?: string;
}

export default function ScanBar({ lastChecked, scanning, onRefresh, label = "Verificar agora" }: ScanBarProps) {
  return (
    <div className={styles.scanBar}>
      <p>
        Última verificação: <span className={styles.value}>{lastChecked.toLocaleTimeString("pt-BR")}</span>
      </p>
      <button onClick={onRefresh} disabled={scanning} className={styles.button}>
        <RefreshCw size={13} className={scanning ? "animate-spin" : ""} />
        {scanning ? "Verificando..." : label}
      </button>
    </div>
  );
}
