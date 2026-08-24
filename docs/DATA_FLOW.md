# Fluxo de Dados

## 1. Cadastro no SQLite

```text
printers
    ↓
GET /api/printers/with-status
    ↓
ApiPrinterWithStatus
    ↓
adaptPrinter()
    ↓
Printer do frontend
    ↓
Dashboard / Impressoras / Toner
```

`with-status` combina cada cadastro com a leitura mais recente encontrada em `printer_readings`. Sem leitura, o backend retorna status `offline`, contador zero e `last_seen` nulo.

## 2. Coleta SNMP real

```text
IP cadastrado
    ↓
ping
    ↓
SNMP UDP/161
    ↓
SNMPClient
    ↓
SNMPResult
    ↓
PrinterCollector
    ↓
PrinterReading
    ↓
SQLite
    ↓
Alert engine
    ↓
GET /api/printers/with-status e GET /api/alerts
    ↓
Frontend
```

O cliente consulta Printer-MIB para:

- uptime;
- contador acumulativo `prtMarkerLifeCount`;
- níveis de toner;
- capacidade e descrição de suprimentos.

O contador mensal não é lido diretamente. O backend calcula diferenças entre leituras do mês.

## 3. Coleta de frota

```text
SELECT printers WHERE active=true
    ↓
grupos por IP
    ↓
consulta única por IP no ciclo
    ↓
ThreadPoolExecutor para I/O de rede
    ↓
persistência sequencial
    ↓
PrinterReading por impressora
    ↓
Alert engine
```

Duas filas no mesmo IP compartilham o resultado de rede, mas recebem leituras persistidas separadas.

## 4. Print Server

```text
Print Server
    ↓
Get-Printer -ComputerName host
Get-PrinterPort -ComputerName host
    ↓
_run_powershell_json()
    ↓
port map: PortName -> PrinterHostAddress
    ↓
DiscoveredPrinter
    ↓
POST /api/servers/discover
    ↓
enrichment service (dedupe por IP)
    ↓
SNMPClient ou MockSNMPClient
    ↓
JSON com source, ip_resolution e telemetria transitória
```

A rota `POST /api/servers/discover` apenas retorna o resultado. A rota `POST /api/servers/sync` passa esse resultado para `printer_sync.py`, que grava/atualiza/desativa cadastros.

## 5. Sincronização

```text
DiscoveredPrinter
    ↓
chave (server, name)
    ↓
comparação com printers
    ↓
criar / atualizar / reativar / desativar
    ↓
SQLite
```

Impressoras ausentes não são apagadas. Ficam inativas para preservar leituras e alertas.

## 6. Alertas

```text
PrinterReading persistida
    ↓
evaluate_reading()
    ↓
condição offline / toner
    ↓
alerts
    ↓
webhook opcional para toner crítico
```

O webhook só é enviado quando um alerta crítico de toner é criado ou escalado, não a cada coleta enquanto a condição permanece igual.

## 7. Relatório mensal

O backend usa:

```text
maior page_count do período - menor page_count do período
```

O legado PowerShell usa `printers.json` e um arquivo de histórico para calcular deltas. São dois fluxos distintos:

- relatório via SQLite/FastAPI;
- relatório via JSON/PowerShell.

## 8. Fallback do frontend

```text
API FastAPI disponível
    ↓
SQLite/API

API indisponível
    ↓
public/data/monthly-report.json, se existir
    ↓
src/data/printers.ts
```

O fallback é deliberado no código e **sempre identificado na interface** (Fase 9):

- faixa no topo (`AppShell.tsx`) sempre que houver número fictício na tela;
- selo `DemoDataBadge` no próprio card, para quem lê um gráfico isolado ou tira print dele;
- rótulo do ambiente e três indicadores no rodapé.

A regra é "ou tudo da API, ou tudo de demonstração", com UMA exceção conhecida e agora
sinalizada: a frota pode ser real enquanto o relatório mensal ainda não fechou no backend.
Nesse caso os gráficos de consumo são fictícios, e tanto a faixa quanto os selos dizem isso.

## 9. Dados mock

Os pontos de entrada fictícios são:

- `src/data/printers.ts`;
- `backend/app/services/snmp_mock.py`;
- `backend/app/services/snmp_fleet_mock.py`;
- `_mock_discover()` em `print_server.py`;
- `scripts/Simular-Ambiente.ps1`;
- `public/data/*.json` gerados localmente.

O modo mock do Print Server é padrão na configuração atual. O modo mock de coleta exige
`ALLOW_MOCK_COLLECT=true`.

**Proteção de produção (Fase 9).** `ENVIRONMENT` tem três valores — `development`, `demo` e
`production` — e a simulação é bloqueada em duas camadas:

| Camada | Onde | O que faz |
|---|---|---|
| Boot | `app/config.py` | `production` **recusa subir** com `PRINT_SERVER_MODE != real` ou `ALLOW_MOCK_COLLECT=true` |
| Requisição | `app/services/environment_guard.py` | **409** em collect mock, discover/sync de servidor mock e criar/editar servidor com `mode="mock"` |

A segunda camada existe porque a primeira não alcança o modo **por servidor** (Fase 4): um
Print Server gravado com `mode="mock"` antes de a instância virar produção continua no banco,
e nenhuma validação de boot o enxerga.

`GET /health` publica o ambiente para o painel — não há `NEXT_PUBLIC_ENVIRONMENT`, porque uma
variável de build descreveria o bundle e não o servidor a que ele se conectou.

## 10. Escanear Rede (implementado)

```text
Frontend (botão "Escanear Rede", handleDiscovery())
    ↓ POST /api/servers/discover + JWT
FastAPI (routes/servers.py: discover())
    ↓
discover_printers()
    ↓
enrichment service (dedupe por IP, ping e SNMP aplicável)
    ↓
resultado transitório
    ↓
Frontend guarda em estado (discoveredPrinters) e exibe em DiscoveryResults.tsx
```

Este fluxo (ver também seção 4) não chama `sync_printers()` nem altera o SQLite. A lista principal de impressoras cadastradas não é substituída pelo resultado da descoberta.
