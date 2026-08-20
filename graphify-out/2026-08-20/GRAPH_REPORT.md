# Graph Report - PrinterControl  (2026-08-20)

## Corpus Check
- 114 files · ~62,760 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 857 nodes · 1699 edges · 61 communities (50 shown, 11 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 76 edges (avg confidence: 0.56)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7d7b2c31`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- snmp_fleet_mock.py
- package.json
- Main.ps1
- Elgin Impressoras (painel de monitoramento)
- printer_fleet.py
- Coletar-Impressoras.ps1
- compilerOptions
- database.py
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
- PrinterCollector
- tests_collect_api.py
- printers.py
- Sidebar.tsx
- collect_fleet
- Printer
- adaptApi.ts
- app-data.tsx
- routes/auth.py
- TonerMonitoring.tsx
- api.ts
- Settings
- app/page.tsx
- useAppData
- Simular-Ambiente.ps1
- SNMPClient
- cn
- .collect_and_save
- types.ts
- Relatorio-Mensal.ps1
- servers.py
- notify_alert
- MockSNMPClient
- unhandled_exception_handler
- AlertsView.tsx
- Printer
- printers.ts
- webhook_notifier.py
- theme.tsx
- tests_printers_crud.py
- filterPrinters.ts
- ElginLogo.tsx
- Alert
- Printer

## God Nodes (most connected - your core abstractions)
1. `Printer` - 42 edges
2. `SNMPClient` - 31 edges
3. `cn()` - 31 edges
4. `Printer` - 25 edges
5. `PrinterCollector` - 24 edges
6. `PrinterReading` - 22 edges
7. `useAppData()` - 21 edges
8. `Elgin Impressoras (painel de monitoramento)` - 20 edges
9. `compilerOptions` - 19 edges
10. `Alert` - 18 edges

## Surprising Connections (you probably didn't know these)
- `require_user()` --calls--> `decode_token()`  [INFERRED]
  backend/app/dependencies.py → backend/app/services/auth.py
- `Lucide` --conceptually_related_to--> `Elgin Impressoras (painel de monitoramento)`  [EXTRACTED]
  README.md → CONTEXTO-DESENVOLVIMENTO.md
- `React` --conceptually_related_to--> `Elgin Impressoras (painel de monitoramento)`  [EXTRACTED]
  README.md → CONTEXTO-DESENVOLVIMENTO.md
- `Recharts` --conceptually_related_to--> `Elgin Impressoras (painel de monitoramento)`  [EXTRACTED]
  README.md → CONTEXTO-DESENVOLVIMENTO.md
- `Tailwind CSS v4` --conceptually_related_to--> `Elgin Impressoras (painel de monitoramento)`  [EXTRACTED]
  README.md → CONTEXTO-DESENVOLVIMENTO.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Comandos do CLI graphify (query/path/explain/update)** — claude_graphify, claude_graphify_query, claude_graphify_path, claude_graphify_explain, claude_graphify_update [EXTRACTED 1.00]
- **Stack tecnológico do painel (Vite/React/TS/Tailwind/Recharts/Lucide)** — readme_vite, readme_react, readme_typescript, readme_tailwind_css_v4, readme_recharts, readme_lucide [EXTRACTED 1.00]
- **Arquitetura de dados de 3 modos (Demo/Real/Simulado)** — contexto_desenvolvimento_elgin_impressoras, contexto_desenvolvimento_modo_demo, contexto_desenvolvimento_modo_real, contexto_desenvolvimento_modo_simulado [EXTRACTED 1.00]

## Communities (61 total, 11 thin omitted)

### Community 0 - "snmp_fleet_mock.py"
Cohesion: 0.15
Nodes (14): _base_page_count(), FleetMockClient, _increment(), profile_for(), SNMPResult, TonerInfo, Simulador de frota — APENAS PARA TESTE LOCAL. Diferenca para snmp_mock.py: la…, Perfil deterministico da impressora: online | offline | snmp_mudo | baixo |… (+6 more)

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
Cohesion: 0.10
Nodes (16): AsyncIOScheduler, collect_fleet(), FleetCollectionResult, _group_by_ip(), Session, Orquestracao da coleta da frota inteira (Etapa 5). Separacao de…, Um ciclo completo de coleta sobre toda a frota ATIVA (active=True). Nunca chama…, Coleta agendada (Etapa 7; frota inteira desde a Etapa 5). APScheduler roda… (+8 more)

### Community 5 - "Coletar-Impressoras.ps1"
Cohesion: 0.21
Nodes (13): Build-SnmpGet(), Build-SnmpGetBulk(), Convert-SnmpValueBytes(), Get-ImpressorasServidor(), Get-TonerSNMP(), Parse-SnmpBulkResponse(), Parse-SnmpCounter(), Parse-SnmpInt() (+5 more)

### Community 6 - "compilerOptions"
Cohesion: 0.06
Nodes (30): dom, dom.iterable, esnext, .next/dev/types/**/*.ts, next-env.d.ts, .next/types/**/*.ts, node_modules, **/*.ts (+22 more)

### Community 7 - "database.py"
Cohesion: 0.12
Nodes (25): create_db_and_tables(), _finish_printer_migration(), get_session(), _migrate_alert_type(), _migrate_printer_schema(), _migrate_reading_uptime(), Recria `printers` (schema atual) e copia `printers_old` para dentro dela, numa…, Adiciona alerts.alert_type em bancos criados antes da Etapa 8A. (+17 more)

### Community 8 - "toast.tsx"
Cohesion: 0.10
Nodes (16): react, ibmPlexMono, metadata, publicSans, sourceSerif, Providers(), AuthGate(), Modal() (+8 more)

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

### Community 21 - "PrinterCollector"
Cohesion: 0.17
Nodes (12): Alert, SQLModel, TonerHistory, PrinterCollector, Coleta uma impressora e grava o resultado como PrinterReading., active(), collect(), Etapa 8A - validacao dos alertas automaticos. Usa banco SQLite temporario e o… (+4 more)

### Community 22 - "tests_collect_api.py"
Cohesion: 0.67
Nodes (3): check(), main(), Teste ponta a ponta dos endpoints /api/collect com os cenarios simulados.…

### Community 28 - "printers.py"
Cohesion: 0.12
Nodes (30): create_printer(), create_printer_reading(), get_printer(), get_printer_readings(), list_printers(), list_printers_with_status(), monthly_report(), get (+22 more)

### Community 29 - "Sidebar.tsx"
Cohesion: 0.17
Nodes (15): AlertsDonutCard(), AlertsDonutCardProps, PagesConsumedCard(), TotalPrintsCard(), NavItem(), NavItemProps, Sidebar(), SidebarProps (+7 more)

### Community 30 - "collect_fleet"
Cohesion: 0.25
Nodes (11): collect_fleet(), collect_printer(), CollectRequest, CollectResponse, FleetCollectResponse, BaseModel, post, Session (+3 more)

### Community 31 - "Printer"
Cohesion: 0.17
Nodes (17): Printer, PrinterMonthly, PrinterReading, SQLModel, Etapa 4: identidade e (server, name), NAO ip — o Print Server permite varias…, _active(), evaluate_reading(), Session (+9 more)

### Community 32 - "adaptApi.ts"
Cohesion: 0.19
Nodes (12): RightPanelProps, adaptPrinter(), ApiMonthlyReport, formatLastSeen(), toStatus(), toToner(), VALID_COLORS, VALID_STATUS (+4 more)

### Community 33 - "app-data.tsx"
Cohesion: 0.21
Nodes (13): adaptAlert(), loadMonthlyReportFromApi(), fetchPrintersWithStatus(), AppDataContext, AppDataProvider(), handleScan(), loadFromApi(), deriveAlerts() (+5 more)

### Community 34 - "routes/auth.py"
Cohesion: 0.17
Nodes (18): SQLModel, User, login(), post, Session, register(), Config, BaseModel (+10 more)

### Community 35 - "TonerMonitoring.tsx"
Cohesion: 0.22
Nodes (9): TonerPage(), classify(), FILTERS, SummaryCard(), SummaryCardProps, TONE, TonerClass, TonerMonitoring() (+1 more)

### Community 36 - "api.ts"
Cohesion: 0.09
Nodes (25): ACTIVE_NODES, features, Login(), handleSubmit(), LoginProps, NETWORK_LINKS, NETWORK_NODES, api (+17 more)

### Community 37 - "Settings"
Cohesion: 0.25
Nodes (6): Config, field_validator, Normaliza um DATABASE_URL sqlite relativo (ex.: sqlite:///./x.db) para um…, Settings, BaseSettings, Path

### Community 38 - "app/page.tsx"
Cohesion: 0.14
Nodes (10): BottomCharts(), PrinterTable(), RightPanel(), StatCard(), StatCardProps, StatCards(), StatCardsProps, TONE (+2 more)

### Community 39 - "useAppData"
Cohesion: 0.23
Nodes (11): DashboardPage(), PrintersPage(), ReportsPage(), AppShell(), Topbar(), onExportCsv(), handleAlertSelect(), updateFilter() (+3 more)

### Community 40 - "Simular-Ambiente.ps1"
Cohesion: 0.22
Nodes (5): Modo Simulado, public/data/monthly-report.json, public/data/printers.json, Arquivos de dados gerados são ignorados pelo git — gerar/apagar localmente nunca afeta o repositório, Impressoras simuladas usam prefixo SIM_ / departamentos TESTE - de propósito, pra nunca confundir com dado real

### Community 41 - "SNMPClient"
Cohesion: 0.05
Nodes (40): parse_varbinds(), SNMP Collector para impressoras. Porte direto da funcao Get-TonerSNMP de…, Decodifica um OID BER para notacao pontuada., Decodifica bytes BER como inteiro sem sinal., Extrai a lista de varbinds de uma resposta SNMP. Percorre a estrutura completa…, Cliente SNMP para coleta de impressoras (Printer-MIB, RFC 3805)., Coleta status, contador de paginas e toners de uma impressora. Nunca levanta…, PS1: `if ($ip -match '^\\d')` — descarta 'N/A' e nomes de porta. (+32 more)

### Community 42 - "cn"
Cohesion: 0.22
Nodes (11): PrinterDetailsModal(), config, PrinterStatusBadge(), PAGE_SIZE_OPTIONS, PrinterTableProps, cn(), PrinterFilters, CHANNEL_COLOR_DARK (+3 more)

### Community 43 - ".collect_and_save"
Cohesion: 0.15
Nodes (11): Session, SNMPResult, Converte SNMPResult em PrinterReading. Toner ausente vira NULL (a coluna e…, Deduz se a impressora e colorida a partir do modelo/nome (regra do PS1)., Etiquetadora/portatil: sem Printer-MIB, o PS1 nem consulta SNMP., Coleta uma impressora e persiste a leitura. Args: printer_id: id da impressora…, _collect_ip_network(), _group_plan() (+3 more)

### Community 44 - "types.ts"
Cohesion: 0.22
Nodes (10): AlertBanner(), AlertBannerProps, AlertsViewProps, BottomChartsProps, MonthlyCounters(), MonthlyCountersProps, Alert, MonthlyPageCount (+2 more)

### Community 45 - "Relatorio-Mensal.ps1"
Cohesion: 0.33
Nodes (3): Modo Real, Contador mensal calculado por diff de duas leituras SNMP acumulativas (não existe OID de páginas do mês), Scripts PowerShell reais nunca rodaram de verdade (sem interpretador PowerShell no ambiente de dev)

### Community 46 - "servers.py"
Cohesion: 0.07
Nodes (43): discover(), DiscoveredPrinterResponse, DiscoverResponse, get_current_server(), BaseModel, get, post, Session (+35 more)

### Community 47 - "notify_alert"
Cohesion: 0.20
Nodes (11): get_alert(), list_alerts(), notify_alert(), get, patch, post, Session, User (+3 more)

### Community 48 - "MockSNMPClient"
Cohesion: 0.12
Nodes (12): get_scheduler_status(), list_scenarios(), get, Cenarios simulados disponiveis e se o modo mock esta habilitado., Estado da coleta agendada (APScheduler)., Cenarios de teste disponiveis (fonte unica: snmp_mock.SCENARIOS)., Args: mode: "real" (SNMP de verdade), "mock" (cenario fixo) ou "fleet" (frota…, Estado atual, para o endpoint de diagnostico. (+4 more)

### Community 49 - "unhandled_exception_handler"
Cohesion: 0.40
Nodes (5): Exception, Erro nao tratado: o detalhe vai para o log do servidor, o cliente recebe apenas…, unhandled_exception_handler(), exception_handler, Request

### Community 51 - "Printer"
Cohesion: 0.21
Nodes (10): PrinterDetailsModalProps, PrinterRanking(), PrinterRankingProps, RankedPrinter, RankList(), rankPrinters(), STATUS_LABEL, isValidPrinter() (+2 more)

### Community 52 - "printers.ts"
Cohesion: 0.18
Nodes (12): Levantamento_impressões (planilha original), DecommissionedList(), DecommissionedListProps, DepartmentBreakdown(), DepartmentBreakdownProps, MONTHS, DecommissionedPrinter, decommissionedPrinters (+4 more)

### Community 53 - "webhook_notifier.py"
Cohesion: 0.32
Nodes (7): _build_adaptive_card(), Notificacao de alerta critico via webhook (Etapa 6). Equivalente a Send-…, Envia o Adaptive Card ao webhook configurado. Nunca levanta excecao — retorna…, Host da URL, para logar sem expor path/assinatura., Mesmo corpo de Send-AlertaWebhook (Main.ps1:1319): titulo/cor conforme manual…, _safe_host(), send_toner_alert_webhook()

### Community 54 - "theme.tsx"
Cohesion: 0.33
Nodes (5): getInitialTheme(), Theme, ThemeContext, ThemeContextValue, ThemeProvider()

### Community 55 - "tests_printers_crud.py"
Cohesion: 0.33
Nodes (3): Etapa 12 - CRUD de impressoras contra o servidor rodando. Usa o banco REAL,…, Devolve (status, payload)., request()

### Community 56 - "filterPrinters.ts"
Cohesion: 0.53
Nodes (4): DEFAULT_FILTERS, filterPrinters(), getPrinterType(), PrinterType

### Community 57 - "ElginLogo.tsx"
Cohesion: 0.40
Nodes (4): Logo Elgin é redesenho à mão (IA sem acesso a imagens coladas no chat, só uploads), src/components/ (padrão com header-comment por arquivo), ElginLogo(), ElginLogoProps

## Knowledge Gaps
- **130 isolated node(s):** `Config`, `Config`, `features`, `NETWORK_NODES`, `NETWORK_LINKS` (+125 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SNMPClient` connect `SNMPClient` to `MockSNMPClient`, `.collect_and_save`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Why does `Printer` connect `Printer` to `routes/auth.py`, `printer_fleet.py`, `database.py`, `.collect_and_save`, `servers.py`, `notify_alert`, `MockSNMPClient`, `PrinterCollector`, `printers.py`, `collect_fleet`?**
  _High betweenness centrality (0.069) - this node is a cross-community bridge._
- **Why does `_collect_ip_network()` connect `.collect_and_save` to `snmp_fleet_mock.py`, `printer_fleet.py`, `SNMPClient`, `MockSNMPClient`, `Printer`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Are the 18 inferred relationships involving `Printer` (e.g. with `_finish_printer_migration()` and `notify_alert()`) actually correct?**
  _`Printer` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `SNMPClient` (e.g. with `.collect_and_save()` and `.__init__()`) actually correct?**
  _`SNMPClient` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `PrinterCollector` (e.g. with `collect_fleet()` and `collect_printer()`) actually correct?**
  _`PrinterCollector` has 9 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Config`, `Config`, `features` to the rest of the system?**
  _130 weakly-connected nodes found - possible documentation gaps or missing edges._