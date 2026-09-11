"use client";

/**
 * Dependências externas: react (useState/useRef) e lucide-react (ícones).
 * A validação das credenciais é feita pelo backend (POST /api/auth/login via
 * lib/auth.ts). `onSuccess` é a única saída deste componente;
 * quem decide o que fazer com a conta autenticada é App.tsx.
 */
import { useRef, useState, type FormEvent, type KeyboardEvent } from "react";
import {
  Mail,
  Lock,
  Eye,
  EyeOff,
  Loader2,
  TriangleAlert,
  ShieldCheck,
  Activity,
  BellRing,
  Wifi,
  Sun,
  Moon,
  Monitor,
  ArrowRight,
  Printer as PrinterIcon,
  type LucideIcon,
} from "lucide-react";
import { login, type Account } from "../lib/auth";
import { useTheme, type ThemePreference } from "../lib/theme";
import { ApiError } from "../lib/api";
import { useToast } from "../lib/toast";
import ElginLogo from "./ElginLogo";
import { cn } from "../lib/cn";
import styles from "./Login.module.css";

interface LoginProps {
  onSuccess: (account: Account, remember: boolean) => void;
}

// Textos curtos de propósito: cabem em uma linha no painel de ~42% da tela e
// deixam o painel inteiro dentro de uma janela de notebook sem rolagem.
const features = [
  {
    icon: Activity,
    title: "Monitoramento em tempo real",
    text: "Status de toda a frota em um só lugar.",
  },
  {
    icon: BellRing,
    title: "Alertas inteligentes",
    text: "Aviso antes do toner acabar ou de uma impressora cair.",
  },
  {
    icon: ShieldCheck,
    title: "Acesso seguro",
    text: "Só quem tem permissão entra no painel.",
  },
];

// Os três estados de lib/theme.tsx. "Sistema" precisa estar aqui: sem ele,
// quem tocasse em Claro/Escuro uma vez nunca mais voltava a seguir o SO.
const THEME_OPTIONS: { value: ThemePreference; label: string; icon: LucideIcon }[] = [
  { value: "light", label: "Claro", icon: Sun },
  { value: "dark", label: "Escuro", icon: Moon },
  { value: "system", label: "Sistema", icon: Monitor },
];

// Nós fixos do "mapa de rede" decorativo do painel esquerdo — coordenadas em
// percentual (viewBox 0-100), pensadas pra parecerem uma malha de dispositivos
// monitorados, não um padrão repetido genérico.
const NETWORK_NODES = [
  { x: 12, y: 14 }, { x: 34, y: 8 }, { x: 58, y: 18 }, { x: 82, y: 10 },
  { x: 6, y: 38 }, { x: 28, y: 34 }, { x: 50, y: 42 }, { x: 74, y: 36 }, { x: 93, y: 44 },
  { x: 16, y: 60 }, { x: 40, y: 66 }, { x: 64, y: 58 }, { x: 88, y: 68 },
  { x: 10, y: 86 }, { x: 33, y: 90 }, { x: 56, y: 82 }, { x: 80, y: 92 },
];
const NETWORK_LINKS: [number, number][] = [
  [0, 1], [1, 2], [2, 3], [0, 4], [1, 5], [2, 6], [3, 7], [3, 8],
  [4, 5], [5, 6], [6, 7], [7, 8], [5, 9], [6, 10], [7, 11], [8, 12],
  [9, 10], [10, 11], [11, 12], [9, 13], [10, 14], [11, 15], [12, 16],
  [13, 14], [14, 15], [15, 16],
];
const ACTIVE_NODES = [2, 6, 10, 15];

// `slice` (e não `none`) mantém a proporção: com `none` o SVG esticava junto
// com o painel e os nós viravam elipses. `non-scaling-stroke` deixa as linhas
// com 1px em qualquer tamanho de tela.
function NetworkMap() {
  return (
    <svg
      className={styles.networkMap}
      viewBox="0 0 100 100"
      preserveAspectRatio="xMidYMid slice"
      aria-hidden="true"
    >
      {NETWORK_LINKS.map(([a, b], i) => (
        <line
          key={i}
          x1={NETWORK_NODES[a].x}
          y1={NETWORK_NODES[a].y}
          x2={NETWORK_NODES[b].x}
          y2={NETWORK_NODES[b].y}
          stroke="white"
          strokeWidth="1"
          vectorEffect="non-scaling-stroke"
        />
      ))}
      {NETWORK_NODES.map((n, i) => (
        <circle key={i} cx={n.x} cy={n.y} r={0.55} fill="white" />
      ))}
      {ACTIVE_NODES.map((index, i) => (
        <g key={index}>
          <circle
            className={styles.nodeHalo}
            style={{ animationDelay: `${i * 0.8}s` }}
            cx={NETWORK_NODES[index].x}
            cy={NETWORK_NODES[index].y}
            r={2.6}
            fill="white"
          />
          <circle cx={NETWORK_NODES[index].x} cy={NETWORK_NODES[index].y} r={1.1} fill="white" />
        </g>
      ))}
    </svg>
  );
}

