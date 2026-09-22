/**
 * Estado compartilhado entre todas as rotas do painel — equivalente direto
 * do estado que antes vivia em App.tsx (SPA de página única) e descia via
 * props. Agora que a navegação usa rotas reais do Next.js, cada página é um
 * componente separado; este Context é o que permite que todas continuem
 * enxergando os mesmos dados (impressoras, filtros, conta logada, modal de
 * detalhes) sem re-buscar ou perder estado ao trocar de rota.
 *
 * Estado puramente de "chrome" (menu mobile aberto, modal de ajuda) continua
 * local ao AppShell — não precisa ser global.
 */
"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import {
  printers as mockPrinters,
  monthlyUsage as mockMonthlyUsage,
  departmentUsage as mockDepartmentUsage,
  decommissionedPrinters as mockDecommissionedPrinters,
} from "../data/printers";
import { logout as clearSession, restoreSession, type Account } from "./auth";
import {
  ApiError,
  discoverPrinters,
  fetchAlerts,
  fetchBackendEnvironment,
  fetchDataVersion,
  fetchPrintersWithStatus,
  fetchPrintServers,
  fetchUnreadNotificationCount,
  listUnits,
  markAlertRead,
  markAlertsRead,
  markAlertUnread,
  type BackendEnvironment,
} from "./api";
import { permissionsFor, type Permissions } from "./permissions";
import { adaptAlert, adaptPrinter, adaptPrintServer, adaptUnit, loadMonthlyReportFromApi } from "./adaptApi";
import { hostsDaUnidade, parseUnitScope, unitScope } from "./serverScope";
import { loadMonthlyReport, mergeMonthlyReport } from "./fetchMonthlyReport";
import { deriveAlerts, deriveGlobalToner } from "./deriveFromPrinters";
import { leituraVelha } from "./adaptApi";
import { DEFAULT_FILTERS, filterPrinters, type PrinterFilters } from "./filterPrinters";
import { useToast } from "./toast";
import type { Alert, DiscoveredPrinter, MonthlyReport, Printer, PrintServer, TonerLevel, Unit } from "../types";

interface AppDataContextValue {
  /** Conta logada (null quando anonimo). Fonte: GET /api/auth/me. */
  account: Account | null;
  isAuthenticated: boolean;
  /** true enquanto a sessao guardada ainda esta sendo confirmada no backend. */
  sessionLoading: boolean;
  /**
   * false quando ha token mas o backend nao respondeu para confirma-lo: a UI
   * abre em modo demonstracao e o papel exibido vem do cache local.
   */
  sessionVerified: boolean;
  /** Permissoes derivadas do papel — mesma hierarquia do backend. */
  can: Permissions;
  handleLoginSuccess: (loggedInAccount: Account, remember: boolean) => void;
  handleLogout: () => void;
  /**
   * Reflete no painel um perfil que o proprio dono acabou de alterar
   * (Fase 8, perfil e configuracoes). Nao refaz a carga de dados: so o nome
   * muda, e ele aparece no
   * Topbar/Sidebar imediatamente.
   */
  applyAccountUpdate: (updated: Account) => void;

  printers: Printer[];
  monthlyUsage: typeof mockMonthlyUsage;
  departmentUsage: typeof mockDepartmentUsage;
  decommissionedPrinters: typeof mockDecommissionedPrinters;
  usingRealData: boolean;
  usingRealMonthlyReport: boolean;
  /**
   * Ambiente informado pelo backend em GET /health (Fase 9). null = o
   * backend nao respondeu; "desconhecido" NAO deve ser tratado como
   * producao nem como demonstracao.
   */
  backendEnv: BackendEnvironment | null;
  /**
   * True quando ha numero ficticio na tela por QUALQUER motivo: a frota
   * inteira e de demonstracao, OU so o relatorio mensal caiu no mock. O
   * segundo caso e o que passava despercebido — frota real com grafico de
   * consumo inventado ao lado.
   */
  exibindoDadoFicticio: boolean;
  /**
   * True quando o ambiente e producao, ha sessao, e o que falta e dado real
   * (nao mock) — a faixa de aviso troca o texto de "dados de demonstracao"
   * para "sem dados reais", porque em producao nao ha numero ficticio na
   * tela para descrever.
   */
  semDadoRealEmProducao: boolean;
  initialLoading: boolean;
  /** Mensagem quando a API falhou; null quando os dados vieram do backend. */
  apiError: string | null;

  /**
   * Nao lidas na caixa pessoal (Fase 8). Vive aqui, e nao no Topbar, porque
   * duas telas dependem do mesmo numero: o badge do cabecalho e a pagina
   * /notifications. Marcar uma como lida na pagina chama
   * `refreshUnreadNotifications` e o badge acompanha na hora.
   */
  unreadNotifications: number;
  refreshUnreadNotifications: () => Promise<void>;

