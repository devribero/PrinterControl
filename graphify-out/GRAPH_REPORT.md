# Graph Report - PrinterControl  (2026-08-20)

## Corpus Check
- 125 files · ~70,495 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1042 nodes · 1926 edges · 73 communities (54 shown, 19 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 81 edges (avg confidence: 0.57)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `92fb1071`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- .collect
- package.json
- Main.ps1
- Elgin Impressoras (painel de monitoramento)
- database.py
- Coletar-Impressoras.ps1
- compilerOptions
- collect.py
- toast.tsx
- ComingSoon.tsx
- plugins
- HistoryMatrix.tsx
- graphify (knowledge graph tool)
- next.config.ts
- Elgin (Brand)
- PrinterControl Favicon Icon
- npm run build
- npm run dev
- next-env.d.ts
- navIds.ts
- MockSNMPScenarios
- Alert
- tests_collect_api.py
- printers.py
- Sidebar.tsx
- collect_fleet
- PrinterReading
- adaptApi.ts
- app-data.tsx
- routes/auth.py
- enrich_discovered_printers
- api.ts
- Settings
- app/page.tsx
- useAppData
- Simular-Ambiente.ps1
- SNMPClient
- cn
- PrinterCollector
- types.ts
- PLANO DE IMPLEMENTAÇÃO — ESCANEAR REDE REAL
- tests_printer_sync.py
- Impressoras
- Guia de Uso do PrinterControl
- unhandled_exception_handler
- AlertsView.tsx
- Printer
- printers.ts
- Guia do Desenvolvedor
- theme.tsx
- tests_printers_crud.py
- filterPrinters.ts
- Login.tsx
- Alert
- Printer
- Printer
- Fluxo de Dados
- Arquitetura de Deploy
- PrinterTable
- RecordingThreadPoolExecutor
- Modo Simulado
- FEATURE_MATRIX.md
- BaseModel
- get
- post
- Session
- User

## God Nodes (most connected - your core abstractions)
1. `Printer` - 42 edges
2. `SNMPClient` - 33 edges
3. `cn()` - 31 edges
4. `Printer` - 26 edges
5. `PrinterCollector` - 24 edges
6. `enrich_discovered_printers()` - 23 edges
7. `PrinterReading` - 22 edges
8. `useAppData()` - 21 edges
9. `Elgin Impressoras (painel de monitoramento)` - 20 edges
10. `PLANO DE IMPLEMENTAÇÃO — ESCANEAR REDE REAL` - 19 edges

## Surprising Connections (you probably didn't know these)
- `printer()` --calls--> `DiscoveredPrinter`  [EXTRACTED]
  backend/tests_discovery_snmp.py → src/types.ts
- `require_user()` --calls--> `decode_token()`  [INFERRED]
  backend/app/dependencies.py → backend/app/services/auth.py
- `Lucide` --conceptually_related_to--> `Elgin Impressoras (painel de monitoramento)`  [EXTRACTED]
  README.md → CONTEXTO-DESENVOLVIMENTO.md
- `React` --conceptually_related_to--> `Elgin Impressoras (painel de monitoramento)`  [EXTRACTED]
  README.md → CONTEXTO-DESENVOLVIMENTO.md
- `Recharts` --conceptually_related_to--> `Elgin Impressoras (painel de monitoramento)`  [EXTRACTED]
  README.md → CONTEXTO-DESENVOLVIMENTO.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Comandos do CLI graphify (query/path/explain/update)** — claude_graphify, claude_graphify_query, claude_graphify_path, claude_graphify_explain, claude_graphify_update [EXTRACTED 1.00]
- **Stack tecnológico do painel (Vite/React/TS/Tailwind/Recharts/Lucide)** — readme_vite, readme_react, readme_typescript, readme_tailwind_css_v4, readme_recharts, readme_lucide [EXTRACTED 1.00]
- **Arquitetura de dados de 3 modos (Demo/Real/Simulado)** — contexto_desenvolvimento_elgin_impressoras, contexto_desenvolvimento_modo_demo, contexto_desenvolvimento_modo_real, contexto_desenvolvimento_modo_simulado [EXTRACTED 1.00]

## Communities (73 total, 19 thin omitted)

### Community 0 - ".collect"
Cohesion: 0.20
Nodes (9): _base_page_count(), _increment(), SNMPResult, TonerInfo, Contador inicial plausivel para uma impressora que nunca foi lida., Paginas impressas entre duas coletas — fixo por impressora, 5 a 124., Nivel do toner: base do perfil + desvio deterministico por impressora/cor,…, _toner() (+1 more)

### Community 1 - "package.json"
Cohesion: 0.06
Nodes (31): lucide-react, next, oxlint, dependencies, lucide-react, next, react, react-dom (+23 more)

### Community 2 - "Main.ps1"
Cohesion: 0.13
Nodes (29): Atualizar-ImpressorasAsync(), Build-ListaExibicaoAgrupada(), Build-SnmpGet(), Build-SnmpGetBulk(), Convert-SnmpValueBytes(), Get-ImpressorasEmpresa(), Get-TonerSNMP(), Import-Tabela() (+21 more)

### Community 3 - "Elgin Impressoras (painel de monitoramento)"
Cohesion: 0.10
Nodes (21): Tela Alertas, Tela Dashboard, Elgin Impressoras (painel de monitoramento), Tela Histórico, Tela Impressoras, Tela Login, Migração futura para FastAPI (Python) + Next.js + banco de dados, Modo claro/escuro (toggle) (+13 more)

### Community 4 - "database.py"
Cohesion: 0.10
Nodes (22): AsyncIOScheduler, create_db_and_tables(), _finish_printer_migration(), _migrate_alert_type(), _migrate_printer_schema(), _migrate_reading_uptime(), Recria `printers` (schema atual) e copia `printers_old` para dentro dela, numa…, Adiciona alerts.alert_type em bancos criados antes da Etapa 8A. (+14 more)

### Community 5 - "Coletar-Impressoras.ps1"
Cohesion: 0.21
Nodes (13): Build-SnmpGet(), Build-SnmpGetBulk(), Convert-SnmpValueBytes(), Get-ImpressorasServidor(), Get-TonerSNMP(), Parse-SnmpBulkResponse(), Parse-SnmpCounter(), Parse-SnmpInt() (+5 more)

### Community 6 - "compilerOptions"
Cohesion: 0.06
Nodes (30): dom, dom.iterable, esnext, .next/dev/types/**/*.ts, next-env.d.ts, .next/types/**/*.ts, node_modules, **/*.ts (+22 more)

### Community 7 - "collect.py"
Cohesion: 0.10
Nodes (25): get_session(), Session, User, Dependencias compartilhadas pelas rotas. Autenticacao: `require_user` protege…, Usuario dono do JWT do header Authorization. 401 se ausente/invalido., require_user(), get_alert(), list_alerts() (+17 more)

### Community 8 - "toast.tsx"
Cohesion: 0.22
Nodes (7): ToastContext, ToastContextValue, ToastItem, ToastProvider(), ToastVariant, VARIANT_COLOR, VARIANT_ICON

### Community 10 - "plugins"
Cohesion: 0.22
Nodes (8): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, typescript, warn

### Community 11 - "HistoryMatrix.tsx"
Cohesion: 0.27
Nodes (5): HistoryPage(), HistoryMatrix(), HistoryMatrixProps, getDepartmentLabel(), getPrinterSite()

### Community 12 - "graphify (knowledge graph tool)"
Cohesion: 0.25
Nodes (8): graphify (knowledge graph tool), graphify explain command, graphify path command, graphify query command, graphify update command, graphify-out/graph.json, graphify-out/GRAPH_REPORT.md, graphify-out/wiki/index.md

### Community 20 - "MockSNMPScenarios"
Cohesion: 0.12
Nodes (15): MockSNMPScenarios, SNMPResult, TonerInfo, SNMP responde o contador, mas nao expoe a tabela de consumiveis., Monocromatica com toner em 5%., Colorida com ciano critico (18%) e os demais normais., Contador reiniciado (troca de placa/formatador): page_count baixo., Devolve o resultado fixo do cenario (ip e is_color sao ignorados). (+7 more)

### Community 21 - "Alert"
Cohesion: 0.14
Nodes (13): Alert, SQLModel, TonerHistory, profile_for(), Simulador de frota — APENAS PARA TESTE LOCAL. Diferenca para snmp_mock.py: la…, Perfil deterministico da impressora: online | offline | snmp_mudo | baixo |…, active(), collect() (+5 more)

### Community 22 - "tests_collect_api.py"
Cohesion: 0.67
Nodes (3): check(), main(), Teste ponta a ponta dos endpoints /api/collect com os cenarios simulados.…

### Community 28 - "printers.py"
Cohesion: 0.12
Nodes (30): create_printer(), create_printer_reading(), get_printer(), get_printer_readings(), list_printers(), list_printers_with_status(), monthly_report(), get (+22 more)

### Community 29 - "Sidebar.tsx"
Cohesion: 0.16
Nodes (15): AlertsDonutCard(), AlertsDonutCardProps, PagesConsumedCard(), TotalPrintsCard(), NavItem(), NavItemProps, Sidebar(), SidebarProps (+7 more)

### Community 30 - "collect_fleet"
Cohesion: 0.25
Nodes (11): collect_fleet(), collect_printer(), CollectRequest, CollectResponse, FleetCollectResponse, BaseModel, post, Session (+3 more)

### Community 31 - "PrinterReading"
Cohesion: 0.13
Nodes (20): PrinterReading, _active(), evaluate_reading(), Session, Alertas automaticos (Etapa 8A). Roda logo apos cada PrinterReading ser…, Cria, mantem ou resolve o alerta de uma condicao. Retorna a acao tomada., Avalia uma leitura e sincroniza os alertas da impressora. Faz commit ao final.…, _sync_condition() (+12 more)

### Community 32 - "adaptApi.ts"
Cohesion: 0.24
Nodes (10): adaptPrinter(), ApiMonthlyReport, formatLastSeen(), toStatus(), toToner(), VALID_COLORS, VALID_STATUS, ApiAlert (+2 more)

### Community 33 - "app-data.tsx"
Cohesion: 0.18
Nodes (16): adaptAlert(), loadMonthlyReportFromApi(), discoverPrinters(), fetchAlerts(), fetchPrintersWithStatus(), AppDataContext, AppDataProvider(), handleDiscovery() (+8 more)

### Community 34 - "routes/auth.py"
Cohesion: 0.23
Nodes (14): login(), post, Session, register(), Config, BaseModel, TokenResponse, UserCreate (+6 more)

### Community 35 - "enrich_discovered_printers"
Cohesion: 0.10
Nodes (31): discover(), DiscoveredPrinterResponse, DiscoverResponse, get_current_server(), Print Server (Etapa 3) — descoberta pura, sem tocar no banco. Sincronizar o…, Descobre e sincroniza com o banco (Etapa 4): cria impressoras novas, atualiza…, Print Server configurado e modo ativo (mock ou real)., Descobre as impressoras publicadas no Print Server configurado (equivalente a… (+23 more)

### Community 36 - "api.ts"
Cohesion: 0.11
Nodes (19): handleSubmit(), api, API_BASE_URL, ApiDiscoveredPrinter, ApiDiscoveredToner, ApiDiscoveryResponse, ApiError, ApiPrinterReading (+11 more)

### Community 37 - "Settings"
Cohesion: 0.20
Nodes (8): Config, field_validator, Normaliza um DATABASE_URL sqlite relativo (ex.: sqlite:///./x.db) para um…, Settings, Caminho do arquivo .db atual, se o banco for SQLite em disco (nao :memory:)., _sqlite_backup_path(), BaseSettings, Path

### Community 38 - "app/page.tsx"
Cohesion: 0.25
Nodes (5): StatCard(), StatCardProps, StatCardsProps, TONE, NAV_ROUTES

### Community 39 - "useAppData"
Cohesion: 0.17
Nodes (13): react, DashboardPage(), TonerPage(), AppShell(), AuthGate(), Login(), ModalProps, Topbar() (+5 more)

### Community 40 - "Simular-Ambiente.ps1"
Cohesion: 0.16
Nodes (6): Modo Real, Contador mensal calculado por diff de duas leituras SNMP acumulativas (não existe OID de páginas do mês), Scripts PowerShell reais nunca rodaram de verdade (sem interpretador PowerShell no ambiente de dev), public/data/monthly-report.json, public/data/printers.json, Arquivos de dados gerados são ignorados pelo git — gerar/apagar localmente nunca afeta o repositório

### Community 41 - "SNMPClient"
Cohesion: 0.05
Nodes (38): parse_varbinds(), SNMP Collector para impressoras. Porte direto da funcao Get-TonerSNMP de…, Decodifica um OID BER para notacao pontuada., Decodifica bytes BER como inteiro sem sinal., Extrai a lista de varbinds de uma resposta SNMP. Percorre a estrutura completa…, Cliente SNMP para coleta de impressoras (Printer-MIB, RFC 3805)., Coleta status, contador de paginas e toners de uma impressora. Nunca levanta…, PS1: `if ($ip -match '^\\d')` — descarta 'N/A' e nomes de porta. (+30 more)

### Community 42 - "cn"
Cohesion: 0.14
Nodes (18): Modal(), PrinterDetailsModal(), config, PrinterStatusBadge(), PAGE_SIZE_OPTIONS, RightPanel(), classify(), FILTERS (+10 more)

### Community 43 - "PrinterCollector"
Cohesion: 0.08
Nodes (28): list_scenarios(), Cenarios simulados disponiveis e se o modo mock esta habilitado., PrinterCollector, Session, SNMPResult, Converte SNMPResult em PrinterReading. Toner ausente vira NULL (a coluna e…, Cenarios de teste disponiveis (fonte unica: snmp_mock.SCENARIOS)., Coleta uma impressora e grava o resultado como PrinterReading. (+20 more)

### Community 44 - "types.ts"
Cohesion: 0.26
Nodes (9): BottomChartsProps, DiscoveryResults(), DiscoveryResultsProps, statusLabel(), MonthlyCountersProps, DiscoveredPrinter, MonthlyPageCount, MonthlyUsage (+1 more)

### Community 45 - "PLANO DE IMPLEMENTAÇÃO — ESCANEAR REDE REAL"
Cohesion: 0.05
Nodes (39): A. Endpoint (implementado), Alertas, Arquitetura atual, Arquitetura do PrinterControl, B. Service reutilizável, Banco, C. Funções Print Server reutilizáveis, Cliente de API (+31 more)

### Community 46 - "tests_printer_sync.py"
Cohesion: 0.07
Nodes (29): discover_printers(), DiscoveredPrinter, _mock_discover(), PrintServerError, Exception, Camada de Print Server (Etapa 3). Reproduz a descoberta de impressoras do…, Equivalente exato de Get-ImpressorasEmpresa + o inicio de Process-…, Descobre as impressoras publicadas no Print Server configurado. Levanta… (+21 more)

### Community 47 - "Impressoras"
Cohesion: 0.06
Nodes (31): Alertas, Autenticação, Coleta, Diagnóstico, Escanear Rede (implementado), `GET /`, `GET /api/alerts`, `GET /api/alerts/{alert_id}` (+23 more)

### Community 48 - "Guia de Uso do PrinterControl"
Cohesion: 0.10
Nodes (20): Acessar via web — PARCIAL, Adicionar impressora — AUSENTE/PARCIAL, Alertas — FUNCIONAL na leitura; PARCIAL nas ações, Ações, Como acessar, Configurações — COMING SOON, Configurações, Usuários e Integrações — COMING SOON, Dashboard — FUNCIONAL/PARCIAL (+12 more)

### Community 49 - "unhandled_exception_handler"
Cohesion: 0.40
Nodes (5): Exception, Erro nao tratado: o detalhe vai para o log do servidor, o cliente recebe apenas…, unhandled_exception_handler(), exception_handler, Request

### Community 50 - "AlertsView.tsx"
Cohesion: 0.31
Nodes (5): AlertsPage(), AlertBannerProps, AlertsView(), AlertsViewProps, Alert

### Community 51 - "Printer"
Cohesion: 0.23
Nodes (11): PrinterDetailsModalProps, PrinterRanking(), PrinterRankingProps, RankedPrinter, RankList(), rankPrinters(), RightPanelProps, TonerMonitoringProps (+3 more)

### Community 52 - "printers.ts"
Cohesion: 0.12
Nodes (18): Levantamento_impressões (planilha original), ReportsPage(), DecommissionedList(), DecommissionedListProps, DepartmentBreakdown(), DepartmentBreakdownProps, MONTHS, MonthlyCounters() (+10 more)

### Community 53 - "Guia do Desenvolvedor"
Cohesion: 0.13
Nodes (14): Backend, Banco, Comandos do frontend, Escanear Rede (implementado), Guia do Desenvolvedor, O que não executar em produção sem autorização, Print Server, Riscos conhecidos (+6 more)

### Community 54 - "theme.tsx"
Cohesion: 0.16
Nodes (10): ibmPlexMono, metadata, publicSans, sourceSerif, Providers(), getInitialTheme(), Theme, ThemeContext (+2 more)

### Community 55 - "tests_printers_crud.py"
Cohesion: 0.33
Nodes (3): Etapa 12 - CRUD de impressoras contra o servidor rodando. Usa o banco REAL,…, Devolve (status, payload)., request()

### Community 56 - "filterPrinters.ts"
Cohesion: 0.36
Nodes (7): PrinterTableProps, DEFAULT_FILTERS, filterPrinters(), PrinterFilters, getPrinterType(), PrinterType, PrinterStatus

### Community 57 - "Login.tsx"
Cohesion: 0.17
Nodes (10): Logo Elgin é redesenho à mão (IA sem acesso a imagens coladas no chat, só uploads), src/components/ (padrão com header-comment por arquivo), ElginLogo(), ElginLogoProps, ACTIVE_NODES, features, LoginProps, NETWORK_LINKS (+2 more)

### Community 61 - "Printer"
Cohesion: 0.35
Nodes (8): Printer, PrinterMonthly, SQLModel, Etapa 4: identidade e (server, name), NAO ip — o Print Server permite varias…, SQLModel, User, hash_password(), seed_database()

### Community 62 - "Fluxo de Dados"
Cohesion: 0.17
Nodes (11): 10. Escanear Rede (implementado), 1. Cadastro no SQLite, 2. Coleta SNMP real, 3. Coleta de frota, 4. Print Server, 5. Sincronização, 6. Alertas, 7. Relatório mensal (+3 more)

### Community 63 - "Arquitetura de Deploy"
Cohesion: 0.18
Nodes (10): Arquitetura avaliada, Arquitetura de Deploy, Autenticação, Bloqueios atuais, Cloudflare Tunnel, Configuração de aplicação, CORS, Estado atual (+2 more)

## Knowledge Gaps
- **241 isolated node(s):** ``POST /api/auth/login``, ``POST /api/auth/register``, ``GET /api/printers``, ``GET /api/printers/with-status``, ``GET /api/printers/monthly-report`` (+236 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DiscoveredPrinter` connect `types.ts` to `app-data.tsx`, `enrich_discovered_printers`, `Printer`?**
  _High betweenness centrality (0.264) - this node is a cross-community bridge._
- **Why does `printer()` connect `enrich_discovered_printers` to `types.ts`?**
  _High betweenness centrality (0.262) - this node is a cross-community bridge._
- **Why does `enrich_discovered_printers()` connect `enrich_discovered_printers` to `SNMPClient`, `PrinterCollector`?**
  _High betweenness centrality (0.105) - this node is a cross-community bridge._
- **Are the 18 inferred relationships involving `Printer` (e.g. with `_finish_printer_migration()` and `notify_alert()`) actually correct?**
  _`Printer` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `SNMPClient` (e.g. with `.collect_and_save()` and `.__init__()`) actually correct?**
  _`SNMPClient` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `PrinterCollector` (e.g. with `collect_fleet()` and `collect_printer()`) actually correct?**
  _`PrinterCollector` has 9 INFERRED edges - model-reasoned connections that need verification._
- **What connects ``POST /api/auth/login``, ``POST /api/auth/register``, ``GET /api/printers`` to the rest of the system?**
  _241 weakly-connected nodes found - possible documentation gaps or missing edges._