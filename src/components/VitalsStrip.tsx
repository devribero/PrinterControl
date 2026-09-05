"use client";

import { ArrowRight, TriangleAlert } from "lucide-react";
import type { Alert } from "../types";
import { cn } from "../lib/cn";
import styles from "./VitalsStrip.module.css";

type StatusFilter = "Todos" | "online" | "offline" | "atencao";

interface VitalsStripProps {
  total: number;
  online: number;
  attention: number;
  offline: number;
  activeStatus: StatusFilter;
  onSelectStatus: (status: StatusFilter) => void;
  topAlert: Alert | null;
  alertsRest: number;
  onViewAlerts: () => void;
  onSelectAlert?: (alert: Alert) => void;
}

export default function VitalsStrip({
  total,
  online,
  attention,
  offline,
  activeStatus,
  onSelectStatus,
  topAlert,
  alertsRest,
  onViewAlerts,
  onSelectAlert,
}: VitalsStripProps) {
  return (
    <div className={styles.strip}>
      <button
        onClick={() => onSelectStatus("Todos")}
        className={cn(styles.totalCell, activeStatus === "Todos" && styles.cellActive)}
      >
        <p className={styles.totalLabel}>Frota monitorada</p>
        <p className={styles.totalValue}>{total}</p>
      </button>

      <div className={styles.countsCell}>
        <button
          onClick={() => onSelectStatus("online")}
          className={cn(styles.countItem, activeStatus === "online" && styles.cellActive)}
        >
          <p className={styles.countLabel}>
            <span className={cn(styles.dot, styles.dotSuccess)} />
            Online
          </p>
          <p className={cn(styles.countValue, styles.countValueSuccess)}>{online}</p>
        </button>
        <button
          onClick={() => onSelectStatus("atencao")}
          className={cn(styles.countItem, activeStatus === "atencao" && styles.cellActive)}
        >
          <p className={styles.countLabel}>
            <span className={cn(styles.dot, styles.dotWarning)} />
            Atenção
          </p>
          <p className={cn(styles.countValue, styles.countValueWarning)}>{attention}</p>
        </button>
        <button
          onClick={() => onSelectStatus("offline")}
          className={cn(styles.countItem, activeStatus === "offline" && styles.cellActive)}
        >
          <p className={styles.countLabel}>
            <span className={cn(styles.dot, styles.dotMuted)} />
            Offline
          </p>
          <p className={styles.countValue}>{offline}</p>
        </button>
      </div>

      {topAlert && (
        <div className={styles.alertCell}>
          <TriangleAlert size={18} className={styles.alertIcon} />
          <div className={styles.alertBody}>
            <p className={styles.alertLabel}>Mais urgente agora</p>
            <button onClick={() => onSelectAlert?.(topAlert)} className={styles.alertMessage}>
              {topAlert.message}
              {alertsRest > 0 && <span className={styles.alertRest}> · +{alertsRest} outros</span>}
            </button>
          </div>
          <button onClick={onViewAlerts} className={styles.alertLink}>
            Ver alertas
            <ArrowRight size={14} />
          </button>
        </div>
      )}
    </div>
  );
}
