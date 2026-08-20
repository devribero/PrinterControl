# Graph Report - PrinterControl  (2026-08-19)

## Corpus Check
- 109 files · ~57,817 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 800 nodes · 1601 edges · 56 communities (47 shown, 9 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 64 edges (avg confidence: 0.53)
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
- FakeAgent
- Coletar-Impressoras.ps1
- compilerOptions
- main.py
- PrinterDetailsModal.tsx
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
- PrinterCollector
- tests_collect_api.py
- Printer
- Sidebar.tsx
- collect.py
- SNMPClient
- api.ts
- app-data.tsx
- routes/auth.py
- TonerMonitoring.tsx
- Login.tsx
- database.py
- app/page.tsx
- dependencies.py
- Simular-Ambiente.ps1
- snmp.py
- cn
- auth.ts
- AppDataProvider
- Relatorio-Mensal.ps1
- servers.py
- get_scheduler_status
- printer_collector.py
- unhandled_exception_handler
- useAppData
- types.ts
- DecommissionedList.tsx
- fetchPrinters.ts
- theme.tsx
- tests_printers_crud.py

## God Nodes (most connected - your core abstractions)
1. `SNMPClient` - 32 edges
2. `cn()` - 31 edges
3. `Printer` - 26 edges
4. `Printer` - 26 edges
5. `PrinterCollector` - 24 edges
6. `SNMPResult` - 23 edges
7. `useAppData()` - 21 edges
8. `User` - 20 edges
9. `Elgin Impressoras (painel de monitoramento)` - 20 edges
10. `compilerOptions` - 19 edges

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

## Communities (56 total, 9 thin omitted)

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
Cohesion: 0.10
Nodes (21): Tela Alertas, Tela Dashboard, Elgin Impressoras (painel de monitoramento), Tela Histórico, Tela Impressoras, Tela Login, Migração futura para FastAPI (Python) + Next.js + banco de dados, Modo claro/escuro (toggle) (+13 more)

### Community 4 - "FakeAgent"
Cohesion: 0.12
Nodes (12): Decodifica um OID BER para notacao pontuada., Le um TLV BER. Retorna (tag, length, value_start, next_pos)., _read_oid(), _read_tlv(), check(), FakeAgent, LocalSNMPClient, main() (+4 more)

### Community 5 - "Coletar-Impressoras.ps1"
Cohesion: 0.21
Nodes (13): Build-SnmpGet(), Build-SnmpGetBulk(), Convert-SnmpValueBytes(), Get-ImpressorasServidor(), Get-TonerSNMP(), Parse-SnmpBulkResponse(), Parse-SnmpCounter(), Parse-SnmpInt() (+5 more)

### Community 6 - "compilerOptions"
Cohesion: 0.06
Nodes (30): dom, dom.iterable, esnext, .next/dev/types/**/*.ts, next-env.d.ts, .next/types/**/*.ts, node_modules, **/*.ts (+22 more)

### Community 7 - "main.py"
Cohesion: 0.20
Nodes (12): AsyncIOScheduler, health_check(), lifespan(), get, read_root(), Coleta agendada (Etapa 7). APScheduler roda dentro do proprio processo do…, Um ciclo de coleta: percorre as impressoras configuradas e grava as leituras., Liga o scheduler conforme o .env. Retorna None quando desabilitado. (+4 more)

### Community 8 - "PrinterDetailsModal.tsx"
Cohesion: 0.10
Nodes (22): react, ReportsPage(), AppShell(), DepartmentBreakdown(), DepartmentBreakdownProps, MONTHS, Modal(), ModalProps (+14 more)

### Community 10 - "plugins"
Cohesion: 0.22
Nodes (8): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, typescript, warn

### Community 11 - "HistoryMatrix.tsx"
Cohesion: 0.33
Nodes (4): HistoryMatrix(), HistoryMatrixProps, getDepartmentLabel(), getPrinterSite()

### Community 12 - "graphify (knowledge graph tool)"
Cohesion: 0.25
Nodes (8): graphify (knowledge graph tool), graphify explain command, graphify path command, graphify query command, graphify update command, graphify-out/graph.json, graphify-out/GRAPH_REPORT.md, graphify-out/wiki/index.md

### Community 20 - "SNMPResult"
Cohesion: 0.14
Nodes (14): MockSNMPScenarios, SNMP responde o contador, mas nao expoe a tabela de consumiveis., Monocromatica com toner em 5%., Colorida com ciano critico (18%) e os demais normais., Contador reiniciado (troca de placa/formatador): page_count baixo., Cenarios de teste. Cada metodo devolve um SNMPResult completo., Monocromatica saudavel., Colorida saudavel (4 toners, ordem C, M, Y, K). (+6 more)

### Community 21 - "PrinterCollector"
Cohesion: 0.07
Nodes (39): Alert, Alert, SQLModel, TonerHistory, PrinterMonthly, PrinterReading, SQLModel, get_alert() (+31 more)

### Community 22 - "tests_collect_api.py"
Cohesion: 0.67
Nodes (3): check(), main(), Teste ponta a ponta dos endpoints /api/collect com os cenarios simulados.…

### Community 28 - "Printer"
Cohesion: 0.12
Nodes (31): Printer, Etapa 4: identidade e (server, name), NAO ip — o Print Server permite varias…, create_printer(), create_printer_reading(), get_printer(), get_printer_readings(), list_printers(), list_printers_with_status() (+23 more)

### Community 29 - "Sidebar.tsx"
Cohesion: 0.13
Nodes (19): AlertsDonutCard(), AlertsDonutCardProps, BottomChartsProps, PagesConsumedCard(), TotalPrintsCard(), MonthlyCountersProps, NavItem(), NavItemProps (+11 more)

### Community 30 - "collect.py"
Cohesion: 0.24
Nodes (13): SQLModel, User, collect_fleet(), collect_printer(), CollectRequest, CollectResponse, FleetCollectResponse, BaseModel (+5 more)

### Community 31 - "SNMPClient"
Cohesion: 0.14
Nodes (10): Cliente SNMP para coleta de impressoras (Printer-MIB, RFC 3805)., Coleta status, contador de paginas e toners de uma impressora. Nunca levanta…, PS1: `if ($ip -match '^\\d')` — descarta 'N/A' e nomes de porta., ICMP ping, equivalente ao `New-Object ...Ping).Send($ip, 400)` do PS1. SNMP…, Escolhe os toners finais. PS1 colorida: um por cor (primeiro de cada grupo),…, Cor pela descricao; se nao identificar e for colorida, usa indice % 4., SNMPv1 GET (PS1: Build-SnmpGet, version 0, PDU 0xA0)., SNMPv2c GETBULK (PS1: Build-SnmpGetBulk, version 1, PDU 0xA5). (+2 more)

### Community 32 - "api.ts"
Cohesion: 0.14
Nodes (15): adaptPrinter(), ApiMonthlyReport, formatLastSeen(), toStatus(), toToner(), VALID_COLORS, VALID_STATUS, api (+7 more)

### Community 33 - "app-data.tsx"
Cohesion: 0.22
Nodes (15): Levantamento_impressões (planilha original), decommissionedPrinters, monthlyUsage, printers, adaptAlert(), loadMonthlyReportFromApi(), fetchAlerts(), fetchPrintersWithStatus() (+7 more)

### Community 34 - "routes/auth.py"
Cohesion: 0.28
Nodes (13): login(), post, Session, register(), Config, BaseModel, TokenResponse, UserCreate (+5 more)

### Community 35 - "TonerMonitoring.tsx"
Cohesion: 0.15
Nodes (13): PrinterDetailsModal(), PrinterTable(), classify(), FILTERS, SummaryCardProps, TONE, TonerClass, TonerMonitoring() (+5 more)

### Community 36 - "Login.tsx"
Cohesion: 0.12
Nodes (13): Logo Elgin é redesenho à mão (IA sem acesso a imagens coladas no chat, só uploads), src/components/ (padrão com header-comment por arquivo), ElginLogo(), ElginLogoProps, ACTIVE_NODES, features, Login(), handleSubmit() (+5 more)

### Community 37 - "database.py"
Cohesion: 0.22
Nodes (12): create_db_and_tables(), _finish_printer_migration(), _migrate_alert_type(), _migrate_printer_schema(), Recria `printers` (schema atual) e copia `printers_old` para dentro dela, numa…, Adiciona alerts.alert_type em bancos criados antes da Etapa 8A., Caminho do arquivo .db atual, se o banco for SQLite em disco (nao :memory:)., Etapa 4 — reconstroi `printers` para trocar a identidade de `ip UNIQUE` para… (+4 more)

### Community 38 - "app/page.tsx"
Cohesion: 0.18
Nodes (9): DashboardPage(), AlertBanner(), AlertBannerProps, BottomCharts(), RightPanel(), RightPanelProps, globalToner, updateFilter() (+1 more)

### Community 39 - "dependencies.py"
Cohesion: 0.28
Nodes (7): get_session(), Session, Dependencias compartilhadas pelas rotas. Autenticacao: `require_user` protege…, Usuario dono do JWT do header Authorization. 401 se ausente/invalido., require_user(), decode_token(), HTTPAuthorizationCredentials

### Community 40 - "Simular-Ambiente.ps1"
Cohesion: 0.22
Nodes (5): Modo Simulado, public/data/monthly-report.json, public/data/printers.json, Arquivos de dados gerados são ignorados pelo git — gerar/apagar localmente nunca afeta o repositório, Impressoras simuladas usam prefixo SIM_ / departamentos TESTE - de propósito, pra nunca confundir com dado real

### Community 41 - "snmp.py"
Cohesion: 0.14
Nodes (16): parse_varbinds(), SNMP Collector para impressoras. Porte direto da funcao Get-TonerSNMP de…, Decodifica bytes BER como inteiro sem sinal., Extrai a lista de varbinds de uma resposta SNMP. Percorre a estrutura completa…, Retorna (candidatos, houve_resposta_snmp)., GETBULK das tres colunas de uma vez (PS1: Build-SnmpGetBulk)., Fallback: um GET por indice (PS1: laco 1..20 com 3 falhas seguidas)., Aplica os filtros do PS1 e monta um candidato a toner. (+8 more)

### Community 42 - "cn"
Cohesion: 0.21
Nodes (10): MonthlyCounters(), config, PrinterStatusBadge(), StatCard(), StatCardProps, StatCards(), StatCardsProps, TONE (+2 more)

### Community 43 - "auth.ts"
Cohesion: 0.31
Nodes (9): apiRequest(), clearToken(), getToken(), setToken(), login(), LoginResponse, logout(), readStoredAccount() (+1 more)

### Community 44 - "AppDataProvider"
Cohesion: 0.28
Nodes (6): AppDataProvider(), handleScan(), isValidReport(), loadMonthlyReport(), mergeMonthlyReport(), MonthlyReport

### Community 45 - "Relatorio-Mensal.ps1"
Cohesion: 0.33
Nodes (3): Modo Real, Contador mensal calculado por diff de duas leituras SNMP acumulativas (não existe OID de páginas do mês), Scripts PowerShell reais nunca rodaram de verdade (sem interpretador PowerShell no ambiente de dev)

### Community 46 - "servers.py"
Cohesion: 0.06
Nodes (47): Config, field_validator, Normaliza um DATABASE_URL sqlite relativo (ex.: sqlite:///./x.db) para um…, Settings, discover(), DiscoveredPrinterResponse, DiscoverResponse, get_current_server() (+39 more)

### Community 47 - "get_scheduler_status"
Cohesion: 0.40
Nodes (5): get_scheduler_status(), get, Estado da coleta agendada (APScheduler)., Estado atual, para o endpoint de diagnostico., scheduler_status()

### Community 48 - "printer_collector.py"
Cohesion: 0.20
Nodes (6): Orquestrador da coleta de impressoras. Separa as tres responsabilidades da…, Args: mode: "real" (SNMP de verdade), "mock" (cenario fixo) ou "fleet" (frota…, MockSNMPClient, Agente SNMP simulado — APENAS PARA TESTE LOCAL. Existe porque a maquina de…, Substituto do SNMPClient com a mesma assinatura de collect()., Devolve o resultado fixo do cenario (ip e is_color sao ignorados).

### Community 49 - "unhandled_exception_handler"
Cohesion: 0.40
Nodes (5): Exception, Erro nao tratado: o detalhe vai para o log do servidor, o cliente recebe apenas…, unhandled_exception_handler(), exception_handler, Request

### Community 50 - "useAppData"
Cohesion: 0.24
Nodes (7): AlertsPage(), HistoryPage(), PrintersPage(), TonerPage(), AlertsView(), AlertsViewProps, useAppData()

### Community 51 - "types.ts"
Cohesion: 0.21
Nodes (15): PrinterRanking(), PrinterRankingProps, RankedPrinter, RankList(), rankPrinters(), PAGE_SIZE_OPTIONS, PrinterTableProps, DEFAULT_FILTERS (+7 more)

### Community 52 - "DecommissionedList.tsx"
Cohesion: 0.67
Nodes (3): DecommissionedList(), DecommissionedListProps, DecommissionedPrinter

### Community 54 - "theme.tsx"
Cohesion: 0.13
Nodes (12): ibmPlexMono, metadata, publicSans, sourceSerif, Providers(), AuthGate(), getInitialTheme(), Theme (+4 more)

### Community 55 - "tests_printers_crud.py"
Cohesion: 0.33
Nodes (3): Etapa 12 - CRUD de impressoras contra o servidor rodando. Usa o banco REAL,…, Devolve (status, payload)., request()

## Knowledge Gaps
- **130 isolated node(s):** `$schema`, `typescript`, `oxc`, `react/rules-of-hooks`, `warn` (+125 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SNMPClient` connect `SNMPClient` to `printer_collector.py`, `snmp.py`, `FakeAgent`, `PrinterCollector`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Why does `PrinterCollector` connect `PrinterCollector` to `snmp_fleet_mock.py`, `main.py`, `printer_collector.py`, `SNMPResult`, `Printer`, `collect.py`, `SNMPClient`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Why does `Printer` connect `Printer` to `database.py`, `servers.py`, `printer_collector.py`, `PrinterCollector`, `collect.py`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `SNMPClient` (e.g. with `PrinterCollector` and `FakeAgent`) actually correct?**
  _`SNMPClient` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `Printer` (e.g. with `_finish_printer_migration()` and `collect_fleet()`) actually correct?**
  _`Printer` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `PrinterCollector` (e.g. with `collect_fleet()` and `collect_printer()`) actually correct?**
  _`PrinterCollector` has 9 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `typescript`, `oxc` to the rest of the system?**
  _130 weakly-connected nodes found - possible documentation gaps or missing edges._