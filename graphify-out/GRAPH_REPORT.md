# Graph Report - PrinterControl  (2026-08-24)

## Corpus Check
- 157 files · ~129,756 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1589 nodes · 3246 edges · 97 communities (86 shown, 11 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 137 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a8ca4263`
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
- Printer
- MockSNMPClient
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
- Alert
- schemas/printer.py
- routes/auth.py
- Operação em Produção
- evaluate_reading
- printer_sync.py
- _executar_discover
- User
- Notification
- collect_printer
- SNMPClient
- enrich_discovered_printers
- NetworkView.tsx
- Simular-Ambiente.ps1
- main.py
- PrintServerCreate
- printers.ts
- database.py
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
- create_db_and_tables
- Settings
- SNMPResult
- auth.ts
- ServerMode
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
- _Req
- types.ts
- ._limpar
- 6. Subir o sistema em produção hoje
- Modo Simulado
- PrinterControl — Visão geral do sistema
- 5. Modo real x modo simulado, e os riscos
- ambiente
- 2. Como o sistema é montado
- layout.tsx
- tests_printer_fleet.py
- discovery.py
- tests_environment.py
- theme.tsx
- require_user
- Ações

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

## Communities (97 total, 11 thin omitted)

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
Cohesion: 0.14
Nodes (28): PrintServer, SQLModel, create_server(), discover_server(), _get_or_404(), list_servers(), _marcar_resultado(), PrintServerResponse (+20 more)

### Community 8 - "Printer"
Cohesion: 0.21
Nodes (19): Printer, Etapa 4: identidade e (server, name), NAO ip — o Print Server permite varias…, create_printer(), create_printer_reading(), get_printer(), get_printer_readings(), _inicio_da_janela(), list_printers() (+11 more)

### Community 9 - "MockSNMPClient"
Cohesion: 0.13
Nodes (10): get_scheduler_status(), list_scenarios(), get, Cenarios simulados disponiveis e se o modo mock esta habilitado., Estado da coleta agendada (APScheduler)., Cenarios de teste disponiveis (fonte unica: snmp_mock.SCENARIOS)., Args: mode: "real" (SNMP de verdade), "mock" (cenario fixo) ou "fleet" (frota…, MockSNMPClient (+2 more)

### Community 10 - "plugins"
Cohesion: 0.22
Nodes (8): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, typescript, warn

### Community 11 - "HistoryMatrix.tsx"
Cohesion: 0.27
Nodes (5): HistoryPage(), HistoryMatrix(), HistoryMatrixProps, getDepartmentLabel(), getPrinterSite()

### Community 12 - "graphify (knowledge graph tool)"
Cohesion: 0.25
Nodes (8): graphify (knowledge graph tool), graphify explain command, graphify path command, graphify query command, graphify update command, graphify-out/graph.json, graphify-out/GRAPH_REPORT.md, graphify-out/wiki/index.md

### Community 20 - "cn"
Cohesion: 0.07
Nodes (38): AlertsPage(), DashboardPage(), AlertBanner(), AlertBannerProps, AlertsView(), AlertsViewProps, AlertsDonutCard(), AlertsDonutCardProps (+30 more)

### Community 21 - "unhandled_exception_handler"
Cohesion: 0.40
Nodes (5): Exception, Request, Erro nao tratado: o detalhe vai para o log do servidor, o cliente recebe apenas…, unhandled_exception_handler(), exception_handler

### Community 22 - "tests_collect_api.py"
Cohesion: 0.67
Nodes (3): check(), main(), Teste ponta a ponta dos endpoints /api/collect com os cenarios simulados.…

### Community 23 - "Cloudflare Tunnel — expor a API sem abrir porta (Fase 11)"
Cohesion: 0.13
Nodes (15): 10. Resumo do que muda em cada lugar, 1. Instalar o `cloudflared`, 2. Criar o túnel — caminho recomendado (via painel, com token), 3. Apontar o hostname para o backend, 4. Validar antes de seguir, 5. Confirmar que o serviço sobe sozinho, 6. Cabeçalhos de segurança — no Cloudflare, não no backend, 7. CORS — o que falta até a Vercel existir (Fase 12) (+7 more)

### Community 25 - "Alert"
Cohesion: 0.16
Nodes (14): Alert, SQLModel, TonerHistory, PrinterMonthly, PrinterReading, SQLModel, Alertas automaticos (Etapa 8A). Roda logo apos cada PrinterReading ser…, collect_fleet() (+6 more)

### Community 28 - "schemas/printer.py"
Cohesion: 0.14
Nodes (16): Config, PrinterCreate, PrinterReadingCreate, PrinterReadingResponse, PrinterResponse, PrinterUpdate, PrinterWithStatus, BaseModel (+8 more)

### Community 29 - "routes/auth.py"
Cohesion: 0.11
Nodes (28): change_own_password(), _identificar_origem(), login(), get, patch, post, Request, Session (+20 more)

### Community 30 - "Operação em Produção"
Cohesion: 0.11
Nodes (18): 1. Antes do primeiro deploy, 2. Instalar, 3. Dia a dia, 4. Diagnóstico, 5. Backup, 6. Recuperação — o que acontece se o processo cair, 7. Problemas comuns, 8. Dívida técnica conhecida — FK órfã para `printers_old` (+10 more)

### Community 31 - "evaluate_reading"
Cohesion: 0.43
Nodes (7): Alert, _active(), evaluate_reading(), Session, Cria, mantem ou resolve o alerta de uma condicao. Retorna a acao tomada., Avalia uma leitura e sincroniza os alertas da impressora. Faz commit ao final.…, _sync_condition()

### Community 32 - "printer_sync.py"
Cohesion: 0.20
Nodes (11): obter_modelo(), obter_tipo_impressora(), Regras de classificacao portadas do Main.ps1 (Etapa 4). Correspondencia exata:…, Traduz DriverName (Windows) em nome comercial, igual ao Main.ps1., Classifica A4 / Etiqueta / Portatil a partir de Nome+Modelo, igual ao Main.ps1., Session, Sincronizacao Print Server -> banco (Etapa 4). Print Server ->…, Executa um ciclo completo de sincronizacao para UM Print Server. Ja era… (+3 more)

### Community 33 - "_executar_discover"
Cohesion: 0.20
Nodes (11): discover(), DiscoveredPrinterResponse, DiscoverResponse, _executar_discover(), get_current_server(), BaseModel, get, Descoberta + enriquecimento SNMP, sem tocar no banco. (+3 more)

### Community 34 - "User"
Cohesion: 0.22
Nodes (14): Fabrica de dependencia: exige que o usuario tenha (ou herde) um dos papeis…, require_roles(), SQLModel, True se o papel do usuario satisfaz qualquer um dos exigidos., User, verify_password(), check(), check_true() (+6 more)

### Community 35 - "Notification"
Cohesion: 0.10
Nodes (29): Notification, SQLModel, AlertRef, create_notifications(), list_notifications(), mark_all_as_read(), mark_as_read(), _minha_ou_404() (+21 more)

### Community 36 - "collect_printer"
Cohesion: 0.27
Nodes (10): collect_fleet(), collect_printer(), CollectRequest, CollectResponse, FleetCollectResponse, BaseModel, post, Session (+2 more)

### Community 37 - "SNMPClient"
Cohesion: 0.05
Nodes (36): parse_varbinds(), SNMP Collector para impressoras. Porte direto da funcao Get-TonerSNMP de…, Decodifica um OID BER para notacao pontuada., Decodifica bytes BER como inteiro sem sinal., Extrai a lista de varbinds de uma resposta SNMP. Percorre a estrutura completa…, Cliente SNMP para coleta de impressoras (Printer-MIB, RFC 3805)., Coleta status, contador de paginas e toners de uma impressora. Nunca levanta…, PS1: `if ($ip -match '^\\d')` — descarta 'N/A' e nomes de porta. (+28 more)

### Community 38 - "enrich_discovered_printers"
Cohesion: 0.24
Nodes (9): enrich_discovered_printers(), Enriquece filas em memória; não recebe nem acessa uma sessão SQL., Nivel de um consumivel de toner., TonerInfo, DiscoverySnmpTests, printer(), DiscoveredPrinter, Testes locais do enriquecimento SNMP, sem rede corporativa ou SQLite. (+1 more)

### Community 39 - "NetworkView.tsx"
Cohesion: 0.08
Nodes (29): DiscoveryResults(), DiscoveryResultsProps, statusLabel(), Modal(), ModalProps, adaptDiscovered(), FORM_VAZIO, formatarMomento() (+21 more)

### Community 40 - "Simular-Ambiente.ps1"
Cohesion: 0.16
Nodes (6): Modo Real, Contador mensal calculado por diff de duas leituras SNMP acumulativas (não existe OID de páginas do mês), Scripts PowerShell reais nunca rodaram de verdade (sem interpretador PowerShell no ambiente de dev), public/data/monthly-report.json, public/data/printers.json, Arquivos de dados gerados são ignorados pelo git — gerar/apagar localmente nunca afeta o repositório

### Community 41 - "main.py"
Cohesion: 0.08
Nodes (30): AsyncIOScheduler, _migrate_reading_uptime(), Etapa 7: adiciona printer_readings.uptime em bancos criados antes desta etapa.…, _caminho_do_log(), Path, Configuracao de log (Fase 10). Por que existe como modulo, e nao como um…, Substitui valores sensiveis na mensagem antes de ela ser emitida. Fica no…, Resolve settings.log_file. Vazio = so console. (+22 more)

### Community 42 - "PrintServerCreate"
Cohesion: 0.28
Nodes (5): PrintServerCreate, PrintServerUpdate, field_validator, `host` fica de fora de proposito: ele e a chave natural que aparece em…, Recusa no cadastro o que a camada de execucao ja recusaria. O host e…

### Community 43 - "printers.ts"
Cohesion: 0.19
Nodes (11): Levantamento_impressões (planilha original), DecommissionedList(), DecommissionedListProps, DepartmentBreakdown(), DepartmentBreakdownProps, MONTHS, DecommissionedPrinter, DepartmentUsage (+3 more)

### Community 44 - "database.py"
Cohesion: 0.07
Nodes (35): _finish_printer_migration(), get_session(), _migrate_printer_schema(), Path, Caminho do arquivo .db atual, se o banco for SQLite em disco (nao :memory:)., Etapa 4 — reconstroi `printers` para trocar a identidade de `ip UNIQUE` para…, Recria `printers` (schema atual) e copia `printers_old` para dentro dela, numa…, _sqlite_backup_path() (+27 more)

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
Cohesion: 0.11
Nodes (20): ComingSoon(), ComingSoonProps, RequireRole(), FORM_VAZIO, formatarData(), FormState, UsersView(), abrirEdicao() (+12 more)

### Community 53 - "Guia do Desenvolvedor"
Cohesion: 0.13
Nodes (15): Backend, Banco, Comandos do frontend, Escanear Rede (implementado), Guia do Desenvolvedor, Já resolvido — não reabra, O que não executar em produção sem autorização, Print Server (+7 more)

### Community 54 - "api.ts"
Cohesion: 0.06
Nodes (47): FORM_VAZIO, formatarMomento(), FormState, ICONE_SEVERIDADE, NotificationsView(), abrirEnvio(), enviar(), marcarComoLida() (+39 more)

### Community 55 - "create_db_and_tables"
Cohesion: 0.09
Nodes (31): create_db_and_tables(), _migrate_alert_type(), _migrate_print_servers(), _migrate_user_login_fields(), _migrate_user_rbac(), Fase 1 (RBAC): adiciona users.role e users.is_active em bancos criados antes…, Login por username e troca de senha obrigatoria (2026-08-24). Adiciona…, Fase 4: registro de Print Servers. A tabela `print_servers` em si e criada pelo… (+23 more)

### Community 56 - "Settings"
Cohesion: 0.08
Nodes (17): Config, field_validator, Fail-fast: producao nao sobe com simulacao ligada (Fase 9). O risco concreto e…, Impede que um ambiente de producao suba silenciosamente com o secret de…, Aceita "https://a.com, https://b.com" alem da lista JSON. Sem isto,…, Producao exige origens proprias e explicitas (Fase 10). Tres recusas, todas por…, Normaliza um DATABASE_URL sqlite relativo (ex.: sqlite:///./x.db) para um…, Um ambiente escrito errado nao pode cair no default em silencio:… (+9 more)

### Community 57 - "SNMPResult"
Cohesion: 0.13
Nodes (15): MockSNMPScenarios, Agente SNMP simulado — APENAS PARA TESTE LOCAL. Existe porque a maquina de…, SNMP responde o contador, mas nao expoe a tabela de consumiveis., Monocromatica com toner em 5%., Colorida com ciano critico (18%) e os demais normais., Contador reiniciado (troca de placa/formatador): page_count baixo., Cenarios de teste. Cada metodo devolve um SNMPResult completo., Monocromatica saudavel. (+7 more)

### Community 58 - "auth.ts"
Cohesion: 0.10
Nodes (29): Logo Elgin é redesenho à mão (IA sem acesso a imagens coladas no chat, só uploads), src/components/ (padrão com header-comment por arquivo), ElginLogo(), ElginLogoProps, ACTIVE_NODES, features, Login(), handleSubmit() (+21 more)

### Community 59 - "ServerMode"
Cohesion: 0.67
Nodes (3): str, Modos aceitos, iguais aos de `settings.print_server_mode`., ServerMode

### Community 60 - "useAppData"
Cohesion: 0.08
Nodes (37): react, PrintersPage(), ReportsPage(), AppShell(), AuthGate(), MustChangePasswordGate(), PrinterDetailsModal(), SettingsView() (+29 more)

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
Cohesion: 0.29
Nodes (8): Print Server como entidade (Fase 4). Ate aqui um Print Server existia de duas…, check(), check_true(), h(), main(), Fase 4 - Registro de Print Servers e operacao por servidor. Como…, Monta um banco no formato ANTERIOR a Fase 4 (printers sem print_server_id, sem…, _testa_migracao_legada()

### Community 66 - "Autenticação"
Cohesion: 0.29
Nodes (7): Autenticação, Bloqueio de simulação em produção (Fase 9), `GET /api/auth/me`, `GET /health`, `PATCH /api/auth/me`, `POST /api/auth/change-password`, `POST /api/auth/login`

### Community 67 - "VISAO_GERAL.md"
Cohesion: 0.29
Nodes (3): Matriz de Funcionalidades, Itens que os documentos antigos listavam e que **já não existem**, Resolvido na Fase 10 (24/08/2026)

### Community 68 - "Role"
Cohesion: 0.11
Nodes (24): str, RBAC minimo (Fase 1). Tres papeis cobrem todas as rotas existentes hoje: -…, Role, _active_admin_count(), create_user(), _ensure_not_last_admin(), list_users(), get (+16 more)

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

### Community 82 - "types.ts"
Cohesion: 0.08
Nodes (39): TonerPage(), PrinterDetailsModalProps, PrinterRanking(), PrinterRankingProps, RankedPrinter, RankList(), rankPrinters(), config (+31 more)

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

### Community 90 - "2. Como o sistema é montado"
Cohesion: 0.50
Nodes (4): 2. Como o sistema é montado, O "crachá" (token), O que cada tecnologia é, em uma linha, Por que duas peças, e não uma

### Community 91 - "layout.tsx"
Cohesion: 0.29
Nodes (5): ibmPlexMono, metadata, publicSans, sourceSerif, Providers()

### Community 93 - "tests_printer_fleet.py"
Cohesion: 0.18
Nodes (4): fake_real_collect(), Etapa 5 - orquestracao da frota (printer_fleet.collect_fleet). Roda sobre um…, RecordingThreadPoolExecutor, _OriginalTPE

### Community 97 - "discovery.py"
Cohesion: 0.39
Nodes (8): _empty_result(), EnrichedDiscoveredPrinter, _is_color(), _is_label(), _normalize_ip(), DiscoveredPrinter, Enriquecimento transitório de filas descobertas com telemetria SNMP., _result_for_ip()

### Community 98 - "tests_environment.py"
Cohesion: 0.12
Nodes (9): RateLimiter, Limite de tentativas para o login (Fase 10). POR QUE existe --------------…, Esvazia tudo. Existe para os testes; nao ha rota que chegue aqui., Janela deslizante em memoria, protegida por lock. O lock existe porque o…, Fase 9 - Mock e Demo Seguros. Cobre as DUAS camadas que protegem o risco…, medir(), Fase 10 - endurecimento do login. Cobre as duas falhas levantadas na auditoria…, Tentativa com a contagem limpa — isola o caso do limite de tentativas. (+1 more)

### Community 100 - "theme.tsx"
Cohesion: 0.27
Nodes (8): lerPreferencia(), resolver(), sistemaEscuro(), Theme, ThemeContext, ThemeContextValue, ThemePreference, ThemeProvider()

### Community 106 - "require_user"
Cohesion: 0.33
Nodes (6): Session, Usuario dono do JWT do header Authorization. 401 se ausente/invalido. O usuario…, require_user(), decode_token(), Devolve {"email": ...} para um token valido, ou None. `algorithms` e uma lista…, HTTPAuthorizationCredentials

### Community 108 - "Ações"
Cohesion: 0.33
Nodes (6): Acessar via web — PARCIAL, Adicionar impressora — AUSENTE/PARCIAL, Ações, Configurações — COMING SOON, Impressoras — FUNCIONAL/PARCIAL, Imprimir página de teste — SIMULADA

## Knowledge Gaps
- **372 isolated node(s):** `$schema`, `typescript`, `oxc`, `react/rules-of-hooks`, `warn` (+367 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `_executar_discover`, `tests_environment.py`, `Notification`, `collect_printer`, `Role`, `tests_print_servers.py`, `servers.py`, `Printer`, `main.py`, `require_user`, `MockSNMPClient`, `database.py`, `tests_rbac.py`, `create_db_and_tables`, `Alert`, `routes/auth.py`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Why does `SNMPClient` connect `SNMPClient` to `discovery.py`, `PrinterCollector`, `enrich_discovered_printers`, `MockSNMPClient`, `main.py`, `printer_fleet.py`, `tests_printer_fleet.py`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Why does `Printer` connect `Printer` to `printer_sync.py`, `tests_print_servers.py`, `tests_environment.py`, `collect_printer`, `PrinterCollector`, `servers.py`, `main.py`, `database.py`, `printer_fleet.py`, `tests_rbac.py`, `create_db_and_tables`, `Alert`, `tests_printer_fleet.py`, `evaluate_reading`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Are the 39 inferred relationships involving `User` (e.g. with `require_active_user()` and `require_roles()`) actually correct?**
  _`User` has 39 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `Printer` (e.g. with `_finish_printer_migration()` and `notify_alert()`) actually correct?**
  _`Printer` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `SNMPClient` (e.g. with `PrinterCollector` and `FakeAgent`) actually correct?**
  _`SNMPClient` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `typescript`, `oxc` to the rest of the system?**
  _372 weakly-connected nodes found - possible documentation gaps or missing edges._