interface LoginError {
  message: string;
  /** true quando o problema é o que foi digitado (marca os campos). */
  invalid: boolean;
}

export default function Login({ onSuccess }: LoginProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [remember, setRemember] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<LoginError | null>(null);
  const [shake, setShake] = useState(false);
  const [capsLock, setCapsLock] = useState(false);
  const emailRef = useRef<HTMLInputElement>(null);
  const passwordRef = useRef<HTMLInputElement>(null);
  const { push } = useToast();
  const { theme, preference, setPreference } = useTheme();

  function showInvalid(message: string) {
    setError({ message, invalid: true });
    setShake(true);
    window.setTimeout(() => setShake(false), 420);
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (loading) return;

    // Campo vazio nem chega ao backend: cada POST conta para o bloqueio por
    // tentativas (429), e "senha incorreta" para um campo em branco é mentira.
    const user = email.trim();
    if (!user || !password) {
      showInvalid("Informe o e-mail/usuário e a senha para entrar.");
      (user ? passwordRef : emailRef).current?.focus();
      return;
    }

    setError(null);
    setLoading(true);

    try {
      const account = await login(user, password, remember);
      onSuccess(account, remember);
    } catch (err) {
      setLoading(false);

      // 0 (rede) e 429 (bloqueio por tentativas) já vêm do backend com uma
      // mensagem específica e verdadeira ("tente novamente em N minuto(s)")
      // — mostrar "senha incorreta" por cima dela é enganoso: a senha pode
      // estar certíssima, o pedido nem chegou a ser conferido. Só o "resto"
      // (401 de fato) cai no texto genérico.
      //
      // O "shake" e o contorno vermelho sinalizam "o que você digitou está
      // errado" — correto para 401, mas mentiroso para 429: a digitação pode
      // estar perfeita, o bloqueio é por excesso de tentativas, não por esta.
      const lockedOrOffline = err instanceof ApiError && (err.status === 0 || err.status === 429);
      if (lockedOrOffline) {
        setError({ message: err.message, invalid: false });
      } else {
        showInvalid("E-mail/usuário ou senha incorretos. Verifique os dados e tente novamente.");
        passwordRef.current?.select();
      }
    }
  }

  // Ao corrigir o que foi digitado, o aviso de credencial inválida sai.
  // O de bloqueio/servidor fica: editar o campo não muda aquela situação.
  function clearInvalid() {
    if (error?.invalid) setError(null);
  }

  function handleCapsLock(e: KeyboardEvent<HTMLInputElement>) {
    setCapsLock(e.getModifierState("CapsLock"));
  }

  function handleForgotPassword() {
    push({
      variant: "info",
      title: "Fale com o administrador",
      description: "A redefinição de senha é feita pela equipe de TI da Elgin.",
    });
  }

  const invalid = error?.invalid ?? false;
  const passwordDescribedBy = [capsLock ? "login-caps" : "", error ? "login-error" : ""]
    .filter(Boolean)
    .join(" ");

  return (
    <div className={styles.page}>
      {/* Left / branded hero panel */}
      <aside className={styles.heroPanel}>
        <NetworkMap />
        <div className={styles.glowTop} aria-hidden="true" />
        <div className={styles.glowBottom} aria-hidden="true" />

        <div className={styles.heroLogo}>
          <ElginLogo height={36} tone="white" />
          <p className={styles.heroLogoSubtitle}>Impressoras</p>
        </div>

        <div className={styles.heroContent}>
          <span className={styles.badge}>
            <PrinterIcon size={12} aria-hidden="true" />
            Painel corporativo
          </span>
          <h1 className={styles.heroTitle}>
            Gerencie sua frota de impressoras com{" "}
            <span className={styles.heroTitleAccent}>clareza total.</span>
          </h1>
          <p className={styles.heroSubtitle}>
            Um painel único para status, toner, alertas e relatórios de toda a sua rede corporativa.
          </p>

          <ul className={styles.featureList}>
            {features.map((f) => (
              <li key={f.title} className={styles.featureItem}>
                <span className={styles.featureIconWrap} aria-hidden="true">
                  <f.icon size={17} />
                </span>
                <div>
                  <p className={styles.featureTitle}>{f.title}</p>
                  <p className={styles.featureText}>{f.text}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>

        <div className={styles.statusCard}>
          <span className={styles.statusIconWrap} aria-hidden="true">
            <Wifi size={18} />
          </span>
          <div>
            <p className={styles.statusTitle}>100+ impressoras monitoradas</p>
            <p className={styles.statusSubtitle}>
              <span className={styles.liveDot} aria-hidden="true" />
              8 unidades · atualizado em tempo real
            </p>
          </div>
        </div>
      </aside>

      {/* Right / form panel */}
      <main className={styles.formPanel}>
        <header className={styles.formTopbar}>
          <div className={styles.mobileLogo}>
            <ElginLogo height={28} tone={theme === "dark" ? "white" : "brand"} />
            <p className={styles.mobileLogoSubtitle}>Impressoras</p>
          </div>

          <div className={styles.themeSwitch} role="group" aria-label="Tema da tela">
            {THEME_OPTIONS.map(({ value, label, icon: Icon }) => (
              <button
                key={value}
                type="button"
                onClick={() => setPreference(value)}
                aria-pressed={preference === value}
                aria-label={label}
                title={label}
                className={cn(styles.themeOption, preference === value ? styles.themeOptionActive : "")}
              >
                <Icon size={14} aria-hidden="true" />
                <span className={styles.themeLabel}>{label}</span>
              </button>
            ))}
          </div>
        </header>

        <div className={styles.formMain}>
          <div className={cn(styles.card, shake ? styles.shake : "")}>
            <div className={styles.cardIcon} aria-hidden="true">
              <ShieldCheck size={20} />
            </div>
            <h2 className={styles.cardTitle}>Bem-vindo de volta</h2>
            <p className={styles.cardSubtitle}>Entre com sua conta para acessar o painel de monitoramento.</p>

            <form className={styles.form} onSubmit={handleSubmit} noValidate>
              <div className={styles.field}>
                <label htmlFor="login-email" className={styles.label}>
                  E-mail ou usuário
                </label>
                <div className={styles.inputWrap}>
                  <Mail size={17} className={styles.inputIcon} aria-hidden="true" />
                  <input
                    ref={emailRef}
                    id="login-email"
                    name="username"
                    type="text"
                    autoComplete="username"
                    autoCapitalize="none"
                    autoCorrect="off"
                    spellCheck={false}
                    value={email}
                    onChange={(e) => {
                      setEmail(e.target.value);
                      clearInvalid();
                    }}
                    placeholder="nome.sobrenome ou e-mail"
                    aria-invalid={invalid}
                    aria-describedby={error ? "login-error" : undefined}
                    className={styles.input}
                  />
                </div>
              </div>

              <div className={styles.field}>
                <div className={styles.labelRow}>
                  <label htmlFor="login-password" className={styles.label}>
                    Senha
                  </label>
                  <button type="button" className={styles.forgotLink} onClick={handleForgotPassword}>
                    Esqueceu a senha?
                  </button>
                </div>
                <div className={styles.inputWrap}>
                  <Lock size={17} className={styles.inputIcon} aria-hidden="true" />
                  <input
                    ref={passwordRef}
                    id="login-password"
                    name="password"
                    type={showPassword ? "text" : "password"}
                    autoComplete="current-password"
                    value={password}
                    onChange={(e) => {
                      setPassword(e.target.value);
                      clearInvalid();
                    }}
                    onKeyDown={handleCapsLock}
                    onKeyUp={handleCapsLock}
                    onBlur={() => setCapsLock(false)}
                    placeholder="••••••••"
                    aria-invalid={invalid}
                    aria-describedby={passwordDescribedBy || undefined}
                    className={styles.input}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((s) => !s)}
                    className={styles.togglePassword}
                    aria-label={showPassword ? "Ocultar senha" : "Mostrar senha"}
                    title={showPassword ? "Ocultar senha" : "Mostrar senha"}
                  >
                    {showPassword ? <EyeOff size={17} aria-hidden="true" /> : <Eye size={17} aria-hidden="true" />}
                  </button>
                </div>
                {capsLock && (
                  <p id="login-caps" className={styles.capsHint} role="status">
                    <TriangleAlert size={13} aria-hidden="true" />
                    Caps Lock está ativado
                  </p>
                )}
              </div>

              {error && (
                <div id="login-error" className={styles.errorBox} role="alert">
                  <TriangleAlert size={17} className={styles.errorIcon} aria-hidden="true" />
                  <span>{error.message}</span>
                </div>
              )}

              <label className={styles.rememberLabel}>
                <input
                  type="checkbox"
                  checked={remember}
                  onChange={(e) => setRemember(e.target.checked)}
                  className={styles.checkbox}
                />
                Lembrar de mim neste dispositivo
              </label>

              <button type="submit" disabled={loading} aria-busy={loading} className={styles.submitButton}>
                {loading ? (
                  <>
                    <Loader2 size={17} className="animate-spin" aria-hidden="true" />
                    Entrando...
                  </>
                ) : (
                  <>
                    Entrar
                    <ArrowRight size={17} className={styles.submitArrow} aria-hidden="true" />
                  </>
                )}
              </button>
            </form>
          </div>
        </div>

        <footer className={styles.footer}>© 2026 Elgin Impressoras · Pedro e Mateus</footer>
      </main>
    </div>
  );
}
