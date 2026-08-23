# Graph Report - PrinterControl  (2026-08-21)

## Corpus Check
- 131 files · ~79,528 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1131 nodes · 2305 edges · 71 communities (61 shown, 10 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 112 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `01a8f991`
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
- PrintServerDiscoveryTests
- tests_printer_fleet.py
- RequireRole.tsx
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
- SNMPResult
- unhandled_exception_handler
- tests_collect_api.py
- discovery.py
- printers.py
- cn
- collect.py
- alert_engine.py
- Relatorio-Mensal.ps1
- app/page.tsx
- routes/auth.py
- enrich_discovered_printers
- adaptApi.ts
- Settings
- Topbar
- useAppData
- Simular-Ambiente.ps1
- SNMPClient
- TonerMonitoring.tsx
- Printer
- fetchPrinters.ts
- PLANO DE IMPLEMENTAÇÃO — ESCANEAR REDE REAL
- servers.py
- Impressoras
- Guia de Uso do PrinterControl
- database.py
- app-data.tsx
- tests_fleet.py
- toast.tsx
- Guia do Desenvolvedor
- layout.tsx
- Role
- types.ts
- tests_webhook.py
- auth.ts
- User
- update_user
- tests_rbac.py
- Fluxo de Dados
- Arquitetura de Deploy
- Login.tsx
- api.ts
- resolve_alert
- FEATURE_MATRIX.md
- tests_printer_sync.py
- _migrate_printer_schema
- read_current_user

## God Nodes (most connected - your core abstractions)
1. `User` - 44 edges
2. `Printer` - 42 edges
3. `SNMPClient` - 37 edges
4. `SNMPResult` - 34 edges
5. `cn()` - 33 edges
6. `PrinterCollector` - 26 edges
7. `Printer` - 26 edges
8. `enrich_discovered_printers()` - 25 edges
9. `useAppData()` - 25 edges
10. `PrinterReading` - 22 edges

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

## Communities (71 total, 10 thin omitted)

### Community 0 - "UsersView.tsx"
Cohesion: 0.14
Nodes (20): FORM_VAZIO, formatarData(), FormState, UsersView(), abrirEdicao(), confirmarAtivacao(), salvar(), validar() (+12 more)

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
Cohesion: 0.12
Nodes (15): PrinterCollector, Printer, Session, Orquestrador da coleta de impressoras. Separa as tres responsabilidades da…, Converte SNMPResult em PrinterReading. Toner ausente vira NULL (a coluna e…, Coleta uma impressora e grava o resultado como PrinterReading., Deduz se a impressora e colorida a partir do modelo/nome (regra do PS1)., Etiquetadora/portatil: sem Printer-MIB, o PS1 nem consulta SNMP. (+7 more)

### Community 5 - "Coletar-Impressoras.ps1"
Cohesion: 0.21
Nodes (13): Build-SnmpGet(), Build-SnmpGetBulk(), Convert-SnmpValueBytes(), Get-ImpressorasServidor(), Get-TonerSNMP(), Parse-SnmpBulkResponse(), Parse-SnmpCounter(), Parse-SnmpInt() (+5 more)

### Community 6 - "compilerOptions"
Cohesion: 0.06
Nodes (30): dom, dom.iterable, esnext, .next/dev/types/**/*.ts, next-env.d.ts, .next/types/**/*.ts, node_modules, **/*.ts (+22 more)

### Community 8 - "tests_printer_fleet.py"
Cohesion: 0.13
Nodes (7): AsyncIOScheduler, Liga o scheduler conforme o .env. Retorna None quando desabilitado., start_scheduler(), fake_real_collect(), Etapa 5 - orquestracao da frota (printer_fleet.collect_fleet). Roda sobre um…, RecordingThreadPoolExecutor, _OriginalTPE

### Community 9 - "RequireRole.tsx"
Cohesion: 0.23
Nodes (3): ComingSoon(), ComingSoonProps, RequireRole()

### Community 10 - "plugins"
Cohesion: 0.22
Nodes (8): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, typescript, warn

### Community 11 - "HistoryMatrix.tsx"
Cohesion: 0.27
Nodes (5): HistoryPage(), HistoryMatrix(), HistoryMatrixProps, getDepartmentLabel(), getPrinterSite()

### Community 12 - "graphify (knowledge graph tool)"
Cohesion: 0.25
Nodes (8): graphify (knowledge graph tool), graphify explain command, graphify path command, graphify query command, graphify update command, graphify-out/graph.json, graphify-out/GRAPH_REPORT.md, graphify-out/wiki/index.md

### Community 20 - "SNMPResult"
Cohesion: 0.11
Nodes (18): MockSNMPClient, MockSNMPScenarios, Agente SNMP simulado — APENAS PARA TESTE LOCAL. Existe porque a maquina de…, SNMP responde o contador, mas nao expoe a tabela de consumiveis., Monocromatica com toner em 5%., Colorida com ciano critico (18%) e os demais normais., Contador reiniciado (troca de placa/formatador): page_count baixo., Substituto do SNMPClient com a mesma assinatura de collect(). (+10 more)

### Community 21 - "unhandled_exception_handler"
Cohesion: 0.40
Nodes (5): Exception, Erro nao tratado: o detalhe vai para o log do servidor, o cliente recebe apenas…, unhandled_exception_handler(), exception_handler, Request

### Community 22 - "tests_collect_api.py"
Cohesion: 0.67
Nodes (3): check(), main(), Teste ponta a ponta dos endpoints /api/collect com os cenarios simulados.…

### Community 25 - "discovery.py"
Cohesion: 0.27
Nodes (12): _empty_result(), EnrichedDiscoveredPrinter, _is_color(), _is_label(), _normalize_ip(), DiscoveredPrinter, Enriquecimento transitório de filas descobertas com telemetria SNMP., _result_for_ip() (+4 more)

### Community 28 - "printers.py"
Cohesion: 0.12
Nodes (29): create_printer(), create_printer_reading(), get_printer(), get_printer_readings(), list_printers(), list_printers_with_status(), monthly_report(), get (+21 more)

### Community 29 - "cn"
Cohesion: 0.11
Nodes (21): AlertsView(), AlertsDonutCard(), AlertsDonutCardProps, BottomChartsProps, PagesConsumedCard(), TotalPrintsCard(), Login(), MonthlyCounters() (+13 more)

### Community 30 - "collect.py"
Cohesion: 0.13
Nodes (19): collect_fleet(), collect_printer(), CollectRequest, CollectResponse, FleetCollectResponse, get_scheduler_status(), list_scenarios(), BaseModel (+11 more)

### Community 31 - "alert_engine.py"
Cohesion: 0.15
Nodes (18): Alert, notify_alert(), post, Disparo manual do webhook de alerta (Etapa 6) — equivalente ao botao "avisar"…, _active(), evaluate_reading(), Session, Alertas automaticos (Etapa 8A). Roda logo apos cada PrinterReading ser… (+10 more)

### Community 32 - "Relatorio-Mensal.ps1"
Cohesion: 0.33
Nodes (3): Modo Real, Contador mensal calculado por diff de duas leituras SNMP acumulativas (não existe OID de páginas do mês), Scripts PowerShell reais nunca rodaram de verdade (sem interpretador PowerShell no ambiente de dev)

### Community 33 - "app/page.tsx"
Cohesion: 0.21
Nodes (10): AlertBanner(), AlertBannerProps, AlertsViewProps, BottomCharts(), DiscoveryResults(), DiscoveryResultsProps, statusLabel(), NAV_ROUTES (+2 more)

### Community 34 - "routes/auth.py"
Cohesion: 0.15
Nodes (16): login(), post, Session, Config, BaseModel, Usuario exposto pela API. `password_hash` nunca aparece aqui., TokenResponse, UserCreate (+8 more)

### Community 35 - "enrich_discovered_printers"
Cohesion: 0.25
Nodes (7): enrich_discovered_printers(), Enriquece filas em memória; não recebe nem acessa uma sessão SQL., DiscoverySnmpTests, printer(), DiscoveredPrinter, Testes locais do enriquecimento SNMP, sem rede corporativa ou SQLite., result()

### Community 36 - "adaptApi.ts"
Cohesion: 0.15
Nodes (16): adaptAlert(), adaptPrinter(), ApiMonthlyReport, formatLastSeen(), loadMonthlyReportFromApi(), toStatus(), toToner(), VALID_COLORS (+8 more)

### Community 37 - "Settings"
Cohesion: 0.18
Nodes (7): Config, field_validator, Normaliza um DATABASE_URL sqlite relativo (ex.: sqlite:///./x.db) para um…, Impede que um ambiente de producao suba silenciosamente com o secret de…, Settings, BaseSettings, model_validator

### Community 38 - "Topbar"
Cohesion: 0.29
Nodes (5): DashboardPage(), Topbar(), onExportCsv(), handleAlertSelect(), updateFilter()

### Community 39 - "useAppData"
Cohesion: 0.11
Nodes (20): react, AlertsPage(), PrintersPage(), TonerPage(), AppShell(), AuthGate(), Modal(), ModalProps (+12 more)

### Community 40 - "Simular-Ambiente.ps1"
Cohesion: 0.22
Nodes (5): Modo Simulado, public/data/monthly-report.json, public/data/printers.json, Arquivos de dados gerados são ignorados pelo git — gerar/apagar localmente nunca afeta o repositório, Impressoras simuladas usam prefixo SIM_ / departamentos TESTE - de propósito, pra nunca confundir com dado real

### Community 41 - "SNMPClient"
Cohesion: 0.05
Nodes (39): Args: mode: "real" (SNMP de verdade), "mock" (cenario fixo) ou "fleet" (frota…, parse_varbinds(), SNMP Collector para impressoras. Porte direto da funcao Get-TonerSNMP de…, Decodifica um OID BER para notacao pontuada., Decodifica bytes BER como inteiro sem sinal., Extrai a lista de varbinds de uma resposta SNMP. Percorre a estrutura completa…, Cliente SNMP para coleta de impressoras (Printer-MIB, RFC 3805)., Coleta status, contador de paginas e toners de uma impressora. Nunca levanta… (+31 more)

### Community 42 - "TonerMonitoring.tsx"
Cohesion: 0.14
Nodes (17): PrinterDetailsModal(), PrinterTable(), RightPanel(), classify(), FILTERS, SummaryCard(), SummaryCardProps, TONE (+9 more)

### Community 43 - "Printer"
Cohesion: 0.16
Nodes (17): Printer, Etapa 4: identidade e (server, name), NAO ip — o Print Server permite varias…, collect_fleet(), _collect_ip_network(), FleetCollectionResult, _group_by_ip(), _group_plan(), Printer (+9 more)

### Community 45 - "PLANO DE IMPLEMENTAÇÃO — ESCANEAR REDE REAL"
Cohesion: 0.05
Nodes (39): A. Endpoint (implementado), Alertas, Arquitetura atual, Arquitetura do PrinterControl, B. Service reutilizável, Banco, C. Funções Print Server reutilizáveis, Cliente de API (+31 more)

### Community 46 - "servers.py"
Cohesion: 0.10
Nodes (27): discover(), DiscoveredPrinterResponse, DiscoverResponse, get_current_server(), BaseModel, get, post, Session (+19 more)

### Community 47 - "Impressoras"
Cohesion: 0.06
Nodes (35): Alertas, Autenticação, Coleta, Diagnóstico, Escanear Rede (implementado), `GET /`, `GET /api/alerts`, `GET /api/alerts/{alert_id}` (+27 more)

### Community 48 - "Guia de Uso do PrinterControl"
Cohesion: 0.10
Nodes (20): Acessar via web — PARCIAL, Adicionar impressora — AUSENTE/PARCIAL, Alertas — FUNCIONAL na leitura; PARCIAL nas ações, Ações, Como acessar, Configurações — COMING SOON, Configurações, Usuários e Integrações — COMING SOON, Dashboard — FUNCIONAL/PARCIAL (+12 more)

### Community 49 - "database.py"
Cohesion: 0.17
Nodes (16): get_session(), Session, Dependencias compartilhadas pelas rotas. Autorizacao (Fase 1) fica CENTRALIZADA…, Usuario dono do JWT do header Authorization. 401 se ausente/invalido. O usuario…, Fabrica de dependencia: exige que o usuario tenha (ou herde) um dos papeis…, require_roles(), require_user(), health_check() (+8 more)

### Community 50 - "app-data.tsx"
Cohesion: 0.13
Nodes (23): Levantamento_impressões (planilha original), decommissionedPrinters, globalToner, monthlyUsage, printers, discoverPrinters(), AppDataContext, AppDataContextValue (+15 more)

### Community 51 - "tests_fleet.py"
Cohesion: 0.14
Nodes (13): _base_page_count(), _increment(), profile_for(), Simulador de frota — APENAS PARA TESTE LOCAL. Diferenca para snmp_mock.py: la…, Perfil deterministico da impressora: online | offline | snmp_mudo | baixo |…, Contador inicial plausivel para uma impressora que nunca foi lida., Paginas impressas entre duas coletas — fixo por impressora, 5 a 124., Nivel do toner: base do perfil + desvio deterministico por impressora/cor,… (+5 more)

### Community 52 - "toast.tsx"
Cohesion: 0.11
Nodes (17): ReportsPage(), DecommissionedList(), DecommissionedListProps, DepartmentBreakdown(), DepartmentBreakdownProps, MONTHS, DecommissionedPrinter, DepartmentUsage (+9 more)

### Community 53 - "Guia do Desenvolvedor"
Cohesion: 0.13
Nodes (14): Backend, Banco, Comandos do frontend, Escanear Rede (implementado), Guia do Desenvolvedor, O que não executar em produção sem autorização, Print Server, Riscos conhecidos (+6 more)

### Community 54 - "layout.tsx"
Cohesion: 0.29
Nodes (5): ibmPlexMono, metadata, publicSans, sourceSerif, Providers()

### Community 55 - "Role"
Cohesion: 0.16
Nodes (15): create_db_and_tables(), _migrate_alert_type(), _migrate_reading_uptime(), _migrate_user_rbac(), Adiciona alerts.alert_type em bancos criados antes da Etapa 8A., Etapa 7: adiciona printer_readings.uptime em bancos criados antes desta etapa.…, Fase 1 (RBAC): adiciona users.role e users.is_active em bancos criados antes…, RBAC minimo (Fase 1). Tres papeis cobrem todas as rotas existentes hoje: -… (+7 more)

### Community 56 - "types.ts"
Cohesion: 0.17
Nodes (18): PrinterDetailsModalProps, PrinterRanking(), PrinterRankingProps, RankedPrinter, RankList(), rankPrinters(), config, PrinterStatusBadge() (+10 more)

### Community 57 - "tests_webhook.py"
Cohesion: 0.25
Nodes (10): Alert, SQLModel, TonerHistory, PrinterMonthly, PrinterReading, SQLModel, make_offline_reading(), make_reading() (+2 more)

### Community 58 - "auth.ts"
Cohesion: 0.23
Nodes (15): handleSubmit(), clearToken(), getToken(), isTokenPersistent(), setToken(), ApiUser, cacheAccount(), fetchCurrentUser() (+7 more)

### Community 59 - "User"
Cohesion: 0.25
Nodes (12): SQLModel, True se o papel do usuario satisfaz qualquer um dos exigidos., User, check(), check_true(), h(), _hash_de(), main() (+4 more)

### Community 60 - "update_user"
Cohesion: 0.16
Nodes (13): _active_admin_count(), _ensure_not_last_admin(), list_users(), get, patch, Session, Altera nome, papel, ativacao e/ou senha de uma conta. Desativar aqui basta para…, Impede que a ultima conta admin ativa perca o proprio acesso administrativo.… (+5 more)

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

### Community 65 - "api.ts"
Cohesion: 0.14
Nodes (11): API_BASE_URL, ApiDiscoveredPrinter, ApiDiscoveredToner, ApiDiscoveryResponse, ApiPrinterReading, apiRequest(), describeDetail(), PrinterInput (+3 more)

### Community 66 - "resolve_alert"
Cohesion: 0.29
Nodes (8): get_alert(), list_alerts(), get, patch, Session, Resolve um alerta. Ate a Fase 1 esta rota estava SEM protecao alguma — qualquer…, resolved=false (padrao) -> ativos | true -> resolvidos | omitido como null ->…, resolve_alert()

### Community 68 - "tests_printer_sync.py"
Cohesion: 0.18
Nodes (12): obter_modelo(), obter_tipo_impressora(), Regras de classificacao portadas do Main.ps1 (Etapa 4). Correspondencia exata:…, Traduz DriverName (Windows) em nome comercial, igual ao Main.ps1., Classifica A4 / Etiqueta / Portatil a partir de Nome+Modelo, igual ao Main.ps1., Session, Sincronizacao Print Server -> banco (Etapa 4). Print Server ->…, Executa um ciclo completo de sincronizacao para um Print Server. Levanta… (+4 more)

### Community 69 - "_migrate_printer_schema"
Cohesion: 0.29
Nodes (7): _finish_printer_migration(), _migrate_printer_schema(), Caminho do arquivo .db atual, se o banco for SQLite em disco (nao :memory:)., Etapa 4 — reconstroi `printers` para trocar a identidade de `ip UNIQUE` para…, Recria `printers` (schema atual) e copia `printers_old` para dentro dela, numa…, _sqlite_backup_path(), Path

### Community 70 - "read_current_user"
Cohesion: 0.67
Nodes (3): get, Conta autenticada e seu papel — usado para decidir o que exibir/permitir., read_current_user()

## Knowledge Gaps
- **251 isolated node(s):** `$schema`, `typescript`, `oxc`, `react/rules-of-hooks`, `warn` (+246 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `resolve_alert`, `routes/auth.py`, `read_current_user`, `Printer`, `servers.py`, `update_user`, `database.py`, `Role`, `tests_webhook.py`, `printers.py`, `tests_rbac.py`, `collect.py`, `alert_engine.py`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Why does `SNMPClient` connect `SNMPClient` to `enrich_discovered_printers`, `PrinterCollector`, `tests_printer_fleet.py`, `Printer`, `discovery.py`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Why does `Printer` connect `Printer` to `PrinterCollector`, `_migrate_printer_schema`, `tests_printer_sync.py`, `tests_printer_fleet.py`, `database.py`, `tests_fleet.py`, `Role`, `tests_webhook.py`, `printers.py`, `tests_rbac.py`, `collect.py`, `alert_engine.py`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Are the 24 inferred relationships involving `User` (e.g. with `require_roles()` and `require_user()`) actually correct?**
  _`User` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `Printer` (e.g. with `_finish_printer_migration()` and `notify_alert()`) actually correct?**
  _`Printer` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `SNMPClient` (e.g. with `PrinterCollector` and `FakeAgent`) actually correct?**
  _`SNMPClient` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `SNMPResult` (e.g. with `enrich_discovered_printers()` and `PrinterCollector`) actually correct?**
  _`SNMPResult` has 6 INFERRED edges - model-reasoned connections that need verification._