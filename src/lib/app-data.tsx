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

import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import {
  printers as mockPrinters,
  monthlyUsage as mockMonthlyUsage,
  departmentUsage,
  decommissionedPrinters,
} from "../data/printers";
import { logout as clearSession, readStoredAccount, type Account } from "./auth";
import { fetchAlerts, fetchPrintersWithStatus } from "./api";
import { adaptAlert, adaptPrinter, loadMonthlyReportFromApi } from "./adaptApi";
import { loadMonthlyReport, mergeMonthlyReport } from "./fetchMonthlyReport";
import { deriveAlerts, deriveGlobalToner } from "./deriveFromPrinters";
import { DEFAULT_FILTERS, filterPrinters, type PrinterFilters } from "./filterPrinters";
import { useToast } from "./toast";
import type { Alert, MonthlyReport, Printer, TonerLevel } from "../types";

interface AppDataContextValue {
  account: Account | null;
  handleLoginSuccess: (loggedInAccount: Account, remember: boolean) => void;
  handleLogout: () => void;

  printers: Printer[];
  monthlyUsage: typeof mockMonthlyUsage;
  departmentUsage: typeof departmentUsage;
  decommissionedPrinters: typeof decommissionedPrinters;
  usingRealData: boolean;
  usingRealMonthlyReport: boolean;
  initialLoading: boolean;
  /** Mensagem quando a API falhou; null quando os dados vieram do backend. */
  apiError: string | null;

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
  handleScan: () => Promise<void>;
}

const AppDataContext = createContext<AppDataContextValue | null>(null);

/**
 * Carrega impressoras + alertas do backend em paralelo. Devolve null quando a
 * API não responde, para o provider cair no conjunto de demonstração em vez
 * de deixar o painel vazio.
 */
async function loadFromApi(): Promise<{
  printers: Printer[];
  alerts: Alert[];
  monthlyReport: MonthlyReport | null;
} | null> {
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
      printers: apiPrinters.map(adaptPrinter),
      alerts: apiAlerts.map(adaptAlert),
      monthlyReport,
    };
  } catch {
    return null;
  }
}

export function AppDataProvider({ children }: { children: ReactNode }) {
  const [account, setAccount] = useState<Account | null>(null);
  const [rawPrinters, setRawPrinters] = useState<Printer[]>(mockPrinters);
  const [usingRealData, setUsingRealData] = useState(false);
  // Alertas vindos de /api/alerts; null enquanto o backend não respondeu.
  const [apiAlerts, setApiAlerts] = useState<Alert[] | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);
  const [monthlyReport, setMonthlyReport] = useState<Awaited<ReturnType<typeof loadMonthlyReport>>>(null);
  const [filters, setFilters] = useState<PrinterFilters>(DEFAULT_FILTERS);
  const [selectedPrinter, setSelectedPrinter] = useState<Printer | null>(null);
  const [scanning, setScanning] = useState(false);
  const [lastChecked, setLastChecked] = useState<Date>(() => new Date());
  const [initialLoading, setInitialLoading] = useState(true);
  const { push } = useToast();

  useEffect(() => {
    setAccount(readStoredAccount());
  }, []);

  // Impressoras de fato usadas pela UI: base (mock ou real) + monthlyPages
  // do relatório mensal real, quando disponível. Derivado (não é estado)
  // para não depender da ordem em que os dois fetches abaixo terminam.
  const printers = useMemo(() => mergeMonthlyReport(rawPrinters, monthlyReport), [rawPrinters, monthlyReport]);
  const monthlyUsage = monthlyReport && monthlyReport.monthlyUsage.length > 0 ? monthlyReport.monthlyUsage : mockMonthlyUsage;
  const usingRealMonthlyReport = !!monthlyReport && monthlyReport.monthlyUsage.length > 0;

  useEffect(() => {
    let cancelled = false;
    // Ou tudo vem da API, ou tudo vem das fontes de demonstração — nunca uma
    // mistura das duas, para que o indicador do cabeçalho seja verdadeiro.
    const printersDone = loadFromApi().then(async (data) => {
      if (cancelled) return;

      if (data) {
        setRawPrinters(data.printers);
        setApiAlerts(data.alerts);
        setMonthlyReport(data.monthlyReport);
        setUsingRealData(true);
        setApiError(null);
        return;
      }

      // Backend fora do ar: dados de demonstração, incluindo o relatório
      // mensal do coletor PowerShell (se estiver publicado) ou o mock.
      setApiError("Não foi possível conectar ao servidor. Exibindo dados de demonstração.");
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
  }, []);

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

  // O token/conta ja foram persistidos por lib/auth.login() antes deste callback.
  function handleLoginSuccess(loggedInAccount: Account, _remember: boolean) {
    setAccount(loggedInAccount);
  }

  function handleLogout() {
    clearSession();
    setAccount(null);
  }

  async function handleScan() {
    setScanning(true);
    const started = Date.now();
    const data = await loadFromApi();
    const elapsed = Date.now() - started;
    if (elapsed < 1100) await new Promise((r) => window.setTimeout(r, 1100 - elapsed));

    if (data) {
      setRawPrinters(data.printers);
      setApiAlerts(data.alerts);
      setMonthlyReport(data.monthlyReport);
      setUsingRealData(true);
      setApiError(null);
      push({ variant: "success", title: "Dados atualizados", description: `${data.printers.length} impressora(s) carregada(s) do servidor.` });
    } else {
      setApiError("Não foi possível conectar ao servidor. Exibindo dados de demonstração.");
      push({
        variant: "info",
        title: "Servidor indisponível",
        description: "Exibindo dados de demonstração. Verifique se o backend está rodando.",
      });
    }
    setLastChecked(new Date());
    setScanning(false);
  }

  function handleAlertSelect(alert: Alert) {
    const printer = printers.find((p) => p.id === alert.printerId);
    if (printer) setSelectedPrinter(printer);
  }

  const value: AppDataContextValue = {
    account,
    handleLoginSuccess,
    handleLogout,

    printers,
    monthlyUsage,
    departmentUsage,
    decommissionedPrinters,
    usingRealData,
    usingRealMonthlyReport,
    initialLoading,
    apiError,

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
    handleScan,
  };

  return <AppDataContext.Provider value={value}>{children}</AppDataContext.Provider>;
}

export function useAppData(): AppDataContextValue {
  const ctx = useContext(AppDataContext);
  if (!ctx) throw new Error("useAppData must be used within AppDataProvider");
  return ctx;
}
