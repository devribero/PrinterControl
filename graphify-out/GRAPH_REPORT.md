# Graph Report - PrinterControl  (2026-08-23)

## Corpus Check
- 139 files · ~93,603 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1296 nodes · 2654 edges · 79 communities (60 shown, 19 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 130 edges (avg confidence: 0.54)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a3f5b8e4`
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
- database.py
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
- adaptApi.ts
- schemas/printer.py
- cn
- tests_print_servers.py
- alert_engine.py
- NetworkView.tsx
- tests_printers_crud.py
- Role
- notifications.py
- api.ts
- SNMPClient
- NotificationsView.tsx
- Printer
- Simular-Ambiente.ps1
- TonerInfo
- useToast
- Exception
- User
- PLANO DE IMPLEMENTAÇÃO — ESCANEAR REDE REAL
- services/print_server.py
- Mapa da API
- Guia de Uso do PrinterControl
- .collect_and_save
- app-data.tsx
- snmp_fleet_mock.py
- useAppData
- Guia do Desenvolvedor
- tests_webhook.py
- Settings
- Printer
- get
- auth.ts
- SQLModel
- tests_rbac.py
- Fluxo de Dados
- Arquitetura de Deploy
- Login.tsx
- BaseModel
- field_validator
- FEATURE_MATRIX.md
- patch
- post
- Session
- Notification
- snmp.py
- printers.ts
- notify_alert
- .collect
- FakeAgent
- PrinterCollector
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

## Communities (79 total, 19 thin omitted)

### Community 0 - "UsersView.tsx"
Cohesion: 0.10
Nodes (21): ComingSoon(), ComingSoonProps, RequireRole(), FORM_VAZIO, formatarData(), FormState, UsersView(), abrirEdicao() (+13 more)

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

### Community 8 - "database.py"
Cohesion: 0.07
Nodes (29): AsyncIOScheduler, create_db_and_tables(), _finish_printer_migration(), _migrate_alert_type(), _migrate_print_servers(), _migrate_printer_schema(), _migrate_reading_uptime(), _migrate_user_rbac() (+21 more)

### Community 9 - "SNMPResult"
Cohesion: 0.07
Nodes (35): _empty_result(), enrich_discovered_printers(), EnrichedDiscoveredPrinter, _is_color(), _is_label(), _normalize_ip(), DiscoveredPrinter, Enriquecimento transitório de filas descobertas com telemetria SNMP. (+27 more)

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
Cohesion: 0.09
Nodes (39): create_server(), discover(), discover_server(), DiscoveredPrinterResponse, DiscoverResponse, _executar_discover(), get_current_server(), _get_or_404() (+31 more)

### Community 21 - "unhandled_exception_handler"
Cohesion: 0.40
Nodes (5): Erro nao tratado: o detalhe vai para o log do servidor, o cliente recebe apenas…, unhandled_exception_handler(), Exception, exception_handler, Request

### Community 22 - "tests_collect_api.py"
Cohesion: 0.67
Nodes (3): check(), main(), Teste ponta a ponta dos endpoints /api/collect com os cenarios simulados.…

### Community 25 - "adaptApi.ts"
Cohesion: 0.16
Nodes (14): adaptPrinter(), ApiMonthlyReport, formatLastSeen(), toStatus(), toToner(), VALID_COLORS, VALID_STATUS, api (+6 more)

### Community 28 - "schemas/printer.py"
Cohesion: 0.16
Nodes (17): list_printers_with_status(), Impressoras + ultima leitura de cada uma, em uma unica chamada. E o que o…, Config, PrinterCreate, PrinterReadingCreate, PrinterReadingResponse, PrinterResponse, PrinterUpdate (+9 more)

### Community 29 - "cn"
Cohesion: 0.09
Nodes (28): AlertsPage(), DashboardPage(), AlertBanner(), AlertBannerProps, AlertsView(), AlertsViewProps, AlertsDonutCard(), AlertsDonutCardProps (+20 more)

### Community 30 - "tests_print_servers.py"
Cohesion: 0.39
Nodes (7): check(), check_true(), h(), main(), Fase 4 - Registro de Print Servers e operacao por servidor. Como…, Monta um banco no formato ANTERIOR a Fase 4 (printers sem print_server_id, sem…, _testa_migracao_legada()

### Community 31 - "alert_engine.py"
Cohesion: 0.18
Nodes (15): Alert, _active(), evaluate_reading(), Session, Alertas automaticos (Etapa 8A). Roda logo apos cada PrinterReading ser…, Cria, mantem ou resolve o alerta de uma condicao. Retorna a acao tomada., Avalia uma leitura e sincroniza os alertas da impressora. Faz commit ao final.…, _sync_condition() (+7 more)

### Community 32 - "NetworkView.tsx"
Cohesion: 0.10
Nodes (25): adaptDiscovered(), FORM_VAZIO, formatarMomento(), MODOS, NetworkView(), confirmarAtivacao(), executarDescoberta(), executarSync() (+17 more)

### Community 33 - "tests_printers_crud.py"
Cohesion: 0.33
Nodes (3): Etapa 12 - CRUD de impressoras contra o servidor rodando. Usa o banco REAL,…, Devolve (status, payload)., request()

### Community 34 - "Role"
Cohesion: 0.09
Nodes (33): get_session(), Session, Dependencias compartilhadas pelas rotas. Autorizacao (Fase 1) fica CENTRALIZADA…, Usuario dono do JWT do header Authorization. 401 se ausente/invalido. O usuario…, require_user(), health_check(), lifespan(), get (+25 more)

### Community 35 - "notifications.py"
Cohesion: 0.08
Nodes (37): Notification, Notificacoes internas (Fase 7). Por que uma tabela separada de `alerts`…, AlertRef, create_notifications(), list_notifications(), mark_all_as_read(), mark_as_read(), _minha_ou_404() (+29 more)

### Community 36 - "api.ts"
Cohesion: 0.11
Nodes (15): API_BASE_URL, ApiDiscoveredPrinter, ApiDiscoveredToner, ApiError, ApiNotificationAlertRef, ApiPrinterReading, apiRequest(), describeDetail() (+7 more)

### Community 37 - "SNMPClient"
Cohesion: 0.27
Nodes (5): Cliente SNMP para coleta de impressoras (Printer-MIB, RFC 3805)., Cor pela descricao; se nao identificar e for colorida, usa indice % 4., SNMPv1 GET (PS1: Build-SnmpGet, version 0, PDU 0xA0)., SNMPv2c GETBULK (PS1: Build-SnmpGetBulk, version 1, PDU 0xA5)., SNMPClient

### Community 38 - "NotificationsView.tsx"
Cohesion: 0.13
Nodes (19): FORM_VAZIO, formatarMomento(), FormState, ICONE_SEVERIDADE, NotificationsView(), abrirEnvio(), enviar(), marcarComoLida() (+11 more)

### Community 39 - "Printer"
Cohesion: 0.24
Nodes (16): Printer, PrinterMonthly, SQLModel, Etapa 4: identidade e (server, name), NAO ip — o Print Server permite varias…, create_printer(), create_printer_reading(), get_printer(), get_printer_readings() (+8 more)

### Community 40 - "Simular-Ambiente.ps1"
Cohesion: 0.16
Nodes (6): Modo Real, Contador mensal calculado por diff de duas leituras SNMP acumulativas (não existe OID de páginas do mês), Scripts PowerShell reais nunca rodaram de verdade (sem interpretador PowerShell no ambiente de dev), public/data/monthly-report.json, public/data/printers.json, Arquivos de dados gerados são ignorados pelo git — gerar/apagar localmente nunca afeta o repositório

### Community 41 - "TonerInfo"
Cohesion: 0.16
Nodes (13): Decodifica bytes BER como inteiro sem sinal., Retorna (candidatos, houve_resposta_snmp)., GETBULK das tres colunas de uma vez (PS1: Build-SnmpGetBulk)., Fallback: um GET por indice (PS1: laco 1..20 com 3 falhas seguidas)., Aplica os filtros do PS1 e monta um candidato a toner., GET de um valor numerico (INTEGER, Counter32, Gauge32, TimeTicks)., GET de uma OCTET STRING., Envia um GET e devolve o primeiro varbind valido da resposta. (+5 more)

### Community 42 - "useToast"
Cohesion: 0.11
Nodes (22): PrinterDetailsModal(), PrinterTable(), RightPanel(), RightPanelProps, classify(), FILTERS, SummaryCardProps, TONE (+14 more)

### Community 44 - "User"
Cohesion: 0.10
Nodes (31): Fabrica de dependencia: exige que o usuario tenha (ou herde) um dos papeis…, require_roles(), True se o papel do usuario satisfaz qualquer um dos exigidos., User, get, Conta autenticada e seu papel — usado para decidir o que exibir/permitir., read_current_user(), _active_admin_count() (+23 more)

### Community 45 - "PLANO DE IMPLEMENTAÇÃO — ESCANEAR REDE REAL"
Cohesion: 0.05
Nodes (39): A. Endpoint (implementado), Alertas, Arquitetura atual, Arquitetura do PrinterControl, B. Service reutilizável, Banco, C. Funções Print Server reutilizáveis, Cliente de API (+31 more)

### Community 46 - "services/print_server.py"
Cohesion: 0.05
Nodes (35): PrintServer, SQLModel, str, Print Server como entidade (Fase 4). Ate aqui um Print Server existia de duas…, Modos aceitos, iguais aos de `settings.print_server_mode`., ServerMode, discover_printers(), DiscoveredPrinter (+27 more)

### Community 47 - "Mapa da API"
Cohesion: 0.04
Nodes (46): Alertas, Autenticação, Coleta, Diagnóstico, Escanear Rede (implementado), `GET /`, `GET /api/alerts`, `GET /api/alerts/{alert_id}` (+38 more)

### Community 48 - "Guia de Uso do PrinterControl"
Cohesion: 0.10
Nodes (20): Acessar via web — PARCIAL, Adicionar impressora — AUSENTE/PARCIAL, Alertas — FUNCIONAL na leitura; PARCIAL nas ações, Ações, Como acessar, Configurações — COMING SOON, Configurações, Usuários e Integrações — COMING SOON, Dashboard — FUNCIONAL/PARCIAL (+12 more)

### Community 49 - ".collect_and_save"
Cohesion: 0.22
Nodes (6): Printer, Session, Converte SNMPResult em PrinterReading. Toner ausente vira NULL (a coluna e…, Deduz se a impressora e colorida a partir do modelo/nome (regra do PS1)., Etiquetadora/portatil: sem Printer-MIB, o PS1 nem consulta SNMP., Coleta uma impressora e persiste a leitura. Args: printer_id: id da impressora…

### Community 50 - "app-data.tsx"
Cohesion: 0.12
Nodes (27): DiscoveryResults(), DiscoveryResultsProps, statusLabel(), adaptAlert(), loadMonthlyReportFromApi(), discoverPrinters(), fetchAlerts(), fetchPrintersWithStatus() (+19 more)

### Community 51 - "snmp_fleet_mock.py"
Cohesion: 0.23
Nodes (10): _base_page_count(), _increment(), profile_for(), Simulador de frota — APENAS PARA TESTE LOCAL. Diferenca para snmp_mock.py: la…, Perfil deterministico da impressora: online | offline | snmp_mudo | baixo |…, Contador inicial plausivel para uma impressora que nunca foi lida., Paginas impressas entre duas coletas — fixo por impressora, 5 a 124., Nivel do toner: base do perfil + desvio deterministico por impressora/cor,… (+2 more)

### Community 52 - "useAppData"
Cohesion: 0.09
Nodes (23): react, ibmPlexMono, metadata, publicSans, sourceSerif, PrintersPage(), Providers(), TonerPage() (+15 more)

### Community 53 - "Guia do Desenvolvedor"
Cohesion: 0.13
Nodes (14): Backend, Banco, Comandos do frontend, Escanear Rede (implementado), Guia do Desenvolvedor, O que não executar em produção sem autorização, Print Server, Riscos conhecidos (+6 more)

### Community 54 - "tests_webhook.py"
Cohesion: 0.36
Nodes (5): PrinterReading, make_offline_reading(), make_reading(), Etapa 6 - webhook de alerta critico de toner. Banco SQLite temporario e ISOLADO…, reset_alerts_and_readings()

### Community 55 - "Settings"
Cohesion: 0.18
Nodes (7): Config, field_validator, Normaliza um DATABASE_URL sqlite relativo (ex.: sqlite:///./x.db) para um…, Impede que um ambiente de producao suba silenciosamente com o secret de…, Settings, BaseSettings, model_validator

### Community 56 - "Printer"
Cohesion: 0.18
Nodes (16): PrinterDetailsModalProps, PrinterRanking(), PrinterRankingProps, RankedPrinter, RankList(), rankPrinters(), PAGE_SIZE_OPTIONS, PrinterTableProps (+8 more)

### Community 58 - "auth.ts"
Cohesion: 0.25
Nodes (15): clearToken(), getToken(), isTokenPersistent(), setToken(), ApiUser, cacheAccount(), fetchCurrentUser(), login() (+7 more)

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
Cohesion: 0.10
Nodes (17): Logo Elgin é redesenho à mão (IA sem acesso a imagens coladas no chat, só uploads), src/components/ (padrão com header-comment por arquivo), ElginLogo(), ElginLogoProps, ACTIVE_NODES, features, Login(), handleSubmit() (+9 more)

### Community 75 - "snmp.py"
Cohesion: 0.26
Nodes (10): parse_varbinds(), SNMP Collector para impressoras. Porte direto da funcao Get-TonerSNMP de…, Decodifica um OID BER para notacao pontuada., Extrai a lista de varbinds de uma resposta SNMP. Percorre a estrutura completa…, Le um TLV BER. Retorna (tag, length, value_start, next_pos)., _read_oid(), _read_tlv(), check() (+2 more)

### Community 76 - "printers.ts"
Cohesion: 0.10
Nodes (22): Levantamento_impressões (planilha original), ReportsPage(), DecommissionedList(), DecommissionedListProps, DepartmentBreakdown(), DepartmentBreakdownProps, MONTHS, MonthlyCounters() (+14 more)

### Community 77 - "notify_alert"
Cohesion: 0.20
Nodes (11): get_alert(), list_alerts(), notify_alert(), get, patch, post, Session, Resolve um alerta. Ate a Fase 1 esta rota estava SEM protecao alguma — qualquer… (+3 more)

### Community 78 - ".collect"
Cohesion: 0.20
Nodes (5): Coleta status, contador de paginas e toners de uma impressora. Nunca levanta…, PS1: `if ($ip -match '^\\d')` — descarta 'N/A' e nomes de porta., ICMP ping, equivalente ao `New-Object ...Ping).Send($ip, 400)` do PS1. SNMP…, Escolhe os toners finais. PS1 colorida: um por cor (primeiro de cada grupo),…, Ticks de 1/100s -> 'Xd, Yh, Zm' (mesmo formato do PS1).

### Community 79 - "FakeAgent"
Cohesion: 0.31
Nodes (3): FakeAgent, Extrai (pdu_tag, [oids]) de um GET/GETBULK., Responde GET e GETBULK para um conjunto de OIDs configurado.

### Community 80 - "PrinterCollector"
Cohesion: 0.17
Nodes (12): Alert, SQLModel, TonerHistory, PrinterCollector, Coleta uma impressora e grava o resultado como PrinterReading., active(), collect(), Etapa 8A - validacao dos alertas automaticos. Usa banco SQLite temporario e o… (+4 more)

## Knowledge Gaps
- **273 isolated node(s):** ``GET /api/auth/me``, ``POST /api/auth/login``, ``GET /api/users``, ``POST /api/users``, ``PATCH /api/users/{user_id}`` (+268 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Notification` connect `notifications.py` to `adaptApi.ts`, `app-data.tsx`, `NotificationsView.tsx`?**
  _High betweenness centrality (0.322) - this node is a cross-community bridge._
- **Why does `SNMPClient` connect `SNMPClient` to `printer_fleet.py`, `database.py`, `SNMPResult`, `TonerInfo`, `snmp.py`, `.collect`, `FakeAgent`, `PrinterCollector`, `.collect_and_save`, `LocalSNMPClient`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Are the 29 inferred relationships involving `User` (e.g. with `require_roles()` and `require_user()`) actually correct?**
  _`User` has 29 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `Printer` (e.g. with `_finish_printer_migration()` and `notify_alert()`) actually correct?**
  _`Printer` has 22 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `SNMPClient` (e.g. with `PrinterCollector` and `FakeAgent`) actually correct?**
  _`SNMPClient` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `SNMPResult` (e.g. with `enrich_discovered_printers()` and `PrinterCollector`) actually correct?**
  _`SNMPResult` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects ``GET /api/auth/me``, ``POST /api/auth/login``, ``GET /api/users`` to the rest of the system?**
  _273 weakly-connected nodes found - possible documentation gaps or missing edges._