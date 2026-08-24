"use client";

/**
 * Configurações (rota "/settings", Fase 8).
 *
 * O problema que esta tela resolve: até aqui `/settings` era um placeholder
 * atrás de `RequireRole role="admin"`. Ou seja, viewer e operator não
 * conseguiam abrir a página das PRÓPRIAS preferências — a tela mais pessoal
 * do painel era a única que a maioria não podia ver.
 *
 * A separação agora é explícita, e é técnica além de visual:
 *
 *   PESSOAL        -> perfil, senha, aparência, acessibilidade. Todo papel
 *                     acessa; o backend escopa pela sessão (`/api/auth/me`,
 *                     `/api/auth/change-password` não recebem id).
 *   ADMINISTRAÇÃO  -> só atalhos para onde a administração de fato vive
 *                     (/users, /network). Nada crítico é editável aqui, e a
 *                     seção nem aparece para quem não é admin.
 *
 * Nenhum secret ou variável de ambiente é exibido: a única informação de
 * infraestrutura mostrada é o endereço público da API, que o navegador já
 * conhece por estar em toda requisição.
 *
 * Dependências externas: react, next/link e lucide-react. Locais: lib/auth
 * (perfil e senha), lib/theme, lib/preferences, lib/apiErrors.
 */
import { useEffect, useState } from "react";
import Link from "next/link";
import {
  User,
  KeyRound,
  Palette,
  Accessibility,
  ShieldCheck,
  Loader2,
  Check,
  Sun,
  Moon,
  Monitor,
  Users,
  Network,
  RotateCcw,
} from "lucide-react";
import { changeMyPassword, updateMyProfile } from "../lib/auth";
import { API_BASE_URL } from "../lib/api";
import { useApiErrorReporter } from "../lib/apiErrors";
import { useAppData } from "../lib/app-data";
import { usePreferences, ESCALAS } from "../lib/preferences";
import { useTheme, type ThemePreference } from "../lib/theme";
import { ROLE_LABELS } from "../lib/permissions";
import { useToast } from "../lib/toast";
import { cn } from "../lib/cn";
import styles from "./SettingsView.module.css";

const SENHA_MINIMA = 8;

const TEMAS: { value: ThemePreference; label: string; icon: typeof Sun; hint: string }[] = [
  { value: "light", label: "Claro", icon: Sun, hint: "Fixo, independente do sistema." },
  { value: "dark", label: "Escuro", icon: Moon, hint: "Fixo, independente do sistema." },
  { value: "system", label: "Sistema", icon: Monitor, hint: "Acompanha o tema do seu computador." },
];

