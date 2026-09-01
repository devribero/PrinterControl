# Graph Report - PrinterControl  (2026-08-31)

## Corpus Check
- 162 files · ~153,268 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1761 nodes · 3343 edges · 117 communities (99 shown, 18 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 124 edges (avg confidence: 0.58)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `69723639`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- snmp_fleet_mock.py
- package.json
- Main.ps1
- Elgin Impressoras (painel de monitoramento)
- api.ts
- enrich_discovered_printers
- compilerOptions
- servers.py
- AUDITORIA COMPLEMENTAR
- tests_login_hardening.py
- plugins
- printers.py
- graphify (knowledge graph tool)
- next.config.ts
- Elgin (Brand)
- NetworkView.tsx
- npm run build
- npm run dev
- next-env.d.ts
- navIds.ts
- cn
- unhandled_exception_handler
- tests_collect_api.py
- Cloudflare Tunnel — expor a API sem abrir porta (Fase 11)
- AUDITORIA MASTER — PrinterControl
- schemas/printer.py
- hash_password
- Operação em Produção
- Deploy do Frontend na Vercel (Fase 12)
- Printer
- users.py
- User
- notifications.py
- import_historico_planilha.py
- TonerMonitoring.tsx
- ETAPA FINAL — FECHAMENTO DA AUDITORIA
- 1. Desenvolvimento (local)
- tests_rbac.py
- database.py
- SNMPClient
- types.ts
- models/user.py
- PLANO DE IMPLEMENTAÇÃO — ESCANEAR REDE REAL
- Alert
- Impressoras
- Guia de Uso do PrinterControl
- ConfigurarAmbiente.ps1
- app-data.tsx
- UsersView.tsx
- useAppData
- Guia do Desenvolvedor
- NotificationsView
- services/print_server.py
- Settings
- SNMPResult
- auth.ts
- Contador mensal calculado por diff de duas leituras SNMP acumulativas (não existe OID de páginas do mês)
- theme.tsx
- Print Server
- Fluxo de Dados
- DiscoveredPrinter
- Dívida técnica — registro único
- printer_sync.py
- Autenticação
- VISAO_GERAL.md
- 41. Scores, veredito e roadmap
- Path
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
- AlertsView.tsx
- PrinterTable.tsx
- 6. Subir o sistema em produção hoje
- tests_environment.py
- PrinterControl — Visão geral do sistema
- 5. Modo real x modo simulado, e os riscos
- ambiente
- PrinterCollector
- 2. Como o sistema é montado
- printers.ts
- Scripts PowerShell reais nunca rodaram de verdade (sem interpretador PowerShell no ambiente de dev)
- tests_printer_fleet.py
- tests_production.py
- notify_alert
- SettingsView.tsx
- list_scenarios
- scheduler.py
- collect_printer
- C23. Terceiro passe — Frontend real (token/XSS/CSRF) e execução direta dos testes
- discovery.py
- Exception
- Request
- start_scheduler
- create_db_and_tables
- _migrate_printer_schema
- layout.tsx
- Alert
- SQLModel
- Session
- require_user
- Ações
- get
- patch
- post

## God Nodes (most connected - your core abstractions)
1. `User` - 49 edges
2. `cn()` - 39 edges
3. `SNMPClient` - 37 edges
4. `useAppData()` - 35 edges
5. `SNMPResult` - 31 edges
6. `Printer` - 30 edges
7. `create_db_and_tables()` - 30 edges
8. `useToast()` - 29 edges
9. `Alert` - 27 edges
10. `Printer` - 25 edges

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

## Communities (117 total, 18 thin omitted)

### Community 0 - "snmp_fleet_mock.py"
Cohesion: 0.12
Nodes (15): _base_page_count(), FleetMockClient, _increment(), profile_for(), Simulador de frota — APENAS PARA TESTE LOCAL. Diferenca para snmp_mock.py: la…, Perfil deterministico da impressora: online | offline | snmp_mudo | baixo |…, Contador inicial plausivel para uma impressora que nunca foi lida., Paginas impressas entre duas coletas — fixo por impressora, 5 a 124. (+7 more)

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
Cohesion: 0.08
Nodes (27): adaptPrinter(), ApiMonthlyReport, formatLastSeen(), toStatus(), toToner(), VALID_COLORS, VALID_STATUS, ApiAlert (+19 more)

### Community 5 - "enrich_discovered_printers"
Cohesion: 0.27
Nodes (7): enrich_discovered_printers(), Enriquece filas em memória; não recebe nem acessa uma sessão SQL., DiscoverySnmpTests, printer(), DiscoveredPrinter, Testes locais do enriquecimento SNMP, sem rede corporativa ou SQLite., result()

### Community 6 - "compilerOptions"
Cohesion: 0.06
Nodes (30): dom, dom.iterable, esnext, .next/dev/types/**/*.ts, next-env.d.ts, .next/types/**/*.ts, node_modules, **/*.ts (+22 more)

### Community 7 - "servers.py"
Cohesion: 0.08
Nodes (48): create_server(), delete_server(), discover(), discover_server(), DiscoveredPrinterResponse, DiscoverResponse, _executar_discover(), get_current_server() (+40 more)

### Community 8 - "AUDITORIA COMPLEMENTAR"
Cohesion: 0.08
Nodes (24): AUDITORIA COMPLEMENTAR, C10. Backup e Disaster Recovery — revisão significativa da rodada 1, C11. DevOps / CI-CD, C12. Supply Chain — aprofundamento, C13. PowerShell / Command Execution — reavaliação com evidência forte, C14. Segurança da API — inventário de endpoints (parcial, rotas mais sensíveis), C15. Autenticação — fluxo completo, C16. Banco de dados — schema (+16 more)

### Community 9 - "tests_login_hardening.py"
Cohesion: 0.09
Nodes (16): RateLimiter, Limite de tentativas para o login (Fase 10). POR QUE existe --------------…, Consome credito. So a FALHA conta — login certo nao gasta nada., Zera as contagens apos um login BEM-SUCEDIDO. Sem isto, quem erra a senha…, Esvazia tudo. Existe para os testes; nao ha rota que chegue aqui., Veredito de uma checagem. `retry_after` so faz sentido quando bloqueado., Janela deslizante em memoria, protegida por lock. O lock existe porque o…, Descarta o que saiu da janela e devolve o que restou. (+8 more)

### Community 10 - "plugins"
Cohesion: 0.22
Nodes (8): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, typescript, warn

### Community 11 - "printers.py"
Cohesion: 0.14
Nodes (23): create_printer(), create_printer_reading(), get_printer(), get_printer_readings(), _inicio_da_janela(), list_printers(), list_printers_with_status(), monthly_report() (+15 more)

### Community 12 - "graphify (knowledge graph tool)"
Cohesion: 0.25
Nodes (8): graphify (knowledge graph tool), graphify explain command, graphify path command, graphify query command, graphify update command, graphify-out/graph.json, graphify-out/GRAPH_REPORT.md, graphify-out/wiki/index.md

### Community 15 - "NetworkView.tsx"
Cohesion: 0.08
Nodes (30): DiscoveryResults(), DiscoveryResultsProps, statusLabel(), adaptDiscovered(), FORM_VAZIO, formatarMomento(), MODOS, NetworkView() (+22 more)

### Community 20 - "cn"
Cohesion: 0.12
Nodes (21): DashboardPage(), AlertsDonutCard(), AlertsDonutCardProps, PagesConsumedCard(), TotalPrintsCard(), NavItem(), NavItemProps, Sidebar() (+13 more)

### Community 21 - "unhandled_exception_handler"
Cohesion: 0.33
Nodes (6): Erro nao tratado: o detalhe vai para o log do servidor, o cliente recebe apenas…, unhandled_exception_handler(), PlanilhaError, Exception, exception_handler, Request

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
Cohesion: 0.14
Nodes (16): Config, PrinterCreate, PrinterReadingCreate, PrinterReadingResponse, PrinterResponse, PrinterUpdate, PrinterWithStatus, BaseModel (+8 more)

### Community 29 - "hash_password"
Cohesion: 0.16
Nodes (12): create_access_token(), hash_password(), Hash de senha e emissao/validacao do JWT. POR QUE PyJWT E NAO python-jose (Fase…, check(), check_true(), h(), main(), Fase 7 - Notificacoes internas. Como… (+4 more)

### Community 30 - "Operação em Produção"
Cohesion: 0.11
Nodes (18): 1. Antes do primeiro deploy, 2. Instalar, 3. Dia a dia, 4. Diagnóstico, 5. Backup, 6. Recuperação — o que acontece se o processo cair, 7. Problemas comuns, 8. Dívida técnica conhecida — FK órfã para `printers_old` (+10 more)

### Community 31 - "Deploy do Frontend na Vercel (Fase 12)"
Cohesion: 0.25
Nodes (8): 1. O projeto já está pronto para este deploy, 2. Variáveis de ambiente para configurar na Vercel, 3. Conectar o repositório e fazer o primeiro deploy, 4. Validar, 5. Depois do deploy — atualizar o CORS do backend, 6. Redeploy — quando o código mudar, 7. Resumo — Fase 12 concluída, Deploy do Frontend na Vercel (Fase 12)

### Community 32 - "Printer"
Cohesion: 0.18
Nodes (11): HistoryMatrix(), HistoryMatrixProps, PrinterDetailsModalProps, PrinterRanking(), PrinterRankingProps, RankedPrinter, RankList(), rankPrinters() (+3 more)

### Community 33 - "users.py"
Cohesion: 0.08
Nodes (37): _active_admin_count(), create_user(), delete_user(), _ensure_not_last_admin(), list_users(), delete, get, patch (+29 more)

### Community 34 - "User"
Cohesion: 0.11
Nodes (28): Fabrica de dependencia: exige que o usuario tenha (ou herde) um dos papeis…, require_roles(), True se o papel do usuario satisfaz qualquer um dos exigidos., User, change_own_password(), _identificar_origem(), login(), get (+20 more)

### Community 35 - "notifications.py"
Cohesion: 0.10
Nodes (31): Notification, SQLModel, Notificacoes internas (Fase 7). Por que uma tabela separada de `alerts`…, AlertRef, create_notifications(), list_notifications(), mark_all_as_read(), mark_as_read() (+23 more)

### Community 36 - "import_historico_planilha.py"
Cohesion: 0.17
Nodes (16): _cell_value(), _e_cabecalho_de_site(), _e_linha_ip(), _e_linha_total(), importar_para_banco(), _ler_planilha(), LinhaImpressora, main() (+8 more)

### Community 37 - "TonerMonitoring.tsx"
Cohesion: 0.12
Nodes (16): PrinterDetailsModal(), config, PrinterStatusBadge(), PrinterTable(), classify(), FILTERS, SummaryCard(), SummaryCardProps (+8 more)

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
Cohesion: 0.14
Nodes (19): get_session(), _sqlite_pragmas(), Dependencias compartilhadas pelas rotas. Autorizacao (Fase 1) fica CENTRALIZADA…, `require_user` + bloqueio de conta com troca de senha pendente. Toda rota do…, require_active_user(), lifespan(), Coleta manual de impressoras (Etapa 6). Sem agendamento: cada chamada dispara…, Guarda de ambiente (Fase 9) — impede simulacao em producao. Complementa, e nao… (+11 more)

### Community 42 - "SNMPClient"
Cohesion: 0.05
Nodes (37): parse_varbinds(), Decodifica um OID BER para notacao pontuada., Decodifica bytes BER como inteiro sem sinal., Extrai a lista de varbinds de uma resposta SNMP. Percorre a estrutura completa…, Cliente SNMP para coleta de impressoras (Printer-MIB, RFC 3805)., Coleta status, contador de paginas e toners de uma impressora. Nunca levanta…, PS1: `if ($ip -match '^\\d')` — descarta 'N/A' e nomes de porta., ICMP ping, equivalente ao `New-Object ...Ping).Send($ip, 400)` do PS1. SNMP… (+29 more)

### Community 43 - "types.ts"
Cohesion: 0.16
Nodes (13): BottomChartsProps, DemoDataBadge(), DemoDataBadgeProps, DepartmentBreakdown(), DepartmentBreakdownProps, MonthlyCounters(), MonthlyCountersProps, DepartmentUsage (+5 more)

### Community 44 - "models/user.py"
Cohesion: 0.13
Nodes (15): SQLModel, str, RBAC minimo (Fase 1). Tres papeis cobrem todas as rotas existentes hoje: -…, Role, migrar_dominio(), mostrar_senha_uma_vez(), obter_senha_admin(), Session (+7 more)

### Community 45 - "PLANO DE IMPLEMENTAÇÃO — ESCANEAR REDE REAL"
Cohesion: 0.05
Nodes (39): A. Endpoint (implementado), Alertas, Arquitetura atual, Arquitetura do PrinterControl, B. Service reutilizável, Banco, C. Funções Print Server reutilizáveis, Cliente de API (+31 more)

### Community 46 - "Alert"
Cohesion: 0.12
Nodes (23): Alert, TonerHistory, _active(), evaluate_reading(), _notify_all_active_users(), PrinterReading, Alertas automaticos (Etapa 8A, re-alerta de toner na Fase 11). Roda logo apos…, Fan-out de uma Notification por usuario ativo (Fase 11) — e o canal "site" dos… (+15 more)

### Community 47 - "Impressoras"
Cohesion: 0.22
Nodes (9): `GET /api/printers`, `GET /api/printers/monthly-report`, `GET /api/printers/{printer_id}`, `GET /api/printers/{printer_id}/readings`, `GET /api/printers/with-status`, Impressoras, `PATCH /api/printers/{printer_id}`, `POST /api/printers` (+1 more)

### Community 48 - "Guia de Uso do PrinterControl"
Cohesion: 0.13
Nodes (14): Alertas — FUNCIONAL na leitura; PARCIAL nas ações, Como acessar, Configurações, Usuários e Integrações — COMING SOON, Dashboard — FUNCIONAL/PARCIAL, Exportar CSV — FUNCIONAL, Guia de Uso do PrinterControl, Histórico — PARCIAL, Interpretação dos dados (+6 more)

### Community 49 - "ConfigurarAmbiente.ps1"
Cohesion: 0.31
Nodes (4): Aviso(), Info(), Perguntar-Campo(), Perguntar-SimNao()

### Community 50 - "app-data.tsx"
Cohesion: 0.12
Nodes (27): public/data/monthly-report.json, public/data/printers.json, Arquivos de dados gerados são ignorados pelo git — gerar/apagar localmente nunca afeta o repositório, adaptAlert(), loadMonthlyReportFromApi(), BackendEnvironment, discoverPrinters(), fetchAlerts() (+19 more)

### Community 51 - "UsersView.tsx"
Cohesion: 0.09
Nodes (26): ComingSoon(), ComingSoonProps, abrirEnvio(), RequireRole(), FORM_VAZIO, formatarData(), FormState, UsersView() (+18 more)

### Community 52 - "useAppData"
Cohesion: 0.09
Nodes (31): react, HistoryPage(), PrintersPage(), ReportsPage(), TonerPage(), AppShell(), AuthGate(), Modal() (+23 more)

### Community 53 - "Guia do Desenvolvedor"
Cohesion: 0.13
Nodes (15): Backend, Banco, Comandos do frontend, Escanear Rede (implementado), Guia do Desenvolvedor, Já resolvido — não reabra, O que não executar em produção sem autorização, Print Server (+7 more)

### Community 54 - "NotificationsView"
Cohesion: 0.16
Nodes (11): formatarMomento(), NotificationsView(), enviar(), marcarComoLida(), marcarTodasComoLidas(), validar(), adaptNotification(), createNotifications() (+3 more)

### Community 55 - "services/print_server.py"
Cohesion: 0.18
Nodes (13): _escapar_powershell(), PrintServerError, Exception, Camada de Print Server (Etapa 3). Reproduz a descoberta de impressoras do…, Executa um comando PowerShell que termina em `ConvertTo-Json` e devolve sempre…, Equivalente exato de Get-ImpressorasEmpresa + o inicio de Process-…, RPC ao Print Server falhou ou saida do PowerShell nao pode ser interpretada., Devolve o host se for hostname/FQDN/IPv4 valido; levanta PrintServerError caso… (+5 more)

### Community 56 - "Settings"
Cohesion: 0.11
Nodes (13): Config, field_validator, Fail-fast: producao nao sobe com simulacao ligada (Fase 9). O risco concreto e…, Impede que um ambiente de producao suba silenciosamente com o secret de…, Aceita "https://a.com, https://b.com" alem da lista JSON. Sem isto,…, Producao exige origens proprias e explicitas (Fase 10). Tres recusas, todas por…, Normaliza um DATABASE_URL sqlite relativo (ex.: sqlite:///./x.db) para um…, Um ambiente escrito errado nao pode cair no default em silencio:… (+5 more)

### Community 57 - "SNMPResult"
Cohesion: 0.12
Nodes (16): MockSNMPScenarios, Agente SNMP simulado — APENAS PARA TESTE LOCAL. Existe porque a maquina de…, SNMP responde o contador, mas nao expoe a tabela de consumiveis., Monocromatica com toner em 5%., Colorida com ciano critico (18%) e os demais normais., Contador reiniciado (troca de placa/formatador): page_count baixo., Cenarios de teste. Cada metodo devolve um SNMPResult completo., Monocromatica saudavel. (+8 more)

### Community 58 - "auth.ts"
Cohesion: 0.11
Nodes (25): ACTIVE_NODES, features, Login(), handleSubmit(), LoginProps, NETWORK_LINKS, NETWORK_NODES, salvarPerfil() (+17 more)

### Community 60 - "theme.tsx"
Cohesion: 0.27
Nodes (8): lerPreferencia(), resolver(), sistemaEscuro(), Theme, ThemeContext, ThemeContextValue, ThemePreference, ThemeProvider()

### Community 61 - "Print Server"
Cohesion: 0.22
Nodes (9): `GET /api/servers`, `GET /api/servers/current`, `PATCH /api/servers/{server_id}`, `POST /api/servers`, `POST /api/servers/discover`, `POST /api/servers/{server_id}/discover`, `POST /api/servers/{server_id}/sync`, `POST /api/servers/sync` (+1 more)

### Community 62 - "Fluxo de Dados"
Cohesion: 0.17
Nodes (11): 10. Escanear Rede (implementado), 1. Cadastro no SQLite, 2. Coleta SNMP real, 3. Coleta de frota, 4. Print Server, 5. Sincronização, 6. Alertas, 7. Relatório mensal (+3 more)

### Community 63 - "DiscoveredPrinter"
Cohesion: 0.12
Nodes (6): DiscoveredPrinter, _mock_discover(), Uma linha do que Get-Printer + Get-PrinterPort devolveriam, combinadas., Frota simulada. Inclui de proposito: - drivers que casam as regras de Obter-…, PrintServerDiscoveryTests, Testes isolados da descoberta do Print Server, sem rede ou banco real.

### Community 64 - "Dívida técnica — registro único"
Cohesion: 0.11
Nodes (18): Como ler, D10 — O frontend não tem nenhum teste automatizado, D11 — O painel cai em dados de demonstração quando a API não responde, D12 — Datas ingênuas no servidor, hora do navegador no cliente, D13 — `/health` existe, mas nada o consulta, D14 — `httpx` sem teto de versão quebrava todas as suítes que usam `TestClient`, D15 — `requirements.txt` está em UTF-16, D16 — `backend/.env` em produção estava configurado como `demo`/`mock`, não `production` (+10 more)

### Community 65 - "printer_sync.py"
Cohesion: 0.16
Nodes (14): discover_printers(), Descobre as impressoras publicadas em um Print Server. `server` e `mode` sao…, obter_modelo(), obter_tipo_impressora(), Regras de classificacao portadas do Main.ps1 (Etapa 4). Correspondencia exata:…, Traduz DriverName (Windows) em nome comercial, igual ao Main.ps1., Classifica A4 / Etiqueta / Portatil a partir de Nome+Modelo, igual ao Main.ps1., Session (+6 more)

### Community 66 - "Autenticação"
Cohesion: 0.29
Nodes (7): Autenticação, Bloqueio de simulação em produção (Fase 9), `GET /api/auth/me`, `GET /health`, `PATCH /api/auth/me`, `POST /api/auth/change-password`, `POST /api/auth/login`

### Community 67 - "VISAO_GERAL.md"
Cohesion: 0.35
Nodes (3): Matriz de Funcionalidades, Itens que os documentos antigos listavam e que **já não existem**, Resolvido na Fase 10 (24/08/2026)

### Community 68 - "41. Scores, veredito e roadmap"
Cohesion: 0.25
Nodes (8): 10 perguntas respondidas objetivamente, 41. Scores, veredito e roadmap, Matriz de risco (resumo), Scores por categoria (0–10, com base apenas no que foi verificável), Seção de falsos positivos (obrigatória), Seção "não verificado" (obrigatória), Top 10 pontos fortes, Top 10 problemas

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
Cohesion: 0.17
Nodes (18): Printer, PrinterMonthly, PrinterReading, SQLModel, Etapa 4: identidade e (server, name), NAO ip — o Print Server permite varias…, Orquestrador da coleta de impressoras. Separa as tres responsabilidades da…, collect_fleet(), _collect_ip_network() (+10 more)

### Community 81 - "RODADA G — FECHAMENTO DE LACUNAS RESIDUAIS"
Cohesion: 0.29
Nodes (6): G1. LGPD — inventário técnico de dados pessoais, G2. CVE scan — executado onde seguro, sem alterar nada, G3. Itens "NÃO VERIFICADO" reavaliados — fechados nesta rodada, G4. Ajuste de score decorrente desta rodada, G5. Veredito — o que muda com esta rodada, RODADA G — FECHAMENTO DE LACUNAS RESIDUAIS

### Community 82 - "AlertsView.tsx"
Cohesion: 0.31
Nodes (5): AlertsPage(), AlertBannerProps, AlertsView(), AlertsViewProps, Alert

### Community 83 - "PrinterTable.tsx"
Cohesion: 0.36
Nodes (8): PAGE_SIZE_OPTIONS, PrinterTableProps, DEFAULT_FILTERS, filterPrinters(), PrinterFilters, getPrinterType(), PrinterType, PrinterStatus

### Community 84 - "6. Subir o sistema em produção hoje"
Cohesion: 0.22
Nodes (9): 6. Subir o sistema em produção hoje, Passo 1 — Preparar o `.env`, Passo 2 — Testar a configuração ANTES de subir, Passo 3 — Definir a senha das contas de administrador, Passo 4 — Backup antes de qualquer coisa, Passo 5 — Subir o backend, Passo 6 — Verificar a saúde, Passo 7 — Subir o painel (+1 more)

### Community 85 - "tests_environment.py"
Cohesion: 0.13
Nodes (14): PrintServer, SQLModel, str, Print Server como entidade (Fase 4). Ate aqui um Print Server existia de duas…, Modos aceitos, iguais aos de `settings.print_server_mode`., ServerMode, Fase 9 - Mock e Demo Seguros. Cobre as DUAS camadas que protegem o risco…, check() (+6 more)

### Community 86 - "PrinterControl — Visão geral do sistema"
Cohesion: 0.29
Nodes (7): 1. O que o sistema faz, 8. Onde está o resto da documentação, Como ele descobre isso, O ciclo, em uma frase, O detalhe que explica o relatório mensal, PrinterControl — Visão geral do sistema, Índice

### Community 87 - "5. Modo real x modo simulado, e os riscos"
Cohesion: 0.33
Nodes (6): 5. Modo real x modo simulado, e os riscos, As duas camadas de proteção, Como o sistema decide entre real e simulado, O problema em uma frase, O risco mais grave: sincronizar em modo simulado, Riscos corrigidos na Fase 10 (24/08/2026)

### Community 89 - "PrinterCollector"
Cohesion: 0.10
Nodes (16): PrinterCollector, Printer, Session, Converte SNMPResult em PrinterReading. Toner ausente vira NULL (a coluna e…, Cenarios de teste disponiveis (fonte unica: snmp_mock.SCENARIOS)., Coleta uma impressora e grava o resultado como PrinterReading., Args: mode: "real" (SNMP de verdade), "mock" (cenario fixo) ou "fleet" (frota…, Deduz se a impressora e colorida a partir do modelo/nome (regra do PS1). (+8 more)

### Community 90 - "2. Como o sistema é montado"
Cohesion: 0.50
Nodes (4): 2. Como o sistema é montado, O "crachá" (token), O que cada tecnologia é, em uma linha, Por que duas peças, e não uma

### Community 91 - "printers.ts"
Cohesion: 0.14
Nodes (15): Levantamento_impressões (planilha original), DecommissionedList(), DecommissionedListProps, RightPanel(), RightPanelProps, DecommissionedPrinter, decommissionedPrinters, DEPARTMENT_PERIODS (+7 more)

### Community 93 - "tests_printer_fleet.py"
Cohesion: 0.18
Nodes (4): fake_real_collect(), Etapa 5 - orquestracao da frota (printer_fleet.collect_fleet). Roda sobre um…, RecordingThreadPoolExecutor, _OriginalTPE

### Community 94 - "tests_production.py"
Cohesion: 0.12
Nodes (13): _caminho_do_log(), Path, Configuracao de log (Fase 10). Por que existe como modulo, e nao como um…, Substitui valores sensiveis na mensagem antes de ela ser emitida. Fica no…, Resolve settings.log_file. Vazio = so console., Instala console + arquivo rotativo na raiz do logging. Idempotente: chamar duas…, RedactSecretsFilter, setup_logging() (+5 more)

### Community 95 - "notify_alert"
Cohesion: 0.20
Nodes (11): get_alert(), list_alerts(), notify_alert(), get, patch, post, Session, Resolve um alerta. Ate a Fase 1 esta rota estava SEM protecao alguma — qualquer… (+3 more)

### Community 96 - "SettingsView.tsx"
Cohesion: 0.14
Nodes (16): handleSubmit(), validar(), SettingsView(), trocarSenha(), validarSenha(), TEMAS, API_BASE_URL, changeMyPassword() (+8 more)

### Community 97 - "list_scenarios"
Cohesion: 0.18
Nodes (11): health_check(), get, Saude, identificacao do ambiente (Fase 9) e diagnostico (Fase 10). O ambiente…, read_root(), get_scheduler_status(), list_scenarios(), get, Cenarios simulados disponiveis e se o modo mock esta habilitado. (+3 more)

### Community 98 - "scheduler.py"
Cohesion: 0.18
Nodes (16): month_bounds(), month_period(), pages_from_readings(), datetime, Session, Calculo de paginas por mes, compartilhado entre tres consumidores (Fase 12): -…, 2026-08' — chave de mes usada em PrinterMonthly.month e nas respostas da API., Primeiro instante do mes de `dt` e primeiro instante do mes seguinte (limite… (+8 more)

### Community 99 - "collect_printer"
Cohesion: 0.27
Nodes (10): collect_fleet(), collect_printer(), CollectRequest, CollectResponse, FleetCollectResponse, BaseModel, post, Session (+2 more)

### Community 100 - "C23. Terceiro passe — Frontend real (token/XSS/CSRF) e execução direta dos testes"
Cohesion: 0.40
Nodes (5): C23.1 Frontend — armazenamento de token, XSS, CSRF (corrige C1/C2-C3 de "NÃO VERIFICADO" para CONFIRMADO), C23.2 Execução real dos testes (corrige C19 com evidência de execução, não só inspeção estrutural), C23.3 Ajuste de score, C23.4 Seção "não verificado" — fecho, C23. Terceiro passe — Frontend real (token/XSS/CSRF) e execução direta dos testes

### Community 101 - "discovery.py"
Cohesion: 0.39
Nodes (8): _empty_result(), EnrichedDiscoveredPrinter, _is_color(), _is_label(), _normalize_ip(), DiscoveredPrinter, Enriquecimento transitório de filas descobertas com telemetria SNMP., _result_for_ip()

### Community 105 - "start_scheduler"
Cohesion: 0.33
Nodes (7): AsyncIOScheduler, Liga o scheduler conforme o .env. Retorna None quando desabilitado., Um ciclo de coleta: toda a frota ativa, agrupada por IP…, Dia 1 de cada mes, de madrugada: forca um ciclo de coleta extra so para…, run_collection_cycle(), run_month_start_snapshot(), start_scheduler()

### Community 106 - "create_db_and_tables"
Cohesion: 0.13
Nodes (19): create_db_and_tables(), _migrate_alert_type(), _migrate_alert_value(), _migrate_print_servers(), _migrate_reading_uptime(), _migrate_user_login_fields(), _migrate_user_rbac(), Adiciona alerts.value em bancos criados antes da escada de re-alerta de toner.… (+11 more)

### Community 107 - "_migrate_printer_schema"
Cohesion: 0.29
Nodes (7): _finish_printer_migration(), _migrate_printer_schema(), Caminho do arquivo .db atual, se o banco for SQLite em disco (nao :memory:)., Etapa 4 — reconstroi `printers` para trocar a identidade de `ip UNIQUE` para…, Recria `printers` (schema atual) e copia `printers_old` para dentro dela, numa…, _sqlite_backup_path(), Path

### Community 108 - "layout.tsx"
Cohesion: 0.29
Nodes (5): ibmPlexMono, metadata, publicSans, sourceSerif, Providers()

### Community 112 - "require_user"
Cohesion: 0.33
Nodes (6): Session, Usuario dono do JWT do header Authorization. 401 se ausente/invalido. O usuario…, require_user(), decode_token(), Devolve {"email": ...} para um token valido, ou None. `algorithms` e uma lista…, HTTPAuthorizationCredentials

### Community 113 - "Ações"
Cohesion: 0.33
Nodes (6): Acessar via web — PARCIAL, Adicionar impressora — AUSENTE/PARCIAL, Ações, Configurações — COMING SOON, Impressoras — FUNCIONAL/PARCIAL, Imprimir página de teste — SIMULADA

## Knowledge Gaps
- **465 isolated node(s):** `DEPARTMENT_PERIODS`, `VALID_STATUS`, `VALID_COLORS`, `ApiMonthlyReport`, `AppDataContext` (+460 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SNMPClient` connect `SNMPClient` to `enrich_discovered_printers`, `discovery.py`, `Printer`, `PrinterCollector`, `tests_printer_fleet.py`, `SNMPResult`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Why does `Settings` connect `Settings` to `tests_rbac.py`, `database.py`, `tests_environment.py`, `tests_production.py`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **Why does `User` connect `User` to `list_scenarios`, `collect_printer`, `notifications.py`, `tests_rbac.py`, `database.py`, `tests_login_hardening.py`, `create_db_and_tables`, `models/user.py`, `require_user`, `Printer`, `tests_environment.py`, `hash_password`, `notify_alert`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **Are the 24 inferred relationships involving `User` (e.g. with `require_active_user()` and `require_roles()`) actually correct?**
  _`User` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `SNMPClient` (e.g. with `PrinterCollector` and `FakeAgent`) actually correct?**
  _`SNMPClient` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `SNMPResult` (e.g. with `enrich_discovered_printers()` and `PrinterCollector`) actually correct?**
  _`SNMPResult` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `DEPARTMENT_PERIODS`, `VALID_STATUS`, `VALID_COLORS` to the rest of the system?**
  _465 weakly-connected nodes found - possible documentation gaps or missing edges._