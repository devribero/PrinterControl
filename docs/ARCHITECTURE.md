# Arquitetura do PrinterControl

## Escopo

Este documento descreve o comportamento encontrado no código atual. A arquitetura futura do botão **Escanear Rede real** está documentada na seção específica ao final, mas não está implementada.

## Arquitetura atual

```text
Next.js / React
    |
    | src/lib/api.ts
    | Authorization: Bearer <JWT>
    v
FastAPI
    |
    v
Routes (/api)
    |
    v
Services
    |------------------|-------------------|
    v                  v                   v
SQLite             SNMP real/mock      Print Server
                                          |
                                          v
                                  PowerShell / RPC / Windows
```

## Frontend

O frontend está em `src/app`, `src/components` e `src/lib`.

`AppDataProvider`, em `src/lib/app-data.tsx`, mantém:

- conta logada;
- impressoras;
- alertas;
- filtros;
- indicadores do dashboard;
- impressora selecionada;
- estado do botão de atualização.

Na inicialização, o provider tenta consultar em paralelo:

```text
GET /api/printers/with-status
GET /api/alerts?resolved=false
GET /api/printers/monthly-report
```

Quando a API responde, os dados são adaptados por `src/lib/adaptApi.ts`. Quando a API falha, o frontend usa dados de demonstração em `src/data/printers.ts` e, quando disponível, JSONs em `public/data`.

## Cliente de API

`src/lib/api.ts` é o cliente HTTP central. Ele:

- resolve `NEXT_PUBLIC_API_URL`;
- usa `http://127.0.0.1:8000` como fallback;
- serializa JSON;
- envia `Authorization: Bearer <token>`;
- normaliza erros em `ApiError`;
- fornece helpers `GET`, `POST` e `PATCH`.

Não há proxy ou rewrite configurado em `next.config.ts`.

## FastAPI

`backend/app/main.py` cria a aplicação, configura CORS, registra as rotas e inicializa o banco no `lifespan`. O scheduler também é tentado no `lifespan`, mas fica desligado por padrão por `COLLECTION_ENABLED=false`.

Rotas registradas:

- `auth`;
- `printers`;
- `alerts`;
- `collect`;
- `servers`.

As rotas de leitura são abertas no código atual. Operações de escrita normalmente usam `require_user`, com a exceção observada de `PATCH /api/alerts/{alert_id}/resolve`.

## Banco

O banco padrão é SQLite em `backend/printer_control.db`. Os modelos SQLModel representam:

- usuários;
- impressoras;
- leituras;
- dados mensais;
- alertas;
- histórico de toner.

A identidade atual da impressora é `(server, name)`. O IP não é único porque filas diferentes podem compartilhar o mesmo equipamento físico.

## Print Server

`backend/app/services/print_server.py` possui dois modos:

- `mock`: retorna uma frota fixa e não acessa rede;
- `real`: executa `powershell.exe` com `Get-Printer` e `Get-PrinterPort`.

A descoberta não grava banco. A sincronização está separada em `printer_sync.py` e é acionada por `POST /api/servers/sync`.

## SNMP e coleta

`backend/app/services/snmp.py` consulta ping, `sysUpTime`, contador acumulativo e suprimentos via UDP/161. `PrinterCollector` converte o resultado em `PrinterReading`, persiste e dispara `alert_engine.evaluate_reading`.

A coleta da frota, em `printer_fleet.py`:

1. seleciona `printers.active=True`;
2. agrupa por IP;
3. deduplica a consulta de rede dentro do ciclo;
4. executa I/O de rede em threads;
5. persiste leituras sequencialmente na sessão SQLite;
6. avalia alertas por impressora.

O scheduler não descobre nem sincroniza o Print Server. Ele coleta somente a frota ativa já existente no SQLite.

## Alertas

O motor cria condições para:

- impressora offline;
- toner preto, ciano, magenta ou amarelo baixo/crítico.

Limites atuais:

