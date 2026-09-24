"use client";

/**
 * E-mail: situação do SMTP, teste de envio e QUEM RECEBE. Só para admin.
 *
 * O servidor e a senha ficam no backend/.env — a senha nunca passa pelo
 * painel. Os destinatários, sim: são cadastrados aqui (GET/POST/DELETE
 * /api/notifications/email-recipients) e somam às listas fixas do .env
 * (ALERT_EMAIL_TO / REPORT_EMAIL_TO), que aparecem só para leitura.
 *
 *   Alertas de toner  -> cada e-mail vale para TODAS as impressoras ou só
 *                        para as de uma unidade.
 *   Relatório mensal  -> um só para a empresa (o levantamento é único).
 */
import { useEffect, useState, type FormEvent } from "react";
import { Loader2, Mail, Plus, Trash2 } from "lucide-react";
import {
  addEmailRecipient,
  fetchEmailRecipients,
  fetchEmailStatus,
  removeEmailRecipient,
  sendTestEmail,
  type ApiEmailRecipient,
  type ApiEmailStatus,
  type EmailRecipientKind,
} from "../../lib/api";
import { useApiErrorReporter } from "../../lib/apiErrors";
import { useAppData } from "../../lib/app-data";
import { useToast } from "../../lib/toast";
import styles from "../SettingsView.module.css";
import { Card, Fact, FactList, Field, StatusPill } from "./ui";

/** Por que o e-mail não saiu, em linguagem de quem vai corrigir o .env. */
function motivoFalhaEmail(detail: string): string {
  switch (detail) {
    case "nao_configurado":
      return "O e-mail está desligado: preencha SMTP_HOST no backend/.env e reinicie o backend.";
    case "autenticacao":
      return "O servidor recusou o login. Contas do Outlook/Microsoft não aceitam mais só senha — é preciso conectar com a conta Microsoft (OAuth2).";
    case "recusado":
      return "O servidor aceitou o login mas recusou a mensagem (remetente ou destinatário não permitido).";
    case "timeout":
      return "O servidor SMTP não respondeu a tempo. Confira SMTP_HOST e SMTP_PORT.";
    default:
      return "Não foi possível conectar ao servidor SMTP (rede, firewall ou porta bloqueada).";
  }
}

const TODAS = "todas";

export function EmailSection({ defaultTo }: { defaultTo: string }) {
  const [status, setStatus] = useState<ApiEmailStatus | null>(null);
  const [destinatarios, setDestinatarios] = useState<ApiEmailRecipient[] | null>(null);
  const [erroCarga, setErroCarga] = useState<string | null>(null);

  useEffect(() => {
    const controle = new AbortController();
    fetchEmailStatus(controle.signal)
      .then(setStatus)
      .catch(() => setStatus(null));
    fetchEmailRecipients(controle.signal)
      .then(setDestinatarios)
      .catch((error: unknown) => {
        if (!controle.signal.aborted) setErroCarga(error instanceof Error ? error.message : "Erro ao carregar.");
      });
    return () => controle.abort();
  }, []);

  function adicionado(novo: ApiEmailRecipient) {
    setDestinatarios((lista) => [...(lista ?? []), novo]);
  }

  function removido(id: number) {
    setDestinatarios((lista) => (lista ?? []).filter((r) => r.id !== id));
  }

  return (
    <>
      <StatusCard status={status} defaultTo={defaultTo} />
      <RecipientsCard
        kind="alert"
        title="Quem recebe os alertas de toner"
        description="Um e-mail a cada toner que chega no nível crítico. Escolha se a pessoa recebe de todas as impressoras ou só das de uma unidade."
        itens={destinatarios}
        doEnv={status?.env_alert_recipients ?? []}
        erroCarga={erroCarga}
        onAdicionado={adicionado}
        onRemovido={removido}
      />
      <RecipientsCard
        kind="report"
        title="Quem recebe o relatório mensal"
        description="Uma vez por mês, quando o levantamento é gerado: resumo no corpo do e-mail e a planilha em anexo."
        itens={destinatarios}
        doEnv={status?.env_report_recipients ?? []}
        erroCarga={erroCarga}
        onAdicionado={adicionado}
        onRemovido={removido}
      />
    </>
  );
}

function StatusCard({ status, defaultTo }: { status: ApiEmailStatus | null; defaultTo: string }) {
  const { push } = useToast();
  const relatarErro = useApiErrorReporter();
  const [destino, setDestino] = useState(defaultTo);
  const [enviando, setEnviando] = useState(false);
  const [falha, setFalha] = useState<string | null>(null);

  async function testar(e: FormEvent) {
    e.preventDefault();
    setEnviando(true);
    setFalha(null);
    try {
      const r = await sendTestEmail(destino.trim() || undefined);
      if (r.sent) {
        push({ variant: "success", title: "E-mail de teste enviado", description: `Confira a caixa de ${r.to}.` });
      } else {
        setFalha(motivoFalhaEmail(r.detail));
      }
    } catch (error) {
      setFalha(relatarErro(error, "Não foi possível enviar o teste"));
    } finally {
      setEnviando(false);
    }
  }

  return (
    <form onSubmit={(e) => void testar(e)} noValidate>
      <Card
        title="E-mail"
        description="Conta que envia os e-mails. O servidor e a senha ficam no backend/.env, nunca no painel."
        footer={
          <button type="submit" disabled={enviando} className={styles.secondaryButton}>
            {enviando ? <Loader2 size={16} className="animate-spin" /> : <Mail size={16} />}
            {enviando ? "Enviando..." : "Enviar e-mail de teste"}
          </button>
        }
      >
        <FactList>
          <Fact
            label="Situação"
            value={
              status === null ? (
                "Carregando..."
              ) : status.configured ? (
                <StatusPill tone="ok">Ligado</StatusPill>
              ) : (
                <StatusPill tone="neutral">Desligado</StatusPill>
              )
            }
            hint={status?.configured ? <span className={styles.mono}>{status.smtp_host}</span> : "Preencha SMTP_HOST no backend/.env."}
          />
          {status?.configured && <Fact label="Remetente" value={status.sender || "—"} />}
        </FactList>

        <Field label="Enviar o teste para">
          {(props) => (
            <input
              {...props}
              type="email"
              value={destino}
              onChange={(e) => setDestino(e.target.value)}
              className={styles.input}
              autoComplete="email"
            />
          )}
        </Field>

        {falha && (
          <p className={styles.formError} role="alert">
            {falha}
          </p>
        )}
      </Card>
    </form>
  );
}

