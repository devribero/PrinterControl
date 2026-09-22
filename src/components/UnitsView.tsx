"use client";

/**
 * Gestao de unidades (rota "/units"), somente admin.
 *
 * Uma unidade agrupa Print Servers (cada servidor em no maximo uma) e
 * usuarios (cada pessoa em no maximo uma). Ela NAO restringe o que alguem
 * enxerga: decide o escopo com que o painel abre e para onde vao os alertas
 * daquela regiao, via webhook proprio do Teams.
 *
 * A URL do webhook e segredo (carrega assinatura). O backend nunca a
 * devolve — so `webhook_configured` e o host — entao o campo abre sempre
 * vazio: vazio mantem, preenchido troca, e remover e uma acao explicita.
 *
 * Servidores e usuarios sao associados nas telas deles (Mapeamento de rede
 * e Usuarios); aqui so aparecem contados.
 *
 * Dependencias externas: react e lucide-react. Locais: Modal, lib/api,
 * lib/apiErrors, lib/toast, lib/webhookTest.
 */
import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Building2, Loader2, Pencil, Plus, RefreshCw, Send, Trash2 } from "lucide-react";
import {
  createUnit,
  deleteUnit,
  listUnits,
  testUnitWebhook,
  updateUnit,
  type UnitUpdateInput,
} from "../lib/api";
import { adaptUnit } from "../lib/adaptApi";
import { useApiErrorReporter } from "../lib/apiErrors";
import { useAppData } from "../lib/app-data";
import { useToast } from "../lib/toast";
import { avisoDoTesteDeUnidade } from "../lib/webhookTest";
import { cn } from "../lib/cn";
import Modal from "./Modal";
import type { Unit } from "../types";
import styles from "./UnitsView.module.css";

interface FormState {
  name: string;
  /** Nova URL digitada. Vazio = manter a atual (na edicao). */
  webhookUrl: string;
  /** Remocao explicita do webhook atual, enviada como `webhook_url: ""`. */
  removerWebhook: boolean;
}

const FORM_VAZIO: FormState = { name: "", webhookUrl: "", removerWebhook: false };

function plural(n: number, um: string, varios: string): string {
  return `${n} ${n === 1 ? um : varios}`;
}

