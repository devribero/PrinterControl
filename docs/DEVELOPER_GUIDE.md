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

A aplicação FastAPI é `app.main:app`.

O arquivo `backend/app/main.py` tem um bloco de execução direta que sobe em
`0.0.0.0:8000` com `reload=True`. **Isso é conveniência de desenvolvimento e
não deve ser usado em produção**: `0.0.0.0` expõe a API a toda a rede, em HTTP
puro, com o token trafegando no header. Em produção, o comando é sempre:

```powershell
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Ver D6 em [`TECHNICAL_DEBT.md`](TECHNICAL_DEBT.md).

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

`scripts/` hoje só tem `Servico-PrinterControl.ps1` (instalar/parar/iniciar
o backend como tarefa agendada — ver `OPERATIONS.md`). Os scripts
pré-backend (`Coletar-Impressoras.ps1`, `Relatorio-Mensal.ps1`,
`Simular-Ambiente.ps1`) foram removidos: a coleta SNMP, o relatório mensal e
o modo de demonstração são todos feitos pelo próprio backend Python hoje
(`backend/app/services/snmp.py`, `GET /api/printers/monthly-report`,
`ENVIRONMENT=demo`).

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

Eles não formam uma suíte pytest convencional: são scripts que executam lógica
durante a importação, usam bancos/mocks temporários e imprimem `[OK]`/`[FALHA]`.

Rodam com o Python do venv, de dentro de `backend/`:

```powershell
.\venv\Scripts\python.exe tests_environment.py
```

Duas suítes **falham hoje por motivo conhecido** (D8): `tests_fleet.py` e
`tests_printers_crud.py` esperam 73 impressoras e o banco tem 79.
`tests_collect_api.py` não roda por falta de `requests` (D9). As demais passam.

Suítes que exigem o backend rodando (`tests_printers_crud.py`,
`tests_collect_api.py`) leem as credenciais do ambiente
(`TEST_ADMIN_PASSWORD`), já que a senha das contas semeadas deixou de ser fixa.

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

> **A lista completa e atualizada vive em
> [`TECHNICAL_DEBT.md`](TECHNICAL_DEBT.md) (D1–D13).** Não mantenha uma
> segunda lista aqui — foi assim que itens já resolvidos continuaram
> aparecendo como pendentes por semanas.

Resumo dos que mais afetam quem desenvolve:

- **D1** — FK órfã para `printers_old`. **Não ligue `PRAGMA foreign_keys=ON`**:
  derruba toda a coleta.
- **D2** — sem migrações versionadas. `create_all()` não altera tabela
  existente; adicionar coluna a um modelo não muda o banco já criado.
- **D6** — o bloco `if __name__ == "__main__"` de `app/main.py` sobe em
  `0.0.0.0` com `reload=True`. Para produção use sempre
  `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`.
- **D7/D8/D9** — os testes não são pytest, duas suítes falham por contagem
  desatualizada (73 vs 79 impressoras) e `tests_collect_api.py` não roda por
  falta de `requests`.
- **D10** — o frontend não tem teste automatizado nenhum.
- **D11** — o fallback do painel para dados de demonstração pode mascarar API
  indisponível (mitigado com faixa e badge).
- **D3** — SQLite é single-node e tem um escritor por vez.

### Já resolvido — não reabra

Estes itens constavam aqui como pendentes e **não são mais verdade**:
`SECRET_KEY` de desenvolvimento (produção recusa subir), CORS apenas local
(é por ambiente, com validação de produção), resolução de alerta sem JWT
(exige `operator`), e o botão “Verificar agora” (dispara coleta).

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
