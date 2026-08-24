# Cloudflare Tunnel — expor a API sem abrir porta (Fase 11)

> **✅ Concluída em 2026-08-24.** O túnel está no ar e validado:
>
> | | |
> |---|---|
> | **Nome do túnel** | `Elgin - Impressoras` |
> | **Subdomínio publicado** | `elginprint.devribero.online` → `http://127.0.0.1:8000` |
> | **Conector** | Windows `DESKTOP-K7J9N5H`, serviço `Cloudflared` ativo (sobe no boot) |
> | **Status no painel** | Healthy |
> | **Validado com** | `GET https://elginprint.devribero.online/health` → `200` |
> | **`TRUST_PROXY_HEADERS`** | `true` em `backend/.env` (o túnel é agora o único caminho de entrada) |
> | **`CORS_ORIGINS`** | continua vazio — Fase 12, quando a Vercel tiver URL (ver seção 7) |
>
> O passo a passo abaixo fica como referência para reinstalação, uma segunda
> máquina, ou depuração — não precisa ser repetido para o dia a dia.

Runbook para publicar `http://127.0.0.1:8000` (o backend, já rodando só em
loopback — ver [`TECHNICAL_DEBT.md`](TECHNICAL_DEBT.md), D6) em
**`https://elginprint.devribero.online`**, sem abrir a porta 8000 no roteador
nem no firewall do Windows. Escrito para ser seguido por alguém que não
acompanhou a decisão — inclusive você daqui a alguns meses.

Escopo: instalar o `cloudflared`, criar e rotear o túnel, subir como serviço
do Windows, e validar. O que preencher no `.env` depois que a Vercel tiver URL
está na seção 7; a arquitetura e o raciocínio por trás da escolha (por que
Tunnel e não VPN, por que não expor a porta) estão em
[`DEPLOYMENT_ARCHITECTURE.md`](DEPLOYMENT_ARCHITECTURE.md) e em
`ARCHITECTURE.md` (seção "Cloudflare Tunnel"/"FASE 5"). Este documento é o
passo a passo operacional; aqueles são o porquê.

**Pré-requisitos:**
- `devribero.online` já é um domínio gerenciado no Cloudflare (DNS já sob
  controle — dado como certo aqui, não é parte deste runbook).
- O backend já roda em `127.0.0.1:8000` (confirmado pelo fix do D6 — o bloco
  de execução direta não escuta mais em `0.0.0.0`).
- Acesso de Administrador na máquina Windows que hospeda o backend.
- Acesso ao painel do Cloudflare (conta com permissão sobre a zona
  `devribero.online`).

---

## 1. Instalar o `cloudflared`

Duas formas, qualquer uma serve:

```powershell
# Opcao A — winget (mais simples, se disponivel)
winget install --id Cloudflare.cloudflared

# Opcao B — instalador manual
# Baixe o .msi em https://github.com/cloudflare/cloudflared/releases
# (arquivo "cloudflared-windows-amd64.msi") e rode-o.
```

Verifique:

```powershell
cloudflared --version
```

Sem isso no PATH, feche e reabra o PowerShell antes de continuar — o
instalador às vezes exige uma sessão nova para o PATH atualizar.

---

## 2. Criar o túnel — caminho recomendado (via painel, com token)

Existem dois jeitos de criar um túnel: pela CLI (`cloudflared tunnel create`,
com `config.yml` e um arquivo de credenciais locais) ou pelo painel do
Cloudflare, que gera um **token** e não exige gerenciar arquivo de config à
mão. Para rodar como serviço do Windows, o caminho do token é mais simples —
o serviço sobe com um único comando, sem se preocupar com onde o `config.yml`
fica nem com qual usuário consegue lê-lo. É o caminho recomendado aqui; o
caminho por CLI está na seção 8, como alternativa.

1. No painel do Cloudflare, entre em **Zero Trust → Networks → Tunnels**
   (o menu pode aparecer como "Access → Tunnels" dependendo da versão do
   painel — se não achar em um lugar, procure no outro).
2. **Create a tunnel** → escolha o conector **Cloudflared** → dê um nome
   interno, por exemplo `printercontrol-api` (é só um rótulo; não precisa
   bater com o subdomínio).
3. O painel mostra um comando de instalação pronto para Windows, no formato:

   ```powershell
   cloudflared service install eyJhIjoiXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX...
   ```

   Esse token de longo prazo autentica o túnel — trate-o como segredo (mesma
   categoria de `SECRET_KEY`/`WEBHOOK_URL`: nunca commitar, nunca colar em
   chat ou issue pública). Copie o comando exato que o painel mostrar; o
   token muda a cada túnel criado.

