# Mapa da API

Prefixo configurado: `/api`.

## Autenticação

**RBAC (Fase 1).** Três papéis, guardados em `users.role`, com herança
`admin > operator > viewer`:

| Papel | Pode |
| --- | --- |
| `viewer` | somente leitura |
| `operator` | leitura + operação (coleta real, resolver/notificar alertas, registrar leituras) |
| `admin` | tudo, incluindo operações administrativas/perigosas (usuários, cadastro de impressoras, discovery/sync, coleta simulada, agendador) |

As dependências ficam centralizadas em `backend/app/dependencies.py`
(`require_user`, `require_viewer`, `require_operator`, `require_admin`);
nenhuma rota compara `user.role` diretamente. Sem token → **401**; token válido
mas papel insuficiente ou conta desativada → **403**. O usuário é relido do
banco a cada requisição, então desativar uma conta corta o acesso na hora,
mesmo com um JWT ainda válido.

**Fase 2:** as rotas `GET` de leitura deixaram de ser públicas. O painel só
busca dados depois de confirmar a sessão em `GET /api/auth/me`, então sempre
há token para enviar. A exigência está declarada no próprio `APIRouter` de
`printers` e `alerts`, para que nenhuma rota nova nasça pública por
esquecimento.

Rotas públicas restantes: `POST /api/auth/login`, `GET /` e `GET /health`.

### `GET /api/auth/me`

- Arquivo: `backend/app/routes/auth.py`
- Função: `read_current_user`
- Auth: autenticado (qualquer papel)
- Retorno: `id`, `email`, `name`, `role`, `is_active`, `created_at`

### `POST /api/auth/login`

- Arquivo: `backend/app/routes/auth.py`
- Função: `login`
- Auth: pública (é o ponto de entrada). Conta desativada recebe 403.
- Service: `verify_password`, `create_access_token`
- Banco/rede: consulta `users` no SQLite
- Frontend: usado por `src/lib/auth.ts`
- Estado: funcional
- Retorno: token JWT e usuário

## Usuários (Fase 3)

Recurso administrativo de contas. A exigência de **admin** está declarada no
próprio `APIRouter` (`backend/app/routes/users.py`), então nenhuma rota nova
nasce sem proteção. Substitui o antigo `POST /api/auth/register`, que era
administrativo desde a Fase 1 e foi movido para o recurso a que pertence —
não existem duas formas de criar um usuário.

Não há `DELETE`: desativar (`is_active=false`) é a exclusão deste sistema.
Apagar a linha liberaria o e-mail para outra pessoa herdar a identidade e
descartaria o histórico da conta.

### `GET /api/users`

- Arquivo: `backend/app/routes/users.py`
- Função: `list_users`
- Auth: **admin**
- Banco/rede: lê `users` no SQLite, ordenado por `id`
- Frontend: `src/components/UsersView.tsx` (rota `/users`)
- Estado: funcional
- Retorno: lista de `id`, `email`, `name`, `role`, `is_active`, `created_at`
  (**nunca** `password_hash`)

### `POST /api/users`

- Arquivo: `backend/app/routes/users.py`
- Função: `create_user`
- Auth: **admin**
- Service: `hash_password` (Argon2, o mesmo do login)
- Banco/rede: insere em `users`
- Frontend: `src/components/UsersView.tsx`
- Estado: funcional
- Corpo: `email`, `password` (mín. 8), `name`, `role` opcional (padrão `viewer`)
- Erros: `409` e-mail já cadastrado · `422` validação (papel inválido, senha
  curta, e-mail malformado, nome em branco)
- Retorno: `201` com o usuário criado — nunca um token para a conta nova

### `PATCH /api/users/{user_id}`

- Arquivo: `backend/app/routes/users.py`
- Função: `update_user`
- Auth: **admin**
- Banco/rede: atualiza `users`
- Frontend: `src/components/UsersView.tsx`
- Estado: funcional
- Corpo (todos opcionais): `name`, `role`, `is_active`, `password`
- Não aceita: `id`, `email` (é o `sub` do JWT — trocá-lo invalidaria a sessão
  do dono em silêncio) e `password_hash`
