# Operação em Produção

Runbook do backend do PrinterControl em Windows. Escrito para ser seguido por
alguém que **não** acompanhou o desenvolvimento — inclusive você daqui a seis
meses, às 2h da manhã.

Escopo: subir, derrubar, diagnosticar, fazer backup e restaurar. A exposição
externa (Cloudflare Tunnel) é assunto de `DEPLOYMENT_ARCHITECTURE.md`.

---

## 1. Antes do primeiro deploy

O backend **recusa subir** com configuração incoerente. Isso é proposital: as
falhas abaixo aparecem no boot, com mensagem explícita, em vez de virarem um
problema silencioso em produção.

Preencha `backend/.env` (copie de `backend/.env.example`):

| Variável | Valor em produção | Se estiver errado |
|---|---|---|
| `ENVIRONMENT` | `production` | Valor desconhecido → recusa subir |
| `SECRET_KEY` | 32+ chars, própria | Default ou curta → recusa subir |
| `PRINT_SERVER_MODE` | `real` | `mock` → recusa subir |
| `ALLOW_MOCK_COLLECT` | `false` (ou ausente) | `true` → recusa subir |
| `CORS_ORIGINS` | origem HTTPS do painel | Vazio, `*`, localhost ou http → recusa subir |
| `COLLECTION_ENABLED` | `true` para coletar sozinho | `false` → nada é coletado e ninguém avisa |
| `LOGIN_MAX_ATTEMPTS` / `LOGIN_WINDOW_SECONDS` | `5` / `900` | Muito alto → força bruta viável |
| `TRUST_PROXY_HEADERS` | `false` até o Tunnel entrar | `true` sem proxy de confiança **enfraquece** o limite de login |

**Senha das contas de administrador.** Elas não têm mais senha fixa. Num banco
novo, `seed.py` gera uma senha forte e a mostra **uma única vez**. Num banco
criado antes da Fase 10 (que ainda usa a senha antiga), rotacione:

```powershell
.\venv\Scripts\python.exe seed.py --resetar-senhas
```

Anote na hora — ela não fica gravada em texto claro em lugar nenhum.

Gere a `SECRET_KEY`:

```powershell
.\backend\venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"
```

**`CORS_ORIGINS` é a origem do FRONTEND**, não a do backend. Com o painel na
Vercel e o backend em `elginprint.devribero.online`, o valor é o domínio da
Vercel.

Teste a configuração **antes** de instalar o serviço — é mais rápido ver o erro
no terminal do que no log de uma tarefa agendada:

```powershell
cd backend
.\venv\Scripts\python.exe -c "from app.config import settings; print('OK', settings.environment)"
```

---

## 2. Instalar

Como Administrador, na raiz do projeto:

```powershell
pwsh .\scripts\Servico-PrinterControl.ps1 -Acao instalar
```

Cria duas tarefas agendadas: `PrinterControl-Backend` (sobe no boot, reinicia
em falha) e `PrinterControl-Backup` (a cada 6h, mantendo 14 cópias).

### A escolha da conta — leia se a coleta falhar

O padrão é **SYSTEM**: sobe sem ninguém logado e não exige senha guardada.
Mas a coleta real precisa de RPC/PowerShell até o Print Server e SNMP até as
impressoras. Em domínio, SYSTEM se apresenta como a **conta de máquina**
(`DOMINIO\MAQUINA$`), que normalmente **não** tem essa permissão.

O sintoma é característico: **a API sobe normalmente e toda coleta falha.**
Se acontecer, reinstale com uma conta de domínio:

```powershell
pwsh .\scripts\Servico-PrinterControl.ps1 -Acao instalar -Conta "DOMINIO\usuario"
```

---

## 3. Dia a dia

```powershell
pwsh .\scripts\Servico-PrinterControl.ps1 -Acao status    # estado + /health
pwsh .\scripts\Servico-PrinterControl.ps1 -Acao parar
pwsh .\scripts\Servico-PrinterControl.ps1 -Acao iniciar
pwsh .\scripts\Servico-PrinterControl.ps1 -Acao remover
```

`status` consulta as tarefas **e** chama `/health`, porque as duas coisas podem
divergir: o Windows pode considerar a tarefa "Running" com o processo de pé
porém travado. **Quem diz a verdade é o `/health`.**

---

## 4. Diagnóstico