4. **Como Administrador**, no PowerShell, rode o comando copiado. Isso já
   **instala e inicia** o serviço do Windows — não é preciso rodar
   `cloudflared service install` de novo depois; é a mesma etapa.

---

## 3. Apontar o hostname para o backend

Ainda na tela do túnel recém-criado, no painel:

1. Aba **Public Hostname** → **Add a public hostname**.
2. Preencha:
   - **Subdomain:** `elginprint`
   - **Domain:** `devribero.online`
   - **Path:** deixe vazio (a rota inteira vai para o backend)
   - **Type:** `HTTP`
   - **URL:** `127.0.0.1:8000`
3. Salvar.

Isso faz duas coisas ao mesmo tempo: cria a regra de roteamento do túnel
(`elginprint.devribero.online` → este `cloudflared` → `127.0.0.1:8000`) **e**
o registro DNS (`CNAME elginprint → <id-do-tunel>.cfargotunnel.com`,
proxied — nuvem laranja) na zona `devribero.online`. Não é preciso mexer na
aba de DNS separadamente.

**Por que `Type: HTTP` e não `HTTPS`:** o backend fala HTTP puro em
`127.0.0.1:8000` (D6 — a criptografia é responsabilidade do túnel, não do
backend). Configurar `HTTPS` aqui faria o `cloudflared` tentar um handshake
TLS contra uma porta que não fala TLS, e a rota falharia.

### Verificação — o registro DNS foi criado

Em **DNS → Records** da zona `devribero.online`, deve existir:

```
CNAME   elginprint   <id-do-tunel>.cfargotunnel.com   Proxied (nuvem laranja)
```

Se aparecer como "DNS only" (nuvem cinza), o túnel não vai funcionar — clique
no registro e ative o proxy. Isso não deveria acontecer no fluxo normal (o
painel já cria proxied), mas é o tipo de coisa que uma edição manual
posterior desfaz sem querer.

---

## 4. Validar antes de seguir

Da própria máquina Windows ou de qualquer outra com internet:

```powershell
curl.exe https://elginprint.devribero.online/health
```

Resposta esperada — o mesmo JSON que `GET /health` já devolve localmente:

```json
{
  "status": "ok",
  "version": "0.1.0",
  "environment": "demo",
  "is_demo": true,
  "is_production": false,
  "mock_collect_enabled": true,
  "print_server_mode": "mock",
  "uptime_seconds": 123.4,
  "database": "ok",
  "scheduler": { "enabled": true, "running": true, "next_run": "..." }
}
```

Se der timeout ou 502/530: veja a seção 9 (diagnóstico) antes de continuar
para os passos seguintes — não adianta mexer em CORS ou na Vercel com o túnel
ainda não respondendo.

Se der 200 mas com `status: "degraded"`: o túnel está funcionando, o
problema é outro (banco inacessível) — não é assunto deste documento, ver
`OPERATIONS.md` seção 4.

> ✅ Validado em 2026-08-24 — `200`, `status: "ok"`.

---

## 5. Confirmar que o serviço sobe sozinho

O comando da seção 2 já registrou o `cloudflared` como serviço do Windows
(equivalente ao que `cloudflared service install` faz sempre, com ou sem
token). Confirme:

```powershell
Get-Service -Name Cloudflared
```

Deve mostrar `Status: Running` e `StartType: Automatic`. Reinicie a máquina
uma vez, se puder, e repita o `curl.exe` da seção 4 — é a única forma real de
confirmar que ele sobe sozinho no boot, e não só "enquanto alguém lembrou de
rodar na mão".

> ✅ Serviço confirmado rodando (conector `DESKTOP-K7J9N5H`, Healthy no
> painel). ⬜ Teste de reboot ainda não confirmado — vale fazer na próxima
> janela de manutenção, não é bloqueante para seguir.

---

## 6. Cabeçalhos de segurança — no Cloudflare, não no backend

HSTS, `X-Content-Type-Options` e `X-Frame-Options` fazem mais sentido
configurados no Cloudflare do que no FastAPI, pela mesma razão do D6: o
backend nunca fala HTTPS — ele não tem como saber, de dentro do processo, se
quem está do outro lado do túnel chegou por HTTPS ou não, e HSTS
especificamente só faz sentido vindo de quem efetivamente terminou o TLS.
Configurar no painel também desacopla a política de segurança de um deploy
de código: liga/desliga sem tocar no backend.

### HSTS

**SSL/TLS → Edge Certificates**, na zona `devribero.online`:

