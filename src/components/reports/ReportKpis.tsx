"use client";

/**
 * Quatro indicadores do período escolhido.
 *
 * A variação compara o último mês FECHADO do período com o mês anterior a
 * ele — mês em andamento nunca entra (no dia 21 ele tem só parte do mês, e
 * "−67%" diria que o consumo despencou quando o mês só não terminou). Quando
 * os dois meses têm número de equipamentos diferente, a variação bruta mistura
 * consumo com cobertura; a tela mostra as duas coberturas e a variação por
 * equipamento ao lado.
 */
import { AlertTriangle, ArrowDownRight, ArrowUpRight } from "lucide-react";
import { formatInt, formatPct, type ReportKpis as Kpis } from "./reportModel";
import styles from "./Reports.module.css";

interface ReportKpisProps {
  kpis: Kpis;
  monthCount: number;
  lastLabel: string;
  scoped: boolean;
}

export default function ReportKpis({ kpis, monthCount, lastLabel, scoped }: ReportKpisProps) {
  const { total, estimated, inProgressMonth, average, closedCount, variation, variationMissing } = kpis;

  return (
    <div className={styles.kpis}>
      <div className={styles.kpi}>
        <p className={styles.kpiLabel}>Páginas no período</p>
        <p className={styles.kpiValue}>{formatInt(total)}</p>
        <p className={styles.kpiSub}>
          {monthCount} {monthCount === 1 ? "mês" : "meses"}
          {inProgressMonth && ` · ${inProgressMonth.longLabel} parcial`}
        </p>
        {estimated !== null && estimated > 0 && (
          <p className={styles.kpiSub}>
            {formatInt(estimated)} estimadas ({formatPct((estimated / Math.max(1, total)) * 100)})
          </p>
        )}
        {estimated === null && scoped && <p className={styles.kpiSub}>Parte estimada só na visão de todos os servidores</p>}
      </div>

      <div className={styles.kpi}>
        <p className={styles.kpiLabel}>Média mensal</p>
        <p className={styles.kpiValue}>{average === null ? "—" : formatInt(average)}</p>
        <p className={styles.kpiSub}>
          {closedCount === 0
            ? "Nenhum mês fechado no período"
            : `${closedCount} ${closedCount === 1 ? "mês fechado" : "meses fechados"}`}
        </p>
      </div>

      <div className={styles.kpi}>
        <p className={styles.kpiLabel}>Variação vs mês anterior</p>
        {variation ? (
          <>
            <p className={styles.kpiValue}>
              {variation.pct >= 0 ? (
                <ArrowUpRight size={18} aria-hidden="true" className={styles.kpiArrow} />
              ) : (
                <ArrowDownRight size={18} aria-hidden="true" className={styles.kpiArrow} />
              )}
              {formatPct(variation.pct, true)}
            </p>
            <p className={styles.kpiSub}>
              {variation.current.longLabel} vs {variation.previous.longLabel}
            </p>
            {variation.perDevicePct !== null && (
              <p className={styles.kpiCaveat}>
                <AlertTriangle size={13} aria-hidden="true" className={styles.kpiCaveatIcon} />
                <span>
                  Cobertura diferente: {variation.current.devices} vs {variation.previous.devices} equip. Por
                  equipamento: {formatPct(variation.perDevicePct, true)}
                </span>
              </p>
            )}
          </>
        ) : (
          <>
            <p className={styles.kpiValue}>—</p>
            <p className={styles.kpiSub}>{variationMissing}</p>
          </>
        )}
      </div>

      <div className={styles.kpi}>
        <p className={styles.kpiLabel}>Equipamentos com dado</p>
        <p className={styles.kpiValue}>{formatInt(kpis.devicesLast)}</p>
        <p className={styles.kpiSub}>em {lastLabel}</p>
        {monthCount > 1 && (
          <p className={styles.kpiSub}>
            {kpis.devicesMin === kpis.devicesMax
              ? "Mesma cobertura em todo o período"
              : `Variou de ${kpis.devicesMin} a ${kpis.devicesMax} no período`}
          </p>
        )}
      </div>
    </div>
  );
}
