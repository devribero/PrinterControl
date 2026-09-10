# Bateria de testes em máquina do domínio — PrinterControl

## Atualização Fase A — 10/09/2026

A Fase A foi implementada localmente; **a validação em domínio permanece
pendente**. O restante deste documento preserva o diagnóstico anterior como
histórico. Main.ps1 foi removido da árvore; testes de sua GUI, instalação de
drivers e Point & Print não fazem parte do produto ativo. SYSTEM sem permissão
é hipótese, não causa raiz confirmada.

Sequência em campo:

1. Iniciar o backend na máquina de domínio usando explicitamente
   `backend/.env.dominio` (development/real), preservando o `.env` de dev.
   Ver o comando e a precedência de variáveis em [Operações](OPERATIONS.md).
2. Autenticar como admin e consultar `GET /health/print-server` na API do
   processo iniciado pela tarefa/serviço sob avaliação. Guardar HTTP, host,
   `configured_mode`, `probe_mode`, `identity`, `identity_error`, `category`,
   `detail`, `call_id`, `duration_ms` e `count`.
3. Executar discovery manual e correlacionar logs de Get-Printer e
   Get-PrinterPort; comparar contagem e nomes com a frota conhecida.
4. Se houver sync, queda >20% das filas ativas do host deve retornar 409,
   sem alterar impressoras; verificar `last_error` em `GET /api/servers`.
5. Com a evidência real, o operador decide se solicita a Fase B. Não trocar
   conta, permissões ou tarefa apenas por inferência a partir de SYSTEM.

Um diagnóstico 200 confirma a consulta mínima, não a completude da frota,
o acesso a portas nem SNMP. RPC indisponível não distingue sozinho firewall
e Spooler; resultado desconhecido deve permanecer inconclusivo.

**Documento de planejamento. Nada aqui foi executado.**
Gerado em 09/09/2026 a partir da leitura do código em
`fix/auditoria-qa-2026-09-08`.

> **Escopo e regra de ouro.** Este documento **descreve** os testes; não
> altera código, `.env`, GPO, contas, permissões ou infraestrutura. Todos os
> comandos marcados com ⚠️ **DESTRUTIVO** ou 🔒 **REQUER APROVAÇÃO** estão
> aqui para serem *lidos e aprovados por uma pessoa antes de rodar* — nunca
> para execução automática por um agente.

---

## 1. Sumário executivo

O PrinterControl tem **duas peças de software vivas**. A peça legada abaixo
permanece apenas no histórico Git desde a Fase A; sua localização e
funcionalidades na tabela descrevem o estado anterior à remoção:

| Peça | Onde | Como toca o domínio |
|---|---|---|
| **Backend FastAPI** | `backend/app/` | `powershell.exe → Get-Printer/Get-PrinterPort -ComputerName <print server>` (RPC/DCOM autenticado), SNMP/ICMP à frota, webhook HTTPS de saída, tarefa agendada do Windows |
| **Frontend Next.js** | `src/` | Nenhuma chamada ao AD. Depende do domínio só indiretamente: proxy corporativo, inspeção TLS, políticas de navegador, `allowedDevOrigins`, CORS |
| **Main.ps1 (legado)** | raiz do repo | GUI WPF: RPC ao print server, **Point & Print via UNC** (`\\servidor\fila`), instalação de driver `.inf`/`.exe`, resolução de atalhos `.lnk` para shares, UAC |

### O achado mais importante para o planejamento

**Não existe autenticação integrada ao Windows/AD em lugar nenhum do
sistema.** A verificação foi exaustiva: busca por `LDAP`, `Kerberos`, `NTLM`,
`Negotiate`, `SSPI`, `pywin32`, `ldap3`, `Get-ADUser`, `USERDOMAIN`,
`WindowsIdentity`, `Invoke-Command`, `New-PSSession`, `WinRM`, `WMI/CIM`
retorna **zero ocorrências funcionais** no backend e no frontend.

A autenticação é **100% aplicacional**: JWT HS256 assinado com `SECRET_KEY`,
senhas em argon2, contas na tabela `users` do SQLite, três papéis
(`viewer`/`operator`/`admin`) definidos em `backend/app/dependencies.py`.

**Consequência prática para a bateria de testes:**

1. Não há nada a testar em "SSO", "login com conta de domínio", "grupos do AD
   → papéis". Testes desse tipo seriam *falsos positivos de planejamento*.
2. O domínio entra por outro lugar, e é aí que a bateria precisa se
   concentrar: **a identidade do processo do backend** (`DOMÍNIO\usuário` ou
   `DOMÍNIO\MÁQUINA$`) é o que autentica o RPC ao print server. É a única
   credencial de domínio que o sistema usa — e ela é implícita, herdada do
   token do processo, nunca digitada.
3. Isso torna o **teste D-01 (conta de execução do serviço)** o mais crítico
   de todos: é o ponto onde nasce o "funciona quando eu rodo à mão / falha
   quando roda sozinho".

### Distribuição dos testes

| Categoria | Prefixo | Testes | Só no domínio |
|---|---|---:|---:|
| Autenticação (aplicacional) | `AU` | 7 | 1 |
| Active Directory / identidade | `AD` | 7 | 7 |
| Permissões | `PE` | 7 | 4 |
| Rede corporativa (SNMP/ICMP/DNS) | `RE` | 6 | 6 |
| Servidores (Print Server / RPC) | `SV` | 7 | 7 |
| Impressão (Point & Print, drivers) | `IM` | 5 | 5 |
| Segurança (firewall, EDR, proxy, TLS) | `SE` | 6 | 5 |
| Integrações de saída (webhook, GitHub) | `IN` | 4 | 3 |
| Infraestrutura (serviço, banco, backup, logs) | `IF` | 8 | 4 |
| Políticas de domínio / GPO | `GP` | 7 | 7 |
| Resiliência e tratamento de erro | `RS` | 7 | 4 |
| **Total** | | **71** | **53** |

---

## 2. Como o sistema funciona — o mapa que os testes seguem

```
                 ┌─────────────── MÁQUINA DO DOMÍNIO ────────────────┐
                 │                                                    │
  Print Server   │  powershell.exe -NoProfile -NonInteractive         │
  elgjunprt      │    Get-Printer     -ComputerName elgjunprt   ◄──── │ ① RPC/DCOM 135 + dinâmicas
  (membro do  ◄──┼──  Get-PrinterPort -ComputerName elgjunprt         │   autenticado pelo TOKEN
   domínio)      │              │                                     │   do processo (Kerberos/NTLM
                 │              ▼                                     │   implícito — nunca digitado)
                 │     print_server.py::_real_discover                 │
                 │              │                                     │
                 │              ▼                                     │
                 │     printer_sync.py::sync_printers ──► SQLite       │
                 │              │                        printer_control.db
                 │              ▼                                     │
  Impressoras ◄──┼──  snmp.py::_ping (ICMP)  ② ────────────────────── │
  10.x.x.x       │    snmp.py::_exchange (UDP/161, community public)   │
                 │              │                                     │
                 │              ▼                                     │
                 │     alert_engine.py ──► webhook_notifier.py ────────┼──► ③ HTTPS Power Automate
                 │                                                    │      (proxy / inspeção TLS)
                 │     uvicorn --host 127.0.0.1:8000                   │
                 │              ▲                                     │
                 └──────────────┼─────────────────────────────────────┘
                                │ ④ CORS + JWT Bearer
                       Navegador (Next.js) — políticas de navegador via GPO
```

Quatro fronteiras. Cada uma vira um bloco da matriz:

- **①** é a única que usa credencial de domínio.
- **②** é rede pura (ICMP + UDP/161) — firewall, VLAN, segmentação, EDR.
- **③** é saída para a internet — proxy, inspeção TLS, allowlist de URL.
- **④** é local ao navegador — CORS, políticas de navegador, armazenamento.

---

## 3. Inventário detalhado — funcionalidade por funcionalidade

Cada item traz os 12 campos pedidos. Prioridade: **P0** = bloqueia tudo,
**P1** = funcionalidade central, **P2** = importante, **P3** = borda.

---

### D-01 · Identidade do processo que executa a coleta

**1. Funcionalidade** — Todo acesso ao Print Server herda a identidade do
processo `python.exe`/`powershell.exe`. Não há `Get-Credential`,
`-Credential`, cofre, nem campo de senha em lugar nenhum do backend.

**2. Onde existe no projeto**
- `scripts/Servico-PrinterControl.ps1:33-41` — bloco "CONTA DE EXECUCAO",
  que documenta o problema explicitamente.
- `scripts/Servico-PrinterControl.ps1:118-134` — `New-ScheduledTaskPrincipal
  -UserId "SYSTEM" -LogonType ServiceAccount` (padrão) vs.
  `Register-ScheduledTask -User $Conta -Password $plain`.
- `backend/app/services/print_server.py:158-165` — o `subprocess.run` que
  herda esse token.

**3. Por que o domínio é relevante** — SYSTEM em máquina de domínio se
apresenta na rede como a **conta de máquina** `DOMÍNIO\NOME-DA-MÁQUINA$`.
Essa conta normalmente **não** tem permissão de enumerar filas em outro
servidor. O sintoma é traiçoeiro: a API sobe, `/health` diz `ok`, o painel
abre — e **toda coleta falha**, porque a falha está uma camada abaixo do que
o healthcheck observa.

**4. Pré-requisitos** — Máquina ingressada no domínio; tarefa
`PrinterControl-Backend` instalada; um segundo terminal com uma conta de
domínio interativa para comparação.

**5. Procedimento de teste**
```powershell
# (a) Qual é a identidade interativa de quem está testando
whoami
whoami /fqdn
whoami /groups | Select-String "Domain|Print|Admin"
[System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$env:USERDOMAIN; $env:USERDNSDOMAIN; $env:LOGONSERVER; $env:COMPUTERNAME

# (b) Sob qual conta a tarefa agendada roda de fato
Get-ScheduledTask -TaskName PrinterControl-Backend |
  Select-Object -ExpandProperty Principal |
  Format-List UserId, LogonType, RunLevel

# (c) A identidade do PROCESSO vivo (é ela que autentica o RPC)
Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
  ForEach-Object { $_.ProcessId; ($_ | Invoke-CimMethod -MethodName GetOwner) }
```

**6. Resultado esperado** — `Principal.UserId` deve ser **uma conta de
domínio com direito de leitura no print server**, não `SYSTEM`, *a menos que*
o teste D-02 comprove que a conta de máquina consegue enumerar.

**7. Como validar** — Objetivamente: rodar D-02 **duas vezes**, uma no
contexto interativo e uma no contexto da tarefa. Se a interativa funciona e a
da tarefa falha, a causa é esta e nenhuma outra.

**8. Evidências** — Saída completa dos três blocos acima; `Principal` em
texto; PID e owner do processo; horário.

**9. Possíveis erros** — `Access is denied` / `0x80070005`; a tarefa não é
criada se a conta não tiver `SeBatchLogonRight`; senha da conta de serviço
expirada por GPO derruba a tarefa em silêncio no próximo boot.

**10. Impacto se não funcionar** — Coleta 100% parada. O painel mostra a
última foto do banco indefinidamente, sem nenhum aviso visual de que está
congelado (não há alerta de "coleta parada" — ver RS-05).

**11. Dentro ou fora do domínio** — **Somente dentro.** Fora do domínio
SYSTEM não tem conta de máquina no AD e o cenário simplesmente não existe.

