# Deploy do Frontend na Vercel (Fase 12)

> **✅ Fase 12 concluída em 2026-08-24.** URL de produção:
> **`https://printercontrol.vercel.app`**, falando com a API através do
> Cloudflare Tunnel, CORS validado ao vivo.
>
> | | |
> |---|---|
> | **URL de produção** | `https://printercontrol.vercel.app` |
> | **`NEXT_PUBLIC_API_URL`** (Vercel) | `https://elginprint.devribero.online` |
> | **`CORS_ORIGINS`** (`backend/.env`) | `https://printercontrol.vercel.app` — ✅ escrito e ativo |
> | **Backend reiniciado com a nova config** | ✅ feito (reinício manual — ver nota abaixo) |
> | **CORS validado ao vivo** (Vercel → API) | ✅ confirmado — `GET /health` e o preflight `OPTIONS /api/auth/login` respondem com `access-control-allow-origin: https://printercontrol.vercel.app` |
>
> **O que aconteceu entre preparar isto e confirmar:** a sessão que editou o
> `.env` não rodava como Administrador na máquina Windows e não conseguiu
> localizar nem sinalizar o processo real da porta 8000 para reiniciá-lo (um
> `fastapi dev main.py` avulso e sem relação foi encontrado e encerrado
> durante a investigação, sem efeito no serviço real). Quem tem acesso à
> máquina reiniciou o backend manualmente — no meio do caminho o processo
> chegou a cair sem log de encerramento limpo (provavelmente por ter sido
> iniciado num terminal comum, não como serviço) e um segundo reinício foi
> necessário. Com o backend de fato no ar, o CORS foi confirmado por fora,
> com uma requisição real carregando `Origin: https://printercontrol.vercel.app`
> contra `https://elginprint.devribero.online` — não é um teste local, é o
> mesmo caminho que o navegador de um usuário percorre.
>
> **Consideração para não repetir isso:** o backend ainda não está instalado
> como tarefa agendada (`OPERATIONS.md` seção 2) — rodando num terminal
> comum, uma queda de energia, logoff ou fechamento acidental da janela
> derruba a API sem ninguém perceber até alguém tentar usá-la. Vale
> considerar `pwsh .\scripts\Servico-PrinterControl.ps1 -Acao instalar`
> numa próxima janela de manutenção.

Passo a passo para publicar o painel Next.js na Vercel, usando o domínio
padrão (`*.vercel.app` — domínio customizado fica para uma fase futura) e
apontando para o backend já publicado pelo Cloudflare Tunnel
(`https://elginprint.devribero.online`, ver
[`CLOUDFLARE_TUNNEL.md`](CLOUDFLARE_TUNNEL.md)).

Escrito para ser seguido por alguém que não acompanhou a decisão. O deploy em
si exige login interativo na Vercel — ninguém além de quem tem a conta
consegue seguir os passos 2–4; o resto (variáveis, validação, CORS,
redeploys) vale para qualquer pessoa que precisar mexer nisso depois.

**Pré-requisitos:**
- Conta na Vercel com acesso para importar de
  `github.com/devribero/PrinterControl`.
- O Cloudflare Tunnel já ativo e validado (Fase 11 — se
  `https://elginprint.devribero.online/health` não responder, resolva isso
  primeiro; o frontend sem API não tem o que mostrar além do modo
  demonstração).

---

## 1. O projeto já está pronto para este deploy

Não há nada para ajustar no código antes de publicar — checado nesta fase:

- **`next.config.ts` está vazio** (`{}`). Nenhum `output`, `basePath` ou
  `rewrites` que exigisse configuração extra na Vercel.
- **`package.json` está na raiz do repositório**, junto de `backend/`. A
  Vercel detecta Next.js automaticamente na raiz — não é preciso configurar
  "Root Directory" no painel (a Vercel simplesmente ignora `backend/`, que
  não tem nada que pareça um projeto Next.js/Node para ela).
- **Uma única variável de ambiente:** `NEXT_PUBLIC_API_URL`
  (`src/lib/api.ts`). É a única forma pela qual o frontend sabe onde fica a
  API; sem ela, cai no fallback `http://127.0.0.1:8000`, que só funciona
  rodando localmente.
- **Nenhum outro hardcode de URL de desenvolvimento.** Os únicos `http://`
  fora de `api.ts` são os links "abrir página da impressora"
  (`PrinterTable.tsx`, `PrinterDetailsModal.tsx`), que apontam para o IP de
  cada impressora na rede — não têm relação com onde o painel está
  hospedado.
- **`public/data/*.json` não existe no repositório** (gitignorado de
  propósito — são dados gerados localmente por
  `scripts/Relatorio-Mensal.ps1`). Isso é esperado: `fetchMonthlyReport.ts`
  já trata a ausência desse arquivo (404) como sinal para cair no próximo
  nível de fallback. Não é um erro a corrigir antes do deploy — é o
  comportamento pretendido rodando fora da rede da empresa.