- Erros: `404` id inexistente · `409` a mudança deixaria o sistema sem nenhum
  administrador ativo · `422` validação
- Desativar corta o acesso na hora: `require_user` relê o usuário a cada
  requisição, então o JWT que a pessoa já tem passa a receber `403` (Fase 1)

## Impressoras

### `GET /api/printers`

- Arquivo: `backend/app/routes/printers.py`
- Função: `list_printers`
- Auth: autenticado (qualquer papel) — fechado na Fase 2
- Service: nenhum
- Banco/rede: lê `printers` no SQLite
- Frontend: não utilizado atualmente
- Estado: funcional

### `GET /api/printers/with-status`

- Arquivo: `backend/app/routes/printers.py`
- Função: `list_printers_with_status`
- Auth: autenticado (qualquer papel) — fechado na Fase 2
- Service: nenhum
- Banco/rede: lê `printers` e a leitura mais recente de `printer_readings`
- Frontend: usado pelo dashboard, impressoras e toner
- Estado: funcional para consulta

### `GET /api/printers/monthly-report`

- Arquivo: `backend/app/routes/printers.py`
- Função: `monthly_report`
- Auth: autenticado (qualquer papel) — fechado na Fase 2
- Service: nenhum
- Banco/rede: calcula diferenças de `printer_readings`
- Frontend: usado por `loadMonthlyReportFromApi`
- Estado: funcional quando há leituras suficientes

### `GET /api/printers/{printer_id}`

- Arquivo: `backend/app/routes/printers.py`
- Função: `get_printer`
- Auth: autenticado (qualquer papel) — fechado na Fase 2
- Banco/rede: lê `printers`
- Frontend: não utilizado diretamente
- Estado: funcional

### `POST /api/printers`

- Arquivo: `backend/app/routes/printers.py`
- Função: `create_printer`
- Auth: **admin**
- Banco/rede: insere em `printers`
- Frontend: helper existe, tela não chama
- Estado: backend funcional, UI ausente

### `PATCH /api/printers/{printer_id}`

- Arquivo: `backend/app/routes/printers.py`
- Função: `update_printer`
- Auth: **admin**
- Banco/rede: altera `printers`
- Frontend: helper existe, tela não chama
- Estado: backend funcional, UI ausente

### `GET /api/printers/{printer_id}/readings`

- Arquivo: `backend/app/routes/printers.py`
- Função: `get_printer_readings`
- Auth: autenticado (qualquer papel) — fechado na Fase 2
- Banco/rede: lê `printer_readings`
- Frontend: helper existe, tela History não chama
- Estado: funcional, subutilizado

### `POST /api/printers/{printer_id}/readings`

- Arquivo: `backend/app/routes/printers.py`
- Função: `create_printer_reading`
- Auth: **operator** (admin herda)
- Banco/rede: insere leitura manual
- Frontend: não utilizado
- Estado: funcional no backend, risco de dados manuais sem fluxo de UI

## Alertas

### `GET /api/alerts`

- Arquivo: `backend/app/routes/alerts.py`
- Função: `list_alerts`
- Auth: autenticado (qualquer papel) — fechado na Fase 2
- Banco/rede: lê `alerts` no SQLite
- Frontend: usado com `resolved=false`
- Estado: funcional
- Filtros: `severity`, `resolved`, `printer_id`, `alert_type`

### `GET /api/alerts/{alert_id}`

- Arquivo: `backend/app/routes/alerts.py`
- Função: `get_alert`
- Auth: autenticado (qualquer papel) — fechado na Fase 2
- Banco/rede: lê `alerts`
- Frontend: não utilizado
- Estado: funcional

### `POST /api/alerts/{alert_id}/notify`

- Arquivo: `backend/app/routes/alerts.py`
- Função: `notify_alert`
- Auth: **operator** (admin herda)
- Service: `send_toner_alert_webhook`
- Banco/rede: lê alerta/impressora e chama webhook externo
- Frontend: não utilizado
- Estado: backend parcial