**12. Prioridade** — **P0.** Faça este primeiro; ele explica metade dos
outros achados possíveis.

---

### D-02 · Descoberta real via `Get-Printer -ComputerName` (RPC ao Print Server)

**1. Funcionalidade** — Enumeração das filas publicadas e o mapa
porta → `PrinterHostAddress`, que produz o IP usado por todo o SNMP depois.

**2. Onde existe**
- `backend/app/services/print_server.py:170-180` — os dois comandos exatos.
- `backend/app/services/print_server.py:130-155` — `_run_powershell_json`,
  `timeout=settings.print_server_timeout_seconds` (default **30 s**).
- `backend/app/services/print_server.py:190-196` — `port_map` e o fallback
  `ip = port_map.get(port_name) or port_name`.
- Endpoints: `POST /api/servers/discover` (host padrão) e
  `POST /api/servers/{id}/discover` — `backend/app/routes/servers.py`.

**3. Por que o domínio é relevante** — `Get-Printer -ComputerName` usa
RPC/DCOM sobre o serviço Spooler remoto. Exige (a) resolução do nome,
(b) porta 135 + faixa RPC dinâmica abertas, (c) **autenticação Kerberos ou
NTLM bem-sucedida**, (d) direito de leitura no Spooler remoto. Nada disso
existe fora do domínio.

**4. Pré-requisitos** — D-01 resolvido; `PRINT_SERVER_MODE=real` e
`PRINT_SERVER_HOST` apontando para o servidor correto (`elgjunprt` é o
default histórico em `config.py`); conta com token de sessão válido.

**5. Procedimento**
```powershell
# Camada 1 — o comando cru, exatamente como o Python o executa
powershell.exe -NoProfile -NonInteractive -Command `
  "Get-Printer -ComputerName 'elgjunprt' -ErrorAction Stop | Select-Object Name,DriverName,PortName | ConvertTo-Json -Compress"

powershell.exe -NoProfile -NonInteractive -Command `
  "Get-PrinterPort -ComputerName 'elgjunprt' -ErrorAction Stop | Select-Object Name,PrinterHostAddress | ConvertTo-Json -Compress"

# Camada 2 — pela API (token de admin necessário)
curl.exe -s -X POST http://127.0.0.1:8000/api/servers/discover -H "Authorization: Bearer $TOKEN"
```

**6. Resultado esperado** — JSON com N filas reais; `count` > 0;
`source = "print_server_real"`; `unique_ips` coerente; `ip_resolution`
majoritariamente `"resolved"`.

**7. Como validar** — Compare `count` da API com
`(Get-Printer -ComputerName elgjunprt).Count`. Devem ser **idênticos**.
Divergência = filtro ou truncamento não previsto.

**8. Evidências** — JSON bruto dos dois comandos; corpo da resposta da API;
`backend/logs/printercontrol.log` na linha
`Descoberta em modo real | server=...`; tempo de resposta.

**9. Possíveis erros**

| Sintoma | Causa provável |
|---|---|
| `PrintServerError: PowerShell falhou: ...Access is denied` | D-01, permissão |
| `PowerShell nao respondeu em 30s` | RPC filtrado; o timeout mascara "porta fechada" como "lento" |
| `Saida do PowerShell nao e JSON valido` | Banner de profile, aviso de módulo, ou GPO de transcrição poluindo o stdout — **`-NoProfile` reduz mas não elimina** |
| `powershell.exe nao encontrado` | `PATH` reduzido de uma sessão de serviço |
| Lista vazia sem erro | Conta enxerga o servidor mas nenhuma fila (permissão por fila) |

**10. Impacto** — Sem isto não há sincronização, não há frota, não há SNMP,
não há alertas, não há relatório. É a raiz da árvore.

**11. Dentro/fora** — **Somente dentro** no modo `real`. Fora, só o modo
`mock` (`print_server.py:_mock_discover`), que produz 7 filas fictícias.

**12. Prioridade** — **P0.**

---

### D-03 · Resolução de nome do Print Server (DNS interno / NetBIOS / FQDN)

**1. Funcionalidade** — `validar_host()` aceita hostname NetBIOS curto, FQDN
ou IPv4. Qual das três formas está configurada muda o comportamento de
autenticação.

**2. Onde existe**
- `backend/app/services/print_server.py:57-59` — regex RFC 1123.
- `backend/app/services/print_server.py:62-100` — `validar_host`.
- `backend/app/routes/servers.py` — a mesma validação no cadastro
  (`PrintServerCreate._host_valido`), para o 422 aparecer no formulário.
- Default: `config.py` → `print_server_host = "elgjunprt"` (NetBIOS curto).

**3. Por que o domínio é relevante** — Nome curto depende do **sufixo DNS de
busca** entregue por GPO/DHCP; some numa VPN mal configurada. E há um efeito
de segurança real: **um IP literal força NTLM** (não há SPN para IP),
enquanto FQDN permite Kerberos. Se o domínio tiver *NTLM restrito por
política*, discovery por IP falha e por FQDN funciona — com a mesma conta.

**4. Pré-requisitos** — Nenhum além da máquina no domínio.

**5. Procedimento**
```powershell
Resolve-DnsName elgjunprt
Resolve-DnsName elgjunprt.<sufixo-do-dominio>
nslookup elgjunprt
Get-DnsClientGlobalSetting          # sufixo de busca
Get-DnsClientServerAddress          # servidores DNS (devem ser os DCs)
Test-NetConnection elgjunprt -Port 135

# Qual protocolo foi realmente usado, depois de rodar D-02:
klist | Select-String "cifs/|host/|HOST/"
```

**6. Resultado esperado** — As três formas resolvem; DNS aponta para DCs
internos; porta 135 `TcpTestSucceeded : True`; `klist` mostra um ticket
`host/elgjunprt...` após o discovery (prova de Kerberos).

**7. Como validar** — Rode D-02 três vezes: com nome curto, com FQDN, com IP.
Registre qual funciona. Se só o IP falhar → NTLM bloqueado. Se só o curto
falhar → sufixo de busca.

**8. Evidências** — Saída de cada comando; `klist` antes e depois;
`klist purge` + repetição (🔒 requer aprovação: derruba tickets da sessão).

**9. Possíveis erros** — `DNS name does not exist`; resolve para IP antigo
(registro obsoleto); `KDC_ERR_S_PRINCIPAL_UNKNOWN` (SPN ausente);
resolução para IPv6 sem rota.

**10. Impacto** — Discovery falha de forma intermitente e difícil de
reproduzir — o pior modo de falha possível.

**11. Dentro/fora** — **Somente dentro.**

**12. Prioridade** — **P0.**

---

### D-04 · Sincronização — o teste de maior risco de dano

**1. Funcionalidade** — `sync_printers()` cria/atualiza filas descobertas e
**marca `active=False` toda impressora do servidor que não apareceu na
descoberta**.

**2. Onde existe**
- `backend/app/services/printer_sync.py:44-132`.
- `printer_sync.py:120-126` — o laço de desativação.
- `POST /api/servers/sync` e `/api/servers/{id}/sync` — `routes/servers.py`.
- Guardas: `services/environment_guard.py:27-46`;
  `config.py::_validate_production_mock` (recusa boot com `mock` em produção);
  `routes/servers.py::sync_server` (recusa sync de servidor gravado como
  `mock`).

**3. Por que o domínio é relevante** — Uma falha **parcial** de RPC (a conta
enxerga 20 de 79 filas por permissão por fila) não gera exceção: gera uma
descoberta pequena e válida. O sync então **desativa 59 impressoras reais**.
Esse cenário só é reproduzível dentro do domínio, porque só lá existe
permissão granular por fila.

**4. Pré-requisitos** — D-02 **verde e completo** (contagem conferida).
**Backup do banco tomado imediatamente antes.**

**5. Procedimento** — 🔒 **REQUER APROVAÇÃO — escreve no banco.**
```powershell
# 1. Backup ANTES (não é opcional)
Copy-Item backend\printer_control.db "backend\backups\pre-sync-$(Get-Date -f yyyyMMdd-HHmmss).db"

# 2. Contagem antes
sqlite3 backend\printer_control.db "SELECT server, active, COUNT(*) FROM printers GROUP BY server, active;"

# 3. Discovery (não escreve) e conferência da contagem — PARE aqui se divergir
curl.exe -s -X POST http://127.0.0.1:8000/api/servers/discover -H "Authorization: Bearer $TOKEN"

# 4. Só então o sync
curl.exe -s -X POST http://127.0.0.1:8000/api/servers/sync -H "Authorization: Bearer $TOKEN"

# 5. Contagem depois
sqlite3 backend\printer_control.db "SELECT server, active, COUNT(*) FROM printers GROUP BY server, active;"
```

**6. Resultado esperado** — Num ambiente já sincronizado: `created=0`,
`deactivated=0`, `updated=N`. **`deactivated > 0` numa máquina de produção é
um sinal de alarme**, não um sucesso.

**7. Como validar** — `discovered` do sync == `count` do discover ==
`(Get-Printer -ComputerName ...).Count`. As três precisam bater.

**8. Evidências** — As duas contagens SQL; corpo do `SyncResponse`; caminho do
backup; log `printercontrol.log`.

**9. Possíveis erros** — 502 (`PrintServerError`, nada é escrito — o
`session.add` só ocorre após a descoberta); 409 se o servidor está com
`mode='mock'` em produção; 429 (limite de 10 ações de rede por 60 s por
usuário — `config.py::network_action_max_attempts`).

**10. Impacto** — Desativação em massa da frota. Recuperável (nada é
apagado; `active=False` preserva leituras e alertas), mas exige o backup.

**11. Dentro/fora** — **Somente dentro** para valer alguma coisa.

**12. Prioridade** — **P0**, e **sempre depois** de D-02 conferido.

---

### D-05 · Exclusão de Print Server — cascata destrutiva

**1. Funcionalidade** — `DELETE /api/servers/{id}` apaga **em definitivo** o
servidor, suas impressoras, e todas as leituras, contadores mensais, alertas,
histórico de toner e notificações associadas.

**2. Onde existe** — `backend/app/routes/servers.py::delete_server`. Exige
`confirm_host` idêntico ao host no corpo do pedido.

**3. Por que o domínio é relevante** — Só faz sentido numa instalação com
mais de um print server, o que só existe no ambiente corporativo. E o risco
é máximo justamente lá, onde os dados são reais.

**4. Pré-requisitos** — Um servidor **de teste, descartável**, cadastrado só
para isso.

**5. Procedimento** — ⚠️ **DESTRUTIVO — NUNCA contra um servidor real.**
Cadastre via `POST /api/servers` um host fictício válido, confirme que ele
tem 0 impressoras, e só então apague. Documente; não execute contra produção.

**6. Resultado esperado** — 204; 400 se `confirm_host` não bate.

**7. Como validar** — Contagem em `printers`, `alerts`, `printer_readings`
antes e depois, no servidor de teste.

**8. Evidências** — Registro em `audit_logs` (`action='server.delete'`,
`before` com `printer_count`).

**9. Possíveis erros** — 404; 400 de confirmação.

**10. Impacto** — Perda irreversível de histórico. Só o backup salva.

**11. Dentro/fora** — Pode ser testado fora, e **deve** ser: teste a mecânica
fora, não dentro.

**12. Prioridade** — **P3** dentro do domínio (documentar, não executar).

---

### D-06 · Ping ICMP à frota

**1. Funcionalidade** — Antes de qualquer SNMP, `_ping()` decide
online/offline.

