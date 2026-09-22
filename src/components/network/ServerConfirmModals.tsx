"use client";

/**
 * Confirmações das ações sensíveis sobre um Print Server. Cada diálogo é
 * montado pelo pai só enquanto aberto e guarda o próprio estado (ocupado,
 * erro, texto digitado) — ver a nota de foco em ServerFormModal.
 */
import { useState } from "react";
import { Loader2, Power, RefreshCw, Trash2 } from "lucide-react";
import Modal from "../Modal";
import type { PrintServer } from "../../types";
import { useServerAdmin } from "./useServerAdmin";
import shared from "./shared.module.css";

interface ConfirmProps {
  server: PrintServer;
  onClose: () => void;
}

/** Desativar (exclusão lógica) ou reativar. */
export function ToggleServerModal({ server, onClose }: ConfirmProps) {
  const { toggleActive } = useServerAdmin();
  const [busy, setBusy] = useState(false);
  const desativando = server.active;

  async function confirmar() {
    setBusy(true);
    await toggleActive(server);
    // Sucesso ou erro, fecha: o erro já saiu em toast e não há o que corrigir aqui.
    setBusy(false);
    onClose();
  }

  return (
    <Modal
      open
      onClose={() => (busy ? undefined : onClose())}
      title={desativando ? "Desativar este Print Server?" : "Reativar este Print Server?"}
      subtitle={server.host}
      maxWidth="28rem"
      footer={
        <div className={shared.dialogFooter}>
          <button type="button" onClick={onClose} disabled={busy} className={shared.secondaryButton}>
            Cancelar
          </button>
          <button
            type="button"
            onClick={() => void confirmar()}
            disabled={busy}
            className={desativando ? shared.dangerButton : shared.primaryButton}
          >
            {busy ? <Loader2 size={15} className="animate-spin" /> : <Power size={15} />}
            {desativando ? "Desativar" : "Reativar"}
          </button>
        </div>
      }
    >
      {desativando ? (
        <>
          <p className={shared.confirmText}>
            Descoberta e sincronização (inclusive a automática) deixam de rodar contra{" "}
            <strong>{server.host}</strong>. O registro e o histórico permanecem — é exclusão lógica.
          </p>
          <p className={shared.confirmText}>
            As <strong>{server.printerCount}</strong> impressora(s) já cadastradas continuam no banco e no
            painel; elas só param de ser atualizadas por este servidor.
          </p>
        </>
      ) : (
        <p className={shared.confirmText}>
          <strong>{server.host}</strong> volta a aceitar descoberta e sincronização. Nada é gravado agora — a
          próxima sincronização é que atualiza o cadastro.
        </p>
      )}
    </Modal>
  );
}

/** Exclusão definitiva — exige digitar o host. */
export function DeleteServerModal({ server, onClose }: ConfirmProps) {
  const { remove } = useServerAdmin();
  const [text, setText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const confere = text.trim() === server.host;

  async function confirmar() {
    if (!confere || busy) return;
    setBusy(true);
    setError(null);
    const falha = await remove(server, text);
    setBusy(false);
    if (falha) setError(falha);
    else onClose();
  }

  return (
    <Modal
      open
      onClose={() => (busy ? undefined : onClose())}
      title="Excluir este Print Server em definitivo?"
      subtitle={server.host}
      maxWidth="28rem"
      footer={
        <div className={shared.dialogFooter}>
          <button type="button" onClick={onClose} disabled={busy} className={shared.secondaryButton}>
            Cancelar
          </button>
          <button
            type="button"
            onClick={() => void confirmar()}
            disabled={busy || !confere}
            className={shared.dangerButton}
          >
            {busy ? <Loader2 size={15} className="animate-spin" /> : <Trash2 size={15} />}
            Excluir em definitivo
          </button>
        </div>
      }
    >
      <p className={shared.confirmText}>
        Esta ação <strong>não pode ser desfeita</strong>. Diferente de <em>Desativar</em>, o registro some
        junto com <strong>{server.printerCount}</strong> impressora(s) cadastrada(s) neste servidor — e as
        leituras, alertas e histórico de toner delas.
      </p>
      <label className={shared.field}>
        <span className={shared.label}>
          Digite <strong>{server.host}</strong> para confirmar
        </span>
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") void confirmar();
          }}
          className={shared.input}
          placeholder={server.host}
          autoComplete="off"
          autoCapitalize="none"
          spellCheck={false}
        />
      </label>
      {error && <p className={shared.formError}>{error}</p>}
    </Modal>
  );
}

interface SyncConfirmProps extends ConfirmProps {
  onConfirm: (server: PrintServer) => void;
}

/**
 * Sincronizar grava no banco. A execução em si roda fora do diálogo (ver
 * useServerSync) para o usuário poder seguir usando a página.
 */
export function SyncConfirmModal({ server, onClose, onConfirm }: SyncConfirmProps) {
  return (
    <Modal
      open
      onClose={onClose}
      title="Sincronizar este Print Server agora?"
      subtitle={server.host}
      maxWidth="28rem"
      footer={
        <div className={shared.dialogFooter}>
          <button type="button" onClick={onClose} className={shared.secondaryButton}>
            Cancelar
          </button>
          <button
            type="button"
            onClick={() => {
              onClose();
              onConfirm(server);
            }}
            className={shared.primaryButton}
          >
            <RefreshCw size={15} />
            Sincronizar
          </button>
        </div>
      }
    >
      <p className={shared.confirmText}>
        Esta ação <strong>altera o cadastro</strong>: filas novas são criadas, as existentes atualizadas e as
        que não aparecerem mais no servidor são marcadas como inativas.
      </p>
      <p className={shared.confirmText}>
        Nada é apagado — leituras e alertas são preservados, e uma impressora inativa volta a ficar ativa se
        reaparecer. Apenas <strong>{server.host}</strong> é afetado.
        {server.mode === "real" && " Servidores reais já sincronizam sozinhos a cada 6 h; use isto só para não esperar o próximo ciclo."}
      </p>

      {/* Sincronizar um servidor em modo simulado contra um cadastro real
          desativa tudo que o simulador não publica. O usuário precisa saber
          ANTES de clicar. */}
      {server.mode === "mock" && server.activePrinterCount > 0 && (
        <p className={shared.confirmWarn}>
          <strong>Atenção:</strong> este servidor está em modo <strong>simulado</strong>. O simulador publica
          uma frota fictícia, então as <strong>{server.activePrinterCount}</strong> impressoras ativas que não
          aparecerem nele serão marcadas como <strong>inativas</strong> e sumirão do painel. Elas voltam ao
          sincronizar com o servidor em modo real.
        </p>
      )}
    </Modal>
  );
}
