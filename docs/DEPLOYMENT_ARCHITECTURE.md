# Arquitetura de Deploy

## Estado atual

O frontend usa `NEXT_PUBLIC_API_URL`, com fallback para:

```text
http://127.0.0.1:8000
```

O backend aceita CORS para:

```text
http://localhost:3000
http://localhost:3001
http://127.0.0.1:3000
```

Não há proxy/rewrite no Next.js.

## Arquitetura avaliada

```text
Vercel / Next.js
    | HTTPS
    v
Cloudflare Tunnel
    | conexão de saída da máquina corporativa
    v
FastAPI
    |------------------|
    v                  v
SQLite             Rede corporativa
                         |-------------|
                         v             v
                    Print Server     SNMP
```

A Vercel não acessaria diretamente o Print Server, as impressoras ou o SQLite. O FastAPI seria o único serviço publicado pelo Tunnel.

## Cloudflare Tunnel

A máquina dentro da rede corporativa executaria o conector do Cloudflare Tunnel, que estabeleceria uma conexão de saída. O serviço público encaminharia para o FastAPI local.

A arquitetura não requer:

- port forwarding;
- porta 8000 exposta na Internet;
- abertura de porta no roteador;
- acesso VPN do navegador frontend;
- publicação direta do Print Server.

O Tunnel não elimina as permissões internas necessárias para:

- RPC/PowerShell até `elgjunprt`;
- DNS do Print Server;
- ping às impressoras;
- UDP/161 até as impressoras.

## Configuração de aplicação

Frontend:

```text
NEXT_PUBLIC_API_URL=https://api.exemplo.tld
```

Backend já possui configurações para:

```text
SECRET_KEY
DATABASE_URL
SNMP_COMMUNITY
SNMP_TIMEOUT
SNMP_RETRIES
COLLECTION_ENABLED
COLLECTION_INTERVAL_MINUTES
COLLECTION_MODE
PRINT_SERVER_MODE
PRINT_SERVER_HOST
PRINT_SERVER_TIMEOUT_SECONDS
WEBHOOK_URL
WEBHOOK_TIMEOUT_SECONDS
```

Para a primeira versão de discovery, recomenda-se:

```text
COLLECTION_ENABLED=false
ALLOW_MOCK_COLLECT=false
PRINT_SERVER_MODE=real
```

O scheduler e a descoberta manual devem continuar sendo operações separadas.

## CORS

Será necessário adicionar ao backend as origens HTTPS reais do frontend, por exemplo:

```text
https://app.exemplo.vercel.app
https://painel.exemplo.com
```

A lista deve ser explícita. Não se deve usar `*` com intenção de resolver o problema rapidamente.

`allow_credentials` atualmente é `false`, compatível com JWT no header Authorization e sem cookies.

## Autenticação

Fluxo atual:

```text
POST /api/auth/login
    ↓
JWT
    ↓
Authorization: Bearer <token>
    ↓
FastAPI / require_user
```

Antes da exposição pública, devem ser revisados:

- segredo JWT;
- expiração;
- proteção de todas as rotas mutáveis;
- rotas GET públicas;
- documentação OpenAPI;
- ausência de refresh token;
- política de contas e permissões.

## SQLite no cenário

O SQLite pode permanecer junto do FastAPI em um primeiro deploy controlado. Não deve ser colocado atrás do Tunnel como arquivo acessível ao frontend.

Riscos:

- dependência da disponibilidade de uma única máquina;
- backup manual;
- bloqueios de escrita;
- concorrência entre scheduler e requisições;
- incompatibilidade com múltiplas réplicas da API;
- risco de migração executada durante operação.

Se o sistema crescer ou precisar de alta disponibilidade, PostgreSQL seria uma evolução futura, não parte desta etapa.

## Sequência de implantação futura

1. Validar frontend e backend localmente.
2. Validar discovery com mocks e sem escrita.
3. Validar Print Server real dentro da rede.
4. Validar SNMP real dentro da rede.
5. ✅ Configurar Tunnel para uma rota de teste protegida — feito na Fase 11
   ([`CLOUDFLARE_TUNNEL.md`](CLOUDFLARE_TUNNEL.md));
   `elginprint.devribero.online` está no ar e validado.
6. Configurar `NEXT_PUBLIC_API_URL` na Vercel — passo a passo em
   [`VERCEL_DEPLOY.md`](VERCEL_DEPLOY.md) (Fase 12; documentado, pendente de
   execução — exige login interativo na Vercel).
7. Adicionar CORS da origem da Vercel — só é possível depois do passo 6 (a
   URL só existe após o primeiro deploy); ver seção 5 de `VERCEL_DEPLOY.md`.
8. Validar JWT e discovery por HTTPS.
9. Só depois avaliar coleta agendada e sincronização permanente.

## Bloqueios atuais

- O passo a passo de deploy na Vercel está documentado
  ([`VERCEL_DEPLOY.md`](VERCEL_DEPLOY.md), Fase 12), mas ainda não foi
  executado — exige login interativo na conta da Vercel.
- O CORS não contém a origem da Vercel (depende do item acima).
- A URL da API ainda tem fallback local (`127.0.0.1:8000`, só usado quando
  `NEXT_PUBLIC_API_URL` não está definida — ver `VERCEL_DEPLOY.md` seção 1).
- O backend possui segredo JWT padrão inseguro.
- `Main.ps1` contém URL de webhook embutida no legado.
- O endpoint de resolução de alertas não exige JWT.
- O frontend ainda pode exibir fallback demo sem deixar a aplicação vazia.