**2. Onde existe** — `backend/app/services/snmp.py:282-303`. Em Windows:
`ping -n 1 -w 400 <ip>` com `CREATE_NO_WINDOW`. Chamado em
`snmp.py:218` e em `printer_fleet.py:126`.

**3. Por que o domínio é relevante** — Timeout de **400 ms** é apertado para
rede corporativa com VLANs, roteamento entre unidades e QoS. Firewall
corporativo ou GPO de Windows Firewall que bloqueie ICMP de saída marca a
**frota inteira como offline** — e o painel apresenta isso como falha das
impressoras, não da rede.

**4. Pré-requisitos** — Lista de IPs reais (vem de D-02).

**5. Procedimento**
```powershell
# Amostra de 10 IPs da frota, com o MESMO timeout do código
$ips | Select-Object -First 10 | ForEach-Object {
  ping -n 1 -w 400 $_ | Out-Null
  [pscustomobject]@{ IP=$_; OK=($LASTEXITCODE -eq 0) }
}
# Comparação com timeout folgado — separa "lento" de "bloqueado"
$ips | Select-Object -First 10 | ForEach-Object { Test-Connection $_ -Count 1 -TimeoutSeconds 3 -Quiet }
```

**6. Resultado esperado** — Impressoras ligadas respondem dentro de 400 ms.

**7. Como validar** — Se responde com 3 s e **não** com 400 ms, o problema é
latência e o valor precisa ser revisto (hoje é constante em
`SNMPClient.__init__`, `ping_timeout_ms=400`, **não configurável por `.env`**
— registrado como achado A-02).

**8. Evidências** — Tabela IP × resultado nos dois timeouts; `tracert` de uma
impressora de unidade remota; regras de firewall de saída para ICMP.

**9. Possíveis erros** — ICMP bloqueado por GPO; impressora em VLAN sem rota;
EDR interceptando `ping.exe` (processo filho de `python.exe` é um padrão que
alguns EDRs sinalizam).

**10. Impacto** — Frota inteira reportada offline; motor de alertas dispara
em massa; webhook inunda o canal do Teams.

**11. Dentro/fora** — **Somente dentro** (fora não há frota real).

**12. Prioridade** — **P1.**

---

### D-07 · SNMP UDP/161 e community string

**1. Funcionalidade** — GetBulk (SNMPv2c) com fallback para GET sequencial,
sobre os OIDs de `Printer-MIB` (RFC 3805).

**2. Onde existe**
- `backend/app/services/snmp.py:227-231` — socket UDP.
- `snmp.py` (constantes de `SNMPClient`) — OIDs `1.3.6.1.2.1.43.*` e
  `sysUpTime`.
- `snmp.py:504-525` — `_exchange` com `self.retries` (Fase 17).
- `config.py` — `SNMP_COMMUNITY` (default **`"public"`**),
  `SNMP_TIMEOUT=1.5`, `SNMP_RETRIES=1`.

**3. Por que o domínio é relevante** — UDP/161 costuma ser filtrado entre
VLANs corporativas. E `public` é frequentemente desabilitado pela norma de
segurança da empresa em favor de uma community própria — que precisa entrar
no `.env`, e hoje **não há teste automatizado que valide a community contra a
frota real**.

**4. Pré-requisitos** — D-06 verde.

**5. Procedimento**
```powershell
Test-NetConnection <ip-impressora> -Port 161 -InformationLevel Detailed   # UDP: indicativo, não conclusivo
# Teste conclusivo — pelo próprio código, que é a implementação real:
cd backend
.\venv\Scripts\python.exe -c "from app.services.snmp import SNMPClient; print(SNMPClient(community='public', timeout=1.5).collect('<ip>'))"
```

**6. Resultado esperado** — `reachable=True`, `snmp_responded=True`,
`page_count` inteiro plausível, `toners` com pelo menos K.

**7. Como validar** — `page_count` deve **crescer monotonicamente** entre duas
coletas separadas por horas. Compare o nível de toner com o painel físico da
impressora — é a única validação verdadeiramente independente.

**8. Evidências** — `SNMPResult` completo; `status_reason` (o campo é o
diagnóstico: `ping_ok_snmp_not_responding`, `snmp_without_page_count`,
`snmp_partial_data`, `snmp_data_available`); foto do painel da impressora.

**9. Possíveis erros** — `ping_ok_snmp_not_responding` (SNMP desligado na
impressora, community errada, ou UDP/161 filtrado — os três dão o mesmo
sintoma); `snmp_timeout`; `snmp_socket_error`.

**10. Impacto** — Toner e contador ficam vazios; relatório mensal zera;
alertas de suprimento nunca disparam.

**11. Dentro/fora** — **Somente dentro.**

**12. Prioridade** — **P1.**

---

### D-08 · Coleta paralela da frota — e o que o EDR vê

**1. Funcionalidade** — `collect_fleet()` agrupa por IP e dispara até
`COLLECTION_MAX_WORKERS` (default 4) consultas simultâneas.

**2. Onde existe** — `backend/app/services/printer_fleet.py:147-210`;
`ThreadPoolExecutor` na linha 184; agrupamento por IP em `_group_by_ip:75`;
`_group_plan:82` decide quem faz SNMP completo quando há filas compartilhando
IP.

**3. Por que o domínio é relevante** — Um processo Python varrendo dezenas de
IPs com ICMP + UDP/161 em paralelo é, para um IDS/EDR corporativo, **o
padrão de um scanner de rede**. Falso positivo aqui é plausível e precisa ser
verificado com a equipe de segurança **antes** de subir o scheduler.

**4. Pré-requisitos** — D-06 e D-07 verdes; **aviso prévio à equipe de
segurança** (pré-requisito organizacional, não técnico).

**5. Procedimento**
```powershell
curl.exe -s -X POST http://127.0.0.1:8000/api/collect/fleet -H "Authorization: Bearer $TOKEN_ADMIN"
```
Em paralelo, colete o log do EDR / eventos de firewall da janela de tempo.

**6. Resultado esperado** — `collected` ≈ total de IPs; `failed` baixo;
ciclo dentro do intervalo configurado (`COLLECTION_INTERVAL_MINUTES=5`).

**7. Como validar** — `by_status` do `FleetCollectionResult` deve refletir a
realidade física da unidade. E: **duração do ciclo < intervalo**. Se o ciclo
demora mais que o intervalo, o APScheduler descarta o próximo disparo
(`max_instances=1, coalesce=True` em `scheduler.py`) — a coleta silencia sem
erro.

**8. Evidências** — `FleetCollectionResult` completo; `result.errors[:10]` do
log; carimbo de início/fim; eventos do EDR na janela.

**9. Possíveis erros** — Bloqueio/quarentena pelo EDR; exaustão de portas
efêmeras com muitos workers; `max_workers` alto saturando o link da unidade.

**10. Impacto** — Coleta bloqueada por segurança, ou incidente aberto contra
a máquina. É o teste com maior chance de gerar atrito organizacional.

**11. Dentro/fora** — **Somente dentro.**

**12. Prioridade** — **P1** — e **avise a segurança antes**.

---

### D-09 · Point & Print via UNC (`Main.ps1`) — GPO PrintNightmare

**1. Funcionalidade** — Botão "Mapear via Rede": conecta o usuário a uma fila
compartilhada do print server, abrindo o assistente nativo do Windows.

**2. Onde existe** — `Main.ps1:1753-1755`:
```powershell
$uncPath = "\\$servidorPrint\$nomeImpressora"
Start-Process "rundll32.exe" -ArgumentList "printui.dll,PrintUIEntry /in /n `"$uncPath`""
```
Condição em `Main.ps1:1621` — só aparece quando o IP casa com
`FaixaRedeLocal` (`"10."`, `Main.ps1:8`) e não é etiquetadora.

**3. Por que o domínio é relevante** — Este é **o** ponto mais afetado por
política de domínio no projeto inteiro. As mitigações de PrintNightmare
(`RestrictDriverInstallationToAdministrators=1`,
`Point and Print Restrictions`, `PackagePointAndPrintOnly`,
`RestrictedServerList`) bloqueiam exatamente esta operação para usuário não
administrador. É o comportamento **correto e desejado** do domínio — e o
recurso do sistema simplesmente não funciona sob ele.

**4. Pré-requisitos** — `Main.ps1` executável (WPF/.NET, PowerShell 5.1
Desktop — **não roda em PowerShell 7 Core**); usuário de domínio comum
(não administrador) para o caso realista.

**5. Procedimento**
```powershell
# Ler as políticas em vigor (SOMENTE LEITURA)
Get-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows NT\Printers\PointAndPrint" -EA SilentlyContinue
Get-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows NT\Printers" -EA SilentlyContinue |
  Select-Object RestrictDriverInstallationToAdministrators, RegisterSpoolerRemoteRpcEndPoint
gpresult /h "$env:TEMP\gpo.html"   # revisar a seção de Impressoras