- **Always Use HTTPS:** ligado (redireciona qualquer HTTP para HTTPS antes
  de chegar ao túnel).
- **HTTP Strict Transport Security (HSTS):** Enable → configure `max-age`
  (12 meses é um valor comum), `includeSubDomains` se `devribero.online` não
  tiver outros subdomínios em HTTP puro, e deixe `preload` desligado a menos
  que você entenda a implicação (submeter o domínio à lista de preload do
  Chrome é praticamente irreversível).

Não precisa mexer em **SSL/TLS → Overview** (modo Full/Full strict) para o
hostname do túnel: a conexão entre o Cloudflare e o `cloudflared` já usa o
protocolo do túnel, não uma conexão HTTPS comum contra um IP de origem — o
modo da zona importa para registros DNS apontando direto a um IP, não para
hostnames roteados por Tunnel.

### `X-Content-Type-Options` e `X-Frame-Options`

**Rules → Overview → Managed Transforms**, ligue **"Add security headers"**
— adiciona um conjunto padrão (inclui `X-Content-Type-Options: nosniff`) com
um clique, sem regra customizada.

Se precisar de `X-Frame-Options` com um valor específico (ou de algo que o
Managed Transform não cobre), use **Rules → Transform Rules → Modify
Response Header** e crie uma regra:

- **Se o hostname for** `elginprint.devribero.online`
- **Então adicione o cabeçalho** `X-Frame-Options: DENY`

Vale notar: esta API só devolve JSON, nunca HTML — `X-Frame-Options` protege
contra clickjacking de uma página renderizada, o que não existe aqui. É baixo
risco não configurar isso agora; `X-Content-Type-Options` (via Managed
Transform) é o que efetivamente vale a pena.

**Não adicione esses cabeçalhos no FastAPI.** Duplicar a mesma política nos
dois lugares (backend e Cloudflare) é como duplicar validação de CORS: os
dois podem divergir silenciosamente depois de um ajuste em só um lado, e aí
ninguém sabe qual vale.

---

## 7. CORS — o que falta até a Vercel existir (Fase 12)

`CORS_ORIGINS` no `.env` do backend continua **vazio** por enquanto — não há
o que colocar até o painel ter uma URL na Vercel. Isso é esperado nesta fase:

- Em `ENVIRONMENT=demo` (o valor atual do `.env` real), CORS vazio não
  impede o backend de subir — a validação estrita só existe para
  `ENVIRONMENT=production` (ver `app/config.py`, `_validate_production_cors`).
- Quando a Vercel tiver URL (Fase 12), preencha:

  ```env
  CORS_ORIGINS=https://SEU-APP.vercel.app
  ```

  Múltiplas origens (por exemplo, um domínio customizado além do
  `*.vercel.app` de preview) vão separadas por vírgula. O backend recusa
  subir em produção se essa variável estiver vazia, tiver `*`, `localhost`
  ou uma origem sem `https://` — ver `docs/OPERATIONS.md` seção 1.
- **Não é preciso reinstalar nem tocar no túnel** para esse ajuste — só
  editar o `.env` e reiniciar o processo do backend (`pwsh
  .\scripts\Servico-PrinterControl.ps1 -Acao parar` seguido de `-Acao
  iniciar`, ou a tarefa reinicia sozinha se você só matar o processo).

### `TRUST_PROXY_HEADERS` — ligar agora que o túnel existe

Antes desta fase, `TRUST_PROXY_HEADERS=false` era a única opção correta: sem
proxy na frente, confiar em `X-Forwarded-For` deixaria qualquer cliente
escolher seu próprio "IP" e furar o limite de tentativas de login. Com o
`cloudflared` como proxy de confiança na frente, isso muda — mas só troque
depois de validar a seção 4 (o túnel respondendo de verdade), e leia a nota
já presente em `.env.example` sobre o efeito colateral: atrás do túnel, todo
request chega com o mesmo IP de origem, e a contagem POR IP do rate-limit de
login vira, na prática, uma contagem quase global. Quem protege de verdade
nesse cenário é a contagem por conta (e-mail/username), que não depende
desta variável.

```env
TRUST_PROXY_HEADERS=true
```

---

## 8. Alternativa — túnel via CLI, com `config.yml` local

Só use este caminho se precisar versionar a configuração do túnel como
arquivo (por exemplo, gerenciar vários hostnames num só `config.yml`) — para
um único hostname, a seção 2 é mais simples e evita o problema de "onde o
serviço do Windows vai achar o `config.yml`".

