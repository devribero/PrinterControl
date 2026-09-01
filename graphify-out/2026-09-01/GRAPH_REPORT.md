# Graph Report - PrinterControl  (2026-09-01)

## Corpus Check
- 169 files · ~158,345 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1809 nodes · 3385 edges · 124 communities (99 shown, 25 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 120 edges (avg confidence: 0.62)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1e5b148d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- snmp_fleet_mock.py
- package.json
- Main.ps1
- Elgin Impressoras (painel de monitoramento)
- main.py
- TonerInfo
- compilerOptions
- servers.py
- AUDITORIA COMPLEMENTAR
- RateLimiter
- plugins
- scheduler.py
- graphify (knowledge graph tool)
- next.config.ts
- Elgin (Brand)
- api.ts
- npm run build
- npm run dev
- next-env.d.ts
- navIds.ts
- cn
- PrinterCollector
- tests_collect_api.py
- Cloudflare Tunnel — expor a API sem abrir porta (Fase 11)
- AUDITORIA MASTER — PrinterControl
- schemas/printer.py
- SNMPClient
- Operação em Produção
- Deploy do Frontend na Vercel (Fase 12)
- HistoryMatrix.tsx
- routes/auth.py
- tests_printers_crud.py
- notifications.py
- import_historico_planilha.py
- types.ts
- ETAPA FINAL — FECHAMENTO DA AUDITORIA
- 1. Desenvolvimento (local)
- tests_rbac.py
- layout.tsx
- snmp.py
- reports/page.tsx
- FakeAgent
- PLANO DE IMPLEMENTAÇÃO — ESCANEAR REDE REAL
- printers.py
- Impressoras
- Guia de Uso do PrinterControl
- ConfigurarAmbiente.ps1
- datetime
- UsersView.tsx
- useAppData
- Guia do Desenvolvedor
- NotificationsView.tsx
- users.py
- Settings
- MockSNMPScenarios
- auth.ts
- Contador mensal calculado por diff de duas leituras SNMP acumulativas (não existe OID de páginas do mês)
- Alert
- Print Server
- Fluxo de Dados
- SQLModel
- Dívida técnica — registro único
- config.py
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
- theme.tsx
- RODADA G — FECHAMENTO DE LACUNAS RESIDUAIS
- Printer
- models/user.py
- 6. Subir o sistema em produção hoje
- integrations/page.tsx
- PrinterControl — Visão geral do sistema
- 5. Modo real x modo simulado, e os riscos
- User
- tests_printer_fleet.py
- 2. Como o sistema é montado
- datetime
- Scripts PowerShell reais nunca rodaram de verdade (sem interpretador PowerShell no ambiente de dev)
- notify_alert
- hash_password
- collect.py
- datetime
- Session
- SNMPResult
- seed.py
- C23. Terceiro passe — Frontend real (token/XSS/CSRF) e execução direta dos testes
- tests_uptime.py
- Exception
- Request
- app-data.tsx
- database.py
- tests_login_hardening.py
- webhook_notifier.py
- Alert
- SQLModel
- Session
- tests_webhook.py
- NotificationCreate
- get
- patch
- post
- tests_environment.py
- Printer
- tests_fleet.py
- Path
- unhandled_exception_handler
- BaseModel
- field_validator

## God Nodes (most connected - your core abstractions)
1. `User` - 39 edges
2. `cn()` - 39 edges
3. `SNMPClient` - 37 edges
4. `useAppData()` - 35 edges
5. `SNMPResult` - 31 edges
6. `useToast()` - 29 edges
7. `create_db_and_tables()` - 29 edges
8. `Alert` - 26 edges
9. `Printer` - 25 edges
10. `Printer` - 25 edges

## Surprising Connections (you probably didn't know these)
- `collect()` --calls--> `PrinterCollector`  [INFERRED]
  backend/tests_alerts.py → backend/app/services/printer_collector.py
- `reset_alerts_and_readings()` --uses--> `Alert`  [INFERRED]
  backend/tests_webhook.py → backend/app/models/alert.py
- `monthly_report()` --calls--> `month_label()`  [INFERRED]
  backend/app/routes/printers.py → backend/app/services/monthly_report.py
- `Lucide` --conceptually_related_to--> `Elgin Impressoras (painel de monitoramento)`  [EXTRACTED]
  README.md → CONTEXTO-DESENVOLVIMENTO.md
- `React` --conceptually_related_to--> `Elgin Impressoras (painel de monitoramento)`  [EXTRACTED]
  README.md → CONTEXTO-DESENVOLVIMENTO.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Comandos do CLI graphify (query/path/explain/update)** — claude_graphify, claude_graphify_query, claude_graphify_path, claude_graphify_explain, claude_graphify_update [EXTRACTED 1.00]
- **Stack tecnológico do painel (Vite/React/TS/Tailwind/Recharts/Lucide)** — readme_vite, readme_react, readme_typescript, readme_tailwind_css_v4, readme_recharts, readme_lucide [EXTRACTED 1.00]
- **Arquitetura de dados de 3 modos (Demo/Real/Simulado)** — contexto_desenvolvimento_elgin_impressoras, contexto_desenvolvimento_modo_demo, contexto_desenvolvimento_modo_real, contexto_desenvolvimento_modo_simulado [EXTRACTED 1.00]

## Communities (124 total, 25 thin omitted)

### Community 0 - "snmp_fleet_mock.py"
Cohesion: 0.15
Nodes (14): _base_page_count(), FleetMockClient, _increment(), profile_for(), Simulador de frota — APENAS PARA TESTE LOCAL. Diferenca para snmp_mock.py: la…, Perfil deterministico da impressora: online | offline | snmp_mudo | baixo |…, Contador inicial plausivel para uma impressora que nunca foi lida., Paginas impressas entre duas coletas — fixo por impressora, 5 a 124. (+6 more)

### Community 1 - "package.json"
Cohesion: 0.06
Nodes (31): lucide-react, next, oxlint, dependencies, lucide-react, next, react, react-dom (+23 more)

### Community 2 - "Main.ps1"
Cohesion: 0.13
Nodes (29): Atualizar-ImpressorasAsync(), Build-ListaExibicaoAgrupada(), Build-SnmpGet(), Build-SnmpGetBulk(), Convert-SnmpValueBytes(), Get-ImpressorasEmpresa(), Get-TonerSNMP(), Import-Tabela() (+21 more)

### Community 3 - "Elgin Impressoras (painel de monitoramento)"
Cohesion: 0.07
Nodes (28): Tela Alertas, Tela Dashboard, Elgin Impressoras (painel de monitoramento), Tela Histórico, Tela Impressoras, Tela Login, Migração futura para FastAPI (Python) + Next.js + banco de dados, Modo claro/escuro (toggle) (+20 more)

### Community 4 - "main.py"
Cohesion: 0.11
Nodes (18): Session, User, rate_limited_action(), Dependencias compartilhadas pelas rotas. Autorizacao (Fase 1) fica CENTRALIZADA…, Fabrica de dependencia: exige que o usuario tenha (ou herde) um dos papeis…, Fabrica de dependencia: limita quantas vezes UM usuario pode disparar UMA acao…, Usuario dono do JWT do header Authorization. 401 se ausente/invalido. O usuario…, `require_user` + bloqueio de conta com troca de senha pendente. Toda rota do… (+10 more)

### Community 5 - "TonerInfo"
Cohesion: 0.21
Nodes (7): Nivel de um consumivel de toner., TonerInfo, DiscoverySnmpTests, printer(), DiscoveredPrinter, Testes locais do enriquecimento SNMP, sem rede corporativa ou SQLite., result()

### Community 6 - "compilerOptions"
Cohesion: 0.06
Nodes (30): dom, dom.iterable, esnext, .next/dev/types/**/*.ts, next-env.d.ts, .next/types/**/*.ts, node_modules, **/*.ts (+22 more)

### Community 7 - "servers.py"
Cohesion: 0.08
Nodes (49): create_server(), delete_server(), discover(), discover_server(), DiscoveredPrinterResponse, DiscoverResponse, _executar_discover(), get_current_server() (+41 more)

### Community 8 - "AUDITORIA COMPLEMENTAR"
Cohesion: 0.08
Nodes (24): AUDITORIA COMPLEMENTAR, C10. Backup e Disaster Recovery — revisão significativa da rodada 1, C11. DevOps / CI-CD, C12. Supply Chain — aprofundamento, C13. PowerShell / Command Execution — reavaliação com evidência forte, C14. Segurança da API — inventário de endpoints (parcial, rotas mais sensíveis), C15. Autenticação — fluxo completo, C16. Banco de dados — schema (+16 more)

### Community 9 - "RateLimiter"
Cohesion: 0.15
Nodes (10): RateLimiter, Limite de tentativas para o login (Fase 10). POR QUE existe --------------…, Consome credito. So a FALHA conta — login certo nao gasta nada., Zera as contagens apos um login BEM-SUCEDIDO. Sem isto, quem erra a senha…, Esvazia tudo. Existe para os testes; nao ha rota que chegue aqui., Veredito de uma checagem. `retry_after` so faz sentido quando bloqueado., Janela deslizante em memoria, protegida por lock. O lock existe porque o…, Descarta o que saiu da janela e devolve o que restou. (+2 more)

### Community 10 - "plugins"
Cohesion: 0.22
Nodes (8): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, typescript, warn

### Community 11 - "scheduler.py"
Cohesion: 0.16
Nodes (18): AsyncIOScheduler, month_bounds(), pages_from_readings(), Session, Grava ou atualiza o total de UM mes de UMA impressora — chave e (printer_id,…, Primeiro instante do mes de `dt` e primeiro instante do mes seguinte (limite…, Paginas impressas por impressora dentro de [month_start, month_end), somando o…, upsert_printer_monthly() (+10 more)

### Community 12 - "graphify (knowledge graph tool)"
Cohesion: 0.25
Nodes (8): graphify (knowledge graph tool), graphify explain command, graphify path command, graphify query command, graphify update command, graphify-out/graph.json, graphify-out/GRAPH_REPORT.md, graphify-out/wiki/index.md

### Community 15 - "api.ts"
Cohesion: 0.05
Nodes (56): adaptDiscovered(), FORM_VAZIO, formatarMomento(), MODOS, NetworkView(), confirmarAtivacao(), confirmarExclusao(), executarDescoberta() (+48 more)

### Community 20 - "cn"
Cohesion: 0.06
Nodes (40): AlertsPage(), DashboardPage(), AlertBannerProps, AlertsView(), AlertsViewProps, AlertsDonutCard(), AlertsDonutCardProps, BottomChartsProps (+32 more)

### Community 21 - "PrinterCollector"
Cohesion: 0.15
Nodes (11): PrinterCollector, Session, Orquestrador da coleta de impressoras. Separa as tres responsabilidades da…, Converte SNMPResult em PrinterReading. Toner ausente vira NULL (a coluna e…, Coleta uma impressora e grava o resultado como PrinterReading., Args: mode: "real" (SNMP de verdade), "mock" (cenario fixo) ou "fleet" (frota…, Deduz se a impressora e colorida — so um PALPITE inicial, usado para decidir a…, Etiquetadora/portatil: sem Printer-MIB, o PS1 nem consulta SNMP. (+3 more)

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
Nodes (16): Config, PrinterCreate, PrinterReadingCreate, PrinterReadingResponse, PrinterResponse, PrinterUpdate, PrinterWithStatus, Impressora + ultima leitura conhecida (o que o painel consome). (+8 more)

### Community 29 - "SNMPClient"
Cohesion: 0.13
Nodes (10): Cliente SNMP para coleta de impressoras (Printer-MIB, RFC 3805)., PS1: `if ($ip -match '^\\d')` — descarta 'N/A' e nomes de porta., ICMP ping, equivalente ao `New-Object ...Ping).Send($ip, 400)` do PS1. SNMP…, Aplica os filtros do PS1 e monta um candidato a toner., Escolhe os toners finais. PS1 colorida: um por cor (primeiro de cada grupo),…, Cor pela descricao; se nao identificar e for colorida, usa indice % 4., SNMPv1 GET (PS1: Build-SnmpGet, version 0, PDU 0xA0)., SNMPv2c GETBULK (PS1: Build-SnmpGetBulk, version 1, PDU 0xA5). (+2 more)

### Community 30 - "Operação em Produção"
Cohesion: 0.11
Nodes (19): 1. Antes do primeiro deploy, 2. Instalar, 3. Dia a dia, 4. Diagnóstico, 5. Backup, 6. Recuperação — o que acontece se o processo cair, 7. Problemas comuns, 8. Dívida técnica conhecida — FK órfã para `printers_old` (+11 more)

### Community 31 - "Deploy do Frontend na Vercel (Fase 12)"
Cohesion: 0.25
Nodes (8): 1. O projeto já está pronto para este deploy, 2. Variáveis de ambiente para configurar na Vercel, 3. Conectar o repositório e fazer o primeiro deploy, 4. Validar, 5. Depois do deploy — atualizar o CORS do backend, 6. Redeploy — quando o código mudar, 7. Resumo — Fase 12 concluída, Deploy do Frontend na Vercel (Fase 12)

### Community 32 - "HistoryMatrix.tsx"
Cohesion: 0.27
Nodes (5): HistoryPage(), HistoryMatrix(), HistoryMatrixProps, getDepartmentLabel(), getPrinterSite()

### Community 33 - "routes/auth.py"
Cohesion: 0.09
Nodes (33): change_own_password(), _identificar_origem(), login(), patch, post, Request, Session, Perfil da PROPRIA conta (Fase 8). So o nome. `require_active_user` (nao… (+25 more)

### Community 34 - "tests_printers_crud.py"
Cohesion: 0.33
Nodes (3): Etapa 12 - CRUD de impressoras contra o servidor rodando. Usa o banco REAL,…, Devolve (status, payload)., request()

### Community 35 - "notifications.py"
Cohesion: 0.12
Nodes (29): get_session(), Notification, SQLModel, Notificacoes internas (Fase 7). Por que uma tabela separada de `alerts`…, AlertRef, create_notifications(), list_notifications(), mark_all_as_read() (+21 more)

### Community 36 - "import_historico_planilha.py"
Cohesion: 0.15
Nodes (18): _cell_value(), _e_cabecalho_de_site(), _e_linha_ip(), _e_linha_total(), importar_para_banco(), _ler_planilha(), LinhaImpressora, main() (+10 more)

### Community 37 - "types.ts"
Cohesion: 0.09
Nodes (31): TonerPage(), PrinterDetailsModal(), PrinterDetailsModalProps, config, PrinterStatusBadge(), PAGE_SIZE_OPTIONS, PrinterTable(), PrinterTableProps (+23 more)

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
Cohesion: 0.12
Nodes (18): parse_varbinds(), SNMP Collector para impressoras. Porte direto da funcao Get-TonerSNMP de…, Decodifica um OID BER para notacao pontuada., Decodifica bytes BER como inteiro sem sinal., Extrai a lista de varbinds de uma resposta SNMP. Percorre a estrutura completa…, Coleta status, contador de paginas e toners de uma impressora. Nunca levanta…, Retorna (candidatos, houve_resposta_snmp)., GETBULK das tres colunas de uma vez (PS1: Build-SnmpGetBulk). (+10 more)

### Community 43 - "reports/page.tsx"
Cohesion: 0.15
Nodes (13): ReportsPage(), DecommissionedList(), DecommissionedListProps, formatarData(), DepartmentBreakdown(), DepartmentBreakdownProps, Topbar(), onExportCsv() (+5 more)

### Community 44 - "FakeAgent"
Cohesion: 0.14
Nodes (9): check(), FakeAgent, LocalSNMPClient, main(), Validacao local do SNMPClient sem impressoras reais. Sobe um agente SNMP falso…, Extrai (pdu_tag, [oids]) de um GET/GETBULK., SNMPClient apontando para a porta do agente falso, sem depender de ICMP., Mesma logica de retry do SNMPClient real (ver snmp.py), so redirecionando o… (+1 more)

### Community 45 - "PLANO DE IMPLEMENTAÇÃO — ESCANEAR REDE REAL"
Cohesion: 0.05
Nodes (39): A. Endpoint (implementado), Alertas, Arquitetura atual, Arquitetura do PrinterControl, B. Service reutilizável, Banco, C. Funções Print Server reutilizáveis, Cliente de API (+31 more)

### Community 46 - "printers.py"
Cohesion: 0.17
Nodes (19): create_printer(), create_printer_reading(), get_printer(), get_printer_readings(), list_printers(), list_printers_with_status(), monthly_report(), Contagem mensal por impressora, por mes e por departamento. Fase 12: mes ja… (+11 more)

### Community 47 - "Impressoras"
Cohesion: 0.22
Nodes (9): `GET /api/printers`, `GET /api/printers/monthly-report`, `GET /api/printers/{printer_id}`, `GET /api/printers/{printer_id}/readings`, `GET /api/printers/with-status`, Impressoras, `PATCH /api/printers/{printer_id}`, `POST /api/printers` (+1 more)

### Community 48 - "Guia de Uso do PrinterControl"
Cohesion: 0.10
Nodes (20): Acessar via web — PARCIAL, Adicionar impressora — AUSENTE/PARCIAL, Alertas — FUNCIONAL na leitura; PARCIAL nas ações, Ações, Como acessar, Configurações — COMING SOON, Configurações, Usuários e Integrações — COMING SOON, Dashboard — FUNCIONAL/PARCIAL (+12 more)

### Community 49 - "ConfigurarAmbiente.ps1"
Cohesion: 0.31
Nodes (4): Aviso(), Info(), Perguntar-Campo(), Perguntar-SimNao()

### Community 50 - "datetime"
Cohesion: 0.14
Nodes (12): _inicio_da_janela(), Primeiro instante do mes que abre uma janela de `months` meses ate hoje., month_label(), month_period(), Calculo de paginas por mes, compartilhado entre tres consumidores (Fase 12): -…, 2026-08' — chave de mes usada em PrinterMonthly.month e nas respostas da API., gravar(), Fase 17 - pages_from_readings() soma saltos positivos entre leituras… (+4 more)

### Community 51 - "UsersView.tsx"
Cohesion: 0.10
Nodes (24): RequireRole(), FORM_VAZIO, formatarData(), FormState, UsersView(), abrirEdicao(), confirmarAtivacao(), confirmarExclusao() (+16 more)

### Community 52 - "useAppData"
Cohesion: 0.10
Nodes (31): react, PrintersPage(), AppShell(), AuthGate(), ModalProps, MustChangePasswordGate(), handleSubmit(), validar() (+23 more)

### Community 53 - "Guia do Desenvolvedor"
Cohesion: 0.13
Nodes (15): Backend, Banco, Comandos do frontend, Escanear Rede (implementado), Guia do Desenvolvedor, Já resolvido — não reabra, O que não executar em produção sem autorização, Print Server (+7 more)

### Community 54 - "NotificationsView.tsx"
Cohesion: 0.11
Nodes (20): Modal(), FORM_VAZIO, formatarMomento(), FormState, ICONE_SEVERIDADE, NotificationsView(), abrirEnvio(), enviar() (+12 more)

### Community 55 - "users.py"
Cohesion: 0.11
Nodes (28): Any, _active_admin_count(), create_user(), delete_user(), _ensure_not_last_admin(), list_users(), delete, get (+20 more)

### Community 56 - "Settings"
Cohesion: 0.06
Nodes (26): Config, field_validator, Fail-fast: producao nao sobe com simulacao ligada (Fase 9). O risco concreto e…, Impede que um ambiente de producao suba silenciosamente com o secret de…, Aceita "https://a.com, https://b.com" alem da lista JSON. Sem isto,…, Producao exige origens proprias e explicitas (Fase 10). Tres recusas, todas por…, Normaliza um DATABASE_URL sqlite relativo (ex.: sqlite:///./x.db) para um…, Um ambiente escrito errado nao pode cair no default em silencio:… (+18 more)

### Community 57 - "MockSNMPScenarios"
Cohesion: 0.12
Nodes (12): MockSNMPScenarios, SNMP responde o contador, mas nao expoe a tabela de consumiveis., Monocromatica com toner em 5%., Colorida com ciano critico (18%) e os demais normais., Contador reiniciado (troca de placa/formatador): page_count baixo., Cenarios de teste. Cada metodo devolve um SNMPResult completo., Monocromatica saudavel., Colorida saudavel (4 toners, ordem C, M, Y, K). (+4 more)

### Community 58 - "auth.ts"
Cohesion: 0.11
Nodes (25): ACTIVE_NODES, features, Login(), handleSubmit(), LoginProps, NETWORK_LINKS, NETWORK_NODES, salvarPerfil() (+17 more)

### Community 60 - "Alert"
Cohesion: 0.16
Nodes (16): Alert, _active(), evaluate_reading(), _notify_all_active_users(), PrinterReading, Alertas automaticos (Etapa 8A, re-alerta de toner na Fase 11). Roda logo apos…, Fan-out de uma Notification por usuario ativo (Fase 11) — e o canal "site" dos…, Avalia uma leitura e sincroniza os alertas da impressora. Faz commit ao final.… (+8 more)

### Community 61 - "Print Server"
Cohesion: 0.22
Nodes (9): `GET /api/servers`, `GET /api/servers/current`, `PATCH /api/servers/{server_id}`, `POST /api/servers`, `POST /api/servers/discover`, `POST /api/servers/{server_id}/discover`, `POST /api/servers/{server_id}/sync`, `POST /api/servers/sync` (+1 more)

### Community 62 - "Fluxo de Dados"
Cohesion: 0.17
Nodes (11): 10. Escanear Rede (implementado), 1. Cadastro no SQLite, 2. Coleta SNMP real, 3. Coleta de frota, 4. Print Server, 5. Sincronização, 6. Alertas, 7. Relatório mensal (+3 more)

### Community 63 - "SQLModel"
Cohesion: 0.17
Nodes (11): TonerHistory, AuditLog, Trilha de auditoria administrativa (Fase 16). Registra QUEM fez, O QUE e QUANDO…, list_audit_log(), get, Session, Leitura da trilha de auditoria administrativa (Fase 16). Ver…, Mais recentes primeiro. Filtros combinam com AND quando informados juntos. (+3 more)

### Community 64 - "Dívida técnica — registro único"
Cohesion: 0.11
Nodes (18): Como ler, D10 — O frontend não tem nenhum teste automatizado, D11 — O painel cai em dados de demonstração quando a API não responde, D12 — Datas ingênuas no servidor, hora do navegador no cliente, D13 — `/health` existe, mas nada o consulta, D14 — `httpx` sem teto de versão quebrava todas as suítes que usam `TestClient`, D15 — `requirements.txt` está em UTF-16, D16 — `backend/.env` em produção estava configurado como `demo`/`mock`, não `production` (+10 more)

### Community 65 - "config.py"
Cohesion: 0.06
Nodes (39): PrintServer, SQLModel, str, Print Server como entidade (Fase 4). Ate aqui um Print Server existia de duas…, Modos aceitos, iguais aos de `settings.print_server_mode`., ServerMode, discover_printers(), DiscoveredPrinter (+31 more)

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

### Community 80 - "theme.tsx"
Cohesion: 0.27
Nodes (8): lerPreferencia(), resolver(), sistemaEscuro(), Theme, ThemeContext, ThemeContextValue, ThemePreference, ThemeProvider()

### Community 81 - "RODADA G — FECHAMENTO DE LACUNAS RESIDUAIS"
Cohesion: 0.29
Nodes (6): G1. LGPD — inventário técnico de dados pessoais, G2. CVE scan — executado onde seguro, sem alterar nada, G3. Itens "NÃO VERIFICADO" reavaliados — fechados nesta rodada, G4. Ajuste de score decorrente desta rodada, G5. Veredito — o que muda com esta rodada, RODADA G — FECHAMENTO DE LACUNAS RESIDUAIS

### Community 82 - "Printer"
Cohesion: 0.25
Nodes (13): Printer, Etapa 4: identidade e (server, name), NAO ip — o Print Server permite varias…, collect_fleet(), _collect_ip_network(), FleetCollectionResult, _group_by_ip(), _group_plan(), Printer (+5 more)

### Community 83 - "models/user.py"
Cohesion: 0.20
Nodes (6): SQLModel, str, RBAC minimo (Fase 1). Tres papeis cobrem todas as rotas existentes hoje: -…, Role, Login por username e troca de senha obrigatoria (2026-08-24). Cobre as duas…, Enum

### Community 84 - "6. Subir o sistema em produção hoje"
Cohesion: 0.22
Nodes (9): 6. Subir o sistema em produção hoje, Passo 1 — Preparar o `.env`, Passo 2 — Testar a configuração ANTES de subir, Passo 3 — Definir a senha das contas de administrador, Passo 4 — Backup antes de qualquer coisa, Passo 5 — Subir o backend, Passo 6 — Verificar a saúde, Passo 7 — Subir o painel (+1 more)

### Community 86 - "PrinterControl — Visão geral do sistema"
Cohesion: 0.29
Nodes (7): 1. O que o sistema faz, 8. Onde está o resto da documentação, Como ele descobre isso, O ciclo, em uma frase, O detalhe que explica o relatório mensal, PrinterControl — Visão geral do sistema, Índice

### Community 87 - "5. Modo real x modo simulado, e os riscos"
Cohesion: 0.33
Nodes (6): 5. Modo real x modo simulado, e os riscos, As duas camadas de proteção, Como o sistema decide entre real e simulado, O problema em uma frase, O risco mais grave: sincronizar em modo simulado, Riscos corrigidos na Fase 10 (24/08/2026)

### Community 88 - "User"
Cohesion: 0.22
Nodes (14): True se o papel do usuario satisfaz qualquer um dos exigidos., User, get, Conta autenticada e seu papel — usado para decidir o que exibir/permitir., read_current_user(), verify_password(), check(), check_true() (+6 more)

### Community 89 - "tests_printer_fleet.py"
Cohesion: 0.17
Nodes (4): fake_real_collect(), Etapa 5 - orquestracao da frota (printer_fleet.collect_fleet). Roda sobre um…, RecordingThreadPoolExecutor, _OriginalTPE

### Community 90 - "2. Como o sistema é montado"
Cohesion: 0.50
Nodes (4): 2. Como o sistema é montado, O "crachá" (token), O que cada tecnologia é, em uma linha, Por que duas peças, e não uma

### Community 93 - "notify_alert"
Cohesion: 0.20
Nodes (11): get_alert(), list_alerts(), notify_alert(), get, patch, post, Session, Resolve um alerta. Ate a Fase 1 esta rota estava SEM protecao alguma — qualquer… (+3 more)

### Community 94 - "hash_password"
Cohesion: 0.20
Nodes (14): hash_password(), Hash de senha e emissao/validacao do JWT. POR QUE PyJWT E NAO python-jose (Fase…, check(), check_true(), h(), main(), Fase 7 - Notificacoes internas. Como…, check() (+6 more)

### Community 95 - "collect.py"
Cohesion: 0.11
Nodes (24): health_check(), get, Saude, identificacao do ambiente (Fase 9) e diagnostico (Fase 10). O ambiente…, read_root(), collect_fleet(), collect_printer(), CollectRequest, CollectResponse (+16 more)

### Community 98 - "SNMPResult"
Cohesion: 0.20
Nodes (16): _empty_result(), enrich_discovered_printers(), EnrichedDiscoveredPrinter, _is_color(), _is_label(), _normalize_ip(), DiscoveredPrinter, Enriquecimento transitório de filas descobertas com telemetria SNMP. (+8 more)

### Community 99 - "seed.py"
Cohesion: 0.29
Nodes (9): migrar_dominio(), mostrar_senha_uma_vez(), obter_senha_admin(), Session, Semeia o banco: contas iniciais + a frota de printers_data.json. SENHAS (Fase…, Imprime a senha em destaque. Unica vez que ela aparece em texto claro., Renomeia TODAS as contas `...@example.com` para `...@elgin.com.br`. Uso unico,…, Devolve (senha, foi_gerada). `foi_gerada` decide se a senha precisa ser… (+1 more)

### Community 100 - "C23. Terceiro passe — Frontend real (token/XSS/CSRF) e execução direta dos testes"
Cohesion: 0.40
Nodes (5): C23.1 Frontend — armazenamento de token, XSS, CSRF (corrige C1/C2-C3 de "NÃO VERIFICADO" para CONFIRMADO), C23.2 Execução real dos testes (corrige C19 com evidência de execução, não só inspeção estrutural), C23.3 Ajuste de score, C23.4 Seção "não verificado" — fecho, C23. Terceiro passe — Frontend real (token/XSS/CSRF) e execução direta dos testes

### Community 101 - "tests_uptime.py"
Cohesion: 0.36
Nodes (4): PrinterMonthly, PrinterReading, SQLModel, Etapa 7 - persistencia de uptime. Parte A roda sobre uma COPIA do banco REAL…

### Community 105 - "app-data.tsx"
Cohesion: 0.08
Nodes (38): Levantamento_impressões (planilha original), public/data/monthly-report.json, public/data/printers.json, Arquivos de dados gerados são ignorados pelo git — gerar/apagar localmente nunca afeta o repositório, DiscoveryResults(), DiscoveryResultsProps, statusLabel(), decommissionedPrinters (+30 more)

### Community 106 - "database.py"
Cohesion: 0.11
Nodes (27): create_db_and_tables(), _finish_printer_migration(), _migrate_alert_type(), _migrate_alert_value(), _migrate_print_servers(), _migrate_printer_schema(), _migrate_reading_uptime(), _migrate_user_login_fields() (+19 more)

### Community 107 - "tests_login_hardening.py"
Cohesion: 0.22
Nodes (6): medir(), Fase 10 - endurecimento do login. Cobre as duas falhas levantadas na auditoria…, Request minimo: so o que _identificar_origem le., Tentativa com a contagem limpa — isola o caso do limite de tentativas., _Req, tentar()

### Community 108 - "webhook_notifier.py"
Cohesion: 0.32
Nodes (7): _build_adaptive_card(), Notificacao de alerta critico via webhook (Etapa 6). Equivalente a Send-…, Envia o Adaptive Card ao webhook configurado. Nunca levanta excecao — retorna…, Host da URL, para logar sem expor path/assinatura., Mesmo corpo de Send-AlertaWebhook (Main.ps1:1319): titulo/cor conforme manual…, _safe_host(), send_toner_alert_webhook()

### Community 112 - "tests_webhook.py"
Cohesion: 0.29
Nodes (5): make_offline_reading(), make_reading(), PrinterReading, Etapa 6 - webhook de alerta critico de toner. Banco SQLite temporario e ISOLADO…, reset_alerts_and_readings()

### Community 113 - "NotificationCreate"
Cohesion: 0.47
Nodes (3): NotificationCreate, field_validator, Uma comunicacao para um ou mais destinatarios (uma linha por pessoa).

### Community 117 - "tests_environment.py"
Cohesion: 0.20
Nodes (3): ambiente, Fase 9 - Mock e Demo Seguros. Cobre as DUAS camadas que protegem o risco…, Troca settings.environment durante o bloco - as rotas leem em runtime.

### Community 119 - "tests_fleet.py"
Cohesion: 0.33
Nodes (3): collect_fleet(), Etapa 11 - coleta simulada da frota inteira, ponta a ponta. Copia o banco real…, Uma coleta completa. Devolve resumo por status.

### Community 121 - "unhandled_exception_handler"
Cohesion: 0.50
Nodes (4): Erro nao tratado: o detalhe vai para o log do servidor, o cliente recebe apenas…, unhandled_exception_handler(), exception_handler, Request

## Knowledge Gaps
- **466 isolated node(s):** `DEPARTMENT_PERIODS`, `VALID_STATUS`, `VALID_COLORS`, `ApiMonthlyReport`, `RequestOptions` (+461 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **25 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SNMPClient` connect `SNMPClient` to `SNMPResult`, `snmp.py`, `FakeAgent`, `Printer`, `PrinterCollector`, `tests_printer_fleet.py`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Why does `SNMPResult` connect `SNMPResult` to `tests_printer_fleet.py`, `TonerInfo`, `snmp.py`, `Printer`, `PrinterCollector`, `MockSNMPScenarios`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Why does `Settings` connect `Settings` to `tests_rbac.py`, `config.py`, `tests_environment.py`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Are the 17 inferred relationships involving `User` (e.g. with `notify_alert()` and `resolve_alert()`) actually correct?**
  _`User` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `SNMPClient` (e.g. with `PrinterCollector` and `FakeAgent`) actually correct?**
  _`SNMPClient` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `SNMPResult` (e.g. with `enrich_discovered_printers()` and `PrinterCollector`) actually correct?**
  _`SNMPResult` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `DEPARTMENT_PERIODS`, `VALID_STATUS`, `VALID_COLORS` to the rest of the system?**
  _466 weakly-connected nodes found - possible documentation gaps or missing edges._