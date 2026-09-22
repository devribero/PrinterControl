"use client";

/**
 * Registro/edição de Print Server.
 *
 * O estado do formulário mora AQUI, e o componente é montado pelo pai só
 * enquanto o diálogo está aberto (com key estável por servidor). Isso evita
 * o bug antigo do campo que perdia o foco a cada tecla: nada de componente
 * definido dentro do render do pai, e digitar só re-renderiza este diálogo.
 * O Modal por sua vez guarda `onClose` numa ref (ver Modal.tsx).
 */
import { useState } from "react";
import { Loader2 } from "lucide-react";
import Modal from "../Modal";
import type { PrintServer, Unit } from "../../types";
import { formInicial, useServerAdmin, type ServerFormState } from "./useServerAdmin";
import shared from "./shared.module.css";

const MODOS: { value: "mock" | "real"; label: string; hint: string }[] = [
  { value: "mock", label: "Simulado", hint: "Frota fictícia, sem tocar a rede. Bom para testar." },
  {
    value: "real",
    label: "Real",
    hint: "Consulta o Print Server de verdade via PowerShell/SNMP. Sincroniza sozinho ao cadastrar e a cada 6 h.",
  },
];

interface ServerFormModalProps {
  /** null = registrando um servidor novo. */
  server: PrintServer | null;
  units: Unit[];
  onClose: () => void;
}

export default function ServerFormModal({ server, units, onClose }: ServerFormModalProps) {
  const { save } = useServerAdmin();
  const [form, setForm] = useState<ServerFormState>(() => formInicial(server));
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const editing = server;

  async function salvar() {
    setSaving(true);
    setError(null);
    const falha = await save(editing, form);
    setSaving(false);
    if (falha) setError(falha);
    else onClose();
  }

  return (
    <Modal
      open
      onClose={() => (saving ? undefined : onClose())}
      title={editing ? "Editar Print Server" : "Novo Print Server"}
      subtitle={editing ? editing.host : "O host é a chave do servidor e não muda depois."}
      maxWidth="30rem"
      footer={
        <div className={shared.dialogFooter}>
          <button type="button" onClick={onClose} disabled={saving} className={shared.secondaryButton}>
            Cancelar
          </button>
          <button type="submit" form="server-form" disabled={saving} className={shared.primaryButton}>
            {saving ? <Loader2 size={15} className="animate-spin" /> : null}
            {editing ? "Salvar alterações" : "Registrar"}
          </button>
        </div>
      }
    >
      <form
        id="server-form"
        className={shared.form}
        onSubmit={(e) => {
          e.preventDefault();
          if (!saving) void salvar();
        }}
        noValidate
      >
        <label className={shared.field}>
          <span className={shared.label}>Host</span>
          <input
            type="text"
            value={form.host}
            onChange={(e) => setForm((f) => ({ ...f, host: e.target.value }))}
            className={shared.input}
            placeholder="SRV-IMPRESSAO01"
            // Mesmo valor de `printers.server`: trocá-lo desligaria em
            // silêncio todas as impressoras do servidor. O backend recusa.
            disabled={editing !== null}
            autoComplete="off"
            autoCapitalize="none"
            spellCheck={false}
          />
          <span className={shared.hint}>
            {editing
              ? "O host não pode ser alterado — é a chave que liga as impressoras a este servidor."
              : "Nome de rede usado no -ComputerName do PowerShell. Precisa ser único."}
          </span>
        </label>

        <label className={shared.field}>
          <span className={shared.label}>Rótulo (opcional)</span>
          <input
            type="text"
            value={form.name}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            className={shared.input}
            placeholder={form.host.trim() || "Como este servidor aparece no painel"}
            autoComplete="off"
          />
          <span className={shared.hint}>Em branco, o painel mostra o próprio host.</span>
        </label>

        <label className={shared.field}>
          <span className={shared.label}>Modo</span>
          <select
            value={form.mode}
            onChange={(e) => setForm((f) => ({ ...f, mode: e.target.value === "real" ? "real" : "mock" }))}
            className={shared.select}
          >
            {MODOS.map((m) => (
              <option key={m.value} value={m.value}>
                {m.label}
              </option>
            ))}
          </select>
          <span className={shared.hint}>{MODOS.find((m) => m.value === form.mode)?.hint}</span>
        </label>

        <label className={shared.field}>
          <span className={shared.label}>Unidade</span>
          <select
            value={form.unitId === null ? "" : String(form.unitId)}
            onChange={(e) => setForm((f) => ({ ...f, unitId: e.target.value === "" ? null : Number(e.target.value) }))}
            className={shared.select}
          >
            <option value="">Sem unidade</option>
            {units.map((u) => (
              <option key={u.id} value={u.id}>
                {u.active ? u.name : `${u.name} (desativada)`}
              </option>
            ))}
          </select>
          <span className={shared.hint}>
            {units.length === 0
              ? "Nenhuma unidade cadastrada ainda — crie em Configurações › Unidades."
              : "Quem é desta unidade abre o painel já filtrado nos servidores dela."}
          </span>
        </label>

        {/* Trocar para simulado num servidor com frota cadastrada é a mesma
            armadilha do sync em modo mock: o próximo sync desativa tudo que
            o simulador não publica. */}
        {editing && form.mode === "mock" && editing.mode === "real" && editing.printerCount > 0 && (
          <p className={shared.confirmWarn}>
            Este servidor tem <strong>{editing.printerCount}</strong> impressora(s) cadastrada(s). Em modo
            simulado, o próximo <strong>Sincronizar</strong> marcaria como inativas todas as que o
            simulador não publicar.
          </p>
        )}

        {error && <p className={shared.formError}>{error}</p>}
      </form>
    </Modal>
  );
}
