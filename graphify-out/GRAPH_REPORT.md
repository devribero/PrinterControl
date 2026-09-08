# Graph Report - PrinterControl  (2026-09-08)

## Corpus Check
- 188 files · ~200,721 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1950 nodes · 3714 edges · 127 communities (106 shown, 21 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 148 edges (avg confidence: 0.58)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `45da832a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- tests_qa_findings.py
- package.json
- Main.ps1
- Elgin Impressoras (painel de monitoramento)
- tests_environment.py
- enrich_discovered_printers
- compilerOptions
- servers.py
- AUDITORIA COMPLEMENTAR
- tests_login_hardening.py
- plugins
- app-data.tsx
- graphify (knowledge graph tool)
- next.config.ts
- Elgin (Brand)
- NotificationsView.tsx
- npm run build
- npm run dev
- next-env.d.ts
- navIds.ts
- cn
- printer_fleet.py
- tests_collect_api.py
- Cloudflare Tunnel — expor a API sem abrir porta (Fase 11)
- AUDITORIA MASTER — PrinterControl
- printers.py
- SNMPClient
- Operação em Produção
- Deploy do Frontend na Vercel (Fase 12)
- PageHeader.tsx
- models/user.py
- User
- create_notifications
- import_historico_planilha.py
- Printer
- ETAPA FINAL — FECHAMENTO DA AUDITORIA
- 2. Produção
- Settings
- layout.tsx
- Printer
- sync_server
- FakeAgent
- PLANO DE IMPLEMENTAÇÃO — ESCANEAR REDE REAL
- SECURITY ASSESSMENT — CYBERSECURITY 360°
- Impressoras
- Guia de Uso do PrinterControl
- ConfigurarAmbiente.ps1
- scheduler.py
- useAppData
- theme.tsx
- Guia do Desenvolvedor
- api.ts
- Handoff: PrinterControl — Glassmorphism UI System
- login
- SNMPResult
- auth.ts
- Contador mensal calculado por diff de duas leituras SNMP acumulativas (não existe OID de páginas do mês)
- alert_engine.py
- Print Server
- Fluxo de Dados
- record
- Dívida técnica — registro único
- services/print_server.py
- Autenticação
- VISAO_GERAL.md
- 41. Scores, veredito e roadmap
- UsersView.tsx
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
- File Structure
- RODADA G — FECHAMENTO DE LACUNAS RESIDUAIS
- File Structure
- tests_rbac.py
- 6. Subir o sistema em produção hoje
- Deliberate deviations from the handoff (documented, not silent)
- PrinterControl — Visão geral do sistema
- 5. Modo real x modo simulado, e os riscos
- notify_alert
- 1. Desenvolvimento (local)
- 2. Como o sistema é montado
- webhook_notifier.py
- Scripts PowerShell reais nunca rodaram de verdade (sem interpretador PowerShell no ambiente de dev)
- tests_fleet.py
- create_db_and_tables
- collect_printer
- tests_print_servers.py
- Scope decision
- Glassmorphism Redesign — Phase 3 (Suprimentos / Toner) Implementation Plan
- tests_webhook.py
- C23. Terceiro passe — Frontend real (token/XSS/CSRF) e execução direta dos testes
- RateLimiter
- unhandled_exception_handler
- Glassmorphism Redesign — Phases 4 & 5 (Alertas, Relatórios)
- scheduler_status
- update_server
- tests_login_username.py
- cybersecurity.agent.md
- relatorio.agent.md
- create_server
- hash_password
- Migração: Cloudflare Tunnel + Vercel → VM Windows Server própria
- Correção do acesso por IP em desenvolvimento
- Path
- Exception
- ambiente
- docs/README.md
- SQLModel
- str
- datetime
- Printer
- Notification
- database.py
- PrintServer

## God Nodes (most connected - your core abstractions)
1. `User` - 85 edges
2. `create_db_and_tables()` - 42 edges
3. `cn()` - 38 edges
4. `useAppData()` - 35 edges
5. `SNMPClient` - 35 edges
6. `Printer` - 35 edges
7. `Role` - 34 edges
8. `SNMPResult` - 30 edges
9. `hash_password()` - 29 edges
10. `useToast()` - 29 edges

## Surprising Connections (you probably didn't know these)
- `create_notifications()` --calls--> `Notification`  [EXTRACTED]
  backend/app/routes/notifications.py → src/types.ts
- `create_server()` --calls--> `PrintServer`  [EXTRACTED]
  backend/app/routes/servers.py → src/types.ts
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

## Communities (127 total, 21 thin omitted)

### Community 0 - "tests_qa_findings.py"
Cohesion: 0.43
Nodes (7): check(), check_true(), entrar(), h(), main(), Regressao dos achados da auditoria QA (08/09/2026). Um teste por achado…, semear()

### Community 1 - "package.json"
Cohesion: 0.06
Nodes (31): lucide-react, next, oxlint, dependencies, lucide-react, next, react, react-dom (+23 more)

### Community 2 - "Main.ps1"
Cohesion: 0.13
Nodes (29): Atualizar-ImpressorasAsync(), Build-ListaExibicaoAgrupada(), Build-SnmpGet(), Build-SnmpGetBulk(), Convert-SnmpValueBytes(), Get-ImpressorasEmpresa(), Get-TonerSNMP(), Import-Tabela() (+21 more)

### Community 3 - "Elgin Impressoras (painel de monitoramento)"
Cohesion: 0.07
Nodes (28): Tela Alertas, Tela Dashboard, Elgin Impressoras (painel de monitoramento), Tela Histórico, Tela Impressoras, Tela Login, Migração futura para FastAPI (Python) + Next.js + banco de dados, Modo claro/escuro (toggle) (+20 more)

### Community 4 - "tests_environment.py"
Cohesion: 0.09
Nodes (14): _caminho_do_log(), Path, Configuracao de log (Fase 10). Por que existe como modulo, e nao como um…, Instala console + arquivo rotativo na raiz do logging. Idempotente: chamar duas…, Substitui valores sensiveis na mensagem antes de ela ser emitida. Fica no…, Resolve settings.log_file. Vazio = so console., RedactSecretsFilter, setup_logging() (+6 more)

### Community 5 - "enrich_discovered_printers"
Cohesion: 0.17
Nodes (17): _empty_result(), enrich_discovered_printers(), EnrichedDiscoveredPrinter, _is_color(), _is_label(), _normalize_ip(), DiscoveredPrinter, Enriquecimento transitório de filas descobertas com telemetria SNMP. (+9 more)

### Community 6 - "compilerOptions"
Cohesion: 0.06
Nodes (30): dom, dom.iterable, esnext, .next/dev/types/**/*.ts, next-env.d.ts, .next/types/**/*.ts, node_modules, **/*.ts (+22 more)

### Community 7 - "servers.py"
Cohesion: 0.16
Nodes (19): discover(), DiscoveredPrinterResponse, DiscoverResponse, _executar_discover(), get_current_server(), list_servers(), PrintServerDelete, PrintServerResponse (+11 more)

### Community 8 - "AUDITORIA COMPLEMENTAR"
Cohesion: 0.08
Nodes (24): AUDITORIA COMPLEMENTAR, C10. Backup e Disaster Recovery — revisão significativa da rodada 1, C11. DevOps / CI-CD, C12. Supply Chain — aprofundamento, C13. PowerShell / Command Execution — reavaliação com evidência forte, C14. Segurança da API — inventário de endpoints (parcial, rotas mais sensíveis), C15. Autenticação — fluxo completo, C16. Banco de dados — schema (+16 more)

### Community 9 - "tests_login_hardening.py"
Cohesion: 0.22
Nodes (6): medir(), Fase 10 - endurecimento do login. Cobre as duas falhas levantadas na auditoria…, Request minimo: so o que _identificar_origem le., Tentativa com a contagem limpa — isola o caso do limite de tentativas., _Req, tentar()

### Community 10 - "plugins"
Cohesion: 0.22
Nodes (8): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, typescript, warn

### Community 11 - "app-data.tsx"
Cohesion: 0.06
Nodes (46): Levantamento_impressões (planilha original), public/data/monthly-report.json, public/data/printers.json, Arquivos de dados gerados são ignorados pelo git — gerar/apagar localmente nunca afeta o repositório, DepartmentBreakdown(), DepartmentBreakdownProps, DiscoveryResults(), DiscoveryResultsProps (+38 more)

### Community 12 - "graphify (knowledge graph tool)"
Cohesion: 0.25
Nodes (8): graphify (knowledge graph tool), graphify explain command, graphify path command, graphify query command, graphify update command, graphify-out/graph.json, graphify-out/GRAPH_REPORT.md, graphify-out/wiki/index.md

### Community 15 - "NotificationsView.tsx"
Cohesion: 0.11
Nodes (22): Modal(), ModalProps, FORM_VAZIO, formatarMomento(), FormState, ICONE_SEVERIDADE, NotificationsView(), abrirEnvio() (+14 more)

### Community 20 - "cn"
Cohesion: 0.06
Nodes (44): DashboardPage(), TonerPage(), AlertsDonutCard(), AlertsDonutCardProps, BottomCharts(), BottomChartsProps, PagesConsumedCard(), TotalPrintsCard() (+36 more)

### Community 21 - "printer_fleet.py"
Cohesion: 0.08
Nodes (27): PrinterCollector, PrinterReading, Session, Converte SNMPResult em PrinterReading. Toner ausente vira NULL (a coluna e…, Cenarios de teste disponiveis (fonte unica: snmp_mock.SCENARIOS)., Coleta uma impressora e grava o resultado como PrinterReading., Args: mode: "real" (SNMP de verdade), "mock" (cenario fixo) ou "fleet" (frota…, Deduz se a impressora e colorida — so um PALPITE inicial, usado para decidir a… (+19 more)

### Community 22 - "tests_collect_api.py"
Cohesion: 0.67
Nodes (3): check(), main(), Teste ponta a ponta dos endpoints /api/collect com os cenarios simulados.…

### Community 23 - "Cloudflare Tunnel — expor a API sem abrir porta (Fase 11)"
Cohesion: 0.13
Nodes (15): 10. Resumo do que muda em cada lugar, 1. Instalar o `cloudflared`, 2. Criar o túnel — caminho recomendado (via painel, com token), 3. Apontar o hostname para o backend, 4. Validar antes de seguir, 5. Confirmar que o serviço sobe sozinho, 6. Cabeçalhos de segurança — no Cloudflare, não no backend, 7. CORS — preenchido na Fase 12 (+7 more)

### Community 25 - "AUDITORIA MASTER — PrinterControl"
Cohesion: 0.10
Nodes (21): 10. Dependências e supply chain, 11. Performance e escalabilidade, 12. Testes, 13. Frontend, 14. LGPD / dados pessoais, 15. Observabilidade / auditoria / logs, 16. Backup / Disaster Recovery, 17. Threat Modeling (STRIDE) — resumo (+13 more)

### Community 28 - "printers.py"
Cohesion: 0.09
Nodes (35): create_printer(), create_printer_reading(), get_printer(), get_printer_readings(), _inicio_da_janela(), list_printers(), list_printers_with_status(), get (+27 more)

### Community 29 - "SNMPClient"
Cohesion: 0.08
Nodes (23): parse_varbinds(), Decodifica bytes BER como inteiro sem sinal., Extrai a lista de varbinds de uma resposta SNMP. Percorre a estrutura completa…, Cliente SNMP para coleta de impressoras (Printer-MIB, RFC 3805)., Coleta status, contador de paginas e toners de uma impressora. Nunca levanta…, PS1: `if ($ip -match '^\\d')` — descarta 'N/A' e nomes de porta., ICMP ping, equivalente ao `New-Object ...Ping).Send($ip, 400)` do PS1. SNMP…, Retorna (candidatos, houve_resposta_snmp). (+15 more)

### Community 30 - "Operação em Produção"
Cohesion: 0.11
Nodes (19): 1. Antes do primeiro deploy, 2. Instalar, 3. Dia a dia, 4. Diagnóstico, 5. Backup, 6. Recuperação — o que acontece se o processo cair, 7. Problemas comuns, 8. Dívida técnica conhecida — FK órfã para `printers_old` (+11 more)

### Community 31 - "Deploy do Frontend na Vercel (Fase 12)"
Cohesion: 0.25
Nodes (8): 1. O projeto já está pronto para este deploy, 2. Variáveis de ambiente para configurar na Vercel, 3. Conectar o repositório e fazer o primeiro deploy, 4. Validar, 5. Depois do deploy — atualizar o CORS do backend, 6. Redeploy — quando o código mudar, 7. Resumo — Fase 12 concluída, Deploy do Frontend na Vercel (Fase 12)

### Community 32 - "PageHeader.tsx"
Cohesion: 0.12
Nodes (9): AlertsPage(), PrintersPage(), AlertsView(), AlertsViewProps, ComingSoon(), ComingSoonProps, PageHeader(), PageHeaderProps (+1 more)

### Community 33 - "models/user.py"
Cohesion: 0.07
Nodes (45): RBAC minimo (Fase 1). Tres papeis cobrem todas as rotas existentes hoje: -…, Role, _active_admin_count(), create_user(), delete_user(), _ensure_not_last_admin(), list_users(), delete (+37 more)

### Community 34 - "User"
Cohesion: 0.09
Nodes (30): Fabrica de dependencia: exige que o usuario tenha (ou herde) um dos papeis…, require_roles(), True se o papel do usuario satisfaz qualquer um dos exigidos., User, get, Conta autenticada e seu papel — usado para decidir o que exibir/permitir., read_current_user(), get_scheduler_status() (+22 more)

### Community 35 - "create_notifications"
Cohesion: 0.09
Nodes (27): AlertRef, create_notifications(), list_notifications(), mark_all_as_read(), mark_as_read(), _minha_ou_404(), NotificationCreate, NotificationResponse (+19 more)

### Community 36 - "import_historico_planilha.py"
Cohesion: 0.14
Nodes (20): Grava ou atualiza o total de UM mes de UMA impressora — chave e (printer_id,…, upsert_printer_monthly(), _cell_value(), _e_cabecalho_de_site(), _e_linha_ip(), _e_linha_total(), importar_para_banco(), _ler_planilha() (+12 more)

### Community 37 - "Printer"
Cohesion: 0.12
Nodes (21): HistoryPage(), HistoryMatrix(), HistoryMatrixProps, PrinterDetailsModalProps, PrinterRanking(), PrinterRankingProps, RankedPrinter, RankList() (+13 more)

### Community 38 - "ETAPA FINAL — FECHAMENTO DA AUDITORIA"
Cohesion: 0.14
Nodes (14): Cálculo do score geral, ETAPA FINAL — FECHAMENTO DA AUDITORIA, F0. Auditorias realizadas nesta etapa, F1. Áreas finalmente cobertas (antes NÃO VERIFICADO por orçamento, agora CONFIRMADO), F2. Achados de UX — resumo consolidado, F3. Achados de acessibilidade — resumo consolidado, F4. Segurança da API — `alerts.py` e `notifications.py` (fecha C14), F4b. Backend — reforço de `auth.py`/`collect.py`/`printers.py`, grep de segurança final, concorrência dos DELETE novos (+6 more)

### Community 39 - "2. Produção"
Cohesion: 0.17
Nodes (12): 2. Produção, 3. Roteiro de teste em produção (amanhã), 4. Sinais de problema e como reagir, 5. Links e referências rápidas, Backup manual do banco, Como atualizar o sistema, Guia Rápido — PrinterControl, Logs (+4 more)

### Community 40 - "Settings"
Cohesion: 0.09
Nodes (17): Config, field_validator, Um ambiente escrito errado nao pode cair no default em silencio:…, Fail-fast: producao nao sobe com simulacao ligada (Fase 9). O risco concreto e…, Impede que um ambiente de producao suba silenciosamente com o secret de…, Aceita "https://a.com, https://b.com" alem da lista JSON. Sem isto,…, Mesmo tratamento de _cors_lista: aceita "127.0.0.1, ::1" alem de JSON. A…, Avisa (nao derruba) sobre a configuracao de proxy confiavel. Nao levanta… (+9 more)

### Community 41 - "layout.tsx"
Cohesion: 0.29
Nodes (5): ibmPlexMono, metadata, publicSans, sourceSerif, Providers()

### Community 42 - "Printer"
Cohesion: 0.20
Nodes (12): Printer, PrinterMonthly, PrinterReading, SQLModel, Etapa 4: identidade e (server, name), NAO ip — o Print Server permite varias…, Calculo de paginas por mes, compartilhado entre tres consumidores (Fase 12): -…, reading(), gravar() (+4 more)

### Community 43 - "sync_server"
Cohesion: 0.21
Nodes (16): delete_server(), discover_server(), _get_or_404(), _marcar_resultado(), delete, post, RecursoId, Session (+8 more)

### Community 44 - "FakeAgent"
Cohesion: 0.12
Nodes (13): Decodifica um OID BER para notacao pontuada., Le um TLV BER. Retorna (tag, length, value_start, next_pos)., _read_oid(), _read_tlv(), check(), FakeAgent, LocalSNMPClient, main() (+5 more)

### Community 45 - "PLANO DE IMPLEMENTAÇÃO — ESCANEAR REDE REAL"
Cohesion: 0.05
Nodes (39): A. Endpoint (implementado), Alertas, Arquitetura atual, Arquitetura do PrinterControl, B. Service reutilizável, Banco, C. Funções Print Server reutilizáveis, Cliente de API (+31 more)

### Community 46 - "SECURITY ASSESSMENT — CYBERSECURITY 360°"
Cohesion: 0.08
Nodes (24): Achados Detalhados, 🔴 ALTA PRIORIDADE (Implementar em 1-2 sprints), Avaliação por Domínio (Security Scorecard), ⚪ BAIXA PRIORIDADE (Considerar em roadmap), Conclusão, Escopo, Executive Summary, Limitações da Auditoria (+16 more)

### Community 47 - "Impressoras"
Cohesion: 0.22
Nodes (9): `GET /api/printers`, `GET /api/printers/monthly-report`, `GET /api/printers/{printer_id}`, `GET /api/printers/{printer_id}/readings`, `GET /api/printers/with-status`, Impressoras, `PATCH /api/printers/{printer_id}`, `POST /api/printers` (+1 more)

### Community 48 - "Guia de Uso do PrinterControl"
Cohesion: 0.10
Nodes (20): Acessar via web — PARCIAL, Adicionar impressora — AUSENTE/PARCIAL, Alertas — FUNCIONAL na leitura; PARCIAL nas ações, Ações, Como acessar, Configurações — COMING SOON, Configurações, Usuários e Integrações — COMING SOON, Dashboard — FUNCIONAL/PARCIAL (+12 more)

### Community 49 - "ConfigurarAmbiente.ps1"
Cohesion: 0.31
Nodes (4): Aviso(), Info(), Perguntar-Campo(), Perguntar-SimNao()

### Community 50 - "scheduler.py"
Cohesion: 0.13
Nodes (22): AsyncIOScheduler, monthly_report(), Contagem mensal por impressora, por mes e por departamento. Fase 12: mes ja…, month_bounds(), month_label(), month_period(), pages_from_readings(), datetime (+14 more)

### Community 51 - "useAppData"
Cohesion: 0.09
Nodes (34): react, ReportsPage(), AppShell(), AuthGate(), Login(), MustChangePasswordGate(), SettingsView(), trocarSenha() (+26 more)

### Community 52 - "theme.tsx"
Cohesion: 0.27
Nodes (8): lerPreferencia(), resolver(), sistemaEscuro(), Theme, ThemeContext, ThemeContextValue, ThemePreference, ThemeProvider()

### Community 53 - "Guia do Desenvolvedor"
Cohesion: 0.13
Nodes (15): Backend, Banco, Comandos do frontend, Escanear Rede (implementado), Guia do Desenvolvedor, Já resolvido — não reabra, O que não executar em produção sem autorização, Print Server (+7 more)

### Community 54 - "api.ts"
Cohesion: 0.05
Nodes (65): DecommissionedList(), DecommissionedListProps, formatarData(), adaptDiscovered(), FORM_VAZIO, formatarMomento(), MODOS, NetworkView() (+57 more)

### Community 55 - "Handoff: PrinterControl — Glassmorphism UI System"
Cohesion: 0.12
Nodes (16): About the Design Files, Background aurora, Base tokens, Design Tokens (critical — read this first), Fidelity, Files, Glassmorphism tokens, Handoff: PrinterControl — Glassmorphism UI System (+8 more)

### Community 56 - "login"
Cohesion: 0.18
Nodes (14): change_own_password(), _identificar_origem(), _ip_da_conexao(), login(), patch, post, Request, Session (+6 more)

### Community 57 - "SNMPResult"
Cohesion: 0.08
Nodes (21): Simulador de frota — APENAS PARA TESTE LOCAL. Diferenca para snmp_mock.py: la…, MockSNMPScenarios, Agente SNMP simulado — APENAS PARA TESTE LOCAL. Existe porque a maquina de…, SNMP responde o contador, mas nao expoe a tabela de consumiveis., Monocromatica com toner em 5%., Colorida com ciano critico (18%) e os demais normais., Contador reiniciado (troca de placa/formatador): page_count baixo., Cenarios de teste. Cada metodo devolve um SNMPResult completo. (+13 more)

### Community 58 - "auth.ts"
Cohesion: 0.12
Nodes (24): ACTIVE_NODES, features, handleSubmit(), LoginProps, NETWORK_LINKS, NETWORK_NODES, salvarPerfil(), api (+16 more)

### Community 60 - "alert_engine.py"
Cohesion: 0.14
Nodes (23): Alert, Alert, SQLModel, TonerHistory, Notification, SQLModel, Notificacoes internas (Fase 7). Por que uma tabela separada de `alerts`…, _active() (+15 more)

### Community 61 - "Print Server"
Cohesion: 0.22
Nodes (9): `GET /api/servers`, `GET /api/servers/current`, `PATCH /api/servers/{server_id}`, `POST /api/servers`, `POST /api/servers/discover`, `POST /api/servers/{server_id}/discover`, `POST /api/servers/{server_id}/sync`, `POST /api/servers/sync` (+1 more)

### Community 62 - "Fluxo de Dados"
Cohesion: 0.17
Nodes (11): 10. Escanear Rede (implementado), 1. Cadastro no SQLite, 2. Coleta SNMP real, 3. Coleta de frota, 4. Print Server, 5. Sincronização, 6. Alertas, 7. Relatório mensal (+3 more)

### Community 63 - "record"
Cohesion: 0.18
Nodes (12): Any, AuditLog, SQLModel, Trilha de auditoria administrativa (Fase 16). Registra QUEM fez, O QUE e QUANDO…, list_audit_log(), get, Session, Mais recentes primeiro. Filtros combinam com AND quando informados juntos. (+4 more)

### Community 64 - "Dívida técnica — registro único"
Cohesion: 0.11
Nodes (18): Como ler, D10 — O frontend não tem nenhum teste automatizado, D11 — O painel cai em dados de demonstração quando a API não responde, D12 — Datas ingênuas no servidor, hora do navegador no cliente, D13 — `/health` existe, mas nada o consulta, D14 — `httpx` sem teto de versão quebrava todas as suítes que usam `TestClient`, D15 — `requirements.txt` está em UTF-16, D16 — `backend/.env` em produção estava configurado como `demo`/`mock`, não `production` (+10 more)

### Community 65 - "services/print_server.py"
Cohesion: 0.06
Nodes (37): PrintServer, SQLModel, str, Print Server como entidade (Fase 4). Ate aqui um Print Server existia de duas…, Modos aceitos, iguais aos de `settings.print_server_mode`., ServerMode, discover_printers(), DiscoveredPrinter (+29 more)

### Community 66 - "Autenticação"
Cohesion: 0.29
Nodes (7): Autenticação, Bloqueio de simulação em produção (Fase 9), `GET /api/auth/me`, `GET /health`, `PATCH /api/auth/me`, `POST /api/auth/change-password`, `POST /api/auth/login`

### Community 67 - "VISAO_GERAL.md"
Cohesion: 0.35
Nodes (3): Matriz de Funcionalidades, Itens que os documentos antigos listavam e que **já não existem**, Resolvido na Fase 10 (24/08/2026)

### Community 68 - "41. Scores, veredito e roadmap"
Cohesion: 0.25
Nodes (8): 10 perguntas respondidas objetivamente, 41. Scores, veredito e roadmap, Matriz de risco (resumo), Scores por categoria (0–10, com base apenas no que foi verificável), Seção de falsos positivos (obrigatória), Seção "não verificado" (obrigatória), Top 10 pontos fortes, Top 10 problemas

### Community 69 - "UsersView.tsx"
Cohesion: 0.11
Nodes (22): FORM_VAZIO, formatarData(), FormState, UsersView(), abrirEdicao(), confirmarAtivacao(), confirmarExclusao(), salvar() (+14 more)

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

### Community 80 - "File Structure"
Cohesion: 0.17
Nodes (11): File Structure, Glassmorphism Redesign — Phase 0 (Foundation) Implementation Plan, Global Constraints, Roadmap (subsequent phases, planned individually before execution), Self-Review, Task 1: Design tokens, Task 2: Aurora background, Task 3: Reusable PageHeader component (+3 more)

### Community 81 - "RODADA G — FECHAMENTO DE LACUNAS RESIDUAIS"
Cohesion: 0.29
Nodes (6): G1. LGPD — inventário técnico de dados pessoais, G2. CVE scan — executado onde seguro, sem alterar nada, G3. Itens "NÃO VERIFICADO" reavaliados — fechados nesta rodada, G4. Ajuste de score decorrente desta rodada, G5. Veredito — o que muda com esta rodada, RODADA G — FECHAMENTO DE LACUNAS RESIDUAIS

### Community 82 - "File Structure"
Cohesion: 0.17
Nodes (11): File Structure, Glassmorphism Redesign — Phase 1 (Dashboard) Implementation Plan, Global Constraints, Roadmap (unchanged from Phase 0's plan), Self-Review, Task 1: Wire `PageHeader` into the Dashboard route, Task 2: Status dot semantics — `soft-pulse` keyframe + `PrinterStatusBadge` token fix, Task 3: Vitals strip (`VitalsStrip`, replaces `StatCards` + `AlertBanner`) (+3 more)

### Community 83 - "tests_rbac.py"
Cohesion: 0.24
Nodes (12): check(), check_true(), _confere_rbac_do_frontend(), h(), main(), Fase 1 - Autenticacao, RBAC e protecao das rotas. Diferente dos demais…, O frontend tem a sua propria copia da hierarquia de papeis, em…, Cria um banco no formato ANTERIOR a Fase 1 (users sem role/is_active), roda a… (+4 more)

### Community 84 - "6. Subir o sistema em produção hoje"
Cohesion: 0.22
Nodes (9): 6. Subir o sistema em produção hoje, Passo 1 — Preparar o `.env`, Passo 2 — Testar a configuração ANTES de subir, Passo 3 — Definir a senha das contas de administrador, Passo 4 — Backup antes de qualquer coisa, Passo 5 — Subir o backend, Passo 6 — Verificar a saúde, Passo 7 — Subir o painel (+1 more)

### Community 85 - "Deliberate deviations from the handoff (documented, not silent)"
Cohesion: 0.20
Nodes (9): Deliberate deviations from the handoff (documented, not silent), Glassmorphism Redesign — Phase 2 (Impressoras) Implementation Plan, Global Constraints (unchanged from Phases 0/1), Roadmap, Task 1: Wire `PageHeader` into `/printers`, Task 2: Table card header — status tabs + compact controls, Task 3: Row anatomy per handoff, Task 4: Pagination per handoff (+1 more)

### Community 86 - "PrinterControl — Visão geral do sistema"
Cohesion: 0.29
Nodes (7): 1. O que o sistema faz, 8. Onde está o resto da documentação, Como ele descobre isso, O ciclo, em uma frase, O detalhe que explica o relatório mensal, PrinterControl — Visão geral do sistema, Índice

### Community 87 - "5. Modo real x modo simulado, e os riscos"
Cohesion: 0.33
Nodes (6): 5. Modo real x modo simulado, e os riscos, As duas camadas de proteção, Como o sistema decide entre real e simulado, O problema em uma frase, O risco mais grave: sincronizar em modo simulado, Riscos corrigidos na Fase 10 (24/08/2026)

### Community 88 - "notify_alert"
Cohesion: 0.21
Nodes (12): get_alert(), list_alerts(), notify_alert(), get, patch, post, RecursoId, Session (+4 more)

### Community 89 - "1. Desenvolvimento (local)"
Cohesion: 0.22
Nodes (9): 1. Desenvolvimento (local), Acesso local, Credenciais de teste, Modo demo vs modo real (frontend), Pré-requisitos, Subir o backend, Subir o frontend, Testes em desenvolvimento (+1 more)

### Community 90 - "2. Como o sistema é montado"
Cohesion: 0.50
Nodes (4): 2. Como o sistema é montado, O "crachá" (token), O que cada tecnologia é, em uma linha, Por que duas peças, e não uma

### Community 91 - "webhook_notifier.py"
Cohesion: 0.32
Nodes (7): _build_adaptive_card(), Notificacao de alerta critico via webhook (Etapa 6). Equivalente a Send-…, Envia o Adaptive Card ao webhook configurado. Nunca levanta excecao — retorna…, Host da URL, para logar sem expor path/assinatura., Mesmo corpo de Send-AlertaWebhook (Main.ps1:1319): titulo/cor conforme manual…, _safe_host(), send_toner_alert_webhook()

### Community 93 - "tests_fleet.py"
Cohesion: 0.12
Nodes (12): _base_page_count(), _increment(), profile_for(), Perfil deterministico da impressora: online | offline | snmp_mudo | baixo |…, Contador inicial plausivel para uma impressora que nunca foi lida., Paginas impressas entre duas coletas — fixo por impressora, 5 a 124., Nivel do toner: base do perfil + desvio deterministico por impressora/cor,…, _toner() (+4 more)

### Community 94 - "create_db_and_tables"
Cohesion: 0.07
Nodes (27): create_db_and_tables(), _finish_printer_migration(), _migrate_alert_type(), _migrate_alert_value(), _migrate_child_foreign_keys(), _migrate_print_servers(), _migrate_printer_schema(), _migrate_user_login_fields() (+19 more)

### Community 95 - "collect_printer"
Cohesion: 0.21
Nodes (13): collect_fleet(), collect_printer(), CollectRequest, CollectResponse, FleetCollectResponse, BaseModel, post, RecursoId (+5 more)

### Community 96 - "tests_print_servers.py"
Cohesion: 0.39
Nodes (7): check(), check_true(), h(), main(), Fase 4 - Registro de Print Servers e operacao por servidor. Como…, Monta um banco no formato ANTERIOR a Fase 4 (printers sem print_server_id, sem…, _testa_migracao_legada()

### Community 97 - "Scope decision"
Cohesion: 0.22
Nodes (8): Follow-ups (not done here), Glassmorphism Redesign — Phase 6 (remaining screens) Implementation Plan, Scope decision, Task 1: Histórico, Task 2: Integrações, Task 3: Page headers on the four functional screens, Task 4: Retire the legacy token layer, Task 5: Verify

### Community 98 - "Glassmorphism Redesign — Phase 3 (Suprimentos / Toner) Implementation Plan"
Cohesion: 0.25
Nodes (7): Glassmorphism Redesign — Phase 3 (Suprimentos / Toner) Implementation Plan, Roadmap, Task 1: Extract `ScanBar`, Task 2: Page header on `/toner`, Task 3: Severity strip replaces the summary grid, Task 4: Table per handoff, Task 5: Verify

### Community 99 - "tests_webhook.py"
Cohesion: 0.29
Nodes (4): make_offline_reading(), make_reading(), PrinterReading, Etapa 6 - webhook de alerta critico de toner. Banco SQLite temporario e ISOLADO…

### Community 100 - "C23. Terceiro passe — Frontend real (token/XSS/CSRF) e execução direta dos testes"
Cohesion: 0.40
Nodes (5): C23.1 Frontend — armazenamento de token, XSS, CSRF (corrige C1/C2-C3 de "NÃO VERIFICADO" para CONFIRMADO), C23.2 Execução real dos testes (corrige C19 com evidência de execução, não só inspeção estrutural), C23.3 Ajuste de score, C23.4 Seção "não verificado" — fecho, C23. Terceiro passe — Frontend real (token/XSS/CSRF) e execução direta dos testes

### Community 101 - "RateLimiter"
Cohesion: 0.15
Nodes (10): RateLimiter, Limite de tentativas para o login (Fase 10). POR QUE existe --------------…, Consome credito. So a FALHA conta — login certo nao gasta nada., Zera as contagens apos um login BEM-SUCEDIDO. Sem isto, quem erra a senha…, Esvazia tudo. Existe para os testes; nao ha rota que chegue aqui., Veredito de uma checagem. `retry_after` so faz sentido quando bloqueado., Janela deslizante em memoria, protegida por lock. O lock existe porque o…, Descarta o que saiu da janela e devolve o que restou. (+2 more)

### Community 102 - "unhandled_exception_handler"
Cohesion: 0.40
Nodes (5): Request, Erro nao tratado: o detalhe vai para o log do servidor, o cliente recebe apenas…, unhandled_exception_handler(), Exception, exception_handler

### Community 103 - "Glassmorphism Redesign — Phases 4 & 5 (Alertas, Relatórios)"
Cohesion: 0.33
Nodes (5): Deliberate deviation, Glassmorphism Redesign — Phases 4 & 5 (Alertas, Relatórios), Phase 4 — Alertas, Phase 5 — Relatórios, Roadmap

### Community 105 - "scheduler_status"
Cohesion: 0.33
Nodes (6): health_check(), get, Saude, identificacao do ambiente (Fase 9) e diagnostico (Fase 10). O ambiente…, read_root(), Estado atual, para o endpoint de diagnostico., scheduler_status()

### Community 106 - "update_server"
Cohesion: 0.33
Nodes (5): PrintServerUpdate, patch, `host` fica de fora de proposito: ele e a chave natural que aparece em…, Altera rotulo, modo e ativacao. `host` nao muda (ver PrintServerUpdate)., update_server()

### Community 111 - "create_server"
Cohesion: 0.32
Nodes (5): create_server(), PrintServerCreate, field_validator, Registra um Print Server. O host e unico — e a chave natural., Recusa no cadastro o que a camada de execucao ja recusaria. O host e…

### Community 112 - "hash_password"
Cohesion: 0.10
Nodes (18): create_access_token(), hash_password(), Hash de senha e emissao/validacao do JWT. POR QUE PyJWT E NAO python-jose (Fase…, Assina o JWT. Quem chama passa `sub` (e-mail) e `ver` (User.token_version) — os…, Fase 16 - trilha de auditoria administrativa. Cobre: criar/editar/excluir…, Fase 12 - relatorio mensal: mescla PrinterMonthly (meses fechados, via…, Fase 16 - limite de taxa em acoes de rede (discover/sync/coleta), alem do…, Etapa 12 - CRUD de impressoras contra o servidor rodando. Usa o banco REAL,… (+10 more)

### Community 113 - "Migração: Cloudflare Tunnel + Vercel → VM Windows Server própria"
Cohesion: 0.17
Nodes (11): Atenção pré-existente (não é novidade desta migração), Backend, Caddy no Windows Server, Contexto, Corte (baixo risco, com fallback), Decisão central, Domínio, Firewall do Windows Server (+3 more)

### Community 114 - "Correção do acesso por IP em desenvolvimento"
Cohesion: 0.40
Nodes (4): Correção do acesso por IP em desenvolvimento, Design — 2026-09-08, Operação e critérios de aceite, Roadmap e backlog desta correção

### Community 125 - "database.py"
Cohesion: 0.09
Nodes (28): get_session(), _migrate_reading_uptime(), Etapa 7: adiciona printer_readings.uptime em bancos criados antes desta etapa.…, _sqlite_pragmas(), Session, rate_limited_action(), Dependencias compartilhadas pelas rotas. Autorizacao (Fase 1) fica CENTRALIZADA…, `require_user` + bloqueio de conta com troca de senha pendente. Toda rota do… (+20 more)

## Knowledge Gaps
- **552 isolated node(s):** `Config`, `Config`, `ModalProps`, `ServerFormState`, `FORM_VAZIO` (+547 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `tests_qa_findings.py`, `tests_environment.py`, `servers.py`, `tests_login_hardening.py`, `printers.py`, `models/user.py`, `create_notifications`, `Printer`, `sync_server`, `login`, `alert_engine.py`, `record`, `tests_rbac.py`, `notify_alert`, `create_db_and_tables`, `collect_printer`, `tests_print_servers.py`, `tests_webhook.py`, `update_server`, `tests_login_username.py`, `create_server`, `hash_password`, `database.py`?**
  _High betweenness centrality (0.145) - this node is a cross-community bridge._
- **Why does `create_server()` connect `create_server` to `User`, `servers.py`, `sync_server`, `app-data.tsx`, `collect_printer`, `record`?**
  _High betweenness centrality (0.130) - this node is a cross-community bridge._
- **Why does `PrintServer` connect `app-data.tsx` to `api.ts`, `create_server`?**
  _High betweenness centrality (0.129) - this node is a cross-community bridge._
- **Are the 46 inferred relationships involving `User` (e.g. with `rate_limited_action()` and `require_active_user()`) actually correct?**
  _`User` has 46 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `SNMPClient` (e.g. with `.collect_and_save()` and `.__init__()`) actually correct?**
  _`SNMPClient` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Config`, `Config`, `ModalProps` to the rest of the system?**
  _552 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.0625 - nodes in this community are weakly interconnected._