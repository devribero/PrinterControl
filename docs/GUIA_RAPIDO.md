# Guia Rápido — PrinterControl

Referência única para retomar o trabalho amanhã: como rodar em desenvolvimento,
como operar em produção, e um roteiro de teste em produção passo a passo.

Para detalhes profundos, use os runbooks específicos (seção 5).

---

## 1. Desenvolvimento (local)

### Pré-requisitos

- **Node.js** 20+ (projeto usa Next.js 16, React 19)
- **Python** 3.11+ com `venv`
- Windows (scripts de coleta real dependem de PowerShell/RPC — mas o modo
  `mock`/demo funciona em qualquer SO)

### Subir o backend

```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt   # só na primeira vez / após mudanças
python app/main.py
```

Sobe em `http://127.0.0.1:8000`. Sem banco existente, rode antes:

```powershell
.\venv\Scripts\python.exe seed.py
```

Isso cria as contas iniciais e imprime a senha do admin **uma única vez** no
console — anote na hora.

### Subir o frontend

```powershell
npm install   # só na primeira vez / após mudanças no package.json
npm run dev
```

Sobe em `http://localhost:3000`.

### Variáveis de ambiente

**Raiz do projeto** — `.env.local` (copie de `.env.example`):
```
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

**`backend/.env`** (copie de `backend/.env.example`) — em desenvolvimento os
defaults já servem; os campos que mais importam:
```
ENVIRONMENT=development
SECRET_KEY=change-me-in-production   # ok em dev, NUNCA em produção
PRINT_SERVER_MODE=mock               # real exige rede da Elgin
ALLOW_MOCK_COLLECT=true              # libera coleta simulada
COLLECTION_ENABLED=false             # true se quiser coleta automática local
```

### Acesso local

| O quê | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend / API | http://127.0.0.1:8000 |
| Health check | http://127.0.0.1:8000/health |
| Docs interativas (Swagger) | http://127.0.0.1:8000/docs |

### Credenciais de teste

Não há senha fixa. `seed.py` gera uma senha forte na primeira execução e
mostra uma única vez no console. Se perdida, rotacione:

```powershell
.\venv\Scripts\python.exe seed.py --resetar-senhas
```

### Testes em desenvolvimento

```powershell
cd backend
.\venv\Scripts\python.exe -m pytest
```

Algumas suítes (`tests_collect_api`, `tests_printers_crud`, `tests_fleet`)
exigem infraestrutura externa (rede/SNMP real) e são normalmente puladas fora
de um ambiente com Print Server acessível.

### Modo demo vs modo real (frontend)

O painel funciona sem nenhum arquivo de dados: cai automaticamente no **modo
demonstração** (dados fixos de `src/data/printers.ts`). Para ver dados reais
localmente, é preciso que o backend em `PRINT_SERVER_MODE=real` esteja no ar
e acessível — normalmente só de dentro da rede da Elgin/VPN.

---

## 2. Produção

### Verificar se está no ar

```
GET https://elginprint.devribero.online/health
```

| Campo | Significado |
|---|---|
| `status` | `ok` ou `degraded` — monitore isto, não só o HTTP 200 |
| `uptime_seconds` | Se sempre baixo, o processo está reiniciando em laço |
| `database` | `erro` = banco não respondeu |
| `scheduler.running` | `false` com `enabled: true` = coleta parada sem aviso |
| `environment` | Confirma que é a instância certa (deve ser `production`) |

### Reiniciar o backend se cair

**Nota importante:** apesar da documentação original prever Task Scheduler
(`scripts\Servico-PrinterControl.ps1`), na última verificação (Fase 12) o
backend estava rodando como **processo comum de terminal**, não como tarefa
agendada — ele já caiu sem encerramento limpo uma vez por esse motivo.

Se o script de serviço estiver instalado:
```powershell
pwsh .\scripts\Servico-PrinterControl.ps1 -Acao status
pwsh .\scripts\Servico-PrinterControl.ps1 -Acao iniciar
```

Se **não** estiver (cenário mais provável agora), suba manualmente:
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python app/main.py
```
Confirme com `/health` logo em seguida. Considere rodar `-Acao instalar`
como Administrador para não depender de reinício manual (ver `OPERATIONS.md`
seção 2).

### Logs

`backend/logs/printercontrol.log` (rotação 5 MB × 10 arquivos):
```powershell
Get-Content backend\logs\printercontrol.log -Tail 50 -Wait
Select-String -Path backend\logs\printercontrol.log -Pattern "ERROR|FALHA"
```
Segredos aparecem como `***REDIGIDO***` — isso é o filtro funcionando, não erro.

### Backup manual do banco

