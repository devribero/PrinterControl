# Graph Report - PrinterControl  (2026-08-23)

## Corpus Check
- 142 files · ~97,796 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1326 nodes · 2804 edges · 78 communities (67 shown, 11 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 136 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `27b8b296`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- UsersView.tsx
- package.json
- Main.ps1
- Elgin Impressoras (painel de monitoramento)
- PrinterCollector
- Coletar-Impressoras.ps1
- compilerOptions
- collect.py
- main.py
- enrich_discovered_printers
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
- servers.py
- unhandled_exception_handler
- tests_collect_api.py
- app/page.tsx
- schemas/printer.py
- Sidebar.tsx
- database.py
- Alert
- NetworkView.tsx
- tests_printers_crud.py
- routes/auth.py
- Notification
- api.ts
- SettingsView.tsx
- NotificationsView.tsx
- Printer
- Simular-Ambiente.ps1
- Printer
- cn
- AlertsView.tsx
- User
- PLANO DE IMPLEMENTAÇÃO — ESCANEAR REDE REAL
- services/print_server.py
- Mapa da API
- Guia de Uso do PrinterControl
- create_server
- app-data.tsx
- snmp_fleet_mock.py
- useAppData
- Guia do Desenvolvedor
- printer_sync.py
- tests_rbac.py
- filterPrinters.ts
- SNMPResult
- auth.ts
- notifications.py
- DiscoveryResults.tsx
- Fluxo de Dados
- Arquitetura de Deploy
- Login.tsx
- types.ts
- FEATURE_MATRIX.md
- toast.tsx
- PrintServer
- PrintServerDiscoveryTests
- PrintServerCreate
- layout.tsx
- SNMPClient
- RecordingThreadPoolExecutor
- printers.ts
- FakeAgent
- Settings
- Modo Simulado
- MockSNMPClient

## God Nodes (most connected - your core abstractions)
1. `User` - 64 edges
2. `Printer` - 49 edges
3. `cn()` - 39 edges
4. `SNMPClient` - 37 edges
5. `SNMPResult` - 34 edges
6. `useAppData()` - 33 edges
7. `useToast()` - 27 edges
8. `PrinterCollector` - 26 edges
9. `Printer` - 26 edges
10. `create_db_and_tables()` - 25 edges

## Surprising Connections (you probably didn't know these)
- `active()` --uses--> `Alert`  [INFERRED]
  backend/tests_alerts.py → backend/app/models/alert.py
- `resolved()` --uses--> `Alert`  [INFERRED]
  backend/tests_alerts.py → backend/app/models/alert.py
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

## Communities (78 total, 11 thin omitted)

### Community 0 - "UsersView.tsx"
Cohesion: 0.11
Nodes (20): ComingSoon(), ComingSoonProps, RequireRole(), FORM_VAZIO, formatarData(), FormState, UsersView(), abrirEdicao() (+12 more)

### Community 1 - "package.json"
Cohesion: 0.06
Nodes (31): lucide-react, next, oxlint, dependencies, lucide-react, next, react, react-dom (+23 more)

### Community 2 - "Main.ps1"
Cohesion: 0.13
Nodes (29): Atualizar-ImpressorasAsync(), Build-ListaExibicaoAgrupada(), Build-SnmpGet(), Build-SnmpGetBulk(), Convert-SnmpValueBytes(), Get-ImpressorasEmpresa(), Get-TonerSNMP(), Import-Tabela() (+21 more)

### Community 3 - "Elgin Impressoras (painel de monitoramento)"
Cohesion: 0.10
Nodes (21): Tela Alertas, Tela Dashboard, Elgin Impressoras (painel de monitoramento), Tela Histórico, Tela Impressoras, Tela Login, Migração futura para FastAPI (Python) + Next.js + banco de dados, Modo claro/escuro (toggle) (+13 more)

### Community 4 - "PrinterCollector"
Cohesion: 0.08
Nodes (29): PrinterCollector, Printer, Session, Orquestrador da coleta de impressoras. Separa as tres responsabilidades da…, Converte SNMPResult em PrinterReading. Toner ausente vira NULL (a coluna e…, Coleta uma impressora e grava o resultado como PrinterReading., Deduz se a impressora e colorida a partir do modelo/nome (regra do PS1)., Etiquetadora/portatil: sem Printer-MIB, o PS1 nem consulta SNMP. (+21 more)

### Community 5 - "Coletar-Impressoras.ps1"
Cohesion: 0.21
Nodes (13): Build-SnmpGet(), Build-SnmpGetBulk(), Convert-SnmpValueBytes(), Get-ImpressorasServidor(), Get-TonerSNMP(), Parse-SnmpBulkResponse(), Parse-SnmpCounter(), Parse-SnmpInt() (+5 more)

### Community 6 - "compilerOptions"
Cohesion: 0.06
Nodes (30): dom, dom.iterable, esnext, .next/dev/types/**/*.ts, next-env.d.ts, .next/types/**/*.ts, node_modules, **/*.ts (+22 more)

### Community 7 - "collect.py"
Cohesion: 0.16
Nodes (18): collect_fleet(), collect_printer(), CollectRequest, CollectResponse, FleetCollectResponse, get_scheduler_status(), list_scenarios(), BaseModel (+10 more)

### Community 8 - "main.py"
Cohesion: 0.11
Nodes (15): AsyncIOScheduler, health_check(), lifespan(), get, read_root(), Coleta agendada (Etapa 7; frota inteira desde a Etapa 5). APScheduler roda…, Um ciclo de coleta: toda a frota ativa, agrupada por IP…, Liga o scheduler conforme o .env. Retorna None quando desabilitado. (+7 more)

### Community 9 - "enrich_discovered_printers"
Cohesion: 0.23
Nodes (9): enrich_discovered_printers(), Enriquece filas em memória; não recebe nem acessa uma sessão SQL., Nivel de um consumivel de toner., TonerInfo, DiscoverySnmpTests, printer(), DiscoveredPrinter, Testes locais do enriquecimento SNMP, sem rede corporativa ou SQLite. (+1 more)

### Community 10 - "plugins"
Cohesion: 0.22
Nodes (8): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, typescript, warn

### Community 11 - "HistoryMatrix.tsx"
Cohesion: 0.27
Nodes (5): HistoryPage(), HistoryMatrix(), HistoryMatrixProps, getDepartmentLabel(), getPrinterSite()

### Community 12 - "graphify (knowledge graph tool)"
Cohesion: 0.25
Nodes (8): graphify (knowledge graph tool), graphify explain command, graphify path command, graphify query command, graphify update command, graphify-out/graph.json, graphify-out/GRAPH_REPORT.md, graphify-out/wiki/index.md

### Community 20 - "servers.py"
Cohesion: 0.17
Nodes (17): discover(), DiscoveredPrinterResponse, DiscoverResponse, _executar_discover(), get_current_server(), list_servers(), BaseModel, get (+9 more)

### Community 21 - "unhandled_exception_handler"
Cohesion: 0.40
Nodes (5): Exception, Erro nao tratado: o detalhe vai para o log do servidor, o cliente recebe apenas…, unhandled_exception_handler(), exception_handler, Request

### Community 22 - "tests_collect_api.py"
Cohesion: 0.67
Nodes (3): check(), main(), Teste ponta a ponta dos endpoints /api/collect com os cenarios simulados.…

### Community 25 - "app/page.tsx"
Cohesion: 0.19
Nodes (8): BottomCharts(), RightPanel(), StatCard(), StatCardProps, StatCards(), StatCardsProps, TONE, NAV_ROUTES

### Community 28 - "schemas/printer.py"
Cohesion: 0.17
Nodes (15): Config, PrinterCreate, PrinterReadingCreate, PrinterReadingResponse, PrinterResponse, PrinterUpdate, PrinterWithStatus, BaseModel (+7 more)

### Community 29 - "Sidebar.tsx"
Cohesion: 0.18
Nodes (14): AlertsDonutCard(), AlertsDonutCardProps, PagesConsumedCard(), TotalPrintsCard(), NavItem(), NavItemProps, Sidebar(), SidebarProps (+6 more)

### Community 30 - "database.py"
Cohesion: 0.11
Nodes (28): create_db_and_tables(), _finish_printer_migration(), _migrate_alert_type(), _migrate_print_servers(), _migrate_printer_schema(), _migrate_reading_uptime(), _migrate_user_rbac(), Fase 4: registro de Print Servers. A tabela `print_servers` em si e criada pelo… (+20 more)

### Community 31 - "Alert"
Cohesion: 0.09
Nodes (36): Alert, Alert, SQLModel, TonerHistory, PrinterMonthly, PrinterReading, SQLModel, get_alert() (+28 more)

### Community 32 - "NetworkView.tsx"
Cohesion: 0.11
Nodes (23): adaptDiscovered(), FORM_VAZIO, formatarMomento(), MODOS, NetworkView(), confirmarAtivacao(), executarDescoberta(), executarSync() (+15 more)

### Community 33 - "tests_printers_crud.py"
Cohesion: 0.33
Nodes (3): Etapa 12 - CRUD de impressoras contra o servidor rodando. Usa o banco REAL,…, Devolve (status, payload)., request()

### Community 34 - "routes/auth.py"
Cohesion: 0.13
Nodes (24): change_own_password(), login(), get, patch, post, Session, Conta autenticada e seu papel — usado para decidir o que exibir/permitir., Perfil da PROPRIA conta (Fase 8). So o nome. Nao recebe id: o alvo e sempre a… (+16 more)

### Community 35 - "Notification"
Cohesion: 0.09
Nodes (30): Notification, SQLModel, Notificacoes internas (Fase 7). Por que uma tabela separada de `alerts`…, AlertRef, create_notifications(), list_notifications(), mark_all_as_read(), mark_as_read() (+22 more)

### Community 36 - "api.ts"
Cohesion: 0.08
Nodes (22): api, API_BASE_URL, ApiAlert, ApiDiscoveredPrinter, ApiDiscoveredToner, ApiNotification, ApiNotificationAlertRef, ApiPrinterReading (+14 more)

### Community 37 - "SettingsView.tsx"
Cohesion: 0.11
Nodes (22): SettingsView(), trocarSenha(), validarSenha(), TEMAS, useApiErrorReporter(), changeMyPassword(), ESCALAS, ler() (+14 more)

### Community 38 - "NotificationsView.tsx"
Cohesion: 0.13
Nodes (19): FORM_VAZIO, formatarMomento(), FormState, ICONE_SEVERIDADE, NotificationsView(), abrirEnvio(), enviar(), marcarComoLida() (+11 more)

### Community 39 - "Printer"
Cohesion: 0.26
Nodes (16): Printer, Etapa 4: identidade e (server, name), NAO ip — o Print Server permite varias…, create_printer(), create_printer_reading(), get_printer(), get_printer_readings(), list_printers(), list_printers_with_status() (+8 more)

### Community 40 - "Simular-Ambiente.ps1"
Cohesion: 0.16
Nodes (6): Modo Real, Contador mensal calculado por diff de duas leituras SNMP acumulativas (não existe OID de páginas do mês), Scripts PowerShell reais nunca rodaram de verdade (sem interpretador PowerShell no ambiente de dev), public/data/monthly-report.json, public/data/printers.json, Arquivos de dados gerados são ignorados pelo git — gerar/apagar localmente nunca afeta o repositório

### Community 41 - "Printer"
Cohesion: 0.27
Nodes (9): PrinterDetailsModalProps, PrinterRanking(), PrinterRankingProps, RankedPrinter, RankList(), rankPrinters(), RightPanelProps, TonerMonitoringProps (+1 more)

### Community 42 - "cn"
Cohesion: 0.14
Nodes (18): TonerPage(), PrinterDetailsModal(), config, PrinterStatusBadge(), PAGE_SIZE_OPTIONS, PrinterTable(), classify(), FILTERS (+10 more)

### Community 43 - "AlertsView.tsx"
Cohesion: 0.31
Nodes (6): AlertsPage(), AlertBanner(), AlertBannerProps, AlertsView(), AlertsViewProps, Alert

### Community 44 - "User"
Cohesion: 0.09
Nodes (40): SQLModel, str, True se o papel do usuario satisfaz qualquer um dos exigidos., RBAC minimo (Fase 1). Tres papeis cobrem todas as rotas existentes hoje: -…, Role, User, _active_admin_count(), create_user() (+32 more)

### Community 45 - "PLANO DE IMPLEMENTAÇÃO — ESCANEAR REDE REAL"
Cohesion: 0.05
Nodes (39): A. Endpoint (implementado), Alertas, Arquitetura atual, Arquitetura do PrinterControl, B. Service reutilizável, Banco, C. Funções Print Server reutilizáveis, Cliente de API (+31 more)

### Community 46 - "services/print_server.py"
Cohesion: 0.14
Nodes (17): discover_printers(), DiscoveredPrinter, _mock_discover(), PrintServerError, Exception, Camada de Print Server (Etapa 3). Reproduz a descoberta de impressoras do…, Equivalente exato de Get-ImpressorasEmpresa + o inicio de Process-…, Descobre as impressoras publicadas em um Print Server. `server` e `mode` sao… (+9 more)

### Community 47 - "Mapa da API"
Cohesion: 0.04
Nodes (48): Alertas, Autenticação, Coleta, Diagnóstico, Escanear Rede (implementado), `GET /`, `GET /api/alerts`, `GET /api/alerts/{alert_id}` (+40 more)

### Community 48 - "Guia de Uso do PrinterControl"
Cohesion: 0.10
Nodes (20): Acessar via web — PARCIAL, Adicionar impressora — AUSENTE/PARCIAL, Alertas — FUNCIONAL na leitura; PARCIAL nas ações, Ações, Como acessar, Configurações — COMING SOON, Configurações, Usuários e Integrações — COMING SOON, Dashboard — FUNCIONAL/PARCIAL (+12 more)

### Community 49 - "create_server"
Cohesion: 0.19
Nodes (18): create_server(), discover_server(), _get_or_404(), _marcar_resultado(), PrintServerResponse, patch, post, Session (+10 more)

### Community 50 - "app-data.tsx"
Cohesion: 0.13
Nodes (25): decommissionedPrinters, monthlyUsage, adaptAlert(), loadMonthlyReportFromApi(), discoverPrinters(), fetchAlerts(), fetchPrintersWithStatus(), fetchUnreadNotificationCount() (+17 more)

### Community 51 - "snmp_fleet_mock.py"
Cohesion: 0.23
Nodes (10): _base_page_count(), _increment(), profile_for(), Simulador de frota — APENAS PARA TESTE LOCAL. Diferenca para snmp_mock.py: la…, Perfil deterministico da impressora: online | offline | snmp_mudo | baixo |…, Contador inicial plausivel para uma impressora que nunca foi lida., Paginas impressas entre duas coletas — fixo por impressora, 5 a 124., Nivel do toner: base do perfil + desvio deterministico por impressora/cor,… (+2 more)

### Community 52 - "useAppData"
Cohesion: 0.17
Nodes (12): react, DashboardPage(), PrintersPage(), AppShell(), AuthGate(), Login(), Modal(), ModalProps (+4 more)

### Community 53 - "Guia do Desenvolvedor"
Cohesion: 0.13
Nodes (14): Backend, Banco, Comandos do frontend, Escanear Rede (implementado), Guia do Desenvolvedor, O que não executar em produção sem autorização, Print Server, Riscos conhecidos (+6 more)

### Community 54 - "printer_sync.py"
Cohesion: 0.20
Nodes (11): obter_modelo(), obter_tipo_impressora(), Regras de classificacao portadas do Main.ps1 (Etapa 4). Correspondencia exata:…, Traduz DriverName (Windows) em nome comercial, igual ao Main.ps1., Classifica A4 / Etiqueta / Portatil a partir de Nome+Modelo, igual ao Main.ps1., Session, Sincronizacao Print Server -> banco (Etapa 4). Print Server ->…, Executa um ciclo completo de sincronizacao para UM Print Server. Ja era… (+3 more)

### Community 55 - "tests_rbac.py"
Cohesion: 0.29
Nodes (10): check(), check_true(), h(), main(), Fase 1 - Autenticacao, RBAC e protecao das rotas. Diferente dos demais…, Cria um banco no formato ANTERIOR a Fase 1 (users sem role/is_active), roda a…, Cria as contas de teste e uma impressora + alerta para as rotas de escrita., semear() (+2 more)

### Community 56 - "filterPrinters.ts"
Cohesion: 0.36
Nodes (7): PrinterTableProps, DEFAULT_FILTERS, filterPrinters(), PrinterFilters, getPrinterType(), PrinterType, PrinterStatus

### Community 57 - "SNMPResult"
Cohesion: 0.10
Nodes (24): _empty_result(), EnrichedDiscoveredPrinter, _is_color(), _is_label(), _normalize_ip(), DiscoveredPrinter, Enriquecimento transitório de filas descobertas com telemetria SNMP., _result_for_ip() (+16 more)

### Community 58 - "auth.ts"
Cohesion: 0.23
Nodes (16): handleSubmit(), salvarPerfil(), clearToken(), isTokenPersistent(), setToken(), ApiUser, cacheAccount(), fetchCurrentUser() (+8 more)

### Community 59 - "notifications.py"
Cohesion: 0.21
Nodes (10): get_session(), Session, Dependencias compartilhadas pelas rotas. Autorizacao (Fase 1) fica CENTRALIZADA…, Usuario dono do JWT do header Authorization. 401 se ausente/invalido. O usuario…, Fabrica de dependencia: exige que o usuario tenha (ou herde) um dos papeis…, require_roles(), require_user(), Central de notificacoes internas (Fase 7). Caixa PESSOAL: `GET` e `PATCH`… (+2 more)

### Community 60 - "DiscoveryResults.tsx"
Cohesion: 0.60
Nodes (4): DiscoveryResults(), DiscoveryResultsProps, statusLabel(), DiscoveredPrinter

### Community 62 - "Fluxo de Dados"
Cohesion: 0.17
Nodes (11): 10. Escanear Rede (implementado), 1. Cadastro no SQLite, 2. Coleta SNMP real, 3. Coleta de frota, 4. Print Server, 5. Sincronização, 6. Alertas, 7. Relatório mensal (+3 more)

### Community 63 - "Arquitetura de Deploy"
Cohesion: 0.18
Nodes (10): Arquitetura avaliada, Arquitetura de Deploy, Autenticação, Bloqueios atuais, Cloudflare Tunnel, Configuração de aplicação, CORS, Estado atual (+2 more)

### Community 64 - "Login.tsx"
Cohesion: 0.15
Nodes (11): Logo Elgin é redesenho à mão (IA sem acesso a imagens coladas no chat, só uploads), src/components/ (padrão com header-comment por arquivo), ElginLogo(), ElginLogoProps, ACTIVE_NODES, features, LoginProps, NETWORK_LINKS (+3 more)

### Community 65 - "types.ts"
Cohesion: 0.14
Nodes (18): BottomChartsProps, MonthlyCounters(), MonthlyCountersProps, adaptPrinter(), ApiMonthlyReport, formatLastSeen(), toStatus(), toToner() (+10 more)

### Community 68 - "toast.tsx"
Cohesion: 0.22
Nodes (7): ToastContext, ToastContextValue, ToastItem, ToastProvider(), ToastVariant, VARIANT_COLOR, VARIANT_ICON

### Community 69 - "PrintServer"
Cohesion: 0.29
Nodes (6): PrintServer, SQLModel, str, Print Server como entidade (Fase 4). Ate aqui um Print Server existia de duas…, Modos aceitos, iguais aos de `settings.print_server_mode`., ServerMode

### Community 71 - "PrintServerCreate"
Cohesion: 0.33
Nodes (4): PrintServerCreate, PrintServerUpdate, field_validator, `host` fica de fora de proposito: ele e a chave natural que aparece em…

### Community 72 - "layout.tsx"
Cohesion: 0.29
Nodes (5): ibmPlexMono, metadata, publicSans, sourceSerif, Providers()

### Community 73 - "SNMPClient"
Cohesion: 0.08
Nodes (23): parse_varbinds(), Decodifica bytes BER como inteiro sem sinal., Extrai a lista de varbinds de uma resposta SNMP. Percorre a estrutura completa…, Cliente SNMP para coleta de impressoras (Printer-MIB, RFC 3805)., Coleta status, contador de paginas e toners de uma impressora. Nunca levanta…, PS1: `if ($ip -match '^\\d')` — descarta 'N/A' e nomes de porta., ICMP ping, equivalente ao `New-Object ...Ping).Send($ip, 400)` do PS1. SNMP…, Retorna (candidatos, houve_resposta_snmp). (+15 more)

### Community 76 - "printers.ts"
Cohesion: 0.13
Nodes (17): Levantamento_impressões (planilha original), ReportsPage(), DecommissionedList(), DecommissionedListProps, DepartmentBreakdown(), DepartmentBreakdownProps, MONTHS, onExportCsv() (+9 more)

### Community 81 - "FakeAgent"
Cohesion: 0.12
Nodes (12): Decodifica um OID BER para notacao pontuada., Le um TLV BER. Retorna (tag, length, value_start, next_pos)., _read_oid(), _read_tlv(), check(), FakeAgent, LocalSNMPClient, main() (+4 more)

### Community 83 - "Settings"
Cohesion: 0.14
Nodes (10): Config, field_validator, Normaliza um DATABASE_URL sqlite relativo (ex.: sqlite:///./x.db) para um…, Impede que um ambiente de producao suba silenciosamente com o secret de…, Settings, _confere_rbac_do_frontend(), O frontend tem a sua propria copia da hierarquia de papeis, em…, BaseSettings (+2 more)

### Community 86 - "MockSNMPClient"
Cohesion: 0.20
Nodes (5): Cenarios de teste disponiveis (fonte unica: snmp_mock.SCENARIOS)., Args: mode: "real" (SNMP de verdade), "mock" (cenario fixo) ou "fleet" (frota…, MockSNMPClient, Substituto do SNMPClient com a mesma assinatura de collect()., Devolve o resultado fixo do cenario (ip e is_color sao ignorados).

## Knowledge Gaps
- **279 isolated node(s):** `$schema`, `typescript`, `oxc`, `react/rules-of-hooks`, `warn` (+274 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SNMPClient` connect `SNMPClient` to `PrinterCollector`, `main.py`, `enrich_discovered_printers`, `FakeAgent`, `MockSNMPClient`, `SNMPResult`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Why does `User` connect `User` to `routes/auth.py`, `Notification`, `collect.py`, `Printer`, `main.py`, `create_server`, `servers.py`, `tests_rbac.py`, `notifications.py`, `database.py`, `Alert`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Why does `Printer` connect `Printer` to `PrinterCollector`, `collect.py`, `main.py`, `User`, `create_server`, `servers.py`, `printer_sync.py`, `tests_rbac.py`, `database.py`, `Alert`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Are the 37 inferred relationships involving `User` (e.g. with `require_roles()` and `require_user()`) actually correct?**
  _`User` has 37 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `Printer` (e.g. with `_finish_printer_migration()` and `notify_alert()`) actually correct?**
  _`Printer` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `SNMPClient` (e.g. with `PrinterCollector` and `FakeAgent`) actually correct?**
  _`SNMPClient` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `SNMPResult` (e.g. with `enrich_discovered_printers()` and `PrinterCollector`) actually correct?**
  _`SNMPResult` has 6 INFERRED edges - model-reasoned connections that need verification._