- **Build local validado** com a variável de produção:
  `NEXT_PUBLIC_API_URL=https://elginprint.devribero.online npm run build`
  compila e gera as 13 rotas estáticas sem erro.

---

## 2. Variáveis de ambiente para configurar na Vercel

Só uma:

| Variável | Valor | Ambientes |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `https://elginprint.devribero.online` | Production, Preview **e** Development |

**Por que nos três ambientes, e não só Production:** deploys de preview (de
uma branch ou PR) usam a mesma variável. Sem ela configurada ali, um preview
cairia no fallback local (`127.0.0.1:8000`) — inacessível para quem abrir o
link do preview num navegador que não seja o da própria máquina de
desenvolvimento. Como só existe um backend (não há um ambiente de staging
separado), aponta-se o mesmo endereço nos três.

**Sem barra no final:** `https://elginprint.devribero.online`, não
`https://elginprint.devribero.online/`. `api.ts` já remove uma barra final se
houver (`.replace(/\/$/, "")`), mas evite depender disso.

**Não é segredo:** o valor é enviado ao navegador de qualquer visitante (é o
que o prefixo `NEXT_PUBLIC_` significa) — não há problema em vê-lo em texto
claro no painel da Vercel, nos logs de build, ou no próprio bundle
publicado.

---

## 3. Conectar o repositório e fazer o primeiro deploy

