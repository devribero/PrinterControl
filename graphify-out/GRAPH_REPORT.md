# Graph Report - PrinterControl  (2026-08-23)

## Corpus Check
- 150 files · ~107,819 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1420 nodes · 2966 edges · 78 communities (69 shown, 9 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 135 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f4ec274f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- snmp_fleet_mock.py
- package.json
- Main.ps1
- Elgin Impressoras (painel de monitoramento)
- PrinterCollector
- Coletar-Impressoras.ps1
- compilerOptions
- Printer
- tests_printer_fleet.py
- routes/auth.py
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
- NotificationsView
- adaptApi.ts
- printers.py
- theme.tsx
- Operação em Produção
- alert_engine.py
- NetworkView
- collect.py
- dependencies.py
- notifications.py
- api.ts
- SNMPClient
- Simular-Ambiente.ps1
- database.py
- cn
- AlertsView.tsx
- Role
- PLANO DE IMPLEMENTAÇÃO — ESCANEAR REDE REAL
- services/print_server.py
- Impressoras
- Guia de Uso do PrinterControl
- ElginLogo.tsx
- app-data.tsx
- NotificationsView.tsx
- types.ts
- Guia do Desenvolvedor
- User
- hash_password
- tests_rbac.py
- SNMPResult
- auth.ts
- Alert
- useAppData
- Print Server
- Fluxo de Dados
- Arquitetura de Deploy
- tests_production.py
- tests_print_servers.py
- Autenticação
- FEATURE_MATRIX.md
- layout.tsx
- Relatorio-Mensal.ps1
- Mapa da API
- Notificações (Fase 7)
- Alertas
- backup_db.py
- Coleta
- Usuários (Fase 3)
- Servico-PrinterControl.ps1
- NetworkView.tsx
- integrations/page.tsx
- printers.ts

## God Nodes (most connected - your core abstractions)
1. `User` - 65 edges
2. `Printer` - 49 edges
3. `cn()` - 39 edges
4. `SNMPClient` - 37 edges
5. `SNMPResult` - 34 edges
6. `useAppData()` - 33 edges
7. `create_db_and_tables()` - 27 edges
8. `useToast()` - 27 edges
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

## Communities (78 total, 9 thin omitted)

### Community 0 - "snmp_fleet_mock.py"
Cohesion: 0.23
Nodes (10): _base_page_count(), _increment(), profile_for(), Simulador de frota — APENAS PARA TESTE LOCAL. Diferenca para snmp_mock.py: la…, Perfil deterministico da impressora: online | offline | snmp_mudo | baixo |…, Contador inicial plausivel para uma impressora que nunca foi lida., Paginas impressas entre duas coletas — fixo por impressora, 5 a 124., Nivel do toner: base do perfil + desvio deterministico por impressora/cor,… (+2 more)

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
Nodes (26): PrinterCollector, Printer, Session, Orquestrador da coleta de impressoras. Separa as tres responsabilidades da…, Converte SNMPResult em PrinterReading. Toner ausente vira NULL (a coluna e…, Coleta uma impressora e grava o resultado como PrinterReading., Deduz se a impressora e colorida a partir do modelo/nome (regra do PS1)., Etiquetadora/portatil: sem Printer-MIB, o PS1 nem consulta SNMP. (+18 more)

### Community 5 - "Coletar-Impressoras.ps1"
Cohesion: 0.21
Nodes (13): Build-SnmpGet(), Build-SnmpGetBulk(), Convert-SnmpValueBytes(), Get-ImpressorasServidor(), Get-TonerSNMP(), Parse-SnmpBulkResponse(), Parse-SnmpCounter(), Parse-SnmpInt() (+5 more)

### Community 6 - "compilerOptions"
Cohesion: 0.06
Nodes (30): dom, dom.iterable, esnext, .next/dev/types/**/*.ts, next-env.d.ts, .next/types/**/*.ts, node_modules, **/*.ts (+22 more)

### Community 7 - "Printer"
Cohesion: 0.16
Nodes (13): Printer, PrinterMonthly, PrinterReading, SQLModel, Etapa 4: identidade e (server, name), NAO ip — o Print Server permite varias…, seed_database(), collect_fleet(), Etapa 11 - coleta simulada da frota inteira, ponta a ponta. Copia o banco real… (+5 more)

### Community 8 - "tests_printer_fleet.py"
Cohesion: 0.18
Nodes (4): fake_real_collect(), Etapa 5 - orquestracao da frota (printer_fleet.collect_fleet). Roda sobre um…, RecordingThreadPoolExecutor, _OriginalTPE

### Community 9 - "routes/auth.py"
Cohesion: 0.14
Nodes (24): change_own_password(), login(), get, patch, post, Session, Conta autenticada e seu papel — usado para decidir o que exibir/permitir., Perfil da PROPRIA conta (Fase 8). So o nome. Nao recebe id: o alvo e sempre a… (+16 more)

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
Nodes (41): create_server(), discover(), discover_server(), DiscoveredPrinterResponse, DiscoverResponse, _executar_discover(), get_current_server(), _get_or_404() (+33 more)

### Community 21 - "unhandled_exception_handler"
Cohesion: 0.40
Nodes (5): Exception, Erro nao tratado: o detalhe vai para o log do servidor, o cliente recebe apenas…, unhandled_exception_handler(), exception_handler, Request

### Community 22 - "tests_collect_api.py"
Cohesion: 0.67
Nodes (3): check(), main(), Teste ponta a ponta dos endpoints /api/collect com os cenarios simulados.…

### Community 23 - "NotificationsView"
Cohesion: 0.15
Nodes (12): formatarMomento(), NotificationsView(), abrirEnvio(), enviar(), marcarComoLida(), marcarTodasComoLidas(), validar(), adaptNotification() (+4 more)

### Community 25 - "adaptApi.ts"
Cohesion: 0.13
Nodes (19): adaptAlert(), adaptPrinter(), ApiMonthlyReport, formatLastSeen(), loadMonthlyReportFromApi(), toStatus(), toToner(), VALID_COLORS (+11 more)

### Community 28 - "printers.py"
Cohesion: 0.12
Nodes (29): create_printer(), create_printer_reading(), get_printer(), get_printer_readings(), list_printers(), list_printers_with_status(), monthly_report(), get (+21 more)

### Community 29 - "theme.tsx"
Cohesion: 0.27
Nodes (8): lerPreferencia(), resolver(), sistemaEscuro(), Theme, ThemeContext, ThemeContextValue, ThemePreference, ThemeProvider()

### Community 30 - "Operação em Produção"
Cohesion: 0.11
Nodes (18): 1. Antes do primeiro deploy, 2. Instalar, 3. Dia a dia, 4. Diagnóstico, 5. Backup, 6. Recuperação — o que acontece se o processo cair, 7. Problemas comuns, 8. Dívida técnica conhecida — FK órfã para `printers_old` (+10 more)

### Community 31 - "alert_engine.py"
Cohesion: 0.18
Nodes (15): Alert, _active(), evaluate_reading(), Session, Alertas automaticos (Etapa 8A). Roda logo apos cada PrinterReading ser…, Cria, mantem ou resolve o alerta de uma condicao. Retorna a acao tomada., Avalia uma leitura e sincroniza os alertas da impressora. Faz commit ao final.…, _sync_condition() (+7 more)

### Community 32 - "NetworkView"
Cohesion: 0.14
Nodes (14): adaptDiscovered(), formatarMomento(), NetworkView(), confirmarAtivacao(), executarDescoberta(), limparResultados(), salvar(), selecionar() (+6 more)

### Community 33 - "collect.py"
Cohesion: 0.14
Nodes (17): collect_fleet(), collect_printer(), CollectRequest, CollectResponse, FleetCollectResponse, get_scheduler_status(), list_scenarios(), BaseModel (+9 more)

### Community 34 - "dependencies.py"
Cohesion: 0.14
Nodes (11): Session, Dependencias compartilhadas pelas rotas. Autorizacao (Fase 1) fica CENTRALIZADA…, Usuario dono do JWT do header Authorization. 401 se ausente/invalido. O usuario…, Fabrica de dependencia: exige que o usuario tenha (ou herde) um dos papeis…, require_roles(), require_user(), decode_token(), Etapa 12 - CRUD de impressoras contra o servidor rodando. Usa o banco REAL,… (+3 more)

### Community 35 - "notifications.py"
Cohesion: 0.10
Nodes (31): Notification, SQLModel, Notificacoes internas (Fase 7). Por que uma tabela separada de `alerts`…, AlertRef, create_notifications(), list_notifications(), mark_all_as_read(), mark_as_read() (+23 more)

### Community 36 - "api.ts"
Cohesion: 0.12
Nodes (15): API_BASE_URL, ApiDiscoveredPrinter, ApiDiscoveredToner, ApiNotificationAlertRef, ApiPrinterReading, apiRequest(), describeDetail(), getToken() (+7 more)

### Community 37 - "SNMPClient"
Cohesion: 0.05
Nodes (38): parse_varbinds(), SNMP Collector para impressoras. Porte direto da funcao Get-TonerSNMP de…, Decodifica um OID BER para notacao pontuada., Decodifica bytes BER como inteiro sem sinal., Extrai a lista de varbinds de uma resposta SNMP. Percorre a estrutura completa…, Cliente SNMP para coleta de impressoras (Printer-MIB, RFC 3805)., Coleta status, contador de paginas e toners de uma impressora. Nunca levanta…, PS1: `if ($ip -match '^\\d')` — descarta 'N/A' e nomes de porta. (+30 more)

### Community 40 - "Simular-Ambiente.ps1"
Cohesion: 0.18
Nodes (7): Modo Simulado, public/data/monthly-report.json, public/data/printers.json, Arquivos de dados gerados são ignorados pelo git — gerar/apagar localmente nunca afeta o repositório, Impressoras simuladas usam prefixo SIM_ / departamentos TESTE - de propósito, pra nunca confundir com dado real, isValidPrinter(), loadRealPrinters()

### Community 41 - "database.py"
Cohesion: 0.08
Nodes (35): AsyncIOScheduler, create_db_and_tables(), _finish_printer_migration(), _migrate_alert_type(), _migrate_print_servers(), _migrate_printer_schema(), _migrate_reading_uptime(), _migrate_user_rbac() (+27 more)

### Community 42 - "cn"
Cohesion: 0.07
Nodes (42): DashboardPage(), TonerPage(), AlertsDonutCard(), AlertsDonutCardProps, BottomCharts(), PagesConsumedCard(), TotalPrintsCard(), ElginLogo() (+34 more)

### Community 43 - "AlertsView.tsx"
Cohesion: 0.31
Nodes (6): AlertsPage(), AlertBanner(), AlertBannerProps, AlertsView(), AlertsViewProps, Alert

### Community 44 - "Role"
Cohesion: 0.13
Nodes (21): str, RBAC minimo (Fase 1). Tres papeis cobrem todas as rotas existentes hoje: -…, Role, _active_admin_count(), create_user(), _ensure_not_last_admin(), list_users(), get (+13 more)

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
Cohesion: 0.50
Nodes (3): Logo Elgin é redesenho à mão (IA sem acesso a imagens coladas no chat, só uploads), src/components/ (padrão com header-comment por arquivo), ElginLogoProps

### Community 50 - "app-data.tsx"
Cohesion: 0.14
Nodes (22): decommissionedPrinters, monthlyUsage, BackendEnvironment, discoverPrinters(), fetchBackendEnvironment(), fetchUnreadNotificationCount(), AppDataContext, AppDataContextValue (+14 more)

### Community 51 - "NotificationsView.tsx"
Cohesion: 0.09
Nodes (25): Modal(), ModalProps, FORM_VAZIO, FormState, ICONE_SEVERIDADE, Severidade, SEVERIDADES, RequireRole() (+17 more)

### Community 52 - "types.ts"
Cohesion: 0.14
Nodes (20): PrinterRanking(), PrinterRankingProps, RankedPrinter, RankList(), rankPrinters(), PAGE_SIZE_OPTIONS, PrinterTableProps, RightPanelProps (+12 more)

### Community 53 - "Guia do Desenvolvedor"
Cohesion: 0.13
Nodes (14): Backend, Banco, Comandos do frontend, Escanear Rede (implementado), Guia do Desenvolvedor, O que não executar em produção sem autorização, Print Server, Riscos conhecidos (+6 more)

### Community 54 - "User"
Cohesion: 0.25
Nodes (12): SQLModel, True se o papel do usuario satisfaz qualquer um dos exigidos., User, check(), check_true(), h(), _hash_de(), main() (+4 more)

### Community 55 - "hash_password"
Cohesion: 0.24
Nodes (12): hash_password(), check(), check_true(), h(), main(), Fase 7 - Notificacoes internas. Como…, check(), check_true() (+4 more)

### Community 56 - "tests_rbac.py"
Cohesion: 0.08
Nodes (25): Config, field_validator, Fail-fast: producao nao sobe com simulacao ligada (Fase 9). O risco concreto e…, Impede que um ambiente de producao suba silenciosamente com o secret de…, Aceita "https://a.com, https://b.com" alem da lista JSON. Sem isto,…, Producao exige origens proprias e explicitas (Fase 10). Tres recusas, todas por…, Normaliza um DATABASE_URL sqlite relativo (ex.: sqlite:///./x.db) para um…, Um ambiente escrito errado nao pode cair no default em silencio:… (+17 more)

### Community 57 - "SNMPResult"
Cohesion: 0.07
Nodes (34): _empty_result(), enrich_discovered_printers(), EnrichedDiscoveredPrinter, _is_color(), _is_label(), _normalize_ip(), DiscoveredPrinter, Enriquecimento transitório de filas descobertas com telemetria SNMP. (+26 more)

### Community 58 - "auth.ts"
Cohesion: 0.11
Nodes (26): ACTIVE_NODES, features, Login(), handleSubmit(), LoginProps, NETWORK_LINKS, NETWORK_NODES, salvarPerfil() (+18 more)

### Community 59 - "Alert"
Cohesion: 0.20
Nodes (15): get_session(), Alert, SQLModel, TonerHistory, get_alert(), list_alerts(), notify_alert(), get (+7 more)

### Community 60 - "useAppData"
Cohesion: 0.09
Nodes (33): react, PrintersPage(), ReportsPage(), AppShell(), AuthGate(), SettingsView(), trocarSenha(), validarSenha() (+25 more)

### Community 61 - "Print Server"
Cohesion: 0.22
Nodes (9): `GET /api/servers`, `GET /api/servers/current`, `PATCH /api/servers/{server_id}`, `POST /api/servers`, `POST /api/servers/discover`, `POST /api/servers/{server_id}/discover`, `POST /api/servers/{server_id}/sync`, `POST /api/servers/sync` (+1 more)

### Community 62 - "Fluxo de Dados"
Cohesion: 0.17
Nodes (11): 10. Escanear Rede (implementado), 1. Cadastro no SQLite, 2. Coleta SNMP real, 3. Coleta de frota, 4. Print Server, 5. Sincronização, 6. Alertas, 7. Relatório mensal (+3 more)

### Community 63 - "Arquitetura de Deploy"
Cohesion: 0.18
Nodes (10): Arquitetura avaliada, Arquitetura de Deploy, Autenticação, Bloqueios atuais, Cloudflare Tunnel, Configuração de aplicação, CORS, Estado atual (+2 more)

### Community 64 - "tests_production.py"
Cohesion: 0.12
Nodes (13): _caminho_do_log(), Path, Configuracao de log (Fase 10). Por que existe como modulo, e nao como um…, Substitui valores sensiveis na mensagem antes de ela ser emitida. Fica no…, Resolve settings.log_file. Vazio = so console., Instala console + arquivo rotativo na raiz do logging. Idempotente: chamar duas…, RedactSecretsFilter, setup_logging() (+5 more)

### Community 65 - "tests_print_servers.py"
Cohesion: 0.11
Nodes (16): PrintServer, SQLModel, str, Print Server como entidade (Fase 4). Ate aqui um Print Server existia de duas…, Modos aceitos, iguais aos de `settings.print_server_mode`., ServerMode, ambiente, Fase 9 - Mock e Demo Seguros. Cobre as DUAS camadas que protegem o risco… (+8 more)

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

### Community 73 - "backup_db.py"
Cohesion: 0.29
Nodes (11): aplicar_retencao(), _caminho_do_banco(), fazer_backup(), main(), _progresso(), Path, Backup do SQLite (Fase 10). .\\venv\\Scripts\\python.exe backup_db.py…, integrity_check no ARQUIVO GERADO — ver docstring do modulo. (+3 more)

### Community 74 - "Coleta"
Cohesion: 0.40
Nodes (5): Coleta, `GET /api/collect/scenarios`, `GET /api/collect/scheduler`, `POST /api/collect/fleet`, `POST /api/collect/printers/{printer_id}`

### Community 75 - "Usuários (Fase 3)"
Cohesion: 0.50
Nodes (4): `GET /api/users`, `PATCH /api/users/{user_id}`, `POST /api/users`, Usuários (Fase 3)

### Community 76 - "Servico-PrinterControl.ps1"
Cohesion: 0.53
Nodes (9): Confirmar-PreRequisitos(), Escrever(), Iniciar(), Instalar(), Instalar-Backup(), Obter-Tarefa(), Parar(), Remover() (+1 more)

### Community 77 - "NetworkView.tsx"
Cohesion: 0.15
Nodes (15): DiscoveryResults(), DiscoveryResultsProps, statusLabel(), FORM_VAZIO, MODOS, executarSync(), ServerFormState, STATUS_SERVIDOR (+7 more)

### Community 82 - "printers.ts"
Cohesion: 0.12
Nodes (18): Levantamento_impressões (planilha original), BottomChartsProps, DecommissionedList(), DecommissionedListProps, DemoDataBadge(), DemoDataBadgeProps, DepartmentBreakdown(), DepartmentBreakdownProps (+10 more)

## Knowledge Gaps
- **295 isolated node(s):** `$schema`, `typescript`, `oxc`, `react/rules-of-hooks`, `warn` (+290 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `collect.py`, `dependencies.py`, `notifications.py`, `tests_print_servers.py`, `Printer`, `routes/auth.py`, `database.py`, `Role`, `servers.py`, `hash_password`, `tests_rbac.py`, `Alert`, `printers.py`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Why does `SNMPClient` connect `SNMPClient` to `tests_printer_fleet.py`, `SNMPResult`, `PrinterCollector`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `Printer` connect `Printer` to `collect.py`, `tests_print_servers.py`, `PrinterCollector`, `tests_printer_fleet.py`, `database.py`, `services/print_server.py`, `servers.py`, `hash_password`, `tests_rbac.py`, `Alert`, `printers.py`, `alert_engine.py`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Are the 37 inferred relationships involving `User` (e.g. with `require_roles()` and `require_user()`) actually correct?**
  _`User` has 37 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `Printer` (e.g. with `_finish_printer_migration()` and `notify_alert()`) actually correct?**
  _`Printer` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `SNMPClient` (e.g. with `PrinterCollector` and `FakeAgent`) actually correct?**
  _`SNMPClient` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `SNMPResult` (e.g. with `enrich_discovered_printers()` and `PrinterCollector`) actually correct?**
  _`SNMPResult` has 6 INFERRED edges - model-reasoned connections that need verification._