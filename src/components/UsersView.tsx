"use client";

/**
 * Tela de gestão de contas (rota "/users"). Consome /api/users, que exige
 * admin no backend — o RequireRole da página é só experiência de uso.
 *
 * Os usuários NÃO entram no AppDataProvider de propósito: são dados de uma
 * única tela, visíveis a um único papel. Carregá-los globalmente faria toda
 * sessão viewer/operator disparar uma chamada que sempre voltaria 403.
 *
 * Dependências externas: react e lucide-react (ícones). Locais: Modal
 * (mesmo diálogo do resto do painel), lib/api, lib/permissions, lib/toast.
 */
import { useCallback, useEffect, useMemo, useState } from "react";
import { UserPlus, Pencil, Search, ShieldCheck, Loader2, RefreshCw } from "lucide-react";
import { createUser, fetchUsers, updateUser, type ApiUser, type UserUpdateInput } from "../lib/api";
import { useApiErrorReporter } from "../lib/apiErrors";
import { ROLES, ROLE_LABELS, parseRole, type Role } from "../lib/permissions";
import { useAppData } from "../lib/app-data";
import { useToast } from "../lib/toast";
import { cn } from "../lib/cn";
import Modal from "./Modal";
import styles from "./UsersView.module.css";

/**
 * Estado do formulário do diálogo — criação e edição usam o mesmo.
 *
 * Ativar/desativar NÃO está aqui de propósito: é a ação mais sensível da
 * tela (corta o acesso na hora) e tem o próprio fluxo com confirmação, em
 * vez de virar um campo que se salva junto com uma troca de nome.
 */
interface FormState {
  name: string;
  email: string;
  password: string;
  role: Role;
}

const FORM_VAZIO: FormState = {
  name: "",
  email: "",
  password: "",
  role: "viewer",
};

const SENHA_MINIMA = 8;

function formatarData(iso: string): string {
  const data = new Date(iso);
  return Number.isNaN(data.getTime()) ? "—" : data.toLocaleDateString("pt-BR");
}

