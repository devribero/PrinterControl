# Graph Report - PrinterControl  (2026-08-23)

## Corpus Check
- 139 files · ~93,095 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1289 nodes · 2655 edges · 86 communities (68 shown, 18 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 133 edges (avg confidence: 0.54)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4d5488b0`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- UsersView.tsx
- package.json
- Main.ps1
- Elgin Impressoras (painel de monitoramento)
- printer_fleet.py
- Coletar-Impressoras.ps1
- compilerOptions
- collect.py
- tests_uptime.py
- SNMPResult
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
- create_server
- unhandled_exception_handler
- tests_collect_api.py
- printer_sync.py
- schemas/printer.py
- cn
- types.ts
- alert_engine.py
- NetworkView.tsx
- AlertsView.tsx
- routes/auth.py
- notifications.py
- api.ts
- SNMPClient
- NotificationsView.tsx
- Printer
- Simular-Ambiente.ps1
- TonerInfo
- TonerMonitoring.tsx
- Exception
- User
- PLANO DE IMPLEMENTAÇÃO — ESCANEAR REDE REAL
- services/print_server.py
- Mapa da API
- Guia de Uso do PrinterControl
- PrinterCollector
- AppDataProvider
- snmp_fleet_mock.py
- useAppData
- Guia do Desenvolvedor
- PrinterReading
- Settings
- PrinterTable.tsx
- app-data.tsx
- auth.ts
- SQLModel
- layout.tsx
- tests_rbac.py
- Fluxo de Dados
- Arquitetura de Deploy
- Login.tsx
- BaseModel
- field_validator
- FEATURE_MATRIX.md
- patch
- PrintServer
- post
- database.py
- Role
- Session
- Notification
- snmp.py
- reports/page.tsx
- notify_alert
- .collect
- FakeAgent
- Alert
- servers.py
- PrintServerCreate
- theme.tsx
- LocalSNMPClient
- Modo Simulado

## God Nodes (most connected - your core abstractions)
1. `User` - 50 edges
2. `Printer` - 47 edges
3. `SNMPClient` - 37 edges
4. `cn()` - 37 edges
5. `SNMPResult` - 34 edges
6. `useAppData()` - 31 edges
7. `Printer` - 26 edges
8. `PrinterCollector` - 26 edges
9. `useToast()` - 25 edges
10. `enrich_discovered_printers()` - 24 edges

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

## Communities (86 total, 18 thin omitted)

### Community 0 - "UsersView.tsx"
Cohesion: 0.10
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

### Community 4 - "printer_fleet.py"
Cohesion: 0.20
Nodes (13): collect_fleet(), _collect_ip_network(), FleetCollectionResult, _group_by_ip(), _group_plan(), Printer, Session, Orquestracao da coleta da frota inteira (Etapa 5). Separacao de… (+5 more)

### Community 5 - "Coletar-Impressoras.ps1"
Cohesion: 0.21
Nodes (13): Build-SnmpGet(), Build-SnmpGetBulk(), Convert-SnmpValueBytes(), Get-ImpressorasServidor(), Get-TonerSNMP(), Parse-SnmpBulkResponse(), Parse-SnmpCounter(), Parse-SnmpInt() (+5 more)

### Community 6 - "compilerOptions"
Cohesion: 0.06
Nodes (30): dom, dom.iterable, esnext, .next/dev/types/**/*.ts, next-env.d.ts, .next/types/**/*.ts, node_modules, **/*.ts (+22 more)

### Community 7 - "collect.py"
Cohesion: 0.16
Nodes (18): collect_fleet(), collect_printer(), CollectRequest, CollectResponse, FleetCollectResponse, get_scheduler_status(), list_scenarios(), BaseModel (+10 more)

### Community 8 - "tests_uptime.py"
Cohesion: 0.08
Nodes (16): AsyncIOScheduler, _migrate_reading_uptime(), Etapa 7: adiciona printer_readings.uptime em bancos criados antes desta etapa.…, Coleta agendada (Etapa 7; frota inteira desde a Etapa 5). APScheduler roda…, Um ciclo de coleta: toda a frota ativa, agrupada por IP…, Liga o scheduler conforme o .env. Retorna None quando desabilitado., run_collection_cycle(), shutdown_scheduler() (+8 more)

### Community 9 - "SNMPResult"
Cohesion: 0.07
Nodes (33): _empty_result(), enrich_discovered_printers(), EnrichedDiscoveredPrinter, _is_color(), _is_label(), _normalize_ip(), DiscoveredPrinter, Enriquecimento transitório de filas descobertas com telemetria SNMP. (+25 more)

### Community 10 - "plugins"
Cohesion: 0.22
Nodes (8): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, typescript, warn

### Community 11 - "Printer"
Cohesion: 0.14
Nodes (14): HistoryPage(), HistoryMatrix(), HistoryMatrixProps, PrinterDetailsModalProps, PrinterRanking(), PrinterRankingProps, RankedPrinter, RankList() (+6 more)

### Community 12 - "graphify (knowledge graph tool)"
Cohesion: 0.25
Nodes (8): graphify (knowledge graph tool), graphify explain command, graphify path command, graphify query command, graphify update command, graphify-out/graph.json, graphify-out/GRAPH_REPORT.md, graphify-out/wiki/index.md

### Community 20 - "create_server"
Cohesion: 0.19
Nodes (18): create_server(), discover_server(), _get_or_404(), _marcar_resultado(), PrintServerResponse, patch, post, Session (+10 more)

### Community 21 - "unhandled_exception_handler"
Cohesion: 0.40
Nodes (5): Erro nao tratado: o detalhe vai para o log do servidor, o cliente recebe apenas…, unhandled_exception_handler(), Exception, exception_handler, Request

### Community 22 - "tests_collect_api.py"
Cohesion: 0.67
Nodes (3): check(), main(), Teste ponta a ponta dos endpoints /api/collect com os cenarios simulados.…

### Community 25 - "printer_sync.py"
Cohesion: 0.18
Nodes (13): discover_printers(), Descobre as impressoras publicadas em um Print Server. `server` e `mode` sao…, obter_modelo(), obter_tipo_impressora(), Regras de classificacao portadas do Main.ps1 (Etapa 4). Correspondencia exata:…, Traduz DriverName (Windows) em nome comercial, igual ao Main.ps1., Classifica A4 / Etiqueta / Portatil a partir de Nome+Modelo, igual ao Main.ps1., Session (+5 more)

### Community 28 - "schemas/printer.py"
Cohesion: 0.17
Nodes (15): Config, PrinterCreate, PrinterReadingCreate, PrinterReadingResponse, PrinterResponse, PrinterUpdate, PrinterWithStatus, BaseModel (+7 more)

### Community 29 - "cn"
Cohesion: 0.12
Nodes (24): DashboardPage(), AlertsDonutCard(), AlertsDonutCardProps, BottomCharts(), PagesConsumedCard(), TotalPrintsCard(), NavItem(), NavItemProps (+16 more)

### Community 30 - "types.ts"
Cohesion: 0.19
Nodes (12): BottomChartsProps, DiscoveryResults(), DiscoveryResultsProps, statusLabel(), MonthlyCounters(), MonthlyCountersProps, DiscoveredPrinter, MonthlyPageCount (+4 more)

### Community 31 - "alert_engine.py"
Cohesion: 0.19
Nodes (14): Alert, _active(), evaluate_reading(), Session, Alertas automaticos (Etapa 8A). Roda logo apos cada PrinterReading ser…, Cria, mantem ou resolve o alerta de uma condicao. Retorna a acao tomada., Avalia uma leitura e sincroniza os alertas da impressora. Faz commit ao final.…, _sync_condition() (+6 more)

### Community 32 - "NetworkView.tsx"
Cohesion: 0.10
Nodes (25): adaptDiscovered(), FORM_VAZIO, formatarMomento(), MODOS, NetworkView(), confirmarAtivacao(), executarDescoberta(), executarSync() (+17 more)

### Community 33 - "AlertsView.tsx"
Cohesion: 0.31
Nodes (6): AlertsPage(), AlertBanner(), AlertBannerProps, AlertsView(), AlertsViewProps, Alert

### Community 34 - "routes/auth.py"
Cohesion: 0.10
Nodes (22): login(), get, post, Session, Conta autenticada e seu papel — usado para decidir o que exibir/permitir., read_current_user(), Config, BaseModel (+14 more)

### Community 35 - "notifications.py"
Cohesion: 0.10
Nodes (33): Notification, Notificacoes internas (Fase 7). Por que uma tabela separada de `alerts`…, AlertRef, create_notifications(), list_notifications(), mark_as_read(), _minha_ou_404(), NotificationCreate (+25 more)

### Community 36 - "api.ts"
Cohesion: 0.08
Nodes (32): adaptAlert(), adaptPrinter(), ApiMonthlyReport, formatLastSeen(), loadMonthlyReportFromApi(), toStatus(), toToner(), VALID_COLORS (+24 more)

### Community 37 - "SNMPClient"
Cohesion: 0.27
Nodes (5): Cliente SNMP para coleta de impressoras (Printer-MIB, RFC 3805)., Cor pela descricao; se nao identificar e for colorida, usa indice % 4., SNMPv1 GET (PS1: Build-SnmpGet, version 0, PDU 0xA0)., SNMPv2c GETBULK (PS1: Build-SnmpGetBulk, version 1, PDU 0xA5)., SNMPClient

### Community 38 - "NotificationsView.tsx"
Cohesion: 0.13
Nodes (18): FORM_VAZIO, formatarMomento(), FormState, ICONE_SEVERIDADE, NotificationsView(), abrirEnvio(), enviar(), marcarComoLida() (+10 more)

### Community 39 - "Printer"
Cohesion: 0.22
Nodes (18): Printer, PrinterMonthly, SQLModel, Etapa 4: identidade e (server, name), NAO ip — o Print Server permite varias…, create_printer(), create_printer_reading(), get_printer(), get_printer_readings() (+10 more)

### Community 40 - "Simular-Ambiente.ps1"
Cohesion: 0.16
Nodes (6): Modo Real, Contador mensal calculado por diff de duas leituras SNMP acumulativas (não existe OID de páginas do mês), Scripts PowerShell reais nunca rodaram de verdade (sem interpretador PowerShell no ambiente de dev), public/data/monthly-report.json, public/data/printers.json, Arquivos de dados gerados são ignorados pelo git — gerar/apagar localmente nunca afeta o repositório

### Community 41 - "TonerInfo"
Cohesion: 0.16
Nodes (13): Decodifica bytes BER como inteiro sem sinal., Retorna (candidatos, houve_resposta_snmp)., GETBULK das tres colunas de uma vez (PS1: Build-SnmpGetBulk)., Fallback: um GET por indice (PS1: laco 1..20 com 3 falhas seguidas)., Aplica os filtros do PS1 e monta um candidato a toner., GET de um valor numerico (INTEGER, Counter32, Gauge32, TimeTicks)., GET de uma OCTET STRING., Envia um GET e devolve o primeiro varbind valido da resposta. (+5 more)

### Community 42 - "TonerMonitoring.tsx"
Cohesion: 0.11
Nodes (16): PrintersPage(), TonerPage(), PrinterTable(), RightPanel(), classify(), FILTERS, SummaryCard(), SummaryCardProps (+8 more)

### Community 44 - "User"
Cohesion: 0.18
Nodes (20): create_db_and_tables(), True se o papel do usuario satisfaz qualquer um dos exigidos., User, hash_password(), seed_database(), check(), check_true(), h() (+12 more)

### Community 45 - "PLANO DE IMPLEMENTAÇÃO — ESCANEAR REDE REAL"
Cohesion: 0.05
Nodes (39): A. Endpoint (implementado), Alertas, Arquitetura atual, Arquitetura do PrinterControl, B. Service reutilizável, Banco, C. Funções Print Server reutilizáveis, Cliente de API (+31 more)

### Community 46 - "services/print_server.py"
Cohesion: 0.09
Nodes (16): DiscoveredPrinter, _mock_discover(), PrintServerError, Exception, Camada de Print Server (Etapa 3). Reproduz a descoberta de impressoras do…, Equivalente exato de Get-ImpressorasEmpresa + o inicio de Process-…, Uma linha do que Get-Printer + Get-PrinterPort devolveriam, combinadas., RPC ao Print Server falhou ou saida do PowerShell nao pode ser interpretada. (+8 more)

### Community 47 - "Mapa da API"
Cohesion: 0.04
Nodes (45): Alertas, Autenticação, Coleta, Diagnóstico, Escanear Rede (implementado), `GET /`, `GET /api/alerts`, `GET /api/alerts/{alert_id}` (+37 more)

### Community 48 - "Guia de Uso do PrinterControl"
Cohesion: 0.10
Nodes (20): Acessar via web — PARCIAL, Adicionar impressora — AUSENTE/PARCIAL, Alertas — FUNCIONAL na leitura; PARCIAL nas ações, Ações, Como acessar, Configurações — COMING SOON, Configurações, Usuários e Integrações — COMING SOON, Dashboard — FUNCIONAL/PARCIAL (+12 more)

### Community 49 - "PrinterCollector"
Cohesion: 0.14
Nodes (11): PrinterCollector, Printer, Session, Converte SNMPResult em PrinterReading. Toner ausente vira NULL (a coluna e…, Cenarios de teste disponiveis (fonte unica: snmp_mock.SCENARIOS)., Coleta uma impressora e grava o resultado como PrinterReading., Args: mode: "real" (SNMP de verdade), "mock" (cenario fixo) ou "fleet" (frota…, Deduz se a impressora e colorida a partir do modelo/nome (regra do PS1). (+3 more)

### Community 50 - "AppDataProvider"
Cohesion: 0.21
Nodes (12): discoverPrinters(), fetchUnreadNotificationCount(), useApiErrorReporter(), AppDataProvider(), expireSession(), handleAlertSelect(), handleDiscovery(), handleLogout() (+4 more)

### Community 51 - "snmp_fleet_mock.py"
Cohesion: 0.23
Nodes (10): _base_page_count(), _increment(), profile_for(), Simulador de frota — APENAS PARA TESTE LOCAL. Diferenca para snmp_mock.py: la…, Perfil deterministico da impressora: online | offline | snmp_mudo | baixo |…, Contador inicial plausivel para uma impressora que nunca foi lida., Paginas impressas entre duas coletas — fixo por impressora, 5 a 124., Nivel do toner: base do perfil + desvio deterministico por impressora/cor,… (+2 more)

### Community 52 - "useAppData"
Cohesion: 0.12
Nodes (20): react, ReportsPage(), AppShell(), AuthGate(), Login(), Modal(), ModalProps, PrinterDetailsModal() (+12 more)

### Community 53 - "Guia do Desenvolvedor"
Cohesion: 0.13
Nodes (14): Backend, Banco, Comandos do frontend, Escanear Rede (implementado), Guia do Desenvolvedor, O que não executar em produção sem autorização, Print Server, Riscos conhecidos (+6 more)

### Community 54 - "PrinterReading"
Cohesion: 0.18
Nodes (8): PrinterReading, Orquestrador da coleta de impressoras. Separa as tres responsabilidades da…, collect_fleet(), Etapa 11 - coleta simulada da frota inteira, ponta a ponta. Copia o banco real…, Uma coleta completa. Devolve resumo por status., make_offline_reading(), make_reading(), reset_alerts_and_readings()

### Community 55 - "Settings"
Cohesion: 0.18
Nodes (7): Config, field_validator, Normaliza um DATABASE_URL sqlite relativo (ex.: sqlite:///./x.db) para um…, Impede que um ambiente de producao suba silenciosamente com o secret de…, Settings, BaseSettings, model_validator

### Community 56 - "PrinterTable.tsx"
Cohesion: 0.31
Nodes (9): config, PrinterStatusBadge(), PAGE_SIZE_OPTIONS, PrinterTableProps, filterPrinters(), PrinterFilters, getPrinterType(), PrinterType (+1 more)

### Community 57 - "app-data.tsx"
Cohesion: 0.17
Nodes (15): Levantamento_impressões (planilha original), RightPanelProps, decommissionedPrinters, globalToner, monthlyUsage, networkHistory, printers, AppDataContext (+7 more)

### Community 58 - "auth.ts"
Cohesion: 0.23
Nodes (16): handleSubmit(), clearToken(), getToken(), isTokenPersistent(), setToken(), ApiUser, cacheAccount(), fetchCurrentUser() (+8 more)

### Community 60 - "layout.tsx"
Cohesion: 0.29
Nodes (5): ibmPlexMono, metadata, publicSans, sourceSerif, Providers()

### Community 61 - "tests_rbac.py"
Cohesion: 0.24
Nodes (12): check(), check_true(), _confere_rbac_do_frontend(), h(), main(), Fase 1 - Autenticacao, RBAC e protecao das rotas. Diferente dos demais…, O frontend tem a sua propria copia da hierarquia de papeis, em…, Cria um banco no formato ANTERIOR a Fase 1 (users sem role/is_active), roda a… (+4 more)

### Community 62 - "Fluxo de Dados"
Cohesion: 0.17
Nodes (11): 10. Escanear Rede (implementado), 1. Cadastro no SQLite, 2. Coleta SNMP real, 3. Coleta de frota, 4. Print Server, 5. Sincronização, 6. Alertas, 7. Relatório mensal (+3 more)

### Community 63 - "Arquitetura de Deploy"
Cohesion: 0.18
Nodes (10): Arquitetura avaliada, Arquitetura de Deploy, Autenticação, Bloqueios atuais, Cloudflare Tunnel, Configuração de aplicação, CORS, Estado atual (+2 more)

### Community 64 - "Login.tsx"
Cohesion: 0.15
Nodes (11): Logo Elgin é redesenho à mão (IA sem acesso a imagens coladas no chat, só uploads), src/components/ (padrão com header-comment por arquivo), ElginLogo(), ElginLogoProps, ACTIVE_NODES, features, LoginProps, NETWORK_LINKS (+3 more)

### Community 69 - "PrintServer"
Cohesion: 0.29
Nodes (6): PrintServer, SQLModel, str, Print Server como entidade (Fase 4). Ate aqui um Print Server existia de duas…, Modos aceitos, iguais aos de `settings.print_server_mode`., ServerMode

### Community 71 - "database.py"
Cohesion: 0.09
Nodes (28): _finish_printer_migration(), get_session(), _migrate_alert_type(), _migrate_print_servers(), _migrate_printer_schema(), _migrate_user_rbac(), Fase 4: registro de Print Servers. A tabela `print_servers` em si e criada pelo…, Caminho do arquivo .db atual, se o banco for SQLite em disco (nao :memory:). (+20 more)

### Community 72 - "Role"
Cohesion: 0.14
Nodes (18): SQLModel, str, RBAC minimo (Fase 1). Tres papeis cobrem todas as rotas existentes hoje: -…, Role, _active_admin_count(), create_user(), _ensure_not_last_admin(), list_users() (+10 more)

### Community 75 - "snmp.py"
Cohesion: 0.26
Nodes (10): parse_varbinds(), SNMP Collector para impressoras. Porte direto da funcao Get-TonerSNMP de…, Decodifica um OID BER para notacao pontuada., Extrai a lista de varbinds de uma resposta SNMP. Percorre a estrutura completa…, Le um TLV BER. Retorna (tag, length, value_start, next_pos)., _read_oid(), _read_tlv(), check() (+2 more)

### Community 76 - "reports/page.tsx"
Cohesion: 0.23
Nodes (8): DecommissionedList(), DecommissionedListProps, DepartmentBreakdown(), DepartmentBreakdownProps, MONTHS, DecommissionedPrinter, DepartmentUsage, STATUS_LABEL

### Community 77 - "notify_alert"
Cohesion: 0.20
Nodes (11): get_alert(), list_alerts(), notify_alert(), get, patch, post, Session, Resolve um alerta. Ate a Fase 1 esta rota estava SEM protecao alguma — qualquer… (+3 more)

### Community 78 - ".collect"
Cohesion: 0.20
Nodes (5): Coleta status, contador de paginas e toners de uma impressora. Nunca levanta…, PS1: `if ($ip -match '^\\d')` — descarta 'N/A' e nomes de porta., ICMP ping, equivalente ao `New-Object ...Ping).Send($ip, 400)` do PS1. SNMP…, Escolhe os toners finais. PS1 colorida: um por cor (primeiro de cada grupo),…, Ticks de 1/100s -> 'Xd, Yh, Zm' (mesmo formato do PS1).

### Community 79 - "FakeAgent"
Cohesion: 0.31
Nodes (3): FakeAgent, Extrai (pdu_tag, [oids]) de um GET/GETBULK., Responde GET e GETBULK para um conjunto de OIDs configurado.

### Community 80 - "Alert"
Cohesion: 0.36
Nodes (6): Alert, SQLModel, TonerHistory, active(), Etapa 8A - validacao dos alertas automaticos. Usa banco SQLite temporario e o…, resolved()

### Community 81 - "servers.py"
Cohesion: 0.17
Nodes (17): discover(), DiscoveredPrinterResponse, DiscoverResponse, _executar_discover(), get_current_server(), list_servers(), BaseModel, get (+9 more)

### Community 82 - "PrintServerCreate"
Cohesion: 0.33
Nodes (4): PrintServerCreate, PrintServerUpdate, field_validator, `host` fica de fora de proposito: ele e a chave natural que aparece em…

### Community 83 - "theme.tsx"
Cohesion: 0.33
Nodes (5): getInitialTheme(), Theme, ThemeContext, ThemeContextValue, ThemeProvider()

## Knowledge Gaps
- **272 isolated node(s):** ``GET /api/auth/me``, ``POST /api/auth/login``, ``GET /api/users``, ``POST /api/users``, ``PATCH /api/users/{user_id}`` (+267 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `routes/auth.py`, `collect.py`, `Role`, `database.py`, `Printer`, `tests_uptime.py`, `notify_alert`, `servers.py`, `create_server`, `tests_rbac.py`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Why does `SNMPClient` connect `SNMPClient` to `printer_fleet.py`, `tests_uptime.py`, `SNMPResult`, `TonerInfo`, `snmp.py`, `.collect`, `FakeAgent`, `PrinterCollector`, `LocalSNMPClient`, `PrinterReading`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Why does `Printer` connect `Printer` to `notifications.py`, `printer_fleet.py`, `collect.py`, `database.py`, `tests_uptime.py`, `User`, `notify_alert`, `Alert`, `servers.py`, `PrinterCollector`, `create_server`, `PrinterReading`, `printer_sync.py`, `tests_rbac.py`, `alert_engine.py`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Are the 29 inferred relationships involving `User` (e.g. with `require_roles()` and `require_user()`) actually correct?**
  _`User` has 29 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `Printer` (e.g. with `_finish_printer_migration()` and `notify_alert()`) actually correct?**
  _`Printer` has 22 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `SNMPClient` (e.g. with `PrinterCollector` and `FakeAgent`) actually correct?**
  _`SNMPClient` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `SNMPResult` (e.g. with `enrich_discovered_printers()` and `PrinterCollector`) actually correct?**
  _`SNMPResult` has 6 INFERRED edges - model-reasoned connections that need verification._