export default function SettingsView() {
  const { account, can, applyAccountUpdate } = useAppData();
  const { theme, preference, setPreference } = useTheme();
  const { preferences, setPreference: setPref, reset, modificado } = usePreferences();
  const { push } = useToast();
  const relatarErro = useApiErrorReporter();

  // ── Perfil ─────────────────────────────────────────────────────────────
  const [nome, setNome] = useState("");
  const [salvandoPerfil, setSalvandoPerfil] = useState(false);
  const [erroPerfil, setErroPerfil] = useState<string | null>(null);

  // ── Senha ──────────────────────────────────────────────────────────────
  const [senhaAtual, setSenhaAtual] = useState("");
  const [senhaNova, setSenhaNova] = useState("");
  const [senhaConfirma, setSenhaConfirma] = useState("");
  const [trocandoSenha, setTrocandoSenha] = useState(false);
  const [erroSenha, setErroSenha] = useState<string | null>(null);

  useEffect(() => {
    setNome(account?.name ?? "");
  }, [account?.name]);

  if (!account) return null;

  const nomeMudou = nome.trim() !== account.name && nome.trim().length > 0;

  async function salvarPerfil() {
    if (!nomeMudou) return;
    setSalvandoPerfil(true);
    setErroPerfil(null);
    try {
      applyAccountUpdate(await updateMyProfile(nome.trim()));
      push({ variant: "success", title: "Perfil atualizado", description: "Seu nome foi alterado." });
    } catch (error) {
      setErroPerfil(relatarErro(error, "Não foi possível salvar o perfil"));
    } finally {
      setSalvandoPerfil(false);
    }
  }

  function validarSenha(): string | null {
    if (!senhaAtual) return "Informe a senha atual.";
    if (senhaNova.length < SENHA_MINIMA) return `A nova senha deve ter ao menos ${SENHA_MINIMA} caracteres.`;
    if (senhaNova === senhaAtual) return "A nova senha precisa ser diferente da atual.";
    if (senhaNova !== senhaConfirma) return "A confirmação não confere com a nova senha.";
    return null;
  }

  async function trocarSenha() {
    const invalido = validarSenha();
    if (invalido) {
      setErroSenha(invalido);
      return;
    }

    setTrocandoSenha(true);
    setErroSenha(null);
    try {
      await changeMyPassword(senhaAtual, senhaNova);
      setSenhaAtual("");
      setSenhaNova("");
      setSenhaConfirma("");
      push({
        variant: "success",
        title: "Senha alterada",
        description: "Use a nova senha no próximo login.",
      });
    } catch (error) {
      // 400 (senha atual errada / nova igual à atual) e 422 (curta demais)
      // ficam aqui no formulário, onde dá para corrigir.
      setErroSenha(relatarErro(error, "Não foi possível alterar a senha"));
    } finally {
      setTrocandoSenha(false);
    }
  }

  return (
    <div className={styles.page}>
      {/* ══ PESSOAL ═══════════════════════════════════════════════════════ */}
      <div className={styles.groupHeader}>
        <h2 className={styles.groupTitle}>Suas preferências</h2>
        <p className={styles.groupSubtitle}>
          Valem só para você. Nada aqui altera o funcionamento do sistema para as outras pessoas.
        </p>
      </div>

      {/* ── Perfil ──────────────────────────────────────────────────────── */}
      <section className={styles.card}>
        <header className={styles.cardHeader}>
          <User size={17} className={styles.cardIcon} />
          <div>
            <h3 className={styles.cardTitle}>Perfil</h3>
            <p className={styles.cardSubtitle}>Como você aparece no painel.</p>
          </div>
        </header>

        <div className={styles.cardBody}>
          <label className={styles.field}>
            <span className={styles.label}>Nome</span>
            <input
              type="text"
              value={nome}
              onChange={(e) => setNome(e.target.value)}
              className={styles.input}
              placeholder="Seu nome"
            />
          </label>

          <label className={styles.field}>
            <span className={styles.label}>E-mail</span>
            <input type="text" value={account.email} className={styles.input} disabled readOnly />
            {/* Decisão da Fase 3, mantida: o e-mail é o `sub` do JWT. Trocá-lo
                invalidaria a própria sessão em silêncio. O backend recusa. */}
            <span className={styles.hint}>
              O e-mail identifica sua conta no sistema e não pode ser alterado. Se precisar trocar,
              peça a um administrador.
            </span>
          </label>

          <div className={styles.field}>
            <span className={styles.label}>Perfil de acesso</span>
            <div className={styles.roleRow}>
              <span className={styles.roleBadge}>{ROLE_LABELS[account.role]}</span>
              <span className={styles.hint}>
                Só um administrador altera perfis de acesso, em <Link href="/users">Usuários</Link>.
              </span>
            </div>
          </div>

          {erroPerfil && <p className={styles.formError}>{erroPerfil}</p>}
        </div>

        <footer className={styles.cardFooter}>
          <button
            onClick={() => void salvarPerfil()}
            disabled={!nomeMudou || salvandoPerfil}
            className={styles.primaryButton}
          >
            {salvandoPerfil ? <Loader2 size={15} className="animate-spin" /> : <Check size={15} />}
            Salvar perfil
          </button>
        </footer>
      </section>

      {/* ── Senha ───────────────────────────────────────────────────────── */}
      <section className={styles.card}>
        <header className={styles.cardHeader}>
          <KeyRound size={17} className={styles.cardIcon} />
          <div>
            <h3 className={styles.cardTitle}>Senha</h3>
            <p className={styles.cardSubtitle}>
              Exige a senha atual — é o que impede que uma sessão aberta em máquina alheia troque
              sua senha e tome a conta.
            </p>
          </div>
        </header>

        <div className={styles.cardBody}>
          <label className={styles.field}>
            <span className={styles.label}>Senha atual</span>
            <input
              type="password"
              value={senhaAtual}
              onChange={(e) => setSenhaAtual(e.target.value)}
              className={styles.input}
              autoComplete="current-password"
            />
          </label>

          <div className={styles.fieldRow}>
            <label className={styles.field}>
              <span className={styles.label}>Nova senha</span>
              <input
                type="password"
                value={senhaNova}
                onChange={(e) => setSenhaNova(e.target.value)}
                className={styles.input}
                placeholder={`Mínimo de ${SENHA_MINIMA} caracteres`}
                autoComplete="new-password"
              />
            </label>

            <label className={styles.field}>
              <span className={styles.label}>Confirmar nova senha</span>
              <input
                type="password"
                value={senhaConfirma}
                onChange={(e) => setSenhaConfirma(e.target.value)}
                className={styles.input}
                autoComplete="new-password"
              />
            </label>
          </div>

          {/* Limitação real, documentada no backend: o JWT não guarda versão
              de senha, então sessões já abertas continuam valendo. Melhor
              dizer do que deixar a pessoa supor que trocou e "expulsou" todo
              mundo. */}
          <p className={styles.note}>
            Sessões já abertas em outros dispositivos continuam válidas até expirarem. Para encerrar
            uma sessão suspeita agora, peça a um administrador para desativar e reativar sua conta.
          </p>

          {erroSenha && <p className={styles.formError}>{erroSenha}</p>}
        </div>

        <footer className={styles.cardFooter}>
          <button
            onClick={() => void trocarSenha()}
            disabled={trocandoSenha || !senhaAtual || !senhaNova}
            className={styles.primaryButton}
          >
            {trocandoSenha ? <Loader2 size={15} className="animate-spin" /> : <KeyRound size={15} />}
            Alterar senha
          </button>
        </footer>
      </section>

      {/* ── Aparência ───────────────────────────────────────────────────── */}
      <section className={styles.card}>
        <header className={styles.cardHeader}>
          <Palette size={17} className={styles.cardIcon} />
          <div>
            <h3 className={styles.cardTitle}>Aparência</h3>
            <p className={styles.cardSubtitle}>
              Aplicada neste dispositivo. Atualmente em modo {theme === "dark" ? "escuro" : "claro"}.
            </p>
          </div>
        </header>

        <div className={styles.cardBody}>
          <div className={styles.field}>
            <span className={styles.label}>Tema</span>
            <div className={styles.optionGrid}>
              {TEMAS.map((t) => {
                const Icone = t.icon;
                const ativo = preference === t.value;
                return (
                  <button
                    key={t.value}
                    onClick={() => setPreference(t.value)}
                    className={cn(styles.option, ativo && styles.optionActive)}
                    aria-pressed={ativo}
                  >
                    <Icone size={18} />
                    <span className={styles.optionLabel}>{t.label}</span>
                    <span className={styles.optionHint}>{t.hint}</span>
                  </button>
                );
              })}
            </div>
            {/* Antes da Fase 8 só existiam claro e escuro: bastava usar o botão
                do cabeçalho uma vez para nunca mais voltar a seguir o SO. */}
            <span className={styles.hint}>
              O botão de tema no cabeçalho fixa claro ou escuro. Escolha <strong>Sistema</strong>{" "}
              aqui para voltar a acompanhar o computador.
            </span>
          </div>
        </div>
      </section>

      {/* ── Acessibilidade ──────────────────────────────────────────────── */}
      <section className={styles.card}>
        <header className={styles.cardHeader}>
          <Accessibility size={17} className={styles.cardIcon} />
          <div>
            <h3 className={styles.cardTitle}>Acessibilidade</h3>
            <p className={styles.cardSubtitle}>
              Guardadas neste dispositivo, não na sua conta — a necessidade costuma ser da máquina,
              não da pessoa.
            </p>
          </div>
        </header>

        <div className={styles.cardBody}>
          <div className={styles.field}>
            <span className={styles.label}>Tamanho do texto</span>
            <div className={styles.optionGrid}>
              {ESCALAS.map((e) => {
                const ativo = preferences.fontScale === e.value;
                return (
                  <button
                    key={e.value}
                    onClick={() => setPref("fontScale", e.value)}
                    className={cn(styles.option, ativo && styles.optionActive)}
                    aria-pressed={ativo}
                  >
                    <span className={styles.escalaAmostra} style={{ fontSize: `${e.value}rem` }}>
                      Aa
                    </span>
                    <span className={styles.optionLabel}>{e.label}</span>
                    <span className={styles.optionHint}>
                      {e.value === 1 ? "Como o navegador define" : `${Math.round(e.value * 100)}%`}
                    </span>
                  </button>
                );
              })}
            </div>
            <span className={styles.hint}>
              Parte do tamanho do seu navegador, então funciona junto com o zoom dele.
            </span>
          </div>

          <label className={styles.switchRow}>
            <input
              type="checkbox"
              checked={preferences.reduceMotion}
              onChange={(e) => setPref("reduceMotion", e.target.checked)}
              className={styles.checkbox}
            />
            <span className={styles.switchBody}>
              <span className={styles.switchLabel}>Reduzir animações</span>
              <span className={styles.hint}>
                Corta transições e movimentos do painel. Soma-se à configuração do sistema
                operacional; útil quando você não tem permissão para mexer nela.
              </span>
            </span>
          </label>

          <label className={styles.switchRow}>
            <input
              type="checkbox"
              checked={preferences.strongFocus}
              onChange={(e) => setPref("strongFocus", e.target.checked)}
              className={styles.checkbox}
            />
            <span className={styles.switchBody}>
              <span className={styles.switchLabel}>Realce de foco reforçado</span>
              <span className={styles.hint}>
                Anel mais grosso ao navegar por teclado, para não perder o cursor em telas densas
                como a tabela de impressoras.
              </span>
            </span>
          </label>
        </div>

        {modificado && (
          <footer className={styles.cardFooter}>
            <button onClick={reset} className={styles.secondaryButton}>
              <RotateCcw size={15} />
              Restaurar padrões
            </button>
          </footer>
        )}
      </section>

      {/* ══ ADMINISTRAÇÃO ═════════════════════════════════════════════════ */}
      {can.canAdmin && (
        <>
          <div className={styles.groupHeader}>
            <h2 className={styles.groupTitle}>Administração</h2>
            <p className={styles.groupSubtitle}>
              Afeta o sistema inteiro e as outras pessoas. Visível só para administradores.
            </p>
          </div>

          <section className={cn(styles.card, styles.cardAdmin)}>
            <header className={styles.cardHeader}>
              <ShieldCheck size={17} className={styles.cardIconAdmin} />
              <div>
                <h3 className={styles.cardTitle}>Onde a administração acontece</h3>
                <p className={styles.cardSubtitle}>
                  Nada crítico é editável nesta página, de propósito: cada ação vive na tela que a
                  documenta e a confirma.
                </p>
              </div>
            </header>

            <div className={styles.cardBody}>
              <div className={styles.linkGrid}>
                <Link href="/users" className={styles.adminLink}>
                  <Users size={18} className={styles.adminLinkIcon} />
                  <span className={styles.adminLinkTitle}>Usuários</span>
                  <span className={styles.optionHint}>
                    Criar contas, alterar perfis de acesso, ativar e desativar.
                  </span>
                </Link>

                <Link href="/network" className={styles.adminLink}>
                  <Network size={18} className={styles.adminLinkIcon} />
                  <span className={styles.adminLinkTitle}>Print Servers</span>
                  <span className={styles.optionHint}>
                    Registrar servidores, descobrir impressoras e sincronizar o cadastro.
                  </span>
                </Link>
              </div>

              {/* Endereço público da API — não é secret: o navegador o envia em
                  toda requisição. Nenhuma variável de ambiente, chave ou
                  credencial é exposta aqui. */}
              <div className={styles.field}>
                <span className={styles.label}>Backend em uso</span>
                <code className={styles.code}>{API_BASE_URL}</code>
                <span className={styles.hint}>
                  Definido no build (<code>NEXT_PUBLIC_API_URL</code>). Configurações sensíveis do
                  servidor — chaves, credenciais, webhook — ficam no <code>.env</code> do backend e
                  nunca são expostas na interface.
                </span>
              </div>
            </div>
          </section>
        </>
      )}
    </div>
  );
}
