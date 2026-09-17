"use client";

/**
 * Fumaça decorativa ao clicar/tocar no elemento PAI (o painel da marca no
 * login). As partículas são spans criados direto no DOM e animados com a
 * Web Animations API: nada passa pelo estado do React, então um clique não
 * re-renderiza a tela de login, e cada span se remove ao fim da animação.
 *
 * A regra global de movimento reduzido (app/globals.css) só encurta animações
 * e transições CSS — a Web Animations API não é afetada por ela, por isso a
 * checagem explícita aqui, incluindo a preferência do próprio painel.
 */
import { useEffect, useRef } from "react";
import styles from "./ClickSmoke.module.css";

const PUFFS_PER_CLICK = 16;
// Teto de nós vivos: cliques em rajada não acumulam centenas de animações.
const MAX_LIVE_NODES = 160;

function prefersReducedMotion(): boolean {
  return (
    window.matchMedia("(prefers-reduced-motion: reduce)").matches ||
    document.documentElement.classList.contains("reduce-motion")
  );
}

function spawnSmoke(layer: HTMLElement, x: number, y: number) {
  if (layer.childElementCount > MAX_LIVE_NODES) return;

  const ring = document.createElement("span");
  ring.className = styles.ring;
  ring.style.left = `${x}px`;
  ring.style.top = `${y}px`;
  layer.appendChild(ring);
  const ringAnimation = ring.animate(
    [
      { transform: "translate(-50%, -50%) scale(0.2)", opacity: 0.9 },
      { transform: "translate(-50%, -50%) scale(2.6)", opacity: 0 },
    ],
    { duration: 650, easing: "cubic-bezier(0.16, 1, 0.3, 1)" },
  );
  ringAnimation.onfinish = () => ring.remove();
  ringAnimation.oncancel = () => ring.remove();

  for (let i = 0; i < PUFFS_PER_CLICK; i++) {
    const puff = document.createElement("span");
    const size = 36 + Math.random() * 72;
    const angle = Math.random() * Math.PI * 2;
    const spread = 30 + Math.random() * 120;
    // Espalha para os lados e sobe, como fumaça quente.
    const dx = Math.cos(angle) * spread;
    const dy = Math.sin(angle) * spread * 0.5 - (50 + Math.random() * 110);

    puff.className = styles.puff;
    puff.style.width = `${size}px`;
    puff.style.height = `${size}px`;
    puff.style.left = `${x - size / 2}px`;
    puff.style.top = `${y - size / 2}px`;
    layer.appendChild(puff);

    const animation = puff.animate(
      [
        { transform: "translate(0, 0) scale(0.25) rotate(0deg)", opacity: 0 },
        { opacity: 0.5 + Math.random() * 0.3, offset: 0.12 },
        {
          transform: `translate(${dx}px, ${dy}px) scale(${1.8 + Math.random() * 1.4}) rotate(${(Math.random() - 0.5) * 140}deg)`,
          opacity: 0,
        },
      ],
      {
        duration: 1200 + Math.random() * 1000,
        delay: Math.random() * 120,
        easing: "cubic-bezier(0.22, 1, 0.36, 1)",
        fill: "backwards",
      },
    );
    animation.onfinish = () => puff.remove();
    animation.oncancel = () => puff.remove();
  }
}

export default function ClickSmoke() {
  const layerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const layer = layerRef.current;
    const target = layer?.parentElement;
    if (!layer || !target) return;

    function handlePointerDown(e: PointerEvent) {
      if (e.button !== 0 || prefersReducedMotion()) return;
      const rect = layer!.getBoundingClientRect();
      spawnSmoke(layer!, e.clientX - rect.left, e.clientY - rect.top);
    }

    target.addEventListener("pointerdown", handlePointerDown);
    return () => {
      target.removeEventListener("pointerdown", handlePointerDown);
      layer.replaceChildren();
    };
  }, []);

  return <div ref={layerRef} className={styles.layer} aria-hidden="true" />;
}