  /**
   * Escopo de servidor — o painel fala de UM Print Server por vez.
   *
   * `serverScope` e o host escolhido; `null` significa "todos os
   * servidores", `""` as impressoras cadastradas a mao (as que tem
   * `Printer.server === ""`, sem servidor de origem) e `"unit:<id>"` os
   * servidores de uma unidade (ver lib/serverScope.ts). Tudo o que descreve a
   * frota — `printers`, `activeFleet`, `stats`, `alerts`, toner,
   * departamentos — ja sai filtrado por ele, para que nenhuma tela precise
   * lembrar de aplicar o filtro (e nenhuma esqueca, que era o modo de isso
   * dar errado: contagem de um servidor ao lado da lista de todos).
   *
   * A escolha fica no dispositivo (localStorage), separada por conta: e
   * ponto de vista de quem esta olhando. Sem escolha salva, quem tem
   * unidade abre na propria unidade; quem nao tem, em "todos".
   */
  servers: PrintServer[];
  serversLoading: boolean;
  serversError: string | null;
  refreshServers: () => Promise<void>;
  serverScope: string | null;
  setServerScope: (scope: string | null) => void;
  /** Unidade em foco quando o escopo e `"unit:<id>"`; null nos demais. */
  scopeUnit: Unit | null;
  /**
   * Unidades cadastradas (GET /api/units, qualquer papel). Lista vazia
   * quando o backend ainda nao tem o recurso — o painel segue funcionando
   * so com escopo por servidor.
   */
  units: Unit[];
  refreshUnits: () => Promise<void>;
  /** Ativas por unidade, sobre a frota inteira (como `serverCounts`). */
  unitCounts: Record<number, number>;
  /**
   * Impressoras ATIVAS por escopo, sempre sobre a frota inteira e nunca
   * sobre o escopo atual — o seletor precisa dizer quantas ha em cada
   * servidor, inclusive nos que nao estao selecionados. Chave = host;
   * `""` = sem servidor.
   */
  serverCounts: Record<string, number>;
  /** Ativas na frota inteira, ignorando o escopo. */
  allActiveCount: number;

  filters: PrinterFilters;
  updateFilter: <K extends keyof PrinterFilters>(key: K, value: PrinterFilters[K]) => void;
  filteredPrinters: Printer[];
  departments: string[];

  /** Contagens da frota ATIVA (QA-02). `stale` = com leitura velha demais
   *  para descrever o presente; não descontado de `online` — ver o cálculo. */
  stats: { total: number; online: number; offline: number; attention: number; stale: number };
  /** Frota ativa: `printers` sem as desativadas. Base de `stats` e `filteredPrinters`. */
  activeFleet: Printer[];
  alerts: Alert[];
  globalToner: TonerLevel[] | undefined;
  worstPrinter: Printer | null;

  selectedPrinter: Printer | null;
  setSelectedPrinter: (printer: Printer | null) => void;
  handleAlertSelect: (alert: Alert) => void;
  /**
   * Alertas ainda nao marcados como lidos (conta so os reais do backend;
   * nos derivados de demonstracao, todos). Os badges de Sidebar/Topbar
   * podem trocar `alerts.length` por este valor.
   */
  unreadAlertCount: number;
  /** Marca/desmarca como lidos (otimista; desfaz e avisa se o backend recusar). */
  setAlertsRead: (alerts: Alert[], read: boolean) => Promise<void>;

  /**
   * Impressora aguardando confirmação da página de teste. Vive aqui, e o
   * diálogo é montado uma vez só no AppShell, porque dois lugares pedem o
   * teste — a tabela e o modal de detalhes — e o do modal abriria um
   * diálogo por cima de outro.
   */
  testPrintTarget: Printer | null;
  requestTestPrint: (printer: Printer) => void;
  closeTestPrint: () => void;

  scanning: boolean;
  lastChecked: Date;
  handleRefresh: () => Promise<void>;
  handleDiscovery: () => Promise<void>;
  discoveredPrinters: DiscoveredPrinter[] | null;
  discoverySource: string | null;
  discoveryServer: string | null;
  discoveryScanning: boolean;
}

const AppDataContext = createContext<AppDataContextValue | null>(null);

/**
 * Resultado da carga real. O motivo da falha importa: "unauthorized" (401)
 * significa sessao morta e leva ao logout; "offline" e indisponibilidade do
 * servidor e cai no conjunto de demonstracao sem derrubar a sessao.
 */
type LoadResult =
  | { ok: true; printers: Printer[]; alerts: Alert[]; monthlyReport: MonthlyReport | null }
  | { ok: false; reason: "unauthorized" | "offline" };

/** Carrega impressoras + alertas + relatorio mensal do backend, em paralelo. */
async function loadFromApi(): Promise<LoadResult> {
  try {
    const [apiPrinters, apiAlerts, monthlyReport] = await Promise.all([
      fetchPrintersWithStatus(),
      fetchAlerts(false).catch(() => [] as Awaited<ReturnType<typeof fetchAlerts>>),
      // Já devolve null quando o backend ainda não tem leituras suficientes
      // para fechar um mês — nesse caso o painel mostra o relatório de
      // demonstração e o cabeçalho sinaliza isso.
      loadMonthlyReportFromApi(),
    ]);
    return {
      ok: true,
      printers: apiPrinters.map(adaptPrinter),
      alerts: apiAlerts.map(adaptAlert),
      monthlyReport,
    };
  } catch (error) {
    const unauthorized = error instanceof ApiError && error.status === 401;
    return { ok: false, reason: unauthorized ? "unauthorized" : "offline" };
  }
}

/** Mensagem exibida quando a carga real nao aconteceu. */
const OFFLINE_MESSAGE = "Não foi possível conectar ao servidor. Exibindo dados de demonstração.";
const ANONYMOUS_MESSAGE = "Faça login para ver os dados reais da frota. Exibindo dados de demonstração.";

// Fase 13: atualizacao automatica em segundo plano. Mais frequente que o
// ciclo de coleta do backend (5min por padrao) para sempre pegar a leitura
// mais nova sem precisar clicar em nada ao trocar de aba.
const AUTO_REFRESH_INTERVAL_MS = 2 * 60 * 1000;

// 22/09/2026: além do recarregamento completo acima, pergunta a cada poucos
// segundos só a VERSÃO dos dados (resposta de poucos bytes). O backend lê o
// contador das impressoras online a cada 30s e sobe a versão quando algo
// muda; aqui a tela recarrega na hora em que a versão muda — uma folha
// impressa aparece em segundos, sem baixar a frota inteira o tempo todo.
const VERSION_CHECK_INTERVAL_MS = 10 * 1000;

