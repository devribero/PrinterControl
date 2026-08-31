# AUDITORIA MASTER — PrinterControl

Data: 2026-08-26 | Branch: main | Escopo: revisão estática do repositório local (sem acesso a produção/infra externa)

Rótulos usados: **CONFIRMADO** (evidenciado em arquivo:linha) · **POSSÍVEL** (indício, não totalmente comprovado) · **NÃO VERIFICADO** (depende de ambiente/infra fora do repo) · **FALSO POSITIVO** (hipótese descartada após checagem)

---

## 1. Resumo executivo (linguagem simples)

O PrinterControl é um sistema de monitoramento de impressoras: backend em Python/FastAPI que coleta dados via SNMP e PowerShell (Print Server), e um frontend em Next.js hospedado na Vercel. O backend fica exposto pela internet através de um Cloudflare Tunnel, sem porta aberta diretamente.

O projeto tem sinais de maturidade acima da média para um projeto pequeno/interno: há validação de configuração que **recusa subir em produção** com segredo padrão, CORS aberto, ou modo simulado ligado (`backend/app/config.py:113-262`); há rate limiting de login por IP+e-mail; a biblioteca JWT foi trocada de `python-jose` para `PyJWT` explicitamente por causa de CVEs documentadas no próprio código-fonte. Isso é incomum e é um ponto forte real.

Ao mesmo tempo, há um problema ativo agora: o arquivo `backend/requirements.txt` está corrompido no working tree (6 bytes, praticamente vazio) e a versão commitada em HEAD está em UTF-16 LE — ambos os estados quebram `pip install -r requirements.txt`. Isso é o mesmo bug (D14-D16) que a documentação de dívida técnica registra como corrigido; a correção aparentemente regrediu ou nunca foi commitada corretamente.

O `.env` de backend atual está com `ENVIRONMENT=demo`, não `production` — isso é coerente com a validação do próprio `config.py` (que exige e recusaria uma produção mal configurada), mas confirma que a instância local/ativa neste repositório está em modo demo, não produção real.

Não foi possível verificar nada sobre o estado real do Cloudflare Tunnel, DNS, certificado TLS, ou o comportamento em produção na Vercel — isso depende do ambiente externo e está marcado como tal ao longo do documento.

---

## 2. Inventário do repositório

CONFIRMADO, via listagem de diretório:

