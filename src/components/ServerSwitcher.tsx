"use client";

/**
 * Seletor do escopo de servidor — o controle que decide de qual Print
 * Server o painel esta falando.
 *
 * O estado nao e daqui: mora no AppDataProvider (`serverScope`), porque a
 * escolha vale para o painel inteiro, nao so para a tela que mostra o
 * botao. Este componente e apenas a interface dela, e por isso pode
 * aparecer em mais de um lugar sem risco de as duas copias divergirem.
 *
 * Nao renderiza nada quando nao ha servidor registrado (modo demonstracao,
 * sessao sem backend): oferecer um filtro de servidor sobre uma frota que
 * nao veio de servidor nenhum so confundiria.
 *
 * Dependencias externas: react e lucide-react.
 */
import { useEffect, useRef, useState } from "react";
import { Check, ChevronDown, Layers, Server, Unplug } from "lucide-react";
import { useAppData } from "../lib/app-data";
import { cn } from "../lib/cn";
import styles from "./ServerSwitcher.module.css";

/** Rotulo do escopo, no mesmo vocabulario usado no Mapeamento de rede. */
function rotular(escopo: string | null, nome: string | undefined): string {
  if (escopo === null) return "Todos os servidores";
  if (escopo === "") return "Sem servidor";
  return nome ?? escopo;
}

export default function ServerSwitcher({ className }: { className?: string }) {
  const { servers, serverScope, setServerScope, serverCounts, allActiveCount, usingRealData } = useAppData();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    function handleEscape(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }
    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleEscape);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleEscape);
    };
  }, []);

  if (servers.length === 0) return null;

  const selecionado = servers.find((s) => s.host === serverScope) ?? null;
  // So aparece quando existe: impressora cadastrada a mao e excecao, e uma
  // opcao permanente que quase sempre da zero seria ruido.
  const semServidor = serverCounts[""] ?? 0;

  function escolher(escopo: string | null) {
    setServerScope(escopo);
    setOpen(false);
  }

  const rotuloAtual = rotular(serverScope, selecionado?.name);
  const contagemAtual =
    serverScope === null ? allActiveCount : (serverCounts[serverScope] ?? 0);

  return (
    <div className={cn(styles.anchor, className)} ref={ref}>
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className={styles.trigger}
        aria-haspopup="listbox"
        aria-expanded={open}
        title="Escolher de qual Print Server o painel fala"
      >
        {serverScope === null ? <Layers size={15} /> : <Server size={15} />}
        <span className={styles.triggerText}>
          <span className={styles.triggerLabel}>Servidor</span>
          <span className={styles.triggerValue}>{rotuloAtual}</span>
        </span>
        {/* A contagem so descreve a realidade quando a frota e real; no modo
            demonstracao o escopo nem chega a ser aplicado. */}
        {usingRealData && <span className={styles.triggerCount}>{contagemAtual}</span>}
        <ChevronDown size={14} className={cn(styles.chevron, open && styles.chevronOpen)} />
      </button>

      {open && (
        <div className={styles.dropdown} role="listbox">
          <p className={styles.dropdownHint}>O painel inteiro passa a falar do servidor escolhido.</p>

          <button
            type="button"
            role="option"
            aria-selected={serverScope === null}
            onClick={() => escolher(null)}
            className={cn(styles.item, serverScope === null && styles.itemActive)}
          >
            <Layers size={15} className={styles.itemIcon} />
            <span className={styles.itemBody}>
              <span className={styles.itemTitle}>Todos os servidores</span>
              <span className={styles.itemMeta}>{allActiveCount} impressora(s) ativa(s)</span>
            </span>
            {serverScope === null && <Check size={15} className={styles.itemCheck} />}
          </button>

          <div className={styles.separator} />

          {servers.map((server) => (
            <button
              key={server.id}
              type="button"
              role="option"
              aria-selected={server.host === serverScope}
              onClick={() => escolher(server.host)}
              className={cn(styles.item, server.host === serverScope && styles.itemActive)}
            >
              <Server size={15} className={styles.itemIcon} />
              <span className={styles.itemBody}>
                <span className={styles.itemTitle}>
                  {server.name}
                  {!server.active && <span className={styles.tagOff}>desativado</span>}
                </span>
                <span className={styles.itemMeta}>
                  {server.host} · {serverCounts[server.host] ?? 0} ativa(s)
                </span>
              </span>
              {server.host === serverScope && <Check size={15} className={styles.itemCheck} />}
            </button>
          ))}

          {semServidor > 0 && (
            <>
              <div className={styles.separator} />
              <button
                type="button"
                role="option"
                aria-selected={serverScope === ""}
                onClick={() => escolher("")}
                className={cn(styles.item, serverScope === "" && styles.itemActive)}
              >
                <Unplug size={15} className={styles.itemIcon} />
                <span className={styles.itemBody}>
                  <span className={styles.itemTitle}>Sem servidor</span>
                  {/* Estas nao aparecem em NENHUM escopo de servidor; sem
                      esta opcao elas so seriam visiveis em "Todos". */}
                  <span className={styles.itemMeta}>
                    {semServidor} ativa(s) fora de qualquer Print Server
                  </span>
                </span>
                {serverScope === "" && <Check size={15} className={styles.itemCheck} />}
              </button>
            </>
          )}
        </div>
      )}
    </div>
  );
}
