# Guia do Desenvolvedor

## Stack encontrada

Frontend:

- Next.js;
- React;
- TypeScript;
- Recharts;
- Lucide React;
- Oxlint.

Backend:

- FastAPI;
- SQLModel;
- SQLite;
- APScheduler;
- Python;
- PowerShell para Print Server real.

## Comandos do frontend

Os comandos declarados em `package.json` são:

```bash
npm install
npm run dev
npm run build
npm run start
npm run lint
```

`npm install` não deve ser executado como parte de uma operação de produção sem autorização, pois instala/altera dependências locais.

## Backend

As dependências estão em `backend/requirements.txt`.

A aplicação FastAPI é `app.main:app`. O arquivo `backend/app/main.py` possui execução direta com Uvicorn em:

```text
0.0.0.0:8000
```

O backend espera que os imports `app.*` sejam resolvidos a partir de `backend`.

## Variáveis de ambiente

Frontend, em `.env.example`:

```text
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

Backend, em `backend/.env.example`:

```text
DATABASE_URL=sqlite:///./printer_control.db
SECRET_KEY=change-me-in-production
ALLOW_MOCK_COLLECT=false
COLLECTION_ENABLED=false
COLLECTION_INTERVAL_MINUTES=5
COLLECTION_MODE=real
COLLECTION_SCENARIO=online_mono
COLLECTION_MAX_WORKERS=4
PRINT_SERVER_MODE=mock
PRINT_SERVER_HOST=elgjunprt
PRINT_SERVER_TIMEOUT_SECONDS=30
WEBHOOK_URL=
WEBHOOK_TIMEOUT_SECONDS=5
```

O código também define `SNMP_COMMUNITY`, `SNMP_TIMEOUT`, `SNMP_RETRIES` e origens CORS padrão.

## Banco

O banco padrão é `backend/printer_control.db`.

A inicialização chama `create_db_and_tables()`, que executa `create_all` e migrações idempotentes. Algumas migrações criam backup e alteram a estrutura de `printers`; portanto, não devem ser executadas contra o banco de produção sem procedimento autorizado.

Tabelas principais:

- `users`;
- `printers`;
- `printer_readings`;
- `printer_monthly`;
- `alerts`;
- `toner_history`.

## Scheduler

O scheduler é iniciado no `lifespan` do FastAPI apenas quando:

```text
COLLECTION_ENABLED=true
```

O modo mock exige `ALLOW_MOCK_COLLECT=true`. O modo real consulta toda a frota ativa do banco, agrupada por IP.

O scheduler não faz descoberta nem sincronização Print Server.

## SNMP

A coleta real usa:

- ping;
- UDP/161;
- community configurada;
- Printer-MIB;
- timeout e retries definidos na configuração.

O serviço distingue impressora offline, impressora acessível sem resposta SNMP e resposta SNMP parcial/completa.

## Print Server

O modo real usa `powershell.exe` e os comandos:

```powershell
Get-Printer -ComputerName elgjunprt
Get-PrinterPort -ComputerName elgjunprt
```

Isso exige Windows, PowerShell, PrintManagement, RPC, DNS e permissões na rede corporativa.

`POST /api/servers/discover` somente descobre. `POST /api/servers/sync` grava e altera cadastros.

## Scripts PowerShell

Comandos encontrados:

```powershell
pwsh .\scripts\Coletar-Impressoras.ps1
pwsh .\scripts\Relatorio-Mensal.ps1
pwsh .\scripts\Simular-Ambiente.ps1
```

- `Coletar-Impressoras.ps1` consulta Print Server/SNMP e grava JSON.
- `Relatorio-Mensal.ps1` grava histórico e relatório mensal.
- `Simular-Ambiente.ps1` grava dados fictícios locais.

Não executar esses scripts em ambiente operacional sem confirmar os caminhos de saída e a autorização para escrita.

## Testes

Existem scripts Python `backend/tests_*.py`, incluindo testes de:

- alertas;
- coleta;
- frota;
- Print Server;
- sincronização;
- CRUD;
- SNMP local;
- uptime;
- webhook.

Eles não formam necessariamente uma suíte pytest convencional: alguns executam lógica durante a importação e usam bancos/mocks temporários.

## O que não executar em produção sem autorização

- `POST /api/servers/sync`;
- qualquer `POST /api/collect/*`;
- migrações;
- `COLLECTION_ENABLED=true` sem janela operacional;
- modo mock com escrita habilitada;
- scripts que gravam `public/data` ou histórico;
- alterações no banco SQLite;
- scripts PowerShell contra Print Server real;
- descoberta de rede sem limites e auditoria.

## Riscos conhecidos

- fallback do frontend pode mascarar API indisponível;
- `SECRET_KEY` padrão não é apropriado para produção;
- CORS atual é apenas local;
- resolução de alerta não está protegida por JWT;
- SQLite é single-node;
- `Main.ps1` contém configuração de webhook embutida;
- ações de imprimir teste e configurações são simuladas;
- o botão “Verificar agora” não dispara coleta.

## Escanear Rede (implementado)

O botão "Escanear Rede" já está ligado ao frontend desde a Fase 4. O fluxo real, validado nas Fases 2–4:

```text
Frontend (handleDiscovery())
    ↓ POST /api/servers/discover + JWT
Print Server Discovery (discover_printers())
    ↓
deduplicação por IP + enriquecimento SNMP (enrich_discovered_printers())
    ↓
resultado transitório
    ↓
Frontend (estado discoveredPrinters, painel DiscoveryResults.tsx)
```

Esse fluxo não chama `sync_printers()` e não grava no SQLite — o resultado é transitório e a lista principal de impressoras cadastradas não é substituída. Sincronização permanente continua sendo `POST /api/servers/sync`, uma ação manual separada. O plano de deploy em produção (Cloudflare Tunnel, validação corporativa real) está em `docs/ARCHITECTURE.md` e `docs/DEPLOYMENT_ARCHITECTURE.md`.
