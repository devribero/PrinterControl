# Graph Report - PrinterControl  (2026-08-23)

## Corpus Check
- 135 files · ~87,714 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1213 nodes · 2502 edges · 71 communities (61 shown, 10 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 121 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `99cfda87`
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
- tests_printer_fleet.py
- RequireRole.tsx
- plugins
- Printer
- graphify (knowledge graph tool)
- next.config.ts
- Elgin (Brand)
- PrinterControl Favicon Icon
- npm run build
- npm run dev
- next-env.d.ts
- navIds.ts
- SNMPResult
- unhandled_exception_handler
- tests_collect_api.py
- Printer
- printers.py
- Sidebar.tsx
- types.ts
- alert_engine.py
- NetworkView.tsx
- cn
- Role
- enrich_discovered_printers
- api.ts
- notify_alert
- create_server
- reports/page.tsx
- Simular-Ambiente.ps1
- SNMPClient
- TonerMonitoring.tsx
- printer_sync.py
- PLANO DE IMPLEMENTAÇÃO — ESCANEAR REDE REAL
- services/print_server.py
- Impressoras
- Guia de Uso do PrinterControl
- printer_collector.py
- app-data.tsx
- snmp_fleet_mock.py
- useAppData
- Guia do Desenvolvedor
- tests_printers_crud.py
- Settings
- PrinterTable.tsx
- printers.ts
- auth.ts
- discovery.py
- tests_rbac.py
- Fluxo de Dados
- Arquitetura de Deploy
- ElginLogo.tsx
- Relatorio-Mensal.ps1
- FEATURE_MATRIX.md
- PrintServer
- PrintServerDiscoveryTests
- database.py
- User
- PrintServerCreate
- servers.py

## God Nodes (most connected - your core abstractions)
1. `User` - 50 edges
2. `Printer` - 45 edges
3. `SNMPClient` - 37 edges
4. `cn()` - 35 edges
5. `SNMPResult` - 34 edges
6. `useAppData()` - 29 edges
7. `Printer` - 26 edges
8. `PrinterCollector` - 26 edges
9. `enrich_discovered_printers()` - 24 edges
10. `useToast()` - 23 edges

## Surprising Connections (you probably didn't know these)
- `Lucide` --conceptually_related_to--> `Elgin Impressoras (painel de monitoramento)`  [EXTRACTED]
  README.md → CONTEXTO-DESENVOLVIMENTO.md
- `React` --conceptually_related_to--> `Elgin Impressoras (painel de monitoramento)`  [EXTRACTED]
  README.md → CONTEXTO-DESENVOLVIMENTO.md
- `Recharts` --conceptually_related_to--> `Elgin Impressoras (painel de monitoramento)`  [EXTRACTED]
  README.md → CONTEXTO-DESENVOLVIMENTO.md
- `Tailwind CSS v4` --conceptually_related_to--> `Elgin Impressoras (painel de monitoramento)`  [EXTRACTED]
  README.md → CONTEXTO-DESENVOLVIMENTO.md
- `TypeScript` --conceptually_related_to--> `Elgin Impressoras (painel de monitoramento)`  [EXTRACTED]
  README.md → CONTEXTO-DESENVOLVIMENTO.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Comandos do CLI graphify (query/path/explain/update)** — claude_graphify, claude_graphify_query, claude_graphify_path, claude_graphify_explain, claude_graphify_update [EXTRACTED 1.00]
- **Stack tecnológico do painel (Vite/React/TS/Tailwind/Recharts/Lucide)** — readme_vite, readme_react, readme_typescript, readme_tailwind_css_v4, readme_recharts, readme_lucide [EXTRACTED 1.00]
- **Arquitetura de dados de 3 modos (Demo/Real/Simulado)** — contexto_desenvolvimento_elgin_impressoras, contexto_desenvolvimento_modo_demo, contexto_desenvolvimento_modo_real, contexto_desenvolvimento_modo_simulado [EXTRACTED 1.00]

## Communities (71 total, 10 thin omitted)

### Community 0 - "UsersView.tsx"
Cohesion: 0.12
Nodes (21): FORM_VAZIO, formatarData(), FormState, UsersView(), abrirEdicao(), confirmarAtivacao(), salvar(), validar() (+13 more)

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
Cohesion: 0.13
Nodes (21): PrinterCollector, Printer, Session, Converte SNMPResult em PrinterReading. Toner ausente vira NULL (a coluna e…, Coleta uma impressora e grava o resultado como PrinterReading., Deduz se a impressora e colorida a partir do modelo/nome (regra do PS1)., Etiquetadora/portatil: sem Printer-MIB, o PS1 nem consulta SNMP., Coleta uma impressora e persiste a leitura. Args: printer_id: id da impressora… (+13 more)

### Community 5 - "Coletar-Impressoras.ps1"
Cohesion: 0.21
Nodes (13): Build-SnmpGet(), Build-SnmpGetBulk(), Convert-SnmpValueBytes(), Get-ImpressorasServidor(), Get-TonerSNMP(), Parse-SnmpBulkResponse(), Parse-SnmpCounter(), Parse-SnmpInt() (+5 more)

### Community 6 - "compilerOptions"
Cohesion: 0.06
Nodes (30): dom, dom.iterable, esnext, .next/dev/types/**/*.ts, next-env.d.ts, .next/types/**/*.ts, node_modules, **/*.ts (+22 more)

### Community 7 - "collect.py"
Cohesion: 0.16
Nodes (18): collect_fleet(), collect_printer(), CollectRequest, CollectResponse, FleetCollectResponse, get_scheduler_status(), list_scenarios(), BaseModel (+10 more)

### Community 8 - "tests_printer_fleet.py"
Cohesion: 0.18
Nodes (4): fake_real_collect(), Etapa 5 - orquestracao da frota (printer_fleet.collect_fleet). Roda sobre um…, RecordingThreadPoolExecutor, _OriginalTPE

### Community 9 - "RequireRole.tsx"
Cohesion: 0.33
Nodes (3): ComingSoon(), ComingSoonProps, RequireRole()

### Community 10 - "plugins"
Cohesion: 0.22
Nodes (8): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, typescript, warn

### Community 11 - "Printer"
Cohesion: 0.20
Nodes (10): HistoryMatrix(), HistoryMatrixProps, PrinterDetailsModalProps, PrinterRanking(), PrinterRankingProps, RankedPrinter, rankPrinters(), getDepartmentLabel() (+2 more)

### Community 12 - "graphify (knowledge graph tool)"
Cohesion: 0.25
Nodes (8): graphify (knowledge graph tool), graphify explain command, graphify path command, graphify query command, graphify update command, graphify-out/graph.json, graphify-out/GRAPH_REPORT.md, graphify-out/wiki/index.md

### Community 20 - "SNMPResult"
Cohesion: 0.14
Nodes (14): MockSNMPScenarios, SNMP responde o contador, mas nao expoe a tabela de consumiveis., Monocromatica com toner em 5%., Colorida com ciano critico (18%) e os demais normais., Contador reiniciado (troca de placa/formatador): page_count baixo., Cenarios de teste. Cada metodo devolve um SNMPResult completo., Monocromatica saudavel., Colorida saudavel (4 toners, ordem C, M, Y, K). (+6 more)

### Community 21 - "unhandled_exception_handler"
Cohesion: 0.40
Nodes (5): Exception, Erro nao tratado: o detalhe vai para o log do servidor, o cliente recebe apenas…, unhandled_exception_handler(), exception_handler, Request

### Community 22 - "tests_collect_api.py"
Cohesion: 0.67
Nodes (3): check(), main(), Teste ponta a ponta dos endpoints /api/collect com os cenarios simulados.…

### Community 25 - "Printer"
Cohesion: 0.13
Nodes (19): Alert, SQLModel, TonerHistory, Printer, PrinterMonthly, PrinterReading, SQLModel, Etapa 4: identidade e (server, name), NAO ip — o Print Server permite varias… (+11 more)

### Community 28 - "printers.py"
Cohesion: 0.12
Nodes (29): create_printer(), create_printer_reading(), get_printer(), get_printer_readings(), list_printers(), list_printers_with_status(), monthly_report(), get (+21 more)

### Community 29 - "Sidebar.tsx"
Cohesion: 0.13
Nodes (19): AlertsDonutCard(), AlertsDonutCardProps, PagesConsumedCard(), NavItem(), NavItemProps, Sidebar(), SidebarProps, sparkData (+11 more)

### Community 30 - "types.ts"
Cohesion: 0.17
Nodes (13): AlertBanner(), AlertBannerProps, AlertsViewProps, BottomChartsProps, DiscoveryResults(), DiscoveryResultsProps, statusLabel(), MonthlyCountersProps (+5 more)

### Community 31 - "alert_engine.py"
Cohesion: 0.18
Nodes (15): Alert, _active(), evaluate_reading(), Session, Alertas automaticos (Etapa 8A). Roda logo apos cada PrinterReading ser…, Cria, mantem ou resolve o alerta de uma condicao. Retorna a acao tomada., Avalia uma leitura e sincroniza os alertas da impressora. Faz commit ao final.…, _sync_condition() (+7 more)

### Community 32 - "NetworkView.tsx"
Cohesion: 0.10
Nodes (24): ModalProps, adaptDiscovered(), FORM_VAZIO, formatarMomento(), MODOS, NetworkView(), confirmarAtivacao(), executarDescoberta() (+16 more)

### Community 33 - "cn"
Cohesion: 0.12
Nodes (16): DashboardPage(), AlertsView(), BottomCharts(), TotalPrintsCard(), MonthlyCounters(), RankList(), PrinterTable(), RightPanel() (+8 more)

### Community 34 - "Role"
Cohesion: 0.09
Nodes (39): get_session(), Session, Dependencias compartilhadas pelas rotas. Autorizacao (Fase 1) fica CENTRALIZADA…, Usuario dono do JWT do header Authorization. 401 se ausente/invalido. O usuario…, require_user(), str, RBAC minimo (Fase 1). Tres papeis cobrem todas as rotas existentes hoje: -…, Role (+31 more)

### Community 35 - "enrich_discovered_printers"
Cohesion: 0.24
Nodes (9): enrich_discovered_printers(), Enriquece filas em memória; não recebe nem acessa uma sessão SQL., Nivel de um consumivel de toner., TonerInfo, DiscoverySnmpTests, printer(), DiscoveredPrinter, Testes locais do enriquecimento SNMP, sem rede corporativa ou SQLite. (+1 more)

### Community 36 - "api.ts"
Cohesion: 0.08
Nodes (28): adaptPrinter(), ApiMonthlyReport, formatLastSeen(), toStatus(), toToner(), VALID_COLORS, VALID_STATUS, API_BASE_URL (+20 more)

### Community 37 - "notify_alert"
Cohesion: 0.20
Nodes (11): get_alert(), list_alerts(), notify_alert(), get, patch, post, Session, Resolve um alerta. Ate a Fase 1 esta rota estava SEM protecao alguma — qualquer… (+3 more)

### Community 38 - "create_server"
Cohesion: 0.19
Nodes (17): create_server(), discover(), discover_server(), _get_or_404(), _marcar_resultado(), post, Session, Registra o desfecho da ultima descoberta/sync no proprio servidor. (+9 more)

### Community 39 - "reports/page.tsx"
Cohesion: 0.15
Nodes (12): ReportsPage(), DepartmentBreakdown(), DepartmentBreakdownProps, MONTHS, Topbar(), onExportCsv(), DepartmentUsage, handleAlertSelect() (+4 more)

### Community 40 - "Simular-Ambiente.ps1"
Cohesion: 0.22
Nodes (5): Modo Simulado, public/data/monthly-report.json, public/data/printers.json, Arquivos de dados gerados são ignorados pelo git — gerar/apagar localmente nunca afeta o repositório, Impressoras simuladas usam prefixo SIM_ / departamentos TESTE - de propósito, pra nunca confundir com dado real

### Community 41 - "SNMPClient"
Cohesion: 0.05
Nodes (35): parse_varbinds(), Decodifica um OID BER para notacao pontuada., Decodifica bytes BER como inteiro sem sinal., Extrai a lista de varbinds de uma resposta SNMP. Percorre a estrutura completa…, Cliente SNMP para coleta de impressoras (Printer-MIB, RFC 3805)., Coleta status, contador de paginas e toners de uma impressora. Nunca levanta…, PS1: `if ($ip -match '^\\d')` — descarta 'N/A' e nomes de porta., ICMP ping, equivalente ao `New-Object ...Ping).Send($ip, 400)` do PS1. SNMP… (+27 more)

### Community 42 - "TonerMonitoring.tsx"
Cohesion: 0.16
Nodes (14): PrinterDetailsModal(), config, PrinterStatusBadge(), classify(), FILTERS, SummaryCardProps, TONE, TonerClass (+6 more)

### Community 44 - "printer_sync.py"
Cohesion: 0.20
Nodes (11): obter_modelo(), obter_tipo_impressora(), Regras de classificacao portadas do Main.ps1 (Etapa 4). Correspondencia exata:…, Traduz DriverName (Windows) em nome comercial, igual ao Main.ps1., Classifica A4 / Etiqueta / Portatil a partir de Nome+Modelo, igual ao Main.ps1., Session, Sincronizacao Print Server -> banco (Etapa 4). Print Server ->…, Executa um ciclo completo de sincronizacao para UM Print Server. Ja era… (+3 more)

### Community 45 - "PLANO DE IMPLEMENTAÇÃO — ESCANEAR REDE REAL"
Cohesion: 0.05
Nodes (39): A. Endpoint (implementado), Alertas, Arquitetura atual, Arquitetura do PrinterControl, B. Service reutilizável, Banco, C. Funções Print Server reutilizáveis, Cliente de API (+31 more)

### Community 46 - "services/print_server.py"
Cohesion: 0.12
Nodes (17): discover_printers(), DiscoveredPrinter, _mock_discover(), PrintServerError, Exception, Camada de Print Server (Etapa 3). Reproduz a descoberta de impressoras do…, Equivalente exato de Get-ImpressorasEmpresa + o inicio de Process-…, Descobre as impressoras publicadas em um Print Server. `server` e `mode` sao… (+9 more)

### Community 47 - "Impressoras"
Cohesion: 0.05
Nodes (40): Alertas, Autenticação, Coleta, Diagnóstico, Escanear Rede (implementado), `GET /`, `GET /api/alerts`, `GET /api/alerts/{alert_id}` (+32 more)

### Community 48 - "Guia de Uso do PrinterControl"
Cohesion: 0.10
Nodes (20): Acessar via web — PARCIAL, Adicionar impressora — AUSENTE/PARCIAL, Alertas — FUNCIONAL na leitura; PARCIAL nas ações, Ações, Como acessar, Configurações — COMING SOON, Configurações, Usuários e Integrações — COMING SOON, Dashboard — FUNCIONAL/PARCIAL (+12 more)

### Community 49 - "printer_collector.py"
Cohesion: 0.14
Nodes (8): Orquestrador da coleta de impressoras. Separa as tres responsabilidades da…, Cenarios de teste disponiveis (fonte unica: snmp_mock.SCENARIOS)., Args: mode: "real" (SNMP de verdade), "mock" (cenario fixo) ou "fleet" (frota…, MockSNMPClient, Agente SNMP simulado — APENAS PARA TESTE LOCAL. Existe porque a maquina de…, Substituto do SNMPClient com a mesma assinatura de collect()., Devolve o resultado fixo do cenario (ip e is_color sao ignorados)., SNMP Collector para impressoras. Porte direto da funcao Get-TonerSNMP de…

### Community 50 - "app-data.tsx"
Cohesion: 0.17
Nodes (19): adaptAlert(), loadMonthlyReportFromApi(), discoverPrinters(), fetchAlerts(), fetchPrintersWithStatus(), AppDataContext, AppDataProvider(), expireSession() (+11 more)

### Community 51 - "snmp_fleet_mock.py"
Cohesion: 0.23
Nodes (10): _base_page_count(), _increment(), profile_for(), Simulador de frota — APENAS PARA TESTE LOCAL. Diferenca para snmp_mock.py: la…, Perfil deterministico da impressora: online | offline | snmp_mudo | baixo |…, Contador inicial plausivel para uma impressora que nunca foi lida., Paginas impressas entre duas coletas — fixo por impressora, 5 a 124., Nivel do toner: base do perfil + desvio deterministico por impressora/cor,… (+2 more)

### Community 52 - "useAppData"
Cohesion: 0.09
Nodes (21): react, AlertsPage(), HistoryPage(), ibmPlexMono, metadata, publicSans, sourceSerif, PrintersPage() (+13 more)

### Community 53 - "Guia do Desenvolvedor"
Cohesion: 0.13
Nodes (14): Backend, Banco, Comandos do frontend, Escanear Rede (implementado), Guia do Desenvolvedor, O que não executar em produção sem autorização, Print Server, Riscos conhecidos (+6 more)

### Community 54 - "tests_printers_crud.py"
Cohesion: 0.33
Nodes (3): Etapa 12 - CRUD de impressoras contra o servidor rodando. Usa o banco REAL,…, Devolve (status, payload)., request()

### Community 55 - "Settings"
Cohesion: 0.18
Nodes (7): Config, field_validator, Normaliza um DATABASE_URL sqlite relativo (ex.: sqlite:///./x.db) para um…, Impede que um ambiente de producao suba silenciosamente com o secret de…, Settings, BaseSettings, model_validator

### Community 56 - "PrinterTable.tsx"
Cohesion: 0.36
Nodes (8): PAGE_SIZE_OPTIONS, PrinterTableProps, DEFAULT_FILTERS, filterPrinters(), PrinterFilters, getPrinterType(), PrinterType, PrinterStatus

### Community 57 - "printers.ts"
Cohesion: 0.16
Nodes (13): Levantamento_impressões (planilha original), DecommissionedList(), DecommissionedListProps, RightPanelProps, DecommissionedPrinter, decommissionedPrinters, globalToner, monthlyUsage (+5 more)

### Community 58 - "auth.ts"
Cohesion: 0.12
Nodes (22): ACTIVE_NODES, features, Login(), handleSubmit(), LoginProps, NETWORK_LINKS, NETWORK_NODES, api (+14 more)

### Community 59 - "discovery.py"
Cohesion: 0.39
Nodes (8): _empty_result(), EnrichedDiscoveredPrinter, _is_color(), _is_label(), _normalize_ip(), DiscoveredPrinter, Enriquecimento transitório de filas descobertas com telemetria SNMP., _result_for_ip()

### Community 61 - "tests_rbac.py"
Cohesion: 0.24
Nodes (12): check(), check_true(), _confere_rbac_do_frontend(), h(), main(), Fase 1 - Autenticacao, RBAC e protecao das rotas. Diferente dos demais…, O frontend tem a sua propria copia da hierarquia de papeis, em…, Cria um banco no formato ANTERIOR a Fase 1 (users sem role/is_active), roda a… (+4 more)

### Community 62 - "Fluxo de Dados"
Cohesion: 0.17
Nodes (11): 10. Escanear Rede (implementado), 1. Cadastro no SQLite, 2. Coleta SNMP real, 3. Coleta de frota, 4. Print Server, 5. Sincronização, 6. Alertas, 7. Relatório mensal (+3 more)

### Community 63 - "Arquitetura de Deploy"
Cohesion: 0.18
Nodes (10): Arquitetura avaliada, Arquitetura de Deploy, Autenticação, Bloqueios atuais, Cloudflare Tunnel, Configuração de aplicação, CORS, Estado atual (+2 more)

### Community 64 - "ElginLogo.tsx"
Cohesion: 0.40
Nodes (4): Logo Elgin é redesenho à mão (IA sem acesso a imagens coladas no chat, só uploads), src/components/ (padrão com header-comment por arquivo), ElginLogo(), ElginLogoProps

### Community 66 - "Relatorio-Mensal.ps1"
Cohesion: 0.33
Nodes (3): Modo Real, Contador mensal calculado por diff de duas leituras SNMP acumulativas (não existe OID de páginas do mês), Scripts PowerShell reais nunca rodaram de verdade (sem interpretador PowerShell no ambiente de dev)

### Community 69 - "PrintServer"
Cohesion: 0.29
Nodes (6): PrintServer, SQLModel, str, Print Server como entidade (Fase 4). Ate aqui um Print Server existia de duas…, Modos aceitos, iguais aos de `settings.print_server_mode`., ServerMode

### Community 71 - "database.py"
Cohesion: 0.08
Nodes (35): AsyncIOScheduler, create_db_and_tables(), _finish_printer_migration(), _migrate_alert_type(), _migrate_print_servers(), _migrate_printer_schema(), _migrate_reading_uptime(), _migrate_user_rbac() (+27 more)

### Community 72 - "User"
Cohesion: 0.14
Nodes (21): Fabrica de dependencia: exige que o usuario tenha (ou herde) um dos papeis…, require_roles(), SQLModel, True se o papel do usuario satisfaz qualquer um dos exigidos., User, get, Conta autenticada e seu papel — usado para decidir o que exibir/permitir., read_current_user() (+13 more)

### Community 81 - "servers.py"
Cohesion: 0.15
Nodes (20): DiscoveredPrinterResponse, DiscoverResponse, _executar_discover(), get_current_server(), list_servers(), PrintServerResponse, PrintServerUpdate, BaseModel (+12 more)

## Knowledge Gaps
- **260 isolated node(s):** `ServerFormState`, `FORM_VAZIO`, `MODOS`, `STATUS_SERVIDOR`, `API_BASE_URL` (+255 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `Role`, `notify_alert`, `create_server`, `collect.py`, `database.py`, `servers.py`, `Printer`, `printers.py`, `tests_rbac.py`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Why does `Printer` connect `Printer` to `Role`, `PrinterCollector`, `notify_alert`, `create_server`, `collect.py`, `database.py`, `User`, `tests_printer_fleet.py`, `printer_sync.py`, `servers.py`, `printer_collector.py`, `printers.py`, `tests_rbac.py`, `alert_engine.py`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Why does `SNMPClient` connect `SNMPClient` to `enrich_discovered_printers`, `PrinterCollector`, `tests_printer_fleet.py`, `printer_collector.py`, `discovery.py`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `User` (e.g. with `require_roles()` and `require_user()`) actually correct?**
  _`User` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `Printer` (e.g. with `_finish_printer_migration()` and `notify_alert()`) actually correct?**
  _`Printer` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `SNMPClient` (e.g. with `PrinterCollector` and `FakeAgent`) actually correct?**
  _`SNMPClient` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `SNMPResult` (e.g. with `enrich_discovered_printers()` and `PrinterCollector`) actually correct?**
  _`SNMPResult` has 6 INFERRED edges - model-reasoned connections that need verification._