### `PATCH /api/alerts/{alert_id}/resolve`

- Arquivo: `backend/app/routes/alerts.py`
- Função: `resolve_alert`
- Auth: **operator** (admin herda) — corrigido na Fase 1; antes estava sem proteção alguma
- Banco/rede: altera `alerts.resolved_at`
- Frontend: não utilizado
- Estado: funcional e protegido

## Notificações (Fase 7)

Central **interna**, dirigida a pessoas. Não substitui nem altera `/api/alerts`:

| | Alerta | Notificação |
|---|---|---|
| O que é | evento técnico de uma impressora | comunicação para uma pessoa |
| Quem cria | `alert_engine.evaluate_reading`, após cada leitura | um admin, via `POST /api/notifications` |
| Identidade | deduplicado por `(printer_id, alert_type)` | uma linha por destinatário |
| Fim de vida | resolve-se sozinho quando a condição some | marcada como lida por quem recebeu |
| Tabela | `alerts` | `notifications` |

O vínculo é uma FK **opcional** (`notifications.alert_id`). A notificação
guarda a própria `message` — um instantâneo do momento em que foi criada —
em vez de montar o texto lendo o alerta. Consequências práticas:

- resolver ou escalar o alerta **não** altera o que a pessoa recebeu;
- se o alerta sumir, a resposta traz `alert: null` e a notificação continua
  legível;
- uma notificação pode não ter alerta nenhum (aviso administrativo).

A referência ao alerta é lida na hora de responder, apenas para o painel
poder oferecer o link e mostrar se ele ainda está aberto.

### `GET /api/notifications`

- Arquivo: `backend/app/routes/notifications.py`
- Função: `list_notifications`
- Auth: autenticado (qualquer papel)
- Banco/rede: lê `notifications` **filtrado por `user_id` da sessão**
- Frontend: não utilizado ainda (rota `/notifications` é placeholder)
- Estado: funcional
- Filtros: `unread_only` (bool), `limit` (1–500, padrão 100)
- Não aceita `user_id` como parâmetro: o destinatário é sempre quem está
  autenticado, então não há como pedir a caixa alheia

### `GET /api/notifications/unread-count`

- Arquivo: `backend/app/routes/notifications.py`
- Função: `unread_count`
- Auth: autenticado (qualquer papel)
- Banco/rede: `COUNT` em `notifications` do usuário logado
- Frontend: não utilizado ainda (destinado ao badge do sino)
- Estado: funcional
- Retorno: `{ "unread": <int> }`

### `PATCH /api/notifications/{notification_id}/read`

- Arquivo: `backend/app/routes/notifications.py`
- Função: `mark_as_read`
- Auth: autenticado — **e a notificação precisa ser sua**
- Banco/rede: grava `notifications.read_at`
- Frontend: não utilizado ainda
- Estado: funcional
- Idempotente: reler não reescreve o `read_at` da primeira leitura
- Notificação de outra pessoa responde **404, não 403** — um 403 confirmaria
  que aquele id existe, e numa caixa pessoal isso já é vazamento

### `POST /api/notifications`

- Arquivo: `backend/app/routes/notifications.py`
- Função: `create_notifications`
- Auth: **admin**
- Banco/rede: insere N linhas em `notifications` (uma por destinatário)
- Frontend: não utilizado ainda
- Estado: funcional
- Corpo: `user_ids` (lista, mín. 1), `message` (não vazia), `severity`
  opcional (`info`/`warning`/`critical`, padrão `info`), `alert_id` opcional
- `404` se algum destinatário ou o alerta referenciado não existir
- `409` se algum destinatário for uma conta desativada — a caixa dela nunca
  seria aberta, e o remetente precisa saber
- Destinatários repetidos são deduplicados antes de gravar

Não existe `DELETE`, no mesmo espírito de usuários e Print Servers.

## Coleta

### `POST /api/collect/printers/{printer_id}`

