# Graph Report - PrinterControl  (2026-08-24)

## Corpus Check
- 156 files · ~127,101 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1585 nodes · 3122 edges · 114 communities (92 shown, 22 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 136 edges (avg confidence: 0.59)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6b3a0b86`
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
- servers.py
- types.ts
- MockSNMPClient
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
- Sidebar.tsx
- unhandled_exception_handler
- tests_collect_api.py
- tests_uptime.py
- Printer
- schemas/printer.py
- login
- Operação em Produção
- Alert
- printer_sync.py
- adaptApi.ts
- User
- create_notifications
- api.ts
- SNMPClient
- enrich_discovered_printers
- NetworkView
- Simular-Ambiente.ps1
- scheduler.py
- fetchPrinters.ts
- printers.ts
- database.py
- PLANO DE IMPLEMENTAÇÃO — ESCANEAR REDE REAL
- services/print_server.py
- Impressoras
- Guia de Uso do PrinterControl
- tests_rbac.py
- app-data.tsx
- tests_print_server_discovery.py
- UsersView
- Guia do Desenvolvedor
- NotificationsView.tsx
- create_db_and_tables
- Settings
- SNMPResult
- auth.ts
- notify_alert
- useAppData
- Print Server
- Fluxo de Dados
- Arquitetura de Deploy
- Dívida técnica — registro único
- tests_print_servers.py
- Autenticação
- VISAO_GERAL.md
- Role
- tests_printers_crud.py
- Mapa da API
- Notificações (Fase 7)
- Alertas
- backup_db.py
- Coleta
- Usuários (Fase 3)
- Servico-PrinterControl.ps1
- 7. Roteiro de teste em produção — amanhã
- 4. Variáveis de ambiente
- 3. Tudo o que o sistema faz hoje, por área
- printer_fleet.py
- integrations/page.tsx
- cn
- RateLimiter
- 6. Subir o sistema em produção hoje
- PrinterTable.tsx
- PrinterControl — Visão geral do sistema
- 5. Modo real x modo simulado, e os riscos
- ambiente
- 8. Dívida técnica conhecida — FK órfã para `printers_old`
- 2. Como o sistema é montado
- layout.tsx
- get
- tests_printer_fleet.py
- Relatorio-Mensal.ps1
- Exception
- Login.tsx
- discovery.py
- tests_login_hardening.py
- Topbar
- theme.tsx
- Exception
- Request
- _migrate_printer_schema
- require_user
- Ações
- ElginLogo.tsx
- Path
- SQLModel
- str
- User
- Request
- User
- User

## God Nodes (most connected - your core abstractions)
1. `User` - 67 edges
2. `cn()` - 39 edges
3. `SNMPClient` - 37 edges
4. `useAppData()` - 35 edges
5. `Printer` - 34 edges
6. `SNMPResult` - 34 edges
7. `useToast()` - 29 edges
8. `create_db_and_tables()` - 27 edges
9. `Printer` - 26 edges
10. `PrinterCollector` - 26 edges

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

## Communities (114 total, 22 thin omitted)

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

### Community 4 - "PrinterCollector"
Cohesion: 0.14
Nodes (12): PrinterCollector, Printer, Session, Converte SNMPResult em PrinterReading. Toner ausente vira NULL (a coluna e…, Coleta uma impressora e grava o resultado como PrinterReading., Deduz se a impressora e colorida a partir do modelo/nome (regra do PS1)., Etiquetadora/portatil: sem Printer-MIB, o PS1 nem consulta SNMP., Coleta uma impressora e persiste a leitura. Args: printer_id: id da impressora… (+4 more)

### Community 5 - "Coletar-Impressoras.ps1"
Cohesion: 0.21
Nodes (13): Build-SnmpGet(), Build-SnmpGetBulk(), Convert-SnmpValueBytes(), Get-ImpressorasServidor(), Get-TonerSNMP(), Parse-SnmpBulkResponse(), Parse-SnmpCounter(), Parse-SnmpInt() (+5 more)

### Community 6 - "compilerOptions"
Cohesion: 0.06
Nodes (30): dom, dom.iterable, esnext, .next/dev/types/**/*.ts, next-env.d.ts, .next/types/**/*.ts, node_modules, **/*.ts (+22 more)

### Community 7 - "servers.py"
Cohesion: 0.07
Nodes (52): collect_fleet(), collect_printer(), CollectRequest, CollectResponse, FleetCollectResponse, BaseModel, post, Session (+44 more)

### Community 8 - "types.ts"
Cohesion: 0.12
Nodes (20): AlertsPage(), AlertBanner(), AlertBannerProps, AlertsView(), AlertsViewProps, BottomCharts(), DiscoveryResults(), DiscoveryResultsProps (+12 more)

### Community 9 - "MockSNMPClient"
Cohesion: 0.20
Nodes (5): Cenarios de teste disponiveis (fonte unica: snmp_mock.SCENARIOS)., Args: mode: "real" (SNMP de verdade), "mock" (cenario fixo) ou "fleet" (frota…, MockSNMPClient, Substituto do SNMPClient com a mesma assinatura de collect()., Devolve o resultado fixo do cenario (ip e is_color sao ignorados).

### Community 10 - "plugins"
Cohesion: 0.22
Nodes (8): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, typescript, warn

### Community 11 - "Printer"
Cohesion: 0.16
Nodes (12): HistoryPage(), HistoryMatrix(), HistoryMatrixProps, PrinterDetailsModalProps, PrinterRanking(), PrinterRankingProps, RankedPrinter, RankList() (+4 more)

### Community 12 - "graphify (knowledge graph tool)"
Cohesion: 0.25
Nodes (8): graphify (knowledge graph tool), graphify explain command, graphify path command, graphify query command, graphify update command, graphify-out/graph.json, graphify-out/GRAPH_REPORT.md, graphify-out/wiki/index.md

### Community 20 - "Sidebar.tsx"
Cohesion: 0.11
Nodes (22): AlertsDonutCard(), AlertsDonutCardProps, BottomChartsProps, PagesConsumedCard(), TotalPrintsCard(), DemoDataBadge(), DemoDataBadgeProps, MonthlyCounters() (+14 more)

### Community 21 - "unhandled_exception_handler"
Cohesion: 0.50
Nodes (4): Erro nao tratado: o detalhe vai para o log do servidor, o cliente recebe apenas…, unhandled_exception_handler(), Exception, exception_handler

### Community 22 - "tests_collect_api.py"
Cohesion: 0.67
Nodes (3): check(), main(), Teste ponta a ponta dos endpoints /api/collect com os cenarios simulados.…

### Community 23 - "tests_uptime.py"
Cohesion: 0.11
Nodes (16): _migrate_reading_uptime(), Etapa 7: adiciona printer_readings.uptime em bancos criados antes desta etapa.…, Notification, SQLModel, Notificacoes internas (Fase 7). Por que uma tabela separada de `alerts`…, create_access_token(), hash_password(), Hash de senha e emissao/validacao do JWT. POR QUE PyJWT E NAO python-jose (Fase… (+8 more)

### Community 25 - "Printer"
Cohesion: 0.16
Nodes (13): Printer, PrinterMonthly, PrinterReading, SQLModel, Etapa 4: identidade e (server, name), NAO ip — o Print Server permite varias…, Orquestrador da coleta de impressoras. Separa as tres responsabilidades da…, collect_fleet(), Etapa 11 - coleta simulada da frota inteira, ponta a ponta. Copia o banco real… (+5 more)

### Community 28 - "schemas/printer.py"
Cohesion: 0.07
Nodes (34): create_printer(), create_printer_reading(), get_printer(), get_printer_readings(), list_printers(), list_printers_with_status(), monthly_report(), get (+26 more)

### Community 29 - "login"
Cohesion: 0.19
Nodes (13): change_own_password(), _identificar_origem(), login(), patch, post, Session, Perfil da PROPRIA conta (Fase 8). So o nome. `require_active_user` (nao…, Troca da propria senha, exigindo a atual. Usa `require_user`, nao… (+5 more)

### Community 30 - "Operação em Produção"
Cohesion: 0.15
Nodes (13): 1. Antes do primeiro deploy, 2. Instalar, 3. Dia a dia, 4. Diagnóstico, 5. Backup, 6. Recuperação — o que acontece se o processo cair, 7. Problemas comuns, 9. Se precisar aparecer em `services.msc` (+5 more)

### Community 31 - "Alert"
Cohesion: 0.16
Nodes (18): Alert, Alert, SQLModel, TonerHistory, _active(), evaluate_reading(), Session, Alertas automaticos (Etapa 8A). Roda logo apos cada PrinterReading ser… (+10 more)

### Community 32 - "printer_sync.py"
Cohesion: 0.18
Nodes (12): obter_modelo(), obter_tipo_impressora(), Regras de classificacao portadas do Main.ps1 (Etapa 4). Correspondencia exata:…, Traduz DriverName (Windows) em nome comercial, igual ao Main.ps1., Classifica A4 / Etiqueta / Portatil a partir de Nome+Modelo, igual ao Main.ps1., Session, Sincronizacao Print Server -> banco (Etapa 4). Print Server ->…, Executa um ciclo completo de sincronizacao para UM Print Server. Ja era… (+4 more)

### Community 33 - "adaptApi.ts"
Cohesion: 0.13
Nodes (18): adaptAlert(), adaptPrinter(), ApiMonthlyReport, formatLastSeen(), loadMonthlyReportFromApi(), toStatus(), toToner(), VALID_COLORS (+10 more)

### Community 34 - "User"
Cohesion: 0.16
Nodes (17): Fabrica de dependencia: exige que o usuario tenha (ou herde) um dos papeis…, require_roles(), True se o papel do usuario satisfaz qualquer um dos exigidos., User, get, Conta autenticada e seu papel — usado para decidir o que exibir/permitir., read_current_user(), list_notifications() (+9 more)

### Community 35 - "create_notifications"
Cohesion: 0.10
Nodes (25): AlertRef, create_notifications(), mark_all_as_read(), mark_as_read(), _minha_ou_404(), NotificationCreate, NotificationResponse, BaseModel (+17 more)

### Community 36 - "api.ts"
Cohesion: 0.10
Nodes (17): API_BASE_URL, ApiDiscoveredPrinter, ApiDiscoveredToner, ApiDiscoveryResponse, ApiNotificationAlertRef, ApiPrinterReading, apiRequest(), describeDetail() (+9 more)

### Community 37 - "SNMPClient"
Cohesion: 0.05
Nodes (38): parse_varbinds(), SNMP Collector para impressoras. Porte direto da funcao Get-TonerSNMP de…, Decodifica um OID BER para notacao pontuada., Decodifica bytes BER como inteiro sem sinal., Extrai a lista de varbinds de uma resposta SNMP. Percorre a estrutura completa…, Cliente SNMP para coleta de impressoras (Printer-MIB, RFC 3805)., Coleta status, contador de paginas e toners de uma impressora. Nunca levanta…, PS1: `if ($ip -match '^\\d')` — descarta 'N/A' e nomes de porta. (+30 more)

### Community 38 - "enrich_discovered_printers"
Cohesion: 0.27
Nodes (7): enrich_discovered_printers(), Enriquece filas em memória; não recebe nem acessa uma sessão SQL., DiscoverySnmpTests, printer(), DiscoveredPrinter, Testes locais do enriquecimento SNMP, sem rede corporativa ou SQLite., result()

### Community 39 - "NetworkView"
Cohesion: 0.11
Nodes (17): adaptDiscovered(), formatarMomento(), NetworkView(), confirmarAtivacao(), executarDescoberta(), executarSync(), limparResultados(), salvar() (+9 more)

### Community 40 - "Simular-Ambiente.ps1"
Cohesion: 0.22
Nodes (5): Modo Simulado, public/data/monthly-report.json, public/data/printers.json, Arquivos de dados gerados são ignorados pelo git — gerar/apagar localmente nunca afeta o repositório, Impressoras simuladas usam prefixo SIM_ / departamentos TESTE - de propósito, pra nunca confundir com dado real

### Community 41 - "scheduler.py"
Cohesion: 0.11
Nodes (19): AsyncIOScheduler, health_check(), lifespan(), Saude, identificacao do ambiente (Fase 9) e diagnostico (Fase 10). O ambiente…, read_root(), get_scheduler_status(), list_scenarios(), get (+11 more)

### Community 43 - "printers.ts"
Cohesion: 0.14
Nodes (16): Levantamento_impressões (planilha original), DecommissionedList(), DecommissionedListProps, DepartmentBreakdown(), DepartmentBreakdownProps, MONTHS, RightPanel(), RightPanelProps (+8 more)

### Community 44 - "database.py"
Cohesion: 0.16
Nodes (17): get_session(), _sqlite_pragmas(), Dependencias compartilhadas pelas rotas. Autorizacao (Fase 1) fica CENTRALIZADA…, `require_user` + bloqueio de conta com troca de senha pendente. Toda rota do…, require_active_user(), Configuracao de log (Fase 10). Por que existe como modulo, e nao como um…, Coleta manual de impressoras (Etapa 6). Sem agendamento: cada chamada dispara…, Central de notificacoes internas (Fase 7). Caixa PESSOAL: `GET` e `PATCH`… (+9 more)

### Community 45 - "PLANO DE IMPLEMENTAÇÃO — ESCANEAR REDE REAL"
Cohesion: 0.05
Nodes (39): A. Endpoint (implementado), Alertas, Arquitetura atual, Arquitetura do PrinterControl, B. Service reutilizável, Banco, C. Funções Print Server reutilizáveis, Cliente de API (+31 more)

### Community 46 - "services/print_server.py"
Cohesion: 0.15
Nodes (18): discover_printers(), DiscoveredPrinter, _escapar_powershell(), _mock_discover(), PrintServerError, Camada de Print Server (Etapa 3). Reproduz a descoberta de impressoras do…, Uma linha do que Get-Printer + Get-PrinterPort devolveriam, combinadas., Frota simulada. Inclui de proposito: - drivers que casam as regras de Obter-… (+10 more)

### Community 47 - "Impressoras"
Cohesion: 0.22
Nodes (9): `GET /api/printers`, `GET /api/printers/monthly-report`, `GET /api/printers/{printer_id}`, `GET /api/printers/{printer_id}/readings`, `GET /api/printers/with-status`, Impressoras, `PATCH /api/printers/{printer_id}`, `POST /api/printers` (+1 more)

### Community 48 - "Guia de Uso do PrinterControl"
Cohesion: 0.14
Nodes (14): Alertas — FUNCIONAL na leitura; PARCIAL nas ações, Como acessar, Configurações, Usuários e Integrações — COMING SOON, Dashboard — FUNCIONAL/PARCIAL, Exportar CSV — FUNCIONAL, Guia de Uso do PrinterControl, Histórico — PARCIAL, Interpretação dos dados (+6 more)

### Community 49 - "tests_rbac.py"
Cohesion: 0.24
Nodes (12): check(), check_true(), _confere_rbac_do_frontend(), h(), main(), Fase 1 - Autenticacao, RBAC e protecao das rotas. Diferente dos demais…, O frontend tem a sua propria copia da hierarquia de papeis, em…, Cria um banco no formato ANTERIOR a Fase 1 (users sem role/is_active), roda a… (+4 more)

### Community 50 - "app-data.tsx"
Cohesion: 0.13
Nodes (24): decommissionedPrinters, monthlyUsage, BackendEnvironment, discoverPrinters(), fetchBackendEnvironment(), fetchUnreadNotificationCount(), AppDataContext, AppDataContextValue (+16 more)

### Community 52 - "UsersView"
Cohesion: 0.19
Nodes (12): abrirEnvio(), formatarData(), UsersView(), abrirEdicao(), confirmarAtivacao(), salvar(), validar(), createUser() (+4 more)

### Community 53 - "Guia do Desenvolvedor"
Cohesion: 0.13
Nodes (15): Backend, Banco, Comandos do frontend, Escanear Rede (implementado), Guia do Desenvolvedor, Já resolvido — não reabra, O que não executar em produção sem autorização, Print Server (+7 more)

### Community 54 - "NotificationsView.tsx"
Cohesion: 0.14
Nodes (17): FORM_VAZIO, formatarMomento(), FormState, ICONE_SEVERIDADE, NotificationsView(), enviar(), marcarComoLida(), marcarTodasComoLidas() (+9 more)

### Community 55 - "create_db_and_tables"
Cohesion: 0.11
Nodes (24): create_db_and_tables(), _migrate_alert_type(), _migrate_print_servers(), _migrate_user_login_fields(), _migrate_user_rbac(), Fase 1 (RBAC): adiciona users.role e users.is_active em bancos criados antes…, Login por username e troca de senha obrigatoria (2026-08-24). Adiciona…, Fase 4: registro de Print Servers. A tabela `print_servers` em si e criada pelo… (+16 more)

### Community 56 - "Settings"
Cohesion: 0.06
Nodes (25): Config, field_validator, Fail-fast: producao nao sobe com simulacao ligada (Fase 9). O risco concreto e…, Impede que um ambiente de producao suba silenciosamente com o secret de…, Aceita "https://a.com, https://b.com" alem da lista JSON. Sem isto,…, Producao exige origens proprias e explicitas (Fase 10). Tres recusas, todas por…, Normaliza um DATABASE_URL sqlite relativo (ex.: sqlite:///./x.db) para um…, Um ambiente escrito errado nao pode cair no default em silencio:… (+17 more)

### Community 57 - "SNMPResult"
Cohesion: 0.13
Nodes (15): MockSNMPScenarios, Agente SNMP simulado — APENAS PARA TESTE LOCAL. Existe porque a maquina de…, SNMP responde o contador, mas nao expoe a tabela de consumiveis., Monocromatica com toner em 5%., Colorida com ciano critico (18%) e os demais normais., Contador reiniciado (troca de placa/formatador): page_count baixo., Cenarios de teste. Cada metodo devolve um SNMPResult completo., Monocromatica saudavel. (+7 more)

### Community 58 - "auth.ts"
Cohesion: 0.22
Nodes (17): handleSubmit(), salvarPerfil(), api, clearToken(), isTokenPersistent(), setToken(), ApiUser, cacheAccount() (+9 more)

### Community 59 - "notify_alert"
Cohesion: 0.20
Nodes (11): get_alert(), list_alerts(), notify_alert(), get, patch, post, Session, Resolve um alerta. Ate a Fase 1 esta rota estava SEM protecao alguma — qualquer… (+3 more)

### Community 60 - "useAppData"
Cohesion: 0.08
Nodes (40): react, ReportsPage(), AppShell(), AuthGate(), Modal(), ModalProps, MustChangePasswordGate(), handleSubmit() (+32 more)

### Community 61 - "Print Server"
Cohesion: 0.22
Nodes (9): `GET /api/servers`, `GET /api/servers/current`, `PATCH /api/servers/{server_id}`, `POST /api/servers`, `POST /api/servers/discover`, `POST /api/servers/{server_id}/discover`, `POST /api/servers/{server_id}/sync`, `POST /api/servers/sync` (+1 more)

### Community 62 - "Fluxo de Dados"
Cohesion: 0.18
Nodes (11): 10. Escanear Rede (implementado), 1. Cadastro no SQLite, 2. Coleta SNMP real, 3. Coleta de frota, 4. Print Server, 5. Sincronização, 6. Alertas, 7. Relatório mensal (+3 more)

### Community 63 - "Arquitetura de Deploy"
Cohesion: 0.20
Nodes (10): Arquitetura avaliada, Arquitetura de Deploy, Autenticação, Bloqueios atuais, Cloudflare Tunnel, Configuração de aplicação, CORS, Estado atual (+2 more)

### Community 64 - "Dívida técnica — registro único"
Cohesion: 0.13
Nodes (15): Como ler, D10 — O frontend não tem nenhum teste automatizado, D11 — O painel cai em dados de demonstração quando a API não responde, D12 — Datas ingênuas no servidor, hora do navegador no cliente, D13 — `/health` existe, mas nada o consulta, D1 — Chave estrangeira órfã para `printers_old`, D2 — Sem migrações de banco versionadas, D3 — SQLite: um escritor por vez, um nó só (+7 more)

### Community 65 - "tests_print_servers.py"
Cohesion: 0.18
Nodes (13): PrintServer, SQLModel, str, Print Server como entidade (Fase 4). Ate aqui um Print Server existia de duas…, Modos aceitos, iguais aos de `settings.print_server_mode`., ServerMode, check(), check_true() (+5 more)

### Community 66 - "Autenticação"
Cohesion: 0.29
Nodes (7): Autenticação, Bloqueio de simulação em produção (Fase 9), `GET /api/auth/me`, `GET /health`, `PATCH /api/auth/me`, `POST /api/auth/change-password`, `POST /api/auth/login`

### Community 67 - "VISAO_GERAL.md"
Cohesion: 0.20
Nodes (3): Matriz de Funcionalidades, Itens que os documentos antigos listavam e que **já não existem**, Resolvido na Fase 10 (24/08/2026)

### Community 68 - "Role"
Cohesion: 0.08
Nodes (34): RBAC minimo (Fase 1). Tres papeis cobrem todas as rotas existentes hoje: -…, Role, _active_admin_count(), create_user(), _ensure_not_last_admin(), list_users(), get, patch (+26 more)

### Community 69 - "tests_printers_crud.py"
Cohesion: 0.33
Nodes (3): Etapa 12 - CRUD de impressoras contra o servidor rodando. Usa o banco REAL,…, Devolve (status, payload)., request()

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

### Community 77 - "7. Roteiro de teste em produção — amanhã"
Cohesion: 0.17
Nodes (12): 7. Roteiro de teste em produção — amanhã, Antes de começar, Como reverter, em ordem de gravidade, Etapa 1 — O backend sobe? *(2 min)*, Etapa 2 — A saúde está boa? *(2 min)*, Etapa 3 — O login funciona? *(3 min)*, Etapa 4 — Os dados são reais? *(5 min)* — **a etapa mais importante**, Etapa 5 — A coleta real funciona? *(5 min)* (+4 more)

### Community 78 - "4. Variáveis de ambiente"
Cohesion: 0.18
Nodes (11): 4. Variáveis de ambiente, As que **obrigam** o backend a recusar subir se estiverem erradas, Banco de dados, Coleta automática, Do frontend (na Vercel, não no `.env` do backend), Logs, Print Server, Segurança do login (+3 more)

### Community 79 - "3. Tudo o que o sistema faz hoje, por área"
Cohesion: 0.20
Nodes (10): 3.1 Autenticação (entrar no sistema), 3.2 Usuários, 3.3 Print Servers, 3.4 Impressoras e coleta, 3.5 Alertas, 3.6 Notificações, 3.7 Perfil e configurações, 3.8 Ambiente demo e produção (+2 more)

### Community 80 - "printer_fleet.py"
Cohesion: 0.26
Nodes (11): collect_fleet(), _collect_ip_network(), FleetCollectionResult, _group_by_ip(), _group_plan(), Printer, Session, Orquestracao da coleta da frota inteira (Etapa 5). Separacao de… (+3 more)

### Community 82 - "cn"
Cohesion: 0.13
Nodes (19): TonerPage(), PrinterDetailsModal(), config, PrinterStatusBadge(), StatCard(), StatCardProps, StatCards(), StatCardsProps (+11 more)

### Community 83 - "RateLimiter"
Cohesion: 0.15
Nodes (10): RateLimiter, Limite de tentativas para o login (Fase 10). POR QUE existe --------------…, Consome credito. So a FALHA conta — login certo nao gasta nada., Zera as contagens apos um login BEM-SUCEDIDO. Sem isto, quem erra a senha…, Esvazia tudo. Existe para os testes; nao ha rota que chegue aqui., Veredito de uma checagem. `retry_after` so faz sentido quando bloqueado., Janela deslizante em memoria, protegida por lock. O lock existe porque o…, Descarta o que saiu da janela e devolve o que restou. (+2 more)

### Community 84 - "6. Subir o sistema em produção hoje"
Cohesion: 0.22
Nodes (9): 6. Subir o sistema em produção hoje, Passo 1 — Preparar o `.env`, Passo 2 — Testar a configuração ANTES de subir, Passo 3 — Definir a senha das contas de administrador, Passo 4 — Backup antes de qualquer coisa, Passo 5 — Subir o backend, Passo 6 — Verificar a saúde, Passo 7 — Subir o painel (+1 more)

### Community 85 - "PrinterTable.tsx"
Cohesion: 0.20
Nodes (10): PrintersPage(), PAGE_SIZE_OPTIONS, PrinterTable(), PrinterTableProps, DEFAULT_FILTERS, filterPrinters(), PrinterFilters, getPrinterType() (+2 more)

### Community 86 - "PrinterControl — Visão geral do sistema"
Cohesion: 0.29
Nodes (7): 1. O que o sistema faz, 8. Onde está o resto da documentação, Como ele descobre isso, O ciclo, em uma frase, O detalhe que explica o relatório mensal, PrinterControl — Visão geral do sistema, Índice

### Community 87 - "5. Modo real x modo simulado, e os riscos"
Cohesion: 0.33
Nodes (6): 5. Modo real x modo simulado, e os riscos, As duas camadas de proteção, Como o sistema decide entre real e simulado, O problema em uma frase, O risco mais grave: sincronizar em modo simulado, Riscos corrigidos na Fase 10 (24/08/2026)

### Community 89 - "8. Dívida técnica conhecida — FK órfã para `printers_old`"
Cohesion: 0.40
Nodes (5): 8. Dívida técnica conhecida — FK órfã para `printers_old`, ⚠️ A armadilha, Como quitar, quando for prioridade, O que é, Por que não incomoda

### Community 90 - "2. Como o sistema é montado"
Cohesion: 0.50
Nodes (4): 2. Como o sistema é montado, O "crachá" (token), O que cada tecnologia é, em uma linha, Por que duas peças, e não uma

### Community 91 - "layout.tsx"
Cohesion: 0.29
Nodes (5): ibmPlexMono, metadata, publicSans, sourceSerif, Providers()

### Community 93 - "tests_printer_fleet.py"
Cohesion: 0.18
Nodes (4): fake_real_collect(), Etapa 5 - orquestracao da frota (printer_fleet.collect_fleet). Roda sobre um…, RecordingThreadPoolExecutor, _OriginalTPE

### Community 94 - "Relatorio-Mensal.ps1"
Cohesion: 0.33
Nodes (3): Modo Real, Contador mensal calculado por diff de duas leituras SNMP acumulativas (não existe OID de páginas do mês), Scripts PowerShell reais nunca rodaram de verdade (sem interpretador PowerShell no ambiente de dev)

### Community 96 - "Login.tsx"
Cohesion: 0.18
Nodes (7): ACTIVE_NODES, features, Login(), LoginProps, NETWORK_LINKS, NETWORK_NODES, ApiError

### Community 97 - "discovery.py"
Cohesion: 0.39
Nodes (8): _empty_result(), EnrichedDiscoveredPrinter, _is_color(), _is_label(), _normalize_ip(), DiscoveredPrinter, Enriquecimento transitório de filas descobertas com telemetria SNMP., _result_for_ip()

### Community 98 - "tests_login_hardening.py"
Cohesion: 0.22
Nodes (6): medir(), Fase 10 - endurecimento do login. Cobre as duas falhas levantadas na auditoria…, Request minimo: so o que _identificar_origem le., Tentativa com a contagem limpa — isola o caso do limite de tentativas., _Req, tentar()

### Community 99 - "Topbar"
Cohesion: 0.20
Nodes (7): DashboardPage(), Topbar(), onExportCsv(), handleAlertSelect(), updateFilter(), exportPrintersCsv(), STATUS_LABEL

### Community 100 - "theme.tsx"
Cohesion: 0.27
Nodes (8): lerPreferencia(), resolver(), sistemaEscuro(), Theme, ThemeContext, ThemeContextValue, ThemePreference, ThemeProvider()

### Community 103 - "_migrate_printer_schema"
Cohesion: 0.29
Nodes (7): _finish_printer_migration(), _migrate_printer_schema(), Caminho do arquivo .db atual, se o banco for SQLite em disco (nao :memory:)., Etapa 4 — reconstroi `printers` para trocar a identidade de `ip UNIQUE` para…, Recria `printers` (schema atual) e copia `printers_old` para dentro dela, numa…, _sqlite_backup_path(), Path

### Community 106 - "require_user"
Cohesion: 0.33
Nodes (6): Session, Usuario dono do JWT do header Authorization. 401 se ausente/invalido. O usuario…, require_user(), decode_token(), Devolve {"email": ...} para um token valido, ou None. `algorithms` e uma lista…, HTTPAuthorizationCredentials

### Community 108 - "Ações"
Cohesion: 0.33
Nodes (6): Acessar via web — PARCIAL, Adicionar impressora — AUSENTE/PARCIAL, Ações, Configurações — COMING SOON, Impressoras — FUNCIONAL/PARCIAL, Imprimir página de teste — SIMULADA

### Community 109 - "ElginLogo.tsx"
Cohesion: 0.40
Nodes (4): Logo Elgin é redesenho à mão (IA sem acesso a imagens coladas no chat, só uploads), src/components/ (padrão com header-comment por arquivo), ElginLogo(), ElginLogoProps

## Knowledge Gaps
- **362 isolated node(s):** `LoginProps`, `features`, `NETWORK_NODES`, `NETWORK_LINKS`, `ACTIVE_NODES` (+357 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SNMPClient` connect `SNMPClient` to `discovery.py`, `PrinterCollector`, `enrich_discovered_printers`, `MockSNMPClient`, `printer_fleet.py`, `Printer`, `tests_printer_fleet.py`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Why does `User` connect `User` to `tests_print_servers.py`, `create_notifications`, `Role`, `servers.py`, `scheduler.py`, `require_user`, `database.py`, `tests_rbac.py`, `tests_uptime.py`, `create_db_and_tables`, `Printer`, `notify_alert`, `schemas/printer.py`, `login`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Why does `SNMPResult` connect `SNMPResult` to `snmp_fleet_mock.py`, `discovery.py`, `PrinterCollector`, `SNMPClient`, `enrich_discovered_printers`, `MockSNMPClient`, `printer_fleet.py`, `Printer`, `tests_printer_fleet.py`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **Are the 39 inferred relationships involving `User` (e.g. with `require_active_user()` and `require_roles()`) actually correct?**
  _`User` has 39 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `SNMPClient` (e.g. with `PrinterCollector` and `FakeAgent`) actually correct?**
  _`SNMPClient` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `Printer` (e.g. with `collect_fleet()` and `create_printer()`) actually correct?**
  _`Printer` has 12 INFERRED edges - model-reasoned connections that need verification._
- **What connects `LoginProps`, `features`, `NETWORK_NODES` to the rest of the system?**
  _362 weakly-connected nodes found - possible documentation gaps or missing edges._