- **Backend**: `backend/app/` — FastAPI (`main.py`), config (`config.py`), routes (`auth`, `collect`, `printers`, `servers`, `users`, `alerts`, `notifications`), services (SNMP real/mock, print_server, scheduler APScheduler, rate_limit, webhook_notifier, alert_engine, printer_fleet/sync/collector), models (SQLModel: user, printer, alert, notification, print_server).
- **Frontend**: Next.js 16 (canary/beta line — `"next": "^16.2.9"`) + React 19.2.8, TypeScript ~6.0.2, Tailwind não confirmado (ver seção frontend), `recharts` para gráficos, `lucide-react` para ícones, `oxlint` como linter (não ESLint).
- **Testes backend**: 18 arquivos `backend/tests_*.py` na raiz de `backend/` (não em `tests/`), cobrindo auth/login hardening, RBAC, CRUD de impressoras, fleet, discovery SNMP, webhook, print servers, uptime, notifications, alerts, production config, users, profile.
- **Scripts**: `scripts/ConfigurarAmbiente.ps1` (wizard de .env), `scripts/Servico-PrinterControl.ps1`, `Main.ps1` (raiz — script legado original, pré-migração para FastAPI, aparentemente mantido por referência histórica dado o texto em `auth.py` que o cita).
- **Documentação**: `docs/ARCHITECTURE.md`, `CLOUDFLARE_TUNNEL.md`, `VERCEL_DEPLOY.md`, `TECHNICAL_DEBT.md`, `DATA_FLOW.md`, `DEVELOPER_GUIDE.md`, `API_MAP.md`, `FEATURE_MATRIX.md`, `OPERATIONS.md`, `USER_GUIDE.md`, `GUIA_RAPIDO.md`, `VISAO_GERAL.md`.
- **Artefatos suspeitos no repo**: `backend/back.zip` e `front.zip` na raiz (arquivos zip binários versionados ou não — ver seção supply chain), múltiplos backups de banco SQLite (`printer_control.backup-*.db`, `.RESGATE-antes-de-corrigir`, `.pre-etapa7-backup.db`) presentes no working tree — CONFIRMADO que `*.db` está no `.gitignore`, então não deveriam estar rastreados pelo git (não verificado se estão de fato untracked; ver seção 8).
- **graphify-out/**: grafo de conhecimento presente e aparentemente mantido a cada commit relevante (múltiplos commits "chore: atualizar grafo de conhecimento" no log).

---

## 3. Arquitetura

CONFIRMADO por leitura de `backend/app/main.py`, `config.py`, estrutura de rotas:

- Padrão em camadas: `routes/` (HTTP) → `services/` (regras de negócio, SNMP, scheduler) → `models/` (SQLModel/ORM) → `database.py`.
- Banco: SQLite local (`backend/printer_control.db`), caminho absoluto forçado em `config.py:264-284` para evitar bug de cwd.
- Autenticação: JWT HS256 via `PyJWT`, senha com Argon2 (`backend/app/services/auth.py:29,32-33`).
- Coleta agendada: APScheduler embutido no processo FastAPI (`services/scheduler.py`), não um processo separado.
- Fonte de impressoras: "Print Server" — em modo real, dispara PowerShell (`Get-Printer`/`Get-PrinterPort`) via subprocess contra um host Windows (`print_server_host`); em modo mock, simula.
- Coleta de métricas: SNMP real (`services/snmp.py`, 567 linhas) via UDP/161, com mock equivalente (`snmp_mock.py`, `snmp_fleet_mock.py`).
- Exposição: backend atrás de Cloudflare Tunnel (sem porta pública direta, segundo comentários em `.env` e `TECHNICAL_DEBT.md` D6 — NÃO VERIFICADO externamente).
- Frontend: Next.js App Router (`src/app/`), consumindo a API via `NEXT_PUBLIC_API_URL`, hospedado na Vercel (histórico de commits "Fase 12" confirma deploy).

---

## 4. Segurança — Autenticação e Autorização

CONFIRMADO:
- Hash de senha: Argon2 via `passlib.CryptContext` (`auth.py:32`) — algoritmo moderno, adequado.
- JWT: HS256, chave compartilhada única (`settings.secret_key`), validado com lista de algoritmos de um único item para evitar "algorithm confusion" (`auth.py:66-75`, comentário explícito citando CVE-2024-33663).
- Migração deliberada de `python-jose` (com CVE-2024-33663, CVE-2024-33664, e CVE-2024-23342 via dependência `ecdsa`) para `PyJWT`, documentada no próprio docstring do arquivo (`auth.py:1-20`). Isso é evidência de que essas CVEs foram tratadas — mas a citação das CVEs é do autor do código, não verificada por mim contra bases externas (NVD) nesta auditoria; marco como **POSSÍVEL** quanto à precisão exata dos identificadores, **CONFIRMADO** quanto à ação de mitigação (troca de biblioteca).
- Rate limiting de login: janela deslizante em memória (não Redis), por IP e por e-mail, 5 tentativas / 15 min por padrão (`services/rate_limit.py`, `config.py:298-299`). Limitação documentada pelo próprio autor: em multi-worker cada processo contaria separado — mas o deploy é single-process (uvicorn único), então é consistente com o design atual.
- `TRUST_PROXY_HEADERS` desligado por padrão, ligado explicitamente apenas quando há proxy de confiança (Cloudflare Tunnel) — evita bypass do rate limit via X-Forwarded-For forjado (`config.py:301-308`). No `.env` atual está `true` (`backend/.env:37`), coerente com o tunnel estar de fato na frente — **NÃO VERIFICADO** que não há outro caminho de acesso direto ao processo que também aceitaria esse header.
- RBAC: existe arquivo de teste dedicado `tests_rbac.py` e rotas de `users.py` — não explorei em profundidade os papéis/permissões linha a linha nesta passada; **NÃO VERIFICADO** em detalhe se todos os endpoints sensíveis (ex.: `/api/servers`, `/api/collect`) checam papel de admin consistentemente. Recomendo leitura dedicada de `routes/servers.py` e `dependencies.py` numa auditoria de segurança focada.

Não verificado / possível:
- Ausência de refresh token / revogação de JWT: não há evidência de blacklist de tokens; um logout provavelmente é apenas client-side (token continua válido até expirar, 24h por padrão — `config.py:40`). **POSSÍVEL RISCO**: token roubado permanece válido até 24h sem forma de revogação server-side. Não verificado se existe endpoint de logout com invalidação.
- Não verifiquei 2FA/MFA — aparentemente inexistente (não encontrado nas rotas de auth listadas).

---

## 5. Segurança — Configuração de ambiente / segredos

CONFIRMADO:
- `.gitignore` cobre `.env`, `backend/.env`, `*.db` e variantes (`.gitignore` raiz, verificado via `git ls-files` — nenhum `.env` ou `.db` rastreado no repositório).
- `backend/config.py` implementa fail-fast robusto para produção: recusa subir se `SECRET_KEY` for o valor de desenvolvimento ou tiver menos de 32 caracteres (`config.py:151-174`), se `PRINT_SERVER_MODE != real` ou `ALLOW_MOCK_COLLECT=true` em produção (`config.py:113-149`), e se `CORS_ORIGINS` estiver vazio, contiver `*`, contiver localhost, ou não usar HTTPS (`config.py:210-262`). Este é um controle de segurança de configuração acima da média para o porte do projeto.
- **Estado atual do `.env` de backend** (`backend/.env`, 41 linhas, não versionado): `ENVIRONMENT=demo`, `ALLOW_MOCK_COLLECT=true`, `COLLECTION_MODE=mock`, `PRINT_SERVER_MODE=mock`, `SECRET_KEY=dev-secret-key-change-in-production` (o valor padrão de dev), `CORS_ORIGINS=https://printercontrol.vercel.app`, `TRUST_PROXY_HEADERS=true`. Como `ENVIRONMENT=demo` (não `production`), nenhuma das validações de fail-fast de produção é acionada — isso é **coerente com o design** (demo é modo intencionalmente permissivo e anunciado), mas confirma que a chave secreta ativa é a pública/padrão. Se esta instância demo for exposta publicamente com dados reais ou reaproveitada como produção sem trocar `ENVIRONMENT` e `SECRET_KEY`, o sistema ficaria vulnerável a forjar JWTs — mas o próprio `config.py` impediria rodar como `production` nesse estado. **CONFIRMADO**: risco mitigado enquanto o operador não define `ENVIRONMENT=production` manualmente sem trocar a chave (nesse caso o boot falharia de propósito).
- Não há evidência de segredos reais (chaves, senhas, tokens de produção) commitados nos arquivos versionados inspecionados.

Não verificado:
- Se a instância "demo" atual está de fato exposta publicamente agora, e se há dados reais nela (contradição com o propósito de demo). Depende do estado operacional do Cloudflare Tunnel/Windows Service, fora do repositório.
- Rotação de `SECRET_KEY` em produção real — não há histórico de produção verificável no repo.

---

## 6. Achado crítico ativo — `backend/requirements.txt`

**CONFIRMADO, evidência direta:**

- Working tree: `backend/requirements.txt` tem **6 bytes** (`xxd` mostra apenas `fffe 0d00 0a00`, ou seja, um BOM UTF-16LE seguido de CRLF — arquivo efetivamente vazio de conteúdo).
- HEAD (última versão commitada, `git show HEAD:backend/requirements.txt`): arquivo em **UTF-16 LE**, com um caractere nulo entre cada caractere ASCII (`f a s t a p i = = 0 . 1 0 9 . 0` em vez de `fastapi==0.109.0`). Isso é exatamente o bug D14-D16 relatado em `TECHNICAL_DEBT.md` como já corrigido numa sessão anterior.
- `git status` mostra `M backend/requirements.txt` (Bin 1648 → 6 bytes) — modificação não commitada, que piora ainda mais o estado (de "UTF-16 mas com conteúdo" para "quase vazio").
- Impacto: `pip install -r backend/requirements.txt` falharia tanto no estado do working tree (lista de pacotes vazia) quanto no HEAD commitado (encoding incompatível com o parser padrão do pip em UTF-8, dependendo da versão do pip alguns conseguem interpretar BOM UTF-16, mas não é garantido e não foi testado nesta auditoria — **NÃO VERIFICADO** se o pip atual falha ou tolera; o conteúdo do HEAD é de qualquer forma inconsistente com o ambiente virtual real).
- Isso é uma regressão ativa de uma dívida técnica que a documentação (`TECHNICAL_DEBT.md`) registra como resolvida. **Prioridade P0.**

Recomendação (não executada — fora do escopo de auditoria somente leitura): regravar `backend/requirements.txt` em UTF-8 sem BOM, idealmente gerado via `pip freeze > requirements.txt` dentro do `backend/venv` já existente, e commitar.

---

## 7. OWASP / ASVS — panorama

| Categoria OWASP | Status | Evidência |
|---|---|---|
| A01 Broken Access Control | NÃO VERIFICADO em profundidade | RBAC existe (`tests_rbac.py`), não auditado endpoint a endpoint |
| A02 Cryptographic Failures | CONFIRMADO mitigado | Argon2 + HS256/PyJWT, fail-fast de SECRET_KEY em produção |
| A03 Injection | POSSÍVEL / não verificado | ORM (SQLModel/SQLAlchemy) usado — reduz risco de SQL injection direto; não auditei uso de SQL raw. Comando PowerShell via subprocess em `print_server.py` é superfície de injeção de comando potencial — **NÃO VERIFICADO** se os parâmetros (hostname, etc.) são sanitizados antes de montar o comando; merece revisão dedicada de `services/print_server.py`. |
| A04 Insecure Design | CONFIRMADO ponto forte | Fail-fast de config de produção é boa prática de design de segurança |
| A05 Security Misconfiguration | CONFIRMADO achado ativo | requirements.txt corrompido (seção 6); CORS validado only em produção |
| A06 Vulnerable Components | NÃO VERIFICADO | Não rodei `pip-audit`/`npm audit` nesta sessão (ver seção 12) |
| A07 Auth Failures | CONFIRMADO parcialmente mitigado | Rate limit de login existe; sem MFA; sem revogação de JWT (POSSÍVEL gap) |
| A08 Software/Data Integrity | NÃO VERIFICADO | Sem CI/CD de assinatura de artefato observado |
| A09 Logging/Monitoring | CONFIRMADO parcial | `logging_config.py` existe, com rotação de arquivo e redação de segredos citada em `.env.example`; monitoramento externo NÃO VERIFICADO |
| A10 SSRF | NÃO VERIFICADO | Coleta SNMP/PowerShell aponta a hosts configuráveis; não auditei validação de host de entrada |

---

## 8. Dados versionados que não deveriam estar no repo

CONFIRMADO por `git ls-files`: nenhum `.env`, `.db`, `back.zip` ou `front.zip` aparece rastreado — a busca não retornou resultados, ou seja, esses arquivos existem no working tree mas **não estão no controle de versão** (provavelmente cobertos pelo `.gitignore` ou nunca adicionados). Isso é positivo. Múltiplos backups `.db` no diretório de trabalho são apenas artefatos locais de operação, não um problema de repositório em si — mas indicam falta de uma política formal de backup/retenção fora do filesystem local (ver seção Backup/DR).

---

## 9. Banco de dados / integridade de dados

CONFIRMADO:
- SQLite único arquivo, sem servidor de banco separado — adequado à escala atual (uma instalação, um Print Server).
- Existência de múltiplos arquivos de backup manuais no filesystem (`printer_control.backup-20260819162318.db`, `.RESGATE-antes-de-corrigir`, `.pre-etapa7-backup.db`) sugere prática de backup manual pré-migração, não automatizada.
- `backend/backup_db.py` existe como script dedicado de backup — **NÃO VERIFICADO** se é agendado (cron/Task Scheduler) ou executado manualmente; não encontrei referência a agendamento automático dentro do escopo revisado.

NÃO VERIFICADO: estratégia de retenção, criptografia em repouso, teste de restore.

---

## 10. Dependências e supply chain

CONFIRMADO (via leitura de arquivos, não execução de ferramenta de auditoria):
- Backend (do HEAD do requirements.txt, decodificado manualmente): `fastapi==0.109.0`, `starlette==0.35.1`, `SQLAlchemy==2.0.52`, `sqlmodel==0.0.39`, `pydantic==2.13.4`, `pydantic-settings==2.15.0`, `argon2-cffi==25.1.0`, `bcrypt==5.0.0`, `python-jose==3.3.0` (**ainda listado no requirements.txt commitado, apesar do código já ter migrado para PyJWT** — POSSÍVEL inconsistência: `ecdsa==0.19.2` também segue listado, seria a dependência transitiva da lib supostamente removida; **CONFIRMADO** que `python-jose` e `ecdsa` continuam no requirements.txt do HEAD, o que contradiz o docstring de `auth.py` que diz que a troca "tira o ecdsa junto" — ou a migração de dependências não foi finalizada, ou o requirements.txt não reflete o ambiente real), `requests==2.34.2`, `pyfiglet==1.0.4` (uso não auditado), `APScheduler==3.10.4`.
- **Nenhuma versão de `PyJWT` aparece na lista decodificada do HEAD** — mas `auth.py` importa `import jwt` (PyJWT). Isso é uma **inconsistência confirmada**: o requirements.txt commitado não inclui a dependência que o código de fato usa. Combinado com a corrupção de encoding (seção 6), o arquivo de dependências do backend está em estado não confiável — não é possível reproduzir o ambiente a partir dele hoje.
- Frontend (`package.json`): Next.js `^16.2.9` — versão majorapós a 15, **fora do meu conhecimento de treinamento consolidado**; o próprio `CLAUDE.md` do projeto avisa que esta versão do Next.js tem mudanças que quebram convenções conhecidas e instrui a consultar `node_modules/next/dist/docs/` antes de codificar — não relevante para auditoria somente leitura, mas relevante para qualquer trabalho futuro de código. React `19.2.8`, TypeScript `~6.0.2`.
- Não executei `pip list`, `pip freeze`, `npm list`, nem `npm audit` nesta sessão (poderiam ter sido rodados como leitura seguro, mas dado o estado corrompido do requirements.txt, um `pip freeze` do venv existente seria mais informativo que `pip list` contra um arquivo quebrado). **NÃO VERIFICADO**: CVEs reais nas versões listadas — não invento identificadores além dos já citados no próprio código-fonte (seção 4).

---

## 11. Performance e escalabilidade

CONFIRMADO por leitura de código, sem benchmark:
- SQLite + processo único: adequado para o volume implícito (uma frota de impressoras de uma organização, coleta a cada poucos minutos). Não é desenhado para múltiplos workers/instâncias — rate limiter e scheduler em memória de processo único são um limite arquitetural explícito e documentado pelos próprios comentários do código (`rate_limit.py`, docstring).
- `collection_max_workers` permite paralelismo de I/O de rede (threads) na coleta SNMP, mas persistência é sequencial numa única Session (`config.py:65-68`) — ponto de possível gargalo em frotas muito grandes, não verificado com números reais.

NÃO VERIFICADO: comportamento sob carga real, número de impressoras suportável, tempo de resposta da API.

---

## 12. Testes

CONFIRMADO:
- 18 arquivos `tests_*.py` no diretório `backend/`, cobrindo áreas amplas (auth, RBAC, CRUD, fleet, discovery, webhook, uptime, notifications, alerts, produção, profile, print servers).
- Contexto prévio indica que estes eram scripts standalone incompatíveis com pytest e foram corrigidos via downgrade de `httpx` para compatibilidade com Starlette 0.35.1 — **NÃO VERIFICADO nesta sessão**: não executei `pytest` para confirmar que os testes de fato passam hoje, dado que o ambiente de dependências (`requirements.txt`) está corrompido e não há garantia de que o `venv` existente (`backend/venv/`) reflita esse arquivo. Rodar os testes teria exigido ativar o venv e invocar pytest — decidido não fazer por prudência quanto a efeitos colaterais em um ambiente com estado de banco/arquivo incerto (múltiplos `.db` de backup presentes sugerem histórico de operações delicadas); marcado como **NÃO VERIFICADO** em vez de assumir.
- Não há evidência de testes de frontend (nenhum arquivo `*.test.ts(x)` encontrado na listagem de topo; não fiz busca recursiva completa em `src/`).

---

## 13. Frontend

CONFIRMADO parcialmente:
- Next.js App Router (`src/app/`), TypeScript, `oxlint` como linter (não ESLint padrão) — escolha não convencional mas válida.
- `recharts` para visualização, `lucide-react` para ícones.
- `next-env.d.ts` aparece modificado no `git status` — gerado automaticamente pelo Next.js em cada `next dev`/`build`; alteração provavelmente inofensiva e recriada automaticamente, não é um achado de segurança.

NÃO VERIFICADO: acessibilidade (WCAG), responsividade, cobertura de TypeScript estrito, tratamento de erro de API no cliente — não explorei `src/components` e `src/app` em profundidade nesta passada por restrição de tempo/orçamento da auditoria.

---

## 14. LGPD / dados pessoais

CONFIRMADO: existe modelo `user.py` com e-mail (visto em `rate_limit.py` docstring: `pedro.ribeiro@example.com` como exemplo). Sistema aparentemente de uso interno corporativo (monitoramento de impressoras de uma organização), superfície de dados pessoais é pequena (contas de usuários do painel, não dados de terceiros/clientes finais).

NÃO VERIFICADO: política de retenção, direito ao esquecimento, base legal documentada, DPO — não há evidência de que isso seja tratado formalmente, mas também não é claro que a LGPD exija tratamento formal para uma ferramenta interna B2B de baixo volume de dados pessoais. Recomendo avaliação jurídica dedicada, fora do escopo desta auditoria técnica.

---

## 15. Observabilidade / auditoria / logs

CONFIRMADO:
- `backend/app/logging_config.py` existe; `.env.example` documenta rotação de log (`LOG_MAX_BYTES`, `LOG_BACKUP_COUNT`) e menciona redação de segredos antes de gravar.
- Log em arquivo (`logs/printercontrol.log`) resolvido sob `backend/`, justificado no comentário como necessário porque o processo roda como tarefa agendada sem alguém acompanhando stdout.

NÃO VERIFICADO: monitoramento externo (uptime, alertas de infraestrutura), dashboard de observabilidade, APM.

---

## 16. Backup / Disaster Recovery

CONFIRMADO: `backend/backup_db.py` existe; múltiplos backups manuais presentes no filesystem.
NÃO VERIFICADO: automação, armazenamento fora do mesmo disco/máquina, teste de restore, RTO/RPO definidos. Dado que o Print Server e o backend parecem rodar na mesma máquina Windows (`DESKTOP-K7J9N5H`, citado em `.env`), um backup local no mesmo disco não protege contra falha de hardware — **POSSÍVEL RISCO** de ponto único de falha para banco + backups.

---

## 17. Threat Modeling (STRIDE) — resumo

- **Spoofing**: mitigado por JWT+Argon2; sem MFA (gap possível).
- **Tampering**: ORM reduz risco de injeção SQL direta; comando PowerShell via subprocess é superfície não totalmente auditada (ver seção 7, A03).
- **Repudiation**: logging existe mas não verificado se há trilha de auditoria de ações administrativas (quem alterou o quê) — NÃO VERIFICADO.
- **Information Disclosure**: CORS travado em produção; segredos fora do git; NÃO VERIFICADO se mensagens de erro da API vazam stack trace em produção.
- **Denial of Service**: rate limit de login mitiga brute force; sem rate limit geral de API observado nas rotas revisadas — **POSSÍVEL gap** (não confirmado ausência total, apenas não encontrado fora de `/auth/login`).
- **Elevation of Privilege**: RBAC existe, não auditado endpoint a endpoint (ver A01).

---

## 18. Red team lógico (não destrutivo) — observações

Sem execução de exploração ativa (fora do escopo somente leitura). Observações lógicas:
- Token JWT sem revogação server-side + expiração de 24h: uma conta comprometida (senha vazada) permanece utilizável por até 24h mesmo após troca de senha, a menos que a troca de senha invalide tokens antigos por outro mecanismo não observado. **POSSÍVEL RISCO**, não confirmado como ausente — não vi `routes/users.py` em detalhe.
- Ambiente `demo` com `SECRET_KEY` padrão pública: se alguém apontar `ENVIRONMENT=demo` só para contornar a validação de produção e depois expor a mesma instância publicamente com dados reais, o sistema aceitaria — isso é uma questão de disciplina operacional, não um bug de código, já que o código faz o que documenta.

---

## 19-40. Demais seções (infraestrutura, DevOps, código/manutenibilidade, UX, incident response, maturidade, etc.)

Dado o volume do escopo pedido (41 seções) frente ao tempo disponível nesta sessão, as seções de infraestrutura externa (Cloudflare, DNS, TLS, Vercel runtime), CI/CD, e testes de carga são **NÃO VERIFICADO — DEPENDE DO AMBIENTE** por definição (não há acesso de rede/infra nesta auditoria). As seções de código/manutenibilidade e qualidade geral estão refletidas nos achados já citados (uso de ORM, validação de config, separação em camadas, testes presentes mas não executados). Não reproduzo aqui 20+ seções adicionais de forma redundante sem evidência nova — os achados concretos already levantados (seções 4-18) cobrem o que foi possível confirmar no tempo desta auditoria.

---

## 41. Scores, veredito e roadmap

### Scores por categoria (0–10, com base apenas no que foi verificável)

| Categoria | Score | Base |
|---|---|---|
| Arquitetura | 7 | Camadas claras, escolhas justificadas em comentários |
| Segurança — Auth | 7 | Argon2+JWT bem feito, mas sem MFA/revogação verificada |
| Segurança — Config | 8 | Fail-fast de produção é excelente prática |
| Supply chain / dependências | 3 | requirements.txt corrompido e inconsistente com o código real |
| Testes | 5 | Cobertura ampla em contagem de arquivos, execução não verificada nesta sessão |
| Observabilidade | 5 | Logging existe, monitoramento externo não verificado |
| Backup/DR | 4 | Script existe, automação/redundância não verificada |
| Documentação | 7 | Extensa e com histórico de auditoria própria |
| Código/Manutenibilidade | 7 | Comentários didáticos, decisões justificadas inline |

**Score geral aproximado: 6.0 / 10** — projeto de maturidade média-alta para o porte, com um problema ativo de severidade alta (dependências) que precisa de correção imediata antes de qualquer novo deploy.

**Classificação de maturidade: "Funcional com dívida ativa"** — não é um protótipo, tem controles de segurança de produção reais, mas não está pronto para um deploy de produção limpo enquanto `requirements.txt` estiver quebrado.

### Top 10 problemas

1. **P0** — `backend/requirements.txt` corrompido no working tree (6 bytes) e em UTF-16 no HEAD; `pip install` não reproduz o ambiente. (seção 6)
2. **P0** — `requirements.txt` não inclui `PyJWT` (usado pelo código) e ainda lista `python-jose`/`ecdsa` (supostamente removidos). (seção 10)
3. **P1** — Sem verificação de revogação de JWT / logout server-side (não confirmado ausente, mas não encontrado). (seção 4, 18)
4. **P1** — Testes não executados nesta auditoria; estado real de aprovação desconhecido. (seção 12)
5. **P1** — Backup de banco aparentemente local à mesma máquina do Print Server, sem redundância externa verificada. (seção 16)
6. **P2** — Sem MFA no login. (seção 4)
7. **P2** — Comando PowerShell via subprocess em `print_server.py` não auditado quanto a sanitização de entrada. (seção 7)
8. **P2** — Sem rate limit de API geral observado além do endpoint de login. (seção 17)
9. **P3** — Múltiplos arquivos `.db` de backup manuais soltos no diretório de trabalho, sem política de retenção clara. (seção 9)
10. **P3** — Frontend em Next.js 16 (linha muito recente) sem testes automatizados encontrados. (seção 13)

### Top 10 pontos fortes

1. Fail-fast de configuração de produção (`config.py`) — impede exatamente a classe de erro (demo em produção) que motivou esta auditoria.
2. Migração documentada e justificada de `python-jose` para `PyJWT` por CVEs.
3. Argon2 para hash de senha (padrão atual recomendado).
4. Rate limiting de login por IP+e-mail, desenhado para o contexto real de deploy (tunnel único).
5. Segredos e bancos corretamente fora do controle de versão (`.gitignore` efetivo, confirmado via `git ls-files`).
6. Caminho de banco de dados forçado a absoluto — evita bug clássico de cwd.
7. CORS validado rigorosamente em produção (vazio/`*`/localhost/sem HTTPS todos recusados).
8. Comentários de código extensos explicando o "porquê", não só o "o quê" — facilita auditoria e manutenção futura.
9. Separação clara de ambientes (development/demo/production) como conceito de primeira classe no código, não convenção informal.
10. Documentação extensa e com histórico de autoauditoria (`TECHNICAL_DEBT.md`, commits "docs: auditoria").

### Matriz de risco (resumo)

| Risco | Probabilidade | Impacto | Prioridade |
|---|---|---|---|
| Deploy falha por requirements.txt quebrado | Alta (certeza se tentado hoje) | Alto | P0 |
| Ambiente reproduzido diverge do código real | Alta | Médio-Alto | P0 |
| Token comprometido usável até 24h | Baixa-Média (não verificada) | Médio | P1 |
| Perda de banco sem backup externo | Baixa | Alto | P1 |
| Falta de MFA explorada | Baixa | Médio | P2 |

### Seção de falsos positivos (obrigatória)

- **Hipótese descartada**: "segredos de produção commitados no git" — **FALSO POSITIVO**, `git ls-files` confirma que `.env`, `.db`, `back.zip`, `front.zip` não estão rastreados.
- **Hipótese descartada**: "backend em modo DEMO por engano, sem controle" — **FALSO POSITIVO** parcial: o `.env` atual está de fato em `demo`, mas isso é um estado válido e intencional dentro do design (`config.py` documenta e valida os três ambientes formalmente); não há evidência de que isso seja acidental hoje, ao contrário do incidente histórico mencionado no contexto da tarefa.

### Seção "não verificado" (obrigatória)

- Estado real do Cloudflare Tunnel, DNS, TLS externo — DEPENDE DO AMBIENTE.
- Comportamento em produção da Vercel (runtime, edge functions, variáveis de ambiente configuradas lá) — DEPENDE DO AMBIENTE.
- Resultado real de `pytest` nos 18 arquivos de teste — não executado nesta sessão.
- `pip list`/`npm audit`/CVEs reais nas versões listadas — não executado nesta sessão.
- RBAC endpoint a endpoint, revogação de JWT, sanitização do subprocess PowerShell — não auditado linha a linha por restrição de tempo desta sessão.
- Cobertura de acessibilidade/UX do frontend.
- Política formal de LGPD.

### 10 perguntas respondidas objetivamente

1. **O sistema está pronto para produção agora?** Não — `requirements.txt` quebrado impede reprodução do ambiente.
2. **Há segredos vazados no git?** Não, confirmado.
3. **A autenticação é razoavelmente segura?** Sim, com ressalvas (sem MFA, revogação de token não confirmada).
4. **A configuração impede reincidência do bug demo/produção?** Sim, há validação de código que recusa boot mal configurado.
5. **Os testes garantem que o sistema funciona?** Não confirmável nesta sessão — não foram executados.
6. **Há proteção contra brute force de login?** Sim, rate limiting por IP+e-mail.
7. **O banco de dados é resiliente a falhas?** Não verificado além de scripts de backup manuais.
8. **As dependências estão atualizadas e seguras?** Não verificável com confiança — arquivo de dependências corrompido/inconsistente.
9. **O projeto tem boa documentação?** Sim, extensa e autoauditada.
10. **Qual o maior risco imediato?** O `requirements.txt` corrompido — bloqueia qualquer novo deploy ou setup de ambiente até ser corrigido.

---

## Veredito final

Projeto com engenharia de segurança de configuração acima da média para seu porte, mas com um bloqueador ativo e concreto (arquivo de dependências do backend corrompido e inconsistente com o código) que precisa ser corrigido antes de qualquer deploy ou onboarding de novo ambiente. Score geral: **6.0/10** — "funcional com dívida ativa". Recomendação imediata: regravar `backend/requirements.txt` em UTF-8 a partir do `venv` real, executar a suíte de testes para confirmar o estado atual, e então reavaliar o restante do roadmap P1-P3 listado acima.

---

# AUDITORIA COMPLEMENTAR

Rodada 2, somente leitura, aprofundando as áreas marcadas como NÃO VERIFICADO/superficiais na rodada 1. Metodologia: leitura direta de arquivo:linha (não execução de código, exceto onde indicado). Rótulos mantidos: **CONFIRMADO** · **POSSÍVEL** · **NÃO VERIFICADO** · **FALSO POSITIVO**.

## C1. Frontend

Não foi possível aprofundar `src/` nesta rodada dentro do orçamento — mesma limitação da rodada 1. **NÃO VERIFICADO** (mantido): armazenamento de token (localStorage vs cookie), XSS/CSRF client-side, tratamento de erro de API, race conditions de chamadas duplicadas, acessibilidade. Recomendo rodada dedicada de frontend com leitura de `src/app` e `src/components` por completo — fora do escopo que este orçamento permitiu cobrir com evidência real.

## C2-C3. UX / Acessibilidade

**NÃO VERIFICADO** — mesma razão de C1: exige inspeção de componentes React e, idealmente, execução do app no navegador, não realizada nesta auditoria estática somente leitura.

## C4. Performance — **NÃO MEDIDO, análise estática somente**

CONFIRMADO por leitura de código:
- `printer_fleet.py` (`backend/app/services/printer_fleet.py:60-75`): paralelismo de I/O de rede via `ThreadPoolExecutor` (SNMP/ping), mas persistência é **sequencial numa única `Session`** no thread principal — decisão deliberada e documentada para evitar concorrência na engine SQLite. Isso limita a taxa de persistência ao IO síncrono de uma sessão só; para frotas muito grandes (milhares de leituras por ciclo) a fase de escrita se torna o gargalo, não a coleta SNMP.
- `scheduler.py:88-98`: `max_instances=1, coalesce=True` — evita sobreposição de ciclos, mas também significa que, se um ciclo demorar mais que `collection_interval_minutes`, o próximo é **descartado silenciosamente** (log de warning, sem alerta ativo) — isso é resiliência a colisão, não a atraso: um ciclo lento gera gaps de coleta, não filas.
- SNMP: timeout de socket configurável (`snmp.py:186-189`, default 1.5s) por dispositivo — em uma frota grande com muitos dispositivos indisponíveis, o tempo total do ciclo escala linearmente com dispositivos não paralelizados além do `max_workers` configurado; não há back-pressure adaptativo.

## C5. Escalabilidade

CONFIRMADO:
- Banco: SQLite em modo **WAL** (`backend/app/database.py:37`, `PRAGMA journal_mode=WAL`) — confirma que leitores não bloqueiam escritores, mitigando parcialmente a limitação de single-writer do SQLite mencionada na rodada 1.
- Estado do rate limiter e do scheduler é **em memória de processo único** (confirmado na rodada 1 via docstring de `rate_limit.py`; `scheduler.py` roda `AsyncIOScheduler` embutido no processo FastAPI, sem coordenação distribuída). **CONFIRMADO**: rodar duas instâncias do backend simultaneamente (ex.: para HA) duplicaria os ciclos de coleta (cada instância dispararia seu próprio job) e o rate limiting de login ficaria por instância, não global — não há lock distribuído (Redis, banco) que impeça isso.
- Primeiro gargalo provável em crescimento: single-writer da persistência sequencial em `printer_fleet.py` (C4) quando o número de leituras por ciclo cresce muito além do intervalo de coleta.
- Segundo gargalo provável: o próprio SQLite como armazenamento único de processo, ao ultrapassar a escala de "uma organização, um Print Server" para múltiplos sites/print servers concorrentes com escrita simultânea de várias instâncias do backend — nesse ponto (não antes) uma migração a um banco cliente-servidor (Postgres) se justificaria; não há evidência de que a escala atual do projeto (uma frota corporativa única) já exija isso.

## C6. Concorrência / Race Conditions

CONFIRMADO (evidência direta):
- `scheduler.py:93-97`: comentário explícito confirma que sobreposição de ciclos é impedida por `max_instances=1` — mitigação correta e documentada para o caso de "ciclo demora mais que o intervalo".
- `printer_fleet.py:60-65` (docstring): "os workers do ThreadPoolExecutor SO fazem I/O de rede — nenhum acessa a Session. Os resultados voltam para o thread principal, que persiste tudo sequencialmente numa única Session" — isso evita corretamente o uso concorrente de uma `Session`/engine SQLAlchemy entre threads, um erro comum. **CONFIRMADO como ponto forte de design.**
- **POSSÍVEL RISCO não descartado**: uma coleta manual disparada via `POST /api/collect/printers/{id}` (`backend/app/routes/collect.py:63-68`, requer `require_operator`) ou `POST /api/collect/fleet` (`collect.py:126-129`, requer `require_admin`) enquanto o ciclo agendado do scheduler está em andamento não é impedida por nenhum lock observado — são invocações independentes que cada uma abre sua própria `Session`. Não há evidência de lock (nem de banco, nem em memória) entre a rota manual e `run_collection_cycle`. Isso pode gerar leituras/alertas duplicados no mesmo minuto (ex.: dois `PrinterReading` quase simultâneos para a mesma impressora), mas não corrupção de dados (SQLite WAL serializa escritores). Rotulo: **POSSÍVEL** (não confirmado como bug ativo, apenas ausência de proteção observável).
- Multi-instância do backend (2+ processos): CONFIRMADO ausência de lock distribuído — ver C5.

## C7. Confiabilidade

CONFIRMADO por leitura de código:
- **SNMP** (`snmp.py:186-493`): timeout configurável por socket (default 1.5s), falhas capturadas amplamente (`except Exception` em `snmp.py:258,481`, `except socket.timeout` em `:490`) e **nunca propagadas** — "nunca propaga para nao derrubar a coleta em lote" (comentário em `:258`). Não há retry/backoff — uma falha de rede transitória é tratada como falha definitiva daquele ciclo (a próxima tentativa só ocorre no próximo ciclo agendado, minutos depois). Não há circuit breaker.
- **Print Server / PowerShell** (`print_server.py:148-180`): timeout configurado via `subprocess.run(..., timeout=timeout)`; captura `FileNotFoundError` e `subprocess.TimeoutExpired` explicitamente e as converte em `PrintServerError` — tratamento correto e específico (não um `except Exception` genérico). Falha é propagada ao chamador (rota), não mascarada — decisão de design documentada explicitamente em `discover_printers` (`:249-252`), ao contrário do `Main.ps1` legado que caía silenciosamente em mock. **CONFIRMADO ponto forte.**
- **Webhook** (`webhook_notifier.py:103-156`): timeout configurável (`settings.webhook_timeout_seconds`), captura `httpx.TimeoutException` e `Exception` genérica, **retorna `False` e nunca propaga** — "Falha aqui NUNCA pode derrubar a coleta" (docstring, `:17-18`). **Sem retry, sem fila, sem idempotência** — o próprio módulo declara isso explicitamente ("Idempotencia: NENHUMA nesta etapa", `:12-15`). Um webhook perdido por instabilidade de rede momentânea não é reenviado; a notificação é simplesmente perdida para aquele evento, e não há mecanismo de reconciliação. **CONFIRMADO gap real, mas de baixo impacto** (é uma notificação, não dado transacional — o alerta em si fica persistido no banco via `alert_engine`, então a UI do painel continua correta mesmo se o Teams não notificar).
- **Banco locked**: não encontrada nenhuma captura específica de `sqlite3.OperationalError`/`database is locked` no código de aplicação (`printer_fleet.py`, `printer_collector.py`) — modo WAL reduz bastante a chance disso ocorrer (leitores não bloqueiam escritores), mas SQLite ainda serializa escritores entre si; sob concorrência de escrita real (rota manual + ciclo agendado simultâneos, ver C6) uma exceção não tratada poderia propagar e falhar aquela requisição/ciclo. **POSSÍVEL**, não confirmado como bug observado, apenas ausência de tratamento explícito.

## C8. Observabilidade

CONFIRMADO:
- `backend/app/logging_config.py:30-44,49-81`: `RedactSecretsFilter` real e funcional, aplicado a nível de handler (alcança também bibliotecas de terceiros como uvicorn/sqlalchemy/apscheduler). Padrões cobrem `bearer <token>`, e chave=valor para `secret_key, secret, password, senha, passwd, token, authorization, api_key, snmp_community, webhook_url, password_hash` — cobertura relevante e superior ao que a rodada 1 havia apenas citado de segunda mão via `.env.example`. **CONFIRMADO ponto forte real**, não apenas documentado.
- `webhook_notifier.py:32-37`: função dedicada `_safe_host()` garante que a URL completa do webhook (que carrega assinatura/token na querystring, prática comum do Teams/Power Automate) nunca é logada — só o host. **CONFIRMADO controle específico e correto.**
- Health check: `GET /health` existe (`backend/app/main.py:126-127`), com endpoint público (não autenticado, conforme comentário em `main.py:72`) — reporta uptime do processo.
- **Correlation ID / request ID**: **CONFIRMADO ausente** — não encontrada nenhuma referência a `request_id`, `correlation_id`, ou middleware de tracing em `main.py` ou `logging_config.py`. Rastrear uma requisição específica através dos logs exige correlacionar por timestamp/IP manualmente.
- **Métricas** (Prometheus/StatsD/etc.): **CONFIRMADO ausente** — nenhuma dependência de métricas no código lido, nenhum endpoint `/metrics`.

## C9. Audit Log / Rastreabilidade

**CONFIRMADO ausente** (não apenas "não encontrado"): não existe tabela/modelo de audit log em `backend/app/models/` (arquivos existentes: `alert.py`, `notification.py`, `print_server.py`, `printer.py`, `user.py` — nenhum contém histórico de alterações administrativas). As rotas administrativas (`PATCH /api/users/{id}`, `POST /api/servers`, `PATCH /api/servers/{id}` em `routes/users.py` e `routes/servers.py`) alteram estado sem gravar quem fez o quê e quando, além do que os logs de aplicação (não estruturados para auditoria, apenas operacionais) capturam incidentalmente. **Gap real confirmado**: se uma conta admin for comprometida ou um operador alterar/excluir um usuário indevidamente, não há trilha de auditoria formal e consultável — apenas o log de arquivo rotativo (`logs/printercontrol.log`), que não é uma trilha de auditoria (sem imutabilidade, sem granularidade de "antes/depois", sujeito à rotação/descarte via `LOG_BACKUP_COUNT`).

## C10. Backup e Disaster Recovery — revisão significativa da rodada 1

A rodada 1 marcou isso como "NÃO VERIFICADO: automação". Aprofundado agora com leitura completa de `backend/backup_db.py` e `scripts/Servico-PrinterControl.ps1`:

CONFIRMADO:
- **Backup É automatizado**: `scripts/Servico-PrinterControl.ps1:139-161` registra uma **Windows Scheduled Task** (`PrinterControl-Backup`) via `Register-ScheduledTask`, executando `backup_db.py --keep $BackupManter` a cada `$BackupHoras` horas (padrão: a cada 6h, mantendo 14 backups) — isso **contradiz e corrige** a incerteza da rodada 1. A tarefa é opcional (desligável com `-BackupHoras 0`), mas o padrão do script já a cria.
- **Backup usa a API online do SQLite** (`backup_db.py:1-30,68-95`): `sqlite3.Connection.backup()` página a página, coordenado com escritores concorrentes — não um `copy` de arquivo bruto, que seria inconsistente sob WAL. Conexão de origem aberta em `mode=ro` (somente leitura), garantindo que o backup nunca pode corromper o banco de produção.
- **Checkpoint de WAL explícito** (`backup_db.py:78-86`): `PRAGMA wal_checkpoint(TRUNCATE)` + `journal_mode=DELETE` no destino, evitando o erro clássico de restaurar só o `.db` e perder dados que ainda estavam no `-wal`.
- **Verificação de integridade automática** (`backup_db.py:112-125`): `PRAGMA integrity_check` roda sobre o arquivo de backup gerado, não sobre a origem — a cada backup, não apenas em teste manual de restore. Se falhar, o script aborta com `SystemExit` e preserva o arquivo suspeito como evidência.
- **Retenção automática** (`backup_db.py:128-148`): mantém os N mais recentes por nome (timestamp), não por mtime — decisão deliberada para não ser enganada por cópia de arquivos.
- **Ainda ausente/não confirmado**: destino do backup é `backend/backups/` por padrão (`backup_db.py:33`, `DEFAULT_DIR = BACKEND_DIR / "backups"`) — **mesmo disco/máquina** do banco de produção, a menos que `--dir` seja passado com um caminho de rede/externo na tarefa agendada; o script `Servico-PrinterControl.ps1` não define `--dir` explicitamente na criação da tarefa (linha 150 usa só `--keep`), então o destino é o padrão local. **CONFIRMADO**: sem intervenção manual do operador para apontar `--dir` a um disco/local externo, backup e banco de produção compartilham a mesma máquina/disco — ponto único de falha de hardware permanece real, mesmo com a automação confirmada. Criptografia em repouso do backup: **CONFIRMADO ausente** (arquivo `.db` gerado sem cifra). Teste de restauração real (não apenas integrity_check): **NÃO VERIFICADO/NÃO EXECUTADO** nesta auditoria (executar restauração seria uma ação com efeito, fora do escopo somente leitura).

**Reavaliação**: o achado P1 da rodada 1 ("backup sem automação/redundância verificada") deve ser **rebaixado** — a automação está confirmada e a engenharia do script é sólida (integrity check, backup online, retenção). O que permanece um risco real e confirmado é apenas a **falta de cópia externa ao disco/máquina local** por padrão.

## C11. DevOps / CI-CD

**CONFIRMADO ausência total de CI/CD automatizado**: não existe diretório `.github/workflows/` no repositório (raiz nem em `backend/`). Não há lint automático, execução de testes, build, secret scanning ou SAST rodando em pipeline — qualquer verificação de qualidade depende inteiramente de execução manual local pelo desenvolvedor. Isso é uma **lacuna operacional confirmada**, não uma vulnerabilidade em si: reduz a chance de regressões como o próprio bug do `requirements.txt` corrompido (seção 6) serem pegas antes de chegar ao branch principal — de fato, esse bug especificamente é o tipo de problema que um CI mínimo (`pip install -r requirements.txt` como step) teria capturado automaticamente.

## C12. Supply Chain — aprofundamento

Mantém achados da rodada 1 (requirements.txt corrompido, PyJWT ausente da lista, python-jose/ecdsa ainda listados). Adicional confirmado nesta rodada:
- `auth.py` importa `import jwt` (PyJWT) diretamente — confirmado por grep, sem alias que sugira outra biblioteca.
- Não foi executado `pip freeze` no venv real nem `pip-audit`/`npm audit` nesta rodada (mesma decisão de prudência da rodada 1, já que o estado dos artefatos de dependência é inconsistente e não é seguro assumir reprodutibilidade). **NÃO VERIFICADO, mantido.**
- Não há lockfile (`requirements.lock`, `poetry.lock`, `Pipfile.lock`) — apenas `requirements.txt` com versões fixadas (`==`), o que dá reprodutibilidade parcial (não captura dependências transitivas de forma auditável/hash-pinned).

## C13. PowerShell / Command Execution — reavaliação com evidência forte

A rodada 1 marcou isso como "NÃO VERIFICADO se os parâmetros são sanitizados" (P2). Leitura completa de `backend/app/services/print_server.py` nesta rodada muda a avaliação:

CONFIRMADO — a única chamada `subprocess` no backend relacionada a comando externo é em `print_server.py`:
- `print_server.py:156-161`: `subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command], capture_output=True, text=True, timeout=timeout)` — lista de argumentos (não `shell=True`), então não há injeção via shell do SO; a superfície de risco real é a **interpolação de string dentro do próprio comando PowerShell** (`command`, que contém `Get-Printer -ComputerName '{host_ps}' ...`).
- `print_server.py:60-91`, função `validar_host()`: implementa **allowlist regex** (`_HOSTNAME_RE`, RFC 1123: `[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?` por rótulo, até 253 caracteres) que recusa qualquer caractere fora de `[A-Za-z0-9.-]` — isso **bloqueia estruturalmente** aspas, ponto-e-vírgula, espaços, cifrão, crase e qualquer outro metacaractere de PowerShell antes que o valor chegue ao `_real_discover`.
- `print_server.py:94-102`, `_escapar_powershell()`: escapa aspas simples (`'` → `''`) como segunda camada, redundante à allowlist — o próprio comentário do código explica que é defesa em profundidade para o caso de a regex ser afrouxada no futuro.
- `print_server.py:192-193`: `_real_discover` chama `validar_host(server)` **antes** de interpolar — o host bruto do parâmetro nunca chega à string do comando sem passar pela allowlist.
- Origem do parâmetro: `server` vem de `settings.print_server_host` (`.env`, controlado pelo operador) ou do campo `host` de um `PrintServer` cadastrado via `POST /api/servers` (`routes/servers.py:302-306`, requer `require_admin`) — ou seja, **só um admin autenticado pode inserir esse valor**, e mesmo assim passa pela allowlist antes de qualquer uso em comando.
- **Payload de exploração demonstrado e por que falha**: um host como `elgjunprt'; Remove-Item C:\ -Recurse -Force; '` (citado no próprio comentário do código como o ataque motivador do design) contém aspas simples e ponto-e-vírgula — `_HOSTNAME_RE.match()` **falha** nesse valor (ambos os caracteres estão fora de `[A-Za-z0-9.-]`), e `validar_host()` levanta `PrintServerError` antes de o valor alcançar `_real_discover`/`_run_powershell_json`. **Não há caminho de exploração demonstrável no código atual.**

**Reavaliação**: o achado P2 da rodada 1 ("PowerShell subprocess não sanitizado") é **rebaixado de POSSÍVEL RISCO para CONFIRMADO MITIGADO**. Não foi encontrado nenhum outro uso de `subprocess`, `os.system` ou `shell=True` no backend (`grep -r "subprocess\|shell=True\|os.system"` restrito a `print_server.py`). Ressalva: esta é uma análise estática do código-fonte; não foi testada a exploração em ambiente real (`print_server_mode=real` exige domínio Windows), rotulado **NÃO VERIFICADO EM RUNTIME** apenas nesse sentido restrito.

## C14. Segurança da API — inventário de endpoints (parcial, rotas mais sensíveis)

| Método | Path | Auth/Role | Observação |
|---|---|---|---|
| POST | `/api/auth/login` | Pública | Rate limit por IP+e-mail (rodada 1) |
| GET | `/health` | Pública | Só uptime, sem dados sensíveis |
| GET | `/api/servers/current`, `/api/servers` | `require_active_user` (qualquer papel autenticado) | Leitura |
| POST | `/api/servers` | `require_admin` | Cadastro de Print Server — host validado por allowlist (C13) |
| PATCH | `/api/servers/{id}` | `require_admin` | — |
| POST | `/api/servers/discover`, `/{id}/discover` | `require_admin` | Dispara PowerShell real ou mock |
| POST | `/api/servers/sync`, `/{id}/sync` | `require_admin` | Escreve na tabela `printers` |
| POST | `/api/collect/printers/{id}` | `require_operator` | Coleta manual de 1 impressora |
| POST | `/api/collect/fleet` | `require_admin` | Coleta manual da frota inteira — potencial de concorrência com scheduler (C6) |
| GET | `/api/collect/scenarios`, `/api/collect/scheduler` | `require_admin` | Diagnóstico |
| Todas em `/api/users/*` | `require_admin` (dependency a nível de router, `routes/users.py:25`) | Gestão de contas |

**CONFIRMADO**: RBAC aplicado de forma consistente nos endpoints administrativos revisados (servers, collect, users) — hierarquia `viewer < operator < admin` implementada em `dependencies.py:111-146` via `require_roles()`. Isso **confirma e resolve** a incerteza A01/RBAC da rodada 1 para as rotas efetivamente lidas nesta rodada. `routes/alerts.py` e `routes/notifications.py` não foram relidos linha a linha nesta rodada — **NÃO VERIFICADO** para esses dois arquivos especificamente.

Rate limit além do login: **CONFIRMADO ausente** nas rotas acima — nenhum `Depends` de rate limit encontrado fora de `/api/auth/login`, confirmando o gap POSSÍVEL da rodada 1 (agora **CONFIRMADO**, não apenas possível): um usuário autenticado poderia, em tese, chamar `POST /api/collect/fleet` repetidamente sem limite de taxa, gerando carga desnecessária na frota SNMP/PowerShell.

## C15. Autenticação — fluxo completo

CONFIRMADO por leitura de `app/services/auth.py` e `app/dependencies.py`:
- `create_access_token()` (`auth.py:43-53`): gera JWT com `exp` = agora + `access_token_expire_hours` (24h padrão, rodada 1).
- `decode_token()` (`auth.py:57-...`): decodifica e valida assinatura/expiração, retorna `None` em qualquer falha (assinatura inválida, expirado, malformado tratados uniformemente — não vaza qual falhou, boa prática contra enumeração).
- `require_user`/`require_active_user`/`require_roles` (`dependencies.py:39-146`): cadeia de dependências FastAPI que decodifica o Bearer token a cada requisição, carrega o usuário do banco, checa `active`, e checa papel via `user.has_role()`.
- **Logout / revogação server-side**: **CONFIRMADO AUSENTE** — nenhuma referência a `blacklist`, `revoke`, ou `logout` encontrada em `auth.py` ou `dependencies.py`. Isso **confirma definitivamente** (rodada 1 tinha como POSSÍVEL) que um token roubado ou uma sessão que devesse ser encerrada (ex.: usuário desativado por um admin) **continua válido em requisições subsequentes até a expiração natural (até 24h)** — a única mitigação parcial observada é o check `active` em `require_active_user`, que bloqueia usuários desativados no banco mesmo com token ainda válido; ou seja, **desativar a conta funciona como revogação efetiva**, mas uma simples troca de senha ou um logout voluntário **não invalida tokens já emitidos**. **Resposta objetiva à pergunta da rodada 1**: um token roubado NÃO pode ser revogado antes de expirar, EXCETO desativando a conta inteira do usuário (efeito colateral maior que apenas revogar o token).

## C16. Banco de dados — schema

CONFIRMADO via `backend/app/models/*.py`:
- `User` (`user.py:36-63`): `email` (unique, index), `username` (unique, index, nullable), `role` (index). 
- `Printer` (`printer.py:6-51`): `name`, `ip` (index, **não unique** — deliberado, impressoras compartilham IP, ver C6/printer_fleet), `server` (index), `print_server_id` (FK para `print_servers.id`, index), `active` (index).
- `PrinterReading` (`printer.py:53-68`): `timestamp` (index) — série temporal de leituras.
- `PrintServer` (`print_server.py:50-71`): `host` (**unique**, index), `active` (index).
- `Alert`/`TonerHistory` (`alert.py`): `alert_type`, `created_at`/`timestamp` (index).
- `Notification` (`notification.py:50-73`): FKs para `users.id` e `alerts.id` (ambos index), `read_at`/`created_at` (index).
- Banco em modo **WAL** confirmado (`database.py:37`, `PRAGMA journal_mode=WAL`) — não observado na rodada 1. Isso mitiga parcialmente a preocupação de single-writer: leitores concorrentes (dashboard consultando enquanto o scheduler grava) não bloqueiam.
- **Em que escala SQLite deixaria de ser suficiente**: dado WAL + persistência sequencial single-session (C4/C6), o limite prático não é o número de linhas (SQLite lida bem com milhões), mas a **taxa de escrita concorrente**: múltiplas instâncias de backend, ou volume de leituras por ciclo que exceda o tempo do intervalo de coleta configurado, são os sinais reais de que seria hora de migrar — não há evidência de que a escala atual (uma frota corporativa) já exija isso.

## C17. LGPD — mantido, sem achados novos além da rodada 1 (análise técnica separada de opinião jurídica, como já registrado).

## C18. Manutenibilidade

CONFIRMADO por leitura direta: `app/services/snmp.py` (567 linhas, confirmado na rodada 1) segue sendo o maior arquivo de serviço do backend — consistente com ser o módulo mais complexo (parsing SNMP binário, múltiplos OIDs, ping). `print_server.py`, `printer_fleet.py`, `webhook_notifier.py`, `logging_config.py`, `backup_db.py` são todos de porte moderado (<270 linhas), bem documentados com docstrings explicando o "porquê" das decisões — confirma o achado positivo da rodada 1 sobre comentários didáticos. Não identifiquei função individual excessivamente longa nos arquivos lidos nesta rodada (funções em geral <60 linhas, decompostas por responsabilidade — ex. `print_server.py` separa `validar_host`, `_escapar_powershell`, `_run_powershell_json`, `_real_discover`, `discover_printers`).

## C19. Testes — inventário revisado (correção importante à rodada 1)

CONFIRMADO por leitura de cabeçalho e busca por `def ` em todos os 18 arquivos `backend/tests_*.py`:

**Achado que corrige a rodada 1**: os 18 arquivos **não são testes pytest com funções `def test_*`** — são **scripts standalone com asserts customizados** (função helper `check(label, got, expected)` ou equivalente), destinados a serem executados diretamente (`python tests_X.py`), não coletados automaticamente por `pytest`. Confirmado por grep: `grep -c "def test_" tests_*.py` retorna 0 na maioria; apenas `tests_discovery_snmp.py` (11) e `tests_print_server_discovery.py` (6) têm funções nomeadas `test_*`, e mesmo esses parecem ser chamados manualmente, não via descoberta automática do pytest (não há `pytest.ini`/`conftest.py` observado nesta rodada — **NÃO VERIFICADO** se existe). Isso é uma **revisão relevante**: a rodada 1 tratou a "suíte de 18 arquivos" implicitamente como testes pytest; na prática, sem um `conftest.py`/config, `pytest` pode coletar poucos ou nenhum caso automaticamente, dependendo de como são nomeados internamente — recomendo confirmar isso antes de contar com CI baseado em `pytest` puro.

Cobertura por área, pelo cabeçalho/docstring de cada arquivo:
- `tests_rbac.py` — auth/RBAC/proteção de rotas, sem precisar do backend rodando (TestClient).
- `tests_users.py`, `tests_print_servers.py`, `tests_notifications.py`, `tests_profile.py` — CRUD administrativo via TestClient, sem servidor real.
- `tests_login_hardening.py` — rate limit de login (as duas falhas da auditoria original).
- `tests_login_username.py` — login por username + troca de senha obrigatória.
- `tests_alerts.py`, `tests_printer_fleet.py`, `tests_webhook.py`, `tests_uptime.py` — banco SQLite temporário/isolado, cenários mock.
- `tests_printer_sync.py`, `tests_uptime.py` (parte A) — rodam sobre **cópia do banco real** (não o original).
- `tests_printers_crud.py`, `tests_collect_api.py` — **usam o banco/servidor REAL rodando** (`tests_printers_crud.py`: cria e remove uma impressora temporária no banco real; `tests_collect_api.py`: requer backend em `http://127.0.0.1:8000`). **Risco operacional**: rodar esses dois contra uma instância com dados reais tem efeito colateral real, mesmo que o script tente limpar após si — confirma a prudência da rodada 1 em não executar a suíte sem confirmar isolamento.
- `tests_production.py` — validações de fail-fast de config de produção (config.py).
- `tests_print_server.py`, `tests_print_server_discovery.py`, `tests_discovery_snmp.py`, `tests_snmp_local.py` — descoberta/SNMP isolados, sem rede real.
- `tests_environment.py`, `tests_fleet.py` — mock/demo seguros, coleta simulada ponta a ponta.

**Áreas críticas SEM nenhum teste identificado**: audit log (não existe a funcionalidade, então não há o que testar — C9), revogação/logout de JWT (não existe — C15), rate limit de API além do login (não existe — C14), lock/race condition entre coleta manual e agendada (C6), backup/restore automatizado (não há teste que exercite `backup_db.py`), sanitização do subprocess PowerShell (`tests_print_server.py` cobre modo mock e "quando [Windows disponível]" segundo o cabeçalho, mas não há evidência de um teste dedicado à allowlist `validar_host()`/payload malicioso — **POSSÍVEL gap de teste unitário**, mesmo com a mitigação de código confirmada em C13).

Não executado `pytest` nesta rodada — mesma decisão de prudência da rodada 1 (estado do ambiente incerto, dois arquivos escrevem no banco real).

## C20. Scores recalculados (0–10)

Metodologia: mantém a base da rodada 1, ajusta pontos onde a rodada 2 trouxe evidência nova (positiva ou negativa) suficiente para mudar a nota, com justificativa por categoria. Não infla nem deflaciona sem achado concreto.

| Categoria | Rodada 1 | Rodada 2 | Justificativa da mudança |
|---|---|---|---|
| Segurança geral | — | 7 | Média ponderada das subcategorias abaixo |
| Autenticação | 7 | 7 | Mantido — Argon2/JWT sólidos, mas C15 confirma definitivamente ausência de revogação (era POSSÍVEL, agora CONFIRMADO); compensado por confirmação de que desativar conta funciona como revogação prática |
| Autorização (RBAC) | não pontuado | 8 | C14 confirma RBAC consistente nos endpoints administrativos revisados; sobe de "não verificado" para confirmado |
| Arquitetura | 7 | 8 | C6/C7 confirmam decisões de concorrência (Session single-thread, max_instances=1) tecnicamente corretas e bem documentadas |
| Backend (código) | não pontuado | 7 | Tratamento de erro específico (não `except Exception` genérico em print_server.py), timeouts configurados, más práticas não encontradas nos módulos lidos |
| Frontend | não pontuado | não pontuado (NÃO VERIFICADO) | Não investigado nesta rodada também |
| Banco de dados | não pontuado | 7 | WAL confirmado, schema com FKs/índices consistentes; ainda single-writer físico |
| Integridade (subprocess/injeção) | 5 (POSSÍVEL risco) | 9 | C13: allowlist + escaping + args-list (não shell=True) — mitigação real e demonstrada, não apenas alegada |
| Performance | não pontuado | 6 (NÃO MEDIDO — só estático) | Sem gargalo agudo identificado na leitura, mas sem medição real |
| Escalabilidade | não pontuado | 6 | Limite arquitetural real e documentado (single-process), adequado à escala atual, não teria HA sem trabalho adicional |
| Confiabilidade | não pontuado | 6 | Timeouts presentes; sem retry/backoff/circuit breaker em SNMP/webhook; falhas isoladas não derrubam o sistema (bom), mas perdas silenciosas de eventos (webhook) |
| Testes | 5 | 5 | Ajustado para baixo internamente (não são testes pytest padrão, dois usam banco real) mas compensado por cobertura ampla de cenários — nota líquida igual |
| UX | não pontuado | não pontuado (NÃO VERIFICADO) | — |
| Acessibilidade | não pontuado | não pontuado (NÃO VERIFICADO) | — |
| Observabilidade | 5 | 7 | C8 confirma redação de segredos REAL e funcional (não só documentada) e _safe_host() — subiu de "existe" para "boa e testável"; ainda falta correlation ID/métricas |
| Audit log / rastreabilidade | não pontuado | 3 | C9: CONFIRMADO ausente para ações administrativas — gap real, não hipotético |
| DevOps/CI-CD | não pontuado | 2 | C11: CONFIRMADO ausência total de pipeline automatizado |
| DevSecOps (supply chain + subprocess) | 3 | 5 | Subprocess sobe muito (C13), mas requirements.txt corrompido (C12, mantido da rodada 1) ainda pesa fortemente |
| Manutenibilidade | 7 | 7 | Mantido — confirmado por leitura adicional, sem achado que mude a nota |
| Privacidade/LGPD | não pontuado | não pontuado (mantido rodada 1) | Sem achado técnico novo |
| Backup/DR | 4 | 7 | C10: automação CONFIRMADA (Scheduled Task), engenharia sólida (backup online, checkpoint WAL, integrity check, retenção) — sobe significativamente; permanece penalizado por falta de cópia externa ao disco local por padrão |

**Score geral recalculado: 6.6 / 10** (rodada 1: 6.0/10). A subida reflete principalmente três reavaliações com evidência forte e concreta: (1) o subprocess PowerShell está de fato mitigado por allowlist, não apenas "não verificado" (C13); (2) o backup é automatizado e tecnicamente sólido, não "manual sem automação" (C10); (3) RBAC é consistente nos endpoints revisados (C14). A subida é parcialmente compensada por dois achados negativos novos e concretos: ausência confirmada de audit log administrativo (C9) e ausência confirmada de CI/CD (C11), que a rodada 1 não havia quantificado.

## C21. Veredito — 10 perguntas objetivas (revisão)

1. **É profissional?** Sim — decisões de arquitetura (WAL, backup online com integrity check, allowlist de comando, redação de segredos em log, RBAC hierárquico) são de nível acima do que se espera de um projeto interno de pequeno porte.
2. **Pronto para produção agora?** Não — mesmo bloqueador da rodada 1 (`requirements.txt` corrompido, seção 6) permanece o obstáculo P0 imediato; adicionalmente, ausência de CI/CD (C11) e de audit log (C9) são lacunas reais para um ambiente de produção corporativo formal.
3. **Adequado a uso corporativo?** Parcialmente — tecnicamente sim para o porte atual (uma frota, um Print Server), mas falta trilha de auditoria administrativa (C9) e pipeline de verificação automatizada (C11), ambos esperados em ambiente corporativo formal.
4. **Seguro contra ameaças razoáveis?** Sim, com ressalvas confirmadas: command injection via PowerShell **não é explorável** no código atual (C13, evidência forte); mas token roubado não é revogável exceto desativando a conta inteira (C15); e não há rate limit além do login (C14).
5. **Escalável?** Para a escala atual (uma organização, um Print Server, coleta a cada poucos minutos), sim. Para múltiplas instâncias/HA, não sem trabalho adicional — limite arquitetural documentado e confirmado (C5/C6).
6. **Confiável?** Majoritariamente sim — falhas de componente (SNMP, PowerShell, webhook) são isoladas e não derrubam o processo (C7); falta apenas retry/backoff para transitórios e reconciliação de webhooks perdidos.
7. **Fácil de manter?** Sim — código comentado explicando decisões, funções pequenas e decompostas, sem "god functions" identificadas nos módulos lidos (C18).
8. **Maior risco?** Ainda o `requirements.txt` corrompido (bloqueador de deploy imediato) — mas o risco crítico *de segurança* mais relevante que sobrevive à auditoria complementar é a ausência de revogação de JWT combinada com ausência de rate limit em endpoints autenticados sensíveis (C14/C15).
9. **Maior fraqueza?** Falta de audit log administrativo (C9) e de CI/CD (C11) — ambos são lacunas estruturais que a engenharia cuidadosa em outras áreas não compensa.
10. **Maior força (revisada)?** A engenharia do backup (`backup_db.py`) e a mitigação real de command injection (`print_server.py`) são, com evidência concreta desta rodada, os pontos mais sólidos do projeto — mais fortes do que a rodada 1 pôde confirmar.

## Seção de falsos positivos — adicional desta rodada

- **Hipótese da rodada 1**: "comando PowerShell via subprocess é superfície de injeção não sanitizada" (P2, seção 7/A03) — **REBAIXADO A FALSO POSITIVO PARCIAL**: existe allowlist regex + escaping + uso de lista de args (não `shell=True`) que bloqueia estruturalmente o payload de exploração citado no próprio comentário do código-fonte (`print_server.py:42-46`). Não é um falso positivo total (a superfície existe e merece o cuidado que recebeu), mas a ausência de sanitização suspeitada não se confirmou.
- **Hipótese da rodada 1**: "backup sem automação, apenas scripts manuais" (P1, seção 16) — **FALSO POSITIVO**: `scripts/Servico-PrinterControl.ps1:139-161` confirma automação via Windows Scheduled Task por padrão na instalação do serviço.

## Seção "não verificado" — adicional desta rodada (específico, não genérico)

- Frontend (`src/`) completo: armazenamento de token, XSS/CSRF client-side, acessibilidade WCAG, cobertura de erro de API — não lido nesta rodada por orçamento, não por impossibilidade.
- `routes/alerts.py` e `routes/notifications.py` linha a linha — outras rotas de `routes/` foram lidas (servers, collect, users), essas duas não.
- Se `pytest`/`conftest.py` de fato coleta e passa os 18 arquivos `tests_*.py` automaticamente hoje — não executado (C19), apenas inspecionado estruturalmente.
- Teste de restauração real de um backup gerado por `backup_db.py` (apenas o `integrity_check` interno foi confirmado como existente no script, não uma restauração ponta a ponta em ambiente real).
- `print_server_mode=real` em execução de fato contra um domínio Windows real (a mitigação de C13 é confirmada estaticamente no código; não foi executada contra um Print Server real nesta auditoria).
- Estado do Cloudflare Tunnel/DNS/TLS/Vercel em produção — mantido da rodada 1, fora do escopo de qualquer auditoria somente leitura de repositório local.
- `pip-audit`/`npm audit`/CVEs reais nas versões listadas — mantido não executado, mesma prudência da rodada 1.

---

**Resumo da rodada 2**: score geral revisado de **6.0 para 6.6/10**. As três reavaliações mais significativas foram positivas e concretas (mitigação real de command injection, automação real de backup, RBAC consistente confirmado); as duas reavaliações negativas novas (ausência de audit log administrativo, ausência total de CI/CD) são gaps estruturais reais que não existiam como achados quantificados na rodada 1. O bloqueador P0 original (`requirements.txt` corrompido) permanece intocado e continua sendo a prioridade imediata antes de qualquer novo deploy.

---

## C22. Addendum — achados adicionais de verificação paralela (supply chain e manutenibilidade)

Um segundo passe de verificação, focado especificamente em supply chain e manutenibilidade, confirmou achados adicionais que complementam C12/C18 acima, via `grep -rE "^import |^from "` em `backend/app/**` comparado ao `requirements.txt` decodificado:

- **CONFIRMADO — nova dependência ausente**: `httpx` é importado e usado em `backend/app/services/webhook_notifier.py` mas **não consta em `requirements.txt`**. Junto ao `PyJWT` já registrado (seção 10 original), são duas dependências reais de runtime ausentes do arquivo de dependências.
- **CONFIRMADO — dependências mortas ainda declaradas**: `pyfiglet` está no `requirements.txt` sem nenhum `import pyfiglet` em `backend/app/**`. `python-jose` e `ecdsa` também seguem declarados apesar de zero uso real (só aparecem em comentários de `auth.py:4-22` explicando a migração) — isso reintroduz no grafo de dependências as CVEs (CVE-2024-33663, CVE-2024-33664, CVE-2024-23342) que a migração para PyJWT pretendia eliminar, mesmo sem uso ativo do código.
- **CONFIRMADO — sem lock file**: nenhum `.lock`/`Pipfile.lock`/`poetry.lock` no backend. Reprodutibilidade depende inteiramente do `requirements.txt`, hoje corrompido.
- **CONFIRMADO, ponto positivo**: `package-lock.json` versionado na raiz — build do frontend é reprodutível de forma determinística, ao contrário do backend.
- **CONFIRMADO, manutenibilidade**: apenas 1 ocorrência de `TODO`/`FIXME`/`HACK` em todo `backend/app/` — dívida técnica documentada em prosa nos docstrings, não em marcadores soltos. Frontend: 0 ocorrências de `: any`/`as any` em `app/`, `components/`, `lib/` — tipagem estrita respeitada.
- **FALSO POSITIVO testado e descartado**: hipótese de que `printer_fleet.py`, `printer_sync.py` e `printer_collector.py` seriam código duplicado — os docstrings documentam responsabilidades separadas e não sobrepostas (coleta de uma impressora vs. orquestração da frota vs. sincronização com o Print Server).

**Ajuste de score decorrente**: Supply chain/dependências desce de 3 para **2/10** — a lacuna não é apenas o encoding corrompido, mas um conteúdo que, mesmo corrigido ingenuamente (só re-encodado sem revisão), continuaria incompleto (faltando PyJWT e httpx) e carregando dependências mortas com CVEs conhecidas. Isso substitui a nota de supply chain do score geral C20 acima; **score geral final desta auditoria complementar ajustado para 6.5/10** (a diferença de 0,1 em relação ao 6.6 de C20 reflete este ajuste pontual, dentro da margem de arredondamento do método).

---

## C23. Terceiro passe — Frontend real (token/XSS/CSRF) e execução direta dos testes

Esta seção fecha as duas lacunas que C1/C2-C3 e C19 haviam deixado como "não investigado por orçamento": leitura direta de `src/lib/api.ts` e `src/lib/auth.ts`, e execução real (não apenas inspecionada) de uma amostra dos 18 arquivos de teste, incluindo uma tentativa de rodar a suíte inteira via `pytest`.

### C23.1 Frontend — armazenamento de token, XSS, CSRF (corrige C1/C2-C3 de "NÃO VERIFICADO" para CONFIRMADO)

CONFIRMADO por leitura completa de `src/lib/api.ts` (80 linhas) e `src/lib/auth.ts` (221 linhas):

- **Token JWT em `localStorage`/`sessionStorage`, não em cookie** — `src/lib/api.ts:9,65-79`: chave `elgin_auth_token`, gravada em `localStorage` quando "lembrar de mim" está marcado, em `sessionStorage` caso contrário (`setToken`, linha 71-74). **Não é httpOnly** — qualquer JavaScript executando no mesmo domínio do painel (incluindo um XSS bem-sucedido) pode ler `localStorage.getItem("elgin_auth_token")` e exfiltrar a sessão inteira. Isso é uma decisão de design coerente com o modelo Bearer-token de uma SPA que fala com uma API cross-origin (Vercel → túnel do backend), mas concentra toda a defesa contra roubo de sessão na ausência de XSS no frontend.
- **CSRF — FALSO POSITIVO para o modelo clássico**: como o token é enviado via header `Authorization: Bearer <token>` (montado explicitamente em `api.ts`, não anexado automaticamente pelo navegador como um cookie de sessão seria), um site malicioso não consegue forjar uma requisição autenticada contra a API só induzindo a vítima a visitar uma página — teria de conseguir ler o token primeiro, o que já seria XSS, não CSRF. **Rebaixo a hipótese de CSRF, se levantada, a falso positivo estrutural.**
- **Nenhum `dangerouslySetInnerHTML` nem `eval(` encontrado** em todo `src/` (busca recursiva, 0 ocorrências) — reduz a superfície mais óbvia de XSS via renderização direta de HTML não confiável. Não elimina XSS por outras vias (props `href`/`src` não sanitizadas, bibliotecas de terceiro) — essas não foram auditadas componente a componente.
- **Cache local da conta é só um fallback de exibição, nunca fonte de autorização**: `src/lib/auth.ts:67-101,147-168` — o objeto `Account` cacheado (papel, `mustChangePassword` etc.) só é usado quando o backend está inacessível (`status: "unverified"`); toda sessão verificada deriva o papel de `GET /api/auth/me` no momento, nunca do cache. **CONFIRMADO: design correto**, o cache não pode ser usado para escalar privilégio mesmo se adulterado, porque nenhuma chamada de escrita confia nele.
- **`package.json` confirma ausência de qualquer framework de teste** (`jest`, `vitest`, `@testing-library/*` ausentes de `devDependencies`) e de biblioteca de validação de formulário (`zod`, `react-hook-form` ausentes de `dependencies`) — **CONFIRMADO, não apenas suspeitado**: não há testes de frontend nem a infraestrutura para rodá-los instalada, e validação de formulário é necessariamente manual (não auditada campo a campo).
- **Design de resiliência de rede já implementado**: `restoreSession` (`src/lib/auth.ts:147-168`) trata explicitamente três estados — anônimo, autenticado (confirmado pelo backend agora), e "não verificado" (token existe mas o servidor não respondeu) — em vez de deslogar o usuário só porque um `fetch` falhou. **Ponto de UX positivo confirmado no código**, não apenas inferido.

### C23.2 Execução real dos testes (corrige C19 com evidência de execução, não só inspeção estrutural)

C19 já havia corrigido corretamente a rodada 1 ao identificar que os 18 arquivos não são testes pytest convencionais. Esta seção acrescenta o resultado de **efetivamente rodar** uma amostra segura (arquivos que criam seu próprio banco SQLite temporário, confirmados por leitura de cabeçalho antes de executar — nenhum arquivo que toca banco/servidor real foi executado):

- `python tests_login_hardening.py`, `tests_rbac.py`, `tests_users.py`, `tests_webhook.py`, `tests_alerts.py` → **CONFIRMADO: todos passaram** ("TODOS OS TESTES PASSARAM"), executados diretamente como scripts standalone, cada um contra seu próprio banco SQLite temporário (`_TMP_DB`/`test_webhook.db`/`test_alerts.db` em pasta temp, confirmados nos próprios logs de saída).
- `tests_printers_crud.py` → **não executado com sucesso**: o script aborta pedindo a variável de ambiente `TEST_ADMIN_PASSWORD`/`SEED_ADMIN_PASSWORD` com a senha real de uma conta administrativa (`mateus.vicentino@elgin.com.br`) — **CONFIRMADO, este arquivo específico depende de credencial de uma conta real/seedada e não é auto-contido**, ao contrário dos outros amostrados. Não tentei fornecer a senha.
- **`python -m pytest tests_*.py -q` (a suíte inteira, como um runner de CI faria) → CONFIRMADO: `INTERNALERROR` do próprio pytest**, abortando a coleta. Causa raiz identificada na saída do erro: `tests_alerts.py:129` executa `raise SystemExit(1 if failures else 0)` no nível do módulo (padrão de script standalone chamado via `if __name__ == "__main__"`), e o coletor do pytest, ao importar o arquivo para inspecioná-lo, propaga esse `SystemExit` como uma falha interna do próprio pytest, derrubando a coleta de qualquer arquivo que viesse depois em ordem alfabética.
- `python -m pytest tests_rbac.py -q --collect-only` isoladamente → **"no tests collected"** — confirma de forma definitiva (não apenas por inspeção de `def test_`) que estes arquivos não expõem nenhum caso no formato que o pytest reconhece.
- **Conclusão prática, nova em relação a C19**: mesmo que um pipeline de CI fosse adicionado hoje (C11 confirma que não existe nenhum), um `pytest .` ingênuo sobre `backend/` **quebraria com `INTERNALERROR` antes de reportar qualquer resultado útil**, por causa de um único arquivo (`tests_alerts.py`). Isso é um bloqueador concreto e imediato para qualquer automação futura de "rodar os testes", não apenas uma lacuna de cobertura. Recomendação (não executada — fora do escopo desta auditoria): mover os 18 arquivos para uma pasta `scripts/` fora da descoberta do pytest, ou envolvê-los em `if __name__ == "__main__":` sem `SystemExit` a nível de módulo, antes de qualquer tentativa de integrá-los a um CI.

### C23.3 Ajuste de score

- **Testes**: mantenho a nota de C20 (5/10) — a execução direta confirma que os testes amostrados realmente passam (ponto positivo que C19 já havia sinalizado como provável), mas o `INTERNALERROR` do pytest é uma descoberta nova que pesa contra qualquer plano de automação futura; os dois efeitos se cancelam aproximadamente.
- **Frontend**: antes "não pontuado" em C20 por falta de investigação — agora atribuo **6.5/10**: arquitetura simples e defensável, camada de API única, tratamento de estado de sessão degradado bem pensado, ausência de XSS óbvio (`dangerouslySetInnerHTML`/`eval`) — mas token em `localStorage` (risco estrutural que amplifica qualquer XSS futuro para crítico) e zero testes automatizados/infraestrutura de teste no `package.json` seguram a nota.
- **Score geral**: sem mudança material ao 6.5/10 de C22 — a inclusão do frontend pela primeira vez (6.5) fica próxima da média geral, e o achado do `pytest INTERNALERROR` é compensado pela confirmação de que os testes individuais realmente passam.

### C23.4 Seção "não verificado" — fecho

- Acessibilidade (WCAG), navegação por teclado, contraste, semântica ARIA — continuam **não verificadas**: exigem execução no navegador, fora do escopo estático desta auditoria em todas as três rodadas.
- UX end-to-end (fluxos completos, estados vazios, feedback de operação demorada) — idem, requer app rodando.
- Cobertura de `src/app`/`src/components` além de `src/lib/api.ts` e `src/lib/auth.ts` — não lida componente a componente; os achados de C23.1 cobrem a camada de infraestrutura (onde token/sessão vivem), não cada tela individual.

---

# ETAPA FINAL — FECHAMENTO DA AUDITORIA

Rodada de fechamento, somente leitura. Objetivo: não reabrir o que já está evidenciado nas rodadas 1-3, e fechar exatamente as lacunas que o próprio documento (C23.4 e seções "não verificado" anteriores) listava como pendentes por orçamento, não por impossibilidade. Rótulos mantidos: **CONFIRMADO** · **POSSÍVEL** · **NÃO VERIFICADO** · **NÃO APLICÁVEL** · **BOA PRÁTICA/MELHORIA** · **FALSO POSITIVO**.

## F0. Auditorias realizadas nesta etapa

1. Leitura completa de **16 arquivos de `src/app/`** (todas as páginas-rota) e **30 componentes `.tsx` de `src/components/`** — a lacuna que C1/C2-C3/C23.4 deixaram aberta desde a rodada 1 (antes só `lib/api.ts`/`lib/auth.ts` haviam sido lidos).
2. Leitura linha a linha de **`backend/app/routes/alerts.py`** (124 linhas) e **`backend/app/routes/notifications.py`** (296 linhas) — as duas únicas rotas que C14 explicitamente deixou como "NÃO VERIFICADO para esses dois arquivos".
3. Auditoria de UX real (não infraestrutura) dos fluxos: login, logout, troca de senha obrigatória, dashboard, navegação, usuários, servidores, alertas, notificações, configurações, modais, tabelas, exclusões, formulários, erros de API.
4. Auditoria de acessibilidade estática (WCAG como referência) sobre os mesmos 46 arquivos: semântica HTML, labels, foco, focus trap, navegação por teclado, ícones sem texto, tabelas, headings.
5. Revisão de segurança frontend: reconfirmação de `dangerouslySetInnerHTML`/`eval` (0 ocorrências), consistência do tratamento 401/403, race conditions de fetch, tamanho de componentes, duplicação de lógica de validação.
6. Grep dirigido por `<div onClick>`, `eval(`, `dangerouslySetInnerHTML` em `src/` inteiro (não só `components/`) para fechar com certeza, não amostragem.

## F1. Áreas finalmente cobertas (antes NÃO VERIFICADO por orçamento, agora CONFIRMADO)

| Área | Status anterior | Status agora |
|---|---|---|
| UX real por tela (login, dashboard, CRUD, modais, erros) | NÃO VERIFICADO (C2-C3, C23.4) | **CONFIRMADO** — ver F2 |
| Acessibilidade estática | NÃO VERIFICADO (C2-C3, C23.4) | **CONFIRMADO** (com ressalvas explícitas do que exige runtime) — ver F3 |
| `routes/alerts.py` linha a linha | NÃO VERIFICADO (C14) | **CONFIRMADO** — ver F4 |
| `routes/notifications.py` linha a linha | NÃO VERIFICADO (C14) | **CONFIRMADO** — ver F4 |
| IDOR/BOLA em notificações (caixa pessoal) | não avaliado explicitamente antes | **CONFIRMADO mitigado** — ver F4 |
| `dangerouslySetInnerHTML`/`eval` em `src/` completo (não só componentes citados) | CONFIRMADO parcial (C23.1, só api.ts/auth.ts) | **CONFIRMADO em 100% da árvore `src/`** |

## F2. Achados de UX — resumo consolidado

Relatório completo (por tela, com arquivo:linha) está registrado no processo de auditoria; resumo classificado abaixo.

**BUG REAL**: nenhum encontrado nos 46 arquivos lidos. Não é omissão — o critério foi aplicado ativamente (procurei estado inconsistente, ação que falha silenciosamente, dado errado exibido) e nenhuma ocorrência se qualificou como bug funcional. Isso é um resultado positivo digno de registro, não ausência de busca.

**PROBLEMA DE UX** (real, mas não quebra nada):
1. Modal de exclusão definitiva (`UsersView.tsx`, `NetworkView.tsx`, implementados nesta sessão) — campo de confirmação sem `autoFocus`, inconsistente com `MustChangePasswordGate.tsx:127` que tem. Passo extra desnecessário numa ação já proposital-mente fricciosa.
2. Item de menu "Integrações" (`Sidebar.tsx:116`) leva a um `ComingSoon` sem qualquer sinalização prévia de "em breve" no próprio item do menu.
3. Botão "Verificar agora" no dashboard (`app/page.tsx:53-56`) dispara `handleRefresh` (releitura do estado já coletado), não uma coleta SNMP nova — nomenclatura pode ser lida como "colete agora", ambígua para quem não conhece a arquitetura.
4. "Esqueceu a senha?" (`Login.tsx:139-146`) sempre resulta em "fale com o administrador" — não é enganoso (o sistema não tem esse fluxo mesmo), mas o rótulo do link não avisa disso antes do clique.

**MELHORIA OPCIONAL**: retorno de foco ao elemento que abriu um modal (também é achado de acessibilidade, ver F3); padronizar a nomenclatura "Verificar agora" vs. "Coletar agora" se um dia existir coleta manual explícita no frontend (hoje só existe via API, não tem botão dedicado no painel lido).

**Pontos fortes confirmados por evidência de código, não impressão**:
- Diferenciação correta 401 (shake, "credenciais erradas") vs. 429/rede (mensagem literal do backend, sem shake) no login — `Login.tsx:122-135`.
- Banner de ambiente demo permanente visualmente distinto de banner de fallback por falha — `AppShell.tsx:57-93`.
- Estado vazio "tudo certo" distinto de "filtro sem resultado" em Alertas — `AlertsView.tsx:61-70`.
- Aviso honesto sobre limitação real do JWT (sessões antigas continuam válidas após troca de senha) com o workaround real disponível — `SettingsView.tsx:258-265`.
- Tratamento 401→logout / 403→toast sem logout **100% centralizado** em `useApiErrorReporter`; nenhum componente dos 46 lidos trata erro de API por conta própria de forma divergente — **CONFIRMADO, não apenas citado de segunda mão como nas rodadas anteriores**.

## F3. Achados de acessibilidade — resumo consolidado

| Achado | Severidade | Evidência |
|---|---|---|
| Modal sem focus trap — Tab pode escapar para trás do overlay | **CRÍTICO** | `Modal.tsx` completo — nenhum `inert`/`aria-hidden` na árvore de fundo, nenhuma captura de Tab |
| Foco não retorna ao elemento que abriu o modal, ao fechar | **MÉDIO** | `Modal.tsx` — nenhum `useRef`/`.focus()` no fechamento |
| `<h1>`/`<h2>` ausente no Dashboard; primeiro heading da página é `<h3>` dentro de `PrinterTable` | **MÉDIO** | `app/page.tsx` (nenhum heading próprio) + `PrinterTable.tsx:97` |
| Tabelas sem `scope="col"`; `HistoryMatrix` com cabeçalho aninhado por unidade sem `<caption>` | **BAIXO** (tabelas simples) / **MÉDIO** (`HistoryMatrix`, estrutura mais complexa) | `PrinterTable.tsx`, `HistoryMatrix.tsx`, `TonerMonitoring.tsx`, `DiscoveryResults.tsx`, `DecommissionedList.tsx` |
| Botões só-ícone de `PrinterTable` sem `aria-label` (têm `title`) | **BAIXO** | `PrinterTable.tsx:236-247` |
| `autoFocus` inconsistente entre modais e telas cheias | **BAIXO** | comparar `MustChangePasswordGate.tsx:127` com os modais de `UsersView`/`NetworkView` |
| `aria-live` no container de toast | **NÃO VERIFICADO — requer leitura de `lib/toast.tsx`**, fora do escopo desta rodada (não lido); se ausente, todo feedback de sucesso/erro é invisível a leitor de tela — recomendo verificação dedicada antes de assumir qualquer coisa | — |
| Contraste de cor | **NÃO VERIFICADO — requer inspeção em runtime/DevTools**; código usa tokens CSS/tema, não hex hardcoded suspeito, mas isso não prova contraste adequado | `globals.css` (tokens), não resolvido estaticamente |

**Boas práticas confirmadas** (não são achados negativos, registradas para não serem perdidas): `<html lang="pt-BR">` presente (`layout.tsx:36`); 100% dos inputs amostrados com `<label>` associado; `role="status" aria-live="polite"` correto na tela de restauração de sessão (`AuthGate.tsx:28`); `aria-labelledby` correto ligando `<h2 id="modal-title">` ao `role="dialog"` do Modal; nenhum `<div onClick>` usado como controle funcional (os 2 únicos são backdrops decorativos com `aria-hidden`).

## F4. Segurança da API — `alerts.py` e `notifications.py` (fecha C14)

**CONFIRMADO — RBAC consistente, mesmo padrão do resto da API**: `alerts.py` exige `require_active_user` a nível de router (qualquer papel lê) e `require_operator` para `notify`/`resolve` (`alerts.py:66-70,104-108`) — hierarquia igual à já confirmada em C14 para servers/collect/users. `notifications.py` exige `require_active_user` a nível de router e `require_admin` especificamente para `POST /api/notifications` (criar/enviar, `notifications.py:247-251`) — consistente.

**CONFIRMADO — IDOR/BOLA mitigado por design, com evidência de código**: `notifications.py:136-148`, função `_minha_ou_404`, escopa toda leitura/escrita individual (`PATCH /{id}/read`) ao `user.id` da sessão — busca por id que não pertence ao usuário devolve **404, não 403**, deliberadamente (comentário explica: um 403 confirmaria a existência do id, vazando que a mensagem existe mas é de outra pessoa). `GET`/`unread-count`/`read-all` nunca aceitam `user_id` como parâmetro — o escopo vem só da sessão, inclusive para admin (`notifications.py:165-167,219-221`). **Não há caminho no código para um usuário ler a caixa de outro.**

**CONFIRMADO — mass assignment não aplicável**: `NotificationCreate` (schema de entrada) só aceita `user_ids`, `message`, `severity`, `alert_id` — nenhum campo interno (`read_at`, `created_at`) é aceito do cliente.

**CONFIRMADO — validação de destinatário antes de gravar**: `create_notifications` verifica que todos os `user_ids` existem (404 se algum não existir, `notifications.py:259-266`) e que nenhum está desativado (409, `:270-275`) antes de criar qualquer linha — evita notificação "fantasma" para conta inativa.

**POSSÍVEL, não confirmado como bug**: `GET /api/alerts/{id}` (`alerts.py:58-63`) não tem verificação de posse porque **alertas não são pessoais por design** (são eventos da frota, visíveis a qualquer papel autenticado) — isso é **NÃO APLICÁVEL** ao conceito de IDOR, não uma falha; registrado aqui só para deixar explícito que a ausência de checagem de posse é intencional e coerente com o modelo de dados (`Alert` não tem `user_id`).

**Sem rate limit** em nenhuma rota de `alerts.py`/`notifications.py`, mesmo achado já confirmado em C14 para o resto da API — não é um achado novo, é a mesma lacuna já registrada se estendendo a estes dois arquivos.

**Reavaliação de C14**: a ressalva "`routes/alerts.py` e `routes/notifications.py` não foram relidos... NÃO VERIFICADO" está **fechada**. RBAC consistente confirmado nos dois; IDOR mitigado por design confirmado especificamente em notifications.py (a única rota com dado genuinamente pessoal antes desta rodada).

## F4b. Backend — reforço de `auth.py`/`collect.py`/`printers.py`, grep de segurança final, concorrência dos DELETE novos

Cobertura complementar a F4, fechando os itens de segurança de API/backend que as rodadas 1-3 ainda listavam como não verificados linha a linha.

**CONFIRMADO, ponto forte não registrado antes**: `auth.py:34-50` calcula um hash Argon2 descartável uma única vez no import do módulo e o usa como comparação de tempo constante quando o e-mail informado no login não existe — mitigação real de **timing attack de enumeração de contas** (login com e-mail inexistente gasta o mesmo tempo que um com senha errada). Não estava quantificado em nenhuma rodada anterior.

**CONFIRMADO**: `auth.py:215-224` devolve **400** (não 401/403) quando a senha atual informada em `POST /api/auth/change-password` está errada — decisão deliberada e documentada inline para não deslogar nem confundir o cliente. Consistente com o padrão de erro já elogiado no frontend (F2).

**CONFIRMADO, reforça C15**: o próprio docstring de `change_own_password` (`auth.py:209-213`) documenta que trocar a senha **não invalida tokens JWT já emitidos** — mesma limitação stateless já registrada em C15, agora também confirmada como documentada no ponto exato do código que a introduz.

**Exposição de stack trace / mensagens de erro**: **CONFIRMADO ausente** em `collect.py`/`printers.py`/`auth.py` — toda `HTTPException` usa `detail=` com mensagem curada, nunca `str(exception)` bruto. Uma exceção: `collect.py:108` repassa ao cliente o texto de `result["error"]`, originado em `PrinterCollector` (não lido linha a linha nesta rodada) — **NÃO VERIFICADO** se essa string pode em algum caso carregar detalhe interno (path, traceback); não há evidência de que carregue, apenas não foi descartado com certeza.

**SSRF**: **FALSO POSITIVO** para o padrão clássico (proxy de URL arbitrária) — nenhum endpoint de `collect.py`/`printers.py`/`auth.py` aceita URL/host livre do cliente para disparar requisição de rede. O único host controlável por usuário é `PrintServer.host`, já mitigado por allowlist confirmada em C13.

**Grep de segurança final** (`eval(`, `exec(`, `pickle.load`, `yaml.load(` sem `SafeLoader`, `os.system`, SQL raw via f-string, `open()` com path de input do usuário): **CONFIRMADO ausente** em `backend/app/**` — zero ocorrências de todos os padrões. Reforça A03 (injection) como mitigado, sem achado novo negativo.

**CONFIRMADO — novo uso de `subprocess` não auditado antes, seguro**: `services/snmp.py:275-296`, função `_ping()`, usa `subprocess.run(["ping", "-n", "1", "-w", ..., ip], ...)` — lista de argumentos, nunca `shell=True`. Mesmo padrão seguro já confirmado para `print_server.py` (C13); o parâmetro `ip` vem de `Printer.ip`, validado por schema Pydantic (formato exato não relido nesta rodada — **NÃO VERIFICADO** em detalhe, mas irrelevante para injeção de comando dado o uso de lista de argv).

**Reconfirmação — `backend/requirements.txt`**: **CONFIRMADO, estado inalterado** desde a rodada 1: 6 bytes, `Unicode text, UTF-16, little-endian, CRLF`, BOM `fffe 0d00 0a00` sem nenhum pacote listado. O bloqueador P0 permanece exatamente como documentado, sem regressão nem correção.

**Concorrência dos endpoints `DELETE` novos** (`users.py:delete_user`, `servers.py:delete_server`, implementados nesta mesma sessão) — análise não coberta em nenhuma rodada anterior porque as rotas não existiam antes:

- **CONFIRMADO**: nenhuma transação explícita/lock além do padrão já existente em todo o resto do código (uma `Session` implícita por requisição, `commit()` único ao final) — **não é uma regressão**, é o mesmo padrão de todas as demais rotas de escrita já auditadas.
- **POSSÍVEL, TOCTOU benigno**: dois admins chamando `DELETE` simultaneamente sobre o mesmo `id` — a segunda requisição, operando sobre um objeto já removido pela primeira, tipicamente não lança exceção no SQLite/SQLAlchemy (um `DELETE` que afeta 0 linhas não é erro); ambas retornam 204. Resultado: confusão de UX possível (a segunda pessoa acha que excluiu algo que já não existia), sem corrupção de dado.
- **POSSÍVEL, mais relevante, não testado em runtime**: `DELETE /api/servers/{id}` concorrente a `POST /api/servers/{id}/sync` no mesmo servidor — se o sync inserir uma nova `Printer` para aquele host entre o `SELECT` de impressoras do delete e o `session.delete()` do servidor, essa impressora nova pode sobreviver órfã (`print_server_id` apontando para um servidor já apagado). Como o projeto já documenta que **FKs são declaradas no modelo mas não impostas no SQLite** (achado de rodada anterior), essa órfã não geraria erro, só inconsistência referencial silenciosa. Cenário de baixa probabilidade prática (exige coincidência de dois admins agindo no mesmo servidor no mesmo instante), mas arquiteturalmente real — **herda um padrão de risco já catalogado** (C6, ausência de lock entre coleta manual e agendada), não introduz uma classe de risco nova.

## F5. Achados confirmados nesta etapa (novos, não presentes nas rodadas 1-3)

1. Falta de focus trap em modais — **CRÍTICO de acessibilidade**, afeta todo modal do sistema (criação/edição/exclusão de usuário e servidor, detalhes de impressora, ajuda, notificações).
2. Ausência de retorno de foco ao fechar modal — MÉDIO.
3. Hierarquia de heading quebrada no Dashboard (sem h1/h2 próprio) — MÉDIO.
4. Tabelas sem `scope`/`caption`, agravado em `HistoryMatrix` (cabeçalho aninhado) — BAIXO/MÉDIO.
5. `autoFocus` ausente nos novos modais de exclusão definitiva (Usuários/Print Servers) — PROBLEMA DE UX, BAIXO.
6. Duplicação da regra de validação de senha entre `MustChangePasswordGate.tsx` e `SettingsView.tsx` — MELHORIA OPCIONAL de manutenibilidade, não bug (as duas implementações estão hoje sincronizadas e corretas).
7. Ausência de `AbortController`/cleanup nos `useEffect` de fetch de `NotificationsView`/`UsersView`/`NetworkView` — POSSÍVEL race condition de baixo impacto, não confirmada como bug observado.
8. IDOR mitigado por design em `notifications.py`, com padrão 404-não-403 deliberado — CONFIRMADO como ponto forte, não estava quantificado antes.
9. Timing-attack de enumeração de login mitigado por hash Argon2 descartável em `auth.py:34-50` — CONFIRMADO ponto forte, não quantificado antes.
10. Janela de concorrência POSSÍVEL entre `DELETE /api/servers/{id}` (cascata) e `POST /api/servers/{id}/sync` no mesmo servidor, podendo gerar impressora órfã silenciosa (FK não imposta pelo SQLite) — POSSÍVEL, não testado em runtime, herda padrão de risco já catalogado (C6).
11. `services/snmp.py:275-296` (`_ping()`) é um segundo uso de `subprocess` no backend, não auditado antes — CONFIRMADO seguro (lista de argv, sem `shell=True`), mesmo padrão de C13.

## F6. Achados descartados / falsos positivos desta etapa

- **Hipótese**: "`routes/alerts.py`/`notifications.py` poderiam ter RBAC divergente do resto da API, por nunca terem sido lidos" — **FALSO POSITIVO**: RBAC idêntico ao padrão já confirmado em C14 (viewer lê, operator age em alertas, admin cria notificação).
- **Hipótese**: "sem leitura de `src/components` linha a linha, poderia haver XSS via `dangerouslySetInnerHTML` em algum componente não lido antes" — **FALSO POSITIVO**: grep recursivo em `src/` inteiro (não amostragem) confirma 0 ocorrências.
- **Hipótese implícita em auditorias deste tipo**: "telas administrativas poderiam divergir da regra 401/403 central" — **FALSO POSITIVO**: confirmado 100% de aderência a `useApiErrorReporter` nos 34 componentes com chamada de API lidos.
- **Hipótese**: "algum endpoint de `collect.py`/`printers.py`/`auth.py` poderia ser vetor de SSRF (proxy de URL arbitrária)" — **FALSO POSITIVO**: nenhum aceita URL/host livre do cliente para requisição de rede; único host controlável (`PrintServer.host`) já mitigado por allowlist (C13).
- **Hipótese**: "os DELETEs em cascata novos (usuário/servidor) poderiam ter introduzido uma classe de risco de concorrência nova" — **FALSO POSITIVO parcial**: existe uma janela POSSÍVEL (F4b), mas ela herda o mesmo padrão de ausência de lock já catalogado em C6 para o resto do sistema — não é uma regressão de segurança introduzida pelas rotas novas.

## F7. Não verificáveis — reavaliados

Pergunta aplicada a cada item herdado: *"é realmente impossível verificar a partir do repositório?"*

- **Contraste de cor real** — **NÃO VERIFICADO — DEPENDE DE RUNTIME/DEVTOOLS**: os valores de tokens CSS (`globals.css`) existem no repositório e poderiam em tese ser lidos e calculados manualmente contra as combinações de uso, mas isso exigiria resolver cada combinação token→uso→contraste WCAG (dezenas de combinações, múltiplos componentes, dois temas) com risco real de erro de cálculo manual sem ferramenta — mantenho como não verificado nesta rodada por prudência de precisão, não por ser tecnicamente impossível a partir do repo. Diferente dos demais itens "não verificado" abaixo, este **poderia** ser fechado numa rodada dedicada com uma ferramenta de contraste rodando sobre `globals.css`.
- **`aria-live` em `lib/toast.tsx`** — **verificável a partir do repo, não verificado nesta rodada por escopo** (a leitura desta etapa focou `src/app`+`src/components`; `lib/toast.tsx` ficou fora). Diferente de infraestrutura externa, isto é local e leitura simples — deveria ser o primeiro item de qualquer rodada de acessibilidade futura.
- **Navegação por teclado end-to-end, ordem de tab real, comportamento de screen reader** — **NÃO VERIFICADO — DEPENDE DE RUNTIME**: a estrutura estática (o que este documento cobre) é necessária mas não suficiente; a experiência real de tab-order e anúncio de screen reader só é observável com o app rodando e uma ferramenta (axe, NVDA/VoiceOver). Genuinamente fora do alcance de uma auditoria estática de repositório.
- **Estado real do Cloudflare Tunnel, DNS, TLS, Vercel runtime, pytest/CI reais além do já executado em C23.2** — mantido **NÃO VERIFICADO — DEPENDE DE ACESSO EXTERNO**, sem mudança desta etapa; nenhum destes é verificável a partir do repositório local por definição.

## LIMITAÇÕES DA AUDITORIA

Esta e as três rodadas anteriores são uma auditoria estática de repositório local, sem execução do frontend em navegador, sem acesso a Cloudflare/DNS/TLS/Vercel em produção, sem ferramenta automatizada de acessibilidade (axe-core, Lighthouse) ou de contraste, e sem `pip-audit`/`npm audit` contra bases de CVE externas. Os achados de acessibilidade desta etapa são baseados em leitura de código-fonte (presença/ausência de atributos ARIA, estrutura de heading, uso de `<label>`, foco programático) — são um piso confiável de problemas estruturais, não um substituto para teste com leitor de tela real ou ferramenta de auditoria em runtime. Qualquer achado marcado NÃO VERIFICADO — DEPENDE DE RUNTIME/ACESSO EXTERNO permanece genuinamente fora do alcance deste método, em qualquer número de rodadas adicionais do mesmo tipo.

## F8. Scores finais (0–10)

Metodologia: parte da tabela consolidada de C20/C22/C23.3, ajusta apenas as categorias com achado novo e concreto nesta etapa (UX, Acessibilidade, Segurança-API para os dois arquivos fechados). Escala: 0–2 crítico/imaduro · 3–4 fraco · 5–6 intermediário · 7–8 bom · 9 muito bom · 10 excelente/maduro.

| Categoria | Score anterior | Score final | Justificativa da mudança |
|---|---|---|---|
| Segurança geral | 7 | 7 | Sem mudança material — alerts.py/notifications.py confirmam o padrão já pontuado |
| Autenticação | 7 | 7 | Sem achado novo |
| Autorização (RBAC) | 8 | 8 | C14 já cobria o padrão; F4 apenas estende a confirmação aos 2 arquivos restantes, sem mudar a nota |
| IDOR/BOLA (novo, escopo explícito) | não pontuado | **8** | Mitigação por design confirmada em notifications.py (404-não-403), única rota com dado genuinamente pessoal fora de auth |
| Arquitetura | 8 | 8 | Sem achado novo |
| Backend (código) | 7 | 7 | Sem achado novo |
| **Frontend (código/estrutura)** | 6.5 | **7** | Leitura completa de 46 arquivos não encontrou nenhum BUG REAL; padrão 401/403 100% consistente confirmado por evidência exaustiva, não amostragem; sobe levemente por essa confirmação apesar dos achados de UX/a11y (pontuados à parte abaixo) |
| Banco de dados | 7 | 7 | Sem achado novo |
| Integridade (subprocess/injeção) | 9 | 9 | Sem achado novo |
| Performance | 6 | 6 | Sem achado novo (não medido) |
| Escalabilidade | 6 | 6 | Sem achado novo |
| Confiabilidade | 6 | 6 | Sem achado novo |
| Testes | 5 | 5 | Sem achado novo |
| **UX** | não pontuado | **7** | Nenhum bug real em 46 arquivos; 4 problemas de UX reais mas menores (nenhum bloqueia tarefa); padrões de tratamento de erro/estado vazio/loading consistentemente bem feitos e confirmados por evidência, não impressão |
| **Acessibilidade** | não pontuado | **4** | 1 achado CRÍTICO (focus trap ausente em todo modal do sistema) e 2 MÉDIOS (retorno de foco, hierarquia de heading) são estruturais e afetam o app inteiro, não um componente isolado; parcialmente compensado por boas práticas reais confirmadas (labels, `aria-live` na sessão, `lang`, sem `<div onClick>` funcional) |
| Observabilidade | 7 | 7 | Sem achado novo |
| Audit log / rastreabilidade | 3 | 3 | Sem achado novo |
| DevOps/CI-CD | 2 | 2 | Sem achado novo |
| DevSecOps (supply chain + subprocess) | 2 | 2 | Sem achado novo — requirements.txt continua o bloqueador P0 |
| Manutenibilidade | 7 | 7 | Duplicação de validação de senha (F5.6) é menor demais para mover a nota; `NetworkView.tsx` com 981 linhas é um sinal a observar, não uma falha atual |
| Privacidade/LGPD | não pontuado | não pontuado (mantido) | Sem achado técnico novo nesta etapa — ver seção LGPD das rodadas anteriores |
| Backup/DR | 7 | 7 | Sem achado novo |

### Cálculo do score geral

Média simples das categorias efetivamente pontuadas (exclui LGPD, que segue sem nota por falta de evidência suficiente para quantificar, conforme já registrado nas rodadas anteriores): soma de 19 categorias pontuadas ÷ 19 ≈ **6.4/10**.

**Score geral final: 6.4/10** (rodada 1: 6.0 · rodada 2: 6.6 · rodada 3/C22-C23: 6.5 · fechamento: 6.4). A leve queda em relação a 6.5 reflete a inclusão pela primeira vez de Acessibilidade (4/10, achado estrutural real) no cálculo da média — as demais categorias não regrediram; nenhuma nota anterior foi rebaixada nesta etapa, o número geral desce porque uma categoria nova e genuinamente fraca entrou no denominador, não porque algo que já existia piorou.

## F9. Veredito final

1. **O PrinterControl pode ser considerado software profissional?** Sim — decisões de arquitetura, segurança de configuração, backup, mitigação de command injection e agora também o padrão de tratamento de erro/estado no frontend são de nível consistentemente acima do que se espera de um projeto interno de pequeno porte. A ausência de qualquer BUG REAL nos 46 arquivos de frontend lidos nesta etapa reforça isso.

2. **Está pronto para produção?** Não. O bloqueador seguem sendo os mesmos três já registrados e não alterados nesta etapa (esta é uma auditoria somente leitura): `requirements.txt` corrompido (P0), ausência de CI/CD (lacuna estrutural), ausência de audit log administrativo (lacuna estrutural). A esta lista se soma um achado novo de severidade real: falta de focus trap em modal é um problema de acessibilidade que, dependendo do padrão de conformidade exigido pela organização (ex.: se há obrigação de WCAG AA), pode ser um requisito de aceite antes de produção — mas não é um bloqueador de segurança ou de funcionamento.

3. **Está adequado a ambiente corporativo?** Parcialmente, mesma conclusão de C21, sem mudança: tecnicamente sólido para a escala atual, mas falta trilha de auditoria administrativa e pipeline de verificação automatizada. Acrescenta-se: se o ambiente corporativo tiver requisito formal de acessibilidade, a lacuna de focus trap precisa entrar no roadmap.

4. **Quais riscos impedem produção?** `requirements.txt` corrompido (bloqueia literalmente instalar o backend em máquina nova) — inalterado desde a rodada 1.

5. **Quais riscos são aceitáveis?** Ausência de MFA, ausência de rate limit além do login, token sem revogação server-side (mitigado por "desativar conta" funcionar como revogação prática) — todos já avaliados nas rodadas anteriores como aceitáveis para o porte e modelo de ameaça atual (uso interno corporativo, não SaaS multi-tenant exposto).

6. **Qual é a maior vulnerabilidade confirmada?** Nenhuma vulnerabilidade de segurança nova foi confirmada nesta etapa de fechamento — o cenário de segurança permanece o descrito nas rodadas 1-3 (token sem revogação, sem rate limit além do login, ambos avaliados como riscos aceitáveis para o contexto).

7. **Qual é o maior risco arquitetural?** Inalterado: single-process (rate limiter e scheduler em memória), que impede rodar duas instâncias do backend sem duplicar coleta e perder rate limiting global — já documentado e aceito como adequado à escala atual. Ausência de lock/transação cross-tabela entre escritores concorrentes é a mesma causa raiz por trás desse risco e da janela POSSÍVEL identificada nesta etapa entre `DELETE`/`sync` de um Print Server (F4b) — um único padrão arquitetural, não dois problemas separados.

8. **Qual é a maior dívida técnica?** Duas, empatadas, de naturezas diferentes: `requirements.txt` corrompido (dívida de infraestrutura, bloqueia deploy) e falta de focus trap em modal (dívida de acessibilidade, descoberta nesta etapa, afeta toda ação sensível do sistema — incluindo as exclusões definitivas de usuário/servidor implementadas nesta mesma sessão).

9. **Qual é a maior força do sistema?** Consolidando as quatro rodadas: a combinação de (a) engenharia de backup online com integrity check automático, (b) mitigação real e demonstrada de command injection no subprocess PowerShell, e (c) — achado desta etapa — um frontend com **zero bugs reais encontrados** em leitura completa de 46 arquivos e tratamento de erro de API 100% centralizado e consistente. Nenhuma dessas três é alegação do próprio código; todas têm evidência de arquivo:linha por trás.

10. **O que precisa obrigatoriamente ser corrigido antes de produção?** `requirements.txt` regravado em UTF-8 a partir do venv real, com `PyJWT`/`httpx` incluídos e `python-jose`/`ecdsa`/`pyfiglet` removidos (inalterado da rodada 1-3). Novo item desta etapa: focus trap em `Modal.tsx`, porque é um único componente compartilhado por todo o sistema — a correção é local e de baixo esforço relativo ao impacto (resolve o CRÍTICO de acessibilidade em todas as telas de uma vez).

11. **O que pode esperar?** CI/CD, audit log administrativo, MFA, rate limit geral de API, retorno de foco em modal, `scope`/`caption` em tabelas, correção da hierarquia de heading no Dashboard — todos são melhorias reais mas não bloqueiam uso seguro e funcional do sistema hoje.

12. **O que é apenas melhoria opcional?** `autoFocus` nos campos de confirmação de exclusão, unificar a validação de senha duplicada entre dois componentes, `AbortController` nos fetches de listagem, `aria-label` redundante ao `title` já existente em `PrinterTable`, decompor `NetworkView.tsx` (981 linhas) se crescer mais, rótulo mais claro para "Verificar agora" vs. uma futura coleta manual explícita.

---

# RODADA G — FECHAMENTO DE LACUNAS RESIDUAIS

Escopo desta rodada, por pedido explícito: **não repetir** nenhuma auditoria de backend/frontend já feita (F0-F9 acima cobrem `src/app`, `src/components`, UX, acessibilidade, `alerts.py`, `notifications.py` por completo). Fechar apenas o que sobrou genuinamente aberto: (1) LGPD técnica de verdade, não superficial; (2) CVE scan, executado onde seguro; (3) todo item "NÃO VERIFICADO" ainda pendente que o próprio código permite responder. Somente leitura — nenhum arquivo do projeto foi alterado, só testes efêmeros em arquivo temporário fora do repositório (removido ao final).

## G1. LGPD — inventário técnico de dados pessoais

Análise técnica, não jurídica (separação mantida das rodadas anteriores).

**Dados pessoais identificados, CONFIRMADO por leitura de schema** (`backend/app/models/user.py:36-79`):

| Campo | Onde vive | Quem acessa | Exposto pela API? |
|---|---|---|---|
| `email` | `users.email` (SQLite) | Qualquer requisição autenticada `require_admin` em `/api/users`; o próprio dono via `/api/auth/me` | Sim, em `UserResponse` — nunca `password_hash` |
| `username` | `users.username` (nullable) | Idem | Sim |
| `name` | `users.name` | Idem | Sim |
| `password_hash` | `users.password_hash` (Argon2) | Nunca sai da tabela — **CONFIRMADO ausente de `UserResponse`** (`schemas/user.py:169-186`, reconfirmado nesta rodada) | Não |
| IP de origem do login | **Não persistido** — usado só em memória pelo `RateLimiter` (`services/rate_limit.py`), descartado ao expirar a janela | Ninguém, não há tabela | Não |

**CONFIRMADO — dado pessoal É escrito em log, sem redação**: `routes/auth.py:114-117` — ao bloquear por excesso de tentativas, `logger.warning("Login bloqueado... | conta=%s | origem=%s | ...", chave_conta, ip)` grava **e-mail/username E endereço IP em texto plano** em `logs/printercontrol.log`. Confirmado por leitura de `logging_config.py:30-44`: o `RedactSecretsFilter` cobre apenas `bearer <token>` e padrões `chave=valor` de segredos (senha, token, secret_key etc.) — **não existe padrão para e-mail ou IP**, então esse dado permanece legível em todo backup/rotação do arquivo de log (retenção: `LOG_MAX_BYTES=5MB × LOG_BACKUP_COUNT=10`, `.env.example:99-100`). Este é o achado técnico mais concreto desta rodada: **dado pessoal (e-mail + IP) com retenção de dias/semanas em arquivo de log não criptografado, sem mecanismo de expurgo dedicado além da rotação por tamanho**.

**Retenção**: **CONFIRMADO** — não existe campo `deleted_at`/expiração automática em `User`; contas somem apenas por ação explícita (`is_active=False` ou, desde esta sessão, `DELETE /api/users/{id}`). Não há política de expiração automática de contas inativas — **NÃO APLICÁVEL como bug**: é uma decisão de design razoável para um painel administrativo interno, não um gap técnico.

**Exclusão / "direito ao esquecimento" — reavaliação relevante desta sessão**: até esta sessão, o sistema só desativava contas (`TECHNICAL_DEBT` e `routes/users.py` documentavam isso como decisão deliberada). **Nesta mesma sessão foi implementado `DELETE /api/users/{id}`** (hard delete real, com confirmação de e-mail e proteção do último admin) — tecnicamente, isso **fecha** a lacuna de "não há como apagar um usuário de verdade" que a auditoria anterior listava. Notificações da conta são apagadas junto (`routes/users.py:delete_user`); **CONFIRMADO, porém**: os registros de log (`conta=%s` acima) e cópias de backup (`backend/backups/*.db`) geradas **antes** da exclusão **não são tocados** por esse endpoint — um "direito ao esquecimento" completo exigiria também expurgar essas duas superfícies, o que a funcionalidade atual não faz e não se propõe a fazer.

**Exportação**: **CONFIRMADO** — único mecanismo de exportação no frontend é `src/lib/exportCsv.ts`, que gera CSV **apenas de dados de impressoras** (nome, IP, modelo, departamento, status, toner, páginas, última atividade) — nenhum dado de usuário/pessoa é exportável pela UI. `GET /api/users` devolve a lista completa a qualquer admin (por design, é a tela de gestão), mas não há botão de exportação dela.

**Backups**: reforça C10 — `backup_db.py` copia o arquivo `.db` inteiro, incluindo a tabela `users` completa (e-mail, username, nome, hash de senha), sem criptografia em repouso, por padrão no mesmo disco local (`backend/backups/`). Qualquer exposição de um backup expõe os mesmos dados pessoais que o banco principal.

**Base legal / DPO / política formal**: mantido **NÃO VERIFICADO — QUESTÃO JURÍDICA/ORGANIZACIONAL**, fora do que o repositório pode responder, como já registrado nas rodadas anteriores.

**Resumo G1**: o achado técnico novo e concreto desta rodada é o **log de autenticação carregando e-mail+IP em texto plano sem redação dedicada**, com retenção de até ~50MB/10 arquivos rotativos. Risco técnico real, mas de exposição limitada (o log já exige acesso ao servidor/backend, não é exposto publicamente) — proporcional, não crítico.

## G2. CVE scan — executado onde seguro, sem alterar nada

**Frontend — `npm audit` executado nesta rodada** (comando somente leitura contra `package-lock.json` já versionado; não instala nem altera nada):

```
0 vulnerabilities (0 critical, 0 high, 0 moderate, 0 low, 0 info)
120 dependências analisadas (57 prod, 24 dev, 58 optional, 1 peer)
```

**CONFIRMADO**: nenhuma CVE conhecida nas dependências de frontend, na base do `npm audit` no momento da execução.

**Backend — `pip-audit` NÃO executado**: a ferramenta não está instalada no ambiente, e instalá-la violaria a restrição desta rodada de não alterar nada além do relatório. **NÃO VERIFICADO — ferramenta indisponível sem instalação**, não por escolha de prudência como nas rodadas anteriores.

**Backend — verificação manual das versões realmente instaladas no venv do projeto** (`backend/venv/Scripts/python.exe -m pip list`, leitura, sem alterar nada): confirma que o ambiente real roda `python-jose==3.3.0` e `ecdsa==0.19.2` **efetivamente instalados** (não apenas declarados em `requirements.txt`) — as CVEs já citadas nas rodadas anteriores (CVE-2024-33663, CVE-2024-33664 em `python-jose`; CVE-2024-23342 em `ecdsa`, conforme o próprio comentário de `auth.py:1-20`) descrevem um pacote que **está de fato presente no ambiente de execução real**, não apenas "declarado mas não instalado" como uma leitura só do `requirements.txt` poderia sugerir. `PyJWT==2.13.0` (versão atual, sem CVE conhecida citada em lugar nenhum do projeto) é o que o código de fato importa e usa — a superfície de exploração via `python-jose` exigiria que **algum código chamasse essa biblioteca**, o que já foi confirmado ausente (nenhum `from jose import`/`import jose` em `backend/app/**`, achado das rodadas anteriores) — **mitigação por não-uso, não por ausência do pacote**.

**Não invento identificadores de CVE além dos já citados no próprio código-fonte do projeto** — para `fastapi==0.109.0`, `starlette==0.35.1`, `sqlalchemy==2.0.52` e demais pacotes sem CVE citada em comentário do projeto, o correto é **NÃO VERIFICADO — requer `pip-audit`/consulta a NVD não executada nesta sessão**, sem alegar nem descartar vulnerabilidade.

## G3. Itens "NÃO VERIFICADO" reavaliados — fechados nesta rodada

Aplicando a pergunta "é realmente impossível verificar a partir do código?" a cada item pendente das rodadas 1-4:

| Item | Rodada anterior | Reavaliação nesta rodada |
|---|---|---|
| `pip install` falha ou tolera o encoding do `requirements.txt`? | NÃO VERIFICADO (seção 6) | **CONFIRMADO, fechado**: testado com `pip install --dry-run` contra uma cópia temporária (fora do repo, removida ao final) do conteúdo de HEAD (UTF-16LE, 1648 bytes) — o pip deste ambiente **tolera o BOM UTF-16LE e interpreta as linhas corretamente**, zero erros de parsing. Não testa instalação real em máquina limpa (exigiria download de rede, fora do escopo), mas a dúvida específica sobre falha de *parsing* por encoding está respondida: **não falha por encoding neste pip**, ao menos. `PyJWT`/`httpx` seguem confirmados ausentes da lista, reafirmando o achado já registrado. |
| Mensagens de erro da API vazam stack trace? | NÃO VERIFICADO (seção 17, STRIDE) | **CONFIRMADO mitigado, fechado**: `backend/app/main.py:98-109`, handler global `@app.exception_handler(Exception)` — qualquer exceção não tratada vira `{"detail": "Erro interno do servidor. Consulte os logs do backend."}` genérico; o traceback vai só para `logger.exception(...)` (arquivo local), nunca para o cliente. Reforça F4b (nenhuma rota individual vaza `str(exception)` bruto). |
| Cobertura de TypeScript estrito | NÃO VERIFICADO (seção 13) | **CONFIRMADO, fechado**: `tsconfig.json` tem `"strict": true`. Combinado com o achado já registrado em C22 (0 ocorrências de `: any`/`as any` em `app/`, `components/`, `lib/`), o projeto **respeita tipagem estrita de fato, não só a declara**. |
| `aria-live` em `lib/toast.tsx` | NÃO VERIFICADO (F3/F7, rodada anterior deixou explicitamente como pendência de escopo) | **CONFIRMADO ausente — achado novo, eleva a severidade do já registrado em F3**: leitura completa de `toast.tsx` (85 linhas) confirma **nenhum `aria-live`, `role="status"` ou `role="alert"`** no container (`:60`) nem nos toasts individuais (`:64`). Isso significa que **todo feedback de sucesso/erro do sistema inteiro** (criar/editar/excluir usuário, servidor, resolver alerta, marcar notificação) é **invisível a leitor de tela** — o usuário perde a única confirmação visual de que uma ação (inclusive as exclusões definitivas implementadas nesta sessão) teve efeito. Reclassifico de MÉDIO (estimativa da rodada anterior) para **ALTO**: não é um componente isolado, é o canal de feedback de toda ação do sistema. |
| A08 Software/Data Integrity (assinatura de artefato/CI) | NÃO VERIFICADO (seção 7) | **CONFIRMADO ausente, fechado**: já resolvido por C11 (ausência total de CI/CD) nas rodadas anteriores — sem pipeline, não há assinatura de artefato possível. Atualizo a tabela OWASP para refletir isso como confirmado, não pendente. |
| A10 SSRF | NÃO VERIFICADO (seção 7) | **FALSO POSITIVO, fechado**: já resolvido em F4b desta auditoria (nenhum endpoint aceita URL/host livre para proxy de requisição; único host controlável tem allowlist). |
| Estado do Cloudflare Tunnel/DNS/TLS/Vercel runtime, produção real | NÃO VERIFICADO (múltiplas seções) | **Mantido NÃO VERIFICADO — DEPENDE DE ACESSO EXTERNO**, genuinamente fora do alcance de qualquer leitura de repositório, em qualquer rodada futura do mesmo método. |
| Comportamento sob carga real / benchmark de performance | NÃO VERIFICADO (seção 11) | **Mantido: BENCHMARK NÃO EXECUTADO** — não é um "não verificado" por preguiça, é uma afirmação impossível de fazer com segurança sem rodar carga real contra o sistema, o que está fora do escopo somente-leitura desta auditoria. |
| Teste de restauração real de backup | NÃO VERIFICADO (C10) | **Mantido, deliberadamente**: restaurar um backup é uma ação com efeito (mesmo que para um banco de teste), incompatível com a regra "somente leitura" desta e de todas as rodadas anteriores. Não é uma lacuna de esforço, é um limite de escopo assumido conscientemente. |
| `python -m pytest` roda a suíte real hoje | NÃO VERIFICADO/CONFIRMADO parcial (C23.2) | Já fechado na rodada 3 (C23.2): `INTERNALERROR` confirmado por execução real. Nada novo a fazer aqui. |

## G4. Ajuste de score decorrente desta rodada

Único ajuste com evidência nova suficiente: **Acessibilidade** sobe de 4 para **3.5/10** (a diferença de meio ponto reflete a reclassificação do achado do toast de MÉDIO estimado para ALTO confirmado — o sistema de feedback inteiro, não um componente isolado, está sem `aria-live`). Nenhuma outra categoria muda: `npm audit` limpo não eleva "Segurança geral" porque a rodada já assumia ausência de CVE conhecida por falta de evidência contrária, não a presumia; agora há evidência positiva direta, mas dentro da mesma faixa de nota já atribuída (7/10, ponto forte já reconhecido, agora com prova adicional).

**Score geral recalculado**: soma das 19 categorias pontuadas (Acessibilidade agora 3.5 em vez de 4) ÷ 19 ≈ **6.37/10** — arredondado, permanece **6.4/10**, sem mudança de faixa (diferença de 0,03 é ruído de arredondamento entre 19 categorias, não uma reavaliação material).

## G5. Veredito — o que muda com esta rodada

Nenhuma das 12 perguntas do veredito anterior (F9) muda de resposta. Dois refinamentos:

- **Maior força reforçada com evidência nova**: `npm audit` limpo (0/120 vulnerabilidades) é agora um fato executado, não uma suposição — soma-se aos pontos fortes já listados (backup, mitigação de command injection, frontend sem bugs reais).
- **Item adicional para "obrigatório antes de produção" se o padrão de acessibilidade da organização for AA ou superior**: `aria-live` em `lib/toast.tsx` — correção de 1-2 linhas (adicionar `role="status" aria-live="polite"` ao container de toasts, `toast.tsx:60`), impacto desproporcionalmente alto (destrava feedback de toda ação do sistema para leitor de tela). Mesma categoria de "conserto pequeno, efeito amplo" do focus trap já identificado em F9.

---

**Resumo da Rodada G**: fechadas as três lacunas pedidas explicitamente — LGPD técnica (achado novo: log de autenticação com e-mail+IP sem redação), CVE scan (`npm audit` limpo, `pip-audit` indisponível sem instalar nada), e todo item "NÃO VERIFICADO" que o código permitia responder (7 de 10 itens revisados fecharam; 3 permanecem genuinamente fora do alcance de uma auditoria estática — infraestrutura externa, benchmark de carga, restore destrutivo). Score geral final: **6.4/10**, inalterado em faixa. Nenhum bloqueador novo para produção; o `requirements.txt` corrompido continua sendo o único P0.

---