export default function UsersView() {
  const { account } = useAppData();
  const { push } = useToast();
  // 401 desloga, 403 nao — regra da Fase 2, compartilhada com as demais
  // telas administrativas (lib/apiErrors.ts).
  const relatarErro = useApiErrorReporter();

  const [users, setUsers] = useState<ApiUser[] | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");

  // Diálogo de criação/edição. `editing` null = criando.
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<ApiUser | null>(null);
  const [form, setForm] = useState<FormState>(FORM_VAZIO);
  const [formError, setFormError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  // Confirmação de ativar/desativar — ação sensível, nunca em um clique só.
  const [confirming, setConfirming] = useState<ApiUser | null>(null);
  const [toggling, setToggling] = useState(false);

  const carregar = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetchUsers();
      setUsers(data);
      setLoadError(null);
    } catch (error) {
      setUsers(null);
      setLoadError(relatarErro(error, "Falha ao carregar usuários"));
    } finally {
      setLoading(false);
    }
  }, [relatarErro]);

  useEffect(() => {
    void carregar();
  }, [carregar]);

  const visiveis = useMemo(() => {
    if (!users) return [];
    const termo = query.trim().toLowerCase();
    if (!termo) return users;
    return users.filter(
      (u) => u.name.toLowerCase().includes(termo) || u.email.toLowerCase().includes(termo),
    );
  }, [users, query]);

  const adminsAtivos = useMemo(
    () => (users ?? []).filter((u) => u.role === "admin" && u.is_active).length,
    [users],
  );

  /** Mesma regra do backend (`_ensure_not_last_admin`), aqui só para avisar antes. */
  function ehUltimoAdmin(user: ApiUser): boolean {
    return user.role === "admin" && user.is_active && adminsAtivos <= 1;
  }

  function abrirCriacao() {
    setEditing(null);
    setForm(FORM_VAZIO);
    setFormError(null);
    setDialogOpen(true);
  }

  function abrirEdicao(user: ApiUser) {
    setEditing(user);
    setForm({
      name: user.name,
      email: user.email,
      password: "",
      role: parseRole(user.role),
    });
    setFormError(null);
    setDialogOpen(true);
  }

  function validar(): string | null {
    if (!form.name.trim()) return "Informe o nome.";
    if (!editing) {
      if (!form.email.trim()) return "Informe o e-mail.";
      if (!form.email.includes("@")) return "E-mail inválido.";
      if (form.password.length < SENHA_MINIMA) return `A senha deve ter ao menos ${SENHA_MINIMA} caracteres.`;
    } else if (form.password && form.password.length < SENHA_MINIMA) {
      return `A senha deve ter ao menos ${SENHA_MINIMA} caracteres.`;
    }
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
    try {
      if (editing) {
        // Só o que mudou — e-mail e id nunca são enviados.
        const mudancas: UserUpdateInput = {};
        if (form.name.trim() !== editing.name) mudancas.name = form.name.trim();
        if (form.role !== editing.role) mudancas.role = form.role;
        if (form.password) mudancas.password = form.password;

        if (Object.keys(mudancas).length === 0) {
          setDialogOpen(false);
          return;
        }

        const atualizado = await updateUser(editing.id, mudancas);
        setUsers((atuais) => (atuais ?? []).map((u) => (u.id === atualizado.id ? atualizado : u)));
        push({ variant: "success", title: "Usuário atualizado", description: atualizado.name });
      } else {
        const criado = await createUser({
          email: form.email.trim(),
          name: form.name.trim(),
          password: form.password,
          role: form.role,
        });
        setUsers((atuais) => [...(atuais ?? []), criado]);
        push({ variant: "success", title: "Usuário criado", description: `${criado.name} (${ROLE_LABELS[parseRole(criado.role)]}).` });
      }
      setDialogOpen(false);
    } catch (error) {
      // 409 (e-mail duplicado / último admin) e 422 (validação) ficam no
      // próprio formulário, onde o admin pode corrigir sem perder o que digitou.
      setFormError(relatarErro(error, "Não foi possível salvar"));
    } finally {
      setSaving(false);
    }
  }

  async function confirmarAtivacao() {
    if (!confirming) return;
    setToggling(true);
    try {
      const atualizado = await updateUser(confirming.id, { is_active: !confirming.is_active });
      setUsers((atuais) => (atuais ?? []).map((u) => (u.id === atualizado.id ? atualizado : u)));
      push({
        variant: "success",
        title: atualizado.is_active ? "Usuário ativado" : "Usuário desativado",
        description: atualizado.is_active
          ? `${atualizado.name} voltou a ter acesso.`
          : `${atualizado.name} perdeu o acesso imediatamente.`,
      });
      setConfirming(null);
    } catch (error) {
      relatarErro(error, "Não foi possível alterar o status");
      setConfirming(null);
    } finally {
      setToggling(false);
    }
  }

  const editandoASiMesmo = editing !== null && account !== null && editing.id === account.id;

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <div>
          <h2 className={styles.title}>Usuários</h2>
          <p className={styles.subtitle}>
            {users ? `${users.length} conta(s) cadastrada(s) · ${adminsAtivos} administrador(es) ativo(s)` : "Carregando contas..."}
          </p>
        </div>

        <div className={styles.controls}>
          <div className={styles.searchBox}>
            <Search size={16} />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Buscar por nome ou e-mail..."
              className={styles.searchInput}
            />
          </div>
          <button onClick={() => void carregar()} disabled={loading} className={styles.secondaryButton}>
            <RefreshCw size={15} className={loading ? "animate-spin" : ""} />
            Atualizar
          </button>
          <button onClick={abrirCriacao} className={styles.primaryButton}>
            <UserPlus size={15} />
            Novo usuário
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
              <th className={styles.thFirst}>Nome</th>
              <th className={styles.th}>E-mail</th>
              <th className={styles.th}>Perfil</th>
              <th className={styles.th}>Status</th>
              <th className={styles.th}>Criado em</th>
              <th className={styles.th}>Ações</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr>
                <td colSpan={6} className={styles.emptyState}>
                  <Loader2 size={16} className="animate-spin" /> Carregando usuários...
                </td>
              </tr>
            )}

            {!loading &&
              visiveis.map((user) => {
                const role = parseRole(user.role);
                return (
                  <tr key={user.id} className={styles.row}>
                    <td className={styles.tdFirst}>
                      <span className={styles.userName}>{user.name}</span>
                      {ehUltimoAdmin(user) && (
                        <span className={styles.lastAdminTag} title="Único administrador ativo do sistema">
                          <ShieldCheck size={12} /> último admin
                        </span>
                      )}
                    </td>
                    <td className={styles.td}>{user.email}</td>
                    <td className={styles.td}>
                      <span className={cn(styles.roleBadge, styles[`role_${role}`])}>{ROLE_LABELS[role]}</span>
                    </td>
                    <td className={styles.td}>
                      <span className={cn(styles.statusBadge, user.is_active ? styles.statusOn : styles.statusOff)}>
                        {user.is_active ? "Ativo" : "Inativo"}
                      </span>
                    </td>
                    <td className={styles.tdMuted}>{formatarData(user.created_at)}</td>
                    <td className={styles.td}>
                      <div className={styles.actionsRow}>
                        <button onClick={() => abrirEdicao(user)} className={styles.actionButton} title="Editar">
                          <Pencil size={15} />
                        </button>
                        <button
                          onClick={() => setConfirming(user)}
                          disabled={ehUltimoAdmin(user)}
                          className={cn(styles.toggleButton, user.is_active && styles.toggleButtonDanger)}
                          title={
                            ehUltimoAdmin(user)
                              ? "É o único administrador ativo — promova outro antes de desativar"
                              : user.is_active
                                ? "Desativar usuário"
                                : "Ativar usuário"
                          }
                        >
                          {user.is_active ? "Desativar" : "Ativar"}
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}

            {!loading && visiveis.length === 0 && (
              <tr>
                <td colSpan={6} className={styles.emptyState}>
                  {users && users.length > 0 ? "Nenhum usuário para esta busca." : "Nenhum usuário cadastrado."}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <Modal
        open={dialogOpen}
        onClose={() => (saving ? undefined : setDialogOpen(false))}
        title={editing ? "Editar usuário" : "Novo usuário"}
        subtitle={editing ? editing.email : "A conta nasce com o perfil escolhido abaixo."}
        maxWidth="30rem"
        footer={
          <div className={styles.dialogFooter}>
            <button onClick={() => setDialogOpen(false)} disabled={saving} className={styles.secondaryButton}>
              Cancelar
            </button>
            <button onClick={() => void salvar()} disabled={saving} className={styles.primaryButton}>
              {saving ? <Loader2 size={15} className="animate-spin" /> : null}
              {editing ? "Salvar alterações" : "Criar usuário"}
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
              placeholder="Nome completo"
            />
          </label>

          <label className={styles.field}>
            <span className={styles.label}>E-mail</span>
            <input
              type="email"
              value={form.email}
              onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
              className={styles.input}
              placeholder="pessoa@empresa.com"
              // O e-mail identifica a conta no JWT; alterá-lo invalidaria a
              // sessão do dono em silêncio, então o backend não aceita a troca.
              disabled={editing !== null}
            />
            {editing && <span className={styles.hint}>O e-mail não pode ser alterado.</span>}
          </label>

          <label className={styles.field}>
            <span className={styles.label}>{editing ? "Nova senha (opcional)" : "Senha inicial"}</span>
            <input
              type="password"
              value={form.password}
              onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
              className={styles.input}
              placeholder={editing ? "Deixe em branco para manter" : `Mínimo de ${SENHA_MINIMA} caracteres`}
              autoComplete="new-password"
            />
          </label>

          <label className={styles.field}>
            <span className={styles.label}>Perfil</span>
            <select
              value={form.role}
              onChange={(e) => setForm((f) => ({ ...f, role: parseRole(e.target.value) }))}
              className={styles.select}
            >
              {ROLES.map((r) => (
                <option key={r} value={r}>
                  {ROLE_LABELS[r]}
                </option>
              ))}
            </select>
            <span className={styles.hint}>
              Administrador gerencia contas e a rede · Operador executa coletas e alertas · Visualização só lê.
            </span>
          </label>

          {editandoASiMesmo && form.role !== "admin" && (
            <p className={styles.warning}>
              Você está alterando o próprio perfil. Ao salvar, perderá o acesso a esta página.
            </p>
          )}

          {formError && <p className={styles.formError}>{formError}</p>}
        </div>
      </Modal>

      <Modal
        open={confirming !== null}
        onClose={() => (toggling ? undefined : setConfirming(null))}
        title={confirming?.is_active ? "Desativar usuário?" : "Ativar usuário?"}
        maxWidth="26rem"
        footer={
          <div className={styles.dialogFooter}>
            <button onClick={() => setConfirming(null)} disabled={toggling} className={styles.secondaryButton}>
              Cancelar
            </button>
            <button
              onClick={() => void confirmarAtivacao()}
              disabled={toggling}
              className={cn(styles.primaryButton, confirming?.is_active && styles.dangerButton)}
            >
              {toggling ? <Loader2 size={15} className="animate-spin" /> : null}
              {confirming?.is_active ? "Desativar" : "Ativar"}
            </button>
          </div>
        }
      >
        <p className={styles.confirmText}>
          {confirming?.is_active ? (
            <>
              <strong>{confirming?.name}</strong> perderá o acesso imediatamente, mesmo que já esteja com uma
              sessão aberta. A conta e o histórico são preservados — basta reativar para devolver o acesso.
            </>
          ) : (
            <>
              <strong>{confirming?.name}</strong> voltará a acessar o painel com o perfil{" "}
              {confirming ? ROLE_LABELS[parseRole(confirming.role)] : ""}.
            </>
          )}
        </p>
      </Modal>
    </div>
  );
}
