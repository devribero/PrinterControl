"use client";

/**
 * Selo "dados fictícios" (Fase 9).
 *
 * Existe como componente próprio, e não como marcação repetida em cada card,
 * porque a regra desta fase é que dado fictício se anuncie SEMPRE do mesmo
 * jeito: um selo que muda de forma entre um gráfico e outro treina o olho a
 * ignorá-lo.
 *
 * Fica ao lado do número, não no rodapé da página nem só na faixa do topo: a
 * faixa avisa que existe dado fictício na tela, mas quem lê um gráfico
 * isolado — ou tira print dele — não vê a faixa. O selo viaja junto do dado.
 */
import { FlaskConical } from "lucide-react";
import styles from "./DemoDataBadge.module.css";

interface DemoDataBadgeProps {
  /** Quando false o componente não renderiza nada — deixa o call site limpo. */
  ficticio: boolean;
  /** Texto do title, para explicar POR QUE o dado é fictício neste card. */
  motivo?: string;
}

export default function DemoDataBadge({ ficticio, motivo }: DemoDataBadgeProps) {
  if (!ficticio) return null;

  return (
    <span
      className={styles.badge}
      title={motivo ?? "Estes números são fictícios e não vêm da sua frota."}
    >
      <FlaskConical size={11} aria-hidden="true" />
      dados fictícios
    </span>
  );
}
