"use client";

/**
 * Seletor do escopo do painel — o controle que decide de qual unidade ou
 * Print Server o painel esta falando.
 *
 * O estado nao e daqui: mora no AppDataProvider (`serverScope`), porque a
 * escolha vale para o painel inteiro, nao so para a tela que mostra o
 * botao. Este componente e apenas a interface dela, e por isso pode
 * aparecer em mais de um lugar sem risco de as duas copias divergirem.
 *
 * Ordem das opcoes: a unidade da pessoa (quando ela tem uma), as demais
 * unidades, cada servidor, "Sem servidor" e por fim "Todos". A unidade vem
 * primeiro porque e o escopo com que o painel abre para quem tem uma.
 *
 * Nao renderiza nada quando nao ha servidor registrado (modo demonstracao,
 * sessao sem backend): oferecer um filtro de servidor sobre uma frota que
 * nao veio de servidor nenhum so confundiria.
 *
 * Dependencias externas: react e lucide-react.
 */
import { useEffect, useRef, useState, type ReactNode } from "react";
import { Building2, Check, ChevronDown, Layers, Server, Unplug } from "lucide-react";
import { useAppData } from "../lib/app-data";
import { parseUnitScope, rotularEscopo, unitScope } from "../lib/serverScope";
import { cn } from "../lib/cn";
import styles from "./ServerSwitcher.module.css";

interface OpcaoProps {
  selected: boolean;
  icon: ReactNode;
  title: ReactNode;
  meta: ReactNode;
  onSelect: () => void;
}

/** Uma linha do dropdown. Fora do componente para manter identidade estavel. */
function Opcao({ selected, icon, title, meta, onSelect }: OpcaoProps) {
  return (
    <button
      type="button"
      role="option"
      aria-selected={selected}
      onClick={onSelect}
      className={cn(styles.item, selected && styles.itemActive)}
    >
      <span className={styles.itemIcon}>{icon}</span>
      <span className={styles.itemBody}>
        <span className={styles.itemTitle}>{title}</span>
        <span className={styles.itemMeta}>{meta}</span>
      </span>
      {selected && <Check size={15} className={styles.itemCheck} />}
    </button>
  );
}

function plural(n: number, um: string, varios: string): string {
  return `${n} ${n === 1 ? um : varios}`;
}

export default function ServerSwitcher({ className }: { className?: string }) {
  const {
    account,
    servers,
    units,
    serverScope,
    setServerScope,
    serverCounts,
    unitCounts,
    allActiveCount,
    usingRealData,
  } = useAppData();
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

  const unidadeEmFoco = parseUnitScope(serverScope);
  const minhaUnidade =
    account?.unitId != null ? (units.find((u) => u.id === account.unitId) ?? null) : null;
  // Unidade desativada so aparece se for a que esta em foco: some da lista
  // sem tirar a pessoa do escopo em que ela esta.
  const outrasUnidades = units.filter(
    (u) => u.id !== minhaUnidade?.id && (u.active || u.id === unidadeEmFoco),
  );
  // So aparece quando existe: impressora cadastrada a mao e excecao, e uma
  // opcao permanente que quase sempre da zero seria ruido.
  const semServidor = serverCounts[""] ?? 0;

  function escolher(escopo: string | null) {
    setServerScope(escopo);
    setOpen(false);
  }

  const rotuloAtual = rotularEscopo(serverScope, servers, units);
  const contagemAtual =
    serverScope === null
      ? allActiveCount
      : unidadeEmFoco !== null
        ? (unitCounts[unidadeEmFoco] ?? 0)
        : (serverCounts[serverScope] ?? 0);
  const iconeAtual =
    serverScope === null ? <Layers size={15} /> : unidadeEmFoco !== null ? <Building2 size={15} /> : <Server size={15} />;

  const metaUnidade = (id: number, servidores: number) =>
    `${plural(servidores, "servidor", "servidores")} · ${unitCounts[id] ?? 0} ativa(s)`;

  return (
    <div className={cn(styles.anchor, className)} ref={ref}>
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className={styles.trigger}
        aria-haspopup="listbox"
        aria-expanded={open}
        title="Escolher de qual unidade ou Print Server o painel fala"
      >
        {iconeAtual}
        <span className={styles.triggerText}>
          <span className={styles.triggerLabel}>{unidadeEmFoco !== null ? "Unidade" : "Servidor"}</span>
          <span className={styles.triggerValue}>{rotuloAtual}</span>
        </span>
        {/* A contagem so descreve a realidade quando a frota e real; no modo
            demonstracao o escopo nem chega a ser aplicado. */}
        {usingRealData && <span className={styles.triggerCount}>{contagemAtual}</span>}
        <ChevronDown size={14} className={cn(styles.chevron, open && styles.chevronOpen)} />
      </button>

      {/* Véu só visível no celular, onde a lista vira uma folha inferior. */}
      {open && <div className={styles.scrim} onClick={() => setOpen(false)} aria-hidden="true" />}

      {open && (
        <div className={styles.dropdown} role="listbox">
          <div className={styles.sheetHandle} aria-hidden="true" />
          <p className={styles.dropdownHint}>O painel inteiro passa a falar do escopo escolhido.</p>

          {minhaUnidade && (
            <Opcao
              selected={unidadeEmFoco === minhaUnidade.id}
              icon={<Building2 size={15} />}
              title={
                <>
                  Minha unidade ({minhaUnidade.name})
                  {!minhaUnidade.active && <span className={styles.tagOff}>desativada</span>}
                </>
              }
              meta={metaUnidade(minhaUnidade.id, minhaUnidade.serverCount)}
              onSelect={() => escolher(unitScope(minhaUnidade.id))}
            />
          )}

          {outrasUnidades.map((unit) => (
            <Opcao
              key={unit.id}
              selected={unidadeEmFoco === unit.id}
              icon={<Building2 size={15} />}
              title={
                <>
                  {unit.name}
                  {!unit.active && <span className={styles.tagOff}>desativada</span>}
                </>
              }
              meta={metaUnidade(unit.id, unit.serverCount)}
              onSelect={() => escolher(unitScope(unit.id))}
            />
          ))}

          {(minhaUnidade || outrasUnidades.length > 0) && <div className={styles.separator} />}

          {servers.map((server) => (
            <Opcao
              key={server.id}
              selected={server.host === serverScope}
              icon={<Server size={15} />}
              title={
                <>
                  {server.name}
                  {!server.active && <span className={styles.tagOff}>desativado</span>}
                </>
              }
              meta={
                <>
                  {server.host}
                  {server.unitName ? ` · ${server.unitName}` : ""} · {serverCounts[server.host] ?? 0} ativa(s)
                </>
              }
              onSelect={() => escolher(server.host)}
            />
          ))}

          {semServidor > 0 && (
            // Estas nao aparecem em NENHUM escopo de servidor; sem esta
            // opcao elas so seriam visiveis em "Todos".
            <Opcao
              selected={serverScope === ""}
              icon={<Unplug size={15} />}
              title="Sem servidor"
              meta={`${semServidor} ativa(s) fora de qualquer Print Server`}
              onSelect={() => escolher("")}
            />
          )}

          <div className={styles.separator} />

          <Opcao
            selected={serverScope === null}
            icon={<Layers size={15} />}
            title="Todos os servidores"
            meta={`${allActiveCount} impressora(s) ativa(s)`}
            onSelect={() => escolher(null)}
          />
        </div>
      )}
    </div>
  );
}