- `<=20%`: warning;
- `<=10%`: critical.

A recuperação resolve automaticamente a condição. Toner crítico novo ou escalado pode disparar `WEBHOOK_URL`.

## Legado

`Main.ps1` e os scripts PowerShell representam a arquitetura anterior baseada em Print Server, SNMP e JSON estático. Eles não são a mesma via de comunicação usada pelo frontend moderno quando a API FastAPI está disponível.

## PLANO DE IMPLEMENTAÇÃO — ESCANEAR REDE REAL

### Objetivo futuro

```text
Vercel / Next.js
    | HTTPS
Cloudflare Tunnel
    |
FastAPI em máquina dentro da rede corporativa
    |-------------------|
    v                   v
Print Server          SNMP
    \                 /
     v               v
       impressoras reais
```

A máquina corporativa faria somente conexões de saída para o Cloudflare Tunnel. Não seriam necessários port forwarding, abertura de porta no roteador ou exposição direta da porta 8000.

### A. Endpoint (implementado)

O endpoint escolhido e já implementado é:

```text
POST /api/servers/discover
```

É somente leitura: exige JWT, consulta o Print Server e o enriquecimento SNMP, e não grava nada no banco. Não chama `/api/servers/sync` automaticamente — sincronização continua sendo uma ação manual separada.

### B. Service reutilizável

O novo fluxo deve reutilizar um service de orquestração próprio de descoberta, aproveitando:

- `print_server.discover_printers()` para a lista oficial;
- `SNMPClient` para conectividade e telemetria;
- regras de `PrinterCollector` para cor/etiqueta;
- adaptadores de schema existentes.

Não se deve reutilizar `sync_printers()` no primeiro estágio, porque ele grava e desativa registros ausentes.

### C. Funções Print Server reutilizáveis

Podem ser reutilizadas:

- `discover_printers()`;
- `_real_discover()`;
- `_run_powershell_json()`;
- `DiscoveredPrinter`;
- `PrintServerError`.

A descoberta deve executar em `PRINT_SERVER_MODE=real` para dados reais. O modo mock deve ser explícito e proibido no fluxo de validação real.

### D. Funções SNMP reutilizáveis

Podem ser reutilizados:

- `SNMPClient.collect()`;
- `_ping()`;
- `SNMPResult`;
- regras de `PrinterCollector.is_label_printer()`;
- regras de `PrinterCollector.is_color_printer()`.

A varredura não deve consultar SNMP em filas sem IP válido, USB, etiqueta ou portátil quando as regras atuais indicarem que Printer-MIB não é aplicável.

### E. Formato do resultado

O backend deverá devolver um schema próprio de descoberta, sem fingir que o resultado já é uma impressora persistida. Cada item deve conter, no mínimo:

```text
name
server
port_name
ip
driver_name
model
printer_type
exists_in_database
printer_id
is_new_discovery
reachable
snmp_responded
status
page_count
toners
uptime
error
```

O frontend deverá adaptar esse contrato para um tipo separado, por exemplo `DiscoveredPrinter`, em vez de converter diretamente para `Printer` persistida.

### F. Arquivos frontend envolvidos posteriormente

Prováveis arquivos:

- `src/lib/api.ts`: helper do endpoint novo e tipos de resposta;
- `src/lib/app-data.tsx`: estado separado para resultado de descoberta;
- `src/app/page.tsx`: ação real do botão;
- `src/components/PrinterTable.tsx` ou componente novo: exibição dos resultados;
- `src/components/PrinterDetailsModal.tsx`, se detalhes da descoberta forem exibidos;
- `src/types.ts`: tipo de impressora descoberta;
- CSS do componente que apresentar os estados.

Não se deve substituir silenciosamente a lista cadastrada do dashboard pela lista descoberta sem uma decisão explícita de UX.

### G. Arquivos backend envolvidos posteriormente

Prováveis arquivos:

