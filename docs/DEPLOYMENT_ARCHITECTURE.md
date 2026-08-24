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
5. Configurar Tunnel para uma rota de teste protegida — passo a passo em
   [`CLOUDFLARE_TUNNEL.md`](CLOUDFLARE_TUNNEL.md) (Fase 11; documentado,
   pendente de execução na máquina real).
6. Configurar `NEXT_PUBLIC_API_URL` na Vercel.
7. Adicionar CORS da origem da Vercel.
8. Validar JWT e discovery por HTTPS.
9. Só depois avaliar coleta agendada e sincronização permanente.

## Bloqueios atuais

- O passo a passo de Cloudflare Tunnel está documentado
  ([`CLOUDFLARE_TUNNEL.md`](CLOUDFLARE_TUNNEL.md), Fase 11), mas ainda não
  foi executado na máquina real — `elginprint.devribero.online` não responde
  até alguém seguir aquele runbook.
- O CORS não contém a origem da Vercel (aguardando a Fase 12; ver seção
  "CORS" de `CLOUDFLARE_TUNNEL.md`).
- A URL da API ainda tem fallback local.
- O backend possui segredo JWT padrão inseguro.
- `Main.ps1` contém URL de webhook embutida no legado.
- O endpoint de resolução de alertas não exige JWT.
- O frontend ainda pode exibir fallback demo sem deixar a aplicação vazia.