# Só então, o caminho real
Test-Path "\\elgjunprt\<NomeDaFila>"
rundll32.exe printui.dll,PrintUIEntry /in /n "\\elgjunprt\<NomeDaFila>"
```

**6. Resultado esperado** — Com política permissiva: fila instalada, aparece
em `Get-Printer`. Com PrintNightmare mitigado e usuário comum: prompt de
elevação ou erro `0x00000bcb` / `0x0000011b`.

**7. Como validar** — `Get-Printer | Where Name -like "*<fila>*"` e uma
página de teste impressa de fato.

**8. Evidências** — `gpo.html`; valores do registro; código de erro exato;
Event Log `Microsoft-Windows-PrintService/Admin` e `/Operational`.

**9. Possíveis erros** — `0x0000011b` (mitigação de PrintNightmare),
`0x00000bcb` (fila inexistente), UAC negado, Spooler parado por GPO
(comum em máquinas endurecidas — e aí `Main.ps1:1712` mostra
"Serviço de Spooler do Windows indisponível").

**10. Impacto** — Autoatendimento de mapeamento indisponível; volta para
chamado no service desk.

**11. Dentro/fora** — **Somente dentro.** Sem print server e sem GPO o
caminho não existe.

**12. Prioridade** — **P1** se `Main.ps1` ainda estiver em uso;
**P3** se estiver oficialmente aposentado — decisão que este documento não
toma, mas **recomenda registrar** (achado A-08).

---

### D-10 · Instalação de driver a partir de `..\Drivers` e atalhos `.lnk`

**1. Funcionalidade** — Procura `.inf`/`.exe` numa pasta `Drivers` irmã do
script, **seguindo atalhos `.lnk` para os alvos reais**, e injeta/executa.

**2. Onde existe** — `Main.ps1:1613-1616` (pasta), `1638-1646`
(`Resolve-WindowsShortcut` via COM `WScript.Shell`), `1653-1657` (varredura
recursiva), `1790+` (execução com checagem de `$script:IsElevated`).
`DriverMap` em `Main.ps1:12-15` mapeia nome de fila → caminho de driver.

**3. Por que o domínio é relevante** — Os `.lnk` quase certamente apontam
para **shares SMB** (`\\servidor\drivers\...`). Isso traz para o teste: SMB
signing, SMB1 desabilitado, autenticação na share, Mark-of-the-Web/AppLocker
bloqueando `.exe` vindo da rede, e UAC.

**4. Pré-requisitos** — Pasta `Drivers` populada; usuário comum **e** admin
para comparar.

**5. Procedimento** — 🔒 **REQUER APROVAÇÃO — instala driver na máquina.**
```powershell
# Leitura, sem instalar
Get-ChildItem "..\Drivers" -Filter *.lnk | ForEach-Object {
  $t = (New-Object -ComObject WScript.Shell).CreateShortcut($_.FullName).TargetPath
  [pscustomobject]@{ Atalho=$_.Name; Alvo=$t; Alcancavel=(Test-Path $t) }
}
Get-SmbClientConfiguration | Select-Object RequireSecuritySignature, EnableSecuritySignature
Get-AppLockerPolicy -Effective -Xml | Out-File "$env:TEMP\applocker.xml"
```

**6. Resultado esperado** — Todos os alvos de `.lnk` alcançáveis;
`Test-Path` verdadeiro para os caminhos do `DriverMap`.

**7. Como validar** — `Get-PrinterDriver` antes e depois; a fila imprime.

**8. Evidências** — Tabela atalho→alvo→alcançável; `applocker.xml`; código de
saída do instalador (`Main.ps1` verifica `$proc.ExitCode`).

**9. Possíveis erros** — Alvo inalcançável (o código cai no fallback e avisa,
`Main.ps1:1633`); `.exe` bloqueado por AppLocker/SRP; UAC negado —
`Main.ps1` trata isso com mensagem explícita ("Requer Administrador"), o que é
o comportamento correto; SMB1 desativado contra share legado.

**10. Impacto** — Instalação automática de driver indisponível; usuário cai no
"selecionar manualmente".

**11. Dentro/fora** — **Somente dentro** (shares e AppLocker são do domínio).

**12. Prioridade** — **P2.**

---

### D-11 · Serviço como Tarefa Agendada — instalação, boot e reinício

**1. Funcionalidade** — Backend como tarefa `PrinterControl-Backend`, gatilho
`AtStartup`, `RestartCount 999`, `ExecutionTimeLimit 0`.

**2. Onde existe** — `scripts/Servico-PrinterControl.ps1:87-140`.

**3. Por que o domínio é relevante** — Requer administrador local (que num
domínio endurecido o usuário comum **não** tem); GPO pode restringir criação
de tarefas; `SeBatchLogonRight` precisa estar concedido à conta de serviço;
`Deny log on as a batch job` numa GPO derruba a instalação com conta de
domínio. Política de expiração de senha da conta de serviço quebra a tarefa
semanas depois, silenciosamente.

**4. Pré-requisitos** — Sessão elevada; `backend\venv\Scripts\python.exe` e
`backend\.env` presentes (o script checa em `Confirmar-PreRequisitos`).

**5. Procedimento** — 🔒 **REQUER APROVAÇÃO — cria tarefa agendada.**
```powershell
pwsh .\scripts\Servico-PrinterControl.ps1 -Acao status      # leitura, seguro
# Instalação (aprovada):
pwsh .\scripts\Servico-PrinterControl.ps1 -Acao instalar -Conta "DOMINIO\svc_printercontrol"
pwsh .\scripts\Servico-PrinterControl.ps1 -Acao iniciar
# Teste de boot real: reiniciar a máquina (janela combinada) e checar status
```

**6. Resultado esperado** — `-Acao status` mostra `estado=Running` e
`/health` respondendo com `status=ok`. Após reboot, sobe sozinho **sem
ninguém logado**.

**7. Como validar** — O script já faz a validação certa: consulta `/health`
em vez de confiar no estado da tarefa (`Servico-PrinterControl.ps1`, função
`Status`). Um processo de pé e travado aparece como `Running` mas com
`/health` mudo. **Confie no `/health`.**

**8. Evidências** — Saída de `-Acao status`; `Get-ScheduledTaskInfo`;
`uptime_seconds` de `/health` crescendo entre duas consultas espaçadas (um
uptime que nunca passa de poucos minutos = reinício em laço, exatamente o que
o comentário em `main.py` prevê); Event Log `TaskScheduler/Operational`.

**9. Possíveis erros** — `Access is denied` na `Register-ScheduledTask`;
`Logon failure: the user has not been granted the requested logon type`
(falta `SeBatchLogonRight`); tarefa criada mas nunca dispara (GPO);
`0xC000006A` senha errada.

**10. Impacto** — Sistema não sobe no boot; qualquer reinício da máquina
derruba o monitoramento até alguém perceber.

**11. Dentro/fora** — Mecânica testável fora; **comportamento com conta de
domínio, `SeBatchLogonRight` e GPO, somente dentro**.

**12. Prioridade** — **P0.**

---

### D-12 · Backup do banco em caminho UNC

**1. Funcionalidade** — Tarefa `PrinterControl-Backup` a cada N horas,
opcionalmente para um destino de rede.

**2. Onde existe** — `scripts/Servico-PrinterControl.ps1:63-68` (parâmetro
`-BackupDir`, com o aviso de ponto único de falha), função `Instalar-Backup`;
`backend/backup_db.py`.

**3. Por que o domínio é relevante** — O destino sugerido é literalmente uma
UNC (`\\servidor\backups\printercontrol`). A tarefa roda como **SYSTEM**
(`New-ScheduledTaskPrincipal -UserId "SYSTEM"` em `Instalar-Backup`),
portanto acessa a share como `DOMÍNIO\MÁQUINA$` — **exatamente a mesma
armadilha do D-01, agora no backup**. E é a mais perigosa das duas, porque a
falha é silenciosa: você só descobre no dia em que precisa restaurar.

**4. Pré-requisitos** — Share existente; ACL a definir (**documentar, não
alterar**).

**5. Procedimento**
```powershell
Test-Path "\\servidor\backups\printercontrol"                      # como usuário interativo
# Como SYSTEM (leitura) — 🔒 requer aprovação:
#   psexec -s -accepteula powershell -c "Test-Path '\\servidor\backups\printercontrol'"
(Get-Acl "\\servidor\backups\printercontrol").Access | Format-Table IdentityReference, FileSystemRights
cd backend; .\venv\Scripts\python.exe backup_db.py --dir "\\servidor\backups\printercontrol" --keep 14
```

**6. Resultado esperado** — Arquivo `.db` novo aparece na share, com tamanho
plausível e abrível por `sqlite3`.

**7. Como validar** — Restaure o backup para um caminho temporário e rode
`PRAGMA integrity_check;` — **é a única validação que prova que o backup
serve**. Nunca aceite "o arquivo existe" como validação de backup.

**8. Evidências** — Listagem da share com timestamps; `integrity_check`;
`Get-ScheduledTaskInfo -TaskName PrinterControl-Backup`.

**9. Possíveis erros** — `Access is denied` para `MÁQUINA$` (o modo de falha
esperado); share indisponível no horário; `-BackupDir` vazio deixando backup
no mesmo disco do banco (o script avisa em amarelo, mas prossegue).

**10. Impacto** — Sem backup utilizável. Combinado com D-04 (sync que
desativa em massa), é o cenário de perda de histórico.

**11. Dentro/fora** — **UNC somente dentro.** Backup local testável fora.

**12. Prioridade** — **P0** (é a rede de segurança de D-04; teste antes dele).

---

### D-13 · Webhook Power Automate através do proxy corporativo

**1. Funcionalidade** — Adaptive Card ao Teams quando um alerta de toner
nasce ou escala para crítico.

**2. Onde existe** — `backend/app/services/webhook_notifier.py:105-156`
(`httpx.post`, timeout 5 s, nunca levanta exceção);
`config.py` (`WEBHOOK_URL` vazio = desabilitado).

**3. Por que o domínio é relevante** — Três coisas do ambiente corporativo
incidem: (a) **proxy** — `httpx` respeita `HTTP_PROXY`/`HTTPS_PROXY` do
ambiente, e a tarefa agendada rodando como SYSTEM **não herda as variáveis do
usuário nem as configurações de proxy do perfil**; (b) **inspeção TLS** — o
certificado reemitido pelo appliance não está no store que o `certifi` do
Python usa, causando `SSLCertVerificationError`; (c) **allowlist de URL** —
`*.api.powerplatform.com` pode não estar liberado.

**4. Pré-requisitos** — `WEBHOOK_URL` no `.env`; canal do Teams de **teste**.

**5. Procedimento**
```powershell
netsh winhttp show proxy                    # proxy de nível de máquina (o que SYSTEM usa)
Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" |
  Select-Object ProxyEnable, ProxyServer, AutoConfigURL
