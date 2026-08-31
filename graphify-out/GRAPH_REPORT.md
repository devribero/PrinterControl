# Graph Report - PrinterControl  (2026-08-31)

## Corpus Check
- 156 files · ~147,613 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1691 nodes · 3290 edges · 105 communities (93 shown, 12 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 131 edges (avg confidence: 0.55)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `151d83f1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- snmp_fleet_mock.py
- package.json
- Main.ps1
- Elgin Impressoras (painel de monitoramento)
- api.ts
- adaptApi.ts
- compilerOptions
- servers.py
- AUDITORIA COMPLEMENTAR
- tests_login_hardening.py
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
- Sidebar.tsx
- unhandled_exception_handler
- tests_collect_api.py
- Cloudflare Tunnel — expor a API sem abrir porta (Fase 11)
- AUDITORIA MASTER — PrinterControl
- schemas/printer.py
- routes/auth.py
- Operação em Produção
- Deploy do Frontend na Vercel (Fase 12)
- app-data.tsx
- users.py
- User
- Notification
- scheduler_status
- toast.tsx
- ETAPA FINAL — FECHAMENTO DA AUDITORIA
- 1. Desenvolvimento (local)
- tests_rbac.py
- database.py
- SNMPClient
- cn
- .collect_and_save
- PLANO DE IMPLEMENTAÇÃO — ESCANEAR REDE REAL
- Login.tsx
- Impressoras
- Guia de Uso do PrinterControl
- ConfigurarAmbiente.ps1
- AppDataProvider
- UsersView.tsx
- useAppData
- Guia do Desenvolvedor
- NotificationsView.tsx
- Role
- Settings
- SNMPResult
- auth.ts
- Contador mensal calculado por diff de duas leituras SNMP acumulativas (não existe OID de páginas do mês)
- theme.tsx
- Print Server
- Fluxo de Dados
- enrich_discovered_printers
- Dívida técnica — registro único
- ServerMode
- Autenticação
- VISAO_GERAL.md
- 41. Scores, veredito e roadmap
- _migrate_printer_schema
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
- Printer
- RODADA G — FECHAMENTO DE LACUNAS RESIDUAIS
- types.ts
- ._limpar
- 6. Subir o sistema em produção hoje
- tests_environment.py
- PrinterControl — Visão geral do sistema
- 5. Modo real x modo simulado, e os riscos
- ambiente
- require_user
- 2. Como o sistema é montado
- tests_printers_crud.py
- Scripts PowerShell reais nunca rodaram de verdade (sem interpretador PowerShell no ambiente de dev)
- tests_printer_fleet.py
- RedactSecretsFilter
- notify_alert
- layout.tsx
- PrinterCollector
- Ações
- list_scenarios
- C23. Terceiro passe — Frontend real (token/XSS/CSRF) e execução direta dos testes
- integrations/page.tsx
- Exception
- Request
- create_db_and_tables

## God Nodes (most connected - your core abstractions)
1. `User` - 54 edges
2. `Printer` - 47 edges
3. `cn()` - 39 edges
4. `SNMPClient` - 37 edges
5. `useAppData()` - 35 edges
6. `SNMPResult` - 34 edges
7. `create_db_and_tables()` - 29 edges
8. `useToast()` - 29 edges
9. `PrinterCollector` - 26 edges
10. `AUDITORIA COMPLEMENTAR` - 25 edges

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

## Communities (105 total, 12 thin omitted)

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
Cohesion: 0.07
Nodes (28): Tela Alertas, Tela Dashboard, Elgin Impressoras (painel de monitoramento), Tela Histórico, Tela Impressoras, Tela Login, Migração futura para FastAPI (Python) + Next.js + banco de dados, Modo claro/escuro (toggle) (+20 more)

### Community 4 - "api.ts"
Cohesion: 0.09
Nodes (20): confirmarAtivacao(), salvar(), validar(), API_BASE_URL, ApiDiscoveredPrinter, ApiDiscoveredToner, ApiNotificationAlertRef, ApiPrinterReading (+12 more)

### Community 5 - "adaptApi.ts"
Cohesion: 0.13
Nodes (18): adaptAlert(), adaptPrinter(), ApiMonthlyReport, formatLastSeen(), loadMonthlyReportFromApi(), toStatus(), toToner(), VALID_COLORS (+10 more)

### Community 6 - "compilerOptions"
Cohesion: 0.06
Nodes (30): dom, dom.iterable, esnext, .next/dev/types/**/*.ts, next-env.d.ts, .next/types/**/*.ts, node_modules, **/*.ts (+22 more)

### Community 7 - "servers.py"
Cohesion: 0.06
Nodes (58): collect_fleet(), collect_printer(), CollectRequest, CollectResponse, FleetCollectResponse, BaseModel, post, Session (+50 more)

### Community 8 - "AUDITORIA COMPLEMENTAR"
Cohesion: 0.08
Nodes (24): AUDITORIA COMPLEMENTAR, C10. Backup e Disaster Recovery — revisão significativa da rodada 1, C11. DevOps / CI-CD, C12. Supply Chain — aprofundamento, C13. PowerShell / Command Execution — reavaliação com evidência forte, C14. Segurança da API — inventário de endpoints (parcial, rotas mais sensíveis), C15. Autenticação — fluxo completo, C16. Banco de dados — schema (+16 more)

### Community 9 - "tests_login_hardening.py"
Cohesion: 0.08
Nodes (14): RateLimiter, Limite de tentativas para o login (Fase 10). POR QUE existe --------------…, Esvazia tudo. Existe para os testes; nao ha rota que chegue aqui., Janela deslizante em memoria, protegida por lock. O lock existe porque o…, medir(), Fase 10 - endurecimento do login. Cobre as duas falhas levantadas na auditoria…, Request minimo: so o que _identificar_origem le., Tentativa com a contagem limpa — isola o caso do limite de tentativas. (+6 more)

### Community 10 - "plugins"
Cohesion: 0.22
Nodes (8): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, typescript, warn

### Community 11 - "Printer"
Cohesion: 0.12
Nodes (17): HistoryPage(), ReportsPage(), DecommissionedList(), DecommissionedListProps, HistoryMatrix(), HistoryMatrixProps, PrinterDetailsModalProps, PrinterRanking() (+9 more)

### Community 12 - "graphify (knowledge graph tool)"
Cohesion: 0.25
Nodes (8): graphify (knowledge graph tool), graphify explain command, graphify path command, graphify query command, graphify update command, graphify-out/graph.json, graphify-out/GRAPH_REPORT.md, graphify-out/wiki/index.md

### Community 15 - "NetworkView.tsx"
Cohesion: 0.09
Nodes (27): adaptDiscovered(), FORM_VAZIO, formatarMomento(), MODOS, NetworkView(), confirmarAtivacao(), confirmarExclusao(), executarDescoberta() (+19 more)

### Community 20 - "Sidebar.tsx"
Cohesion: 0.12
Nodes (21): AlertsDonutCard(), AlertsDonutCardProps, BottomChartsProps, PagesConsumedCard(), DemoDataBadge(), DemoDataBadgeProps, MonthlyCounters(), MonthlyCountersProps (+13 more)

### Community 21 - "unhandled_exception_handler"
Cohesion: 0.40
Nodes (5): Erro nao tratado: o detalhe vai para o log do servidor, o cliente recebe apenas…, unhandled_exception_handler(), Exception, exception_handler, Request

### Community 22 - "tests_collect_api.py"
Cohesion: 0.67
Nodes (3): check(), main(), Teste ponta a ponta dos endpoints /api/collect com os cenarios simulados.…

### Community 23 - "Cloudflare Tunnel — expor a API sem abrir porta (Fase 11)"
Cohesion: 0.13
Nodes (15): 10. Resumo do que muda em cada lugar, 1. Instalar o `cloudflared`, 2. Criar o túnel — caminho recomendado (via painel, com token), 3. Apontar o hostname para o backend, 4. Validar antes de seguir, 5. Confirmar que o serviço sobe sozinho, 6. Cabeçalhos de segurança — no Cloudflare, não no backend, 7. CORS — preenchido na Fase 12 (+7 more)

### Community 25 - "AUDITORIA MASTER — PrinterControl"
Cohesion: 0.10
Nodes (21): 10. Dependências e supply chain, 11. Performance e escalabilidade, 12. Testes, 13. Frontend, 14. LGPD / dados pessoais, 15. Observabilidade / auditoria / logs, 16. Backup / Disaster Recovery, 17. Threat Modeling (STRIDE) — resumo (+13 more)

### Community 28 - "schemas/printer.py"
Cohesion: 0.09
Nodes (31): create_printer(), create_printer_reading(), get_printer(), get_printer_readings(), _inicio_da_janela(), list_printers(), list_printers_with_status(), monthly_report() (+23 more)

### Community 29 - "routes/auth.py"
Cohesion: 0.10
Nodes (30): change_own_password(), _identificar_origem(), login(), get, patch, post, Request, Session (+22 more)

### Community 30 - "Operação em Produção"
Cohesion: 0.11
Nodes (18): 1. Antes do primeiro deploy, 2. Instalar, 3. Dia a dia, 4. Diagnóstico, 5. Backup, 6. Recuperação — o que acontece se o processo cair, 7. Problemas comuns, 8. Dívida técnica conhecida — FK órfã para `printers_old` (+10 more)

### Community 31 - "Deploy do Frontend na Vercel (Fase 12)"
Cohesion: 0.25
Nodes (8): 1. O projeto já está pronto para este deploy, 2. Variáveis de ambiente para configurar na Vercel, 3. Conectar o repositório e fazer o primeiro deploy, 4. Validar, 5. Depois do deploy — atualizar o CORS do backend, 6. Redeploy — quando o código mudar, 7. Resumo — Fase 12 concluída, Deploy do Frontend na Vercel (Fase 12)

### Community 32 - "app-data.tsx"
Cohesion: 0.14
Nodes (20): Levantamento_impressões (planilha original), DepartmentBreakdown(), DepartmentBreakdownProps, MONTHS, RightPanelProps, decommissionedPrinters, DepartmentUsage, globalToner (+12 more)

### Community 33 - "users.py"
Cohesion: 0.11
Nodes (24): _active_admin_count(), create_user(), delete_user(), _ensure_not_last_admin(), list_users(), delete, get, patch (+16 more)

### Community 34 - "User"
Cohesion: 0.12
Nodes (21): SQLModel, True se o papel do usuario satisfaz qualquer um dos exigidos., User, hash_password(), Hash de senha e emissao/validacao do JWT. POR QUE PyJWT E NAO python-jose (Fase…, verify_password(), Login por username e troca de senha obrigatoria (2026-08-24). Cobre as duas…, check() (+13 more)

### Community 35 - "Notification"
Cohesion: 0.10
Nodes (28): Notification, AlertRef, create_notifications(), list_notifications(), mark_all_as_read(), mark_as_read(), _minha_ou_404(), NotificationCreate (+20 more)

### Community 36 - "scheduler_status"
Cohesion: 0.33
Nodes (6): health_check(), get, Saude, identificacao do ambiente (Fase 9) e diagnostico (Fase 10). O ambiente…, read_root(), Estado atual, para o endpoint de diagnostico., scheduler_status()

### Community 37 - "toast.tsx"
Cohesion: 0.09
Nodes (25): react, TonerPage(), AppShell(), AuthGate(), Modal(), ModalProps, PrinterDetailsModal(), classify() (+17 more)

### Community 38 - "ETAPA FINAL — FECHAMENTO DA AUDITORIA"
Cohesion: 0.14
Nodes (14): Cálculo do score geral, ETAPA FINAL — FECHAMENTO DA AUDITORIA, F0. Auditorias realizadas nesta etapa, F1. Áreas finalmente cobertas (antes NÃO VERIFICADO por orçamento, agora CONFIRMADO), F2. Achados de UX — resumo consolidado, F3. Achados de acessibilidade — resumo consolidado, F4. Segurança da API — `alerts.py` e `notifications.py` (fecha C14), F4b. Backend — reforço de `auth.py`/`collect.py`/`printers.py`, grep de segurança final, concorrência dos DELETE novos (+6 more)

### Community 39 - "1. Desenvolvimento (local)"
Cohesion: 0.10
Nodes (21): 1. Desenvolvimento (local), 2. Produção, 3. Roteiro de teste em produção (amanhã), 4. Sinais de problema e como reagir, 5. Links e referências rápidas, Acesso local, Backup manual do banco, Como atualizar o sistema (+13 more)

### Community 40 - "tests_rbac.py"
Cohesion: 0.24
Nodes (12): check(), check_true(), _confere_rbac_do_frontend(), h(), main(), Fase 1 - Autenticacao, RBAC e protecao das rotas. Diferente dos demais…, O frontend tem a sua propria copia da hierarquia de papeis, em…, Cria um banco no formato ANTERIOR a Fase 1 (users sem role/is_active), roda a… (+4 more)

### Community 41 - "database.py"
Cohesion: 0.12
Nodes (24): get_session(), _sqlite_pragmas(), Dependencias compartilhadas pelas rotas. Autorizacao (Fase 1) fica CENTRALIZADA…, Fabrica de dependencia: exige que o usuario tenha (ou herde) um dos papeis…, `require_user` + bloqueio de conta com troca de senha pendente. Toda rota do…, require_active_user(), require_roles(), Configuracao de log (Fase 10). Por que existe como modulo, e nao como um… (+16 more)

### Community 42 - "SNMPClient"
Cohesion: 0.05
Nodes (37): parse_varbinds(), Decodifica um OID BER para notacao pontuada., Decodifica bytes BER como inteiro sem sinal., Extrai a lista de varbinds de uma resposta SNMP. Percorre a estrutura completa…, Cliente SNMP para coleta de impressoras (Printer-MIB, RFC 3805)., Coleta status, contador de paginas e toners de uma impressora. Nunca levanta…, PS1: `if ($ip -match '^\\d')` — descarta 'N/A' e nomes de porta., ICMP ping, equivalente ao `New-Object ...Ping).Send($ip, 400)` do PS1. SNMP… (+29 more)

### Community 43 - "cn"
Cohesion: 0.08
Nodes (23): DashboardPage(), BottomCharts(), TotalPrintsCard(), DiscoveryResults(), DiscoveryResultsProps, statusLabel(), Login(), RankList() (+15 more)

### Community 44 - ".collect_and_save"
Cohesion: 0.22
Nodes (6): Printer, Session, Converte SNMPResult em PrinterReading. Toner ausente vira NULL (a coluna e…, Deduz se a impressora e colorida a partir do modelo/nome (regra do PS1)., Etiquetadora/portatil: sem Printer-MIB, o PS1 nem consulta SNMP., Coleta uma impressora e persiste a leitura. Args: printer_id: id da impressora…

### Community 45 - "PLANO DE IMPLEMENTAÇÃO — ESCANEAR REDE REAL"
Cohesion: 0.05
Nodes (39): A. Endpoint (implementado), Alertas, Arquitetura atual, Arquitetura do PrinterControl, B. Service reutilizável, Banco, C. Funções Print Server reutilizáveis, Cliente de API (+31 more)

### Community 46 - "Login.tsx"
Cohesion: 0.22
Nodes (6): ACTIVE_NODES, features, LoginProps, NETWORK_LINKS, NETWORK_NODES, ApiError

### Community 47 - "Impressoras"
Cohesion: 0.22
Nodes (9): `GET /api/printers`, `GET /api/printers/monthly-report`, `GET /api/printers/{printer_id}`, `GET /api/printers/{printer_id}/readings`, `GET /api/printers/with-status`, Impressoras, `PATCH /api/printers/{printer_id}`, `POST /api/printers` (+1 more)

### Community 48 - "Guia de Uso do PrinterControl"
Cohesion: 0.13
Nodes (14): Alertas — FUNCIONAL na leitura; PARCIAL nas ações, Como acessar, Configurações, Usuários e Integrações — COMING SOON, Dashboard — FUNCIONAL/PARCIAL, Exportar CSV — FUNCIONAL, Guia de Uso do PrinterControl, Histórico — PARCIAL, Interpretação dos dados (+6 more)

### Community 49 - "ConfigurarAmbiente.ps1"
Cohesion: 0.31
Nodes (4): Aviso(), Info(), Perguntar-Campo(), Perguntar-SimNao()

### Community 50 - "AppDataProvider"
Cohesion: 0.17
Nodes (14): public/data/monthly-report.json, public/data/printers.json, Arquivos de dados gerados são ignorados pelo git — gerar/apagar localmente nunca afeta o repositório, discoverPrinters(), fetchBackendEnvironment(), fetchUnreadNotificationCount(), AppDataProvider(), expireSession() (+6 more)

### Community 51 - "UsersView.tsx"
Cohesion: 0.13
Nodes (15): RequireRole(), FORM_VAZIO, formatarData(), FormState, UsersView(), abrirEdicao(), confirmarExclusao(), ApiUser (+7 more)

### Community 52 - "useAppData"
Cohesion: 0.15
Nodes (20): PrintersPage(), MustChangePasswordGate(), handleSubmit(), validar(), SettingsView(), trocarSenha(), validarSenha(), TEMAS (+12 more)

### Community 53 - "Guia do Desenvolvedor"
Cohesion: 0.13
Nodes (15): Backend, Banco, Comandos do frontend, Escanear Rede (implementado), Guia do Desenvolvedor, Já resolvido — não reabra, O que não executar em produção sem autorização, Print Server (+7 more)

### Community 54 - "NotificationsView.tsx"
Cohesion: 0.13
Nodes (19): FORM_VAZIO, formatarMomento(), FormState, ICONE_SEVERIDADE, NotificationsView(), abrirEnvio(), enviar(), marcarComoLida() (+11 more)

### Community 55 - "Role"
Cohesion: 0.20
Nodes (13): str, RBAC minimo (Fase 1). Tres papeis cobrem todas as rotas existentes hoje: -…, Role, migrar_dominio(), mostrar_senha_uma_vez(), obter_senha_admin(), Session, Semeia o banco: contas iniciais + a frota de printers_data.json. SENHAS (Fase… (+5 more)

### Community 56 - "Settings"
Cohesion: 0.11
Nodes (13): Config, field_validator, Fail-fast: producao nao sobe com simulacao ligada (Fase 9). O risco concreto e…, Impede que um ambiente de producao suba silenciosamente com o secret de…, Aceita "https://a.com, https://b.com" alem da lista JSON. Sem isto,…, Producao exige origens proprias e explicitas (Fase 10). Tres recusas, todas por…, Normaliza um DATABASE_URL sqlite relativo (ex.: sqlite:///./x.db) para um…, Um ambiente escrito errado nao pode cair no default em silencio:… (+5 more)

### Community 57 - "SNMPResult"
Cohesion: 0.10
Nodes (23): _empty_result(), _is_color(), _is_label(), _normalize_ip(), DiscoveredPrinter, Enriquecimento transitório de filas descobertas com telemetria SNMP., _result_for_ip(), MockSNMPScenarios (+15 more)

### Community 58 - "auth.ts"
Cohesion: 0.20
Nodes (19): handleSubmit(), salvarPerfil(), api, clearToken(), isTokenPersistent(), setToken(), ApiUser, cacheAccount() (+11 more)

### Community 60 - "theme.tsx"
Cohesion: 0.27
Nodes (8): lerPreferencia(), resolver(), sistemaEscuro(), Theme, ThemeContext, ThemeContextValue, ThemePreference, ThemeProvider()

### Community 61 - "Print Server"
Cohesion: 0.22
Nodes (9): `GET /api/servers`, `GET /api/servers/current`, `PATCH /api/servers/{server_id}`, `POST /api/servers`, `POST /api/servers/discover`, `POST /api/servers/{server_id}/discover`, `POST /api/servers/{server_id}/sync`, `POST /api/servers/sync` (+1 more)

### Community 62 - "Fluxo de Dados"
Cohesion: 0.17
Nodes (11): 10. Escanear Rede (implementado), 1. Cadastro no SQLite, 2. Coleta SNMP real, 3. Coleta de frota, 4. Print Server, 5. Sincronização, 6. Alertas, 7. Relatório mensal (+3 more)

### Community 63 - "enrich_discovered_printers"
Cohesion: 0.05
Nodes (41): enrich_discovered_printers(), EnrichedDiscoveredPrinter, Enriquece filas em memória; não recebe nem acessa uma sessão SQL., discover_printers(), DiscoveredPrinter, _escapar_powershell(), _mock_discover(), PrintServerError (+33 more)

### Community 64 - "Dívida técnica — registro único"
Cohesion: 0.11
Nodes (18): Como ler, D10 — O frontend não tem nenhum teste automatizado, D11 — O painel cai em dados de demonstração quando a API não responde, D12 — Datas ingênuas no servidor, hora do navegador no cliente, D13 — `/health` existe, mas nada o consulta, D14 — `httpx` sem teto de versão quebrava todas as suítes que usam `TestClient`, D15 — `requirements.txt` está em UTF-16, D16 — `backend/.env` em produção estava configurado como `demo`/`mock`, não `production` (+10 more)

### Community 65 - "ServerMode"
Cohesion: 0.67
Nodes (3): str, Modos aceitos, iguais aos de `settings.print_server_mode`., ServerMode

### Community 66 - "Autenticação"
Cohesion: 0.29
Nodes (7): Autenticação, Bloqueio de simulação em produção (Fase 9), `GET /api/auth/me`, `GET /health`, `PATCH /api/auth/me`, `POST /api/auth/change-password`, `POST /api/auth/login`

### Community 67 - "VISAO_GERAL.md"
Cohesion: 0.35
Nodes (3): Matriz de Funcionalidades, Itens que os documentos antigos listavam e que **já não existem**, Resolvido na Fase 10 (24/08/2026)

### Community 68 - "41. Scores, veredito e roadmap"
Cohesion: 0.25
Nodes (8): 10 perguntas respondidas objetivamente, 41. Scores, veredito e roadmap, Matriz de risco (resumo), Scores por categoria (0–10, com base apenas no que foi verificável), Seção de falsos positivos (obrigatória), Seção "não verificado" (obrigatória), Top 10 pontos fortes, Top 10 problemas

### Community 69 - "_migrate_printer_schema"
Cohesion: 0.29
Nodes (7): _finish_printer_migration(), _migrate_printer_schema(), Path, Caminho do arquivo .db atual, se o banco for SQLite em disco (nao :memory:)., Etapa 4 — reconstroi `printers` para trocar a identidade de `ip UNIQUE` para…, Recria `printers` (schema atual) e copia `printers_old` para dentro dela, numa…, _sqlite_backup_path()

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

### Community 80 - "Printer"
Cohesion: 0.14
Nodes (25): Alert, Printer, PrinterReading, SQLModel, Etapa 4: identidade e (server, name), NAO ip — o Print Server permite varias…, _active(), evaluate_reading(), Session (+17 more)

### Community 81 - "RODADA G — FECHAMENTO DE LACUNAS RESIDUAIS"
Cohesion: 0.29
Nodes (6): G1. LGPD — inventário técnico de dados pessoais, G2. CVE scan — executado onde seguro, sem alterar nada, G3. Itens "NÃO VERIFICADO" reavaliados — fechados nesta rodada, G4. Ajuste de score decorrente desta rodada, G5. Veredito — o que muda com esta rodada, RODADA G — FECHAMENTO DE LACUNAS RESIDUAIS

### Community 82 - "types.ts"
Cohesion: 0.14
Nodes (18): AlertsPage(), AlertBanner(), AlertBannerProps, AlertsView(), AlertsViewProps, config, PrinterStatusBadge(), PAGE_SIZE_OPTIONS (+10 more)

### Community 83 - "._limpar"
Cohesion: 0.22
Nodes (6): Consome credito. So a FALHA conta — login certo nao gasta nada., Zera as contagens apos um login BEM-SUCEDIDO. Sem isto, quem erra a senha…, Veredito de uma checagem. `retry_after` so faz sentido quando bloqueado., Descarta o que saiu da janela e devolve o que restou., Diz se a tentativa deve ser recusada — sem consumir credito. Separado de…, ResultadoLimite

### Community 84 - "6. Subir o sistema em produção hoje"
Cohesion: 0.22
Nodes (9): 6. Subir o sistema em produção hoje, Passo 1 — Preparar o `.env`, Passo 2 — Testar a configuração ANTES de subir, Passo 3 — Definir a senha das contas de administrador, Passo 4 — Backup antes de qualquer coisa, Passo 5 — Subir o backend, Passo 6 — Verificar a saúde, Passo 7 — Subir o painel (+1 more)

### Community 85 - "tests_environment.py"
Cohesion: 0.18
Nodes (11): PrintServer, SQLModel, Print Server como entidade (Fase 4). Ate aqui um Print Server existia de duas…, Fase 9 - Mock e Demo Seguros. Cobre as DUAS camadas que protegem o risco…, check(), check_true(), h(), main() (+3 more)

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

### Community 91 - "tests_printers_crud.py"
Cohesion: 0.33
Nodes (3): Etapa 12 - CRUD de impressoras contra o servidor rodando. Usa o banco REAL,…, Devolve (status, payload)., request()

### Community 93 - "tests_printer_fleet.py"
Cohesion: 0.12
Nodes (11): AsyncIOScheduler, Coleta agendada (Etapa 7; frota inteira desde a Etapa 5). APScheduler roda…, Um ciclo de coleta: toda a frota ativa, agrupada por IP…, Liga o scheduler conforme o .env. Retorna None quando desabilitado., run_collection_cycle(), shutdown_scheduler(), start_scheduler(), fake_real_collect() (+3 more)

### Community 94 - "RedactSecretsFilter"
Cohesion: 0.22
Nodes (8): _caminho_do_log(), Path, Substitui valores sensiveis na mensagem antes de ela ser emitida. Fica no…, Resolve settings.log_file. Vazio = so console., Instala console + arquivo rotativo na raiz do logging. Idempotente: chamar duas…, RedactSecretsFilter, setup_logging(), LogRecord

### Community 95 - "notify_alert"
Cohesion: 0.20
Nodes (11): get_alert(), list_alerts(), notify_alert(), get, patch, post, Session, Resolve um alerta. Ate a Fase 1 esta rota estava SEM protecao alguma — qualquer… (+3 more)

### Community 96 - "layout.tsx"
Cohesion: 0.29
Nodes (5): ibmPlexMono, metadata, publicSans, sourceSerif, Providers()

### Community 97 - "PrinterCollector"
Cohesion: 0.10
Nodes (15): PrinterCollector, Orquestrador da coleta de impressoras. Separa as tres responsabilidades da…, Cenarios de teste disponiveis (fonte unica: snmp_mock.SCENARIOS)., Coleta uma impressora e grava o resultado como PrinterReading., Args: mode: "real" (SNMP de verdade), "mock" (cenario fixo) ou "fleet" (frota…, MockSNMPClient, Substituto do SNMPClient com a mesma assinatura de collect()., Devolve o resultado fixo do cenario (ip e is_color sao ignorados). (+7 more)

### Community 98 - "Ações"
Cohesion: 0.33
Nodes (6): Acessar via web — PARCIAL, Adicionar impressora — AUSENTE/PARCIAL, Ações, Configurações — COMING SOON, Impressoras — FUNCIONAL/PARCIAL, Imprimir página de teste — SIMULADA

### Community 99 - "list_scenarios"
Cohesion: 0.40
Nodes (5): get_scheduler_status(), list_scenarios(), get, Cenarios simulados disponiveis e se o modo mock esta habilitado., Estado da coleta agendada (APScheduler).

### Community 100 - "C23. Terceiro passe — Frontend real (token/XSS/CSRF) e execução direta dos testes"
Cohesion: 0.40
Nodes (5): C23.1 Frontend — armazenamento de token, XSS, CSRF (corrige C1/C2-C3 de "NÃO VERIFICADO" para CONFIRMADO), C23.2 Execução real dos testes (corrige C19 com evidência de execução, não só inspeção estrutural), C23.3 Ajuste de score, C23.4 Seção "não verificado" — fecho, C23. Terceiro passe — Frontend real (token/XSS/CSRF) e execução direta dos testes

### Community 106 - "create_db_and_tables"
Cohesion: 0.09
Nodes (25): create_db_and_tables(), _migrate_alert_type(), _migrate_print_servers(), _migrate_reading_uptime(), _migrate_user_login_fields(), _migrate_user_rbac(), Etapa 7: adiciona printer_readings.uptime em bancos criados antes desta etapa.…, Fase 1 (RBAC): adiciona users.role e users.is_active em bancos criados antes… (+17 more)

## Knowledge Gaps
- **465 isolated node(s):** `Config`, `1. Resumo executivo (linguagem simples)`, `2. Inventário do repositório`, `3. Arquitetura`, `4. Segurança — Autenticação e Autorização` (+460 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SNMPClient` connect `SNMPClient` to `PrinterCollector`, `.collect_and_save`, `Printer`, `SNMPResult`, `tests_printer_fleet.py`, `enrich_discovered_printers`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Why does `SNMPResult` connect `SNMPResult` to `snmp_fleet_mock.py`, `PrinterCollector`, `SNMPClient`, `.collect_and_save`, `Printer`, `tests_printer_fleet.py`, `enrich_discovered_printers`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Why does `Printer` connect `Printer` to `PrinterCollector`, `scheduler_status`, `_migrate_printer_schema`, `servers.py`, `tests_rbac.py`, `database.py`, `create_db_and_tables`, `tests_printer_fleet.py`, `tests_environment.py`, `Role`, `schemas/printer.py`, `enrich_discovered_printers`, `notify_alert`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Are the 27 inferred relationships involving `User` (e.g. with `require_active_user()` and `require_roles()`) actually correct?**
  _`User` has 27 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `Printer` (e.g. with `_finish_printer_migration()` and `notify_alert()`) actually correct?**
  _`Printer` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `SNMPClient` (e.g. with `PrinterCollector` and `FakeAgent`) actually correct?**
  _`SNMPClient` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Config`, `1. Resumo executivo (linguagem simples)`, `2. Inventário do repositório` to the rest of the system?**
  _465 weakly-connected nodes found - possible documentation gaps or missing edges._