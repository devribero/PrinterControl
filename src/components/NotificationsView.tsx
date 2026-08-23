"use client";

/**
 * Caixa pessoal de notificações (rota "/notifications", Fase 8).
 *
 * A distinção que esta tela precisa preservar, e que é a razão de a Fase 7
 * ter criado uma tabela separada:
 *
 *   ALERTA       -> evento técnico de uma impressora. Nasce sozinho do
 *                   alert_engine, resolve-se sozinho, ninguém "lê".
 *                   Continua vivendo em /alerts e no sino do cabeçalho.
 *   NOTIFICAÇÃO  -> mensagem dirigida a uma pessoa, com leitura individual.
 *                   É o que esta tela mostra.
 *
 * Uma notificação PODE citar um alerta (`alertId`), mas carrega a própria
 * mensagem: resolver o alerta não reescreve o que a pessoa recebeu. Por isso
 * o vínculo aparece como um selo de referência, nunca como o conteúdo.
 *
 * O contador de não lidas vive no AppDataProvider, não aqui: o badge do
 * cabeçalho depende do mesmo número, e marcar como lida precisa atualizar os
 * dois ao mesmo tempo.
 *
 * Dependências externas: react, next/link e lucide-react. Locais: Modal
 * (mesmo diálogo do resto do painel), lib/api, lib/adaptApi, lib/apiErrors.
 */
import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import {
  Inbox,
  RefreshCw,
  Loader2,
  Send,
  Check,
  CheckCheck,
  CircleAlert,
  TriangleAlert,
  Info,
  Link2,
} from "lucide-react";
import {
  createNotifications,
  fetchNotifications,
  fetchUsers,
  markAllNotificationsRead,
  markNotificationRead,
  type ApiUser,
} from "../lib/api";
import { adaptNotification } from "../lib/adaptApi";
import { useApiErrorReporter } from "../lib/apiErrors";
import { useAppData } from "../lib/app-data";
import { useToast } from "../lib/toast";
import { cn } from "../lib/cn";
import Modal from "./Modal";
import type { Notification } from "../types";
import styles from "./NotificationsView.module.css";

type Severidade = "info" | "warning" | "critical";

const SEVERIDADES: { value: Severidade; label: string }[] = [
  { value: "info", label: "Informativa" },
  { value: "warning", label: "Atenção" },
  { value: "critical", label: "Crítica" },
];

const ICONE_SEVERIDADE = {
  info: Info,
  warning: CircleAlert,
  critical: TriangleAlert,
} as const;

interface FormState {
  userIds: number[];
  message: string;
  severity: Severidade;
  /** Texto livre: vira `alert_id` numérico só se preenchido. */
  alertId: string;
}

const FORM_VAZIO: FormState = { userIds: [], message: "", severity: "info", alertId: "" };

