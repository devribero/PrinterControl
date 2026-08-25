# Contexto de desenvolvimento — PrinterControl

Resumo do que existe hoje, para qualquer pessoa (ou sessão de IA) que continue
o projeto sem ter acompanhado o histórico.

> **Atualizado em 24/08/2026.** Este arquivo estava severamente desatualizado:
> descrevia o projeto como "frontend puro Vite + React, sem backend", com
> "login fake" e "sem banco de dados". Nada disso é verdade desde a Fase 1.
> Se você leu a versão antiga, esqueça-a.

**Comece por [`docs/VISAO_GERAL.md`](docs/VISAO_GERAL.md)** — é a visão
completa do sistema, escrita em linguagem acessível.

---

## O que é o projeto

Sistema de monitoramento da frota de impressoras: status
(online/offline/atenção), níveis de toner por canal, alertas, contadores
mensais de páginas e histórico por unidade/departamento.

**Duas peças:**

- **Backend** — FastAPI (Python) + SQLite + SQLModel + APScheduler. Roda numa
  máquina Windows dentro da rede da empresa. Fala com os Print Servers via
  PowerShell (`Get-Printer`/`Get-PrinterPort`) e com as impressoras via SNMP.
- **Frontend** — Next.js 16 + React 19 + TypeScript, CSS Modules, Recharts,
  Lucide. Hospedado na Vercel. Não guarda dado nenhum: consome a API.

A ponte entre os dois, em produção, será um **Cloudflare Tunnel** — passo a
passo documentado em `docs/CLOUDFLARE_TUNNEL.md`, ainda não executado na
máquina real.

---

## Os três ambientes

Controlados por `ENVIRONMENT` no `backend/.env`:

| Ambiente | Simulação | Comportamento |
|---|---|---|
| `development` | liberada | Padrão da máquina de quem desenvolve |
| `demo` | esperada | Faixa permanente "dados de demonstração" no painel |
| `production` | **proibida** | O backend **recusa subir** com configuração simulada |

O painel descobre o ambiente perguntando ao backend (`GET /health`), e não por
uma variável do build — a variável descreveria o bundle, não o servidor a que
ele acabou se conectando.

**Não confundir com o fallback do frontend:** quando o backend não responde, o
painel exibe o conjunto de demonstração de `src/data/` com faixa de aviso, em
vez de uma tela vazia. Isso é independente do `ENVIRONMENT` do backend.

---

## O que existe hoje

**Backend** — autenticação JWT com três papéis (viewer/operator/admin), gestão
de usuários, cadastro de impressoras, descoberta e sincronização de múltiplos
Print Servers, coleta SNMP manual e agendada, motor de alertas com
deduplicação e resolução automática, webhook para Teams, notificações
internas, perfil e troca de senha, `/health` com diagnóstico, logs em arquivo
com redação de segredos, backup online do SQLite, e instalação como tarefa
agendada do Windows.

**Frontend** — Dashboard, Impressoras, Suprimentos (toner), Alertas,
Relatórios, Histórico, Mapeamento de Rede, e as telas administrativas
(Usuários, Notificações, Integrações, Configurações). Tema claro/escuro,
preferências de acessibilidade, badges de dados de demonstração, diálogos de
confirmação para as operações destrutivas.

O inventário completo, tela a tela e com quem pode o quê, está na seção 3 de
[`docs/VISAO_GERAL.md`](docs/VISAO_GERAL.md).

---

## Dívida técnica

**Está toda em [`docs/TECHNICAL_DEBT.md`](docs/TECHNICAL_DEBT.md) (D1–D13).**
Não mantenha uma segunda lista aqui — foi exatamente assim que este arquivo
passou meses afirmando que o projeto não tinha backend.

As armadilhas que mais custam tempo a quem chega agora:

- **D1** — não ligue `PRAGMA foreign_keys=ON`. Derruba toda a coleta.
- **D6** — `python app/main.py` sobe em `0.0.0.0` com reload. Em produção use
  `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`.
- **D8/D9** — `tests_fleet.py` e `tests_printers_crud.py` falham por
  esperarem 73 impressoras (o banco tem 79); `tests_collect_api.py` não roda
  por falta de `requests`. **Não são regressões suas.**

---

## Coisas que já não são verdade (e constavam aqui)

| Dizia | É |
|---|---|
| "Frontend puro Vite + React, sem backend" | Next.js 16 + FastAPI + SQLite |
| "Dados vêm de JSON estático em `public/data/`" | Vêm da API; JSON estático é só fallback |
| "Login não é autenticação real, contas em `src/data/accounts.ts`" | JWT real, contas no banco, três papéis, argon2 |
| "Sem backend/banco — fica para conversa futura" | Feito desde a Fase 1 |
| "`SECRET_KEY` padrão não é apropriado para produção" | Produção **recusa subir** com ela |
| "CORS é apenas local" | Por ambiente, com validação de produção |
| "Push para o GitHub bloqueado (403); fluxo é entregar `.zip`" | Push funciona; o fluxo é commit local + push |

Os scripts PowerShell da era anterior ao backend (`Coletar-Impressoras.ps1`,
`Relatorio-Mensal.ps1`, `Simular-Ambiente.ps1`) foram removidos de
`scripts/` — a coleta SNMP, o relatório mensal e o modo demonstração são
todos feitos pelo backend Python hoje. `Servico-PrinterControl.ps1` é o
único que resta ali, é atual e faz parte do deploy.

---

## Como continuar

**Frontend** (da raiz):

```powershell
npm run dev      # desenvolver
npm run lint     # oxlint
npm run build    # validar antes de qualquer entrega
```

**Backend** (de dentro de `backend/`):

```powershell
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload   # desenvolver
.\venv\Scripts\python.exe tests_environment.py               # uma suíte
.\venv\Scripts\python.exe seed.py                            # semear o banco
```

O venv é gerenciado por `uv`; para instalar dependências:
`uv pip install --python venv/Scripts/python.exe -r requirements.txt`

**Depois de mexer no código**, rode `graphify update .` para manter o grafo de
conhecimento em `graphify-out/` atualizado.

---

## Documentação

| Arquivo | Para quê |
|---|---|
| [`docs/VISAO_GERAL.md`](docs/VISAO_GERAL.md) | **Comece aqui.** Visão completa, em linguagem acessível. |
| [`docs/TECHNICAL_DEBT.md`](docs/TECHNICAL_DEBT.md) | Registro único da dívida técnica. |
| [`docs/OPERATIONS.md`](docs/OPERATIONS.md) | Runbook de produção. |
| [`docs/DEVELOPER_GUIDE.md`](docs/DEVELOPER_GUIDE.md) | Para mexer no código. |
| [`docs/API_MAP.md`](docs/API_MAP.md) | Todas as rotas. |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Arquitetura em detalhe. |
| [`docs/DATA_FLOW.md`](docs/DATA_FLOW.md) | Caminho do dado, da impressora ao painel. |
| [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) | Uso do painel. |
| [`docs/FEATURE_MATRIX.md`](docs/FEATURE_MATRIX.md) | O que é funcional e o que é maquete. |
| [`docs/DEPLOYMENT_ARCHITECTURE.md`](docs/DEPLOYMENT_ARCHITECTURE.md) | Plano de exposição externa. |