- novo `backend/app/routes/discovery.py` ou extensão controlada de `servers.py`;
- novo `backend/app/schemas/discovery.py`;
- novo `backend/app/services/discovery.py`;
- `backend/app/main.py` para registrar router, se for criado;
- testes novos de discovery;
- eventualmente `config.py` para parâmetros de timeout e limites.

Não é necessário alterar `printer_sync.py` na primeira implementação, porque o requisito é não gravar automaticamente.

### H. Como evitar o refetch disfarçado

`handleScan()` deverá deixar de chamar `loadFromApi()` como ação principal. Ele deverá:

1. chamar explicitamente o helper do endpoint de discovery;
2. armazenar o resultado em estado separado;
3. exibir status de operação e erro;
4. apresentar a origem `descoberta agora`;
5. manter a lista SQLite separada;
6. não chamar `fetchPrintersWithStatus()` como substituto da descoberta.

A atualização normal do dashboard deve continuar sendo uma ação diferente.

### I. Diferenciar SQLite de descoberta atual

O frontend deve manter dois conjuntos:

```text
printers: Printer[]              // cadastro vindo do SQLite
discoveredPrinters: Discovered[] // resultado da execução atual
```

A comparação deve usar a identidade `(server, name)` quando existir. O IP pode ser usado como evidência de correspondência, mas não como chave única.

O resultado precisa mostrar badges ou campos explícitos:

- `Cadastrada no SQLite`;
- `Descoberta agora`;
- `Nova no resultado`;
- `Online`;
- `Offline`;
- `SNMP respondeu`;
- `SNMP sem resposta`.

### J. Evitar contaminação por mock

- O endpoint real deve aceitar somente modo real por padrão.
- `PRINT_SERVER_MODE=mock` não pode ser usado como fallback silencioso.
- `ALLOW_MOCK_COLLECT` não deve habilitar discovery real nem ser tratado como equivalente.
- O resultado de discovery não deve chamar `session.add`, `commit` ou `sync_printers()`.
- Testes devem usar doubles/mocks em banco temporário, nunca o banco padrão.
- A resposta deve indicar a origem e o modo efetivo.

### K. JWT

A rota deve usar:

```python
_user: User = Depends(require_user)
```

O cliente frontend já envia o Bearer token automaticamente por `apiRequest`. A resposta de ausência ou invalidez deve ser `401`. O endpoint não deve ser exposto como leitura pública porque dispara consultas internas à rede.

### L. Cloudflare Tunnel

O fluxo esperado é:

```text
Vercel
  -> HTTPS para domínio público do Tunnel
Cloudflare Tunnel
  -> conexão de saída já estabelecida pela máquina corporativa
FastAPI em loopback ou interface interna
```

O Tunnel deve encaminhar somente para o FastAPI. Não deve publicar o Print Server, SNMP ou SQLite. O FastAPI continua fazendo conexões internas para `elgjunprt` e UDP/161.

### M. Variáveis futuras

Frontend:

```text
NEXT_PUBLIC_API_URL=https://api.exemplo.tld
```

Backend, conforme necessidade já prevista:

```text
SECRET_KEY=<valor forte>
DATABASE_URL=sqlite:///./printer_control.db
PRINT_SERVER_MODE=real
PRINT_SERVER_HOST=elgjunprt
PRINT_SERVER_TIMEOUT_SECONDS=30
SNMP_COMMUNITY=<valor protegido>
SNMP_TIMEOUT=1.5
SNMP_RETRIES=1
COLLECTION_ENABLED=false
WEBHOOK_URL=<se necessário>
```

Também podem ser necessárias variáveis novas de discovery, como timeout total, limite de IPs e habilitação explícita. Seus nomes devem ser definidos na implementação.

### N. CORS

Devem ser adicionadas as origens HTTPS reais da Vercel, por exemplo:

```text
https://app.exemplo.vercel.app
https://dominio-customizado.exemplo
```