```powershell
# Autentica e baixa cert.pem para %USERPROFILE%\.cloudflared\
cloudflared tunnel login

# Cria o tunel — gera um UUID e um arquivo de credenciais em
# %USERPROFILE%\.cloudflared\<UUID>.json
cloudflared tunnel create printercontrol-api
```

Crie `%USERPROFILE%\.cloudflared\config.yml`:

```yaml
tunnel: printercontrol-api
credentials-file: C:\Users\<usuario>\.cloudflared\<UUID>.json

ingress:
  - hostname: elginprint.devribero.online
    service: http://127.0.0.1:8000
  - service: http_status:404
```

A regra `http_status:404` no fim é obrigatória — sem um catch-all, qualquer
hostname não listado explicitamente derruba o túnel na inicialização.

```powershell
# Cria o CNAME proxied automaticamente
cloudflared tunnel route dns printercontrol-api elginprint.devribero.online

# Testa em primeiro plano ANTES de instalar como servico
cloudflared tunnel run printercontrol-api
```

Valide com o `curl.exe` da seção 4 enquanto ainda está rodando em primeiro
plano (`Ctrl+C` derruba o teste). Só depois disso, instale como serviço:

```powershell
cloudflared service install
```

**Atenção com o serviço:** ao contrário do caminho por token (seção 2), o
serviço criado assim roda como `LocalSystem`, que pode não enxergar o
`config.yml` no perfil do seu usuário. Se o serviço não subir ou não achar a
config, confirme onde o `cloudflared` está procurando (`cloudflared
tunnel run` mostra o caminho no início da saída) e, se necessário, copie
`config.yml` e o `.json` de credenciais para o caminho que o serviço usa —
normalmente sob `C:\Windows\System32\config\systemprofile\.cloudflared\` ou
`%ProgramData%\Cloudflare\`, mas isso varia por versão do `cloudflared`;
verifique o caminho real em vez de assumir um dos dois.

**Nunca commite** o `config.yml` com o caminho de credenciais nem o arquivo
`<UUID>.json` no repositório — mesma regra do `SECRET_KEY`/`WEBHOOK_URL`.

---

## 9. Diagnóstico

| Sintoma | Onde olhar |
|---|---|
| `curl` para `/health` dá timeout | `Get-Service Cloudflared` — se não estiver `Running`, o problema é o serviço, não o backend nem o DNS. |
| `curl` dá 502/530 | Túnel de pé, mas não alcança `127.0.0.1:8000` — confirme que o backend está rodando (`pwsh .\scripts\Servico-PrinterControl.ps1 -Acao status`) e que a porta/URL no Public Hostname está certa. |
| `curl` dá 1016/1033 (erro do Cloudflare) | Geralmente DNS apontando para o túnel errado, ou registro "DNS only" em vez de "Proxied" — ver seção 3. |
| Serviço não inicia | Visualizador de Eventos → Logs do Windows → Aplicativo, procure pela origem `cloudflared`. Alternativa: pare o serviço (`Stop-Service Cloudflared`) e rode `cloudflared tunnel run` (ou o comando com token) em primeiro plano para ver o erro direto no console. |
| Túnel sobe mas hostname não responde | No painel, **Zero Trust → Networks → Tunnels → (seu túnel) → Public Hostname**, confirme que a rota existe e aponta para `127.0.0.1:8000`, não para outro host/porta. |

Desinstalar/recriar do zero, se precisar:

```powershell
cloudflared service uninstall
```

Isso remove o serviço do Windows; o túnel em si (e o registro DNS) continuam
existindo no painel até serem apagados por lá.

---

## 10. Resumo do que muda em cada lugar

| Onde | O que | Quando | Status |
|---|---|---|---|
| Máquina Windows | `cloudflared` instalado e rodando como serviço | Seções 1–2, 5 | ✅ feito (`DESKTOP-K7J9N5H`) |
| Painel Cloudflare | Túnel criado, Public Hostname `elginprint.devribero.online → 127.0.0.1:8000` | Seções 2–3 | ✅ feito (`Elgin - Impressoras`, Healthy) |
| Painel Cloudflare | HSTS ligado, cabeçalhos de segurança via Managed Transform | Seção 6 | ⬜ não confirmado — revisar antes de considerar isso fechado de vez |
| `backend/.env` | `TRUST_PROXY_HEADERS=true` | Seção 7, depois de validar | ✅ feito |
| `backend/.env` | `CORS_ORIGINS=https://SEU-APP.vercel.app` | Fase 12, quando a URL existir | ⬜ aguardando Fase 12 |

Nada disso exige alterar código do backend — só configuração de painel e de
`.env`. Nenhum arquivo de credenciais do túnel deve ir para o repositório.
