# Graph Report - PrinterControl  (2026-08-23)

## Corpus Check
- 145 files · ~101,602 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1354 nodes · 2866 edges · 82 communities (71 shown, 11 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 136 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b52a44f4`
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
- tests_webhook.py
- tests_printer_fleet.py
- SNMPResult
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
- NotificationsView.tsx
- DiscoveryResults.tsx
- Printer
- Sidebar.tsx
- _migrate_printer_schema
- alert_engine.py
- NetworkView.tsx
- collect_printer
- tests_printers_crud.py
- notifications.py
- api.ts
- SNMPClient
- adaptApi.ts
- snmp.py
- Simular-Ambiente.ps1
- database.py
- cn
- app/page.tsx
- Role
- PLANO DE IMPLEMENTAÇÃO — ESCANEAR REDE REAL
- services/print_server.py
- Impressoras
- Guia de Uso do PrinterControl
- ElginLogo.tsx
- app-data.tsx
- tests_fleet.py
- useAppData
- Guia do Desenvolvedor
- User
- create_db_and_tables
- ServerMode
- MockSNMPScenarios
- auth.ts
- Alert
- SettingsView.tsx
- Print Server
- Fluxo de Dados
- Arquitetura de Deploy
- toast.tsx
- tests_print_servers.py
- Autenticação
- FEATURE_MATRIX.md
- layout.tsx
- Relatorio-Mensal.ps1
- Mapa da API
- Notificações (Fase 7)
- Alertas
- Coleta
- Usuários (Fase 3)
- reports/page.tsx
- ambiente
- NotificationCreate
- integrations/page.tsx
- fetchPrinters.ts
- tests_rbac.py
- MockSNMPClient

## God Nodes (most connected - your core abstractions)
1. `User` - 65 edges
2. `Printer` - 49 edges
3. `cn()` - 39 edges
4. `SNMPClient` - 37 edges
5. `SNMPResult` - 34 edges
6. `useAppData()` - 33 edges
7. `useToast()` - 27 edges
8. `create_db_and_tables()` - 26 edges
9. `PrinterCollector` - 26 edges
10. `Printer` - 26 edges

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

## Communities (82 total, 11 thin omitted)

### Community 0 - "UsersView.tsx"
Cohesion: 0.13
Nodes (19): RequireRole(), FORM_VAZIO, formatarData(), FormState, UsersView(), abrirEdicao(), confirmarAtivacao(), salvar() (+11 more)

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
Cohesion: 0.09
Nodes (27): PrinterCollector, Printer, Session, Orquestrador da coleta de impressoras. Separa as tres responsabilidades da…, Converte SNMPResult em PrinterReading. Toner ausente vira NULL (a coluna e…, Coleta uma impressora e grava o resultado como PrinterReading., Deduz se a impressora e colorida a partir do modelo/nome (regra do PS1)., Etiquetadora/portatil: sem Printer-MIB, o PS1 nem consulta SNMP. (+19 more)

### Community 5 - "Coletar-Impressoras.ps1"
Cohesion: 0.21
Nodes (13): Build-SnmpGet(), Build-SnmpGetBulk(), Convert-SnmpValueBytes(), Get-ImpressorasServidor(), Get-TonerSNMP(), Parse-SnmpBulkResponse(), Parse-SnmpCounter(), Parse-SnmpInt() (+5 more)

### Community 6 - "compilerOptions"
Cohesion: 0.06
Nodes (30): dom, dom.iterable, esnext, .next/dev/types/**/*.ts, next-env.d.ts, .next/types/**/*.ts, node_modules, **/*.ts (+22 more)

### Community 7 - "tests_webhook.py"
Cohesion: 0.29
Nodes (7): PrinterMonthly, PrinterReading, SQLModel, make_offline_reading(), make_reading(), Etapa 6 - webhook de alerta critico de toner. Banco SQLite temporario e ISOLADO…, reset_alerts_and_readings()

### Community 8 - "tests_printer_fleet.py"
Cohesion: 0.18
Nodes (4): fake_real_collect(), Etapa 5 - orquestracao da frota (printer_fleet.collect_fleet). Roda sobre um…, RecordingThreadPoolExecutor, _OriginalTPE

### Community 9 - "SNMPResult"
Cohesion: 0.16
Nodes (19): _empty_result(), enrich_discovered_printers(), EnrichedDiscoveredPrinter, _is_color(), _is_label(), _normalize_ip(), DiscoveredPrinter, Enriquecimento transitório de filas descobertas com telemetria SNMP. (+11 more)

### Community 10 - "plugins"
Cohesion: 0.22
Nodes (8): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, typescript, warn

### Community 11 - "HistoryMatrix.tsx"
Cohesion: 0.33
Nodes (4): HistoryMatrix(), HistoryMatrixProps, getDepartmentLabel(), getPrinterSite()

### Community 12 - "graphify (knowledge graph tool)"
Cohesion: 0.25
Nodes (8): graphify (knowledge graph tool), graphify explain command, graphify path command, graphify query command, graphify update command, graphify-out/graph.json, graphify-out/GRAPH_REPORT.md, graphify-out/wiki/index.md

### Community 20 - "servers.py"
Cohesion: 0.09
Nodes (42): PrintServer, create_server(), discover(), discover_server(), DiscoveredPrinterResponse, DiscoverResponse, _executar_discover(), get_current_server() (+34 more)

### Community 21 - "unhandled_exception_handler"
Cohesion: 0.40
Nodes (5): Exception, Erro nao tratado: o detalhe vai para o log do servidor, o cliente recebe apenas…, unhandled_exception_handler(), exception_handler, Request

### Community 22 - "tests_collect_api.py"
Cohesion: 0.67
Nodes (3): check(), main(), Teste ponta a ponta dos endpoints /api/collect com os cenarios simulados.…

### Community 23 - "NotificationsView.tsx"
Cohesion: 0.14
Nodes (18): FORM_VAZIO, formatarMomento(), FormState, ICONE_SEVERIDADE, NotificationsView(), abrirEnvio(), enviar(), marcarComoLida() (+10 more)

### Community 25 - "DiscoveryResults.tsx"
Cohesion: 0.60
Nodes (4): DiscoveryResults(), DiscoveryResultsProps, statusLabel(), DiscoveredPrinter

### Community 28 - "Printer"
Cohesion: 0.12
Nodes (31): Printer, Etapa 4: identidade e (server, name), NAO ip — o Print Server permite varias…, create_printer(), create_printer_reading(), get_printer(), get_printer_readings(), list_printers(), list_printers_with_status() (+23 more)

### Community 29 - "Sidebar.tsx"
Cohesion: 0.11
Nodes (22): AlertsDonutCard(), AlertsDonutCardProps, BottomChartsProps, PagesConsumedCard(), TotalPrintsCard(), DemoDataBadge(), DemoDataBadgeProps, MonthlyCounters() (+14 more)

### Community 30 - "_migrate_printer_schema"
Cohesion: 0.33
Nodes (6): _finish_printer_migration(), _migrate_printer_schema(), Caminho do arquivo .db atual, se o banco for SQLite em disco (nao :memory:)., Etapa 4 — reconstroi `printers` para trocar a identidade de `ip UNIQUE` para…, Recria `printers` (schema atual) e copia `printers_old` para dentro dela, numa…, _sqlite_backup_path()

### Community 31 - "alert_engine.py"
Cohesion: 0.18
Nodes (15): Alert, _active(), evaluate_reading(), Session, Alertas automaticos (Etapa 8A). Roda logo apos cada PrinterReading ser…, Cria, mantem ou resolve o alerta de uma condicao. Retorna a acao tomada., Avalia uma leitura e sincroniza os alertas da impressora. Faz commit ao final.…, _sync_condition() (+7 more)

### Community 32 - "NetworkView.tsx"
Cohesion: 0.10
Nodes (25): adaptDiscovered(), FORM_VAZIO, formatarMomento(), MODOS, NetworkView(), confirmarAtivacao(), executarDescoberta(), executarSync() (+17 more)

### Community 33 - "collect_printer"
Cohesion: 0.27
Nodes (10): collect_fleet(), collect_printer(), CollectRequest, CollectResponse, FleetCollectResponse, BaseModel, post, Session (+2 more)

### Community 34 - "tests_printers_crud.py"
Cohesion: 0.33
Nodes (3): Etapa 12 - CRUD de impressoras contra o servidor rodando. Usa o banco REAL,…, Devolve (status, payload)., request()

### Community 35 - "notifications.py"
Cohesion: 0.13
Nodes (28): Notification, SQLModel, Notificacoes internas (Fase 7). Por que uma tabela separada de `alerts`…, AlertRef, create_notifications(), list_notifications(), mark_all_as_read(), mark_as_read() (+20 more)

### Community 36 - "api.ts"
Cohesion: 0.10
Nodes (17): marcarTodasComoLidas(), API_BASE_URL, ApiDiscoveredPrinter, ApiDiscoveredToner, ApiNotificationAlertRef, ApiPrinterReading, apiRequest(), describeDetail() (+9 more)

### Community 37 - "SNMPClient"
Cohesion: 0.08
Nodes (23): parse_varbinds(), Decodifica bytes BER como inteiro sem sinal., Extrai a lista de varbinds de uma resposta SNMP. Percorre a estrutura completa…, Cliente SNMP para coleta de impressoras (Printer-MIB, RFC 3805)., Coleta status, contador de paginas e toners de uma impressora. Nunca levanta…, PS1: `if ($ip -match '^\\d')` — descarta 'N/A' e nomes de porta., ICMP ping, equivalente ao `New-Object ...Ping).Send($ip, 400)` do PS1. SNMP…, Retorna (candidatos, houve_resposta_snmp). (+15 more)

### Community 38 - "adaptApi.ts"
Cohesion: 0.13
Nodes (19): adaptAlert(), adaptPrinter(), ApiMonthlyReport, formatLastSeen(), loadMonthlyReportFromApi(), toStatus(), toToner(), VALID_COLORS (+11 more)

### Community 39 - "snmp.py"
Cohesion: 0.12
Nodes (13): SNMP Collector para impressoras. Porte direto da funcao Get-TonerSNMP de…, Decodifica um OID BER para notacao pontuada., Le um TLV BER. Retorna (tag, length, value_start, next_pos)., _read_oid(), _read_tlv(), check(), FakeAgent, LocalSNMPClient (+5 more)

### Community 40 - "Simular-Ambiente.ps1"
Cohesion: 0.22
Nodes (5): Modo Simulado, public/data/monthly-report.json, public/data/printers.json, Arquivos de dados gerados são ignorados pelo git — gerar/apagar localmente nunca afeta o repositório, Impressoras simuladas usam prefixo SIM_ / departamentos TESTE - de propósito, pra nunca confundir com dado real

### Community 41 - "database.py"
Cohesion: 0.09
Nodes (32): AsyncIOScheduler, get_session(), Session, Dependencias compartilhadas pelas rotas. Autorizacao (Fase 1) fica CENTRALIZADA…, Usuario dono do JWT do header Authorization. 401 se ausente/invalido. O usuario…, require_user(), health_check(), lifespan() (+24 more)

### Community 42 - "cn"
Cohesion: 0.10
Nodes (32): PrinterDetailsModal(), PrinterDetailsModalProps, PrinterRanking(), PrinterRankingProps, RankedPrinter, RankList(), rankPrinters(), config (+24 more)

### Community 43 - "app/page.tsx"
Cohesion: 0.19
Nodes (9): AlertBanner(), AlertBannerProps, BottomCharts(), StatCard(), StatCardProps, StatCards(), StatCardsProps, TONE (+1 more)

### Community 44 - "Role"
Cohesion: 0.08
Nodes (36): str, RBAC minimo (Fase 1). Tres papeis cobrem todas as rotas existentes hoje: -…, Role, login(), patch, post, Session, Perfil da PROPRIA conta (Fase 8). So o nome. Nao recebe id: o alvo e sempre a… (+28 more)

### Community 45 - "PLANO DE IMPLEMENTAÇÃO — ESCANEAR REDE REAL"
Cohesion: 0.05
Nodes (39): A. Endpoint (implementado), Alertas, Arquitetura atual, Arquitetura do PrinterControl, B. Service reutilizável, Banco, C. Funções Print Server reutilizáveis, Cliente de API (+31 more)

### Community 46 - "services/print_server.py"
Cohesion: 0.06
Nodes (29): discover_printers(), DiscoveredPrinter, _mock_discover(), PrintServerError, Exception, Camada de Print Server (Etapa 3). Reproduz a descoberta de impressoras do…, Equivalente exato de Get-ImpressorasEmpresa + o inicio de Process-…, Descobre as impressoras publicadas em um Print Server. `server` e `mode` sao… (+21 more)

### Community 47 - "Impressoras"
Cohesion: 0.22
Nodes (9): `GET /api/printers`, `GET /api/printers/monthly-report`, `GET /api/printers/{printer_id}`, `GET /api/printers/{printer_id}/readings`, `GET /api/printers/with-status`, Impressoras, `PATCH /api/printers/{printer_id}`, `POST /api/printers` (+1 more)

### Community 48 - "Guia de Uso do PrinterControl"
Cohesion: 0.10
Nodes (20): Acessar via web — PARCIAL, Adicionar impressora — AUSENTE/PARCIAL, Alertas — FUNCIONAL na leitura; PARCIAL nas ações, Ações, Como acessar, Configurações — COMING SOON, Configurações, Usuários e Integrações — COMING SOON, Dashboard — FUNCIONAL/PARCIAL (+12 more)

### Community 49 - "ElginLogo.tsx"
Cohesion: 0.40
Nodes (4): Logo Elgin é redesenho à mão (IA sem acesso a imagens coladas no chat, só uploads), src/components/ (padrão com header-comment por arquivo), ElginLogo(), ElginLogoProps

### Community 50 - "app-data.tsx"
Cohesion: 0.11
Nodes (30): Levantamento_impressões (planilha original), RightPanel(), RightPanelProps, decommissionedPrinters, globalToner, monthlyUsage, printers, BackendEnvironment (+22 more)

### Community 51 - "tests_fleet.py"
Cohesion: 0.14
Nodes (13): _base_page_count(), _increment(), profile_for(), Simulador de frota — APENAS PARA TESTE LOCAL. Diferenca para snmp_mock.py: la…, Perfil deterministico da impressora: online | offline | snmp_mudo | baixo |…, Contador inicial plausivel para uma impressora que nunca foi lida., Paginas impressas entre duas coletas — fixo por impressora, 5 a 124., Nivel do toner: base do perfil + desvio deterministico por impressora/cor,… (+5 more)

### Community 52 - "useAppData"
Cohesion: 0.11
Nodes (17): react, AlertsPage(), HistoryPage(), DashboardPage(), PrintersPage(), TonerPage(), AlertsView(), AlertsViewProps (+9 more)

### Community 53 - "Guia do Desenvolvedor"
Cohesion: 0.13
Nodes (14): Backend, Banco, Comandos do frontend, Escanear Rede (implementado), Guia do Desenvolvedor, O que não executar em produção sem autorização, Print Server, Riscos conhecidos (+6 more)

### Community 54 - "User"
Cohesion: 0.14
Nodes (20): Fabrica de dependencia: exige que o usuario tenha (ou herde) um dos papeis…, require_roles(), SQLModel, True se o papel do usuario satisfaz qualquer um dos exigidos., User, change_own_password(), get, Conta autenticada e seu papel — usado para decidir o que exibir/permitir. (+12 more)

### Community 55 - "create_db_and_tables"
Cohesion: 0.13
Nodes (22): create_db_and_tables(), _migrate_alert_type(), _migrate_print_servers(), _migrate_reading_uptime(), _migrate_user_rbac(), Fase 4: registro de Print Servers. A tabela `print_servers` em si e criada pelo…, Adiciona alerts.alert_type em bancos criados antes da Etapa 8A., Etapa 7: adiciona printer_readings.uptime em bancos criados antes desta etapa.… (+14 more)

### Community 56 - "ServerMode"
Cohesion: 0.67
Nodes (3): str, Modos aceitos, iguais aos de `settings.print_server_mode`., ServerMode

### Community 57 - "MockSNMPScenarios"
Cohesion: 0.11
Nodes (13): MockSNMPScenarios, Agente SNMP simulado — APENAS PARA TESTE LOCAL. Existe porque a maquina de…, SNMP responde o contador, mas nao expoe a tabela de consumiveis., Monocromatica com toner em 5%., Colorida com ciano critico (18%) e os demais normais., Contador reiniciado (troca de placa/formatador): page_count baixo., Cenarios de teste. Cada metodo devolve um SNMPResult completo., Monocromatica saudavel. (+5 more)

### Community 58 - "auth.ts"
Cohesion: 0.21
Nodes (17): handleSubmit(), salvarPerfil(), api, clearToken(), isTokenPersistent(), setToken(), ApiUser, cacheAccount() (+9 more)

### Community 59 - "Alert"
Cohesion: 0.21
Nodes (14): Alert, SQLModel, TonerHistory, get_alert(), list_alerts(), notify_alert(), get, patch (+6 more)

### Community 60 - "SettingsView.tsx"
Cohesion: 0.11
Nodes (21): SettingsView(), trocarSenha(), validarSenha(), TEMAS, changeMyPassword(), ESCALAS, ler(), Preferences (+13 more)

### Community 61 - "Print Server"
Cohesion: 0.22
Nodes (9): `GET /api/servers`, `GET /api/servers/current`, `PATCH /api/servers/{server_id}`, `POST /api/servers`, `POST /api/servers/discover`, `POST /api/servers/{server_id}/discover`, `POST /api/servers/{server_id}/sync`, `POST /api/servers/sync` (+1 more)

### Community 62 - "Fluxo de Dados"
Cohesion: 0.17
Nodes (11): 10. Escanear Rede (implementado), 1. Cadastro no SQLite, 2. Coleta SNMP real, 3. Coleta de frota, 4. Print Server, 5. Sincronização, 6. Alertas, 7. Relatório mensal (+3 more)

### Community 63 - "Arquitetura de Deploy"
Cohesion: 0.18
Nodes (10): Arquitetura avaliada, Arquitetura de Deploy, Autenticação, Bloqueios atuais, Cloudflare Tunnel, Configuração de aplicação, CORS, Estado atual (+2 more)

### Community 64 - "toast.tsx"
Cohesion: 0.10
Nodes (15): ACTIVE_NODES, features, Login(), LoginProps, NETWORK_LINKS, NETWORK_NODES, ApiError, Account (+7 more)

### Community 65 - "tests_print_servers.py"
Cohesion: 0.16
Nodes (10): SQLModel, Print Server como entidade (Fase 4). Ate aqui um Print Server existia de duas…, Fase 9 - Mock e Demo Seguros. Cobre as DUAS camadas que protegem o risco…, check(), check_true(), h(), main(), Fase 4 - Registro de Print Servers e operacao por servidor. Como… (+2 more)

### Community 66 - "Autenticação"
Cohesion: 0.29
Nodes (7): Autenticação, Bloqueio de simulação em produção (Fase 9), `GET /api/auth/me`, `GET /health`, `PATCH /api/auth/me`, `POST /api/auth/change-password`, `POST /api/auth/login`

### Community 68 - "layout.tsx"
Cohesion: 0.29
Nodes (5): ibmPlexMono, metadata, publicSans, sourceSerif, Providers()

### Community 69 - "Relatorio-Mensal.ps1"
Cohesion: 0.33
Nodes (3): Modo Real, Contador mensal calculado por diff de duas leituras SNMP acumulativas (não existe OID de páginas do mês), Scripts PowerShell reais nunca rodaram de verdade (sem interpretador PowerShell no ambiente de dev)

### Community 70 - "Mapa da API"
Cohesion: 0.33
Nodes (5): Diagnóstico, Escanear Rede (implementado), `GET /`, `GET /health`, Mapa da API

### Community 71 - "Notificações (Fase 7)"
Cohesion: 0.33
Nodes (6): `GET /api/notifications`, `GET /api/notifications/unread-count`, Notificações (Fase 7), `PATCH /api/notifications/{notification_id}/read`, `POST /api/notifications`, `POST /api/notifications/read-all`

### Community 72 - "Alertas"
Cohesion: 0.40
Nodes (5): Alertas, `GET /api/alerts`, `GET /api/alerts/{alert_id}`, `PATCH /api/alerts/{alert_id}/resolve`, `POST /api/alerts/{alert_id}/notify`

### Community 74 - "Coleta"
Cohesion: 0.40
Nodes (5): Coleta, `GET /api/collect/scenarios`, `GET /api/collect/scheduler`, `POST /api/collect/fleet`, `POST /api/collect/printers/{printer_id}`

### Community 75 - "Usuários (Fase 3)"
Cohesion: 0.50
Nodes (4): `GET /api/users`, `PATCH /api/users/{user_id}`, `POST /api/users`, Usuários (Fase 3)

### Community 76 - "reports/page.tsx"
Cohesion: 0.21
Nodes (10): ReportsPage(), DecommissionedList(), DecommissionedListProps, DepartmentBreakdown(), DepartmentBreakdownProps, MONTHS, DecommissionedPrinter, DepartmentUsage (+2 more)

### Community 79 - "NotificationCreate"
Cohesion: 0.47
Nodes (3): NotificationCreate, field_validator, Uma comunicacao para um ou mais destinatarios (uma linha por pessoa).

### Community 83 - "tests_rbac.py"
Cohesion: 0.08
Nodes (24): Config, field_validator, Fail-fast: producao nao sobe com simulacao ligada (Fase 9). O risco concreto e…, Impede que um ambiente de producao suba silenciosamente com o secret de…, Normaliza um DATABASE_URL sqlite relativo (ex.: sqlite:///./x.db) para um…, Um ambiente escrito errado nao pode cair no default em silencio:…, Settings, Settings de producao valida, sobrescrevendo so o que o teste investiga. (+16 more)

### Community 86 - "MockSNMPClient"
Cohesion: 0.20
Nodes (5): Cenarios de teste disponiveis (fonte unica: snmp_mock.SCENARIOS)., Args: mode: "real" (SNMP de verdade), "mock" (cenario fixo) ou "fleet" (frota…, MockSNMPClient, Substituto do SNMPClient com a mesma assinatura de collect()., Devolve o resultado fixo do cenario (ip e is_color sao ignorados).

## Knowledge Gaps
- **282 isolated node(s):** `$schema`, `typescript`, `oxc`, `react/rules-of-hooks`, `warn` (+277 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SNMPClient` connect `SNMPClient` to `PrinterCollector`, `snmp.py`, `tests_printer_fleet.py`, `SNMPResult`, `MockSNMPClient`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Why does `User` connect `User` to `collect_printer`, `tests_print_servers.py`, `notifications.py`, `PrinterCollector`, `tests_webhook.py`, `database.py`, `Role`, `tests_rbac.py`, `servers.py`, `create_db_and_tables`, `Alert`, `Printer`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Why does `enrich_discovered_printers()` connect `SNMPResult` to `servers.py`, `SNMPClient`, `MockSNMPClient`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Are the 37 inferred relationships involving `User` (e.g. with `require_roles()` and `require_user()`) actually correct?**
  _`User` has 37 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `Printer` (e.g. with `_finish_printer_migration()` and `notify_alert()`) actually correct?**
  _`Printer` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `SNMPClient` (e.g. with `PrinterCollector` and `FakeAgent`) actually correct?**
  _`SNMPClient` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `SNMPResult` (e.g. with `enrich_discovered_printers()` and `PrinterCollector`) actually correct?**
  _`SNMPResult` has 6 INFERRED edges - model-reasoned connections that need verification._