- Arquivo: `backend/app/routes/collect.py`
- Função: `collect_printer`
- Auth: **operator**; `mode="mock"` exige **admin** além de `ALLOW_MOCK_COLLECT=true`
- Service: `PrinterCollector.collect_and_save`
- Banco/rede: SNMP real/mock, grava `printer_readings`, avalia alertas
- Frontend: não utilizado
- Estado: backend funcional; mock depende de `ALLOW_MOCK_COLLECT`

### `POST /api/collect/fleet`

- Arquivo: `backend/app/routes/collect.py`
- Função: `collect_fleet`
- Auth: **admin** (coleta simulada de toda a frota)
- Service: `PrinterCollector` em modo fleet mock
- Banco/rede: grava leituras e alertas
- Frontend: não utilizado
- Estado: funcional para cenário simulado; não é o fluxo de discovery

### `GET /api/collect/scenarios`

- Arquivo: `backend/app/routes/collect.py`
- Função: `list_scenarios`
- Auth: **admin** (expõe a configuração de mock)
- Service: lista cenários de `snmp_mock`
- Banco/rede: não acessa rede; lê configuração
- Frontend: não utilizado
- Estado: diagnóstico/mock

### `GET /api/collect/scheduler`

- Arquivo: `backend/app/routes/collect.py`
- Função: `get_scheduler_status`
- Auth: **admin**
- Service: `scheduler_status`
- Banco/rede: lê estado e conta impressoras ativas
- Frontend: não utilizado
- Estado: funcional para diagnóstico

## Print Server

**Fase 4 — múltiplos servidores.** Até aqui um Print Server existia só como
`PRINT_SERVER_HOST` (um host global no `.env`) mais a string `printers.server`,
que já era parte da identidade `(server, name)` desde a Etapa 4. A camada de
serviço **já era multi-servidor** — `discover_printers(server)` e
`sync_printers(session, server=...)` sempre aceitaram o host, e o sync só mexe
nas impressoras daquele servidor. O que faltava era o registro por trás dessa
string: a tabela `print_servers`.

`PrintServer.host` guarda exatamente o mesmo valor de `Printer.server`, que
continua sendo a chave natural (participa do `UniqueConstraint (server, name)`).
`Printer.print_server_id` é a ligação estruturada (FK), preenchida pela migração
e mantida pelo `printer_sync` — as duas representações são gravadas sempre
juntas, num único lugar, para não divergirem.

As rotas sem id (`/servers/discover`, `/servers/sync`, `/servers/current`)
continuam operando sobre o servidor padrão e **não mudaram** — é o que o painel
usa hoje.

### `GET /api/servers`

- Arquivo: `backend/app/routes/servers.py`
- Função: `list_servers`
- Auth: autenticado (qualquer papel)
- Banco/rede: lê `print_servers` e conta `printers` por host
- Frontend: ainda não utilizado (interface é da Fase 5)
- Estado: funcional
- Retorno: `id`, `host`, `name`, `mode`, `active`, `last_status`, `last_error`,
  `last_seen_at`, `last_sync_at`, `created_at`, `printer_count`,
  `active_printer_count`, `is_default`

### `POST /api/servers`

- Arquivo: `backend/app/routes/servers.py`
- Função: `create_server`
- Auth: **admin**
- Banco/rede: insere em `print_servers` e liga impressoras órfãs de mesmo host
- Estado: funcional
- Corpo: `host` (obrigatório, único), `name` opcional, `mode` (`mock`/`real`)
- Erros: `409` host já registrado · `422` modo inválido ou host vazio

### `PATCH /api/servers/{server_id}`

- Arquivo: `backend/app/routes/servers.py`
- Função: `update_server`
- Auth: **admin**
- Estado: funcional
- Corpo (opcionais): `name`, `mode`, `active`
- **Não aceita `host`**: é a chave natural presente em `printers.server`;
  renomeá-la orfanaria silenciosamente todas as impressoras do servidor
- Erros: `404` id inexistente · `422` modo inválido

### `POST /api/servers/{server_id}/discover`

