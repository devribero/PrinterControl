"use client";

/**
 * Dependências externas: react (useEffect, para o listener de Escape) e
 * lucide-react (ícone de fechar). Modal genérico reutilizável — quem monta
 * o conteúdo é o caller (ver PrinterDetailsModal.tsx e o modal de Ajuda em
 * AppShell.tsx); este componente só cuida de overlay, Escape e clique fora.
 *
 * `maxWidth` agora é um valor de CSS (ex.: "36rem"), não mais uma classe
 * Tailwind — callers que passavam "max-w-xl" etc. precisam passar o rem
 * equivalente (max-w-lg=32rem, max-w-xl=36rem, max-w-2xl=42rem).
 */
import { useEffect, useRef, type ReactNode } from "react";
import { X } from "lucide-react";
import styles from "./Modal.module.css";

/**
 * Elementos que recebem foco por Tab. `:not([disabled])` e `tabindex="-1"`
 * ficam de fora porque nenhum dos dois entra na ordem de tabulação.
 */
const FOCAVEIS =
  'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), ' +
  'select:not([disabled]), [tabindex]:not([tabindex="-1"])';

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  subtitle?: string;
  children: ReactNode;
  footer?: ReactNode;
  maxWidth?: string;
}

export default function Modal({ open, onClose, title, subtitle, children, footer, maxWidth = "32rem" }: ModalProps) {
  const dialogRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;

    /**
     * QA-15: contenção de foco. Sem isto, o Tab a partir do último botão do
     * diálogo saía para o que estava ATRÁS dele — na auditoria, para o
     * NEXTJS-PORTAL. Quem navega só pelo teclado ficava operando a página de
     * baixo achando que ainda estava no modal, com `aria-modal="true"`
     * afirmando o contrário.
     *
     * O ciclo é feito à mão (e não com uma biblioteca) porque é só isto: a
     * lista de focáveis é relida a cada Tab, então conteúdo que aparece ou
     * some enquanto o diálogo está aberto entra no ciclo sem nenhum registro.
     */
    function handleKey(e: KeyboardEvent) {
      if (e.key === "Escape") {
        onClose();
        return;
      }
      if (e.key !== "Tab" || !dialogRef.current) return;

      const focaveis = Array.from(
        dialogRef.current.querySelectorAll<HTMLElement>(FOCAVEIS),
      ).filter((el) => el.offsetParent !== null);
      if (focaveis.length === 0) return;

      const primeiro = focaveis[0];
      const ultimo = focaveis[focaveis.length - 1];
      const atual = document.activeElement;

      // Foco fora do diálogo (ou nele mesmo) volta para dentro em vez de
      // deixar o Tab escapar para a página de baixo.
      if (!dialogRef.current.contains(atual)) {
        e.preventDefault();
        (e.shiftKey ? ultimo : primeiro).focus();
        return;
      }
      if (!e.shiftKey && atual === ultimo) {
        e.preventDefault();
        primeiro.focus();
      } else if (e.shiftKey && atual === primeiro) {
        e.preventDefault();
        ultimo.focus();
      }
    }

    // Devolve o foco a quem abriu o diálogo ao fechar: sem isto ele volta
    // para o <body> e a próxima tabulação recomeça do topo da página.
    const anterior = document.activeElement as HTMLElement | null;
    dialogRef.current?.querySelector<HTMLElement>(FOCAVEIS)?.focus();

    document.addEventListener("keydown", handleKey);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", handleKey);
      document.body.style.overflow = "";
      anterior?.focus?.();
    };
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className={styles.overlay}>
      <div className={`${styles.backdrop} animate-overlay-in`} onClick={onClose} aria-hidden="true" />
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        className={`${styles.dialog} animate-modal-in`}
        style={{ maxWidth }}
      >
        <div className={styles.header}>
          <div>
            <h2 id="modal-title" className={styles.title}>
              {title}
            </h2>
            {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
          </div>
          <button onClick={onClose} className={styles.closeButton} aria-label="Fechar">
            <X size={18} />
          </button>
        </div>
        <div className={styles.body}>{children}</div>
        {footer && <div className={styles.footer}>{footer}</div>}
      </div>
    </div>
  );
}
