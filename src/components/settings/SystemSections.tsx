"use client";

/**
 * Seções informativas: Coleta e servidores, Notificações e Sobre o sistema.
 *
 * Tudo aqui é SOMENTE LEITURA e sai de dados que o painel já carrega:
 * GET /health (`backendEnv`, público), a lista de Print Servers e a de
 * unidades (ambas do AppDataProvider). Nenhum secret é exibido — do webhook
 * chega só o host, nunca a URL (ela carrega assinatura). Onde há algo a
 * fazer, a seção aponta para a tela que de fato executa a ação.
 */
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import type { Account } from "../../lib/auth";
import { API_BASE_URL, type BackendEnvironment } from "../../lib/api";
import { useAppData } from "../../lib/app-data";
import type { PrintServer } from "../../types";
import styles from "../SettingsView.module.css";
import { Card, Fact, FactList, StatusPill } from "./ui";

const AMBIENTE_LABEL: Record<BackendEnvironment["environment"], string> = {
  production: "Produção",
  demo: "Demonstração",
  development: "Desenvolvimento",
};

function tempoRelativo(iso: string | null): string {
  if (!iso) return "nunca";
  const ms = Date.now() - new Date(iso).getTime();
  if (Number.isNaN(ms)) return "desconhecido";
  const min = Math.round(ms / 60000);
  if (min < 1) return "agora há pouco";
  if (min < 60) return `há ${min} min`;
  const h = Math.round(min / 60);
  if (h < 24) return `há ${h} h`;
  const d = Math.round(h / 24);
  return d === 1 ? "há 1 dia" : `há ${d} dias`;
}

function BackendIndisponivel() {
  return (
    <p className={styles.note}>
      O backend não respondeu à consulta de status. As informações aparecem aqui assim que ele voltar.
    </p>
  );
}

function ServerStatus({ server }: { server: PrintServer }) {
  if (!server.active) return <StatusPill tone="neutral">Desativado</StatusPill>;
  if (server.lastStatus === "online") return <StatusPill tone="ok">Online</StatusPill>;
  if (server.lastStatus === "error") return <StatusPill tone="danger">Com erro</StatusPill>;
  return <StatusPill tone="neutral">Sem contato ainda</StatusPill>;
}

export function CollectionSection() {
  const { backendEnv, servers, serversLoading, serversError, can } = useAppData();

  return (
    <>
      <Card
        title="Coleta de dados"
        description="Como o backend lê as impressoras. Definido na configuração do servidor, não pelo painel."
        readOnly
      >
        {backendEnv ? (
          <FactList>
            <Fact
              label="Intervalo de coleta"
              value={
                backendEnv.collection_interval_minutes
                  ? `A cada ${backendEnv.collection_interval_minutes} min`
                  : "Não informado"
              }
              hint="Uma leitura mais antiga que alguns ciclos é mostrada como desatualizada."
            />
            <Fact
              label="Leitura das impressoras"
              value={
                backendEnv.mock_collect_enabled ? (
                  <StatusPill tone="warn">Simulada</StatusPill>
                ) : (
                  <StatusPill tone="ok">Real (SNMP)</StatusPill>
                )
              }
              hint={
                backendEnv.mock_collect_enabled
                  ? "Os contadores e níveis de toner são gerados pelo backend, não lidos das impressoras."
                  : "Contadores e toner vêm direto das impressoras pela rede."
              }
            />
            <Fact
              label="Print Server"
              value={
                backendEnv.print_server_mode === "real" ? (
                  <StatusPill tone="ok">Real</StatusPill>
                ) : (
                  <StatusPill tone="warn">Simulado</StatusPill>
                )
              }
              hint={
                backendEnv.print_server_mode === "real"
                  ? "A lista de impressoras é consultada nos servidores Windows cadastrados."
                  : "A lista de impressoras dos servidores é simulada pelo backend."
              }
            />
          </FactList>
        ) : (
          <BackendIndisponivel />
        )}
      </Card>

      <Card
        title="Print Servers cadastrados"
        description="Situação da última consulta a cada servidor."
        readOnly
        footer={
          can.canAdmin ? (
            <Link href="/network" className={styles.secondaryButton}>
              Gerenciar servidores
              <ArrowRight size={16} />
            </Link>
          ) : undefined
        }
      >
        {serversLoading && servers.length === 0 ? (
          <p className={styles.hint}>Carregando servidores...</p>
        ) : serversError && servers.length === 0 ? (
          <p className={styles.note}>Não foi possível carregar a lista de servidores: {serversError}</p>
        ) : servers.length === 0 ? (
          <p className={styles.note}>Nenhum Print Server cadastrado.</p>
        ) : (
          <ul className={styles.itemList}>
            {servers.map((s) => (
              <li key={s.id} className={styles.item}>
                <div className={styles.itemMain}>
                  <span className={styles.itemTitle}>{s.name || s.host}</span>
                  <span className={styles.itemMeta}>
                    <span className={styles.mono}>{s.host}</span>
                    {s.unitName && <> · {s.unitName}</>}
                    {" · "}
                    {s.activePrinterCount} impressora{s.activePrinterCount === 1 ? "" : "s"} ativa
                    {s.activePrinterCount === 1 ? "" : "s"}
                    {" · "}sincronizado {tempoRelativo(s.lastSyncAt)}
                  </span>
                  {s.lastStatus === "error" && s.lastError && (
                    <span className={styles.itemError}>{s.lastError}</span>
                  )}
                </div>
                <ServerStatus server={s} />
              </li>
            ))}
          </ul>
        )}
      </Card>
    </>
  );
}