- Arquivo: `backend/app/routes/servers.py`
- Função: `discover_server`
- Auth: **admin**
- Service: `discover_printers(host, mode=...)` + `enrich_discovered_printers`
- Banco/rede: não grava impressoras; grava o desfecho em `print_servers`
  (`last_status`, `last_error`, `last_seen_at`)
- Estado: funcional
- Usa o **modo do próprio servidor**, não o global
- Erros: `404` id inexistente · `409` servidor desativado · `502` falha no RPC

### `POST /api/servers/{server_id}/sync`

- Arquivo: `backend/app/routes/servers.py`
- Função: `sync_server`
- Auth: **admin**
- Service: `sync_printers(session, server=host, mode=...)`
- Banco/rede: escreve em `printers` **apenas** deste servidor; grava
  `last_sync_at` em `print_servers`
- Estado: funcional
- Impressoras de outros servidores nunca são tocadas nem desativadas
- Erros: `404` id inexistente · `409` servidor desativado · `502` falha no RPC

### `GET /api/servers/current`

- Arquivo: `backend/app/routes/servers.py`
- Função: `get_current_server`
- Auth: autenticado (qualquer papel)
- Service: nenhum
- Banco/rede: lê configuração
- Frontend: não utilizado
- Estado: funcional para diagnóstico
- Mantida como estava; a visão do parque de servidores está em `GET /api/servers`

### `POST /api/servers/discover`

- Arquivo: `backend/app/routes/servers.py`
- Função: `discover`
- Auth: **admin**
- Opera sobre o servidor **padrão**; para escolher o servidor use `POST /api/servers/{id}/discover`
- Service: `discover_printers`
- Banco/rede: Print Server mock ou PowerShell/RPC real; não grava banco
- Frontend: usado pelo botão "Escanear Rede" (`handleDiscovery()` em `src/lib/app-data.tsx`, painel `DiscoveryResults.tsx`)
- Estado: backend funcional; modo padrão é mock
- Resposta: informa `source` como `print_server_mock` ou `print_server_real`
- Cada item informa `name`, `server`, `port_name`, `driver_name`, `ip`, `ip_resolution`, `model` e `printer_type`
- Na FASE 3, cada item também informa `reachable`, `snmp_responded`, `status`, `status_reason`, `page_count`, `uptime`, `toners`, `ip_group_size` e `network_query_reused`
- `ip` fica `null` e `ip_resolution` fica `unresolved` quando a porta não fornece IPv4, como `USB001`
- O enriquecimento usa o SNMP real apenas quando `PRINT_SERVER_MODE=real`; em `mock`, usa `MockSNMPClient` explicitamente e não acessa a rede
- A rota não recebe `Session` e não cria `PrinterReading` ou `Alert`

### `POST /api/servers/sync`

- Arquivo: `backend/app/routes/servers.py`
- Função: `sync`
- Auth: **admin**
- Opera sobre o servidor **padrão**; para escolher o servidor use `POST /api/servers/{id}/sync`
- Service: `sync_printers`
- Banco/rede: Print Server e escrita em `printers`
- Frontend: não utilizado
- Estado: funcional; operação mutável

## Diagnóstico

### `GET /`

Retorna mensagem de identificação da API. Público e sem uso conhecido pelo frontend.

### `GET /health`

Retorna `{"status": "ok"}`. Público e adequado para health check básico, sem validar banco, SNMP ou Print Server.

## Escanear Rede (implementado)

O endpoint usado pelo botão "Escanear Rede" é `POST /api/servers/discover` (ver seção Print Server acima), não um endpoint separado `/api/discovery/scan`. Características:

- JWT obrigatório;
- consulta Print Server;
- deduplica IPs;
- consulta ping/SNMP quando aplicável;
- retorna resultado transitório (não persistido);
- não chama `sync_printers()`;
- não grava SQLite.

O frontend chama esse endpoint diretamente (`discoverPrinters()` em `src/lib/api.ts`), e não `GET /api/printers/with-status`.