function formatarMomento(iso: string): string {
  const data = new Date(iso);
  if (Number.isNaN(data.getTime())) return "—";
  return data.toLocaleString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function NotificationsView() {
  const { can, refreshUnreadNotifications } = useAppData();
  const { push } = useToast();
  // 401 desloga, 403 não — regra da Fase 2, compartilhada com as demais telas.
  const relatarErro = useApiErrorReporter();

  const [items, setItems] = useState<Notification[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [somenteNaoLidas, setSomenteNaoLidas] = useState(false);
  const [marcando, setMarcando] = useState<number | null>(null);
  const [marcandoTodas, setMarcandoTodas] = useState(false);

  // Envio (admin).
  const [dialogOpen, setDialogOpen] = useState(false);
  const [form, setForm] = useState<FormState>(FORM_VAZIO);
  const [formError, setFormError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);
  const [usuarios, setUsuarios] = useState<ApiUser[] | null>(null);

  const carregar = useCallback(async () => {
    setLoading(true);
    try {
      const data = (await fetchNotifications({ unreadOnly: somenteNaoLidas })).map(adaptNotification);
      setItems(data);
      setLoadError(null);
    } catch (error) {
      setItems(null);
      setLoadError(relatarErro(error, "Falha ao carregar as notificações"));
    } finally {
      setLoading(false);
    }
  }, [relatarErro, somenteNaoLidas]);

  useEffect(() => {
    void carregar();
  }, [carregar]);

  const naoLidas = useMemo(() => (items ?? []).filter((n) => n.readAt === null).length, [items]);

  async function marcarComoLida(n: Notification) {
    if (n.readAt !== null) return;
    setMarcando(n.id);
    try {
      const atualizada = adaptNotification(await markNotificationRead(n.id));
      if (somenteNaoLidas) {
        // O filtro está ativo: uma vez lida, ela sai da lista.
        setItems((atuais) => (atuais ?? []).filter((x) => x.id !== atualizada.id));
      } else {
        setItems((atuais) => (atuais ?? []).map((x) => (x.id === atualizada.id ? atualizada : x)));
      }
      // O badge do cabeçalho lê o mesmo contador global.
      void refreshUnreadNotifications();
    } catch (error) {
      relatarErro(error, "Não foi possível marcar como lida");
    } finally {
      setMarcando(null);
    }
  }

  async function marcarTodasComoLidas() {
    setMarcandoTodas(true);
    try {
      const { marked } = await markAllNotificationsRead();
      push({
        variant: "success",
        title: marked > 0 ? "Caixa em dia" : "Nada a marcar",
        description:
          marked > 0
            ? `${marked} notificação(ões) marcada(s) como lida(s).`
            : "Todas as suas notificações já estavam lidas.",
      });
      // Recarrega em vez de mexer no estado local: com o filtro "só não
      // lidas" ativo a lista fica vazia, e sem ele cada item precisa exibir
      // o read_at que o backend acabou de gravar.
      await carregar();
      void refreshUnreadNotifications();
    } catch (error) {
      relatarErro(error, "Não foi possível marcar todas como lidas");
    } finally {
      setMarcandoTodas(false);
    }
  }

  async function abrirEnvio() {
    setForm(FORM_VAZIO);
    setFormError(null);
    setDialogOpen(true);
    if (usuarios) return;
    try {
      // /api/users exige admin — só chega aqui quem já passou por can.canAdmin.
      setUsuarios(await fetchUsers());
    } catch (error) {
      setFormError(relatarErro(error, "Falha ao carregar os destinatários"));
    }
  }

  function alternarDestinatario(id: number) {
    setForm((f) => ({
      ...f,
      userIds: f.userIds.includes(id) ? f.userIds.filter((x) => x !== id) : [...f.userIds, id],
    }));
  }

  function validar(): string | null {
    if (form.userIds.length === 0) return "Escolha ao menos um destinatário.";
    if (!form.message.trim()) return "Escreva a mensagem.";
    if (form.alertId.trim() && !/^\d+$/.test(form.alertId.trim())) {
      return "O ID do alerta deve ser um número.";
    }
    return null;
  }

  async function enviar() {
    const invalido = validar();
    if (invalido) {
      setFormError(invalido);
      return;
    }

    setEnviando(true);
    setFormError(null);
    try {
      const criadas = await createNotifications({
        user_ids: form.userIds,
        message: form.message.trim(),
        severity: form.severity,
        alert_id: form.alertId.trim() ? Number(form.alertId.trim()) : null,
      });
      push({
        variant: "success",
        title: "Notificação enviada",
        description: `${criadas.length} destinatário(s). Cada um lê a sua.`,
      });
      setDialogOpen(false);
      // O remetente normalmente não é destinatário, mas pode ter se incluído.
      void carregar();
      void refreshUnreadNotifications();
    } catch (error) {
      // 404 (destinatário/alerta inexistente), 409 (conta desativada) e 422
      // ficam no formulário, onde dá para corrigir sem perder o que digitou.
      setFormError(relatarErro(error, "Não foi possível enviar"));
    } finally {
      setEnviando(false);
    }
  }

  const ativos = useMemo(() => (usuarios ?? []).filter((u) => u.is_active), [usuarios]);

  return (
    <div className={styles.page}>
      <section className={styles.card}>
        <div className={styles.cardHeader}>
          <div>
            <h2 className={styles.cardTitle}>Notificações</h2>
            <p className={styles.cardSubtitle}>
              {items
                ? somenteNaoLidas
                  ? `${items.length} não lida(s)`
                  : `${items.length} na sua caixa · ${naoLidas} não lida(s)`
                : "Carregando..."}
            </p>
          </div>

          <div className={styles.headerActions}>
            <label className={styles.toggle}>
              <input
                type="checkbox"
                checked={somenteNaoLidas}
                onChange={(e) => setSomenteNaoLidas(e.target.checked)}
                className={styles.checkbox}
              />
              Só não lidas
            </label>
            {naoLidas > 0 && (
              <button
                onClick={() => void marcarTodasComoLidas()}
                disabled={marcandoTodas}
                className={styles.secondaryButton}
                title="Marcar todas as suas notificações como lidas"
              >
                {marcandoTodas ? (
                  <Loader2 size={15} className="animate-spin" />
                ) : (
                  <CheckCheck size={15} />
                )}
                Marcar todas como lidas
              </button>
            )}
            <button onClick={() => void carregar()} disabled={loading} className={styles.secondaryButton}>
              <RefreshCw size={15} className={loading ? "animate-spin" : ""} />
              Atualizar
            </button>
            {can.canAdmin && (
              <button onClick={() => void abrirEnvio()} className={styles.primaryButton}>
                <Send size={15} />
                Nova notificação
              </button>
            )}
          </div>
        </div>

        {loadError && !loading && <p className={styles.errorBox}>{loadError}</p>}

        {loading && !items && (
          <p className={styles.emptyState}>
            <Loader2 size={16} className="animate-spin" /> Carregando notificações...
          </p>
        )}

        {items && items.length === 0 && (
          <p className={styles.emptyState}>
            <Inbox size={18} />
            {somenteNaoLidas ? "Nenhuma notificação não lida." : "Sua caixa está vazia."}
          </p>
        )}

        {items && items.length > 0 && (
          <ul className={styles.list}>
            {items.map((n) => {
              const Icone = ICONE_SEVERIDADE[n.severity] ?? Info;
              const lida = n.readAt !== null;

              return (
                <li key={n.id} className={cn(styles.item, !lida && styles.itemUnread)}>
                  <Icone
                    size={17}
                    className={cn(
                      styles.itemIcon,
                      n.severity === "critical" && styles.iconCritical,
                      n.severity === "warning" && styles.iconWarning,
                      n.severity === "info" && styles.iconInfo,
                    )}
                  />

                  <div className={styles.itemBody}>
                    <p className={cn(styles.itemMessage, !lida && styles.itemMessageUnread)}>
                      {n.message}
                    </p>

                    <div className={styles.itemMeta}>
                      <span>{formatarMomento(n.createdAt)}</span>

                      {lida ? (
                        <span className={styles.metaRead}>lida em {formatarMomento(n.readAt!)}</span>
                      ) : (
                        <span className={styles.metaUnread}>não lida</span>
                      )}

                      {/* Vínculo com o alerta: referência, não conteúdo. Se o
                          alerta não existir mais, `alert` vem null e só o id
                          é exibido — a notificação continua legível. */}
                      {n.alertId !== null && (
                        <Link href="/alerts" className={styles.alertLink} title="Ver o histórico de alertas">
                          <Link2 size={12} />
                          Alerta #{n.alertId}
                          {n.alert ? (
                            <span
                              className={cn(
                                styles.alertState,
                                n.alert.resolved ? styles.alertResolved : styles.alertOpen,
                              )}
                            >
                              {n.alert.resolved ? "resolvido" : "aberto"}
                            </span>
                          ) : (
                            <span className={cn(styles.alertState, styles.alertGone)}>não encontrado</span>
                          )}
                        </Link>
                      )}
                    </div>
                  </div>

                  {!lida && (
                    <button
                      onClick={() => void marcarComoLida(n)}
                      disabled={marcando === n.id}
                      className={styles.readButton}
                      title="Marcar como lida"
                    >
                      {marcando === n.id ? (
                        <Loader2 size={14} className="animate-spin" />
                      ) : (
                        <Check size={14} />
                      )}
                      Marcar como lida
                    </button>
                  )}
                </li>
              );
            })}
          </ul>
        )}

        <p className={styles.footnote}>
          Isto é a sua caixa pessoal. O histórico técnico da frota — impressora
          offline, toner acabando — continua em <Link href="/alerts">Alertas</Link> e no sino do
          cabeçalho.
        </p>
      </section>

      <Modal
        open={dialogOpen}
        onClose={() => (enviando ? undefined : setDialogOpen(false))}
        title="Nova notificação"
        subtitle="Cada destinatário recebe a sua, com leitura independente."
        maxWidth="32rem"
        footer={
          <div className={styles.dialogFooter}>
            <button onClick={() => setDialogOpen(false)} disabled={enviando} className={styles.secondaryButton}>
              Cancelar
            </button>
            <button onClick={() => void enviar()} disabled={enviando} className={styles.primaryButton}>
              {enviando ? <Loader2 size={15} className="animate-spin" /> : <Send size={15} />}
              Enviar
            </button>
          </div>
        }
      >
        <div className={styles.form}>
          <div className={styles.field}>
            <span className={styles.label}>
              Destinatários {form.userIds.length > 0 && `(${form.userIds.length})`}
            </span>

            {!usuarios && !formError && (
              <p className={styles.hint}>
                <Loader2 size={13} className="animate-spin" /> Carregando contas...
              </p>
            )}

            {usuarios && (
              <div className={styles.recipientList}>
                {ativos.map((u) => (
                  <label key={u.id} className={styles.recipient}>
                    <input
                      type="checkbox"
                      checked={form.userIds.includes(u.id)}
                      onChange={() => alternarDestinatario(u.id)}
                      className={styles.checkbox}
                    />
                    <span className={styles.recipientName}>{u.name}</span>
                    <span className={styles.recipientEmail}>{u.email}</span>
                  </label>
                ))}
                {ativos.length === 0 && <p className={styles.hint}>Nenhuma conta ativa.</p>}
              </div>
            )}
            {/* Conta desativada nunca abriria a caixa — o backend recusa com
                409, então ela nem aparece na lista. */}
            {usuarios && usuarios.length > ativos.length && (
              <span className={styles.hint}>
                {usuarios.length - ativos.length} conta(s) desativada(s) não aparecem: elas não
                recebem notificação.
              </span>
            )}
          </div>

          <label className={styles.field}>
            <span className={styles.label}>Mensagem</span>
            <textarea
              value={form.message}
              onChange={(e) => setForm((f) => ({ ...f, message: e.target.value }))}
              className={styles.textarea}
              rows={3}
              placeholder="O que os destinatários precisam saber"
            />
          </label>

          <label className={styles.field}>
            <span className={styles.label}>Importância</span>
            <select
              value={form.severity}
              onChange={(e) => setForm((f) => ({ ...f, severity: e.target.value as Severidade }))}
              className={styles.select}
            >
              {SEVERIDADES.map((s) => (
                <option key={s.value} value={s.value}>
                  {s.label}
                </option>
              ))}
            </select>
            <span className={styles.hint}>Define só o ícone e a cor na caixa de quem recebe.</span>
          </label>

          <label className={styles.field}>
            <span className={styles.label}>Alerta relacionado (opcional)</span>
            <input
              type="text"
              inputMode="numeric"
              value={form.alertId}
              onChange={(e) => setForm((f) => ({ ...f, alertId: e.target.value }))}
              className={styles.input}
              placeholder="ID do alerta, ex.: 42"
            />
            <span className={styles.hint}>
              Vira um link na notificação. A mensagem acima continua sendo o conteúdo — resolver o
              alerta depois não reescreve o que foi enviado.
            </span>
          </label>

          {formError && <p className={styles.formError}>{formError}</p>}
        </div>
      </Modal>
    </div>
  );
}
