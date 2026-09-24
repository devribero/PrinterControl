# Ideias e próximos passos

Lista viva de funcionalidades aprovadas para fazer. Dívida técnica fica em
[TECHNICAL_DEBT.md](TECHNICAL_DEBT.md); aqui só entra o que é **novo**.

## Aprovadas (24/09/2026)

### 1. E-mail: relatório mensal + alerta de toner

**Implementado em 24/09/2026** (`services/email_notifier.py`): alerta de
toner para `ALERT_EMAIL_TO`, relatório mensal automático com a planilha para
`REPORT_EMAIL_TO`, e botão de teste em Configurações → Notificações. Falta:
preencher o SMTP no `backend/.env` e, depois, e-mail **por unidade** (coluna
nova em `units`, como o webhook por unidade).

Plano original:

- **Relatório mensal automático:** no dia 1, gerar o relatório do mês
  anterior (dados de `services/monthly_report.py` / levantamento) e enviar
  por e-mail para uma lista de destinatários, com a planilha em anexo.
- **Alerta de toner por e-mail:** mesmo gatilho do webhook de toner crítico
  (`services/webhook_notifier.py`), enviado também por e-mail. Destinatário
  por unidade (como o webhook por unidade) + um endereço central.
- Configuração sugerida: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`,
  `SMTP_PASSWORD`, `SMTP_FROM`, `SMTP_STARTTLS`, `REPORT_EMAIL_TO`.
- Botão "Enviar e-mail de teste" nas Configurações, igual ao teste de webhook.
- Registrar cada envio na trilha de auditoria (sem a senha do SMTP).

### 2. PWA (app instalável no celular)

- `manifest.webmanifest` + ícones + service worker: "Adicionar à tela
  inicial" no Android/iOS, abre em tela cheia como app.
- Cache do "shell" para abrir rápido mesmo com rede ruim.
- Etapa 2: **notificação push** de toner crítico / impressora offline
  (Web Push com chaves VAPID), por usuário e por unidade.

### 3. Estoque de toner

- Cadastro de cartuchos por modelo e por unidade (quantidade em estoque).
- Baixa automática quando o sistema detecta a troca (item 4) ou manual.
- Aviso de estoque mínimo (webhook/e-mail) — "restam 2 cartuchos do
  modelo X em Manaus".

### 4. Detecção automática de troca de toner

- Nível subiu de forma brusca (ex.: 5% → 100%) entre duas leituras = troca.
- Registrar a troca (data, impressora, cor) e calcular o **rendimento real**
  de cada cartucho (páginas impressas entre uma troca e a próxima).
- Base: `toner_history` e `printer_readings` já existem.

### 5. Modo manutenção

- Marcar uma impressora como "em manutenção" (com motivo e previsão).
- Enquanto isso: sem alertas de offline/toner, e ela não pesa nos
  indicadores de disponibilidade. Some sozinho na data prevista.

### 6. Resumo diário no Teams/e-mail

- Todo dia às 8h: "3 offline, 5 com toner baixo, 1 em manutenção", com a
  lista curta e link para o painel. Por unidade (webhook/e-mail da unidade)
  e geral.

### 7. Painel TV

- Rota em tela cheia (`/tv`) para um monitor do TI: status da frota em
  blocos grandes, alertas ativos, sem menus, atualiza sozinho.
- Acesso com uma conta somente leitura (viewer) que não expira no meio do dia.

## Banco de ideias (não aprovadas ainda)

Ver a lista completa na conversa de 24/09/2026; as principais:

- Previsão de fim de toner (dias restantes) pelo ritmo de consumo.
- Custo por página e rateio por unidade/departamento; cotas.
- SSO com o AD / Entra ID e MFA para admins.
- Detecção de anomalias (salto de contador, uso fora do horário).
- Chamados/manutenção por impressora e SLA do fornecedor.
- Tokens de API somente leitura (Power BI).
