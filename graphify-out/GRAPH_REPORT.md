# Graph Report - PrinterControl  (2026-08-24)

## Corpus Check
- 155 files · ~128,272 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1594 nodes · 3232 edges · 95 communities (84 shown, 11 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 134 edges (avg confidence: 0.51)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `879be279`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- tests_fleet.py
- package.json
- Main.ps1
- Elgin Impressoras (painel de monitoramento)
- api.ts
- adaptApi.ts
- compilerOptions
- create_server
- Printer
- config.py
- plugins
- Printer
- graphify (knowledge graph tool)
- next.config.ts
- Elgin (Brand)
- NetworkView.tsx
- npm run build
- npm run dev
- next-env.d.ts
- navIds.ts
- theme.tsx
- unhandled_exception_handler
- tests_collect_api.py
- Cloudflare Tunnel — expor a API sem abrir porta (Fase 11)
- alert_engine.py
- schemas/printer.py
- routes/auth.py
- Operação em Produção
- Deploy do Frontend na Vercel (Fase 12)
- types.ts
- layout.tsx
- User
- notifications.py
- servers.py
- snmp.py
- SNMPClient
- 1. Desenvolvimento (local)
- enrich_discovered_printers
- main.py
- FakeAgent
- cn
- Alert
- PLANO DE IMPLEMENTAÇÃO — ESCANEAR REDE REAL
- services/print_server.py
- Impressoras
- Guia de Uso do PrinterControl
- Login.tsx
- app-data.tsx
- UsersView
- useAppData
- Guia do Desenvolvedor
- NotificationsView.tsx
- hash_password
- Settings
- SNMPResult
- auth.ts
- Contador mensal calculado por diff de duas leituras SNMP acumulativas (não existe OID de páginas do mês)
- SettingsView.tsx
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
- PrinterCollector
- _Req
- PrinterTable.tsx
- ._limpar
- 6. Subir o sistema em produção hoje
- integrations/page.tsx
- PrinterControl — Visão geral do sistema
- 5. Modo real x modo simulado, e os riscos
- ambiente
- require_user
- 2. Como o sistema é montado
- public/data/monthly-report.json
- Scripts PowerShell reais nunca rodaram de verdade (sem interpretador PowerShell no ambiente de dev)
- tests_printer_fleet.py
- database.py

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

## Communities (95 total, 11 thin omitted)

### Community 0 - "tests_fleet.py"
Cohesion: 0.14
Nodes (13): _base_page_count(), _increment(), profile_for(), Simulador de frota — APENAS PARA TESTE LOCAL. Diferenca para snmp_mock.py: la…, Perfil deterministico da impressora: online | offline | snmp_mudo | baixo |…, Contador inicial plausivel para uma impressora que nunca foi lida., Paginas impressas entre duas coletas — fixo por impressora, 5 a 124., Nivel do toner: base do perfil + desvio deterministico por impressora/cor,… (+5 more)

### Community 1 - "package.json"
Cohesion: 0.06
Nodes (31): lucide-react, next, oxlint, dependencies, lucide-react, next, react, react-dom (+23 more)

### Community 2 - "Main.ps1"
Cohesion: 0.13
Nodes (29): Atualizar-ImpressorasAsync(), Build-ListaExibicaoAgrupada(), Build-SnmpGet(), Build-SnmpGetBulk(), Convert-SnmpValueBytes(), Get-ImpressorasEmpresa(), Get-TonerSNMP(), Import-Tabela() (+21 more)

### Community 3 - "Elgin Impressoras (painel de monitoramento)"
Cohesion: 0.08
Nodes (24): Tela Alertas, Tela Dashboard, Elgin Impressoras (painel de monitoramento), Tela Histórico, Tela Impressoras, Tela Login, Migração futura para FastAPI (Python) + Next.js + banco de dados, Modo claro/escuro (toggle) (+16 more)

### Community 4 - "api.ts"
Cohesion: 0.11
Nodes (14): ApiDiscoveredPrinter, ApiDiscoveredToner, ApiError, ApiNotificationAlertRef, ApiPrinterReading, apiRequest(), describeDetail(), NotificationCreateInput (+6 more)

### Community 5 - "adaptApi.ts"
Cohesion: 0.13
Nodes (19): adaptAlert(), adaptPrinter(), ApiMonthlyReport, formatLastSeen(), loadMonthlyReportFromApi(), toStatus(), toToner(), VALID_COLORS (+11 more)

### Community 6 - "compilerOptions"
Cohesion: 0.06
Nodes (30): dom, dom.iterable, esnext, .next/dev/types/**/*.ts, next-env.d.ts, .next/types/**/*.ts, node_modules, **/*.ts (+22 more)

### Community 7 - "create_server"
Cohesion: 0.08
Nodes (36): create_server(), discover(), discover_server(), DiscoveredPrinterResponse, DiscoverResponse, _executar_discover(), get_current_server(), _get_or_404() (+28 more)

### Community 8 - "Printer"
Cohesion: 0.21
Nodes (19): Printer, Etapa 4: identidade e (server, name), NAO ip — o Print Server permite varias…, create_printer(), create_printer_reading(), get_printer(), get_printer_readings(), _inicio_da_janela(), list_printers() (+11 more)

### Community 9 - "config.py"
Cohesion: 0.08
Nodes (16): create_access_token(), Hash de senha e emissao/validacao do JWT. POR QUE PyJWT E NAO python-jose (Fase…, RateLimiter, Limite de tentativas para o login (Fase 10). POR QUE existe --------------…, Esvazia tudo. Existe para os testes; nao ha rota que chegue aqui., Janela deslizante em memoria, protegida por lock. O lock existe porque o…, Notificacao de alerta critico via webhook (Etapa 6). Equivalente a Send-…, Fase 9 - Mock e Demo Seguros. Cobre as DUAS camadas que protegem o risco… (+8 more)

### Community 10 - "plugins"
Cohesion: 0.22
Nodes (8): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, typescript, warn

### Community 11 - "Printer"
Cohesion: 0.16
Nodes (12): HistoryPage(), HistoryMatrix(), HistoryMatrixProps, PrinterDetailsModalProps, PrinterRanking(), PrinterRankingProps, RankedPrinter, RankList() (+4 more)

### Community 12 - "graphify (knowledge graph tool)"
Cohesion: 0.25
Nodes (8): graphify (knowledge graph tool), graphify explain command, graphify path command, graphify query command, graphify update command, graphify-out/graph.json, graphify-out/GRAPH_REPORT.md, graphify-out/wiki/index.md

### Community 15 - "NetworkView.tsx"
Cohesion: 0.10
Nodes (25): adaptDiscovered(), FORM_VAZIO, formatarMomento(), MODOS, NetworkView(), confirmarAtivacao(), executarDescoberta(), executarSync() (+17 more)

### Community 20 - "theme.tsx"
Cohesion: 0.11
Nodes (23): AlertsDonutCard(), AlertsDonutCardProps, PagesConsumedCard(), TotalPrintsCard(), NavItem(), NavItemProps, Sidebar(), SidebarProps (+15 more)

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
Cohesion: 0.19
Nodes (14): Alert, _active(), evaluate_reading(), Session, Alertas automaticos (Etapa 8A). Roda logo apos cada PrinterReading ser…, Cria, mantem ou resolve o alerta de uma condicao. Retorna a acao tomada., Avalia uma leitura e sincroniza os alertas da impressora. Faz commit ao final.…, _sync_condition() (+6 more)

### Community 28 - "schemas/printer.py"
Cohesion: 0.14
Nodes (16): Config, PrinterCreate, PrinterReadingCreate, PrinterReadingResponse, PrinterResponse, PrinterUpdate, PrinterWithStatus, BaseModel (+8 more)

### Community 29 - "routes/auth.py"
Cohesion: 0.09
Nodes (30): change_own_password(), _identificar_origem(), login(), get, patch, post, Request, Session (+22 more)

### Community 30 - "Operação em Produção"
Cohesion: 0.11
Nodes (18): 1. Antes do primeiro deploy, 2. Instalar, 3. Dia a dia, 4. Diagnóstico, 5. Backup, 6. Recuperação — o que acontece se o processo cair, 7. Problemas comuns, 8. Dívida técnica conhecida — FK órfã para `printers_old` (+10 more)

### Community 31 - "Deploy do Frontend na Vercel (Fase 12)"
Cohesion: 0.25
Nodes (8): 1. O projeto já está pronto para este deploy, 2. Variáveis de ambiente para configurar na Vercel, 3. Conectar o repositório e fazer o primeiro deploy, 4. Validar, 5. Depois do deploy — atualizar o CORS do backend, 6. Redeploy — quando o código mudar, 7. Resumo — Fase 12 concluída, Deploy do Frontend na Vercel (Fase 12)

### Community 32 - "types.ts"
Cohesion: 0.10
Nodes (22): Levantamento_impressões (planilha original), BottomChartsProps, DecommissionedList(), DecommissionedListProps, DemoDataBadge(), DemoDataBadgeProps, DepartmentBreakdown(), DepartmentBreakdownProps (+14 more)

### Community 33 - "layout.tsx"
Cohesion: 0.29
Nodes (5): ibmPlexMono, metadata, publicSans, sourceSerif, Providers()

### Community 34 - "User"
Cohesion: 0.24
Nodes (13): Fabrica de dependencia: exige que o usuario tenha (ou herde) um dos papeis…, require_roles(), True se o papel do usuario satisfaz qualquer um dos exigidos., User, verify_password(), check(), check_true(), h() (+5 more)

### Community 35 - "notifications.py"
Cohesion: 0.10
Nodes (31): Notification, SQLModel, Notificacoes internas (Fase 7). Por que uma tabela separada de `alerts`…, AlertRef, create_notifications(), list_notifications(), mark_all_as_read(), mark_as_read() (+23 more)

### Community 36 - "servers.py"
Cohesion: 0.16
Nodes (19): collect_fleet(), collect_printer(), CollectRequest, CollectResponse, FleetCollectResponse, BaseModel, post, Session (+11 more)

### Community 37 - "snmp.py"
Cohesion: 0.11
Nodes (21): parse_varbinds(), SNMP Collector para impressoras. Porte direto da funcao Get-TonerSNMP de…, Decodifica um OID BER para notacao pontuada., Decodifica bytes BER como inteiro sem sinal., Extrai a lista de varbinds de uma resposta SNMP. Percorre a estrutura completa…, Retorna (candidatos, houve_resposta_snmp)., GETBULK das tres colunas de uma vez (PS1: Build-SnmpGetBulk)., Fallback: um GET por indice (PS1: laco 1..20 com 3 falhas seguidas). (+13 more)

### Community 38 - "SNMPClient"
Cohesion: 0.14
Nodes (10): Cliente SNMP para coleta de impressoras (Printer-MIB, RFC 3805)., Coleta status, contador de paginas e toners de uma impressora. Nunca levanta…, PS1: `if ($ip -match '^\\d')` — descarta 'N/A' e nomes de porta., ICMP ping, equivalente ao `New-Object ...Ping).Send($ip, 400)` do PS1. SNMP…, Escolhe os toners finais. PS1 colorida: um por cor (primeiro de cada grupo),…, Cor pela descricao; se nao identificar e for colorida, usa indice % 4., SNMPv1 GET (PS1: Build-SnmpGet, version 0, PDU 0xA0)., SNMPv2c GETBULK (PS1: Build-SnmpGetBulk, version 1, PDU 0xA5). (+2 more)

### Community 39 - "1. Desenvolvimento (local)"
Cohesion: 0.10
Nodes (21): 1. Desenvolvimento (local), 2. Produção, 3. Roteiro de teste em produção (amanhã), 4. Sinais de problema e como reagir, 5. Links e referências rápidas, Acesso local, Backup manual do banco, Como atualizar o sistema (+13 more)

### Community 40 - "enrich_discovered_printers"
Cohesion: 0.27
Nodes (7): enrich_discovered_printers(), Enriquece filas em memória; não recebe nem acessa uma sessão SQL., DiscoverySnmpTests, printer(), DiscoveredPrinter, Testes locais do enriquecimento SNMP, sem rede corporativa ou SQLite., result()

### Community 41 - "main.py"
Cohesion: 0.09
Nodes (26): AsyncIOScheduler, _caminho_do_log(), Path, Configuracao de log (Fase 10). Por que existe como modulo, e nao como um…, Substitui valores sensiveis na mensagem antes de ela ser emitida. Fica no…, Resolve settings.log_file. Vazio = so console., Instala console + arquivo rotativo na raiz do logging. Idempotente: chamar duas…, RedactSecretsFilter (+18 more)

### Community 42 - "FakeAgent"
Cohesion: 0.15
Nodes (7): check(), FakeAgent, LocalSNMPClient, main(), Extrai (pdu_tag, [oids]) de um GET/GETBULK., SNMPClient apontando para a porta do agente falso, sem depender de ICMP., Responde GET e GETBULK para um conjunto de OIDs configurado.

### Community 43 - "cn"
Cohesion: 0.12
Nodes (20): AlertsPage(), DashboardPage(), AlertBanner(), AlertBannerProps, AlertsView(), AlertsViewProps, BottomCharts(), DiscoveryResults() (+12 more)

### Community 44 - "Alert"
Cohesion: 0.09
Nodes (32): Alert, SQLModel, TonerHistory, PrinterMonthly, SQLModel, get_alert(), list_alerts(), notify_alert() (+24 more)

### Community 45 - "PLANO DE IMPLEMENTAÇÃO — ESCANEAR REDE REAL"
Cohesion: 0.05
Nodes (39): A. Endpoint (implementado), Alertas, Arquitetura atual, Arquitetura do PrinterControl, B. Service reutilizável, Banco, C. Funções Print Server reutilizáveis, Cliente de API (+31 more)

### Community 46 - "services/print_server.py"
Cohesion: 0.06
Nodes (33): discover_printers(), DiscoveredPrinter, _escapar_powershell(), _mock_discover(), PrintServerError, Exception, Camada de Print Server (Etapa 3). Reproduz a descoberta de impressoras do…, Uma linha do que Get-Printer + Get-PrinterPort devolveriam, combinadas. (+25 more)

### Community 47 - "Impressoras"
Cohesion: 0.22
Nodes (9): `GET /api/printers`, `GET /api/printers/monthly-report`, `GET /api/printers/{printer_id}`, `GET /api/printers/{printer_id}/readings`, `GET /api/printers/with-status`, Impressoras, `PATCH /api/printers/{printer_id}`, `POST /api/printers` (+1 more)

### Community 48 - "Guia de Uso do PrinterControl"
Cohesion: 0.10
Nodes (20): Acessar via web — PARCIAL, Adicionar impressora — AUSENTE/PARCIAL, Alertas — FUNCIONAL na leitura; PARCIAL nas ações, Ações, Como acessar, Configurações — COMING SOON, Configurações, Usuários e Integrações — COMING SOON, Dashboard — FUNCIONAL/PARCIAL (+12 more)

### Community 49 - "Login.tsx"
Cohesion: 0.14
Nodes (12): Logo Elgin é redesenho à mão (IA sem acesso a imagens coladas no chat, só uploads), src/components/ (padrão com header-comment por arquivo), ElginLogo(), ElginLogoProps, ACTIVE_NODES, features, Login(), handleSubmit() (+4 more)

### Community 50 - "app-data.tsx"
Cohesion: 0.11
Nodes (27): handleSubmit(), validar(), decommissionedPrinters, monthlyUsage, BackendEnvironment, discoverPrinters(), fetchBackendEnvironment(), fetchUnreadNotificationCount() (+19 more)

### Community 51 - "UsersView"
Cohesion: 0.24
Nodes (8): formatarData(), UsersView(), abrirEdicao(), confirmarAtivacao(), salvar(), validar(), createUser(), updateUser()

### Community 52 - "useAppData"
Cohesion: 0.10
Nodes (27): react, ReportsPage(), AppShell(), AuthGate(), Modal(), ModalProps, MustChangePasswordGate(), PrinterDetailsModal() (+19 more)

### Community 53 - "Guia do Desenvolvedor"
Cohesion: 0.13
Nodes (15): Backend, Banco, Comandos do frontend, Escanear Rede (implementado), Guia do Desenvolvedor, Já resolvido — não reabra, O que não executar em produção sem autorização, Print Server (+7 more)

### Community 54 - "NotificationsView.tsx"
Cohesion: 0.12
Nodes (20): FORM_VAZIO, formatarMomento(), FormState, ICONE_SEVERIDADE, NotificationsView(), abrirEnvio(), enviar(), marcarComoLida() (+12 more)

### Community 55 - "hash_password"
Cohesion: 0.18
Nodes (16): hash_password(), migrar_dominio(), mostrar_senha_uma_vez(), obter_senha_admin(), Session, Semeia o banco: contas iniciais + a frota de printers_data.json. SENHAS (Fase…, Imprime a senha em destaque. Unica vez que ela aparece em texto claro., Renomeia TODAS as contas `...@example.com` para `...@elgin.com.br`. Uso unico,… (+8 more)

### Community 56 - "Settings"
Cohesion: 0.08
Nodes (17): Config, field_validator, Fail-fast: producao nao sobe com simulacao ligada (Fase 9). O risco concreto e…, Impede que um ambiente de producao suba silenciosamente com o secret de…, Aceita "https://a.com, https://b.com" alem da lista JSON. Sem isto,…, Producao exige origens proprias e explicitas (Fase 10). Tres recusas, todas por…, Normaliza um DATABASE_URL sqlite relativo (ex.: sqlite:///./x.db) para um…, Um ambiente escrito errado nao pode cair no default em silencio:… (+9 more)

### Community 57 - "SNMPResult"
Cohesion: 0.10
Nodes (24): _empty_result(), EnrichedDiscoveredPrinter, _is_color(), _is_label(), _normalize_ip(), DiscoveredPrinter, Enriquecimento transitório de filas descobertas com telemetria SNMP., _result_for_ip() (+16 more)

### Community 58 - "auth.ts"
Cohesion: 0.24
Nodes (17): clearToken(), getToken(), isTokenPersistent(), setToken(), ApiUser, cacheAccount(), fetchCurrentUser(), login() (+9 more)

### Community 60 - "SettingsView.tsx"
Cohesion: 0.15
Nodes (15): SettingsView(), salvarPerfil(), trocarSenha(), validarSenha(), TEMAS, API_BASE_URL, changeMyPassword(), ESCALAS (+7 more)

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
Cohesion: 0.11
Nodes (18): Como ler, D10 — O frontend não tem nenhum teste automatizado, D11 — O painel cai em dados de demonstração quando a API não responde, D12 — Datas ingênuas no servidor, hora do navegador no cliente, D13 — `/health` existe, mas nada o consulta, D14 — `httpx` sem teto de versão quebrava todas as suítes que usam `TestClient`, D15 — `requirements.txt` está em UTF-16, D16 — `backend/.env` em produção estava configurado como `demo`/`mock`, não `production` (+10 more)

### Community 65 - "tests_print_servers.py"
Cohesion: 0.18
Nodes (13): PrintServer, SQLModel, str, Print Server como entidade (Fase 4). Ate aqui um Print Server existia de duas…, Modos aceitos, iguais aos de `settings.print_server_mode`., ServerMode, check(), check_true() (+5 more)

### Community 66 - "Autenticação"
Cohesion: 0.29
Nodes (7): Autenticação, Bloqueio de simulação em produção (Fase 9), `GET /api/auth/me`, `GET /health`, `PATCH /api/auth/me`, `POST /api/auth/change-password`, `POST /api/auth/login`

### Community 67 - "VISAO_GERAL.md"
Cohesion: 0.33
Nodes (3): Matriz de Funcionalidades, Itens que os documentos antigos listavam e que **já não existem**, Resolvido na Fase 10 (24/08/2026)

### Community 68 - "Role"
Cohesion: 0.15
Nodes (21): SQLModel, str, RBAC minimo (Fase 1). Tres papeis cobrem todas as rotas existentes hoje: -…, Role, _active_admin_count(), create_user(), _ensure_not_last_admin(), list_users() (+13 more)

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

### Community 80 - "PrinterCollector"
Cohesion: 0.08
Nodes (32): PrinterReading, list_scenarios(), get, Cenarios simulados disponiveis e se o modo mock esta habilitado., PrinterCollector, Printer, Session, Orquestrador da coleta de impressoras. Separa as tres responsabilidades da… (+24 more)

### Community 82 - "PrinterTable.tsx"
Cohesion: 0.09
Nodes (26): PrintersPage(), TonerPage(), config, PrinterStatusBadge(), PAGE_SIZE_OPTIONS, PrinterTable(), PrinterTableProps, RightPanel() (+18 more)

### Community 83 - "._limpar"
Cohesion: 0.22
Nodes (6): Consome credito. So a FALHA conta — login certo nao gasta nada., Zera as contagens apos um login BEM-SUCEDIDO. Sem isto, quem erra a senha…, Veredito de uma checagem. `retry_after` so faz sentido quando bloqueado., Descarta o que saiu da janela e devolve o que restou., Diz se a tentativa deve ser recusada — sem consumir credito. Separado de…, ResultadoLimite

### Community 84 - "6. Subir o sistema em produção hoje"
Cohesion: 0.22
Nodes (9): 6. Subir o sistema em produção hoje, Passo 1 — Preparar o `.env`, Passo 2 — Testar a configuração ANTES de subir, Passo 3 — Definir a senha das contas de administrador, Passo 4 — Backup antes de qualquer coisa, Passo 5 — Subir o backend, Passo 6 — Verificar a saúde, Passo 7 — Subir o painel (+1 more)

### Community 86 - "PrinterControl — Visão geral do sistema"
Cohesion: 0.29
Nodes (7): 1. O que o sistema faz, 8. Onde está o resto da documentação, Como ele descobre isso, O ciclo, em uma frase, O detalhe que explica o relatório mensal, PrinterControl — Visão geral do sistema, Índice

### Community 87 - "5. Modo real x modo simulado, e os riscos"
Cohesion: 0.33
Nodes (6): 5. Modo real x modo simulado, e os riscos, As duas camadas de proteção, Como o sistema decide entre real e simulado, O problema em uma frase, O risco mais grave: sincronizar em modo simulado, Riscos corrigidos na Fase 10 (24/08/2026)

### Community 89 - "require_user"
Cohesion: 0.33
Nodes (6): Session, Usuario dono do JWT do header Authorization. 401 se ausente/invalido. O usuario…, require_user(), decode_token(), Devolve {"email": ...} para um token valido, ou None. `algorithms` e uma lista…, HTTPAuthorizationCredentials

### Community 90 - "2. Como o sistema é montado"
Cohesion: 0.50
Nodes (4): 2. Como o sistema é montado, O "crachá" (token), O que cada tecnologia é, em uma linha, Por que duas peças, e não uma

### Community 91 - "public/data/monthly-report.json"
Cohesion: 0.67
Nodes (3): public/data/monthly-report.json, public/data/printers.json, Arquivos de dados gerados são ignorados pelo git — gerar/apagar localmente nunca afeta o repositório

### Community 93 - "tests_printer_fleet.py"
Cohesion: 0.18
Nodes (4): fake_real_collect(), Etapa 5 - orquestracao da frota (printer_fleet.collect_fleet). Roda sobre um…, RecordingThreadPoolExecutor, _OriginalTPE

### Community 106 - "database.py"
Cohesion: 0.08
Nodes (30): create_db_and_tables(), _finish_printer_migration(), get_session(), _migrate_alert_type(), _migrate_print_servers(), _migrate_printer_schema(), _migrate_reading_uptime(), _migrate_user_login_fields() (+22 more)

## Knowledge Gaps
- **401 isolated node(s):** `Pré-requisitos`, `Subir o backend`, `Subir o frontend`, `Variáveis de ambiente`, `Acesso local` (+396 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SNMPClient` connect `SNMPClient` to `snmp.py`, `enrich_discovered_printers`, `FakeAgent`, `PrinterCollector`, `SNMPResult`, `tests_printer_fleet.py`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Why does `User` connect `User` to `tests_print_servers.py`, `notifications.py`, `Role`, `servers.py`, `create_server`, `Printer`, `main.py`, `database.py`, `config.py`, `Alert`, `PrinterCollector`, `hash_password`, `require_user`, `routes/auth.py`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Why does `Printer` connect `Printer` to `tests_fleet.py`, `tests_print_servers.py`, `servers.py`, `create_server`, `main.py`, `database.py`, `config.py`, `Alert`, `services/print_server.py`, `PrinterCollector`, `hash_password`, `alert_engine.py`, `tests_printer_fleet.py`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Are the 39 inferred relationships involving `User` (e.g. with `require_active_user()` and `require_roles()`) actually correct?**
  _`User` has 39 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `Printer` (e.g. with `_finish_printer_migration()` and `notify_alert()`) actually correct?**
  _`Printer` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `SNMPClient` (e.g. with `PrinterCollector` and `FakeAgent`) actually correct?**
  _`SNMPClient` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Pré-requisitos`, `Subir o backend`, `Subir o frontend` to the rest of the system?**
  _401 weakly-connected nodes found - possible documentation gaps or missing edges._