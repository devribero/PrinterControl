# Migração: Cloudflare Tunnel + Vercel → VM Windows Server própria

Status: planejado, não implementado (sem acesso à VM ainda).

## Contexto

Hoje: backend exposto via Cloudflare Tunnel (`elginprint.devribero.online`,
ativo desde 2026-08-24) e frontend na Vercel. Decisão: parar de depender de
qualquer coisa "estilo Cloudflare" e hospedar tudo (frontend + backend) numa
VM Windows Server própria.

## Decisão central

**Caddy** como reverse proxy + TLS, na frente dos dois serviços. Provisiona e
renova certificado Let's Encrypt sozinho, sem configuração manual — substitui
o que o Cloudflare Tunnel fazia.

## Domínio

`devribero.online` sai do Cloudflare Tunnel; a `A record` passa a apontar
direto pro IP público da VM. Dois subdomínios:

- `app.devribero.online` → frontend (porta 3000, local)
- `api.devribero.online` → backend (porta 8000, local)

## Backend

Sem mudança de código. Continua `uvicorn app.main:app --host 127.0.0.1 --port 8000`,
gerenciado por `scripts/Servico-PrinterControl.ps1` (Task Scheduler,
reinício automático) — já existe, reaproveita 100%.

`CORS_ORIGINS` no `.env` de produção passa a ser `https://app.devribero.online`
(hoje aponta pro domínio da Vercel).

## Frontend

Sai da Vercel. Roda `npm run build` uma vez, depois `npm run start` (servidor
Next.js próprio) como processo persistente na VM.

**Novo**: `scripts/Servico-Frontend.ps1`, mesmo padrão do script do backend —
Task Scheduler, sobe no boot, reinicia em falha. Porta 3000, `127.0.0.1`
apenas (Caddy é quem expõe pra fora).

`NEXT_PUBLIC_API_URL` no build de produção passa a ser
`https://api.devribero.online` (hoje aponta pro domínio do Cloudflare Tunnel).

## Caddy no Windows Server

Binário único, mais uma tarefa agendada (mesmo mecanismo dos outros dois
serviços). `Caddyfile` com duas entradas — uma por subdomínio, cada uma
fazendo proxy pra sua porta local. TLS automático, sem passo manual.

## Firewall do Windows Server

Abrir entrada 80/443 (Caddy). Portas 3000 e 8000 continuam só em
`127.0.0.1` — mesma postura de segurança que já existe hoje pro backend.

## Atenção pré-existente (não é novidade desta migração)

Se o Print Server real exigir RPC/PowerShell (não só SNMP), a tarefa do
backend precisa rodar com conta de domínio, não SYSTEM — já documentado no
cabeçalho de `Servico-PrinterControl.ps1` ("CONTA DE EXECUÇÃO — LEIA ANTES
DE INSTALAR").

## Corte (baixo risco, com fallback)

1. Provisionar a VM: Windows Server, Python (venv do projeto), Node.js LTS,
   Caddy.
2. Subir os dois serviços, confirmar respondendo em `localhost` na própria VM.
3. Configurar Caddy com um subdomínio de rascunho primeiro (não o de
   produção), confirmar HTTPS funcionando de fora.
4. Só então trocar a `A record` de produção pro IP da VM.
5. Desligar `cloudflared` e o projeto na Vercel depois de alguns dias
   estável.
6. Atualizar `docs/OPERATIONS.md`, substituindo a seção de Cloudflare/Vercel
   por esta.

## Não incluído neste spec (fora de escopo até a VM existir)

- Provisionamento exato da VM (tamanho, região) — depende do provedor que
  for escolhido quando a VM existir.
- Conteúdo real do `Caddyfile` e do `Servico-Frontend.ps1` — serão escritos
  no momento da implementação, contra a VM de verdade (evita gerar código
  não testável agora).
