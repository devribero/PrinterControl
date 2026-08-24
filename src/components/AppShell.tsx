/**
 * Casco fixo do painel (sidebar + topbar + rodapé + modais globais) que
 * envolve o conteúdo de cada rota — equivalente ao JSX que antes ficava em
 * torno do `switch` de `activeNav` em App.tsx. `mobileMenuOpen` e `helpOpen`
 * são estado só de "chrome" da UI, não precisam estar no AppDataProvider.
 */
"use client";

import { useState, type ReactNode } from "react";
import { usePathname } from "next/navigation";
import { Mail, MessageCircle, LifeBuoy, TriangleAlert, FlaskConical } from "lucide-react";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import PrinterDetailsModal from "./PrinterDetailsModal";
import Modal from "./Modal";
import { useAppData } from "../lib/app-data";
import { useToast } from "../lib/toast";
import styles from "./AppShell.module.css";

export default function AppShell({ children }: { children: ReactNode }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [helpOpen, setHelpOpen] = useState(false);
  const pathname = usePathname();
  const {
    usingRealData,
    usingRealMonthlyReport,
    exibindoDadoFicticio,
    backendEnv,
    sessionVerified,
    apiError,
    selectedPrinter,
    setSelectedPrinter,
  } = useAppData();
  const { push } = useToast();

  return (
    <div className={styles.shell}>
      <Sidebar
        mobileOpen={mobileMenuOpen}
        onCloseMobile={() => setMobileMenuOpen(false)}
        onNavigate={() => setMobileMenuOpen(false)}
        onOpenHelp={() => setHelpOpen(true)}
      />

      <div className={styles.main}>
        <Topbar onOpenMobileMenu={() => setMobileMenuOpen(true)} />

        <main className={styles.content}>
          {/* Faixa PERMANENTE de instância de demonstração (Fase 9).

              Distinta da faixa abaixo de propósito: esta descreve o AMBIENTE
              — dado fictício aqui é esperado e legítimo, não é incidente — e
              por isso não fala em falha nem sugere conferir o backend. Fica
              visível mesmo com a API respondendo perfeitamente, porque numa
              instância de demonstração o que engana não é o erro, é o
              sucesso: tudo funciona, e nada é real. */}
          {backendEnv?.is_demo && (
            <div className={styles.demoEnvBanner} role="status">
              <FlaskConical size={16} className={styles.demoEnvBannerIcon} />
              <p className={styles.demoEnvBannerText}>
                <strong>Ambiente de demonstração.</strong> Esta instância não é a de produção:
                nada aqui reflete a frota real, e nenhuma alteração afeta o sistema em uso.
              </p>
            </div>
          )}

          {/* Faixa de dado fictício por FALHA ou ausência de dado real.

              A condição passou a ser `exibindoDadoFicticio`, e não apenas
              `!usingRealData`: com a frota real carregada mas sem relatório
              mensal fechado no backend, os gráficos de consumo caíam no mock
              sem faixa nenhuma — dado real e inventado lado a lado, que é
              exatamente o que esta fase existe para impedir. */}
          {exibindoDadoFicticio && !backendEnv?.is_demo && (
            <div className={styles.demoBanner} role="status">
              <TriangleAlert size={16} className={styles.demoBannerIcon} />
              <p className={styles.demoBannerText}>
                {!usingRealData ? (
                  <>
                    <strong>Dados de demonstração.</strong>{" "}
                    {apiError ?? "Os números abaixo são fictícios e não vêm da sua frota."}
                    {!sessionVerified && " A sessão não pôde ser confirmada com o servidor."}
                  </>
                ) : (
                  <>
                    <strong>Relatório mensal de demonstração.</strong> A frota exibida é real,
                    mas o servidor ainda não tem leituras suficientes para fechar o mês — os
                    números de consumo mensal e os gráficos de histórico são fictícios.
                  </>
                )}
              </p>
            </div>
          )}

          <div key={pathname} className={`${styles.view} animate-view-in`}>
            {children}
          </div>
        </main>

        <footer className={styles.footer}>
          <p>Elgin Impressoras © 2026 — Todos os direitos reservados</p>
          <div className={styles.footerStatus}>
            {/* Rótulo do ambiente — presente inclusive em produção: saber que
                se está em produção importa tanto quanto saber que não. Some
                quando o backend não respondeu, porque aí o ambiente é
                desconhecido e chutar seria pior que omitir. */}
            {backendEnv && (
              <span
                className={`${styles.envTag} ${
                  backendEnv.is_demo
                    ? styles.envTagDemo
                    : backendEnv.is_production
                      ? styles.envTagProduction
                      : ""
                }`}
                title={`Backend em ${backendEnv.environment} · Print Server ${backendEnv.print_server_mode}`}
              >
                {backendEnv.environment}
              </span>
            )}
            <p className={styles.footerStatusItem}>
              <span className={`${styles.statusDot} ${usingRealData ? styles.statusDotOn : styles.statusDotOff}`} />
              {usingRealData ? "API conectada" : "Modo demonstração (dados fictícios)"}
            </p>
            <p className={styles.footerStatusItem}>
              <span className={`${styles.statusDot} ${usingRealMonthlyReport ? styles.statusDotOn : styles.statusDotOff}`} />
              {usingRealMonthlyReport ? "Relatório mensal real" : "Relatório mensal de demonstração"}
            </p>
            <p className={styles.footerStatusItem}>
              <span className={`${styles.statusDot} ${sessionVerified ? styles.statusDotOn : styles.statusDotOff}`} />
              {sessionVerified ? "Sessão verificada" : "Sessão não verificada"}
            </p>
          </div>
        </footer>
      </div>

      <PrinterDetailsModal printer={selectedPrinter} onClose={() => setSelectedPrinter(null)} />

      <Modal open={helpOpen} onClose={() => setHelpOpen(false)} title="Central de Ajuda" subtitle="Estamos aqui para ajudar">
        <div className={styles.helpList}>
          <a href="mailto:ti@elgin.com.br" className={styles.helpItem}>
            <Mail size={18} className={styles.helpIcon} />
            <div>
              <p className={styles.helpItemTitle}>Enviar e-mail para o suporte</p>
              <p className={styles.helpItemSubtitle}>ti@elgin.com.br</p>
            </div>
          </a>
          <button
            onClick={() => {
              setHelpOpen(false);
              push({ variant: "info", title: "Chat indisponível", description: "O chat de suporte ao vivo chega em breve." });
            }}
            className={`${styles.helpItem} ${styles.helpItemButton}`}
          >
            <MessageCircle size={18} className={styles.helpIcon} />
            <div>
              <p className={styles.helpItemTitle}>Abrir chat de suporte</p>
              <p className={styles.helpItemSubtitle}>Em breve</p>
            </div>
          </button>
          <div className={styles.helpNote}>
            <LifeBuoy size={18} className={styles.helpNoteIcon} />
            <p className={styles.helpNoteText}>
              Script de coleta e documentação em <code className={styles.helpCode}>scripts/Coletar-Impressoras.ps1</code>.
            </p>
          </div>
        </div>
      </Modal>
    </div>
  );
}
