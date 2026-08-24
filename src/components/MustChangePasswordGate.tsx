"use client";

/**
 * Troca de senha obrigatória (conta recém-criada ou recém-resetada por um
 * admin — ver Account.mustChangePassword em lib/auth.ts).
 *
 * AuthGate mostra ESTE componente em vez do painel enquanto a flag estiver
 * ligada. Não é só uma etiqueta de UI: o backend também recusa qualquer
 * rota além de GET /api/auth/me e POST /api/auth/change-password enquanto a
 * conta estiver nesse estado (`require_active_user`), então mesmo que
 * alguém pulasse esta tela via devtools, o resto do painel devolveria 403.
 *
 * Reaproveita o MESMO endpoint que a troca de senha voluntária em
 * Configurações (`changeMyPassword`, POST /api/auth/change-password) — só a
 * tela é diferente, o backend não sabe (nem precisa saber) que esta troca é
 * obrigatória.
 */
import { useState, type FormEvent } from "react";
import { KeyRound, LogOut } from "lucide-react";
import { changeMyPassword, withPasswordChanged } from "../lib/auth";
import { useApiErrorReporter } from "../lib/apiErrors";
import { useAppData } from "../lib/app-data";
import { useToast } from "../lib/toast";
import styles from "./MustChangePasswordGate.module.css";

const SENHA_MINIMA = 8;

export default function MustChangePasswordGate() {
  const { account, applyAccountUpdate, handleLogout, handleRefresh } = useAppData();
  const { push } = useToast();
  const relatarErro = useApiErrorReporter();

  const [senhaAtual, setSenhaAtual] = useState("");
  const [senhaNova, setSenhaNova] = useState("");
  const [senhaConfirma, setSenhaConfirma] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  // AuthGate só renderiza este componente com uma sessão confirmada; a
  // guarda existe para o TypeScript e para o caso improvável de a conta
  // sumir (logout em outra aba) no meio da troca.
  if (!account) return null;

  function validar(): string | null {
    if (!senhaAtual) return "Informe a senha atual (a que você recebeu).";
    if (senhaNova.length < SENHA_MINIMA) return `A nova senha deve ter ao menos ${SENHA_MINIMA} caracteres.`;
    if (senhaNova === senhaAtual) return "A nova senha precisa ser diferente da atual.";
    if (senhaNova !== senhaConfirma) return "A confirmação não confere com a nova senha.";
    return null;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    // Redundante com a guarda do topo do componente, mas o TypeScript não
    // propaga aquela checagem para dentro desta closure — `account` aqui
    // ainda é `Account | null` sem isto.
    if (!account) return;

    const invalido = validar();
    if (invalido) {
      setErro(invalido);
      return;
    }

    setEnviando(true);
    setErro(null);
    try {
      await changeMyPassword(senhaAtual, senhaNova);
      // O backend já desligou a flag; isto só evita esperar por um novo
      // GET /me para o AuthGate liberar o painel.
      applyAccountUpdate(withPasswordChanged(account));
      push({
        variant: "success",
        title: "Senha alterada",
        description: "Tudo certo — você já pode continuar.",
      });
      // A carga de dados reais (printers/alertas) que rodou enquanto esta
      // tela bloqueava o painel foi recusada com 403 (mesma trava do
      // backend) e caiu no conjunto de demonstração. `accountKey` no
      // provider é o e-mail, que não muda aqui — sem este refresh explícito
      // o painel abriria "preso" na demonstração até um F5. Sem `await`: a
      // troca de tela já aconteceu (mustChangePassword acabou de virar
      // false), o refresh continua em segundo plano no AppShell, igual ao
      // botão "Atualizar".
      void handleRefresh();
    } catch (error) {
      setErro(relatarErro(error, "Não foi possível alterar a senha"));
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className={styles.wrap} role="dialog" aria-modal="true" aria-labelledby="must-change-title">
      <div className={styles.card}>
        <div className={styles.iconWrap}>
          <KeyRound size={20} />
        </div>

        <div>
          <h1 id="must-change-title" className={styles.title}>
            Defina uma nova senha
          </h1>
          <p className={styles.subtitle}>
            Por segurança, toda conta nova ou com senha redefinida por um administrador precisa trocar a
            senha antes de acessar o painel.
          </p>
        </div>

        <div className={styles.account}>
          Entrando como <strong>{account.name}</strong>
          {/* `account.email` já vem só com a parte antes do "@" (ver
              toAccount em lib/auth.ts) — não reconstruímos o domínio aqui
              para não arriscar mostrar um errado. */}
          {" "}({account.username ?? account.email})
        </div>

        <form className={styles.form} onSubmit={handleSubmit} noValidate>
          <label className={styles.field}>
            <span className={styles.label}>Senha atual</span>
            <input
              type="password"
              value={senhaAtual}
              onChange={(e) => setSenhaAtual(e.target.value)}
              className={styles.input}
              autoComplete="current-password"
              autoFocus
            />
          </label>

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

          {erro && <p className={styles.formError}>{erro}</p>}

          <button type="submit" disabled={enviando} className={styles.primaryButton}>
            {enviando ? "Salvando..." : "Trocar senha e continuar"}
          </button>
        </form>

        <button type="button" onClick={handleLogout} className={styles.logoutLink}>
          <LogOut size={13} style={{ verticalAlign: "-2px", marginRight: "0.25rem" }} />
          Entrar com outra conta
        </button>
      </div>
    </div>
  );
}