export default function UnitsView() {
  const { refreshUnits } = useAppData();
  const { push } = useToast();
  const relatarErro = useApiErrorReporter();

  const [units, setUnits] = useState<Unit[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  // Criacao/edicao. `editing` null = criando.
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<Unit | null>(null);
  const [form, setForm] = useState<FormState>(FORM_VAZIO);
  const [formError, setFormError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const [testando, setTestando] = useState<number | null>(null);
  const [alternando, setAlternando] = useState<number | null>(null);

  const [deleting, setDeleting] = useState<Unit | null>(null);
  const [deletingBusy, setDeletingBusy] = useState(false);

  /**
   * Lista propria da tela (e nao so a do AppDataProvider) para poder mostrar
   * o erro: o provider carrega em silencio de proposito, e o admin precisa
   * saber quando o backend recusou ou nao tem o recurso.
   */
  const carregar = useCallback(async () => {
    setLoading(true);
    try {
      setUnits((await listUnits()).map(adaptUnit));
      setLoadError(null);
    } catch (error) {
      setUnits(null);
      setLoadError(relatarErro(error, "Falha ao carregar unidades"));
    } finally {
      setLoading(false);
    }
  }, [relatarErro]);

  useEffect(() => {
    void carregar();
  }, [carregar]);

  /** Depois de qualquer mudanca: esta tela e o resto do painel (seletor de escopo). */
  const recarregarTudo = useCallback(async () => {
    await Promise.all([carregar(), refreshUnits()]);
  }, [carregar, refreshUnits]);

  function abrirCriacao() {
    setEditing(null);
    setForm(FORM_VAZIO);
    setFormError(null);
    setDialogOpen(true);
  }

  function abrirEdicao(unit: Unit) {
    setEditing(unit);
    setForm({ name: unit.name, webhookUrl: "", removerWebhook: false });
    setFormError(null);
    setDialogOpen(true);
  }

  function validar(): string | null {
    if (!form.name.trim()) return "Informe o nome da unidade.";
    const url = form.webhookUrl.trim();
    if (url && !url.toLowerCase().startsWith("https://")) return "A URL do webhook precisa começar com https://.";
    return null;
  }

  async function salvar() {
    const invalido = validar();
    if (invalido) {
      setFormError(invalido);
      return;
    }

    setSaving(true);
    setFormError(null);
    const url = form.webhookUrl.trim();
    try {
      if (editing) {
        const mudancas: UnitUpdateInput = {};
        if (form.name.trim() !== editing.name) mudancas.name = form.name.trim();
        if (form.removerWebhook) mudancas.webhook_url = "";
        else if (url) mudancas.webhook_url = url;

        if (Object.keys(mudancas).length === 0) {
          setDialogOpen(false);
          return;
        }
        const atualizada = await updateUnit(editing.id, mudancas);
        push({ variant: "success", title: "Unidade atualizada", description: atualizada.name });
      } else {
        const criada = await createUnit({ name: form.name.trim(), ...(url ? { webhook_url: url } : {}) });
        push({
          variant: "success",
          title: "Unidade criada",
          description: `${criada.name}. Associe os Print Servers dela no Mapeamento de rede.`,
        });
      }
      setDialogOpen(false);
      await recarregarTudo();
    } catch (error) {
      // 409 (nome duplicado) e 422 (URL invalida) ficam no formulario.
      setFormError(relatarErro(error, "Não foi possível salvar"));
    } finally {
      setSaving(false);
    }
  }

  async function testar(unit: Unit) {
    setTestando(unit.id);
    try {
      push(avisoDoTesteDeUnidade(await testUnitWebhook(unit.id), unit.name));
    } catch (error) {
      relatarErro(error, "Não foi possível testar o webhook");
    } finally {
      setTestando(null);
    }
  }

  async function alternarAtiva(unit: Unit) {
    setAlternando(unit.id);
    try {
      const atualizada = await updateUnit(unit.id, { active: !unit.active });
      push({
        variant: "success",
        title: atualizada.active ? "Unidade reativada" : "Unidade desativada",
        description: atualizada.active
          ? `${unit.name} voltou ao seletor de escopo do painel.`
          : `${unit.name} sai do seletor de escopo. Servidores e usuários continuam associados.`,
      });
      await recarregarTudo();
    } catch (error) {
      relatarErro(error, "Não foi possível alterar a unidade");
    } finally {
      setAlternando(null);
    }
  }

  async function confirmarExclusao() {
    if (!deleting) return;
    setDeletingBusy(true);
    try {
      await deleteUnit(deleting.id);
      push({
        variant: "success",
        title: "Unidade excluída",
        description: `${deleting.name} foi removida. Servidores e usuários dela ficaram sem unidade.`,
      });
      setDeleting(null);
      await recarregarTudo();
    } catch (error) {
      relatarErro(error, "Não foi possível excluir");
    } finally {
      setDeletingBusy(false);
    }
  }

  const webhookAtual = editing?.webhookConfigured && !form.removerWebhook;

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <p className={styles.subtitle}>
          {units
            ? `${plural(units.length, "unidade cadastrada", "unidades cadastradas")} · alertas de cada uma vão ao webhook dela e ao canal central`
            : "Carregando unidades..."}
        </p>
        <div className={styles.controls}>
          <button onClick={() => void carregar()} disabled={loading} className={styles.secondaryButton}>
            <RefreshCw size={15} className={loading ? "animate-spin" : ""} />
            Atualizar
          </button>
          <button onClick={abrirCriacao} className={styles.primaryButton}>
            <Plus size={15} />
            Nova unidade
          </button>
        </div>
      </div>

      {loadError && !loading && (
        <div className={styles.loadError}>
          <p>{loadError}</p>
          <button onClick={() => void carregar()} className={styles.secondaryButton}>
            Tentar novamente
          </button>
        </div>
      )}

      <div className={styles.tableWrap}>
        <table className={styles.table}>
          <thead>
            <tr className={styles.theadRow}>
              <th className={styles.thFirst}>Unidade</th>
              <th className={styles.th}>Print Servers</th>
              <th className={styles.th}>Usuários</th>
              <th className={styles.th}>Notificação no Teams</th>
              <th className={styles.th}>Ações</th>
            </tr>
          </thead>
          <tbody>
            {loading && !units && (
              <tr>
                <td colSpan={5} className={styles.emptyState}>
                  <Loader2 size={16} className="animate-spin" /> Carregando unidades...
                </td>
              </tr>
            )}

            {units?.map((unit) => (
              <tr key={unit.id} className={cn(styles.row, !unit.active && styles.rowInactive)}>
                <td className={styles.tdFirst}>
                  <span className={styles.unitName}>
                    <Building2 size={15} className={styles.unitIcon} />
                    {unit.name}
                  </span>
                  {!unit.active && <span className={styles.tagOff}>desativada</span>}
                </td>
                <td className={styles.td} data-label="Print Servers">
                  {unit.serverHosts.length > 0 ? (
                    <span className={styles.hostList}>
                      {unit.serverHosts.map((host) => (
                        <span key={host} className={styles.hostChip}>
                          {host}
                        </span>
                      ))}
                    </span>
                  ) : (
                    <span className={styles.muted}>Nenhum</span>
                  )}
                </td>
                <td className={styles.td} data-label="Usuários">{unit.userCount}</td>
                <td className={styles.td} data-label="Teams">
                  {unit.webhookConfigured ? (
                    <span className={styles.webhookOn}>
                      Webhook: <span className={styles.webhookHost}>{unit.webhookHost || "configurado"}</span>
                    </span>
                  ) : (
                    <span className={styles.muted}>Sem webhook — só o canal central</span>
                  )}
                </td>
                <td className={cn(styles.td, styles.tdActions)}>
                  <div className={styles.actionsRow}>
                    <button
                      onClick={() => void testar(unit)}
                      disabled={!unit.webhookConfigured || testando === unit.id}
                      className={styles.toggleButton}
                      title={unit.webhookConfigured ? "Enviar um card de teste ao webhook desta unidade" : "Configure um webhook primeiro"}
                    >
                      {testando === unit.id ? <Loader2 size={13} className="animate-spin" /> : <Send size={13} />}
                      Testar webhook
                    </button>
                    <button
                      onClick={() => void alternarAtiva(unit)}
                      disabled={alternando === unit.id}
                      className={cn(styles.toggleButton, unit.active && styles.toggleButtonDanger)}
                      title={unit.active ? "Tirar do seletor de escopo sem desfazer associações" : "Reativar unidade"}
                    >
                      {unit.active ? "Desativar" : "Ativar"}
                    </button>
                    <button onClick={() => abrirEdicao(unit)} className={styles.actionButton} title="Editar" aria-label={`Editar ${unit.name}`}>
                      <Pencil size={15} />
                    </button>
                    <button onClick={() => setDeleting(unit)} className={styles.actionButton} title="Excluir unidade" aria-label={`Excluir ${unit.name}`}>
                      <Trash2 size={15} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}

            {!loading && units && units.length === 0 && (
              <tr>
                <td colSpan={5} className={styles.emptyState}>
                  Nenhuma unidade cadastrada. Sem unidades, todo mundo abre o painel na frota inteira e os
                  alertas vão só para o canal central.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <p className={styles.footnote}>
        Servidores são associados em <Link href="/network">Mapeamento de rede</Link> (Editar, no cartão do
        servidor) e pessoas em <Link href="/users">Usuários</Link>.
      </p>

      <Modal
        open={dialogOpen}
        onClose={() => (saving ? undefined : setDialogOpen(false))}
        title={editing ? "Editar unidade" : "Nova unidade"}
        subtitle={editing ? editing.name : "Ex.: Manaus. Os servidores e as pessoas são associados depois."}
        maxWidth="30rem"
        footer={
          <div className={styles.dialogFooter}>
            <button onClick={() => setDialogOpen(false)} disabled={saving} className={styles.secondaryButton}>
              Cancelar
            </button>
            <button onClick={() => void salvar()} disabled={saving} className={styles.primaryButton}>
              {saving ? <Loader2 size={15} className="animate-spin" /> : null}
              {editing ? "Salvar alterações" : "Criar unidade"}
            </button>
          </div>
        }
      >
        <div className={styles.form}>
          <label className={styles.field}>
            <span className={styles.label}>Nome</span>
            <input
              type="text"
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              className={styles.input}
              placeholder="Manaus"
              autoComplete="off"
            />
          </label>

          <label className={styles.field}>
            <span className={styles.label}>Webhook do Teams (opcional)</span>
            <input
              type="password"
              value={form.webhookUrl}
              onChange={(e) => setForm((f) => ({ ...f, webhookUrl: e.target.value }))}
              className={styles.input}
              placeholder={webhookAtual ? "Configurado — deixe vazio para manter" : "https://..."}
              disabled={form.removerWebhook}
              autoComplete="off"
              spellCheck={false}
            />
            <span className={styles.hint}>
              {webhookAtual
                ? `Hoje os alertas vão para ${editing?.webhookHost || "o webhook configurado"}. Cole uma URL nova para trocar.`
                : "URL do fluxo do Teams (Workflows/Power Automate). Depois de salva, ela não é exibida de novo."}
            </span>
          </label>

          {editing?.webhookConfigured && !form.removerWebhook && (
            <button
              type="button"
              onClick={() => setForm((f) => ({ ...f, webhookUrl: "", removerWebhook: true }))}
              className={styles.inlineDanger}
            >
              Remover webhook
            </button>
          )}

          {form.removerWebhook && (
            <p className={styles.warning}>
              O webhook será removido ao salvar. Os alertas desta unidade passam a ir só para o canal central.{" "}
              <button
                type="button"
                onClick={() => setForm((f) => ({ ...f, removerWebhook: false }))}
                className={styles.inlineLink}
              >
                Desfazer
              </button>
            </p>
          )}

          {formError && <p className={styles.formError}>{formError}</p>}
        </div>
      </Modal>

      <Modal
        open={deleting !== null}
        onClose={() => (deletingBusy ? undefined : setDeleting(null))}
        title="Excluir esta unidade?"
        subtitle={deleting?.name}
        maxWidth="28rem"
        footer={
          <div className={styles.dialogFooter}>
            <button onClick={() => setDeleting(null)} disabled={deletingBusy} className={styles.secondaryButton}>
              Cancelar
            </button>
            <button
              onClick={() => void confirmarExclusao()}
              disabled={deletingBusy}
              className={cn(styles.primaryButton, styles.dangerButton)}
            >
              {deletingBusy ? <Loader2 size={15} className="animate-spin" /> : <Trash2 size={15} />}
              Excluir unidade
            </button>
          </div>
        }
      >
        <p className={styles.confirmText}>
          {deleting && (
            <>
              {plural(deleting.serverCount, "Print Server fica", "Print Servers ficam")} e{" "}
              {plural(deleting.userCount, "usuário fica", "usuários ficam")} sem unidade. Nenhum servidor,
              impressora ou conta é apagado — só a unidade e o webhook dela.
            </>
          )}
        </p>
        <p className={styles.confirmText}>
          Pessoas sem unidade abrem o painel na frota inteira e recebem os alertas de todos os servidores,
          como a TI central.
        </p>
      </Modal>
    </div>
  );
}
