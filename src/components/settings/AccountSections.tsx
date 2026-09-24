"use client";

/**
 * Seções de conta: Perfil e Segurança (senha).
 *
 * O backend escopa as duas pela sessão (`/api/auth/me`,
 * `/api/auth/change-password` não recebem id). Só o nome é editável: o
 * e-mail é o `sub` do JWT (trocá-lo invalidaria a própria sessão, e o
 * backend recusa), e perfil de acesso e unidade são decisões de admin.
 */
import { useState, type FormEvent } from "react";
import Link from "next/link";
import { Check, Eye, EyeOff, KeyRound, Loader2, LogOut } from "lucide-react";
import { changeMyPassword, logoutAllSessions, updateMyProfile, type Account } from "../../lib/auth";
import { useApiErrorReporter } from "../../lib/apiErrors";
import { useAppData } from "../../lib/app-data";
import { ROLE_LABELS } from "../../lib/permissions";
import { useToast } from "../../lib/toast";
import styles from "../SettingsView.module.css";
import { Card, Fact, FactList, Field } from "./ui";

/** Mesmo mínimo do backend (`new_password: Field(min_length=8)`). */
const SENHA_MINIMA = 8;

export function ProfileSection({ account }: { account: Account }) {
  const { applyAccountUpdate } = useAppData();
  const { push } = useToast();
  const relatarErro = useApiErrorReporter();

  const [nome, setNome] = useState(account.name);
  const [tocado, setTocado] = useState(false);
  const [salvando, setSalvando] = useState(false);
  const [erroServidor, setErroServidor] = useState<string | null>(null);

  const nomeLimpo = nome.trim();
  const erroNome = nomeLimpo.length === 0 ? "Informe seu nome." : null;
  const mudou = nomeLimpo !== account.name;

  async function salvar(e: FormEvent) {
    e.preventDefault();
    setTocado(true);
    if (erroNome || !mudou) return;
    setSalvando(true);
    setErroServidor(null);
    try {
      const atualizada = await updateMyProfile(nomeLimpo);
      applyAccountUpdate(atualizada);
      setNome(atualizada.name);
      setTocado(false);
      push({ variant: "success", title: "Perfil atualizado", description: "Seu nome já aparece no painel." });
    } catch (error) {
      setErroServidor(relatarErro(error, "Não foi possível salvar o perfil"));
    } finally {
      setSalvando(false);
    }
  }

  return (
    <>
      <form onSubmit={(e) => void salvar(e)} noValidate>
        <Card
          title="Nome de exibição"
          description="Aparece no cabeçalho e nas ações que você registra."
          footer={
            <>
              {mudou && !salvando && (
                <button
                  type="button"
                  onClick={() => {
                    setNome(account.name);
                    setTocado(false);
                    setErroServidor(null);
                  }}
                  className={styles.secondaryButton}
                >
                  Descartar
                </button>
              )}
              <button type="submit" disabled={!mudou || salvando} className={styles.primaryButton}>
                {salvando ? <Loader2 size={16} className="animate-spin" /> : <Check size={16} />}
                {salvando ? "Salvando..." : "Salvar nome"}
              </button>
            </>
          }
        >
          <Field label="Nome" error={tocado ? erroNome : null}>
            {(props) => (
              <input
                {...props}
                type="text"
                value={nome}
                onChange={(e) => setNome(e.target.value)}
                onBlur={() => setTocado(true)}
                className={styles.input}
                autoComplete="name"
                placeholder="Seu nome"
              />
            )}
          </Field>
          {erroServidor && (
            <p className={styles.formError} role="alert">
              {erroServidor}
            </p>
          )}
        </Card>
      </form>

      <Card
        title="Dados da conta"
        description="Definidos por um administrador. Se algo estiver errado, peça a correção em Usuários."
        readOnly
      >
        <FactList>
          <Fact
            label="E-mail"
            value={<span className={styles.breakable}>{account.email}</span>}
            hint="Identifica sua conta no login e não pode ser alterado."
          />
          {account.username && <Fact label="Usuário de login" value={account.username} />}
          <Fact
            label="Perfil de acesso"
            value={ROLE_LABELS[account.role]}
            hint={
              <>
                Só um administrador altera, em <Link href="/users">Usuários</Link>.
              </>
            }
          />
          <Fact
            label="Unidade"
            value={account.unitName ?? "Nenhuma (TI central)"}
            hint="O painel abre filtrado nos servidores da sua unidade. Dá para trocar no seletor do Dashboard."
          />
        </FactList>
      </Card>
    </>
  );
}

type CampoSenha = "atual" | "nova" | "confirma";

