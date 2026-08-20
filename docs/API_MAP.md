# Mapa da API

Prefixo configurado: `/api`.

## Autenticação

### `POST /api/auth/login`

- Arquivo: `backend/app/routes/auth.py`
- Função: `login`
- Auth: não exige JWT
- Service: `verify_password`, `create_access_token`
- Banco/rede: consulta `users` no SQLite
- Frontend: usado por `src/lib/auth.ts`
- Estado: funcional
- Retorno: token JWT e usuário

### `POST /api/auth/register`

- Arquivo: `backend/app/routes/auth.py`
- Função: `register`
- Auth: não exige JWT
- Service: hash e token
- Banco/rede: insere em `users`
- Frontend: não utilizado
- Estado: backend funcional, UI ausente
- Observação: `name` é parâmetro de query

## Impressoras

### `GET /api/printers`

- Arquivo: `backend/app/routes/printers.py`
- Função: `list_printers`
- Auth: pública
- Service: nenhum
- Banco/rede: lê `printers` no SQLite
- Frontend: não utilizado atualmente
- Estado: funcional

### `GET /api/printers/with-status`

- Arquivo: `backend/app/routes/printers.py`
- Função: `list_printers_with_status`
- Auth: pública
- Service: nenhum
- Banco/rede: lê `printers` e a leitura mais recente de `printer_readings`
- Frontend: usado pelo dashboard, impressoras e toner
- Estado: funcional para consulta

### `GET /api/printers/monthly-report`

- Arquivo: `backend/app/routes/printers.py`
- Função: `monthly_report`
- Auth: pública
- Service: nenhum
- Banco/rede: calcula diferenças de `printer_readings`
- Frontend: usado por `loadMonthlyReportFromApi`
- Estado: funcional quando há leituras suficientes

### `GET /api/printers/{printer_id}`

- Arquivo: `backend/app/routes/printers.py`
- Função: `get_printer`
- Auth: pública
- Banco/rede: lê `printers`
- Frontend: não utilizado diretamente
- Estado: funcional

### `POST /api/printers`

- Arquivo: `backend/app/routes/printers.py`
- Função: `create_printer`
- Auth: JWT obrigatório
- Banco/rede: insere em `printers`
- Frontend: helper existe, tela não chama
- Estado: backend funcional, UI ausente

### `PATCH /api/printers/{printer_id}`

- Arquivo: `backend/app/routes/printers.py`
- Função: `update_printer`
- Auth: JWT obrigatório
- Banco/rede: altera `printers`
- Frontend: helper existe, tela não chama
- Estado: backend funcional, UI ausente

### `GET /api/printers/{printer_id}/readings`

- Arquivo: `backend/app/routes/printers.py`
- Função: `get_printer_readings`
- Auth: pública
- Banco/rede: lê `printer_readings`
- Frontend: helper existe, tela History não chama
- Estado: funcional, subutilizado

### `POST /api/printers/{printer_id}/readings`

- Arquivo: `backend/app/routes/printers.py`
- Função: `create_printer_reading`
- Auth: JWT obrigatório
- Banco/rede: insere leitura manual
- Frontend: não utilizado
- Estado: funcional no backend, risco de dados manuais sem fluxo de UI

## Alertas

### `GET /api/alerts`

- Arquivo: `backend/app/routes/alerts.py`
- Função: `list_alerts`
- Auth: pública
- Banco/rede: lê `alerts` no SQLite
- Frontend: usado com `resolved=false`
- Estado: funcional
- Filtros: `severity`, `resolved`, `printer_id`, `alert_type`

### `GET /api/alerts/{alert_id}`

- Arquivo: `backend/app/routes/alerts.py`
- Função: `get_alert`
- Auth: pública
- Banco/rede: lê `alerts`
- Frontend: não utilizado
- Estado: funcional

### `POST /api/alerts/{alert_id}/notify`

- Arquivo: `backend/app/routes/alerts.py`
- Função: `notify_alert`
- Auth: JWT obrigatório
- Service: `send_toner_alert_webhook`
- Banco/rede: lê alerta/impressora e chama webhook externo
- Frontend: não utilizado
- Estado: backend parcial

### `PATCH /api/alerts/{alert_id}/resolve`

- Arquivo: `backend/app/routes/alerts.py`
- Função: `resolve_alert`
- Auth: atualmente sem `require_user`
- Banco/rede: altera `alerts.resolved_at`
- Frontend: não utilizado
- Estado: funcional, mas com falha de proteção

## Coleta

### `POST /api/collect/printers/{printer_id}`

- Arquivo: `backend/app/routes/collect.py`
- Função: `collect_printer`
- Auth: JWT obrigatório
- Service: `PrinterCollector.collect_and_save`
- Banco/rede: SNMP real/mock, grava `printer_readings`, avalia alertas
- Frontend: não utilizado
- Estado: backend funcional; mock depende de `ALLOW_MOCK_COLLECT`

### `POST /api/collect/fleet`

- Arquivo: `backend/app/routes/collect.py`
- Função: `collect_fleet`
- Auth: JWT obrigatório
- Service: `PrinterCollector` em modo fleet mock
- Banco/rede: grava leituras e alertas
- Frontend: não utilizado
- Estado: funcional para cenário simulado; não é o fluxo de discovery

### `GET /api/collect/scenarios`

- Arquivo: `backend/app/routes/collect.py`
- Função: `list_scenarios`
- Auth: pública
- Service: lista cenários de `snmp_mock`
- Banco/rede: não acessa rede; lê configuração
- Frontend: não utilizado
- Estado: diagnóstico/mock

### `GET /api/collect/scheduler`

- Arquivo: `backend/app/routes/collect.py`
- Função: `get_scheduler_status`
- Auth: pública
- Service: `scheduler_status`
- Banco/rede: lê estado e conta impressoras ativas
- Frontend: não utilizado
- Estado: funcional para diagnóstico

## Print Server

### `GET /api/servers/current`

- Arquivo: `backend/app/routes/servers.py`
- Função: `get_current_server`
- Auth: pública
- Service: nenhum
- Banco/rede: lê configuração
- Frontend: não utilizado
- Estado: funcional para diagnóstico

### `POST /api/servers/discover`

- Arquivo: `backend/app/routes/servers.py`
- Função: `discover`
- Auth: JWT obrigatório
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
- Auth: JWT obrigatório
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