### `/health`

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health | ConvertTo-Json
```

| Campo | O que observar |
|---|---|
| `status` | `ok` ou `degraded`. **Monitore este campo, não só o HTTP 200** |
| `uptime_seconds` | Se nunca passa de poucos minutos, o serviço reinicia em laço |
| `database` | `erro` = banco não respondeu (arquivo sumiu, lock, disco cheio) |
| `scheduler.running` | `false` com `enabled: true` = coleta parada sem ninguém ver |
| `environment` | Confirma que a instância é a que você pensa que é |

`/health` responde **200 mesmo degradado**, de propósito: o processo está de
pé e respondendo. Derrubar o healthcheck faria o supervisor reiniciá-lo em
laço sem corrigir a causa.

### Logs

`backend/logs/printercontrol.log`, com rotação (5 MB × 10 arquivos).

```powershell
Get-Content backend\logs\printercontrol.log -Tail 50 -Wait
Select-String -Path backend\logs\printercontrol.log -Pattern "ERROR|FALHA"
```

Segredos são redigidos antes da gravação (`app/logging_config.py`). Se aparecer
`***REDIGIDO***`, o filtro funcionou — não é erro.

---

## 5. Backup

Automático a cada 6h. Manual:

```powershell
cd backend
.\venv\Scripts\python.exe backup_db.py --keep 14
```

Usa a API de backup **online** do SQLite: roda com o serviço no ar, sem janela
de indisponibilidade. Copiar `printer_control.db` com `copy` **não** é
equivalente — em modo WAL a cópia pode sair incoerente e sem os dados que ainda
estão no arquivo `-wal`.

Cada backup passa por `integrity_check` na hora da geração e é colapsado num
**arquivo único** (sem `-wal`/`-shm` ao lado).

### Restaurar

```powershell
# 1. parar
pwsh .\scripts\Servico-PrinterControl.ps1 -Acao parar

# 2. guardar o banco atual (não o apague — pode ser a única cópia do que falta)
Move-Item backend\printer_control.db backend\printer_control.db.quebrado

# 3. remover companheiros do WAL, senão o SQLite tenta aplicá-los ao banco novo
Remove-Item backend\printer_control.db-wal, backend\printer_control.db-shm -ErrorAction SilentlyContinue

# 4. restaurar
Copy-Item backend\backups\printer_control-AAAAMMDD-HHMMSS.db backend\printer_control.db

# 5. subir e conferir
pwsh .\scripts\Servico-PrinterControl.ps1 -Acao iniciar
```

O passo 3 não é opcional: um `-wal` órfão do banco anterior aplicado sobre o
banco restaurado corrompe o resultado.

**Teste uma restauração antes de precisar dela.** Um backup nunca verificado é
uma suposição.

---

## 6. Recuperação — o que acontece se o processo cair

| Situação | Consequência | Ação |
|---|---|---|
| Queda no meio de um **ciclo de coleta** | As impressoras já coletadas têm leitura gravada; as demais, não. Cada leitura é uma transação própria — não existe estado "meio gravado" | Nenhuma. O próximo ciclo recolhe tudo |
| Queda no meio de um **sync de Print Server** | Idem: sem meia-impressora. Nunca há exclusão — quem some é marcado inativo | Rodar o sync de novo |
| Queda no meio de uma **requisição HTTP** | O cliente recebe erro de conexão. A transação não confirmada é descartada pelo SQLite | Repetir a ação no painel |
| **Máquina reiniciada** | A tarefa sobe no boot | Conferir com `-Acao status` |
| **Processo morto** (OOM, crash) | Task Scheduler reinicia em até 1 min | Investigar o log; `uptime_seconds` baixo e recorrente indica laço |

O `PRAGMA synchronous=NORMAL` protege contra queda do **processo**, que é o
cenário real aqui. Queda de energia do sistema inteiro no instante exato de uma
escrita pode custar a última transação — o backup periódico é a rede para isso.

**O scheduler não persiste estado.** É recriado a partir do `.env` a cada boot,
sem fila acumulada: um ciclo perdido é perdido, e o próximo roda no horário
normal. Isso é desejável — coleta atrasada não tem valor retroativo. Ele também
não roda dois ciclos em paralelo (`max_instances=1`): se um demorar mais que o
intervalo, o disparo seguinte é descartado em vez de concorrer pelo banco.

---

## 7. Problemas comuns

| Sintoma | Causa provável | Verificação |
|---|---|---|
| Tarefa "Running" mas `/health` não responde | Processo travado, ou falhou no boot | Log; `parar` e `iniciar` |
| Serviço não sobe | Config recusada no boot | Rodar o teste da seção 1 — a mensagem diz qual variável |
| API sobe, toda coleta falha | Conta SYSTEM sem permissão de rede | Seção 2 |
| Painel com erro de CORS | `CORS_ORIGINS` sem a origem real | Conferir o domínio exato, com `https://` e sem barra final |
| `database is locked` | Escrita concorrente longa | Já há `busy_timeout=5s` e WAL. Recorrente = investigar ciclo lento |
| Disco enchendo | Backups sem retenção | `--keep`; a rotação de log já é limitada a ~50 MB |