export function PasswordSection() {
  const { push } = useToast();
  const relatarErro = useApiErrorReporter();

  const [atual, setAtual] = useState("");
  const [nova, setNova] = useState("");
  const [confirma, setConfirma] = useState("");
  const [mostrar, setMostrar] = useState(false);
  const [tocados, setTocados] = useState<Record<CampoSenha, boolean>>({ atual: false, nova: false, confirma: false });
  const [salvando, setSalvando] = useState(false);
  const [erroServidor, setErroServidor] = useState<string | null>(null);

  const erros: Record<CampoSenha, string | null> = {
    atual: atual ? null : "Informe a senha atual.",
    nova:
      nova.length < SENHA_MINIMA
        ? `Use pelo menos ${SENHA_MINIMA} caracteres.`
        : nova === atual
          ? "A nova senha precisa ser diferente da atual."
          : null,
    confirma: confirma === nova && confirma ? null : "Repita exatamente a nova senha.",
  };
  const valido = !erros.atual && !erros.nova && !erros.confirma;
  const tocar = (campo: CampoSenha) => setTocados((t) => ({ ...t, [campo]: true }));

  async function enviar(e: FormEvent) {
    e.preventDefault();
    setTocados({ atual: true, nova: true, confirma: true });
    if (!valido) return;

    setSalvando(true);
    setErroServidor(null);
    try {
      await changeMyPassword(atual, nova);
      setAtual("");
      setNova("");
      setConfirma("");
      setTocados({ atual: false, nova: false, confirma: false });
      push({
        variant: "success",
        title: "Senha alterada",
        description: "As sessões em outros dispositivos foram encerradas.",
      });
    } catch (error) {
      // 400 (senha atual errada / nova igual à atual) e 422 (curta demais)
      // ficam no formulário, onde dá para corrigir.
      setErroServidor(relatarErro(error, "Não foi possível alterar a senha"));
    } finally {
      setSalvando(false);
    }
  }

  const tipo = mostrar ? "text" : "password";
  const faltam = Math.max(0, SENHA_MINIMA - nova.length);

  return (
    <form onSubmit={(e) => void enviar(e)} noValidate>
      <Card
        title="Alterar senha"
        description="Pedimos a senha atual para que ninguém troque a sua a partir de uma sessão esquecida aberta."
        footer={
          <button type="submit" disabled={salvando} className={styles.primaryButton}>
            {salvando ? <Loader2 size={16} className="animate-spin" /> : <KeyRound size={16} />}
            {salvando ? "Alterando..." : "Alterar senha"}
          </button>
        }
      >
        <Field label="Senha atual" error={tocados.atual ? erros.atual : null}>
          {(props) => (
            <input
              {...props}
              type={tipo}
              value={atual}
              onChange={(e) => setAtual(e.target.value)}
              onBlur={() => tocar("atual")}
              className={styles.input}
              autoComplete="current-password"
            />
          )}
        </Field>

        <div className={styles.fieldRow}>
          <Field
            label="Nova senha"
            error={tocados.nova ? erros.nova : null}
            hint={
              faltam > 0
                ? `Mínimo de ${SENHA_MINIMA} caracteres${nova ? ` (faltam ${faltam})` : ""}.`
                : "Tamanho mínimo atingido."
            }
          >
            {(props) => (
              <input
                {...props}
                type={tipo}
                value={nova}
                onChange={(e) => setNova(e.target.value)}
                onBlur={() => tocar("nova")}
                className={styles.input}
                autoComplete="new-password"
              />
            )}
          </Field>

          <Field label="Confirmar nova senha" error={tocados.confirma ? erros.confirma : null}>
            {(props) => (
              <input
                {...props}
                type={tipo}
                value={confirma}
                onChange={(e) => setConfirma(e.target.value)}
                onBlur={() => tocar("confirma")}
                className={styles.input}
                autoComplete="new-password"
              />
            )}
          </Field>
        </div>

        <button type="button" onClick={() => setMostrar((m) => !m)} className={styles.textButton} aria-pressed={mostrar}>
          {mostrar ? <EyeOff size={16} /> : <Eye size={16} />}
          {mostrar ? "Ocultar senhas" : "Mostrar senhas"}
        </button>

        {/* A troca encerra as outras sessões de fato, via User.token_version (QA-04). */}
        <p className={styles.note}>
          Ao trocar a senha, as sessões abertas em outros dispositivos são encerradas. Esta continua conectada.
        </p>

        {erroServidor && (
          <p className={styles.formError} role="alert">
            {erroServidor}
          </p>
        )}
      </Card>
    </form>
  );
}

/**
 * "Sair de todos os dispositivos": derruba no servidor todo token emitido
 * para a conta (inclusive o desta aba) e volta para o login. É o caminho
 * para quando um computador ficou logado em algum lugar ou o token pode ter
 * vazado — sem precisar trocar a senha.
 */
export function SessionsSection() {
  const { handleLogout } = useAppData();
  const relatarErro = useApiErrorReporter();
  const [saindo, setSaindo] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  async function sairDeTodos() {
    if (!window.confirm("Encerrar a sessão em todos os dispositivos, inclusive neste?")) return;
    setSaindo(true);
    setErro(null);
    try {
      await logoutAllSessions();
      handleLogout();
    } catch (error) {
      setErro(relatarErro(error, "Não foi possível encerrar as sessões"));
      setSaindo(false);
    }
  }

  return (
    <Card
      title="Sessões"
      description="Encerra o acesso em todos os computadores e celulares onde esta conta está conectada."
      footer={
        <button type="button" onClick={() => void sairDeTodos()} disabled={saindo} className={styles.secondaryButton}>
          {saindo ? <Loader2 size={16} className="animate-spin" /> : <LogOut size={16} />}
          {saindo ? "Encerrando..." : "Sair de todos os dispositivos"}
        </button>
      }
    >
      <p className={styles.note}>Use se esqueceu a conta aberta em outra máquina. Você precisará entrar de novo.</p>
      {erro && (
        <p className={styles.formError} role="alert">
          {erro}
        </p>
      )}
    </Card>
  );
}
