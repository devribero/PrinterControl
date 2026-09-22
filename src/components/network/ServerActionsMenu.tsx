"use client";

/**
 * Menu "⋯" de ações secundárias de um Print Server. A ação principal do
 * cartão é selecionar o servidor (clique no cartão); o resto mora aqui.
 *
 * Menu acessível feito à mão: botão com aria-haspopup/expanded, lista com
 * role="menu", setas/Home/End movem o foco, Escape e clique fora fecham e
 * devolvem o foco ao botão. Abre para cima quando falta espaço embaixo.
 */
import { useEffect, useId, useRef, useState, type KeyboardEvent } from "react";
import { EllipsisVertical, Pencil, Power, RadioTower, RefreshCw, Trash2, type LucideIcon } from "lucide-react";
import { cn } from "../../lib/cn";
import type { PrintServer } from "../../types";
import shared from "./shared.module.css";
import styles from "./ServerGrid.module.css";

export type ServerAction = "edit" | "discover" | "sync" | "toggle" | "delete";

interface ServerActionsMenuProps {
  server: PrintServer;
  onAction: (action: ServerAction, server: PrintServer) => void;
  /** Motivo para Descobrir estar indisponível; null = disponível. */
  discoverBlocked: string | null;
  /** Motivo para Sincronizar estar indisponível; null = disponível. */
  syncBlocked: string | null;
}

interface MenuItem {
  action: ServerAction;
  label: string;
  hint: string;
  icon: LucideIcon;
  danger?: boolean;
  disabled?: boolean;
  separatorBefore?: boolean;
}

const ITEM_SELECTOR = '[role="menuitem"]:not([disabled])';

export default function ServerActionsMenu({ server, onAction, discoverBlocked, syncBlocked }: ServerActionsMenuProps) {
  const [open, setOpen] = useState(false);
  const [openUp, setOpenUp] = useState(false);
  const wrapRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const menuRef = useRef<HTMLDivElement>(null);
  const menuId = useId();

  useEffect(() => {
    if (!open) return;
    function onPointerDown(e: PointerEvent) {
      if (!wrapRef.current?.contains(e.target as Node)) setOpen(false);
    }
    function onKeyDown(e: globalThis.KeyboardEvent) {
      if (e.key === "Escape") {
        e.stopPropagation();
        setOpen(false);
        buttonRef.current?.focus();
      }
    }
    document.addEventListener("pointerdown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);
    menuRef.current?.querySelector<HTMLElement>(ITEM_SELECTOR)?.focus();
    return () => {
      document.removeEventListener("pointerdown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open]);

  function toggle() {
    if (!open && buttonRef.current) {
      const rect = buttonRef.current.getBoundingClientRect();
      setOpenUp(window.innerHeight - rect.bottom < 340 && rect.top > 340);
    }
    setOpen((o) => !o);
  }

  function onMenuKeyDown(e: KeyboardEvent<HTMLDivElement>) {
    if (e.key === "Tab") {
      setOpen(false);
      return;
    }
    if (!["ArrowDown", "ArrowUp", "Home", "End"].includes(e.key)) return;
    e.preventDefault();
    const items = Array.from(menuRef.current?.querySelectorAll<HTMLElement>(ITEM_SELECTOR) ?? []);
    if (items.length === 0) return;
    const atual = items.indexOf(document.activeElement as HTMLElement);
    let proximo = 0;
    if (e.key === "End") proximo = items.length - 1;
    else if (e.key === "ArrowDown") proximo = (atual + 1) % items.length;
    else if (e.key === "ArrowUp") proximo = (atual - 1 + items.length) % items.length;
    items[proximo].focus();
  }

  function choose(action: ServerAction) {
    setOpen(false);
    buttonRef.current?.focus();
    onAction(action, server);
  }

  const items: MenuItem[] = [
    { action: "edit", label: "Editar", hint: "Rótulo, modo e unidade", icon: Pencil },
    {
      action: "discover",
      label: "Descobrir filas",
      hint: discoverBlocked ?? "Pré-visualiza o que o servidor publica. Não grava nada.",
      icon: RadioTower,
      disabled: discoverBlocked !== null,
    },
    {
      action: "sync",
      label: "Sincronizar agora",
      hint: syncBlocked ?? "Aplica ao cadastro: cria, atualiza e desativa filas.",
      icon: RefreshCw,
      disabled: syncBlocked !== null,
    },
    {
      action: "toggle",
      label: server.active ? "Desativar" : "Reativar",
      hint: server.active ? "Para de consultar. Mantém o histórico." : "Volta a aceitar descoberta e sync.",
      icon: Power,
      separatorBefore: true,
    },
    {
      action: "delete",
      label: "Excluir",
      hint: "Apaga o servidor e as impressoras dele.",
      icon: Trash2,
      danger: true,
    },
  ];

  return (
    <div ref={wrapRef} className={styles.menuWrap}>
      <button
        ref={buttonRef}
        type="button"
        className={shared.iconButton}
        aria-haspopup="menu"
        aria-expanded={open}
        aria-controls={open ? menuId : undefined}
        aria-label={`Ações de ${server.host}`}
        onClick={toggle}
      >
        <EllipsisVertical size={18} />
      </button>

      {open && (
        <div
          ref={menuRef}
          id={menuId}
          role="menu"
          aria-label={`Ações de ${server.host}`}
          className={cn(styles.menu, openUp && styles.menuUp)}
          onKeyDown={onMenuKeyDown}
        >
          {items.map((item) => {
            const Icon = item.icon;
            return (
              <div key={item.action} role="none" className={cn(item.separatorBefore && styles.menuSeparator)}>
                <button
                  type="button"
                  role="menuitem"
                  disabled={item.disabled}
                  className={cn(styles.menuItem, item.danger && styles.menuItemDanger)}
                  onClick={() => choose(item.action)}
                >
                  <Icon size={16} className={styles.menuIcon} />
                  <span className={styles.menuText}>
                    <span className={styles.menuLabel}>{item.label}</span>
                    <span className={styles.menuHint}>{item.hint}</span>
                  </span>
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