```powershell
cd backend
.\venv\Scripts\python.exe backup_db.py --keep 14
```
Usa a API de backup online do SQLite — não copie `printer_control.db` direto
com `copy`, o resultado pode sair incoerente (modo WAL).

### Se o Cloudflare Tunnel cair

1. Verifique o serviço do `cloudflared` no Windows (conector `DESKTOP-K7J9N5H`).
2. Confira o painel em https://dash.cloudflare.com (túnel "Elgin - Impressoras").
3. Passo a passo completo: [`CLOUDFLARE_TUNNEL.md`](CLOUDFLARE_TUNNEL.md).

### Se a Vercel cair

1. Verifique https://vercel.com/dashboard — status do deploy mais recente.
2. Confira se o build falhou (logs do deploy na Vercel).
3. Passo a passo completo: [`VERCEL_DEPLOY.md`](VERCEL_DEPLOY.md).

### Como atualizar o sistema

1. **Frontend:** `git push` para `main` (ou branch conectada) — a Vercel builda
   e publica automaticamente. Confirme o novo deploy no dashboard.
2. **Backend:** puxe o código novo na máquina de produção, reinstale
   dependências se `requirements.txt` mudou, e reinicie o processo (seção
   "Reiniciar o backend" acima).

---

## 3. Roteiro de teste em produção (amanhã)

Ordenado para falhar cedo e de forma reversível — pare no primeiro problema
e resolva antes de seguir.

1. **Health check** — `GET https://elginprint.devribero.online/health`.
   Confirme `status: ok`, `environment: production`.
2. **Login com `pedro.ribeiro`** — confirme que **não** aparece nenhuma faixa
   de demonstração no painel.
3. **Nomes reais de impressora** — confira que os nomes não são fictícios
   (ex.: nada como `VLO_Diretoria`, que é dado de demo/mock).
4. **`/network` → Discovery** — selecione o servidor de impressão e rode
   Discovery; confira se as impressoras encontradas fazem sentido.
5. **Sync** — rode e confirme que a frota foi atualizada **sem remover nada
   inesperado** (impressoras somem viram "inativas", nunca são apagadas).
6. **`/alerts`** — há alertas reais? Toner baixo? Impressoras offline?
7. **`/notifications`** — crie uma notificação de teste e confirme que aparece.
8. **`/settings`** — troque um nome e confirme que salvou.
9. **RBAC:**
   - Login com `mateus.vicentino@elgin.com.br` (admin) → acesso completo.
   - Se houver conta operator/viewer, confirme que botões de admin **não**
     aparecem para essas contas.
10. **Impressão real** (se possível) — imprima algo e veja se o contador de
    páginas sobe no sistema após o próximo ciclo de coleta.

---

## 4. Sinais de problema e como reagir

| Sinal | Causa provável | Ação |
|---|---|---|
| Faixa âmbar no topo do painel | Backend caiu ou sem conexão | Verificar `/health` → reiniciar (seção 2) |
| Faixa colorida de "demonstração" | `ENVIRONMENT` não está `production` | Verificar `backend/.env` |
| Erro 401 ao navegar | Sessão expirou | Fazer login de novo |
| Erro 403 | Conta sem permissão para aquela ação | Esperado para viewer/operator em rotas admin |
| Erro 429 | Muitas tentativas de login | Aguardar 15 minutos (`LOGIN_WINDOW_SECONDS`) |
| Impressoras não aparecem | Print Server desconfigurado | Verificar `/network` |
| Discovery não encontra nada | Problema de rede/SNMP | Verificar se o servidor de impressão está acessível |
| Sync desativou impressoras inesperadamente | Servidor em modo `mock` | Verificar `PRINT_SERVER_MODE` em `/network` |
| Frontend em branco | Problema na Vercel | Verificar vercel.com/dashboard |
| CORS error no console (F12) | `CORS_ORIGINS` desatualizado no backend | Verificar `.env` e reiniciar o backend |

---

## 5. Links e referências rápidas

- Frontend produção: https://printercontrol.vercel.app
- API produção: https://elginprint.devribero.online
- Health check: https://elginprint.devribero.online/health
- GitHub: https://github.com/devribero/PrinterControl
- Painel Cloudflare: https://dash.cloudflare.com
- Painel Vercel: https://vercel.com/dashboard
- Documentação completa: [`docs/VISAO_GERAL.md`](VISAO_GERAL.md)
- Runbook operacional: [`docs/OPERATIONS.md`](OPERATIONS.md)
- Runbook Cloudflare: [`docs/CLOUDFLARE_TUNNEL.md`](CLOUDFLARE_TUNNEL.md)
- Runbook Vercel: [`docs/VERCEL_DEPLOY.md`](VERCEL_DEPLOY.md)
- Dívidas técnicas: [`docs/TECHNICAL_DEBT.md`](TECHNICAL_DEBT.md)