---

## 8. Dívida técnica conhecida — FK órfã para `printers_old`

> **A lista completa da dívida técnica está em
> [`TECHNICAL_DEBT.md`](TECHNICAL_DEBT.md) (D1–D13).** Este item continua
> detalhado aqui porque é o único com uma armadilha *operacional* — alguém
> mexendo no banco às 2h da manhã precisa esbarrar nele sem ter que abrir
> outro documento. Lá ele é **D1**.
>
> Dois outros itens têm impacto direto na operação e valem conhecer:
> **D6** (o backend fala HTTP puro e depende do túnel para TLS; o bloco de
> execução direta de `app/main.py` já foi corrigido para `127.0.0.1`) e **D13** (`/health` existe mas nada o
> consulta automaticamente — se o banco travar ou a coleta parar, ninguém é
> avisado).

**Status:** conhecida, aceita, adiada deliberadamente. Não é bug novo nem
regressão — está no banco desde as etapas antigas e **não afeta a operação
hoje**. Registrada aqui para não ser redescoberta por acidente.

### O que é

`printer_readings` e `alerts` declaram chave estrangeira para uma tabela
`printers_old`, que não existe mais — resíduo da migração de schema que
renomeou `printers`. Verificável:

```powershell
cd backend
.\venv\Scripts\python.exe -c "import sqlite3; print(sqlite3.connect('printer_control.db').execute('PRAGMA foreign_key_check').fetchall()[:5])"
```

### Por que não incomoda

O SQLite vem com `PRAGMA foreign_keys` **desligado** por padrão, e o
PrinterControl mantém assim (ver `app/database.py`). Com a checagem desligada,
a FK órfã é texto morto no schema.

A integridade referencial continua garantida **pelo código**: nada apaga
impressora — o que some de um Print Server vira `active=False`. Nunca houve
`ON DELETE` para a FK exercer.

### ⚠️ A armadilha

**Ligar `PRAGMA foreign_keys=ON` quebra a aplicação inteira, na hora.** Todo
INSERT em `printer_readings` passa a falhar com:

```
no such table: main.printers_old
```

e a coleta para por completo. Isso foi descoberto na Fase 10, ligando o pragma
como melhoria — o comentário em `app/database.py` existe para impedir que
alguém o reintroduza achando que é um esquecimento.

**Não ligue esse pragma sem antes fazer a migração abaixo.**

### Como quitar, quando for prioridade

Reconstruir as duas tabelas com a FK correta. Exige janela e backup:

1. `backup_db.py` e **guardar o arquivo fora da máquina**;
2. parar o serviço;
3. para `printer_readings` e `alerts`: criar tabela nova com FK para
   `printers`, copiar os dados, remover a antiga, renomear;
4. conferir com `PRAGMA foreign_key_check` (deve voltar vazio);
5. só então ligar `foreign_keys=ON` em `app/database.py`;
6. subir e rodar um ciclo de coleta antes de considerar concluído.

Fazer isso junto de qualquer outra migração de schema economiza uma janela.

---

## 9. Se precisar aparecer em `services.msc`

O Task Scheduler foi escolhido por ser nativo e não exigir instalação. Se um
monitoramento corporativo só enxergar serviços de verdade, o caminho é o
[NSSM](https://nssm.cc):

```powershell
nssm install PrinterControl "C:\...\backend\venv\Scripts\python.exe" "-m uvicorn app.main:app --host 127.0.0.1 --port 8000"
nssm set PrinterControl AppDirectory "C:\...\backend"
nssm set PrinterControl AppStdout "C:\...\backend\logs\service-stdout.log"
nssm set PrinterControl Start SERVICE_AUTO_START
nssm start PrinterControl
```

Remova antes a tarefa agendada (`-Acao remover`) — as duas rodando juntas
disputariam a porta 8000.
