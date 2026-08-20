# Graph Report - PrinterControl  (2026-08-19)

## Corpus Check
- 106 files · ~55,203 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 770 nodes · 1533 edges · 47 communities (38 shown, 9 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 60 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `df944eb9`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- snmp_fleet_mock.py
- package.json
- Main.ps1
- Elgin Impressoras (painel de monitoramento)
- .collect_and_save
- Coletar-Impressoras.ps1
- compilerOptions
- main.py
- useAppData
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
- SNMPResult
- Alert
- tests_collect_api.py
- schemas/printer.py
- useTheme
- collect.py
- PrinterCollector
- app-data.tsx
- PrinterTable
- routes/auth.py
- TonerMonitoring.tsx
- printers.py
- User
- SNMPClient
- cn
- servers.py
- MockSNMPClient
- unhandled_exception_handler
- types.ts
- Printer
- layout.tsx
- tests_printers_crud.py

## God Nodes (most connected - your core abstractions)
1. `SNMPClient` - 32 edges
2. `cn()` - 31 edges
3. `Printer` - 26 edges
4. `PrinterCollector` - 24 edges
5. `SNMPResult` - 23 edges
6. `useAppData()` - 21 edges
7. `Printer` - 20 edges
8. `Elgin Impressoras (painel de monitoramento)` - 20 edges
9. `User` - 19 edges
10. `compilerOptions` - 19 edges

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

## Communities (47 total, 9 thin omitted)

### Community 0 - "snmp_fleet_mock.py"
Cohesion: 0.18
Nodes (12): _base_page_count(), FleetMockClient, _increment(), profile_for(), Simulador de frota — APENAS PARA TESTE LOCAL. Diferenca para snmp_mock.py: la…, Perfil deterministico da impressora: online | offline | snmp_mudo | baixo |…, Contador inicial plausivel para uma impressora que nunca foi lida., Paginas impressas entre duas coletas — fixo por impressora, 5 a 124. (+4 more)

### Community 1 - "package.json"
Cohesion: 0.06
Nodes (31): lucide-react, next, oxlint, dependencies, lucide-react, next, react, react-dom (+23 more)

### Community 2 - "Main.ps1"
Cohesion: 0.13
Nodes (29): Atualizar-ImpressorasAsync(), Build-ListaExibicaoAgrupada(), Build-SnmpGet(), Build-SnmpGetBulk(), Convert-SnmpValueBytes(), Get-ImpressorasEmpresa(), Get-TonerSNMP(), Import-Tabela() (+21 more)

### Community 3 - "Elgin Impressoras (painel de monitoramento)"
Cohesion: 0.05
Nodes (40): Tela Alertas, Tela Dashboard, Elgin Impressoras (painel de monitoramento), Tela Histórico, Tela Impressoras, Levantamento_impressões (planilha original), Tela Login, Migração futura para FastAPI (Python) + Next.js + banco de dados (+32 more)

### Community 4 - ".collect_and_save"
Cohesion: 0.22
Nodes (6): Session, Converte SNMPResult em PrinterReading. Toner ausente vira NULL (a coluna e…, Deduz se a impressora e colorida a partir do modelo/nome (regra do PS1)., Etiquetadora/portatil: sem Printer-MIB, o PS1 nem consulta SNMP., Coleta uma impressora e persiste a leitura. Args: printer_id: id da impressora…, Printer

### Community 5 - "Coletar-Impressoras.ps1"
Cohesion: 0.09
Nodes (21): Modo Real, Contador mensal calculado por diff de duas leituras SNMP acumulativas (não existe OID de páginas do mês), Scripts PowerShell reais nunca rodaram de verdade (sem interpretador PowerShell no ambiente de dev), public/data/monthly-report.json, public/data/printers.json, Arquivos de dados gerados são ignorados pelo git — gerar/apagar localmente nunca afeta o repositório, Build-SnmpGet(), Build-SnmpGetBulk() (+13 more)

### Community 6 - "compilerOptions"
Cohesion: 0.06
Nodes (30): dom, dom.iterable, esnext, .next/dev/types/**/*.ts, next-env.d.ts, .next/types/**/*.ts, node_modules, **/*.ts (+22 more)

### Community 7 - "main.py"
Cohesion: 0.17
Nodes (15): AsyncIOScheduler, create_db_and_tables(), _migrate_alert_type(), Adiciona alerts.alert_type em bancos criados antes da Etapa 8A., health_check(), lifespan(), get, read_root() (+7 more)

### Community 8 - "useAppData"
Cohesion: 0.11
Nodes (23): react, ReportsPage(), AppShell(), AuthGate(), DepartmentBreakdown(), DepartmentBreakdownProps, MONTHS, Modal() (+15 more)

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
Cohesion: 0.13
Nodes (15): MockSNMPScenarios, Agente SNMP simulado — APENAS PARA TESTE LOCAL. Existe porque a maquina de…, SNMP responde o contador, mas nao expoe a tabela de consumiveis., Monocromatica com toner em 5%., Colorida com ciano critico (18%) e os demais normais., Contador reiniciado (troca de placa/formatador): page_count baixo., Cenarios de teste. Cada metodo devolve um SNMPResult completo., Monocromatica saudavel. (+7 more)

### Community 21 - "Alert"
Cohesion: 0.18
Nodes (18): Alert, Alert, SQLModel, TonerHistory, get_alert(), list_alerts(), get, patch (+10 more)

### Community 22 - "tests_collect_api.py"
Cohesion: 0.67
Nodes (3): check(), main(), Teste ponta a ponta dos endpoints /api/collect com os cenarios simulados.…

### Community 28 - "schemas/printer.py"
Cohesion: 0.19
Nodes (14): Config, PrinterCreate, PrinterReadingCreate, PrinterReadingResponse, PrinterResponse, PrinterUpdate, PrinterWithStatus, BaseModel (+6 more)

### Community 29 - "useTheme"
Cohesion: 0.22
Nodes (11): AlertsDonutCard(), AlertsDonutCardProps, PagesConsumedCard(), Sidebar(), getChartColors(), getInitialTheme(), Theme, ThemeContext (+3 more)

### Community 30 - "collect.py"
Cohesion: 0.18
Nodes (16): collect_fleet(), collect_printer(), CollectRequest, CollectResponse, FleetCollectResponse, get_scheduler_status(), BaseModel, get (+8 more)

### Community 31 - "PrinterCollector"
Cohesion: 0.16
Nodes (10): PrinterCollector, Orquestrador da coleta de impressoras. Separa as tres responsabilidades da…, Coleta uma impressora e grava o resultado como PrinterReading., active(), collect(), Etapa 8A - validacao dos alertas automaticos. Usa banco SQLite temporario e o…, resolved(), collect_fleet() (+2 more)

### Community 32 - "app-data.tsx"
Cohesion: 0.06
Nodes (51): ACTIVE_NODES, features, Login(), handleSubmit(), LoginProps, NETWORK_LINKS, NETWORK_NODES, decommissionedPrinters (+43 more)

### Community 34 - "routes/auth.py"
Cohesion: 0.28
Nodes (13): login(), post, Session, register(), Config, BaseModel, TokenResponse, UserCreate (+5 more)

### Community 35 - "TonerMonitoring.tsx"
Cohesion: 0.13
Nodes (18): TonerPage(), PrinterDetailsModal(), RightPanel(), RightPanelProps, classify(), FILTERS, SummaryCard(), SummaryCardProps (+10 more)

### Community 38 - "printers.py"
Cohesion: 0.24
Nodes (18): Printer, PrinterMonthly, PrinterReading, SQLModel, create_printer(), create_printer_reading(), get_printer(), get_printer_readings() (+10 more)

### Community 39 - "User"
Cohesion: 0.23
Nodes (11): get_session(), Session, Dependencias compartilhadas pelas rotas. Autenticacao: `require_user` protege…, Usuario dono do JWT do header Authorization. 401 se ausente/invalido., require_user(), SQLModel, User, decode_token() (+3 more)

### Community 41 - "SNMPClient"
Cohesion: 0.05
Nodes (38): parse_varbinds(), SNMP Collector para impressoras. Porte direto da funcao Get-TonerSNMP de…, Decodifica um OID BER para notacao pontuada., Decodifica bytes BER como inteiro sem sinal., Extrai a lista de varbinds de uma resposta SNMP. Percorre a estrutura completa…, Cliente SNMP para coleta de impressoras (Printer-MIB, RFC 3805)., Coleta status, contador de paginas e toners de uma impressora. Nunca levanta…, PS1: `if ($ip -match '^\\d')` — descarta 'N/A' e nomes de porta. (+30 more)

### Community 42 - "cn"
Cohesion: 0.16
Nodes (13): DashboardPage(), BottomCharts(), TotalPrintsCard(), config, PrinterStatusBadge(), StatCard(), StatCardProps, StatCards() (+5 more)

### Community 46 - "servers.py"
Cohesion: 0.08
Nodes (31): Config, field_validator, Normaliza um DATABASE_URL sqlite relativo (ex.: sqlite:///./x.db) para um…, Settings, discover(), DiscoveredPrinterResponse, DiscoverResponse, get_current_server() (+23 more)

### Community 48 - "MockSNMPClient"
Cohesion: 0.17
Nodes (7): list_scenarios(), Cenarios simulados disponiveis e se o modo mock esta habilitado., Cenarios de teste disponiveis (fonte unica: snmp_mock.SCENARIOS)., Args: mode: "real" (SNMP de verdade), "mock" (cenario fixo) ou "fleet" (frota…, MockSNMPClient, Substituto do SNMPClient com a mesma assinatura de collect()., Devolve o resultado fixo do cenario (ip e is_color sao ignorados).

### Community 49 - "unhandled_exception_handler"
Cohesion: 0.40
Nodes (5): Exception, Erro nao tratado: o detalhe vai para o log do servidor, o cliente recebe apenas…, unhandled_exception_handler(), exception_handler, Request

### Community 50 - "types.ts"
Cohesion: 0.18
Nodes (12): AlertsPage(), AlertBanner(), AlertBannerProps, AlertsView(), AlertsViewProps, BottomChartsProps, MonthlyCounters(), MonthlyCountersProps (+4 more)

### Community 51 - "Printer"
Cohesion: 0.20
Nodes (15): PrinterDetailsModalProps, PrinterRanking(), PrinterRankingProps, RankedPrinter, RankList(), rankPrinters(), PAGE_SIZE_OPTIONS, PrinterTableProps (+7 more)

### Community 54 - "layout.tsx"
Cohesion: 0.29
Nodes (5): ibmPlexMono, metadata, publicSans, sourceSerif, Providers()

### Community 55 - "tests_printers_crud.py"
Cohesion: 0.33
Nodes (3): Etapa 12 - CRUD de impressoras contra o servidor rodando. Usa o banco REAL,…, Devolve (status, payload)., request()

## Knowledge Gaps
- **130 isolated node(s):** `$schema`, `typescript`, `oxc`, `react/rules-of-hooks`, `warn` (+125 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SNMPClient` connect `SNMPClient` to `MockSNMPClient`, `.collect_and_save`, `PrinterCollector`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Why does `PrinterCollector` connect `PrinterCollector` to `snmp_fleet_mock.py`, `.collect_and_save`, `printers.py`, `main.py`, `SNMPClient`, `MockSNMPClient`, `SNMPResult`, `collect.py`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Why does `SNMPResult` connect `SNMPResult` to `snmp_fleet_mock.py`, `.collect_and_save`, `SNMPClient`, `MockSNMPClient`, `PrinterCollector`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `SNMPClient` (e.g. with `PrinterCollector` and `FakeAgent`) actually correct?**
  _`SNMPClient` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `PrinterCollector` (e.g. with `collect_fleet()` and `collect_printer()`) actually correct?**
  _`PrinterCollector` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `SNMPResult` (e.g. with `PrinterCollector` and `FleetMockClient`) actually correct?**
  _`SNMPResult` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `typescript`, `oxc` to the rest of the system?**
  _130 weakly-connected nodes found - possible documentation gaps or missing edges._