A origem do Cloudflare Tunnel não substitui necessariamente a origem do navegador. O CORS deve permitir o domínio que aparece no `Origin` da requisição do frontend.

### O. SQLite

É possível manter SQLite para um primeiro cenário controlado, mas há riscos:

- arquivo local depende da disponibilidade da máquina;
- backup e restauração são responsabilidade operacional;
- concorrência entre scheduler, requests e migrações precisa ser controlada;
- não é ideal para múltiplas réplicas do FastAPI;
- o Tunnel não transforma SQLite em banco distribuído.

O fato de o frontend estar na Vercel não significa que o banco deva ir para a Vercel. O SQLite deve permanecer junto do backend, se mantido.

### P. Riscos antes do Tunnel

Corrigir ou revisar antes da exposição:

- substituir o `SECRET_KEY` padrão;
- proteger `PATCH /api/alerts/{id}/resolve` com JWT;
- revisar rotas GET públicas;
- não expor documentação Swagger sem política definida;
- validar CORS restrito;
- remover/rotacionar o webhook embutido em `Main.ps1`;
- manter `ALLOW_MOCK_COLLECT=false`;
- manter `PRINT_SERVER_MODE=real` somente na máquina corporativa;
- validar limites e timeouts de discovery;
- evitar SSRF por parâmetros de servidor/IP não validados;
- registrar auditoria das descobertas;
- usar HTTPS no caminho público;
- garantir que o Tunnel não publique serviços internos além do FastAPI.

### Q. Testes locais antes da rede corporativa

1. Testar o contrato do endpoint com Print Server mock.
2. Testar deduplicação de IPs.
3. Testar comparação com registros SQLite temporários.
4. Testar IP inválido, USB e impressora sem porta TCP/IP.
5. Testar respostas online/offline/SNMP sem resposta usando doubles.
6. Testar que nenhuma sessão é alterada.
7. Testar JWT ausente, inválido e válido.
8. Testar timeout e erro do PowerShell.
9. Testar adaptação no frontend com resposta salva/fixture.
10. Testar que “Escanear Rede” não chama `/api/printers/with-status`.

## Fases futuras

### FASE 1 — conexão local frontend → backend

- confirmar URL da API;
- confirmar CORS local;
- validar login e GETs existentes;
- não envolver rede corporativa.

### FASE 2 — descoberta via Print Server

- criar contrato de discovery;
- reutilizar `discover_printers()`;
- executar somente em modo real na máquina adequada;
- não gravar no banco.

### FASE 3 — SNMP real

- implementada a camada transitória `services/discovery.py`;
- reutiliza `SNMPClient` e `SNMPResult`;
- deduplica IPs e reaplica o resultado às filas;
- aplica regras de etiqueta/portátil sem criar `Printer`;
- diferencia ping, SNMP parcial, timeout e erro de socket;
- modo mock usa `MockSNMPClient` sem rede;
- nenhum dado é persistido e a validação SNMP corporativa continua pendente.

### FASE 4 — botão Escanear Rede

- criar helper API específico;
- separar descoberta de refresh;
- mostrar resultados e estados;
- manter SQLite inalterado.

### FASE 5 — Cloudflare Tunnel

- instalar/configurar o Tunnel na máquina autorizada;
- encaminhar somente para FastAPI;
- validar saída sem port forwarding.

### FASE 6 — Vercel → Cloudflare → FastAPI

- configurar `NEXT_PUBLIC_API_URL`;
- adicionar CORS da Vercel;
- validar JWT, erros e timeouts por HTTPS.

### FASE 7 — máquina na rede corporativa

- validar Print Server real;
- validar SNMP real;
- validar permissões, DNS, RPC e firewall existente;
- não abrir portas de entrada desnecessárias.

### FASE 8 — sincronização permanente

Somente após a validação, avaliar se a descoberta deve chamar sincronização. Essa etapa deve ser separada do scan inicial e incluir confirmação, auditoria e política para desativação.
