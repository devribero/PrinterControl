import { TriangleAlert } from "lucide-react";
import type { PrinterStatus } from "../types";
import { cn } from "../lib/cn";
import styles from "./PrinterStatusBadge.module.css";

const config: Record<PrinterStatus, { label: string; tone: string }> = {
  online: { label: "Online", tone: styles.toneOnline },
  offline: { label: "Offline", tone: styles.toneOffline },
  atencao: { label: "Atenção", tone: styles.toneAttention },
};

export default function PrinterStatusBadge({ status }: { status: PrinterStatus }) {
  const c = config[status];
  return (
    <span className={cn(styles.badge, c.tone)}>
      {status === "atencao" ? (
        <TriangleAlert size={12} aria-hidden="true" />
      ) : (
        <span className={styles.dot} aria-hidden="true" />
      )}
      {c.label}
    </span>
  );
}