/**
 * Escopo de servidor guardado por dispositivo.
 *
 * A AUSENCIA da chave e diferente de "todos": significa que ninguem
 * escolheu ainda, e ai o painel abre no servidor padrao em vez da frota
 * inteira. Por isso `lerEscopoSalvo` devolve tres coisas distintas —
 * `undefined` (nunca escolheu), `null` (escolheu "todos") e a string do
 * escopo —, e nao um `string | null` que confundiria os dois primeiros.
 */
// Chave por conta ("elgin_server_scope:<id>"). A antiga, global, valia para
// o dispositivo inteiro e impediria o padrao por unidade de valer para quem
// entra depois numa maquina compartilhada — ela e simplesmente ignorada.
const SERVER_SCOPE_KEY = "elgin_server_scope";
const ESCOPO_TODOS = "__todos__";

function chaveEscopo(userId: number): string {
  return `${SERVER_SCOPE_KEY}:${userId}`;
}

function lerEscopoSalvo(userId: number): string | null | undefined {
  try {
    const bruto = localStorage.getItem(chaveEscopo(userId));
    if (bruto === null) return undefined;
    return bruto === ESCOPO_TODOS ? null : bruto;
  } catch {
    // localStorage LANCA (nao devolve null) em navegador com dados de site
    // bloqueados por politica de dominio — mesmo motivo do try/catch em
    // lib/auth.ts. Sem escopo legivel, cai no padrao.
    return undefined;
  }
}

function salvarEscopo(userId: number, scope: string | null) {
  try {
    localStorage.setItem(chaveEscopo(userId), scope ?? ESCOPO_TODOS);
  } catch {
    // Preferencia de visualizacao: nao conseguir guardar nao e erro, a
    // sessao atual continua respeitando a escolha.
  }
}

