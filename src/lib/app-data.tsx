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

import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
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
  fetchPrintersWithStatus,
  fetchUnreadNotificationCount,
  type BackendEnvironment,
} from "./api";
import { permissionsFor, type Permissions } from "./permissions";
import { adaptAlert, adaptPrinter, loadMonthlyReportFromApi } from "./adaptApi";
import { loadMonthlyReport, mergeMonthlyReport } from "./fetchMonthlyReport";
import { deriveAlerts, deriveGlobalToner } from "./deriveFromPrinters";
import { DEFAULT_FILTERS, filterPrinters, type PrinterFilters } from "./filterPrinters";
import { useToast } from "./toast";
import type { Alert, DiscoveredPrinter, MonthlyReport, Printer, TonerLevel } from "../types";

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

  filters: PrinterFilters;
  updateFilter: <K extends keyof PrinterFilters>(key: K, value: PrinterFilters[K]) => void;
  filteredPrinters: Printer[];
  departments: string[];

  stats: { total: number; online: number; offline: number; attention: number };
  alerts: Alert[];
  globalToner: TonerLevel[] | undefined;
  worstPrinter: Printer | null;

  selectedPrinter: Printer | null;
  setSelectedPrinter: (printer: Printer | null) => void;
  handleAlertSelect: (alert: Alert) => void;

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
  const [scanning, setScanning] = useState(false);
  const [discoveredPrinters, setDiscoveredPrinters] = useState<DiscoveredPrinter[] | null>(null);
  const [discoverySource, setDiscoverySource] = useState<string | null>(null);
  const [discoveryServer, setDiscoveryServer] = useState<string | null>(null);
  const [discoveryScanning, setDiscoveryScanning] = useState(false);
  const [lastChecked, setLastChecked] = useState<Date>(() => new Date());
  const [initialLoading, setInitialLoading] = useState(true);
  const [unreadNotifications, setUnreadNotifications] = useState(0);
  const { push } = useToast();

  // Restauracao da sessao: o token guardado so vale se o backend confirmar
  // em GET /api/auth/me. 401/403 (token invalido ou conta desativada) limpam
  // a sessao dentro de restoreSession(); servidor fora do ar mantem o token e
  // devolve status "unverified".
  useEffect(() => {
    let cancelled = false;
    restoreSession().then((session) => {
      if (cancelled) return;
      if (session.status === "anonymous") {
        setAccount(null);
        setSessionVerified(false);
      } else {
        setAccount(session.account);
        setSessionVerified(session.status === "authenticated");
      }
      setSessionLoading(false);
    });
    return () => {
      cancelled = true;
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
  const printers = useMemo(() => {
    if (!usingRealData && semDadoRealEmProducao) return [];
    return mergeMonthlyReport(rawPrinters, monthlyReport);
  }, [rawPrinters, monthlyReport, usingRealData, semDadoRealEmProducao]);
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
      setInitialLoading(false);
      loadMonthlyReport().then((report) => {
        if (!cancelled && report) setMonthlyReport(report);
      });
      return () => {
        cancelled = true;
      };
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

    const intervalId = window.setInterval(() => void tick(), AUTO_REFRESH_INTERVAL_MS);
    function handleVisibilityChange() {
      if (!document.hidden) void tick();
    }
    document.addEventListener("visibilitychange", handleVisibilityChange);

    return () => {
      cancelled = true;
      window.clearInterval(intervalId);
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

  const stats = useMemo(() => {
    const total = printers.length;
    const online = printers.filter((p) => p.status === "online").length;
    const offline = printers.filter((p) => p.status === "offline").length;
    const attention = printers.filter((p) => p.status === "atencao").length;
    return { total, online, offline, attention };
  }, [printers]);

  // Alertas reais do backend quando ele responde; senão, os derivados dos
  // dados de demonstração (mesmo comportamento de antes).
  const alerts = useMemo(
    () => apiAlerts ?? deriveAlerts(printers),
    [apiAlerts, printers],
  );
  const globalToner = useMemo(() => deriveGlobalToner(printers) ?? undefined, [printers]);
  const filteredPrinters = useMemo(() => filterPrinters(printers, filters), [printers, filters]);
  const departments = useMemo(() => Array.from(new Set(printers.map((p) => p.department))).sort(), [printers]);
  const worstPrinter = useMemo(() => {
    const withToner = printers.filter((p) => p.toner && p.toner.length > 0);
    if (withToner.length === 0) return null;
    return withToner.reduce((worst, p) => {
      const worstPct = Math.min(...worst.toner!.map((t) => t.percent));
      const pPct = Math.min(...p.toner!.map((t) => t.percent));
      return pPct < worstPct ? p : worst;
    });
  }, [printers]);

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
    backendEnv,
    exibindoDadoFicticio,
    semDadoRealEmProducao,
    initialLoading,
    apiError,

    unreadNotifications,
    refreshUnreadNotifications,

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
