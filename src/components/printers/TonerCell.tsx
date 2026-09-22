import type { TonerLevel } from "../../types";
import { tonerLevelColor } from "../../lib/tonerColor";
import { levelBand } from "../toner/tonerModel";
import { cn } from "../../lib/cn";
import { lowestToner } from "./fleetModel";
import styles from "./TonerCell.module.css";

/**
 * Canal de toner mais baixo: barra na cor da faixa (crítico ≤10 / baixo ≤20,
 * lib/tonerColor) e percentual. O número só ganha cor quando pede ação.
 * Usado na tabela do Dashboard (PrinterTable) e na lista de /printers.
 */
export default function TonerCell({ toner }: { toner: TonerLevel[] | null }) {
  const worst = lowestToner({ toner });
  if (!worst) return <span className={styles.na}>—</span>;

  const band = levelBand(worst.percent);
  return (
    <span className={styles.cell} title={(toner ?? []).map((t) => `${t.label}: ${t.percent}%`).join(" · ")}>
      <span className={styles.track} aria-hidden="true">
        <span
          className={styles.fill}
          style={{ width: `${Math.max(0, Math.min(100, worst.percent))}%`, backgroundColor: tonerLevelColor(worst.percent) }}
        />
      </span>
      <span
        className={cn(styles.percent, band === "critical" && styles.percentCritical, band === "low" && styles.percentLow)}
      >
        {(toner?.length ?? 0) > 1 && <span className={styles.channel}>{worst.color}</span>}
        {worst.percent}%
      </span>
    </span>
  );
}