1. Em [vercel.com](https://vercel.com), **Add New… → Project**.
2. **Import Git Repository** → selecione `devribero/PrinterControl` (se não
   aparecer na lista, autorize a Vercel a acessar o repositório pela
   configuração de integração do GitHub primeiro).
3. A Vercel deve detectar **Framework Preset: Next.js** e **Root Directory:
   `.`** automaticamente — não altere nenhum dos dois.
4. Em **Environment Variables**, adicione a variável da seção 2:
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `https://elginprint.devribero.online`
   - Marque os três ambientes (Production, Preview, Development).
5. **Deploy.** O build roda `npm install` + `next build` (os mesmos comandos
   validados na seção 1) — leva menos de dois minutos para um projeto deste
   tamanho.

Ao terminar, a Vercel mostra a URL de produção, no formato
`https://<nome-do-projeto>.vercel.app` (o nome exato depende do que a Vercel
sugerir ou de como o projeto for renomeado na criação). **Anote essa URL —
ela é o valor exato que entra no `CORS_ORIGINS` do backend na seção 5.**

---

## 4. Validar

Abra a URL de produção no navegador.

**Esperado, sem CORS configurado ainda:** a tela de login aparece
normalmente (ela não depende da API), mas ao tentar entrar, a requisição
para `https://elginprint.devribero.online/api/auth/login` falha — o console
do navegador mostra um erro de CORS (`No 'Access-Control-Allow-Origin'
header...`), não um erro de rede. **Isso é esperado neste ponto e confirma
que o frontend está de fato tentando falar com o backend certo** — o próximo
passo (seção 5) resolve exatamente isso.

Se em vez de erro de CORS aparecer timeout, erro de DNS, ou "Failed to
fetch" genérico: confira primeiro se `https://elginprint.devribero.online/health`
responde por fora (Fase 11) antes de suspeitar do frontend.

Se a página nem carregar (tela em branco, erro 404/500 da própria Vercel):
veja os **Build Logs** no painel — normalmente indicam exatamente qual
etapa falhou. Como o build foi validado localmente na seção 1, uma falha
aqui tende a ser de variável de ambiente ausente ou de versão do Node.js
(a Vercel usa a versão padrão dela salvo indicação contrária; se algo depender
de uma versão específica, defina em **Project Settings → General → Node.js
Version**, ou adicione `"engines": {"node": ">=20"}` em `package.json`).

> ✅ Confirmado em 2026-08-24: `https://printercontrol.vercel.app` está no
> ar. O erro de CORS descrito acima foi exatamente o observado antes da
> seção 5 ser concluída — depois do reinício do backend, o erro desapareceu
> (ver confirmação ao vivo na seção 5).

---

## 5. Depois do deploy — atualizar o CORS do backend

**Único passo que não dá para fazer antes do primeiro deploy**, porque
depende de uma informação que só existe depois dele: a URL exata que a
Vercel atribuiu ao projeto.

No `backend/.env` (na máquina Windows, **não** neste repositório — arquivo
gitignorado, nunca commitado):

```env
CORS_ORIGINS=https://<nome-do-projeto>.vercel.app
```

Use a URL de **Production** anotada na seção 3 — não uma URL de deploy
específico (as que têm hash/branch no meio, tipo
`printer-control-git-main-devribero.vercel.app` ou
`printer-control-abc123.vercel.app`). A de Production é estável entre
deploys; as outras mudam a cada novo commit/branch.

**Domínios de preview não vão funcionar contra a API por enquanto** — cada
preview deploy tem uma URL própria, e listar todas elas no `CORS_ORIGINS`
não escala. Para este projeto, com um backend único e sem ambiente de
staging separado, isso é aceitável: previews servem para revisar a
interface, não para testar contra dados reais. Se isso virar necessário,
a alternativa é normalizar sufixo por padrão de URL — fora do escopo desta
fase.

Depois de editar o `.env`, reinicie o processo do backend para a mudança
valer:

```powershell
pwsh .\scripts\Servico-PrinterControl.ps1 -Acao parar
pwsh .\scripts\Servico-PrinterControl.ps1 -Acao iniciar
```

> ⚠️ **Isso pressupõe o backend instalado como tarefa agendada** (o caminho
> documentado em `OPERATIONS.md`). Em 2026-08-24, ao tentar confirmar esse
> passo, `Get-ScheduledTask -TaskName "PrinterControl*"` não encontrou
> nenhuma tarefa instalada — o processo real rodava num terminal comum, não
> como serviço. **Isso se confirmou na prática**: no reinício desta fase, o
> processo chegou a cair sem log de encerramento limpo no meio do caminho, e
> foi preciso subir de novo manualmente uma segunda vez até o `/health`
> responder de novo. Considere instalar a tarefa agendada oficial
> (`-Acao instalar`, `OPERATIONS.md` seção 2) para este tipo de fragilidade
> não se repetir.

**Verificação:** volte à URL da Vercel e tente logar de novo. O erro de CORS
da seção 4 deve ter desaparecido — login, `/api/auth/me` e o resto do painel
devem funcionar através do domínio público. Confirmado também por fora, sem
navegador, em 2026-08-24:

```
$ curl -i -H "Origin: https://printercontrol.vercel.app" https://elginprint.devribero.online/health
HTTP/1.1 200 OK
access-control-allow-origin: https://printercontrol.vercel.app
vary: Origin
Strict-Transport-Security: max-age=15552000
...
```

E o preflight que o navegador dispara antes de um `POST /api/auth/login`
(corpo JSON, então exige `OPTIONS` primeiro):

```
$ curl -i -X OPTIONS https://elginprint.devribero.online/api/auth/login \
    -H "Origin: https://printercontrol.vercel.app" \
    -H "Access-Control-Request-Method: POST" \
    -H "Access-Control-Request-Headers: content-type"
HTTP/1.1 200 OK
access-control-allow-methods: GET, POST, PATCH, OPTIONS
access-control-allow-headers: Accept, Accept-Language, Authorization, Content-Language, Content-Type
access-control-allow-origin: https://printercontrol.vercel.app
```

Os dois confirmam: não é só o `GET /health` público que funciona — o login
de verdade (POST com corpo JSON) também passa pelo preflight sem erro.

Nada disso exige um novo deploy do frontend — é só configuração do backend.

---

## 6. Redeploy — quando o código mudar

A Vercel já está conectada ao GitHub, então o caminho normal é automático:

```
git push origin main
```

Todo push em `main` dispara um novo deploy de **produção** automaticamente
(a Vercel mostra o progresso e o resultado direto na aba **Deployments**).
Push em qualquer outra branch, ou abrir um Pull Request, gera um deploy de
**preview** — útil para revisar antes de mesclar, mas lembrando da limitação
de CORS da seção 5 (preview não fala com a API real).

**Redeploy manual, sem novo commit** (por exemplo, depois de mudar uma
variável de ambiente na Vercel — variáveis de ambiente só valem a partir do
**próximo** build, nunca retroagem a um deploy já feito):

1. Painel da Vercel → **Deployments**.
2. No deploy mais recente de Production → menu **⋯** → **Redeploy**.

**Rollback**, se um deploy quebrar algo: mesmo menu **⋯** num deploy
anterior que funcionava → **Promote to Production** — instantâneo, não
precisa reverter commit nem esperar um novo build.

---

## 7. Resumo — Fase 12 concluída

| Item | Onde | Status |
|---|---|---|
| Criar o projeto na Vercel e configurar `NEXT_PUBLIC_API_URL` | Painel da Vercel | ✅ feito — `https://printercontrol.vercel.app` |
| Primeiro deploy | Painel da Vercel | ✅ feito |
| Anotar a URL de Production | Painel da Vercel | ✅ feito |
| `CORS_ORIGINS` no `backend/.env` | Máquina Windows | ✅ feito |
| Reiniciar o backend para carregar o `.env` novo | Máquina Windows | ✅ feito (manual — dois reinícios, ver seção 5) |
| Validar CORS ao vivo (`Access-Control-Allow-Origin` na resposta) | — | ✅ confirmado — `GET /health` e preflight `OPTIONS /api/auth/login` |
| HSTS com `max-age` correto (Fase 11) | Painel Cloudflare | ✅ corrigido para 6 meses (estava `max-age=0`, que na prática desliga o HSTS) |

Nada disso exigiu alterar código deste repositório. Único item que ficou
como sugestão para uma próxima janela de manutenção: instalar o backend
como tarefa agendada (ver nota da seção 5) — hoje ele roda num terminal
comum e não sobrevive a uma queda sozinho.
