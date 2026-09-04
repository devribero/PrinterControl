# Graph Report - glassmorphism-redesign-phase0  (2026-09-04)

## Corpus Check
- 182 files · ~178,272 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1880 nodes · 3725 edges · 115 communities (102 shown, 13 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 157 edges (avg confidence: 0.51)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b585e589`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- snmp_fleet_mock.py
- package.json
- Main.ps1
- Elgin Impressoras (painel de monitoramento)
- logging_config.py
- enrich_discovered_printers
- compilerOptions
- User
- AUDITORIA COMPLEMENTAR
- tests_login_hardening.py
- plugins
- app-data.tsx
- graphify (knowledge graph tool)
- next.config.ts
- Elgin (Brand)
- NetworkView.tsx
- npm run build
- npm run dev
- next-env.d.ts
- navIds.ts
- theme.tsx
- Printer
- tests_collect_api.py
- Cloudflare Tunnel — expor a API sem abrir porta (Fase 11)
- AUDITORIA MASTER — PrinterControl
- printers.py
- SNMPClient
- Operação em Produção
- Deploy do Frontend na Vercel (Fase 12)
- app/page.tsx
- routes/auth.py
- hash_password
- notifications.py
- import_historico_planilha.py
- types.ts
- ETAPA FINAL — FECHAMENTO DA AUDITORIA
- 1. Desenvolvimento (local)
- tests_rbac.py
- layout.tsx
- snmp.py
- DecommissionedList.tsx
- FakeAgent
- PLANO DE IMPLEMENTAÇÃO — ESCANEAR REDE REAL
- SECURITY ASSESSMENT — CYBERSECURITY 360°
- Impressoras
- Guia de Uso do PrinterControl
- ConfigurarAmbiente.ps1
- PrinterReading
- useAppData
- preferences.tsx
- Guia do Desenvolvedor
- api.ts
- Role
- Settings
- MockSNMPScenarios
- auth.ts
- Contador mensal calculado por diff de duas leituras SNMP acumulativas (não existe OID de páginas do mês)
- alert_engine.py
- Print Server
- Fluxo de Dados
- record
- Dívida técnica — registro único
- config.py
- Autenticação
- VISAO_GERAL.md
- 41. Scores, veredito e roadmap
- UsersView
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
- dependencies.py
- 6. Subir o sistema em produção hoje
- Deliberate deviations from the handoff (documented, not silent)
- PrinterControl — Visão geral do sistema
- 5. Modo real x modo simulado, e os riscos
- tests_production.py
- RecordingThreadPoolExecutor
- 2. Como o sistema é montado
- discovery.py
- Scripts PowerShell reais nunca rodaram de verdade (sem interpretador PowerShell no ambiente de dev)
- models/user.py
- database.py
- collect.py
- PrintServerDiscoveryTests
- Scope decision
- Glassmorphism Redesign — Phase 3 (Suprimentos / Toner) Implementation Plan
- seed.py
- C23. Terceiro passe — Frontend real (token/XSS/CSRF) e execução direta dos testes
- field_validator
- unhandled_exception_handler
- Glassmorphism Redesign — Phases 4 & 5 (Alertas, Relatórios)
- public/data/monthly-report.json
- tests_profile.py
- ServerMode
- cybersecurity.agent.md
- relatorio.agent.md
- Migração: Cloudflare Tunnel + Vercel → VM Windows Server própria
- ambiente
- main.py
- Ações

## God Nodes (most connected - your core abstractions)
1. `User` - 82 edges
2. `Printer` - 58 edges
3. `create_db_and_tables()` - 38 edges
4. `cn()` - 38 edges
5. `SNMPClient` - 37 edges
6. `useAppData()` - 35 edges
7. `SNMPResult` - 34 edges
8. `PrinterReading` - 32 edges
9. `Role` - 32 edges
10. `Alert` - 29 edges

## Surprising Connections (you probably didn't know these)
- `notifications()` --uses--> `Notification`  [INFERRED]
  backend/tests_alerts.py → backend/app/models/notification.py
- `Lucide` --conceptually_related_to--> `Elgin Impressoras (painel de monitoramento)`  [EXTRACTED]
  README.md → CONTEXTO-DESENVOLVIMENTO.md
- `React` --conceptually_related_to--> `Elgin Impressoras (painel de monitoramento)`  [EXTRACTED]
  README.md → CONTEXTO-DESENVOLVIMENTO.md
- `Recharts` --conceptually_related_to--> `Elgin Impressoras (painel de monitoramento)`  [EXTRACTED]
  README.md → CONTEXTO-DESENVOLVIMENTO.md
- `Tailwind CSS v4` --conceptually_related_to--> `Elgin Impressoras (painel de monitoramento)`  [EXTRACTED]
  README.md → CONTEXTO-DESENVOLVIMENTO.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Comandos do CLI graphify (query/path/explain/update)** — claude_graphify, claude_graphify_query, claude_graphify_path, claude_graphify_explain, claude_graphify_update [EXTRACTED 1.00]
- **Stack tecnológico do painel (Vite/React/TS/Tailwind/Recharts/Lucide)** — readme_vite, readme_react, readme_typescript, readme_tailwind_css_v4, readme_recharts, readme_lucide [EXTRACTED 1.00]
- **Arquitetura de dados de 3 modos (Demo/Real/Simulado)** — contexto_desenvolvimento_elgin_impressoras, contexto_desenvolvimento_modo_demo, contexto_desenvolvimento_modo_real, contexto_desenvolvimento_modo_simulado [EXTRACTED 1.00]

## Communities (115 total, 13 thin omitted)

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
Cohesion: 0.08
Nodes (24): Tela Alertas, Tela Dashboard, Elgin Impressoras (painel de monitoramento), Tela Histórico, Tela Impressoras, Tela Login, Migração futura para FastAPI (Python) + Next.js + banco de dados, Modo claro/escuro (toggle) (+16 more)

### Community 4 - "logging_config.py"
Cohesion: 0.22
Nodes (9): _caminho_do_log(), Path, Configuracao de log (Fase 10). Por que existe como modulo, e nao como um…, Instala console + arquivo rotativo na raiz do logging. Idempotente: chamar duas…, Substitui valores sensiveis na mensagem antes de ela ser emitida. Fica no…, Resolve settings.log_file. Vazio = so console., RedactSecretsFilter, setup_logging() (+1 more)

### Community 5 - "enrich_discovered_printers"
Cohesion: 0.27
Nodes (7): enrich_discovered_printers(), Enriquece filas em memória; não recebe nem acessa uma sessão SQL., DiscoverySnmpTests, printer(), DiscoveredPrinter, Testes locais do enriquecimento SNMP, sem rede corporativa ou SQLite., result()

### Community 6 - "compilerOptions"
Cohesion: 0.06
Nodes (30): dom, dom.iterable, esnext, .next/dev/types/**/*.ts, next-env.d.ts, .next/types/**/*.ts, node_modules, **/*.ts (+22 more)

### Community 7 - "User"
Cohesion: 0.07
Nodes (52): rate_limited_action(), Fabrica de dependencia: limita quantas vezes UM usuario pode disparar UMA acao…, PrintServer, True se o papel do usuario satisfaz qualquer um dos exigidos., User, create_printer_reading(), Grava uma leitura A MAO. Bloqueada em ENVIRONMENT=production. Esta rota era a…, create_server() (+44 more)

### Community 8 - "AUDITORIA COMPLEMENTAR"
Cohesion: 0.08
Nodes (24): AUDITORIA COMPLEMENTAR, C10. Backup e Disaster Recovery — revisão significativa da rodada 1, C11. DevOps / CI-CD, C12. Supply Chain — aprofundamento, C13. PowerShell / Command Execution — reavaliação com evidência forte, C14. Segurança da API — inventário de endpoints (parcial, rotas mais sensíveis), C15. Autenticação — fluxo completo, C16. Banco de dados — schema (+16 more)

### Community 9 - "tests_login_hardening.py"
Cohesion: 0.09
Nodes (16): RateLimiter, Limite de tentativas para o login (Fase 10). POR QUE existe --------------…, Consome credito. So a FALHA conta — login certo nao gasta nada., Zera as contagens apos um login BEM-SUCEDIDO. Sem isto, quem erra a senha…, Esvazia tudo. Existe para os testes; nao ha rota que chegue aqui., Veredito de uma checagem. `retry_after` so faz sentido quando bloqueado., Janela deslizante em memoria, protegida por lock. O lock existe porque o…, Descarta o que saiu da janela e devolve o que restou. (+8 more)

### Community 10 - "plugins"
Cohesion: 0.22
Nodes (8): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, typescript, warn

### Community 11 - "app-data.tsx"
Cohesion: 0.08
Nodes (39): Levantamento_impressões (planilha original), RightPanelProps, decommissionedPrinters, DEPARTMENT_PERIODS, departmentUsage, globalToner, monthlyUsage, printers (+31 more)

### Community 12 - "graphify (knowledge graph tool)"
Cohesion: 0.25
Nodes (8): graphify (knowledge graph tool), graphify explain command, graphify path command, graphify query command, graphify update command, graphify-out/graph.json, graphify-out/GRAPH_REPORT.md, graphify-out/wiki/index.md

### Community 15 - "NetworkView.tsx"
Cohesion: 0.09
Nodes (30): DiscoveryResults(), DiscoveryResultsProps, statusLabel(), adaptDiscovered(), FORM_VAZIO, formatarMomento(), MODOS, NetworkView() (+22 more)

### Community 20 - "theme.tsx"
Cohesion: 0.07
Nodes (35): Logo Elgin é redesenho à mão (IA sem acesso a imagens coladas no chat, só uploads), src/components/ (padrão com header-comment por arquivo), AlertsDonutCard(), AlertsDonutCardProps, BottomChartsProps, PagesConsumedCard(), TotalPrintsCard(), DemoDataBadge() (+27 more)

### Community 21 - "Printer"
Cohesion: 0.06
Nodes (46): AsyncIOScheduler, Printer, Etapa 4: identidade e (server, name), NAO ip — o Print Server permite varias…, PrinterCollector, Printer, Session, Converte SNMPResult em PrinterReading. Toner ausente vira NULL (a coluna e…, Coleta uma impressora e grava o resultado como PrinterReading. (+38 more)

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
Cohesion: 0.07
Nodes (46): create_printer(), get_printer(), get_printer_readings(), _inicio_da_janela(), list_printers(), list_printers_with_status(), monthly_report(), datetime (+38 more)

### Community 29 - "SNMPClient"
Cohesion: 0.13
Nodes (11): Cliente SNMP para coleta de impressoras (Printer-MIB, RFC 3805)., Coleta status, contador de paginas e toners de uma impressora. Nunca levanta…, PS1: `if ($ip -match '^\\d')` — descarta 'N/A' e nomes de porta., ICMP ping, equivalente ao `New-Object ...Ping).Send($ip, 400)` do PS1. SNMP…, Escolhe os toners finais. PS1 colorida: um por cor (primeiro de cada grupo),…, GET de uma OCTET STRING., Envia um GET e devolve o primeiro varbind valido da resposta., SNMPv1 GET (PS1: Build-SnmpGet, version 0, PDU 0xA0). (+3 more)

### Community 30 - "Operação em Produção"
Cohesion: 0.11
Nodes (19): 1. Antes do primeiro deploy, 2. Instalar, 3. Dia a dia, 4. Diagnóstico, 5. Backup, 6. Recuperação — o que acontece se o processo cair, 7. Problemas comuns, 8. Dívida técnica conhecida — FK órfã para `printers_old` (+11 more)

### Community 31 - "Deploy do Frontend na Vercel (Fase 12)"
Cohesion: 0.25
Nodes (8): 1. O projeto já está pronto para este deploy, 2. Variáveis de ambiente para configurar na Vercel, 3. Conectar o repositório e fazer o primeiro deploy, 4. Validar, 5. Depois do deploy — atualizar o CORS do backend, 6. Redeploy — quando o código mudar, 7. Resumo — Fase 12 concluída, Deploy do Frontend na Vercel (Fase 12)

### Community 32 - "app/page.tsx"
Cohesion: 0.08
Nodes (19): HistoryPage(), DashboardPage(), PrintersPage(), TonerPage(), BottomCharts(), ComingSoon(), ComingSoonProps, HistoryMatrix() (+11 more)

### Community 33 - "routes/auth.py"
Cohesion: 0.11
Nodes (28): change_own_password(), _identificar_origem(), login(), get, patch, post, Request, Session (+20 more)

### Community 34 - "hash_password"
Cohesion: 0.12
Nodes (18): create_access_token(), hash_password(), Hash de senha e emissao/validacao do JWT. POR QUE PyJWT E NAO python-jose (Fase…, verify_password(), Fase 16 - trilha de auditoria administrativa. Cobre: criar/editar/excluir…, Fase 16 - limite de taxa em acoes de rede (discover/sync/coleta), alem do…, Etapa 12 - CRUD de impressoras contra o servidor rodando. Usa o banco REAL,…, Devolve (status, payload). (+10 more)

### Community 35 - "notifications.py"
Cohesion: 0.10
Nodes (31): Notification, SQLModel, Notificacoes internas (Fase 7). Por que uma tabela separada de `alerts`…, AlertRef, create_notifications(), list_notifications(), mark_all_as_read(), mark_as_read() (+23 more)

### Community 36 - "import_historico_planilha.py"
Cohesion: 0.15
Nodes (18): _cell_value(), _e_cabecalho_de_site(), _e_linha_ip(), _e_linha_total(), importar_para_banco(), _ler_planilha(), LinhaImpressora, main() (+10 more)

### Community 37 - "types.ts"
Cohesion: 0.08
Nodes (38): AlertsPage(), AlertsView(), AlertsViewProps, PrinterDetailsModal(), PrinterDetailsModalProps, PrinterRanking(), PrinterRankingProps, RankedPrinter (+30 more)

### Community 38 - "ETAPA FINAL — FECHAMENTO DA AUDITORIA"
Cohesion: 0.14
Nodes (14): Cálculo do score geral, ETAPA FINAL — FECHAMENTO DA AUDITORIA, F0. Auditorias realizadas nesta etapa, F1. Áreas finalmente cobertas (antes NÃO VERIFICADO por orçamento, agora CONFIRMADO), F2. Achados de UX — resumo consolidado, F3. Achados de acessibilidade — resumo consolidado, F4. Segurança da API — `alerts.py` e `notifications.py` (fecha C14), F4b. Backend — reforço de `auth.py`/`collect.py`/`printers.py`, grep de segurança final, concorrência dos DELETE novos (+6 more)

### Community 39 - "1. Desenvolvimento (local)"
Cohesion: 0.10
Nodes (21): 1. Desenvolvimento (local), 2. Produção, 3. Roteiro de teste em produção (amanhã), 4. Sinais de problema e como reagir, 5. Links e referências rápidas, Acesso local, Backup manual do banco, Como atualizar o sistema (+13 more)

### Community 40 - "tests_rbac.py"
Cohesion: 0.24
Nodes (12): check(), check_true(), _confere_rbac_do_frontend(), h(), main(), Fase 1 - Autenticacao, RBAC e protecao das rotas. Diferente dos demais…, O frontend tem a sua propria copia da hierarquia de papeis, em…, Cria um banco no formato ANTERIOR a Fase 1 (users sem role/is_active), roda a… (+4 more)

### Community 41 - "layout.tsx"
Cohesion: 0.29
Nodes (5): ibmPlexMono, metadata, publicSans, sourceSerif, Providers()

### Community 42 - "snmp.py"
Cohesion: 0.15
Nodes (13): SNMP Collector para impressoras. Porte direto da funcao Get-TonerSNMP de…, Decodifica bytes BER como inteiro sem sinal., Retorna (candidatos, houve_resposta_snmp)., GETBULK das tres colunas de uma vez (PS1: Build-SnmpGetBulk)., Fallback: um GET por indice (PS1: laco 1..20 com 3 falhas seguidas)., Aplica os filtros do PS1 e monta um candidato a toner., Cor pela descricao; se nao identificar e for colorida, usa indice % 4., GET de um valor numerico (INTEGER, Counter32, Gauge32, TimeTicks). (+5 more)

### Community 43 - "DecommissionedList.tsx"
Cohesion: 0.60
Nodes (4): DecommissionedList(), DecommissionedListProps, formatarData(), DecommissionedPrinter

### Community 44 - "FakeAgent"
Cohesion: 0.11
Nodes (15): parse_varbinds(), Decodifica um OID BER para notacao pontuada., Extrai a lista de varbinds de uma resposta SNMP. Percorre a estrutura completa…, Le um TLV BER. Retorna (tag, length, value_start, next_pos)., _read_oid(), _read_tlv(), check(), FakeAgent (+7 more)

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
Cohesion: 0.13
Nodes (14): Alertas — FUNCIONAL na leitura; PARCIAL nas ações, Como acessar, Configurações, Usuários e Integrações — COMING SOON, Dashboard — FUNCIONAL/PARCIAL, Exportar CSV — FUNCIONAL, Guia de Uso do PrinterControl, Histórico — PARCIAL, Interpretação dos dados (+6 more)

### Community 49 - "ConfigurarAmbiente.ps1"
Cohesion: 0.31
Nodes (4): Aviso(), Info(), Perguntar-Campo(), Perguntar-SimNao()

### Community 50 - "PrinterReading"
Cohesion: 0.12
Nodes (13): PrinterMonthly, PrinterReading, SQLModel, gravar(), Fase 17 - pages_from_readings() soma saltos positivos entre leituras…, Uma leitura por valor, em ordem, minutos entre elas., Fase 12 - relatorio mensal: mescla PrinterMonthly (meses fechados, via…, Fase 12 - fechamento mensal automatico do scheduler. Cobre: os dois jobs novos… (+5 more)

### Community 51 - "useAppData"
Cohesion: 0.09
Nodes (35): react, ReportsPage(), AppShell(), AuthGate(), DepartmentBreakdown(), DepartmentBreakdownProps, Modal(), ModalProps (+27 more)

### Community 52 - "preferences.tsx"
Cohesion: 0.29
Nodes (7): ESCALAS, ler(), Preferences, PreferencesContext, PreferencesContextValue, PreferencesProvider(), PREFERENCIAS_PADRAO

### Community 53 - "Guia do Desenvolvedor"
Cohesion: 0.13
Nodes (15): Backend, Banco, Comandos do frontend, Escanear Rede (implementado), Guia do Desenvolvedor, Já resolvido — não reabra, O que não executar em produção sem autorização, Print Server (+7 more)

### Community 54 - "api.ts"
Cohesion: 0.06
Nodes (48): FORM_VAZIO, formatarMomento(), FormState, ICONE_SEVERIDADE, NotificationsView(), abrirEnvio(), enviar(), marcarComoLida() (+40 more)

### Community 55 - "Role"
Cohesion: 0.10
Nodes (29): str, RBAC minimo (Fase 1). Tres papeis cobrem todas as rotas existentes hoje: -…, Role, _active_admin_count(), create_user(), delete_user(), _ensure_not_last_admin(), list_users() (+21 more)

### Community 56 - "Settings"
Cohesion: 0.15
Nodes (9): Config, Fail-fast: producao nao sobe com simulacao ligada (Fase 9). O risco concreto e…, Impede que um ambiente de producao suba silenciosamente com o secret de…, Producao exige origens proprias e explicitas (Fase 10). Tres recusas, todas por…, Settings, Settings de producao valida, sobrescrevendo so o que o teste investiga., settings_de_producao(), BaseSettings (+1 more)

### Community 57 - "MockSNMPScenarios"
Cohesion: 0.12
Nodes (12): MockSNMPScenarios, SNMP responde o contador, mas nao expoe a tabela de consumiveis., Monocromatica com toner em 5%., Colorida com ciano critico (18%) e os demais normais., Contador reiniciado (troca de placa/formatador): page_count baixo., Cenarios de teste. Cada metodo devolve um SNMPResult completo., Monocromatica saudavel., Colorida saudavel (4 toners, ordem C, M, Y, K). (+4 more)

### Community 58 - "auth.ts"
Cohesion: 0.11
Nodes (28): ACTIVE_NODES, features, Login(), handleSubmit(), LoginProps, NETWORK_LINKS, NETWORK_NODES, FormState (+20 more)

### Community 60 - "alert_engine.py"
Cohesion: 0.15
Nodes (20): Alert, _active(), evaluate_reading(), _notify_all_active_users(), Session, Alertas automaticos (Etapa 8A, re-alerta de toner na Fase 11). Roda logo apos…, Fan-out de uma Notification por usuario ativo (Fase 11) — e o canal "site" dos…, Avalia uma leitura e sincroniza os alertas da impressora. Faz commit ao final.… (+12 more)

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

### Community 65 - "config.py"
Cohesion: 0.09
Nodes (32): discover_printers(), DiscoveredPrinter, _escapar_powershell(), _mock_discover(), PrintServerError, Exception, Camada de Print Server (Etapa 3). Reproduz a descoberta de impressoras do…, Uma linha do que Get-Printer + Get-PrinterPort devolveriam, combinadas. (+24 more)

### Community 66 - "Autenticação"
Cohesion: 0.29
Nodes (7): Autenticação, Bloqueio de simulação em produção (Fase 9), `GET /api/auth/me`, `GET /health`, `PATCH /api/auth/me`, `POST /api/auth/change-password`, `POST /api/auth/login`

### Community 67 - "VISAO_GERAL.md"
Cohesion: 0.35
Nodes (3): Matriz de Funcionalidades, Itens que os documentos antigos listavam e que **já não existem**, Resolvido na Fase 10 (24/08/2026)

### Community 68 - "41. Scores, veredito e roadmap"
Cohesion: 0.25
Nodes (8): 10 perguntas respondidas objetivamente, 41. Scores, veredito e roadmap, Matriz de risco (resumo), Scores por categoria (0–10, com base apenas no que foi verificável), Seção de falsos positivos (obrigatória), Seção "não verificado" (obrigatória), Top 10 pontos fortes, Top 10 problemas

### Community 69 - "UsersView"
Cohesion: 0.18
Nodes (10): formatarData(), UsersView(), abrirEdicao(), confirmarAtivacao(), confirmarExclusao(), salvar(), validar(), createUser() (+2 more)

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

### Community 83 - "dependencies.py"
Cohesion: 0.10
Nodes (14): get_session(), Session, Dependencias compartilhadas pelas rotas. Autorizacao (Fase 1) fica CENTRALIZADA…, Fabrica de dependencia: exige que o usuario tenha (ou herde) um dos papeis…, Usuario dono do JWT do header Authorization. 401 se ausente/invalido. O usuario…, `require_user` + bloqueio de conta com troca de senha pendente. Toda rota do…, require_active_user(), require_roles() (+6 more)

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

### Community 88 - "tests_production.py"
Cohesion: 0.22
Nodes (4): producao(), Fase 10 - Preparacao para producao corporativa. Cobre o que protege a exposicao…, Sobe um processo separado e diz se a configuracao foi aceita., subir_com_ambiente()

### Community 90 - "2. Como o sistema é montado"
Cohesion: 0.50
Nodes (4): 2. Como o sistema é montado, O "crachá" (token), O que cada tecnologia é, em uma linha, Por que duas peças, e não uma

### Community 91 - "discovery.py"
Cohesion: 0.39
Nodes (8): _empty_result(), EnrichedDiscoveredPrinter, _is_color(), _is_label(), _normalize_ip(), DiscoveredPrinter, Enriquecimento transitório de filas descobertas com telemetria SNMP., _result_for_ip()

### Community 93 - "models/user.py"
Cohesion: 0.09
Nodes (29): Alert, SQLModel, TonerHistory, SQLModel, get_alert(), list_alerts(), notify_alert(), get (+21 more)

### Community 94 - "database.py"
Cohesion: 0.08
Nodes (32): create_db_and_tables(), _finish_printer_migration(), _migrate_alert_type(), _migrate_alert_value(), _migrate_print_servers(), _migrate_printer_schema(), _migrate_reading_uptime(), _migrate_user_login_fields() (+24 more)

### Community 95 - "collect.py"
Cohesion: 0.14
Nodes (17): collect_fleet(), collect_printer(), CollectRequest, CollectResponse, FleetCollectResponse, get_scheduler_status(), list_scenarios(), BaseModel (+9 more)

### Community 97 - "Scope decision"
Cohesion: 0.22
Nodes (8): Follow-ups (not done here), Glassmorphism Redesign — Phase 6 (remaining screens) Implementation Plan, Scope decision, Task 1: Histórico, Task 2: Integrações, Task 3: Page headers on the four functional screens, Task 4: Retire the legacy token layer, Task 5: Verify

### Community 98 - "Glassmorphism Redesign — Phase 3 (Suprimentos / Toner) Implementation Plan"
Cohesion: 0.25
Nodes (7): Glassmorphism Redesign — Phase 3 (Suprimentos / Toner) Implementation Plan, Roadmap, Task 1: Extract `ScanBar`, Task 2: Page header on `/toner`, Task 3: Severity strip replaces the summary grid, Task 4: Table per handoff, Task 5: Verify

### Community 99 - "seed.py"
Cohesion: 0.29
Nodes (9): migrar_dominio(), mostrar_senha_uma_vez(), obter_senha_admin(), Session, Semeia o banco: contas iniciais + a frota de printers_data.json. SENHAS (Fase…, Imprime a senha em destaque. Unica vez que ela aparece em texto claro., Renomeia TODAS as contas `...@example.com` para `...@elgin.com.br`. Uso unico,…, Devolve (senha, foi_gerada). `foi_gerada` decide se a senha precisa ser… (+1 more)

### Community 100 - "C23. Terceiro passe — Frontend real (token/XSS/CSRF) e execução direta dos testes"
Cohesion: 0.40
Nodes (5): C23.1 Frontend — armazenamento de token, XSS, CSRF (corrige C1/C2-C3 de "NÃO VERIFICADO" para CONFIRMADO), C23.2 Execução real dos testes (corrige C19 com evidência de execução, não só inspeção estrutural), C23.3 Ajuste de score, C23.4 Seção "não verificado" — fecho, C23. Terceiro passe — Frontend real (token/XSS/CSRF) e execução direta dos testes

### Community 101 - "field_validator"
Cohesion: 0.29
Nodes (4): field_validator, Aceita "https://a.com, https://b.com" alem da lista JSON. Sem isto,…, Normaliza um DATABASE_URL sqlite relativo (ex.: sqlite:///./x.db) para um…, Um ambiente escrito errado nao pode cair no default em silencio:…

### Community 102 - "unhandled_exception_handler"
Cohesion: 0.40
Nodes (5): Exception, Request, Erro nao tratado: o detalhe vai para o log do servidor, o cliente recebe apenas…, unhandled_exception_handler(), exception_handler

### Community 103 - "Glassmorphism Redesign — Phases 4 & 5 (Alertas, Relatórios)"
Cohesion: 0.33
Nodes (5): Deliberate deviation, Glassmorphism Redesign — Phases 4 & 5 (Alertas, Relatórios), Phase 4 — Alertas, Phase 5 — Relatórios, Roadmap

### Community 105 - "public/data/monthly-report.json"
Cohesion: 0.67
Nodes (3): public/data/monthly-report.json, public/data/printers.json, Arquivos de dados gerados são ignorados pelo git — gerar/apagar localmente nunca afeta o repositório

### Community 106 - "tests_profile.py"
Cohesion: 0.48
Nodes (6): check(), check_true(), h(), login(), main(), Fase 8 - Perfil proprio e troca de senha. Como as demais suites desde a Fase 1,…

### Community 107 - "ServerMode"
Cohesion: 0.67
Nodes (3): str, Modos aceitos, iguais aos de `settings.print_server_mode`., ServerMode

### Community 113 - "Migração: Cloudflare Tunnel + Vercel → VM Windows Server própria"
Cohesion: 0.17
Nodes (11): Atenção pré-existente (não é novidade desta migração), Backend, Caddy no Windows Server, Contexto, Corte (baixo risco, com fallback), Decisão central, Domínio, Firewall do Windows Server (+3 more)

### Community 125 - "main.py"
Cohesion: 0.23
Nodes (9): health_check(), lifespan(), get, Saude, identificacao do ambiente (Fase 9) e diagnostico (Fase 10). O ambiente…, read_root(), ping(), get, shutdown_scheduler() (+1 more)

### Community 126 - "Ações"
Cohesion: 0.33
Nodes (6): Acessar via web — PARCIAL, Adicionar impressora — AUSENTE/PARCIAL, Ações, Configurações — COMING SOON, Impressoras — FUNCIONAL/PARCIAL, Imprimir página de teste — SIMULADA

## Knowledge Gaps
- **533 isolated node(s):** `$schema`, `typescript`, `oxc`, `react/rules-of-hooks`, `warn` (+528 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `routes/auth.py`, `hash_password`, `notifications.py`, `seed.py`, `tests_rbac.py`, `tests_login_hardening.py`, `tests_profile.py`, `alert_engine.py`, `record`, `dependencies.py`, `PrinterReading`, `Printer`, `Role`, `printers.py`, `models/user.py`, `database.py`, `collect.py`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Why does `SNMPClient` connect `SNMPClient` to `enrich_discovered_printers`, `snmp.py`, `FakeAgent`, `Printer`, `discovery.py`, `alert_engine.py`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Why does `Printer` connect `Printer` to `config.py`, `seed.py`, `import_historico_planilha.py`, `User`, `tests_rbac.py`, `alert_engine.py`, `PrinterReading`, `printers.py`, `models/user.py`, `database.py`, `collect.py`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Are the 45 inferred relationships involving `User` (e.g. with `rate_limited_action()` and `require_active_user()`) actually correct?**
  _`User` has 45 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `Printer` (e.g. with `_finish_printer_migration()` and `notify_alert()`) actually correct?**
  _`Printer` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `SNMPClient` (e.g. with `PrinterCollector` and `FakeAgent`) actually correct?**
  _`SNMPClient` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `typescript`, `oxc` to the rest of the system?**
  _533 weakly-connected nodes found - possible documentation gaps or missing edges._