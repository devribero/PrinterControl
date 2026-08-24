# Graph Report - PrinterControl  (2026-08-24)

## Corpus Check
- 158 files · ~131,393 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1598 nodes · 3259 edges · 94 communities (83 shown, 11 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 137 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1948a998`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- snmp_fleet_mock.py
- package.json
- Main.ps1
- Elgin Impressoras (painel de monitoramento)
- hash_password
- Coletar-Impressoras.ps1
- compilerOptions
- servers.py
- Printer
- PrinterCollector
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
- cn
- unhandled_exception_handler
- tests_collect_api.py
- Cloudflare Tunnel — expor a API sem abrir porta (Fase 11)
- alert_engine.py
- schemas/printer.py
- routes/auth.py
- Operação em Produção
- Deploy do Frontend na Vercel (Fase 12)
- printer_sync.py
- layout.tsx
- User
- notifications.py
- collect_printer
- SNMPClient
- enrich_discovered_printers
- NetworkView.tsx
- Simular-Ambiente.ps1
- main.py
- PrintServerCreate
- printers.ts
- printers.py
- PLANO DE IMPLEMENTAÇÃO — ESCANEAR REDE REAL
- services/print_server.py
- Impressoras
- Guia de Uso do PrinterControl
- tests_rbac.py
- app-data.tsx
- tests_print_server_discovery.py
- UsersView.tsx
- Guia do Desenvolvedor
- api.ts
- database.py
- Settings
- SNMPResult
- auth.ts
- Relatorio-Mensal.ps1
- useAppData
- Print Server
- Fluxo de Dados
- Arquitetura de Deploy
- Dívida técnica — registro único
- tests_print_servers.py
- Autenticação
- VISAO_GERAL.md
- Role
- Ações
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
- _Req
- types.ts
- RateLimiter
- 6. Subir o sistema em produção hoje
- fetchPrinters.ts
- PrinterControl — Visão geral do sistema
- 5. Modo real x modo simulado, e os riscos
- ambiente
- 2. Como o sistema é montado
- tests_printer_fleet.py
- tests_environment.py
- theme.tsx
- dependencies.py

## God Nodes (most connected - your core abstractions)
1. `User` - 69 edges
2. `Printer` - 50 edges
3. `cn()` - 39 edges
4. `SNMPClient` - 37 edges
5. `useAppData()` - 35 edges
6. `SNMPResult` - 34 edges
7. `create_db_and_tables()` - 30 edges
8. `useToast()` - 29 edges
9. `Role` - 27 edges
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

## Communities (94 total, 11 thin omitted)

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
Cohesion: 0.09
Nodes (22): Tela Alertas, Tela Dashboard, Elgin Impressoras (painel de monitoramento), Tela Histórico, Tela Impressoras, Tela Login, Migração futura para FastAPI (Python) + Next.js + banco de dados, Modo claro/escuro (toggle) (+14 more)

### Community 4 - "hash_password"
Cohesion: 0.24
Nodes (12): hash_password(), check(), check_true(), h(), main(), Fase 7 - Notificacoes internas. Como…, check(), check_true() (+4 more)

### Community 5 - "Coletar-Impressoras.ps1"
Cohesion: 0.21
Nodes (13): Build-SnmpGet(), Build-SnmpGetBulk(), Convert-SnmpValueBytes(), Get-ImpressorasServidor(), Get-TonerSNMP(), Parse-SnmpBulkResponse(), Parse-SnmpCounter(), Parse-SnmpInt() (+5 more)

### Community 6 - "compilerOptions"
Cohesion: 0.06
Nodes (30): dom, dom.iterable, esnext, .next/dev/types/**/*.ts, next-env.d.ts, .next/types/**/*.ts, node_modules, **/*.ts (+22 more)

### Community 7 - "servers.py"
Cohesion: 0.11
Nodes (37): create_server(), discover(), discover_server(), DiscoveredPrinterResponse, DiscoverResponse, _executar_discover(), get_current_server(), _get_or_404() (+29 more)

### Community 8 - "Printer"
Cohesion: 0.19
Nodes (19): Printer, PrinterReading, SQLModel, Etapa 4: identidade e (server, name), NAO ip — o Print Server permite varias…, create_printer(), create_printer_reading(), get_printer(), get_printer_readings() (+11 more)

### Community 9 - "PrinterCollector"
Cohesion: 0.10
Nodes (15): PrinterCollector, Orquestrador da coleta de impressoras. Separa as tres responsabilidades da…, Cenarios de teste disponiveis (fonte unica: snmp_mock.SCENARIOS)., Coleta uma impressora e grava o resultado como PrinterReading., Args: mode: "real" (SNMP de verdade), "mock" (cenario fixo) ou "fleet" (frota…, MockSNMPClient, Substituto do SNMPClient com a mesma assinatura de collect()., Devolve o resultado fixo do cenario (ip e is_color sao ignorados). (+7 more)

### Community 10 - "plugins"
Cohesion: 0.22
Nodes (8): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, typescript, warn

### Community 11 - "HistoryMatrix.tsx"
Cohesion: 0.33
Nodes (4): HistoryMatrix(), HistoryMatrixProps, getDepartmentLabel(), getPrinterSite()

### Community 12 - "graphify (knowledge graph tool)"
Cohesion: 0.25
Nodes (8): graphify (knowledge graph tool), graphify explain command, graphify path command, graphify query command, graphify update command, graphify-out/graph.json, graphify-out/GRAPH_REPORT.md, graphify-out/wiki/index.md

### Community 20 - "cn"
Cohesion: 0.06
Nodes (40): Logo Elgin é redesenho à mão (IA sem acesso a imagens coladas no chat, só uploads), AlertsPage(), DashboardPage(), AlertBanner(), AlertBannerProps, AlertsView(), AlertsViewProps, AlertsDonutCard() (+32 more)

### Community 21 - "unhandled_exception_handler"
Cohesion: 0.40
Nodes (5): Exception, Request, Erro nao tratado: o detalhe vai para o log do servidor, o cliente recebe apenas…, unhandled_exception_handler(), exception_handler

### Community 22 - "tests_collect_api.py"
Cohesion: 0.67
Nodes (3): check(), main(), Teste ponta a ponta dos endpoints /api/collect com os cenarios simulados.…

### Community 23 - "Cloudflare Tunnel — expor a API sem abrir porta (Fase 11)"
Cohesion: 0.13
Nodes (15): 10. Resumo do que muda em cada lugar, 1. Instalar o `cloudflared`, 2. Criar o túnel — caminho recomendado (via painel, com token), 3. Apontar o hostname para o backend, 4. Validar antes de seguir, 5. Confirmar que o serviço sobe sozinho, 6. Cabeçalhos de segurança — no Cloudflare, não no backend, 7. CORS — o que falta até a Vercel existir (Fase 12) (+7 more)

### Community 25 - "alert_engine.py"
Cohesion: 0.36
Nodes (8): Alert, _active(), evaluate_reading(), Session, Alertas automaticos (Etapa 8A). Roda logo apos cada PrinterReading ser…, Cria, mantem ou resolve o alerta de uma condicao. Retorna a acao tomada., Avalia uma leitura e sincroniza os alertas da impressora. Faz commit ao final.…, _sync_condition()

### Community 28 - "schemas/printer.py"
Cohesion: 0.14
Nodes (16): Config, PrinterCreate, PrinterReadingCreate, PrinterReadingResponse, PrinterResponse, PrinterUpdate, PrinterWithStatus, BaseModel (+8 more)

### Community 29 - "routes/auth.py"
Cohesion: 0.09
Nodes (30): change_own_password(), _identificar_origem(), login(), patch, post, Request, Session, Perfil da PROPRIA conta (Fase 8). So o nome. `require_active_user` (nao… (+22 more)

### Community 30 - "Operação em Produção"
Cohesion: 0.11
Nodes (18): 1. Antes do primeiro deploy, 2. Instalar, 3. Dia a dia, 4. Diagnóstico, 5. Backup, 6. Recuperação — o que acontece se o processo cair, 7. Problemas comuns, 8. Dívida técnica conhecida — FK órfã para `printers_old` (+10 more)

### Community 31 - "Deploy do Frontend na Vercel (Fase 12)"
Cohesion: 0.25
Nodes (8): 1. O projeto já está pronto para este deploy, 2. Variáveis de ambiente para configurar na Vercel, 3. Conectar o repositório e fazer o primeiro deploy, 4. Validar, 5. Depois do deploy — atualizar o CORS do backend, 6. Redeploy — quando o código mudar, 7. Resumo do que fica pendente até alguém com acesso executar, Deploy do Frontend na Vercel (Fase 12)

### Community 32 - "printer_sync.py"
Cohesion: 0.20
Nodes (11): obter_modelo(), obter_tipo_impressora(), Regras de classificacao portadas do Main.ps1 (Etapa 4). Correspondencia exata:…, Traduz DriverName (Windows) em nome comercial, igual ao Main.ps1., Classifica A4 / Etiqueta / Portatil a partir de Nome+Modelo, igual ao Main.ps1., Session, Sincronizacao Print Server -> banco (Etapa 4). Print Server ->…, Executa um ciclo completo de sincronizacao para UM Print Server. Ja era… (+3 more)

### Community 33 - "layout.tsx"
Cohesion: 0.29
Nodes (5): ibmPlexMono, metadata, publicSans, sourceSerif, Providers()

### Community 34 - "User"
Cohesion: 0.19
Nodes (15): True se o papel do usuario satisfaz qualquer um dos exigidos., User, get, Conta autenticada e seu papel — usado para decidir o que exibir/permitir., read_current_user(), patch, update_printer(), check() (+7 more)

### Community 35 - "notifications.py"
Cohesion: 0.10
Nodes (31): Notification, SQLModel, Notificacoes internas (Fase 7). Por que uma tabela separada de `alerts`…, AlertRef, create_notifications(), list_notifications(), mark_all_as_read(), mark_as_read() (+23 more)

### Community 36 - "collect_printer"
Cohesion: 0.27
Nodes (10): collect_fleet(), collect_printer(), CollectRequest, CollectResponse, FleetCollectResponse, BaseModel, post, Session (+2 more)

### Community 37 - "SNMPClient"
Cohesion: 0.05
Nodes (35): parse_varbinds(), Decodifica um OID BER para notacao pontuada., Decodifica bytes BER como inteiro sem sinal., Extrai a lista de varbinds de uma resposta SNMP. Percorre a estrutura completa…, Cliente SNMP para coleta de impressoras (Printer-MIB, RFC 3805)., Coleta status, contador de paginas e toners de uma impressora. Nunca levanta…, PS1: `if ($ip -match '^\\d')` — descarta 'N/A' e nomes de porta., ICMP ping, equivalente ao `New-Object ...Ping).Send($ip, 400)` do PS1. SNMP… (+27 more)

### Community 38 - "enrich_discovered_printers"
Cohesion: 0.24
Nodes (9): enrich_discovered_printers(), Enriquece filas em memória; não recebe nem acessa uma sessão SQL., Nivel de um consumivel de toner., TonerInfo, DiscoverySnmpTests, printer(), DiscoveredPrinter, Testes locais do enriquecimento SNMP, sem rede corporativa ou SQLite. (+1 more)

### Community 39 - "NetworkView.tsx"
Cohesion: 0.09
Nodes (27): DiscoveryResults(), DiscoveryResultsProps, statusLabel(), adaptDiscovered(), FORM_VAZIO, formatarMomento(), MODOS, NetworkView() (+19 more)

### Community 40 - "Simular-Ambiente.ps1"
Cohesion: 0.22
Nodes (5): Modo Simulado, public/data/monthly-report.json, public/data/printers.json, Arquivos de dados gerados são ignorados pelo git — gerar/apagar localmente nunca afeta o repositório, Impressoras simuladas usam prefixo SIM_ / departamentos TESTE - de propósito, pra nunca confundir com dado real

### Community 41 - "main.py"
Cohesion: 0.08
Nodes (31): AsyncIOScheduler, _caminho_do_log(), Path, Configuracao de log (Fase 10). Por que existe como modulo, e nao como um…, Substitui valores sensiveis na mensagem antes de ela ser emitida. Fica no…, Resolve settings.log_file. Vazio = so console., Instala console + arquivo rotativo na raiz do logging. Idempotente: chamar duas…, RedactSecretsFilter (+23 more)

### Community 42 - "PrintServerCreate"
Cohesion: 0.28
Nodes (5): PrintServerCreate, PrintServerUpdate, field_validator, `host` fica de fora de proposito: ele e a chave natural que aparece em…, Recusa no cadastro o que a camada de execucao ja recusaria. O host e…

### Community 43 - "printers.ts"
Cohesion: 0.12
Nodes (16): Levantamento_impressões (planilha original), DecommissionedList(), DecommissionedListProps, DepartmentBreakdown(), DepartmentBreakdownProps, MONTHS, Topbar(), onExportCsv() (+8 more)

### Community 44 - "printers.py"
Cohesion: 0.08
Nodes (32): `require_user` + bloqueio de conta com troca de senha pendente. Toda rota do…, require_active_user(), Alert, SQLModel, TonerHistory, PrinterMonthly, SQLModel, get_alert() (+24 more)

### Community 45 - "PLANO DE IMPLEMENTAÇÃO — ESCANEAR REDE REAL"
Cohesion: 0.05
Nodes (39): A. Endpoint (implementado), Alertas, Arquitetura atual, Arquitetura do PrinterControl, B. Service reutilizável, Banco, C. Funções Print Server reutilizáveis, Cliente de API (+31 more)

### Community 46 - "services/print_server.py"
Cohesion: 0.14
Nodes (20): discover_printers(), DiscoveredPrinter, _escapar_powershell(), _mock_discover(), PrintServerError, Exception, Camada de Print Server (Etapa 3). Reproduz a descoberta de impressoras do…, Uma linha do que Get-Printer + Get-PrinterPort devolveriam, combinadas. (+12 more)

### Community 47 - "Impressoras"
Cohesion: 0.22
Nodes (9): `GET /api/printers`, `GET /api/printers/monthly-report`, `GET /api/printers/{printer_id}`, `GET /api/printers/{printer_id}/readings`, `GET /api/printers/with-status`, Impressoras, `PATCH /api/printers/{printer_id}`, `POST /api/printers` (+1 more)

### Community 48 - "Guia de Uso do PrinterControl"
Cohesion: 0.13
Nodes (14): Alertas — FUNCIONAL na leitura; PARCIAL nas ações, Como acessar, Configurações, Usuários e Integrações — COMING SOON, Dashboard — FUNCIONAL/PARCIAL, Exportar CSV — FUNCIONAL, Guia de Uso do PrinterControl, Histórico — PARCIAL, Interpretação dos dados (+6 more)

### Community 49 - "tests_rbac.py"
Cohesion: 0.24
Nodes (12): check(), check_true(), _confere_rbac_do_frontend(), h(), main(), Fase 1 - Autenticacao, RBAC e protecao das rotas. Diferente dos demais…, O frontend tem a sua propria copia da hierarquia de papeis, em…, Cria um banco no formato ANTERIOR a Fase 1 (users sem role/is_active), roda a… (+4 more)

### Community 50 - "app-data.tsx"
Cohesion: 0.12
Nodes (28): handleSubmit(), validar(), decommissionedPrinters, monthlyUsage, adaptAlert(), loadMonthlyReportFromApi(), BackendEnvironment, discoverPrinters() (+20 more)

### Community 52 - "UsersView.tsx"
Cohesion: 0.10
Nodes (21): ComingSoon(), ComingSoonProps, RequireRole(), FORM_VAZIO, formatarData(), FormState, UsersView(), abrirEdicao() (+13 more)

### Community 53 - "Guia do Desenvolvedor"
Cohesion: 0.13
Nodes (15): Backend, Banco, Comandos do frontend, Escanear Rede (implementado), Guia do Desenvolvedor, Já resolvido — não reabra, O que não executar em produção sem autorização, Print Server (+7 more)

### Community 54 - "api.ts"
Cohesion: 0.06
Nodes (46): FORM_VAZIO, formatarMomento(), FormState, ICONE_SEVERIDADE, NotificationsView(), abrirEnvio(), enviar(), marcarComoLida() (+38 more)

### Community 55 - "database.py"
Cohesion: 0.08
Nodes (30): create_db_and_tables(), _finish_printer_migration(), _migrate_alert_type(), _migrate_print_servers(), _migrate_printer_schema(), _migrate_reading_uptime(), _migrate_user_login_fields(), _migrate_user_rbac() (+22 more)

### Community 56 - "Settings"
Cohesion: 0.08
Nodes (17): Config, field_validator, Fail-fast: producao nao sobe com simulacao ligada (Fase 9). O risco concreto e…, Impede que um ambiente de producao suba silenciosamente com o secret de…, Aceita "https://a.com, https://b.com" alem da lista JSON. Sem isto,…, Producao exige origens proprias e explicitas (Fase 10). Tres recusas, todas por…, Normaliza um DATABASE_URL sqlite relativo (ex.: sqlite:///./x.db) para um…, Um ambiente escrito errado nao pode cair no default em silencio:… (+9 more)

### Community 57 - "SNMPResult"
Cohesion: 0.10
Nodes (24): _empty_result(), EnrichedDiscoveredPrinter, _is_color(), _is_label(), _normalize_ip(), DiscoveredPrinter, Enriquecimento transitório de filas descobertas com telemetria SNMP., _result_for_ip() (+16 more)

### Community 58 - "auth.ts"
Cohesion: 0.11
Nodes (27): ACTIVE_NODES, features, Login(), handleSubmit(), LoginProps, NETWORK_LINKS, NETWORK_NODES, salvarPerfil() (+19 more)

### Community 59 - "Relatorio-Mensal.ps1"
Cohesion: 0.33
Nodes (3): Modo Real, Contador mensal calculado por diff de duas leituras SNMP acumulativas (não existe OID de páginas do mês), Scripts PowerShell reais nunca rodaram de verdade (sem interpretador PowerShell no ambiente de dev)

### Community 60 - "useAppData"
Cohesion: 0.10
Nodes (29): HistoryPage(), PrintersPage(), ReportsPage(), AppShell(), AuthGate(), MustChangePasswordGate(), SettingsView(), trocarSenha() (+21 more)

### Community 61 - "Print Server"
Cohesion: 0.22
Nodes (9): `GET /api/servers`, `GET /api/servers/current`, `PATCH /api/servers/{server_id}`, `POST /api/servers`, `POST /api/servers/discover`, `POST /api/servers/{server_id}/discover`, `POST /api/servers/{server_id}/sync`, `POST /api/servers/sync` (+1 more)

### Community 62 - "Fluxo de Dados"
Cohesion: 0.17
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
Cohesion: 0.32
Nodes (3): Matriz de Funcionalidades, Itens que os documentos antigos listavam e que **já não existem**, Resolvido na Fase 10 (24/08/2026)

### Community 68 - "Role"
Cohesion: 0.13
Nodes (23): str, RBAC minimo (Fase 1). Tres papeis cobrem todas as rotas existentes hoje: -…, Role, _active_admin_count(), create_user(), _ensure_not_last_admin(), list_users(), get (+15 more)

### Community 69 - "Ações"
Cohesion: 0.33
Nodes (6): Acessar via web — PARCIAL, Adicionar impressora — AUSENTE/PARCIAL, Ações, Configurações — COMING SOON, Impressoras — FUNCIONAL/PARCIAL, Imprimir página de teste — SIMULADA

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
Cohesion: 0.12
Nodes (19): Printer, Session, Converte SNMPResult em PrinterReading. Toner ausente vira NULL (a coluna e…, Deduz se a impressora e colorida a partir do modelo/nome (regra do PS1)., Etiquetadora/portatil: sem Printer-MIB, o PS1 nem consulta SNMP., Coleta uma impressora e persiste a leitura. Args: printer_id: id da impressora…, collect_fleet(), _collect_ip_network() (+11 more)

### Community 82 - "types.ts"
Cohesion: 0.07
Nodes (42): react, TonerPage(), Modal(), ModalProps, PrinterDetailsModal(), PrinterDetailsModalProps, PrinterRanking(), PrinterRankingProps (+34 more)

### Community 83 - "RateLimiter"
Cohesion: 0.16
Nodes (9): RateLimiter, Consome credito. So a FALHA conta — login certo nao gasta nada., Zera as contagens apos um login BEM-SUCEDIDO. Sem isto, quem erra a senha…, Esvazia tudo. Existe para os testes; nao ha rota que chegue aqui., Veredito de uma checagem. `retry_after` so faz sentido quando bloqueado., Janela deslizante em memoria, protegida por lock. O lock existe porque o…, Descarta o que saiu da janela e devolve o que restou., Diz se a tentativa deve ser recusada — sem consumir credito. Separado de… (+1 more)

### Community 84 - "6. Subir o sistema em produção hoje"
Cohesion: 0.22
Nodes (9): 6. Subir o sistema em produção hoje, Passo 1 — Preparar o `.env`, Passo 2 — Testar a configuração ANTES de subir, Passo 3 — Definir a senha das contas de administrador, Passo 4 — Backup antes de qualquer coisa, Passo 5 — Subir o backend, Passo 6 — Verificar a saúde, Passo 7 — Subir o painel (+1 more)

### Community 86 - "PrinterControl — Visão geral do sistema"
Cohesion: 0.29
Nodes (7): 1. O que o sistema faz, 8. Onde está o resto da documentação, Como ele descobre isso, O ciclo, em uma frase, O detalhe que explica o relatório mensal, PrinterControl — Visão geral do sistema, Índice

### Community 87 - "5. Modo real x modo simulado, e os riscos"
Cohesion: 0.33
Nodes (6): 5. Modo real x modo simulado, e os riscos, As duas camadas de proteção, Como o sistema decide entre real e simulado, O problema em uma frase, O risco mais grave: sincronizar em modo simulado, Riscos corrigidos na Fase 10 (24/08/2026)

### Community 90 - "2. Como o sistema é montado"
Cohesion: 0.50
Nodes (4): 2. Como o sistema é montado, O "crachá" (token), O que cada tecnologia é, em uma linha, Por que duas peças, e não uma

### Community 93 - "tests_printer_fleet.py"
Cohesion: 0.18
Nodes (4): fake_real_collect(), Etapa 5 - orquestracao da frota (printer_fleet.collect_fleet). Roda sobre um…, RecordingThreadPoolExecutor, _OriginalTPE

### Community 98 - "tests_environment.py"
Cohesion: 0.15
Nodes (6): Limite de tentativas para o login (Fase 10). POR QUE existe --------------…, Fase 9 - Mock e Demo Seguros. Cobre as DUAS camadas que protegem o risco…, medir(), Fase 10 - endurecimento do login. Cobre as duas falhas levantadas na auditoria…, Tentativa com a contagem limpa — isola o caso do limite de tentativas., tentar()

### Community 100 - "theme.tsx"
Cohesion: 0.27
Nodes (8): lerPreferencia(), resolver(), sistemaEscuro(), Theme, ThemeContext, ThemeContextValue, ThemePreference, ThemeProvider()

### Community 106 - "dependencies.py"
Cohesion: 0.20
Nodes (10): get_session(), Session, Dependencias compartilhadas pelas rotas. Autorizacao (Fase 1) fica CENTRALIZADA…, Fabrica de dependencia: exige que o usuario tenha (ou herde) um dos papeis…, Usuario dono do JWT do header Authorization. 401 se ausente/invalido. O usuario…, require_roles(), require_user(), decode_token() (+2 more)

## Knowledge Gaps
- **379 isolated node(s):** `$schema`, `typescript`, `oxc`, `react/rules-of-hooks`, `warn` (+374 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `tests_print_servers.py`, `tests_environment.py`, `notifications.py`, `collect_printer`, `Role`, `hash_password`, `servers.py`, `Printer`, `main.py`, `dependencies.py`, `printers.py`, `tests_rbac.py`, `database.py`, `routes/auth.py`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Why does `SNMPClient` connect `SNMPClient` to `enrich_discovered_printers`, `PrinterCollector`, `printer_fleet.py`, `SNMPResult`, `tests_printer_fleet.py`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Why does `Printer` connect `Printer` to `printer_sync.py`, `tests_print_servers.py`, `User`, `tests_environment.py`, `collect_printer`, `hash_password`, `servers.py`, `main.py`, `PrinterCollector`, `printers.py`, `printer_fleet.py`, `tests_rbac.py`, `database.py`, `alert_engine.py`, `tests_printer_fleet.py`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Are the 39 inferred relationships involving `User` (e.g. with `require_active_user()` and `require_roles()`) actually correct?**
  _`User` has 39 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `Printer` (e.g. with `_finish_printer_migration()` and `notify_alert()`) actually correct?**
  _`Printer` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `SNMPClient` (e.g. with `PrinterCollector` and `FakeAgent`) actually correct?**
  _`SNMPClient` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `typescript`, `oxc` to the rest of the system?**
  _379 weakly-connected nodes found - possible documentation gaps or missing edges._