function RecipientsCard({
  kind,
  title,
  description,
  itens,
  doEnv,
  erroCarga,
  onAdicionado,
  onRemovido,
}: {
  kind: EmailRecipientKind;
  title: string;
  description: string;
  itens: ApiEmailRecipient[] | null;
  doEnv: string[];
  erroCarga: string | null;
  onAdicionado: (r: ApiEmailRecipient) => void;
  onRemovido: (id: number) => void;
}) {
  const { units } = useAppData();
  const { push } = useToast();
  const relatarErro = useApiErrorReporter();
  const [email, setEmail] = useState("");
  const [unidade, setUnidade] = useState(TODAS);
  const [salvando, setSalvando] = useState(false);
  const [removendo, setRemovendo] = useState<number | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  const daLista = (itens ?? []).filter((r) => r.kind === kind);
  const comUnidade = kind === "alert";

  async function adicionar(e: FormEvent) {
    e.preventDefault();
    const limpo = email.trim();
    if (!limpo.includes("@")) {
      setErro("Informe um endereço de e-mail válido.");
      return;
    }
    setSalvando(true);
    setErro(null);
    try {
      const unitId = comUnidade && unidade !== TODAS ? Number(unidade) : null;
      onAdicionado(await addEmailRecipient(limpo, kind, unitId));
      setEmail("");
    } catch (error) {
      setErro(relatarErro(error, "Não foi possível adicionar"));
    } finally {
      setSalvando(false);
    }
  }

  async function remover(r: ApiEmailRecipient) {
    setRemovendo(r.id);
    try {
      await removeEmailRecipient(r.id);
      onRemovido(r.id);
      push({ variant: "success", title: "Removido", description: `${r.email} não recebe mais estes e-mails.` });
    } catch (error) {
      setErro(relatarErro(error, "Não foi possível remover"));
    } finally {
      setRemovendo(null);
    }
  }

  return (
    <form onSubmit={(e) => void adicionar(e)} noValidate>
      <Card
        title={title}
        description={description}
        footer={
          <button type="submit" disabled={salvando} className={styles.secondaryButton}>
            {salvando ? <Loader2 size={16} className="animate-spin" /> : <Plus size={16} />}
            {salvando ? "Adicionando..." : "Adicionar"}
          </button>
        }
      >
        {itens === null && !erroCarga && <p className={styles.note}>Carregando...</p>}
        {erroCarga && <p className={styles.formError}>{erroCarga}</p>}

        {itens !== null && daLista.length === 0 && doEnv.length === 0 && (
          <p className={styles.note}>Ninguém recebe ainda. Adicione o primeiro e-mail abaixo.</p>
        )}

        {(daLista.length > 0 || doEnv.length > 0) && (
          <ul className={styles.itemList}>
            {daLista.map((r) => (
              <li key={r.id} className={styles.item}>
                <div className={styles.itemMain}>
                  <span className={styles.itemTitle}>{r.email}</span>
                  {comUnidade && (
                    <span className={styles.itemMeta}>
                      {r.unit_name ? `Só impressoras de ${r.unit_name}` : "Todas as impressoras"}
                    </span>
                  )}
                </div>
                <button
                  type="button"
                  onClick={() => void remover(r)}
                  disabled={removendo === r.id}
                  className={styles.textButton}
                  aria-label={`Remover ${r.email}`}
                >
                  {removendo === r.id ? <Loader2 size={16} className="animate-spin" /> : <Trash2 size={16} />}
                  Remover
                </button>
              </li>
            ))}
            {doEnv.map((endereco) => (
              <li key={`env-${endereco}`} className={styles.item}>
                <div className={styles.itemMain}>
                  <span className={styles.itemTitle}>{endereco}</span>
                  <span className={styles.itemMeta}>
                    Fixo no backend/.env{comUnidade ? " · todas as impressoras" : ""} — só muda no servidor
                  </span>
                </div>
                <StatusPill tone="neutral">.env</StatusPill>
              </li>
            ))}
          </ul>
        )}

        <div className={comUnidade ? styles.fieldRow : undefined}>
          <Field label="Novo e-mail" error={erro}>
            {(props) => (
              <input
                {...props}
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className={styles.input}
                placeholder="nome@empresa.com.br"
                autoComplete="off"
              />
            )}
          </Field>

          {comUnidade && (
            <Field label="Recebe alertas de">
              {(props) => (
                <select {...props} value={unidade} onChange={(e) => setUnidade(e.target.value)} className={styles.input}>
                  <option value={TODAS}>Todas as impressoras</option>
                  {units
                    .filter((u) => u.active)
                    .map((u) => (
                      <option key={u.id} value={String(u.id)}>
                        Só da unidade {u.name}
                      </option>
                    ))}
                </select>
              )}
            </Field>
          )}
        </div>
      </Card>
    </form>
  );
}