export function NotificationsSection({ account }: { account: Account }) {
  const { units, unreadNotifications, can } = useAppData();

  // Espelha services/units.py (notification_recipients): quem não tem
  // unidade (TI central) recebe o sino de todas as impressoras; quem tem,
  // das impressoras da própria unidade e das que não têm unidade.
  const alcance = account.unitName
    ? `impressoras da unidade ${account.unitName} e das que não pertencem a nenhuma unidade`
    : "todas as impressoras, porque sua conta é da TI central";

  const unidadesAtivas = units.filter((u) => u.active);

  return (
    <>
      <Card
        title="Como os alertas chegam até você"
        description="As regras de envio são fixas no backend; aqui só estão explicadas."
        readOnly
      >
        <FactList>
          <Fact
            label="Sino do painel"
            value="Impressora offline e toner baixo"
            hint={`Você recebe alertas de ${alcance}.`}
          />
          <Fact
            label="Canal do Teams"
            value="Somente toner baixo"
            hint="Vai para o webhook central e, se houver, para o da unidade da impressora. Impressora offline não é enviada ao Teams, para não lotar o canal."
          />
          <Fact
            label="Não lidas agora"
            value={unreadNotifications}
            hint={
              <>
                Veja e marque como lidas em <Link href="/notifications">Notificações</Link>.
              </>
            }
          />
        </FactList>
      </Card>

      {unidadesAtivas.length > 0 && (
        <Card
          title="Webhook por unidade"
          description="Unidades sem webhook próprio recebem os alertas só pelo canal central."
          readOnly
          footer={
            can.canAdmin ? (
              <>
                <Link href="/notifications" className={styles.secondaryButton}>
                  Testar alerta central
                </Link>
                <Link href="/units" className={styles.secondaryButton}>
                  Configurar unidades
                  <ArrowRight size={16} />
                </Link>
              </>
            ) : undefined
          }
        >
          <ul className={styles.itemList}>
            {unidadesAtivas.map((u) => (
              <li key={u.id} className={styles.item}>
                <div className={styles.itemMain}>
                  <span className={styles.itemTitle}>{u.name}</span>
                  {can.canAdmin && u.webhookConfigured && u.webhookHost && (
                    <span className={styles.itemMeta}>
                      <span className={styles.mono}>{u.webhookHost}</span>
                    </span>
                  )}
                </div>
                {u.webhookConfigured ? (
                  <StatusPill tone="ok">Webhook próprio</StatusPill>
                ) : (
                  <StatusPill tone="neutral">Só canal central</StatusPill>
                )}
              </li>
            ))}
          </ul>
        </Card>
      )}
    </>
  );
}

export function AboutSection() {
  const { backendEnv, can } = useAppData();

  return (
    <>
      <Card title="Versão e ambiente" readOnly>
        {backendEnv ? (
          <FactList>
            <Fact
              label="Versão do backend"
              value={backendEnv.version ? <span className={styles.mono}>{backendEnv.version}</span> : "Não informada"}
            />
            <Fact
              label="Ambiente"
              value={
                <StatusPill tone={backendEnv.is_production ? "ok" : "warn"}>
                  {AMBIENTE_LABEL[backendEnv.environment]}
                </StatusPill>
              }
              hint={
                backendEnv.is_demo
                  ? "Instância de demonstração: os números na tela não são da frota real."
                  : backendEnv.is_production
                    ? undefined
                    : "Ambiente de testes da equipe de TI."
              }
            />
            {/* Não é secret: o navegador envia este endereço em toda requisição.
                Vazio é o modo proxy, não "não configurado". */}
            <Fact
              label="Endereço da API"
              value={
                <span className={`${styles.mono} ${styles.breakable}`}>
                  {API_BASE_URL || "Mesmo endereço do painel (proxy)"}
                </span>
              }
              hint={
                API_BASE_URL
                  ? "Definido na publicação do painel."
                  : "O painel repassa as chamadas ao backend pelo próprio servidor."
              }
            />
          </FactList>
        ) : (
          <BackendIndisponivel />
        )}
      </Card>

      {can.canAdmin && (
        <Card
          title="Administração"
          description="Nada crítico é editado nesta página: cada ação vive na tela que a explica e pede confirmação. Chaves, credenciais e URLs de webhook ficam no arquivo .env do backend e nunca aparecem na interface."
        >
          <nav aria-label="Telas de administração" className={styles.linkList}>
            <Link href="/users" className={styles.linkRow}>
              <span className={styles.itemMain}>
                <span className={styles.itemTitle}>Usuários</span>
                <span className={styles.itemMeta}>Criar contas, alterar perfis de acesso, ativar e desativar.</span>
              </span>
              <ArrowRight size={16} aria-hidden="true" />
            </Link>
            <Link href="/units" className={styles.linkRow}>
              <span className={styles.itemMain}>
                <span className={styles.itemTitle}>Unidades</span>
                <span className={styles.itemMeta}>Agrupar servidores e pessoas e definir o webhook de cada região.</span>
              </span>
              <ArrowRight size={16} aria-hidden="true" />
            </Link>
            <Link href="/network" className={styles.linkRow}>
              <span className={styles.itemMain}>
                <span className={styles.itemTitle}>Print Servers</span>
                <span className={styles.itemMeta}>Registrar servidores, descobrir impressoras e sincronizar o cadastro.</span>
              </span>
              <ArrowRight size={16} aria-hidden="true" />
            </Link>
          </nav>
        </Card>
      )}
    </>
  );
}
