"use client";

/**
 * Configurações (rota "/settings").
 *
 * Uma navegação por seções (lista lateral no desktop, abas roláveis no
 * celular) e um painel por seção. Os painéis inativos ficam montados e só
 * escondidos (`hidden`), para que um formulário pela metade não se perca ao
 * trocar de aba. A seção ativa vai para o hash da URL (#seguranca etc.),
 * então dá para mandar o link direto de uma seção.
 *
 *   Perfil, Segurança      -> conta da pessoa logada; o backend escopa pela
 *                             sessão (lib/auth).
 *   Aparência, Acessib.    -> preferências deste dispositivo (localStorage).
 *   Coleta, Notificações,
 *   Sobre                  -> somente leitura, a partir de GET /health e das
 *                             listas de servidores e unidades já carregadas.
 *                             Atalhos de administração só para admin.
 */
import { useCallback, useEffect, useRef, useState, type KeyboardEvent } from "react";
import { Accessibility, Bell, Info, KeyRound, Palette, Server, User } from "lucide-react";
import { useAppData } from "../lib/app-data";
import { cn } from "../lib/cn";
import styles from "./SettingsView.module.css";
import { PasswordSection, ProfileSection } from "./settings/AccountSections";
import { AccessibilitySection, AppearanceSection } from "./settings/PreferenceSections";
import { AboutSection, CollectionSection, NotificationsSection } from "./settings/SystemSections";
import { SettingsPanel } from "./settings/ui";

const SECOES = [
  { id: "perfil", label: "Perfil", icon: User, description: "Seu nome e os dados da sua conta." },
  { id: "seguranca", label: "Segurança", icon: KeyRound, description: "Senha de acesso ao painel." },
  { id: "aparencia", label: "Aparência", icon: Palette, description: "Tema claro, escuro ou do sistema." },
  {
    id: "acessibilidade",
    label: "Acessibilidade",
    icon: Accessibility,
    description: "Tamanho do texto, animações e realce de foco.",
  },
  {
    id: "coleta",
    label: "Coleta e servidores",
    icon: Server,
    description: "Como e com que frequência o sistema lê as impressoras.",
  },
  {
    id: "notificacoes",
    label: "Notificações",
    icon: Bell,
    description: "Quais alertas você recebe e por onde eles saem.",
  },
  { id: "sobre", label: "Sobre o sistema", icon: Info, description: "Versão, ambiente e endereço da API." },
] as const;

type SecaoId = (typeof SECOES)[number]["id"];

function secaoDoHash(): SecaoId | null {
  const hash = window.location.hash.replace(/^#/, "");
  return SECOES.some((s) => s.id === hash) ? (hash as SecaoId) : null;
}

export default function SettingsView() {
  const { account } = useAppData();
  const [ativa, setAtiva] = useState<SecaoId>("perfil");
  const abasRef = useRef<Record<string, HTMLButtonElement | null>>({});

  useEffect(() => {
    const sincronizar = () => {
      const secao = secaoDoHash();
      if (secao) setAtiva(secao);
    };
    sincronizar();
    window.addEventListener("hashchange", sincronizar);
    return () => window.removeEventListener("hashchange", sincronizar);
  }, []);

  const selecionar = useCallback((id: SecaoId, focar = false) => {
    setAtiva(id);
    window.history.replaceState(window.history.state, "", `#${id}`);
    const aba = abasRef.current[id];
    if (focar) aba?.focus();
    aba?.scrollIntoView({ block: "nearest", inline: "nearest" });
  }, []);

  // Setas/Home/End entre as abas (padrão WAI-ARIA de tablist).
  function aoTeclar(e: KeyboardEvent<HTMLDivElement>) {
    const i = SECOES.findIndex((s) => s.id === ativa);
    let proximo: number | null = null;
    if (e.key === "ArrowDown" || e.key === "ArrowRight") proximo = (i + 1) % SECOES.length;
    else if (e.key === "ArrowUp" || e.key === "ArrowLeft") proximo = (i - 1 + SECOES.length) % SECOES.length;
    else if (e.key === "Home") proximo = 0;
    else if (e.key === "End") proximo = SECOES.length - 1;
    if (proximo === null) return;
    e.preventDefault();
    selecionar(SECOES[proximo].id, true);
  }

  if (!account) return null;

  return (
    <div className={styles.layout}>
      <div role="tablist" aria-label="Seções de configuração" className={styles.nav} onKeyDown={aoTeclar}>
        {SECOES.map((s) => {
          const Icone = s.icon;
          const selecionada = s.id === ativa;
          return (
            <button
              key={s.id}
              ref={(el) => {
                abasRef.current[s.id] = el;
              }}
              id={`aba-${s.id}`}
              type="button"
              role="tab"
              aria-selected={selecionada}
              aria-controls={`painel-${s.id}`}
              tabIndex={selecionada ? 0 : -1}
              onClick={() => selecionar(s.id)}
              className={cn(styles.navItem, selecionada && styles.navItemActive)}
            >
              <Icone size={16} aria-hidden="true" className={styles.navIcon} />
              {s.label}
            </button>
          );
        })}
      </div>

      <div className={styles.content}>
        {SECOES.map((s) => (
          <SettingsPanel key={s.id} id={s.id} title={s.label} description={s.description} active={s.id === ativa}>
            {s.id === "perfil" && <ProfileSection account={account} />}
            {s.id === "seguranca" && <PasswordSection />}
            {s.id === "aparencia" && <AppearanceSection />}
            {s.id === "acessibilidade" && <AccessibilitySection />}
            {s.id === "coleta" && <CollectionSection />}
            {s.id === "notificacoes" && <NotificationsSection account={account} />}
            {s.id === "sobre" && <AboutSection />}
          </SettingsPanel>
        ))}
      </div>
    </div>
  );
}