cd backend
.\venv\Scripts\python.exe -c "import httpx,os; print({k:v for k,v in os.environ.items() if 'PROXY' in k.upper()}); print(httpx.get('https://www.microsoft.com', timeout=10).status_code)"
# Disparo real, para canal de TESTE — 🔒 requer aprovação (envia mensagem):
.\venv\Scripts\python.exe -c "from app.services.webhook_notifier import send_toner_alert_webhook as s; print(s('TESTE_DOMINIO','Modelo Teste','K','8%',manual=True))"
```

**6. Resultado esperado** — `True` e o card aparecendo no canal.

**7. Como validar** — O card **visível no Teams**. `True` sozinho prova
apenas HTTP < 400; o Power Automate pode aceitar e descartar.

**8. Evidências** — Captura do card; linha
`Webhook enviado com sucesso | host=...` no log (**a URL nunca é logada — só o
host, por `_safe_host()`**, o que é correto e deve ser confirmado na
evidência); `netsh winhttp show proxy`.

**9. Possíveis erros** — `SSLCertVerificationError` (inspeção TLS — a
correção é apontar `SSL_CERT_FILE`/`REQUESTS_CA_BUNDLE` para o bundle
corporativo; **documentar, não aplicar agora**); `ConnectTimeout` (proxy não
configurado para SYSTEM); 403 do gateway de URL.

**10. Impacto** — Alertas críticos de toner nunca chegam ao Teams. A coleta
continua normal — **a falha é totalmente silenciosa para o usuário**, o
módulo só loga em `WARNING` e devolve `False`.

**11. Dentro/fora** — Proxy e inspeção TLS: **somente dentro**. O disparo em
si é testável fora.

**12. Prioridade** — **P2.**

---

### D-14 · ⚠️ Segredo real versionado em `Main.ps1`

**1. Funcionalidade** — Não é um teste funcional; é um **achado de segurança
encontrado durante esta análise** que precisa entrar na bateria como
verificação.

**2. Onde existe** — `Main.ps1:11` contém a **URL completa do webhook Power
Automate, com a assinatura `sig=` embutida**, em texto claro, commitada no
repositório. O backend fez o certo (`WEBHOOK_URL` só via `.env`, e o
comentário em `config.py` diz explicitamente "nunca commitar a URL real"); o
script legado não.

**3. Por que o domínio é relevante** — Quem tem acesso de leitura ao repo ou à
pasta do projeto na máquina do domínio pode postar no canal do Teams da
empresa. A superfície é interna, o que é exatamente o cenário corporativo.

**4. Pré-requisitos** — Nenhum.

**5. Procedimento** — Confirmar a exposição e o alcance:
```powershell
Select-String -Path Main.ps1 -Pattern "sig=" | Select-Object LineNumber
git log --oneline -- Main.ps1 | Measure-Object       # há quanto tempo está no histórico
(Get-Acl .).Access | Format-Table IdentityReference, FileSystemRights
```

**6. Resultado esperado** — Confirmação de que o segredo está presente e de
quem consegue lê-lo.

**7. Como validar** — Presença da string; ACL da pasta; **se o repositório
`devribero/PrinterControl` for público no GitHub, o alcance é externo, não
interno — e a severidade sobe muito.** Verifique isso explicitamente.

**8. Evidências** — Número da linha (não copie o segredo para o relatório);
saída do `git log`; ACL; status público/privado do repo.

**9. Possíveis erros** — Nenhum; é uma verificação de leitura.

**10. Impacto** — Qualquer leitor pode enviar alertas falsos ao canal
corporativo. Rotacionar a URL do fluxo é a mitigação — **decisão do time,
fora do escopo deste documento**.

**11. Dentro/fora** — Ambos.

**12. Prioridade** — **P0 como achado** (reporte imediatamente); P3 como
"teste".

---

### D-15 · RBAC da aplicação — e o que ele *não* é

**1. Funcionalidade** — Três papéis, hierárquicos, checados centralmente.

**2. Onde existe** — `backend/app/dependencies.py:113-176`
(`require_roles`, `require_viewer/operator/admin`);
`backend/app/models/user.py` (`Role`, `has_role`);
`src/lib/permissions.ts` (espelho no frontend, **cosmético**).

**3. Por que o domínio é relevante** — **Não é.** E documentar isso é o
resultado do teste. Os papéis não vêm de grupos do AD, não há mapeamento
`Domain Admins → admin`, e um administrador do domínio **não tem nenhum
privilégio no PrinterControl** a menos que exista uma conta `admin` no SQLite
para ele. Reciprocamente, um `admin` do PrinterControl pode ser um usuário
comum do domínio.

**4. Pré-requisitos** — Três contas de teste, uma por papel.

**5. Procedimento** — Para cada papel, tentar as rotas de outro:
```powershell
# viewer tentando sincronizar -> deve dar 403
curl.exe -s -o NUL -w "%{http_code}`n" -X POST http://127.0.0.1:8000/api/servers/sync -H "Authorization: Bearer $TOKEN_VIEWER"
# operator tentando criar usuário -> 403
curl.exe -s -o NUL -w "%{http_code}`n" -X POST http://127.0.0.1:8000/api/users -H "Authorization: Bearer $TOKEN_OPERATOR" -H "Content-Type: application/json" -d "{}"
# sem token -> 401
curl.exe -s -o NUL -w "%{http_code}`n" http://127.0.0.1:8000/api/printers
```

**6. Resultado esperado** — 403 / 403 / 401. Confirme também que o **admin do
domínio logado na máquina não ganha nada** por isso.

**7. Como validar** — Matriz papel × endpoint × código HTTP, preenchida por
teste real, não por leitura do código.

**8. Evidências** — A matriz; registros em `audit_logs`.

**9. Possíveis erros** — Frontend escondendo o botão mas backend permitindo
(o inverso do desejado). Teste **sempre pela API**, nunca só pela tela.

**10. Impacto** — Escalada de privilégio dentro do painel.

**11. Dentro/fora** — **Idêntico dentro e fora.** Faça este fora do domínio
para economizar a janela de teste no ambiente corporativo.

**12. Prioridade** — **P1**, mas **fora** do domínio.

---

### D-16 · Sessão, token e o perfil de usuário do domínio

**1. Funcionalidade** — JWT guardado em `localStorage` sob a chave
`elgin_auth_token`; expira em 24 h; invalidado por `token_version`.

**2. Onde existe** — `src/lib/api.ts:9` (`TOKEN_KEY`);
`backend/app/dependencies.py:66-104` (releitura do usuário a cada requisição
+ `token_version`); `config.py` (`ACCESS_TOKEN_EXPIRE_HOURS=24`).

**3. Por que o domínio é relevante** — `localStorage` vive no perfil do
navegador. Em máquina de domínio isso encontra: **perfil móvel/roaming**,
**Redirecionamento de Pastas**, GPO "Limpar dados de navegação ao sair",
perfis obrigatórios, e **múltiplos usuários de domínio na mesma máquina**
(cada um com seu `localStorage` — a sessão do PrinterControl é por perfil do
Windows, o que é o comportamento correto mas precisa ser confirmado).

**4. Pré-requisitos** — Dois usuários de domínio distintos na mesma máquina.

**5. Procedimento** — Logar com A, encerrar a sessão do Windows, entrar como
B, abrir o painel. Depois voltar para A.

**6. Resultado esperado** — B **não** herda a sessão de A. A mantém a sua (a
menos que GPO limpe o storage no logoff — nesse caso, documente).

**7. Como validar** — DevTools → Application → Local Storage → presença ou
ausência de `elgin_auth_token`.

**8. Evidências** — Captura do DevTools para cada perfil; GPO de navegador
(`gpresult /h`, seção Chrome/Edge).

**9. Possíveis erros** — Token sobrevivendo entre perfis (falha grave de
isolamento); token apagado a cada logon (usuário reclama de "cai toda hora").

**10. Impacto** — Ou vazamento de sessão entre usuários, ou fricção diária.

**11. Dentro/fora** — Perfis móveis e GPO de navegador: **somente dentro**.

**12. Prioridade** — **P2.**

---

### D-17 · CORS, `allowedDevOrigins` e acesso pela rede

**1. Funcionalidade** — O painel só consegue falar com a API a partir de
origens explicitamente listadas.

**2. Onde existe** — `backend/app/main.py:88-95` (`CORSMiddleware`);
`config.py::_validate_production_cors` (recusa boot com `*`, com `localhost`
ou sem HTTPS em produção); `next.config.ts:4` —
`allowedDevOrigins: ["10.36.1.34"]`; `docs/DEV_NETWORK_ACCESS.md`.

**3. Por que o domínio é relevante** — `10.36.1.34` é um IP entregue por
**DHCP corporativo**. Ele muda. Quando muda, o Next.js volta a bloquear
`/_next/*` e a tela trava em "Restaurando sessão" — que é exatamente o
incidente documentado em `DEV_NETWORK_ACCESS.md` e que ainda tem um item
`[ ]` em aberto no roadmap daquele arquivo ("Confirmar no navegador após
reiniciar o servidor").

**4. Pré-requisitos** — `npm run dev` rodando.

**5. Procedimento**
```powershell
ipconfig /all | Select-String "IPv4|DHCP|Concessao|Lease|Sufixo"
# Acessar de outra máquina do domínio:  http://<ip-atual>:3000  (Ctrl+F5)
# Conferir no DevTools > Network que /_next/static/* e /_next/hmr não são bloqueados
```

**6. Resultado esperado** — Painel carrega; sem erro de origem no console.

**7. Como validar** — Ausência de mensagem `Blocked cross-origin request` e a
tela de login (ou o painel) renderizando — não "Restaurando sessão" eterno.

**8. Evidências** — `ipconfig /all`; console e aba Network do DevTools;
IP atual vs. o que está no `next.config.ts`.

**9. Possíveis erros** — IP mudou por DHCP; Windows Firewall bloqueando 3000
inbound; **isso é modo de desenvolvimento — em produção o caminho é outro**
(build estático + Cloudflare Tunnel).

**10. Impacto** — Painel inacessível pela rede em dev/homologação.

**11. Dentro/fora** — Testável fora com IP local; **o comportamento com DHCP
corporativo e firewall de domínio, somente dentro**.

**12. Prioridade** — **P2.**

---

### D-18 · Fail-fast de produção — o backend recusa subir mal configurado

**1. Funcionalidade** — Com `ENVIRONMENT=production`, o boot **falha** se:
`SECRET_KEY` for a de dev ou < 32 chars; `PRINT_SERVER_MODE != real`;
`ALLOW_MOCK_COLLECT=true`; `CORS_ORIGINS` vazio, `*`, com localhost ou sem
HTTPS.

**2. Onde existe** — `backend/app/config.py`: `_validate_production_mock`,
`_validate_production_secrets`, `_validate_production_cors`.

**3. Por que o domínio é relevante** — É na máquina do domínio que
`ENVIRONMENT=production` será usado pela primeira vez de verdade. Estas
validações nunca foram exercidas em produção real. Se uma delas falhar
indevidamente, **o sistema não sobe** — e o modo de falha precisa ser
conhecido *antes* da janela de implantação, não durante.

**4. Pré-requisitos** — Uma cópia do `.env` de produção pretendido (não
precisa estar em uso).

**5. Procedimento** — Sem tocar no `.env` real, valide em memória:
```powershell
cd backend
.\venv\Scripts\python.exe -c "import os; os.environ.update({'ENVIRONMENT':'production','SECRET_KEY':'x'*48,'PRINT_SERVER_MODE':'real','ALLOW_MOCK_COLLECT':'false','CORS_ORIGINS':'https://painel.exemplo.com'}); from app.config import Settings; s=Settings(_env_file=None); print('OK', s.environment, s.print_server_mode)"
```
Repita trocando **um** valor por vez para um inválido, confirmando que cada
guarda dispara com a mensagem certa.

**6. Resultado esperado** — Configuração boa: `OK production real`.
Cada variação ruim: `ValidationError` com a mensagem específica daquela guarda.

**7. Como validar** — Cinco execuções, cinco mensagens distintas. Se duas
variações produzem a mesma mensagem, uma guarda está inalcançável.

**8. Evidências** — As cinco saídas; o `.env` de produção pretendido com os
segredos **redigidos**.

**9. Possíveis erros** — `DATABASE_URL` do ambiente do usuário sobrepondo o
`.env` — isso **já aconteceu neste projeto** (outro projeto define
`DATABASE_URL=postgresql://...` no ambiente do Windows; `Iniciar-Sistema.bat`
limpa a variável por causa disso). Numa máquina de domínio, variáveis de
ambiente podem vir de **GPO ou script de logon** — risco específico do
ambiente corporativo, coberto em D-19.

**10. Impacto** — Backend não sobe na janela de implantação.

**11. Dentro/fora** — Testável fora; **a interação com variáveis de GPO,
somente dentro**.

**12. Prioridade** — **P1.**

---

### D-19 · Variáveis de ambiente corporativas sobrepondo o `.env`

**1. Funcionalidade** — Pydantic Settings dá **precedência ao ambiente do
processo** sobre o `.env`. Toda a configuração é vulnerável a isso.

**2. Onde existe** — `backend/app/config.py` (`class Config: env_file`);
`Iniciar-Sistema.bat` (o `set "DATABASE_URL="` e o comentário que o explica)
— a mitigação já existente, e a prova de que o problema é real neste projeto.

**3. Por que o domínio é relevante** — Em máquina de domínio, variáveis de
ambiente são frequentemente definidas por **GPO (Preferências de Política de
Grupo → Variáveis de Ambiente)** ou por **script de logon**. Uma variável
`DATABASE_URL`, `HTTP_PROXY`, `SECRET_KEY` ou `ENVIRONMENT` vinda daí muda o
comportamento do backend **sem que nada no repositório mude** — e a tarefa
agendada rodando como SYSTEM vê um conjunto de variáveis *diferente* do que o
usuário interativo vê.

**4. Pré-requisitos** — Nenhum.

**5. Procedimento**
```powershell
# Ambiente do USUÁRIO
Get-ChildItem Env: | Sort-Object Name
[Environment]::GetEnvironmentVariables('User')
# Ambiente da MÁQUINA (o que SYSTEM enxerga)
[Environment]::GetEnvironmentVariables('Machine')
# Variáveis vindas de GPO
gpresult /h "$env:TEMP\gpo.html"    # seção "Variáveis de ambiente"
# As que importam para este backend, especificamente:
Get-ChildItem Env: | Where-Object Name -match 'DATABASE_URL|SECRET_KEY|ENVIRONMENT|PRINT_SERVER|COLLECTION_|SNMP_|WEBHOOK_|CORS_|TRUST|PROXY|SSL_CERT|REQUESTS_CA'
```

**6. Resultado esperado** — Nenhuma variável com nome colidindo com uma
chave de `Settings`.

**7. Como validar** — Compare a lista Máquina vs. Usuário. Qualquer colisão é
um achado. Depois confirme o efeito real: com o backend rodando, `GET /health`
deve reportar `environment` e `print_server_mode` **iguais ao `.env`**.

**8. Evidências** — Os três dumps de ambiente; `gpo.html`; corpo de `/health`.

**9. Possíveis erros** — Exatamente o incidente já registrado no projeto:
`psycopg2 ModuleNotFoundError` porque `DATABASE_URL` apontava para PostgreSQL.

**10. Impacto** — Backend abrindo o banco errado, ou subindo em `production`
sem intenção, ou com CORS de outro ambiente. Difícil de diagnosticar porque
o repositório está correto.

**11. Dentro/fora** — GPO e script de logon: **somente dentro**.

**12. Prioridade** — **P0** — faça junto com D-11, antes de qualquer coisa.

---

### D-20 · Banco SQLite, disco e perfil

**1. Funcionalidade** — SQLite em caminho absoluto sob `backend/`.

**2. Onde existe** — `config.py` (`DEFAULT_DB_PATH`, `_absolute_sqlite_path`,
que normaliza relativo → absoluto para o cwd não decidir onde fica o banco);
`backend/app/database.py`.

**3. Por que o domínio é relevante** — Se o projeto for instalado no
**Desktop de um perfil móvel** ou numa pasta **redirecionada para share
SMB**, o SQLite passa a operar sobre a rede — e **SQLite sobre SMB tem
bloqueio de arquivo não confiável**, produzindo `database is locked` e
corrupção. O caminho atual é `C:\Users\ribero\Desktop\PrinterControl` —
**Desktop é a pasta mais comumente redirecionada por GPO em domínio**. Risco
concreto, não hipotético.

**4. Pré-requisitos** — Nenhum.

**5. Procedimento**
```powershell
# O Desktop está redirecionado?
[Environment]::GetFolderPath('Desktop')
Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders" |
  Select-Object Desktop, Personal
# O caminho do banco é local?
(Get-Item backend\printer_control.db).FullName
Get-Volume -FilePath (Get-Item backend\printer_control.db).FullName
sqlite3 backend\printer_control.db "PRAGMA integrity_check; PRAGMA journal_mode;"
```

**6. Resultado esperado** — Caminho em disco **local fixo**;
`integrity_check` = `ok`.

**7. Como validar** — `Get-Volume` deve mostrar `DriveType: Fixed`, não
`Network`. Se o Desktop estiver redirecionado, **mover a instalação é uma
recomendação a registrar**, não uma ação a executar agora.

**8. Evidências** — Caminho resolvido; `Get-Volume`; `integrity_check`;
`journal_mode`.

**9. Possíveis erros** — `database is locked`; `disk I/O error`;
corrupção silenciosa sob SMB.

**10. Impacto** — Perda de dados. É o pior impacto do documento inteiro.

**11. Dentro/fora** — Redirecionamento de pasta: **somente dentro**.

**12. Prioridade** — **P0.**

---

### D-21 · Firewall do Windows sob GPO

**1. Funcionalidade** — O backend escuta em `127.0.0.1:8000` (loopback,
não precisa de regra); o frontend dev escuta em `:3000` (**precisa**, para
acesso pela rede); saídas: ICMP, UDP/161, TCP/135 + RPC dinâmico, HTTPS.

**2. Onde existe** — `main.py` (`HOST = "127.0.0.1"`, deliberado, com o
comentário que explica por quê); `Servico-PrinterControl.ps1` (mesma decisão,
comentada); `docs/superpowers/specs/2026-09-01-vm-windows-migration-design.md`
(seção "Firewall do Windows Server").

**3. Por que o domínio é relevante** — Em domínio o firewall é gerido por
GPO e o perfil ativo é **Domain**. Regras locais criadas manualmente podem
ser ignoradas ou sobrescritas na próxima aplicação de política.

**4. Pré-requisitos** — Nenhum (só leitura).

**5. Procedimento**
```powershell
Get-NetFirewallProfile | Select-Object Name, Enabled, DefaultInboundAction, DefaultOutboundAction
Get-NetConnectionProfile                       # confirma perfil "DomainAuthenticated"
Get-NetFirewallRule -PolicyStore ActiveStore |
  Where-Object { $_.DisplayName -match 'Print|SNMP|ICMP|Python|Node|3000|8000' } |
  Select-Object DisplayName, Direction, Action, Enabled, Profile
Test-NetConnection elgjunprt -Port 135
Test-NetConnection 127.0.0.1 -Port 8000
```

**6. Resultado esperado** — Perfil `DomainAuthenticated`; saídas necessárias
permitidas; loopback livre.

**7. Como validar** — `Test-NetConnection` para cada destino do mapa da
seção 2. Quatro fronteiras, quatro testes.

**8. Evidências** — Tabela de perfis e regras; resultados de
`Test-NetConnection`; `gpo.html` seção Firewall.

**9. Possíveis erros** — Saída ICMP negada por padrão; RPC dinâmico
bloqueado; regra local sumindo após `gpupdate`.

**10. Impacto** — Combinação de D-02, D-06, D-07 e D-13 falhando ao mesmo
tempo — e o diagnóstico fica confuso porque parecem quatro problemas.

**11. Dentro/fora** — **Somente dentro** (perfil Domain só existe lá).

**12. Prioridade** — **P0** (faça cedo; explica muitos outros sintomas).

---

### D-22 · UAC e elevação

**1. Funcionalidade** — `Main.ps1` detecta elevação e recusa instalar driver
sem ela, com mensagem clara. Os scripts de serviço exigem admin.

**2. Onde existe** — `Main.ps1:1795-1798` e `1818-1821`
(`if (-not $script:IsElevated)`); `Servico-PrinterControl.ps1:18`
("direitos de administrador para instalar").

**3. Por que o domínio é relevante** — Em domínio o usuário comum **não** é
administrador local, e o UAC costuma estar em "Sempre notificar" por GPO.
`EnableLUA`, `ConsentPromptBehaviorUser` e `FilterAdministratorToken`
mudam o comportamento.

**4. Pré-requisitos** — Uma sessão de usuário comum **e** uma elevada.

**5. Procedimento**
```powershell
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" |
  Select-Object EnableLUA, ConsentPromptBehaviorAdmin, ConsentPromptBehaviorUser, FilterAdministratorToken
([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
net localgroup Administradores        # ou "Administrators"
```

**6. Resultado esperado** — Usuário comum: `False`, e `Main.ps1` mostra
"Requer Administrador" **em vez de falhar silenciosamente**.

**7. Como validar** — A mensagem aparece; nenhum driver é instalado.

**8. Evidências** — Captura da mensagem; valores do registro; membros do
grupo de administradores locais (revela se contas de domínio estão lá).

**9. Possíveis erros** — `ConsentPromptBehaviorUser=0` (negar
automaticamente) faz a elevação falhar sem prompt — confunde o usuário.

**10. Impacto** — Instalação de driver indisponível a usuário comum
(esperado); instalação do serviço exige chamado ao service desk.

**11. Dentro/fora** — **Somente dentro** para o caso realista.

**12. Prioridade** — **P2.**

---

### D-23 · Política de execução do PowerShell e logging por GPO

**1. Funcionalidade** — Tudo no projeto que é PowerShell depende da
`ExecutionPolicy` e é afetado por logging de script.

**2. Onde existe** — `print_server.py:159` (`-NoProfile -NonInteractive
-Command`, que **não** é afetado por `ExecutionPolicy` porque não carrega
arquivo); `Atualizar-PrinterControl.ps1` (documenta
`-ExecutionPolicy Bypass`); `Servico-PrinterControl.ps1` e
`ConfigurarAmbiente.ps1` (arquivos `.ps1`, **afetados**).

**3. Por que o domínio é relevante** — GPO comumente força
`AllSigned` ou `RemoteSigned` em nível de máquina, e essa configuração
**vence a de usuário**. Além disso, **Script Block Logging** e
**Transcription** podem injetar texto no stdout capturado por
`_run_powershell_json`, quebrando o `json.loads` — este é o modo de falha
`"Saida do PowerShell nao e JSON valido"` do D-02, e ele é **específico de
ambiente com GPO de auditoria**.

**4. Pré-requisitos** — Nenhum.

**5. Procedimento**
```powershell
Get-ExecutionPolicy -List
Get-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging" -EA SilentlyContinue
Get-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\Transcription" -EA SilentlyContinue
Get-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell" -EA SilentlyContinue |
  Select-Object ExecutionPolicy
# O teste que importa: a saída é JSON PURO?
powershell.exe -NoProfile -NonInteractive -Command "Get-Printer -ComputerName 'elgjunprt' | Select-Object Name | ConvertTo-Json -Compress" > "$env:TEMP\out.json"
Get-Content "$env:TEMP\out.json" -Raw | ConvertFrom-Json   # se falhar, há poluição no stdout
```

**6. Resultado esperado** — `ConvertFrom-Json` aceita a saída sem erro.

**7. Como validar** — Exatamente o último comando. É binário: ou parseia ou
não.

**8. Evidências** — `Get-ExecutionPolicy -List` completo; o arquivo
`out.json` bruto (**os primeiros bytes revelam BOM ou banner**);
chaves de política.

**9. Possíveis erros** — BOM UTF-8 no início; banner de módulo; aviso de
transcrição; `.ps1` recusado por `AllSigned`.

**10. Impacto** — Discovery falha com uma mensagem que aponta para o lugar
errado ("JSON inválido" sugere bug de código, não política de domínio).
É a falha mais confusa de diagnosticar de todo o documento.

**11. Dentro/fora** — **Somente dentro.**

**12. Prioridade** — **P1.**

---

### D-24 · Atualizador via GitHub através do proxy

**1. Funcionalidade** — `Atualizar-PrinterControl.ps1` baixa o ZIP do branch
`main` do GitHub e sobrepõe os arquivos com `robocopy`, preservando `.env`,
`*.db`, `venv`, `node_modules`, `.next`, `logs`.

**2. Onde existe** — `scripts/Atualizar-PrinterControl.ps1:36-66`.
O cabeçalho diz explicitamente: "Pensado para maquinas de dominio onde
instalar ferramentas nao e uma opcao."

**3. Por que o domínio é relevante** — `Invoke-WebRequest` precisa atravessar
o proxy corporativo (e não usa as configurações do WinINET por padrão em
todas as versões); `github.com` pode não estar na allowlist; `Expand-Archive`
sobre arquivo com Mark-of-the-Web pode ser bloqueado; TLS inspecionado pode
quebrar a validação de certificado.

**4. Pré-requisitos** — Cópia de trabalho limpa (`git status`), ou aceite de
sobrescrita.

**5. Procedimento** — 🔒 **REQUER APROVAÇÃO — sobrescreve arquivos.**
```powershell
# Fase 1: só a conectividade, sem escrever nada no projeto
Invoke-WebRequest -Uri "https://github.com/devribero/PrinterControl/archive/refs/heads/main.zip" -OutFile "$env:TEMP\teste.zip"
Get-Item "$env:TEMP\teste.zip" | Select-Object Length
# Fase 2 (aprovada): a atualização real
powershell -ExecutionPolicy Bypass -File .\scripts\Atualizar-PrinterControl.ps1
```

**6. Resultado esperado** — ZIP baixado com tamanho plausível;
`.env`, `.env.local` e `*.db` **intocados** após a execução.

**7. Como validar** — Hash do `backend\.env` e do `.db` **antes e depois**:
```powershell
Get-FileHash backend\.env, backend\printer_control.db | Format-Table Path, Hash
```
Devem ser idênticos. É a validação objetiva de que o `/XF` do robocopy
funcionou.

**8. Evidências** — Os dois conjuntos de hashes; saída do robocopy;
`git status` depois.

**9. Possíveis erros** — 407 (proxy exige autenticação); erro de TLS por
inspeção; ZIP bloqueado por MOTW; robocopy sem permissão de escrita.

**10. Impacto** — Sem caminho de atualização na máquina de domínio (que é
justamente onde não há Git).

**11. Dentro/fora** — Proxy e allowlist: **somente dentro**.

**12. Prioridade** — **P2.**

---

### D-25 · Fuso horário, virada de mês e relatório mensal

**1. Funcionalidade** — Jobs `cron` no dia 1 às 00:10 e no último dia às
23:50, em `America/Sao_Paulo`, que congelam `PrinterMonthly`.

**2. Onde existe** — `backend/app/services/scheduler.py` — `AsyncIOScheduler
(timezone="America/Sao_Paulo")`, jobs `month_start_snapshot` e `month_close`;
`services/monthly_report.py`.

**3. Por que o domínio é relevante** — GPO define o fuso e sincroniza a hora
via **`w32time` contra o DC**, não contra NTP público. Se a máquina estiver
em UTC (comum em VM de servidor) e o scheduler em `America/Sao_Paulo`, o
fechamento roda 3 h fora do esperado — pegando o mês errado na virada. Além
disso, `run_month_close` usa `datetime.utcnow()` enquanto o gatilho é em
horário local: às 23:50 de 31/01 em São Paulo, o UTC já é 01/02 — **o mês
fechado seria fevereiro, não janeiro**. Confirmar empiricamente; é um risco
real de dado errado (achado A-03).

**4. Pré-requisitos** — Scheduler ligado.

**5. Procedimento**
```powershell
w32tm /query /status
w32tm /query /source          # deve ser o DC do domínio
Get-TimeZone
[datetime]::UtcNow; Get-Date
curl.exe -s http://127.0.0.1:8000/health | ConvertFrom-Json | Select-Object -Expand scheduler
```
Para o comportamento de virada, execute o job **fora da virada**, num
ambiente de teste, forçando a data — 🔒 documentar, não executar em produção.

**6. Resultado esperado** — Fonte de tempo = DC; fuso = `E. South America
Standard Time`; `next_month_close` no último dia do mês às 23:50 **local**.

**7. Como validar** — Compare `next_month_close` de `/health` com o último
dia do mês corrente às 23:50 no relógio da máquina. Divergência = fuso.

**8. Evidências** — `w32tm /query /status`; `next_run`,
`next_month_start_snapshot` e `next_month_close` de `/health`; conteúdo de
`printer_monthly` após uma virada.

**9. Possíveis erros** — Deriva de relógio (rejeita Kerberos acima de 5 min —
**e isso derruba D-02 junto**); fuso UTC; mês fechado errado.

**10. Impacto** — Relatório mensal com o número no mês errado. Erro de dado,
não de disponibilidade — por isso passa despercebido por meses.

**11. Dentro/fora** — Sincronização com DC: **somente dentro**. A lógica de
virada é testável fora e **deveria ser**.

**12. Prioridade** — **P2** (mas o skew de relógio é **P0** por causa do
Kerberos — coberto em D-03/D-21).

---

## 4. Matriz completa de testes por categoria

Legenda: **Dom?** = só no domínio (`S`) ou também fora (`N`).
Ref = item da seção 3 ou arquivo de origem.

### 4.1 Autenticação (aplicacional)

| # | Teste | Ref | Dom? | Pri |
|---|---|---|---|---|
| AU-01 | Login com e-mail e com username resolvem a mesma conta | `routes/auth.py` | N | P1 |
| AU-02 | Senha errada e conta inexistente respondem em tempo semelhante (oráculo de tempo) | `routes/auth.py:39-55` | N | P2 |
| AU-03 | 6ª tentativa em 15 min → 429 com `Retry-After` | `config.py`, `rate_limit.py` | N | P1 |
| AU-04 | `X-Forwarded-For` forjado **não** contorna o limite (QA-10) | `routes/auth.py::_identificar_origem` | N | P0 |
| AU-05 | Token anterior à troca de senha → 401 (`token_version`) | `dependencies.py:95-104` | N | P1 |
| AU-06 | Conta desativada → 403 com mensagem específica, não 401 genérico | `dependencies.py:86-92` | N | P1 |
| AU-07 | **Confirmar ausência de SSO/Windows Auth e registrar como decisão** | esta análise | S | P1 |

### 4.2 Active Directory / identidade

| # | Teste | Ref | Dom? | Pri |
|---|---|---|---|---|
| AD-01 | Identidade interativa: `whoami /fqdn`, `/groups`, `USERDOMAIN` | D-01 | S | P0 |
| AD-02 | Identidade do processo do backend (tarefa vs. interativo) | D-01 | S | P0 |
| AD-03 | Conta de máquina `MÁQUINA$` consegue (ou não) enumerar o print server | D-01/D-02 | S | P0 |
| AD-04 | Kerberos vs. NTLM: `klist` após discovery por FQDN, curto e IP | D-03 | S | P1 |
| AD-05 | Deriva de relógio < 5 min contra o DC | D-25 | S | P0 |
| AD-06 | `SeBatchLogonRight` da conta de serviço | D-11 | S | P1 |
| AD-07 | Expiração de senha da conta de serviço (documentar política) | D-11 | S | P2 |

### 4.3 Permissões

| # | Teste | Ref | Dom? | Pri |
|---|---|---|---|---|
| PE-01 | Matriz papel × endpoint (viewer/operator/admin × todas as rotas) | D-15 | N | P1 |
| PE-02 | Admin do **domínio** não ganha privilégio no painel | D-15 | S | P1 |
| PE-03 | Frontend esconde vs. backend proíbe — testar **pela API** | `src/lib/permissions.ts` | N | P1 |
| PE-04 | `must_change_password` bloqueia tudo exceto `/auth/me` e `/change-password` | `dependencies.py:107-135` | N | P2 |
| PE-05 | Permissão por fila no print server → discovery parcial | D-02/D-04 | S | P0 |
| PE-06 | ACL da share de backup para `MÁQUINA$` | D-12 | S | P0 |
| PE-07 | ACL da pasta do projeto (quem lê o `.env` e o `.db`) | D-14/D-20 | S | P1 |

### 4.4 Rede corporativa

| # | Teste | Ref | Dom? | Pri |
|---|---|---|---|---|
| RE-01 | DNS interno resolve o print server (curto, FQDN, reverso) | D-03 | S | P0 |
| RE-02 | Sufixo de busca DNS entregue por GPO/DHCP | D-03 | S | P1 |
| RE-03 | ICMP a 400 ms vs. 3 s para amostra da frota | D-06 | S | P1 |
| RE-04 | UDP/161 alcançável entre VLANs | D-07 | S | P1 |
| RE-05 | TCP/135 + faixa RPC dinâmica até o print server | D-02/D-21 | S | P0 |
| RE-06 | IP por DHCP vs. `allowedDevOrigins` fixo | D-17 | S | P2 |

### 4.5 Servidores

| # | Teste | Ref | Dom? | Pri |
|---|---|---|---|---|
| SV-01 | `Get-Printer -ComputerName` retorna a frota completa | D-02 | S | P0 |
| SV-02 | `Get-PrinterPort` → `PrinterHostAddress` para todas as portas | D-02 | S | P0 |
| SV-03 | Fallback `ip = port_name` quando a porta não tem endereço (ex.: `USB001`) | `print_server.py:193` | S | P2 |
| SV-04 | Filas compartilhando o mesmo IP são agrupadas (uma consulta SNMP) | `discovery.py::_result_for_ip` | S | P2 |
| SV-05 | Timeout de 30 s: comportamento com print server lento | `config.py` | S | P2 |
| SV-06 | Cadastro de múltiplos print servers, cada um com seu modo | `routes/servers.py::create_server` | S | P2 |
| SV-07 | Sync de um servidor **não** desativa impressoras de outro | `printer_sync.py:83-88` | S | P1 |

### 4.6 Impressão

| # | Teste | Ref | Dom? | Pri |
|---|---|---|---|---|
| IM-01 | Point & Print via UNC sob GPO PrintNightmare | D-09 | S | P1 |
| IM-02 | `Get-PrinterDriver` local e detecção de driver pré-instalado | `Main.ps1:1694-1710` | S | P2 |
| IM-03 | Instalação de `.inf` e de `.exe` a partir da pasta `Drivers` | D-10 | S | P2 |
| IM-04 | Atalhos `.lnk` resolvendo para shares SMB | D-10 | S | P2 |
| IM-05 | Spooler parado → mensagem "Serviço de Spooler indisponível" | `Main.ps1:1712-1715` | S | P3 |

### 4.7 Segurança

| # | Teste | Ref | Dom? | Pri |
|---|---|---|---|---|
| SE-01 | Segredo do webhook versionado em `Main.ps1:11` | D-14 | N | P0 |
| SE-02 | Perfil de firewall `DomainAuthenticated` e regras efetivas | D-21 | S | P0 |
| SE-03 | EDR/IDS não bloqueia a varredura paralela | D-08 | S | P1 |
| SE-04 | Inspeção TLS quebra o webhook (`SSLCertVerificationError`) | D-13 | S | P2 |
| SE-05 | AppLocker/SRP contra `.exe` de driver vindo de share | D-10 | S | P2 |
| SE-06 | `ExecutionPolicy` e Script Block Logging poluindo o stdout | D-23 | S | P1 |

### 4.8 Integrações

| # | Teste | Ref | Dom? | Pri |
|---|---|---|---|---|
| IN-01 | Webhook Teams através do proxy corporativo | D-13 | S | P2 |
| IN-02 | Proxy visto pelo processo SYSTEM vs. usuário | D-13/D-19 | S | P2 |
| IN-03 | Download do GitHub pelo atualizador | D-24 | S | P2 |
| IN-04 | URL do webhook **nunca** aparece no log (só o host) | `webhook_notifier.py::_safe_host` | N | P1 |

### 4.9 Infraestrutura

| # | Teste | Ref | Dom? | Pri |
|---|---|---|---|---|
| IF-01 | Instalação da tarefa agendada com conta de domínio | D-11 | S | P0 |
| IF-02 | Sobe no boot sem ninguém logado | D-11 | S | P0 |
| IF-03 | Reinício automático após kill do processo (`RestartCount 999`) | D-11 | N | P1 |
| IF-04 | `uptime_seconds` crescendo (detecta reinício em laço) | `main.py::health_check` | N | P1 |
| IF-05 | Banco em disco local fixo, não em pasta redirecionada | D-20 | S | P0 |
| IF-06 | Backup em UNC gravável por `MÁQUINA$` | D-12 | S | P0 |
| IF-07 | Restauração do backup + `PRAGMA integrity_check` | D-12 | N | P0 |
| IF-08 | Rotação de log (5 MB × 10) e permissão de escrita em `backend\logs` | `config.py` (`log_*`) | N | P2 |

### 4.10 Políticas de domínio (GPO)

| # | Teste | Ref | Dom? | Pri |
|---|---|---|---|---|
| GP-01 | `gpresult /h` completo — inventário de tudo que se aplica | D-09/D-19 | S | P0 |
| GP-02 | Variáveis de ambiente injetadas por GPO ou script de logon | D-19 | S | P0 |
| GP-03 | Point & Print / `RestrictDriverInstallationToAdministrators` | D-09 | S | P1 |
| GP-04 | `ExecutionPolicy` de máquina e logging de script | D-23 | S | P1 |
| GP-05 | UAC (`EnableLUA`, `ConsentPromptBehavior*`) | D-22 | S | P2 |
| GP-06 | Redirecionamento de Pastas (Desktop) e perfil móvel | D-20/D-16 | S | P0 |
| GP-07 | Políticas de navegador (limpar storage no logoff) | D-16 | S | P2 |

### 4.11 Resiliência e tratamento de erros

| # | Teste | Ref | Dom? | Pri |
|---|---|---|---|---|
| RS-01 | Print server inalcançável → 502, **nada escrito no banco** | `printer_sync.py` (docstring) | S | P0 |
| RS-02 | Descoberta **parcial** (permissão por fila) → desativação em massa | D-04 | S | P0 |
| RS-03 | Impressora offline → `status_reason=ping_failed`, não erro genérico | `discovery.py::_empty_result` | S | P1 |
| RS-04 | SNMP mudo com ping OK → `ping_ok_snmp_not_responding` | `discovery.py:97-104` | S | P1 |
| RS-05 | **Coleta parada não gera alerta nenhum** — confirmar e registrar como lacuna | `scheduler.py`, `/health` | N | P1 |
| RS-06 | Webhook falhando não derruba a coleta | `webhook_notifier.py` (docstring) | N | P1 |
| RS-07 | 429 do limite de ações de rede (10/60 s por usuário) | `dependencies.py::rate_limited_action` | N | P2 |

---

## 5. Testes prioritários para executar na máquina do domínio

Sequência recomendada. **A ordem importa**: cada bloco elimina causas que,
se ignoradas, fariam os blocos seguintes falharem por motivos errados.

### Bloco 0 — Reconhecimento (30 min, somente leitura, risco zero)

Nada aqui altera coisa alguma. Faça tudo antes de tocar no sistema.

1. **GP-01** `gpresult /h "$env:TEMP\gpo.html"` — o inventário do que o
   domínio impõe. Leia antes de testar; economiza horas.
2. **AD-01** Identidade: `whoami /fqdn`, `whoami /groups`, `$env:USERDOMAIN`,
   `$env:LOGONSERVER`, `$env:COMPUTERNAME`.
3. **GP-02 / D-19** Dump das variáveis de ambiente (Usuário **e** Máquina).
   *Se houver colisão com uma chave do `Settings`, pare e resolva primeiro —
   todo o resto seria medido sobre uma configuração que não é a que você acha.*
4. **AD-05** `w32tm /query /status` — deriva de relógio.
   *Acima de 5 min, Kerberos falha e o bloco 1 inteiro dá falso negativo.*
5. **GP-06 / IF-05** Desktop redirecionado? Banco em disco local?
6. **SE-02** Perfil de firewall e regras efetivas.
7. **RE-01** DNS: resolve curto, FQDN e reverso do print server.
8. **SE-01** Confirmar o segredo em `Main.ps1:11` e a ACL da pasta.
   *Reportar imediatamente — não espera o fim da bateria.*

**Portão:** se 3, 4, 5 ou 7 falharem, **não avance**. Corrija (com aprovação)
e recomece o bloco.

### Bloco 1 — O caminho crítico do domínio (1–2 h)

9. **AD-02 / D-01** Conta de execução da tarefa vs. interativo.
10. **D-23 / SE-06** `ExecutionPolicy` e — sobretudo — o teste de
    **stdout puro**: `ConvertFrom-Json` na saída do `Get-Printer`.
    *Se isto falhar, o D-02 vai reportar "JSON inválido" e você vai procurar
    bug no Python por horas.*
11. **SV-01 / D-02** `Get-Printer -ComputerName` cru, no contexto interativo.
12. **SV-02** `Get-PrinterPort` e o mapa de `PrinterHostAddress`.
13. **AD-03** Repetir 11 e 12 **no contexto da tarefa agendada** (a
    diferença entre 11/12 e 13 é o achado mais valioso desta bateria).
14. **AD-04** `klist` — Kerberos ou NTLM? Repetir com FQDN e com IP.
15. **PE-05** Conferir: `count` da API == `(Get-Printer).Count`.
    *Divergência aqui é o gatilho do cenário catastrófico do RS-02.*

**Portão:** 15 precisa bater **exatamente**. Discovery parcial + sync =
desativação em massa da frota.

### Bloco 2 — Rede de segurança, antes de escrever qualquer coisa (30 min)

16. **IF-06 / D-12** Backup em UNC gravável — testado **como SYSTEM**, não só
    como você.
17. **IF-07** Restaurar o backup e rodar `PRAGMA integrity_check`.
    *Um backup não verificado não é um backup.*

**Portão:** não execute o bloco 3 sem 17 verde.

### Bloco 3 — Escrita no banco (🔒 com aprovação, 30 min)

18. **RS-01** Print server inalcançável → 502 e banco intocado (aponte para um
    host válido mas inexistente; é o teste negativo mais barato).
19. **D-04 / SV-07** Sync real, com backup fresco, contagens antes e depois.
20. Conferir `deactivated == 0`. **Qualquer outro valor exige investigação
    antes de prosseguir.**

### Bloco 4 — Rede até a frota (1 h)

21. **RE-03 / D-06** ICMP a 400 ms vs. 3 s.
22. **RE-04 / D-07** SNMP numa impressora, com validação contra o painel
    físico do equipamento.
23. **SE-03 / D-08** Um ciclo `collect/fleet` completo — **com a equipe de
    segurança avisada**. Meça a duração e compare com o intervalo.

### Bloco 5 — Serviço em regime permanente (🔒, meia janela)

24. **IF-01** Instalar a tarefa com a conta de domínio decidida no passo 9.
25. **IF-02** Reboot da máquina; confirmar que sobe sem login.
26. **IF-04** `/health` duas vezes espaçadas: `uptime_seconds` crescendo.
27. **AD-03 bis** Confirmar que a coleta agendada funciona sob a conta do
    serviço — este é o teste que fecha o ciclo aberto no passo 9.

### Bloco 6 — Periferia (pode ficar para uma segunda janela)

28. **IN-01 / D-13** Webhook pelo proxy, para canal de teste.
29. **IM-01 / D-09** Point & Print sob GPO, com usuário comum.
30. **RE-06 / D-17** Acesso ao painel pelo IP atual da máquina.
31. **IN-03 / D-24** Atualizador via GitHub, com verificação de hash do `.env`.
32. **GP-07 / D-16** Sessão entre dois perfis de domínio.

### O que fazer **fora** do domínio (para não gastar a janela)

Toda a seção 4.1 (autenticação), a 4.3 exceto PE-05/06/07, e IF-03, IF-04,
IF-07, IN-04, RS-05, RS-06, RS-07 e D-05 (exclusão em cascata). São ~20
testes que não ganham nada com o ambiente corporativo e consomem tempo que só
existe lá.

---

## 6. Evidências — o pacote mínimo por sessão de teste

Colete sempre, independentemente do teste:

```powershell
$ev = "$env:USERPROFILE\Desktop\evidencias-printercontrol-$(Get-Date -f yyyyMMdd-HHmm)"
New-Item -ItemType Directory $ev | Out-Null

whoami /all                                       > "$ev\identidade.txt"
gpresult /h                                         "$ev\gpo.html"
Get-ChildItem Env: | Sort-Object Name             > "$ev\env-usuario.txt"
[Environment]::GetEnvironmentVariables('Machine') > "$ev\env-maquina.txt"
Get-NetFirewallProfile                            > "$ev\firewall-perfis.txt"
Get-NetConnectionProfile                          > "$ev\firewall-conexao.txt"
w32tm /query /status                              > "$ev\tempo.txt"
Get-ExecutionPolicy -List                         > "$ev\execpolicy.txt"
klist                                             > "$ev\kerberos.txt"
ipconfig /all                                     > "$ev\rede.txt"
Get-ScheduledTask -TaskName PrinterControl-* | Format-List * > "$ev\tarefas.txt"
curl.exe -s http://127.0.0.1:8000/health          > "$ev\health.json"
Copy-Item backend\logs\printercontrol.log "$ev\" -ErrorAction SilentlyContinue
```

Além disso, por teste: **comando exato executado**, **saída bruta completa**,
**horário**, **conta usada**, e — quando houver interface — **captura de
tela**. Uma evidência sem a conta e o horário não é rastreável.

---

## 7. Achados desta análise que não são testes

Registrados aqui porque emergiram da leitura do código e o time precisa
decidir sobre eles. **Nenhum foi corrigido.**

| # | Achado | Onde | Severidade |
|---|---|---|---|
| A-01 | URL de webhook com assinatura, em texto claro, versionada | `Main.ps1:11` | **Alta** |
| A-02 | `ping_timeout_ms=400` fixo no código, não configurável por `.env` — inadequado para WAN corporativa | `snmp.py::SNMPClient.__init__` | Média |
| A-03 | `run_month_close` usa `datetime.utcnow()` com gatilho em horário local: às 23:50 de 31/01 em São Paulo, o UTC já é 01/02 | `scheduler.py` | **Alta** (dado errado) |
| A-04 | Não há alerta para "coleta parada". `/health` expõe `scheduler.running`, mas nada consome isso | `scheduler.py`, `main.py::health_check` | Média |
| A-05 | `Servico-PrinterControl.ps1` instala com SYSTEM por padrão, sabendo que provavelmente falha em domínio — o aviso é texto amarelo, não uma recusa | `Servico-PrinterControl.ps1::Instalar` | Média |
| A-06 | `README.md` desatualizado: descreve Vite e scripts (`Coletar-Impressoras.ps1`, `Relatorio-Mensal.ps1`, `Simular-Ambiente.ps1`) que `CONTEXTO-DESENVOLVIMENTO.md` diz terem sido removidos | `README.md` | Baixa |
| A-07 | `DEV_NETWORK_ACCESS.md` tem item de aceite em aberto (`[ ] Confirmar no navegador`) — é o D-17 | `docs/DEV_NETWORK_ACCESS.md` | Baixa |
| A-08 | Situação do `Main.ps1` indefinida: ainda no repo, com funcionalidade (Point & Print, drivers) que o backend não replica. Ou é produto, ou é legado — hoje é ambíguo, e isso muda a prioridade de IM-01…IM-05 | raiz do repo | Média |

---

## 8. O que este documento deliberadamente não cobre

- **Não propõe alterar GPO, ACL, firewall ou contas.** Onde uma mudança
  parece necessária, o documento diz "documentar" e para aí.
- **Não executa nada.** Todos os comandos são para leitura humana e aprovação.
- **Não decide sobre o `Main.ps1`** (A-08). A prioridade de cinco testes
  depende dessa decisão, que é do time.
- **Não cobre teste de carga**, nem a migração para VM Windows Server descrita
  em `docs/superpowers/specs/2026-09-01-vm-windows-migration-design.md` —
  aquilo é outro plano, com outra janela.