export function AppDataProvider({ children }: { children: ReactNode }) {
  const [account, setAccount] = useState<Account | null>(null);
  const [sessionLoading, setSessionLoading] = useState(true);
  const [sessionVerified, setSessionVerified] = useState(false);
  const [rawPrinters, setRawPrinters] = useState<Printer[]>(mockPrinters);
  const [usingRealData, setUsingRealData] = useState(false);
  const [backendEnv, setBackendEnv] = useState<BackendEnvironment | null>(null);
  // Alertas vindos de /api/alerts; null enquanto o backend não respondeu.
  const [apiAlerts, setApiAlerts] = useState<Alert[] | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);
  const [monthlyReport, setMonthlyReport] = useState<Awaited<ReturnType<typeof loadMonthlyReport>>>(null);
  const [filters, setFilters] = useState<PrinterFilters>(DEFAULT_FILTERS);
  const [selectedPrinter, setSelectedPrinter] = useState<Printer | null>(null);
  const [testPrintTarget, setTestPrintTarget] = useState<Printer | null>(null);
  const [scanning, setScanning] = useState(false);
  const [discoveredPrinters, setDiscoveredPrinters] = useState<DiscoveredPrinter[] | null>(null);
  const [discoverySource, setDiscoverySource] = useState<string | null>(null);
  const [discoveryServer, setDiscoveryServer] = useState<string | null>(null);
  const [discoveryScanning, setDiscoveryScanning] = useState(false);
  const [lastChecked, setLastChecked] = useState<Date>(() => new Date());
  const [initialLoading, setInitialLoading] = useState(true);
  const [unreadNotifications, setUnreadNotifications] = useState(0);
  const [servers, setServers] = useState<PrintServer[]>([]);
  const [serversLoading, setServersLoading] = useState(false);
  const [serversError, setServersError] = useState<string | null>(null);
  const [serverScope, setServerScopeState] = useState<string | null>(null);
  const [units, setUnits] = useState<Unit[]>([]);
  // true quando GET /api/units ja respondeu (com sucesso OU falha) nesta
  // sessao. O escopo salvo so e conferido depois disso — conferir antes
  // descartaria um "unit:<id>" valido so porque a lista ainda nao chegou.
  const [unitsLoaded, setUnitsLoaded] = useState(false);
  // So a PRIMEIRA carga da lista adota o escopo salvo (ou o padrao da
  // unidade); as seguintes apenas conferem se o escopo ainda existe. Sem
  // isto, cada recarga da lista — e ela recarrega depois de todo sync —
  // jogaria a pessoa de volta ao padrao no meio do uso.
  const escopoRestaurado = useRef(false);
  const { push } = useToast();

  // Restauracao da sessao: o token guardado so vale se o backend confirmar
  // em GET /api/auth/me. 401/403 (token invalido ou conta desativada) limpam
  // a sessao dentro de restoreSession(); servidor fora do ar mantem o token e
  // devolve status "unverified".
  // O limite existe porque `fetch` NAO tem timeout proprio: quando o
  // backend nao responde nem recusa (firewall que descarta o pacote em vez
  // de recusar a conexao, ou NEXT_PUBLIC_API_URL apontando para um
  // 127.0.0.1 que so existe na maquina de quem abriu o painel), a promessa
  // simplesmente nunca resolve. Sem isto, `sessionLoading` ficava `true`
  // para sempre e a tela parava em "Restaurando sessao..." — sem erro, sem
  // log, sem saida.
  //
  // 8s e folgado para um GET /api/auth/me, que le uma linha do SQLite.
  // Estourado o prazo, `restoreSession` trata o abort como falha de rede e
  // devolve "unverified" (com cache) ou "anonymous" — ou seja, cai na tela
  // de login, que e um estado em que da para agir.
  const SESSION_TIMEOUT_MS = 8000;

  useEffect(() => {
    let cancelled = false;
    const controller = new AbortController();
    const prazo = setTimeout(() => controller.abort(), SESSION_TIMEOUT_MS);

    const encerrar = (session: Awaited<ReturnType<typeof restoreSession>> | null) => {
      if (cancelled) return;
      if (!session || session.status === "anonymous") {
        setAccount(null);
        setSessionVerified(false);
      } else {
        setAccount(session.account);
        setSessionVerified(session.status === "authenticated");
      }
      setSessionLoading(false);
    };

    restoreSession(controller.signal)
      .then(encerrar)
      // `.catch` NAO e redundante com o try/catch de restoreSession: as
      // leituras de storage acontecem ANTES dele (getToken), e um navegador
      // com dados de site bloqueados por politica faz `localStorage` LANCAR
      // em vez de devolver null. A promessa entao rejeitava, este `.then`
      // nunca rodava, e o resultado era o mesmo spinner eterno — por uma
      // causa completamente diferente da de cima.
      .catch(() => encerrar(null))
      .finally(() => clearTimeout(prazo));

    return () => {
      cancelled = true;
      clearTimeout(prazo);
      controller.abort();
    };
  }, []);

  // Em ambiente de producao, autenticado, sem dado real: mostra vazio em vez
  // de mockup. Fora de producao (dev/demo) ou antes do login, o mockup
  // continua normalmente — so em producao um numero ficticio poderia ser
  // confundido com o estado real da frota.
  const semDadoRealEmProducao = account !== null && !!backendEnv?.is_production;

  // Impressoras de fato usadas pela UI: base (mock ou real) + monthlyPages
  // do relatório mensal real, quando disponível. Derivado (não é estado)
  // para não depender da ordem em que os dois fetches abaixo terminam.
  const allPrinters = useMemo(() => {
    if (!usingRealData && semDadoRealEmProducao) return [];
    return mergeMonthlyReport(rawPrinters, monthlyReport);
  }, [rawPrinters, monthlyReport, usingRealData, semDadoRealEmProducao]);

  /**
   * O escopo em vigor. So vale sobre dado real: a frota de demonstracao tem
   * `server: ""` em todas as linhas (data/printers.ts diz isso de
   * proposito, ela nao vem de Print Server nenhum), entao aplicar um escopo
   * de servidor ali esvaziaria a tela inteira sem que houvesse nada errado.
   */
  const escopoEfetivo = usingRealData ? serverScope : null;

  const scopeUnitId = parseUnitScope(serverScope);
  const scopeUnit = useMemo(
    () => (scopeUnitId === null ? null : (units.find((u) => u.id === scopeUnitId) ?? null)),
    [units, scopeUnitId],
  );

  /** Hosts de cada unidade, ja unindo as duas fontes (ver hostsDaUnidade). */
  const hostsPorUnidade = useMemo(() => {
    const mapa = new Map<number, Set<string>>();
    for (const u of units) mapa.set(u.id, hostsDaUnidade(u, u.id, servers));
    return mapa;
  }, [units, servers]);

  /**
   * A frota do escopo em foco — e ESTA que todas as telas consomem.
   * `allPrinters` nao sai daqui, tirando as contagens abaixo, que precisam
   * justamente ignorar o escopo para poder descreve-lo.
   */
  const printers = useMemo(() => {
    if (escopoEfetivo === null) return allPrinters;
    const unidade = parseUnitScope(escopoEfetivo);
    if (unidade !== null) {
      const hosts = hostsPorUnidade.get(unidade) ?? hostsDaUnidade(undefined, unidade, servers);
      return allPrinters.filter((p) => p.server !== "" && hosts.has(p.server));
    }
    return allPrinters.filter((p) => p.server === escopoEfetivo);
  }, [allPrinters, escopoEfetivo, hostsPorUnidade, servers]);

  const serverCounts = useMemo(() => {
    const contagem: Record<string, number> = {};
    for (const p of allPrinters) {
      if (!p.active) continue;
      contagem[p.server] = (contagem[p.server] ?? 0) + 1;
    }
    return contagem;
  }, [allPrinters]);

  const allActiveCount = useMemo(() => allPrinters.filter((p) => p.active).length, [allPrinters]);

  const unitCounts = useMemo(() => {
    const contagem: Record<number, number> = {};
    for (const [id, hosts] of hostsPorUnidade) {
      let total = 0;
      for (const h of hosts) total += serverCounts[h] ?? 0;
      contagem[id] = total;
    }
    return contagem;
  }, [hostsPorUnidade, serverCounts]);
  const monthlyUsage =
    monthlyReport && monthlyReport.monthlyUsage.length > 0
      ? monthlyReport.monthlyUsage
      : semDadoRealEmProducao
        ? []
        : mockMonthlyUsage;
  // Mesma regra do monthlyUsage: departamento real (Fase 12, backend) quando
  // disponivel, vazio em producao sem dado, mockup nos demais casos.
  const departmentUsage =
    monthlyReport && monthlyReport.departmentUsage.length > 0
      ? monthlyReport.departmentUsage
      : semDadoRealEmProducao
        ? []
        : mockDepartmentUsage;
  // Fase 18: nao precisa de outro fetch — "inativa" ja e Printer.active,
  // que ja esta em `printers`. Derivado do mesmo array, sem round-trip novo.
  const decommissionedPrinters = useMemo(() => {
    if (usingRealData) {
      return printers
        .filter((p) => !p.active)
        .map((p) => ({ ip: p.ip, model: p.model, department: p.department, deactivatedAt: p.updatedAt ?? null }));
    }
    return semDadoRealEmProducao ? [] : mockDecommissionedPrinters;
  }, [printers, usingRealData, semDadoRealEmProducao]);
  const usingRealMonthlyReport = !!monthlyReport && monthlyReport.monthlyUsage.length > 0;
  // Um so dos dois basta para haver numero ficticio na tela. Antes desta fase
  // a faixa olhava apenas usingRealData, entao "frota real + relatorio mensal
  // mock" — o caso comum, porque o backend precisa de leituras suficientes
  // para fechar um mes — nao acendia aviso nenhum.
  const exibindoDadoFicticio = !usingRealData || !usingRealMonthlyReport;

  // Carga dos dados reais. Roda DEPOIS que a sessao foi resolvida e so
  // quando ha usuario — e re-roda quando a conta muda (login/troca de
  // usuario), que era exatamente o que faltava: antes o fetch acontecia uma
  // unica vez no mount, entao logar depois de cair no fallback deixava o
  // painel preso nos dados de demonstracao.
  //
  // A dependencia e o e-mail (string estavel), nao o objeto `account`, para
  // nao refazer a carga a cada re-render do provider.
  const accountKey = account?.email ?? null;
  const accountId = account?.id ?? null;
  const accountUnitId = account?.unitId ?? null;

  /**
   * Lista de Print Servers. Vive aqui, e nao no NetworkView, porque agora
   * duas coisas dependem dela: a tela de mapeamento e o seletor de escopo
   * do cabecalho — e as duas precisam concordar sobre qual servidor esta em
   * foco. GET /api/servers exige apenas sessao ativa (qualquer papel).
   */
  const refreshServers = useCallback(async () => {
    if (!accountKey) {
      setServers([]);
      setServersError(null);
      return;
    }
    setServersLoading(true);
    try {
      setServers((await fetchPrintServers()).map(adaptPrintServer));
      setServersError(null);
    } catch (error) {
      setServers([]);
      setServersError(error instanceof Error ? error.message : "Falha ao carregar os Print Servers.");
    } finally {
      setServersLoading(false);
    }
  }, [accountKey]);

  useEffect(() => {
    if (sessionLoading) return;
    void refreshServers();
  }, [sessionLoading, refreshServers]);

  /**
   * Unidades. Falha em SILENCIO de proposito: um backend sem o recurso (ou
   * fora do ar) so deixa o painel sem escopo por unidade — exatamente como
   * ele funcionava antes — e nao merece toast a cada carga.
   */
  const refreshUnits = useCallback(async () => {
    if (!accountKey) {
      setUnits([]);
      setUnitsLoaded(false);
      return;
    }
    try {
      setUnits((await listUnits()).map(adaptUnit));
    } catch {
      setUnits([]);
    } finally {
      setUnitsLoaded(true);
    }
  }, [accountKey]);

  useEffect(() => {
    if (sessionLoading) return;
    void refreshUnits();
  }, [sessionLoading, refreshUnits]);

  // Outra conta (ou nenhuma): o escopo e por pessoa, entao a proxima sessao
  // restaura o DELA em vez de herdar o da anterior. Precisa vir antes do
  // efeito de reconciliacao abaixo — os dois rodam no mesmo commit.
  useEffect(() => {
    escopoRestaurado.current = false;
    setServerScopeState(null);
  }, [accountId]);

  // Reconcilia o escopo com as listas que chegaram do backend.
  useEffect(() => {
    if (servers.length === 0 || !unitsLoaded || accountId === null) return;

    // `""` (sem servidor) e um escopo legitimo e nao esta na lista de
    // servidores — conferir a lista o descartaria como inexistente.
    const existe = (escopo: string) => {
      if (escopo === "") return true;
      const unidade = parseUnitScope(escopo);
      if (unidade !== null) return units.some((u) => u.id === unidade);
      return servers.some((s) => s.host === escopo);
    };
    // Padrao: a unidade da conta, quando ela tem uma que ainda existe;
    // senao, a frota inteira.
    const padrao =
      accountUnitId !== null && units.some((u) => u.id === accountUnitId) ? unitScope(accountUnitId) : null;

    if (!escopoRestaurado.current) {
      escopoRestaurado.current = true;
      const salvo = lerEscopoSalvo(accountId);
      setServerScopeState(salvo === undefined ? padrao : salvo !== null && existe(salvo) ? salvo : padrao);
      return;
    }

    // Servidor ou unidade excluidos enquanto a aba estava aberta: volta ao
    // padrao em vez de deixar o painel preso num escopo que nao existe mais
    // — o que apareceria como frota vazia, sem explicacao nenhuma na tela.
    setServerScopeState((atual) => (atual !== null && !existe(atual) ? padrao : atual));
  }, [servers, units, unitsLoaded, accountId, accountUnitId]);

  const setServerScope = useCallback(
    (scope: string | null) => {
      escopoRestaurado.current = true;
      setServerScopeState(scope);
      if (accountId !== null) salvarEscopo(accountId, scope);
    },
    [accountId],
  );

  // Ambiente do backend: uma vez, no mount, sem depender de sessao. Precisa
  // valer ANTES do login para que a tela de entrada de uma instancia de
  // demonstracao ja se anuncie como tal.
  useEffect(() => {
    let cancelled = false;
    fetchBackendEnvironment().then((env) => {
      if (!cancelled) setBackendEnv(env);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (sessionLoading) return;

    let cancelled = false;

    // Anonimo: nao ha token para enviar, entao nem tentamos a API — o painel
    // do login fica com o conjunto de demonstracao, claramente rotulado.
    if (!accountKey) {
      setRawPrinters(mockPrinters);
      setApiAlerts(null);
      setUsingRealData(false);
      setApiError(ANONYMOUS_MESSAGE);
      setMonthlyReport(null);
      setInitialLoading(false);
      // Sem sessão só a tela de login é renderizada e nada consome o relatório
      // mensal. Buscar aqui o /data/monthly-report.json legado (que nada gera
      // mais) só servia para deixar um 404 no console da tela de login.
      return;
    }

    setInitialLoading(true);
    // Ou tudo vem da API, ou tudo vem das fontes de demonstração — nunca uma
    // mistura das duas, para que o indicador do cabeçalho seja verdadeiro.
    const printersDone = loadFromApi().then(async (result) => {
      if (cancelled) return;

      if (result.ok) {
        setRawPrinters(result.printers);
        setApiAlerts(result.alerts);
        setMonthlyReport(result.monthlyReport);
        setUsingRealData(true);
        setApiError(null);
        // A carga foi feita com o token e o backend aceitou: uma sessao que
        // tinha ficado "nao verificada" (servidor fora do ar na abertura)
        // esta confirmada agora.
        setSessionVerified(true);
        return;
      }

      if (result.reason === "unauthorized") {
        // O token expirou ou foi revogado entre a confirmacao da sessao e a
        // carga: volta ao estado nao autenticado em vez de fingir demo.
        expireSession();
        return;
      }

      // Backend fora do ar: dados de demonstração, incluindo o relatório
      // mensal do coletor PowerShell (se estiver publicado) ou o mock.
      setRawPrinters(mockPrinters);
      setApiAlerts(null);
      setUsingRealData(false);
      setApiError(OFFLINE_MESSAGE);
      const report = await loadMonthlyReport();
      if (!cancelled && report) setMonthlyReport(report);
    });
    // Skeleton de carregamento inicial: some assim que o carregamento
    // decidir (real ou fallback pro mock), com um piso mínimo pra não
    // "piscar" quando a resposta vem instantânea demais.
    Promise.allSettled([printersDone, new Promise((r) => window.setTimeout(r, 400))]).then(() => {
      if (!cancelled) setInitialLoading(false);
    });
    return () => {
      cancelled = true;
    };
  }, [sessionLoading, accountKey]);

  /**
   * Fase 13: atualizacao automatica — antes so "Verificar agora" (clique
   * manual) re-buscava os dados; sem ele, uma aba aberta ficava com o que
   * carregou no login ate a pessoa lembrar de atualizar. Ao contrario do
   * clique manual, este ciclo fica em SILENCIO de proposito:
   *
   *   - sem toast, sem spinner — ninguem quer aviso a cada 2 minutos;
   *   - uma falha passageira MANTEM o ultimo dado bom, nao cai para o
   *     mockup — um unico ciclo de rede ruim nao pode virar o painel
   *     inteiro em modo demonstracao sozinho (isso so acontece na carga
   *     inicial ou no "Verificar agora" manual, onde faz sentido avisar);
   *   - pausa quando a aba esta em segundo plano (nao gasta requisicao a
   *     toa com a tela fechada) e atualiza na hora ao voltar o foco, caso
   *     tenha passado mais tempo que o intervalo.
   */
  useEffect(() => {
    if (sessionLoading || !accountKey) return;

    let cancelled = false;

    async function tick() {
      if (cancelled || document.hidden) return;
      const result = await loadFromApi();
      if (cancelled) return;

      if (result.ok) {
        setRawPrinters(result.printers);
        setApiAlerts(result.alerts);
        setMonthlyReport(result.monthlyReport);
        setUsingRealData(true);
        setApiError(null);
        setSessionVerified(true);
        setLastChecked(new Date());
      } else if (result.reason === "unauthorized") {
        expireSession();
      }
      // "offline": fica quieto, mantem o ultimo dado bom na tela.
    }

    // Versão vista por último; null = ainda não perguntou (a carga inicial já
    // trouxe os dados, então a primeira resposta só registra o número).
    let versaoVista: number | null = null;
    let recarregando = false;
    async function checarVersao() {
      if (cancelled || document.hidden || recarregando) return;
      try {
        const { version } = await fetchDataVersion();
        if (cancelled) return;
        if (versaoVista !== null && version !== versaoVista) {
          recarregando = true;
          try {
            await tick();
          } finally {
            recarregando = false;
          }
        }
        versaoVista = version;
      } catch {
        // Backend fora ou sessão expirada: o tick completo de 2 min trata.
      }
    }

    const intervalId = window.setInterval(() => void tick(), AUTO_REFRESH_INTERVAL_MS);
    const versionId = window.setInterval(() => void checarVersao(), VERSION_CHECK_INTERVAL_MS);
    void checarVersao();
    function handleVisibilityChange() {
      if (!document.hidden) void tick();
    }
    document.addEventListener("visibilitychange", handleVisibilityChange);

    return () => {
      cancelled = true;
      window.clearInterval(intervalId);
      window.clearInterval(versionId);
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [sessionLoading, accountKey]);

  /**
   * Recarrega o contador. Falha em SILENCIO de proposito: sem backend (modo
   * demonstracao) ou sem sessao, o badge simplesmente some. Um toast de erro
   * a cada carga de pagina por causa de um contador seria ruido.
   */
  const refreshUnreadNotifications = useCallback(async () => {
    if (!accountKey) {
      setUnreadNotifications(0);
      return;
    }
    try {
      setUnreadNotifications((await fetchUnreadNotificationCount()).unread);
    } catch {
      setUnreadNotifications(0);
    }
  }, [accountKey]);

  useEffect(() => {
    if (sessionLoading) return;
    void refreshUnreadNotifications();
  }, [sessionLoading, refreshUnreadNotifications]);

  /**
   * A frota que está sendo monitorada AGORA.
   *
   * QA-02: `printers` carrega também as impressoras com `active === false`
   * — as que sumiram do Print Server no último sync e cujo registro é
   * preservado de propósito (Fase 18). Contá-las junto fazia o painel
   * anunciar "80 online" onde havia 8 impressoras ativas, usando a última
   * leitura de cada uma das 72 restantes, algumas de semanas atrás, como se
   * fosse o estado do momento.
   *
   * A separação fica aqui, e não em cada tela, para que contagem e filtro
   * usem a MESMA base: se `stats` excluísse as inativas mas a listagem não,
   * a aba "Online 8" abriria uma lista de 80.
   *
   * `printers` continua completo para quem precisa do histórico: a lista de
   * desativadas (relatórios), a matriz de histórico e os alertas.
   */
  const activeFleet = useMemo(() => printers.filter((p) => p.active), [printers]);

  const stats = useMemo(() => {
    const total = activeFleet.length;
    const online = activeFleet.filter((p) => p.status === "online").length;
    const offline = activeFleet.filter((p) => p.status === "offline").length;
    const attention = activeFleet.filter((p) => p.status === "atencao").length;
    // Leitura velha demais para descrever o presente. NÃO é descontado de
    // `online` de propósito: decidir se "sem coleta recente" deve aparecer
    // como offline, como um quarto estado, ou apenas como aviso muda o que
    // o painel AFIRMA sobre a frota, e é decisão de produto, não de código.
    // Exposto aqui para a tela poder sinalizar sem que ninguém precise
    // recalcular a regra.
    const stale = activeFleet.filter((p) =>
      leituraVelha(p.lastSeenAt ?? null, backendEnv?.collection_interval_minutes ?? null),
    ).length;
    return { total, online, offline, attention, stale };
  }, [activeFleet, backendEnv]);

  // Alertas reais do backend quando ele responde; senão, os derivados dos
  // dados de demonstração (mesmo comportamento de antes).
  // O escopo tambem vale para alerta: um painel que anuncia "elgjunprt" no
  // cabecalho nao pode ter no sino um alerta de impressora de outro
  // servidor. Os derivados do mock ja nascem escopados (saem de `printers`);
  // os do backend chegam da frota inteira e sao filtrados aqui.
  const alerts = useMemo(() => {
    if (apiAlerts === null) return deriveAlerts(printers);
    if (escopoEfetivo === null) return apiAlerts;
    const noEscopo = new Set(printers.map((p) => p.id));
    return apiAlerts.filter((a) => noEscopo.has(a.printerId));
  }, [apiAlerts, printers, escopoEfetivo]);
  const unreadAlertCount = useMemo(() => alerts.filter((a) => !a.readAt).length, [alerts]);
  // Resumo de toner e "pior impressora" sobre a frota ATIVA, como `stats`
  // (QA-02): sobre `printers`, uma impressora que sumiu do Print Server havia
  // semanas podia virar o "Toner baixo" do Dashboard com uma leitura velha.
  const globalToner = useMemo(() => deriveGlobalToner(activeFleet) ?? undefined, [activeFleet]);
  // Sobre activeFleet, não sobre printers: a listagem precisa bater com as
  // contagens das abas de status (QA-02).
  const filteredPrinters = useMemo(() => filterPrinters(activeFleet, filters), [activeFleet, filters]);
  const departments = useMemo(() => Array.from(new Set(printers.map((p) => p.department))).sort(), [printers]);
  const worstPrinter = useMemo(() => {
    const withToner = activeFleet.filter((p) => p.toner && p.toner.length > 0);
    if (withToner.length === 0) return null;
    return withToner.reduce((worst, p) => {
      const worstPct = Math.min(...worst.toner!.map((t) => t.percent));
      const pPct = Math.min(...p.toner!.map((t) => t.percent));
      return pPct < worstPct ? p : worst;
    });
  }, [activeFleet]);

  function updateFilter<K extends keyof PrinterFilters>(key: K, value: PrinterFilters[K]) {
    setFilters((f) => ({ ...f, [key]: value }));
  }

  // O token/conta ja foram persistidos por lib/auth.login() antes deste
  // callback; a conta vem do proprio backend (resposta do login). Trocar o
  // `account` dispara o efeito acima, que carrega os dados reais.
  function handleLoginSuccess(loggedInAccount: Account, _remember: boolean) {
    setAccount(loggedInAccount);
    setSessionVerified(true);
  }

  /**
   * Encerra a sessao: logout explicito ou 401 do backend (token expirado /
   * revogado). Alem de limpar a credencial, devolve o painel ao conjunto de
   * demonstracao — sem sessao nao ha dados reais para exibir, e a proxima
   * conta nao pode enxergar a frota carregada pela anterior.
   */
  function expireSession() {
    clearSession();
    setAccount(null);
    setSessionVerified(false);
    setRawPrinters(mockPrinters);
    setApiAlerts(null);
    setMonthlyReport(null);
    setUsingRealData(false);
    setApiError(ANONYMOUS_MESSAGE);
    setDiscoveredPrinters(null);
    setDiscoverySource(null);
    setDiscoveryServer(null);
    // Servidores e unidades sao dado autenticado como qualquer outro. O
    // escopo escolhido NAO e apagado do storage de proposito: e preferencia
    // da conta neste dispositivo e sobrevive ao proximo login dela.
    setServers([]);
    setServersError(null);
    setUnits([]);
    setUnitsLoaded(false);
  }

  function handleLogout() {
    expireSession();
  }

  async function handleRefresh() {
    setScanning(true);
    const started = Date.now();
    const result = await loadFromApi();
    const elapsed = Date.now() - started;
    if (elapsed < 1100) await new Promise((r) => window.setTimeout(r, 1100 - elapsed));

    if (result.ok) {
      setRawPrinters(result.printers);
      setApiAlerts(result.alerts);
      setMonthlyReport(result.monthlyReport);
      setUsingRealData(true);
      setApiError(null);
      setSessionVerified(true);
      push({ variant: "success", title: "Dados atualizados", description: `${result.printers.length} impressora(s) carregada(s) do servidor.` });
    } else if (result.reason === "unauthorized") {
      expireSession();
      push({ variant: "warning", title: "Sessão expirada", description: "Faça login novamente para continuar." });
    } else {
      setRawPrinters(mockPrinters);
      setApiAlerts(null);
      setUsingRealData(false);
      setApiError(OFFLINE_MESSAGE);
      setMonthlyReport(await loadMonthlyReport());
      push({
        variant: "info",
        title: "Servidor indisponível",
        description: "Exibindo dados de demonstração. Verifique se o backend está rodando.",
      });
    }
    setLastChecked(new Date());
    setScanning(false);
  }

  async function handleDiscovery() {
    setDiscoveryScanning(true);
    try {
      const data = await discoverPrinters();
      setDiscoveredPrinters(data.printers.map((printer) => ({
        name: printer.name,
        server: printer.server,
        portName: printer.port_name,
        ip: printer.ip,
        driverName: printer.driver_name,
        source: printer.source,
        ipResolution: printer.ip_resolution,
        ipGroupSize: printer.ip_group_size,
        networkQueryReused: printer.network_query_reused,
        reachable: printer.reachable,
        snmpResponded: printer.snmp_responded,
        status: printer.status,
        statusReason: printer.status_reason,
        pageCount: printer.page_count,
        uptime: printer.uptime,
        toners: printer.toners.map((toner) => ({ color: toner.color, percent: toner.percent, description: toner.description })),
        error: printer.error,
      })));
      setDiscoverySource(data.source);
      setDiscoveryServer(data.server);
      push({ variant: "success", title: "Rede consultada", description: `${data.count} fila(s) encontrada(s) em ${data.server}.` });
    } catch (error) {
      setDiscoveredPrinters(null);
      setDiscoverySource(null);
      setDiscoveryServer(null);

      if (error instanceof ApiError && error.status === 401) {
        expireSession();
        push({ variant: "warning", title: "Sessão expirada", description: "Faça login novamente para continuar." });
      } else if (error instanceof ApiError && error.status === 403) {
        // Papel insuficiente (ou conta desativada): o backend recusou a acao,
        // mas a sessao continua valida — nunca deslogar por 403.
        push({ variant: "warning", title: "Sem permissão", description: error.message });
      } else {
        push({ variant: "warning", title: "Falha na descoberta", description: error instanceof Error ? error.message : "Não foi possível consultar o Print Server." });
      }
    } finally {
      setDiscoveryScanning(false);
    }
  }

  function handleAlertSelect(alert: Alert) {
    const printer = printers.find((p) => p.id === alert.printerId);
    if (printer) setSelectedPrinter(printer);
  }

  // "Marcar como lido" dos alertas. Otimista: atualiza a lista na hora e
  // volta ao estado anterior se o backend recusar. So mexe em alertas reais
  // (id numerico); os derivados da demonstracao nao tem onde gravar.
  async function setAlertsRead(targets: Alert[], read: boolean) {
    const reais = targets.filter((a) => a.readAt !== undefined && /^\d+$/.test(a.id));
    const mudar = reais.filter((a) => (read ? !a.readAt : !!a.readAt));
    if (mudar.length === 0) return;
    const ids = new Set(mudar.map((a) => a.id));
    const anterior = apiAlerts;
    const agora = new Date().toISOString();
    const leitor = account?.name || account?.email || null;
    setApiAlerts((atual) =>
      atual === null
        ? atual
        : atual.map((a) => (ids.has(a.id) ? { ...a, readAt: read ? agora : null, readBy: read ? leitor : null } : a)),
    );
    try {
      if (!read) {
        await Promise.all(mudar.map((a) => markAlertUnread(Number(a.id))));
      } else if (mudar.length === 1) {
        const salvo = adaptAlert(await markAlertRead(Number(mudar[0].id)));
        setApiAlerts((atual) => (atual === null ? atual : atual.map((a) => (a.id === salvo.id ? salvo : a))));
      } else {
        await markAlertsRead(mudar.map((a) => Number(a.id)));
      }
    } catch (error) {
      setApiAlerts(anterior);
      push({
        variant: "warning",
        title: "Não foi possível atualizar o alerta",
        description: error instanceof Error ? error.message : "Tente novamente.",
      });
    }
  }

  const applyAccountUpdate = useCallback((updated: Account) => setAccount(updated), []);

  const can = useMemo(() => permissionsFor(account?.role ?? null), [account?.role]);

  const value: AppDataContextValue = {
    account,
    isAuthenticated: account !== null,
    sessionLoading,
    sessionVerified,
    can,
    handleLoginSuccess,
    handleLogout,
    applyAccountUpdate,

    printers,
    monthlyUsage,
    departmentUsage,
    decommissionedPrinters,
    usingRealData,
    usingRealMonthlyReport,
    activeFleet,
    backendEnv,
    exibindoDadoFicticio,
    semDadoRealEmProducao,
    initialLoading,
    apiError,

    unreadNotifications,
    refreshUnreadNotifications,

    servers,
    serversLoading,
    serversError,
    refreshServers,
    serverScope,
    setServerScope,
    scopeUnit,
    units,
    refreshUnits,
    unitCounts,
    serverCounts,
    allActiveCount,

    filters,
    updateFilter,
    filteredPrinters,
    departments,

    stats,
    alerts,
    globalToner,
    worstPrinter,

    selectedPrinter,
    setSelectedPrinter,
    handleAlertSelect,
    unreadAlertCount,
    setAlertsRead,

    testPrintTarget,
    // Fecha o modal de detalhes ao pedir o teste: a confirmação ocupa o
    // lugar dele em vez de empilhar dois diálogos.
    requestTestPrint: (printer: Printer) => {
      setSelectedPrinter(null);
      setTestPrintTarget(printer);
    },
    closeTestPrint: () => setTestPrintTarget(null),

    scanning,
    lastChecked,
    handleRefresh,
    handleDiscovery,
    discoveredPrinters,
    discoverySource,
    discoveryServer,
    discoveryScanning,
  };

  return <AppDataContext.Provider value={value}>{children}</AppDataContext.Provider>;
}

export function useAppData(): AppDataContextValue {
  const ctx = useContext(AppDataContext);
  if (!ctx) throw new Error("useAppData must be used within AppDataProvider");
  return ctx;
}
