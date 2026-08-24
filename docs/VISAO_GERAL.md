# PrinterControl — Visão geral do sistema

**Para quem é este documento:** o dono do sistema. Alguém que entende de
impressoras, de frota, de toner e de contrato — mas que não escreve código
todo dia. Tudo aqui está explicado em português comum; onde um termo técnico
é inevitável, ele vem traduzido na primeira vez que aparece.

**Data:** 24 de agosto de 2026.

**Se você só tem cinco minutos:** leia a seção 1, e depois a seção 7 (o
roteiro de teste em produção).

---

## Índice

1. [O que o sistema faz](#1-o-que-o-sistema-faz)
2. [Como o sistema é montado](#2-como-o-sistema-é-montado)
3. [Tudo o que o sistema faz hoje, por área](#3-tudo-o-que-o-sistema-faz-hoje-por-área)
4. [Variáveis de ambiente](#4-variáveis-de-ambiente)
5. [Modo real x modo simulado, e os riscos](#5-modo-real-x-modo-simulado-e-os-riscos)
6. [Subir o sistema em produção hoje](#6-subir-o-sistema-em-produção-hoje)
7. [Roteiro de teste em produção — amanhã](#7-roteiro-de-teste-em-produção--amanhã)
8. [Onde está o resto da documentação](#8-onde-está-o-resto-da-documentação)

---

## 1. O que o sistema faz

O PrinterControl responde, sozinho e o tempo todo, a perguntas que hoje
alguém responde na mão:

- **Quais impressoras estão de pé agora?** Online, offline, ou "atenção"
  (respondendo, mas com algum problema — tipicamente toner acabando).
- **Quanto de toner resta em cada uma?** Por cor: preto, ciano, magenta,
  amarelo.
- **Quantas páginas cada uma imprimiu neste mês?** E nos meses anteriores.
- **O que precisa de atenção agora?** Toner crítico, impressora que caiu.

### Como ele descobre isso

De duas fontes, que fazem coisas diferentes:

**1. Os servidores de impressão (Print Servers).** São os servidores Windows
onde as impressoras estão publicadas. Eles respondem *quais impressoras
existem*, com nome, driver e endereço. É a **fonte da verdade sobre a frota** —
se uma impressora não está publicada num Print Server, para o sistema ela não
existe.

**2. As próprias impressoras, por SNMP.** SNMP é o "idioma" que impressoras de
rede falam para responder perguntas sobre si mesmas. O sistema pergunta a cada
impressora: você está viva? quanto de toner tem? quantas páginas já imprimiu
desde que foi ligada? É a **fonte da verdade sobre o estado**.

### O detalhe que explica o relatório mensal

Impressoras **não sabem** dizer "imprimi 4.000 páginas este mês". Elas só sabem
dizer o **contador total acumulado** desde a fabricação — um número que só
cresce.

Então o sistema guarda uma leitura desse contador a cada ciclo de coleta, e
"páginas do mês" é a **subtração**: o maior contador visto no mês menos o menor
contador visto no mês.

Isso tem duas consequências que valem entender:

- **Nada é estimado.** O número é o incremento realmente observado.
- **O sistema precisa de tempo para ter história.** Uma impressora com uma
  única leitura no mês aparece com 0 páginas — não porque não imprimiu, mas
  porque ainda não há duas medições para subtrair. **No primeiro mês, o
  relatório mensal vai parecer pobre. Isso é esperado.**

### O ciclo, em uma frase

A cada poucos minutos o sistema pergunta a toda a frota como ela está, guarda
a resposta, compara com os limites configurados, abre alerta quando passa do
limite, e mostra tudo num painel web.

---

## 2. Como o sistema é montado

São **duas peças separadas**, que conversam pela internet.

```
   VOCÊ, no navegador
          |
          | https
          v
  +---------------------+
  |     FRONTEND        |   O painel. As telas, os gráficos, os botões.
  |     (Next.js)       |   Não guarda nada. Só desenha o que pergunta.
  |   roda na Vercel    |
  +---------------------+
          |
          | https, com o "crachá" (token) em cada pergunta
          v
  +---------------------+
  |   Cloudflare Tunnel |   A porta de entrada segura. Ainda não ativada.
  +---------------------+
          |
          v
  +---------------------+
  |      BACKEND        |   O cérebro. Decide, calcula, guarda, coleta.
  |     (FastAPI)       |
  |  roda na máquina    |
  |  do Print Server    |
  +---------------------+
       |          |
       |          +----> banco de dados (um arquivo: printer_control.db)
       |
       +----> Print Servers (PowerShell) e impressoras (SNMP)
```

### Por que duas peças, e não uma

Porque elas precisam estar em **lugares diferentes**.

O **backend precisa estar dentro da rede da empresa** — é ele que fala com os
Print Servers e com as impressoras, e isso só funciona de dentro. Por isso ele
roda numa máquina Windows da rede.

O **frontend precisa estar acessível de qualquer lugar** — de casa, do
celular, de outra unidade. Por isso ele fica hospedado na Vercel, na internet.

O Cloudflare Tunnel é a ponte: ele deixa o frontend, que está na internet,
falar com o backend, que está dentro da rede — **sem precisar abrir nenhuma
porta no firewall da empresa**. É a peça que ainda falta ativar.

### O que cada tecnologia é, em uma linha

| Nome | O que é |
|---|---|
| **Python** | A linguagem em que o backend é escrito. |
| **FastAPI** | A ferramenta que transforma código Python numa API — o "atendente" que responde às perguntas do painel. |
| **SQLite** | O banco de dados. É **um único arquivo** (`printer_control.db`). Fazer backup é copiar esse arquivo (com cuidado — ver seção 6). |
| **SQLModel** | O tradutor entre o código Python e as tabelas do banco. |
| **APScheduler** | O despertador interno. É ele que dispara a coleta a cada X minutos. |
| **SNMP** | O protocolo pelo qual as impressoras respondem sobre si mesmas. |
| **PowerShell** | Usado para perguntar aos Print Servers quais impressoras existem. |
| **Next.js / React** | A tecnologia do painel — o que desenha as telas no navegador. |
| **Vercel** | Onde o painel fica hospedado, de graça, na internet. |
| **Cloudflare Tunnel** | A ponte segura entre a internet e a rede da empresa. |

### O "crachá" (token)

Quando você faz login, o backend devolve um **token** — um texto longo que
funciona como um crachá temporário. O painel guarda esse crachá no navegador e
o apresenta em **toda** pergunta seguinte. Sem crachá, o backend não responde
nada (exceto a tela de login e a verificação de saúde).

**O crachá vale 24 horas.** Depois disso é preciso logar de novo.

Um detalhe importante para incidentes: **trocar a senha não invalida crachás
já emitidos.** Se você suspeita que um crachá vazou, o caminho certo é
**desativar a conta** em Usuários — isso corta o acesso na hora. Trocar a senha
sozinho não corta. (Registrado como D4 em `TECHNICAL_DEBT.md`.)

---

## 3. Tudo o que o sistema faz hoje, por área

### Os três níveis de acesso

Toda conta tem exatamente um papel. Quem tem um papel mais alto pode tudo o
que o mais baixo pode.

| Papel | Pode |
|---|---|
| **viewer** | Só olhar. Ver painel, impressoras, toner, alertas, relatórios, histórico. |
| **operator** | Tudo do viewer + disparar coleta real, resolver alertas, disparar aviso de alerta. |
| **admin** | Tudo do operator + criar/editar contas, cadastrar/editar impressoras, descobrir e sincronizar Print Servers, enviar notificações, coleta simulada. |

Contas novas nascem como **viewer** se ninguém disser o contrário. É
deliberado: o acesso mais restrito é o padrão.

---

### 3.1 Autenticação (entrar no sistema)

| O que faz | Quem pode | Onde fica |
|---|---|---|
| Fazer login com e-mail e senha | Qualquer um | Tela de login |
| Ver quem você é e qual seu papel | Logado | Canto superior direito |
| Trocar o próprio nome | Logado | Configurações → Perfil |
| Trocar a própria senha (exige a senha atual) | Logado | Configurações → Alterar senha |

**Proteções ativas:**

- **Limite de tentativas.** 5 tentativas erradas em 15 minutos bloqueiam o
  login — contado por endereço de origem **e** por e-mail. Passados os 15
  minutos, libera sozinho. Não trava a conta permanentemente (isso viraria uma
  forma de alguém deixar você de fora do próprio sistema de propósito).
- **A resposta não entrega quais e-mails existem.** "E-mail não cadastrado" e
  "senha errada" dão exatamente a mesma resposta, e demoram exatamente o mesmo
  tempo. Antes, o e-mail inexistente respondia muito mais rápido, e comparar os
  tempos revelava quais contas existem — que é a lista de alvos de quem quer
  invadir.
- **A senha atual é obrigatória para trocar a senha.** Sem isso, um crachá
  roubado viraria posse permanente da conta.

---

### 3.2 Usuários

| O que faz | Quem pode | Onde fica |
|---|---|---|
| Listar todas as contas | admin | Menu → Usuários |
| Criar conta (e-mail, nome, senha, papel) | admin | Usuários → botão de criar |
| Alterar nome, papel ou senha de outra conta | admin | Usuários → editar |
| Ativar / desativar conta | admin | Usuários → editar |

**Regras que valem conhecer:**

- Senha mínima: **8 caracteres**, para qualquer conta.
- **O e-mail não pode ser alterado** depois de criado — ele é a identidade
  usada pelo crachá, e trocá-lo derrubaria a sessão da pessoa em silêncio.
- **Desativar é melhor que apagar.** Desativar corta o acesso imediatamente,
  inclusive de crachás já emitidos, e preserva o histórico.
- Não existe recuperação de senha por e-mail. Se alguém esquece a senha, um
  admin redefine em Usuários.

**As duas contas iniciais** (`mateus.vicentino@` e `pedro.ribeiro@`) são
criadas pelo `seed.py`. A senha delas é gerada aleatoriamente e mostrada
**uma única vez** no console. Ver seção 6.

---

### 3.3 Print Servers

O Print Server é a fonte de quais impressoras existem. O sistema suporta
**vários** — na prática as unidades (`elgjunprt`, `elgvloprt`, `elgmcprt`).

| O que faz | Quem pode | Onde fica |
|---|---|---|
| Listar os servidores cadastrados | Logado | Mapeamento de Rede |
| Cadastrar um servidor novo | admin | Mapeamento de Rede |
| Renomear / ativar / desativar um servidor | admin | Mapeamento de Rede |
| **Descobrir** impressoras de um servidor | admin | Botão "Escanear Rede" |
| **Sincronizar** impressoras de um servidor | admin | Botão "Sincronizar" |

**Descobrir e sincronizar são coisas diferentes — e essa é a distinção mais
importante desta seção:**

- **Descobrir** pergunta ao servidor quais impressoras existem e **mostra na
  tela**. Não grava nada. É seguro, pode rodar à vontade.
- **Sincronizar** pega esse resultado e **grava no banco**: cria as que não
  existiam, atualiza as que mudaram, e **marca como inativa toda impressora do
  banco que o servidor não publica mais**.

Sincronizar é a operação mais destrutiva do sistema. Por isso ela pede
confirmação explícita na tela, e por isso existe a proteção descrita na
seção 5.

O nome do servidor (`host`) é validado: só aceita nome de máquina, FQDN ou
IPv4. Nada de espaços, aspas ou ponto-e-vírgula — esse campo é usado num
comando do sistema, e texto livre ali era uma porta de entrada. (Corrigido na
Fase 10.)

---

### 3.4 Impressoras e coleta

| O que faz | Quem pode | Onde fica |
|---|---|---|
| Ver a frota com status, toner e contador | Logado | Dashboard, Impressoras |
| Ver só o toner, com filtro por criticidade | Logado | Suprimentos |
| Ver detalhes e histórico de uma impressora | Logado | Clicar na impressora |
| Buscar, filtrar, alternar lista/grade | Logado | Impressoras |
| Cadastrar impressora à mão | admin | Impressoras |
| Editar nome, modelo, IP, departamento | admin | Impressoras → editar |
| **Coletar agora** (uma ou toda a frota) | operator | Botão "Verificar agora" |
| Relatório mensal de páginas | Logado | Relatórios |
| Matriz impressora × mês | Logado | Histórico |

**Como a coleta automática funciona:** o APScheduler dispara um ciclo a cada
`COLLECTION_INTERVAL_MINUTES` (padrão 5). Cada ciclo:

1. lê do banco todas as impressoras **ativas**;
2. agrupa por IP — várias impressoras podem compartilhar o mesmo endereço, e
   nesse caso o sistema consulta **uma vez só**;
3. consulta por SNMP, em paralelo (até `COLLECTION_MAX_WORKERS` ao mesmo tempo);
4. grava uma leitura por impressora;
5. passa cada leitura pelo motor de alertas.

**Importante:** o ciclo automático **nunca** descobre nem sincroniza Print
Servers. A frota vem exclusivamente do banco. Isso é proposital — impede que
uma descoberta rode sozinha de madrugada e substitua a frota real.

**Cadastro manual é exceção, não a regra.** O caminho normal é sincronizar do
Print Server.

---

### 3.5 Alertas

Alertas são **eventos técnicos de impressora**, gerados automaticamente após
cada coleta.

| O que faz | Quem pode | Onde fica |
|---|---|---|
| Ver alertas ativos, filtrar por severidade | Logado | Alertas |
| Ver alertas já resolvidos | Logado | Alertas → filtro |
| Marcar alerta como resolvido | operator | Alertas |
| Disparar aviso manual (webhook) | operator | Detalhes do alerta |

**Quando um alerta abre:** impressora que ficou offline, ou toner que cruzou
o limite (atenção / crítico).

**Duas coisas que evitam ruído:**

- **Não duplica.** Se a impressora continua offline por 3 horas, é **um**
  alerta, não 36.
- **Fecha sozinho.** Quando a impressora volta ou o toner é trocado, o alerta
  é resolvido automaticamente na coleta seguinte.

Alertas críticos de toner podem disparar um **webhook** — uma mensagem
automática para o Teams (via Power Automate). Configurado em `WEBHOOK_URL`.
Vazio = desligado.

---

### 3.6 Notificações

Notificação é **mensagem para gente**. Não confundir com alerta, que é evento
de máquina.

| O que faz | Quem pode | Onde fica |
|---|---|---|
| Ver a própria caixa | Logado | Sino no topo |
| Contador de não lidas | Logado | Badge no sino |
| Marcar como lida / marcar todas | Logado (a própria caixa) | Notificações |
| Enviar notificação para usuários | admin | Notificações |

**A caixa é pessoal e não tem exceção.** Não existe caminho na API para ler a
caixa de outra pessoa — nem para admin. Admin **envia**; ler o que chegou é do
dono da conta.

---

### 3.7 Perfil e configurações

| O que faz | Quem pode | Onde fica |
|---|---|---|
| Alterar o próprio nome | Logado | Configurações → Perfil |
| Alterar a própria senha | Logado | Configurações → Alterar senha |
| Tema claro / escuro | Logado | Topo da tela |
| Preferências de acessibilidade | Logado | Configurações |

O que você **não** pode mudar em si mesmo: seu e-mail (é a identidade do
crachá), seu papel e se você está ativo (isso é decisão de administrador — se
qualquer um pudesse, a tela de Usuários existiria por decoração).

---

### 3.8 Ambiente demo e produção

O sistema sabe em qual ambiente está rodando e **anuncia isso na tela**.

| Ambiente | Para que serve | O que aparece |
|---|---|---|
| `development` | Máquina de quem desenvolve. Simulação liberada. | Indicadores de simulação |
| `demo` | Demonstração. Dados fictícios são esperados. | Faixa permanente "dados de demonstração" |
| `production` | Frota real. Simulação é erro, não preferência. | Nada de especial — é o normal |

**O rótulo vem do backend, não do painel.** O painel pergunta ao backend
(`GET /health`) em qual ambiente ele está. Isso importa: um painel compilado
como "produção" e apontado por engano para o backend de demonstração mentiria
com toda a confiança. Perguntando ao servidor, o rótulo é sempre o do servidor
que respondeu.

**Quando o backend não responde**, o painel mostra o conjunto de demonstração
com uma faixa de aviso — em vez de uma tela vazia sem explicação. É uma escolha
de produto, com um risco residual conhecido (D11).

---

## 4. Variáveis de ambiente

São as configurações do backend. Ficam no arquivo **`backend/.env`** — um
arquivo de texto, uma linha por configuração, formato `NOME=valor`.

Comece copiando `backend/.env.example`, que tem todas elas comentadas.

> **O `.env` nunca vai para o Git.** Ele contém a chave secreta do sistema.

### As que **obrigam** o backend a recusar subir se estiverem erradas

Isto é proposital. Uma configuração incoerente com produção é erro de
operação, não preferência — e falhar no boot com mensagem clara é muito melhor
que descobrir o problema depois do estrago.

| Variável | O que faz | Valor em produção | Se estiver errada |
|---|---|---|---|
| `ENVIRONMENT` | Diz ao sistema em que ambiente ele está | `production` | Valor não reconhecido (`prod`, `producao`, `Production `) → **não sobe**. Não cai no padrão em silêncio. |
| `SECRET_KEY` | Chave que assina os crachás | 32+ caracteres, aleatória, só sua | Chave de desenvolvimento ou curta → **não sobe**. Com a chave conhecida, qualquer um forja um crachá de admin. |
| `PRINT_SERVER_MODE` | `real` fala com o Print Server; `mock` inventa | `real` | `mock` em produção → **não sobe**. Ver seção 5: é o risco mais grave do sistema. |
| `ALLOW_MOCK_COLLECT` | Permite gravar leituras fictícias | `false` | `true` em produção → **não sobe**. |
| `CORS_ORIGINS` | Quais endereços de painel podem chamar esta API | O endereço HTTPS do painel na Vercel | Vazio, `*`, `localhost` ou sem HTTPS → **não sobe**. |

**Gerar a `SECRET_KEY`:**

```powershell
.\backend\venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"
```

**Sobre `CORS_ORIGINS`:** é o endereço do **painel**, não o do backend. Com o
painel na Vercel, é o domínio da Vercel — por exemplo
`CORS_ORIGINS=https://printercontrol.vercel.app`. Se estiver errada, o painel
carrega mas nenhum dado aparece, e o erro só é visível no console do navegador.

### Banco de dados

| Variável | O que faz | Recomendado | Se estiver errada |
|---|---|---|---|
| `DATABASE_URL` | Onde fica o arquivo do banco | Deixe o padrão | Caminho errado → o sistema cria um banco **vazio** no lugar errado e parece que todos os dados sumiram. Caminho relativo é convertido para absoluto automaticamente, justamente para evitar isso. |

### Coleta automática

| Variável | O que faz | Recomendado | Se estiver errada |
|---|---|---|---|
| `COLLECTION_ENABLED` | Liga o despertador da coleta | `true` | `false` → **nada é coletado sozinho**. O painel mostra dados cada vez mais velhos e ninguém avisa. É o erro mais fácil de não perceber. |
| `COLLECTION_INTERVAL_MINUTES` | De quanto em quanto tempo coletar | `5` a `15` | Muito baixo → carga desnecessária na rede e o banco cresce depressa. Muito alto → alerta de impressora offline demora a aparecer. |
| `COLLECTION_MODE` | `real` = SNMP de verdade | `real` | `mock` grava dados inventados. Em produção o boot já teria falhado por `ALLOW_MOCK_COLLECT`. |
| `COLLECTION_MAX_WORKERS` | Quantas impressoras consultar ao mesmo tempo | `4` a `8` | Alto demais → rede e CPU saturadas. `1` → o ciclo pode não terminar antes do próximo começar. |
| `COLLECTION_SCENARIO` | Cenário simulado | Ignorado em produção | — |
| `COLLECTION_PRINTER_IDS` | **Não é lido por nada.** Legado. | — | Nenhum efeito. (D2) |

### Print Server

| Variável | O que faz | Recomendado | Se estiver errada |
|---|---|---|---|
| `PRINT_SERVER_HOST` | Servidor padrão, para as ações sem servidor específico | `elgjunprt` | Nome errado → descoberta falha com erro do PowerShell. Nome inválido (espaço, aspas) → recusado na validação. |
| `PRINT_SERVER_TIMEOUT_SECONDS` | Quanto esperar pela resposta | `30` | Baixo demais → descoberta falha em servidor lento. Alto demais → a tela fica travada esperando. |

### SNMP

| Variável | O que faz | Recomendado | Se estiver errada |
|---|---|---|---|
| `SNMP_COMMUNITY` | A "senha" de leitura do SNMP | `public`, salvo se a rede usar outra | Errada → **todas** as impressoras aparecem offline, mesmo estando de pé. Sintoma clássico e confuso. |
| `SNMP_TIMEOUT` | Quanto esperar por impressora | `1.5` a `3.0` | Baixo → impressora lenta vira "offline" falso. Alto → o ciclo demora demais. |
| `SNMP_RETRIES` | **Não é lido por nada.** Legado. | — | Nenhum efeito. (D2) |

### Segurança do login

| Variável | O que faz | Recomendado | Se estiver errada |
|---|---|---|---|
| `LOGIN_MAX_ATTEMPTS` | Tentativas erradas antes de bloquear | `5` | Muito alto → força bruta volta a ser viável. `1` → qualquer erro de digitação bloqueia. |
| `LOGIN_WINDOW_SECONDS` | Duração do bloqueio | `900` (15 min) | Muito curto → o limite quase não atrapalha um ataque. Muito longo → quem errou fica de fora por muito tempo. |
| `TRUST_PROXY_HEADERS` | Confiar no cabeçalho `X-Forwarded-For` | `false` até o Tunnel entrar; **avaliar** depois | **`true` sem um proxy de confiança na frente ENFRAQUECE a proteção** — o cabeçalho passa a ser escolhido pelo cliente, que troca de "IP" a cada tentativa e anula o limite por IP. |

### Webhook (aviso no Teams)

| Variável | O que faz | Recomendado | Se estiver errada |
|---|---|---|---|
| `WEBHOOK_URL` | Endereço do Power Automate / Teams | Vazio = desligado | Errada → o aviso não chega e a falha fica só no log. **Nunca comitar a URL real.** |
| `WEBHOOK_TIMEOUT_SECONDS` | Quanto esperar | `5` | Alto demais → o ciclo de coleta atrasa esperando o Teams. |

### Logs

| Variável | O que faz | Recomendado | Se estiver errada |
|---|---|---|---|
| `LOG_LEVEL` | Quanto detalhe registrar | `INFO` | `WARNING` → o ciclo de coleta deixa de aparecer no log, e você perde a auditoria de quando a coleta rodou. `DEBUG` → arquivo enorme. |
| `LOG_FILE` | Onde gravar | `logs/printercontrol.log` | Vazio → só console. **Rodando como tarefa agendada ninguém lê o console** — um erro de madrugada não deixa rastro. |
| `LOG_MAX_BYTES` / `LOG_BACKUP_COUNT` | Tamanho e quantos arquivos guardar | `5242880` / `10` (≈50 MB) | Alto demais → disco cheio. |

Senhas, tokens e a `SECRET_KEY` são **apagados automaticamente** antes de ir
para o log.

### Só do `seed.py` (não precisa ficar no `.env`)

| Variável | O que faz |
|---|---|
| `SEED_ADMIN_PASSWORD` | Senha das contas iniciais. Se ausente, uma senha forte é gerada e mostrada **uma única vez**. Melhor digitar na hora do que deixar gravada no servidor. |

### Do frontend (na Vercel, não no `.env` do backend)

| Variável | O que faz | Se estiver errada |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Endereço do backend | O painel não acha o backend e mostra dados de demonstração com faixa de aviso. |

---

## 5. Modo real x modo simulado, e os riscos

### O problema em uma frase

O sistema tem um modo simulado, que inventa impressoras e leituras para poder
ser desenvolvido fora da rede da empresa. **Dado fictício gravado no banco de
produção é indistinguível de dado real depois.** Não há como separar.

### O risco mais grave: sincronizar em modo simulado

O modo simulado publica uma frota inventada de 7 impressoras. Se um
"Sincronizar" rodar com esse modo ligado contra o banco de produção:

1. as 7 impressoras fictícias são criadas;
2. **todas as ~79 impressoras reais são marcadas como inativas**, porque não
   estão na lista que o simulador publicou;
3. impressora inativa **sai do ciclo de coleta** — o monitoramento da frota
   real simplesmente para;
4. no painel, tudo parece funcionar. Sete impressoras, todas online.

Não é hipótese: `PRINT_SERVER_MODE` tem `mock` como padrão por razões
históricas. Um deploy que apenas herdasse o padrão e depois clicasse em
"Sincronizar" faria exatamente isso.

### Como o sistema decide entre real e simulado

Em **três** níveis, e todos precisam estar certos:

1. **Global, no `.env`:** `PRINT_SERVER_MODE` (`real`/`mock`) e
   `ALLOW_MOCK_COLLECT`.
2. **Por servidor, no banco:** cada Print Server cadastrado tem seu **próprio**
   modo. Numa instalação com vários servidores, um pode estar em produção e
   outro sendo testado.
3. **Por requisição:** a rota de coleta manual aceita `mode="mock"`.

### As duas camadas de proteção

**Camada 1 — no boot (`config.py`).** Com `ENVIRONMENT=production`, o backend
**recusa subir** se `PRINT_SERVER_MODE` não for `real` ou se
`ALLOW_MOCK_COLLECT` for `true`. Recusar, e não avisar: um aviso no log seria
lido depois do estrago.

**Camada 2 — por requisição (`environment_guard.py`).** A camada 1 não alcança
o modo **por servidor**: um Print Server gravado com `mode="mock"` antes de a
instância virar produção continua lá no banco, e nenhuma validação de boot o
enxerga. Então toda operação que envolve simulação responde **409** em
produção — sincronizar, descobrir, cadastrar servidor mock, coletar simulado.

É **409 (Conflito)** e não 403 (Proibido) de propósito: não é falta de
permissão. **Nem um admin pode fazer isso.** Apresentar como permissão
sugeriria, falsamente, que outra conta poderia.

### Riscos corrigidos na Fase 10 (24/08/2026)

| Era | Por que era grave | Como ficou |
|---|---|---|
| **Injeção de comando no host do Print Server** | O nome do servidor ia direto para uma linha de PowerShell. Um nome como `srv'; Remove-Item C:\ -Recurse -Force; '` executava comandos com os privilégios do serviço. Era o pior problema do sistema. | Só nome de máquina, FQDN ou IPv4 são aceitos — validado no cadastro **e** na hora de usar. Aspas escapadas como segunda camada. |
| **Porta dos fundos para gravar leitura fictícia** | A coleta simulada era bloqueada em produção, mas `POST /api/printers/{id}/readings` **não passava por guarda nenhuma**. Quem tivesse crachá de operator gravava a mesma leitura fictícia por ali. | A rota agora passa pela guarda: **409 em produção**. |
| **Leitura sem validação** | Aceitava status inventado, contador negativo, toner em 5000%. Um único registro assim corrompe painel, relatório mensal (que subtrai contadores) e motor de alertas de uma vez — e não há como distingui-lo de dado real depois. | Status na lista conhecida, contador ≥ 0, toner entre 0 e 100. |
| **Login sem limite de tentativas** | Uma lista de senhas comuns podia ser testada na velocidade da rede. | 5 tentativas / 15 minutos, por IP **e** por e-mail. |
| **Vazamento de quais e-mails existem** | E-mail inexistente respondia em microssegundos; senha errada, em dezenas de milissegundos. Comparar os tempos entregava a lista de contas válidas — os alvos de um ataque. | Os dois caminhos agora custam o mesmo. Medido: 65,2 ms vs 65,8 ms. |
| **Senha "123" nas contas de administrador** | As duas únicas contas capazes de criar usuários e sincronizar Print Servers tinham senha de três caracteres — abaixo do mínimo de 8 que a própria API exige das outras. | Senha aleatória forte, mostrada uma única vez. |
| **Biblioteca de crachá com falha conhecida** | `python-jose 3.3.0`: CVE-2024-33663 (confusão de algoritmo) e CVE-2024-33664 (consumo de toda a memória ao processar um token hostil). | Migrado para PyJWT. A biblioteca antiga e sua dependência vulnerável foram removidas. |
| **Consultas sem teto** | `?limit=99999999` carregava o histórico inteiro. O relatório mensal lia **a tabela inteira de leituras** a cada chamada — e ela cresce a cada ciclo, para sempre. | Teto de 500 nas listagens, janela de 12 meses (máx. 60) no relatório. |

**O que continua em aberto** está em
[`TECHNICAL_DEBT.md`](TECHNICAL_DEBT.md). Nada lá bloqueia produção hoje.

---

## 6. Subir o sistema em produção hoje

> Este é o roteiro **antes** do Cloudflare Tunnel. O backend responde só na
> própria máquina; o painel é acessado dessa mesma máquina, ou de outra da
> rede se `NEXT_PUBLIC_API_URL` apontar para ela.
>
> O runbook completo (instalar como serviço do Windows, diagnóstico
> aprofundado) está em [`OPERATIONS.md`](OPERATIONS.md).

### Passo 1 — Preparar o `.env`

```powershell
cd C:\Users\ribero\Desktop\PrinterControl\backend
copy .env.example .env
notepad .env
```

Ajuste, no mínimo:

```
ENVIRONMENT=production
SECRET_KEY=<cole aqui o resultado do comando abaixo>
PRINT_SERVER_MODE=real
ALLOW_MOCK_COLLECT=false
CORS_ORIGINS=https://SEU-PAINEL.vercel.app
COLLECTION_ENABLED=true
COLLECTION_INTERVAL_MINUTES=5
```

Gere a chave:

```powershell
.\venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"
```

### Passo 2 — Testar a configuração ANTES de subir

É mais rápido ver o erro no terminal do que no log de uma tarefa agendada.

```powershell
.\venv\Scripts\python.exe -c "from app.config import settings; print('OK', settings.environment)"
```

**Se imprimir `OK production`**, a configuração está coerente. **Se der erro**,
leia a mensagem — ela diz exatamente qual variável está errada e por quê. Não
prossiga antes de resolver.

### Passo 3 — Definir a senha das contas de administrador

O banco atual foi criado antes da correção da Fase 10 e as contas ainda usam a
senha antiga. Rotacione:

```powershell
.\venv\Scripts\python.exe seed.py --resetar-senhas
```

Isso imprime uma senha forte **uma única vez**. **Anote agora** — ela não é
gravada em lugar nenhum em texto claro. Se perder, rode o comando de novo e
gere outra.

Depois do primeiro acesso, troque em **Configurações → Alterar senha**.

### Passo 4 — Backup antes de qualquer coisa

```powershell
.\venv\Scripts\python.exe backup_db.py
```

Isso usa a API de backup **online** do SQLite e verifica a integridade do
arquivo gerado.

> **Nunca faça backup com um `copy` simples do `printer_control.db` com o
> sistema no ar.** Você provavelmente vai copiar um arquivo corrompido — e vai
> descobrir isso no dia em que precisar restaurar. Use sempre `backup_db.py`.

### Passo 5 — Subir o backend

```powershell
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

**`--host 127.0.0.1` não é detalhe.** Significa "só responde nesta máquina".
Com `0.0.0.0`, a API fica exposta à rede inteira em HTTP puro — e o crachá
trafega no cabeçalho, em claro. (D6.)

Para rodar sozinho no boot, como tarefa agendada do Windows:
`scripts\Servico-PrinterControl.ps1` — ver `OPERATIONS.md` §2.

### Passo 6 — Verificar a saúde

Em outro terminal:

```powershell
curl http://127.0.0.1:8000/health
```

O que você quer ver:

```json
{
  "status": "ok",
  "environment": "production",
  "is_production": true,
  "print_server_mode": "real",
  "mock_collect_enabled": false,
  "database": "ok",
  "scheduler": { "enabled": true, "running": true, "next_run": "..." }
}
```

**Confira campo a campo:**

| Campo | Deve ser | Se não for |
|---|---|---|
| `status` | `"ok"` | `"degraded"` = o banco não respondeu. **Pare e investigue.** |
| `environment` | `"production"` | Está rodando com as regras erradas. |
| `print_server_mode` | `"real"` | Não deveria nem ter subido. |
| `mock_collect_enabled` | `false` | Idem. |
| `scheduler.running` | `true` | A coleta **não vai rodar sozinha**. |
| `scheduler.next_run` | uma data no futuro | Se `null`, o despertador não agendou nada. |

> `/health` responde **200 mesmo degradado**, de propósito. Um monitor precisa
> ler o campo `status`, não só o código HTTP.

### Passo 7 — Subir o painel

```powershell
cd C:\Users\ribero\Desktop\PrinterControl
npm run build
npm run start
```

Acesse `http://localhost:3000` e faça login com a senha do passo 3.

### Recuperar de falha

| Sintoma | O que fazer |
|---|---|
| **O backend não sobe** | Leia a mensagem de erro — ela nomeia a variável. Quase sempre é `.env`. |
| **Sobe mas o painel não mostra dados** | Provavelmente `CORS_ORIGINS`. Abra o console do navegador (F12) e procure erro de CORS. |
| **Todas as impressoras aparecem offline** | Quase sempre `SNMP_COMMUNITY` errada, ou a máquina não alcança a rede das impressoras. Teste um ping para uma impressora. |
| **A coleta parou** | `curl /health` → veja `scheduler`. Se `running: false`, confira `COLLECTION_ENABLED` e reinicie. |
| **O banco corrompeu** | Pare o serviço → guarde o `printer_control.db` atual (**não apague**, pode ser a única cópia) → apague os arquivos `-wal` e `-shm` → copie o backup por cima → suba. Detalhe em `OPERATIONS.md` §5. |
| **Suspeita de acesso indevido** | **Desative a conta** em Usuários. Só trocar a senha **não** derruba crachás já emitidos (D4). |
| **Preciso parar tudo agora** | `Ctrl+C` no terminal do backend, ou `scripts\Servico-PrinterControl.ps1 -Acao parar`. O painel para de mostrar dados novos; nada é perdido. |

---

## 7. Roteiro de teste em produção — amanhã

Ordem pensada para que, se algo der errado, **dê errado cedo e de forma
reversível**. Não pule etapas — cada uma verifica algo que a seguinte assume.

### Antes de começar

- [ ] **Backup feito e verificado.** `.\venv\Scripts\python.exe backup_db.py`
- [ ] **Anote onde o backup ficou.** Você precisa saber disso sem procurar.
- [ ] **Anote quantas impressoras existem hoje.** Esse número é o seu controle:
      se ele cair drasticamente, algo sincronizou errado.
- [ ] Tenha este documento aberto.

---

### Etapa 1 — O backend sobe? *(2 min)*

```powershell
cd backend
.\venv\Scripts\python.exe -c "from app.config import settings; print('OK', settings.environment)"
```

✅ Imprimiu `OK production` → siga.
🛑 Deu erro → **pare.** A mensagem diz qual variável. Corrija o `.env`.

---

### Etapa 2 — A saúde está boa? *(2 min)*

Suba o backend e rode `curl http://127.0.0.1:8000/health`.

✅ `status: ok`, `environment: production`, `scheduler.running: true` → siga.
🛑 `status: degraded` → **pare.** O banco não respondeu.
⚠️ `scheduler.running: false` → o resto funciona, mas **nada será coletado
sozinho**. Resolva antes de continuar.

---

### Etapa 3 — O login funciona? *(3 min)*

Suba o painel e entre com a conta de admin.

✅ Entrou, nome e papel corretos no canto → siga.
🛑 "Email ou senha incorretos" → a senha é a do `--resetar-senhas`. Se
perdeu, rode de novo.
🛑 "Muitas tentativas" → você errou 5 vezes. **Espere 15 minutos** (ou
reinicie o backend, que zera a contagem — D5).

---

### Etapa 4 — Os dados são reais? *(5 min)* — **a etapa mais importante**

Olhe o painel. Faça estas perguntas:

- [ ] Aparece alguma faixa de **"dados de demonstração"**?
      → **Se sim, você NÃO está vendo dados reais.** O painel não achou o
      backend. Confira `NEXT_PUBLIC_API_URL` e `CORS_ORIGINS`.
- [ ] O número de impressoras bate com o que você anotou?
      → **Se caiu muito, pare.** Pode ter havido sincronização indevida.
- [ ] Você **reconhece** os nomes das impressoras?
      → As fictícias têm nomes como `VLO_Diretoria`, `MC_Expedicao_Etiqueta`.
      **Se você vir esses nomes, é a frota simulada.** Pare imediatamente.
- [ ] Os departamentos fazem sentido?

🛑 Qualquer resposta ruim aqui → **pare e investigue antes de coletar.**

---

### Etapa 5 — A coleta real funciona? *(5 min)*

Escolha **uma** impressora que você sabe que está ligada. Abra os detalhes e
clique em **"Verificar agora"**.

✅ Status vira `online`, aparece contador de páginas e nível de toner → **o
sistema está falando com a impressora de verdade. Este é o marco.**
⚠️ Vira `offline` mas você sabe que ela está ligada → confira
`SNMP_COMMUNITY` e se a máquina alcança a rede das impressoras.
⚠️ Fica `atencao` → normal se o toner estiver baixo. Confira na impressora.

---

### Etapa 6 — O ciclo automático roda? *(esperar 1 intervalo)*

Espere `COLLECTION_INTERVAL_MINUTES` (padrão 5) e olhe o log:

```powershell
Get-Content backend\logs\printercontrol.log -Tail 30
```

✅ Linha `Ciclo concluido | frota=... sucesso=... falha=...` → siga.
⚠️ `falha` alto → veja quantas. Algumas offline é normal; **todas** falhando
aponta para SNMP ou rede.
🛑 Nenhuma linha de ciclo → o scheduler não está rodando. Volte à Etapa 2.

---

### Etapa 7 — Descobrir (sem gravar nada) *(5 min)*

Vá em **Mapeamento de Rede** → **"Escanear Rede"**.

Isto **não grava nada**. É seguro.

- [ ] As impressoras listadas são as reais da unidade?
- [ ] A quantidade faz sentido?
- [ ] Você **não** vê `VLO_Diretoria`, `MC_Expedicao_Etiqueta` e companhia?

🛑 Se vir os nomes fictícios → o servidor está cadastrado como `mock`.
**Não sincronize.** Corrija o modo do servidor primeiro.

---

### Etapa 8 — Sincronizar *(a operação destrutiva)*

> ⚠️ **Só faça esta etapa se a Etapa 7 mostrou exatamente as impressoras que
> você esperava.** Sincronizar marca como **inativa** toda impressora do banco
> que o servidor não publicar — e impressora inativa sai do ciclo de coleta.

- [ ] Backup feito hoje? (Se não: faça agora.)
- [ ] Etapa 7 mostrou a frota certa?

Clique em **"Sincronizar"** e confirme.

Depois:

- [ ] Quantas foram criadas / atualizadas / desativadas?
- [ ] O número final de impressoras bate com o esperado?

🛑 **Se muitas impressoras foram desativadas** → algo está errado. Pare, e
restaure o backup (`OPERATIONS.md` §5).

---

### Etapa 9 — Deixar rodando e observar *(o resto do dia)*

- [ ] Volte a cada 1–2 horas e confira `/health` — `status: ok`,
      `uptime_seconds` **crescendo**.
- [ ] Confira o log: os ciclos continuam concluindo?
- [ ] Alertas apareceram? Fazem sentido?
- [ ] Os contadores de página estão subindo em impressoras que estão sendo
      usadas?

**Sinais de que algo está errado:**

| Sinal | O que significa |
|---|---|
| `uptime_seconds` nunca passa de poucos minutos | O serviço está **caindo e reiniciando em laço**. |
| `status: degraded` | O banco não responde. Disco cheio, ou arquivo travado. |
| Nenhum ciclo novo no log | A coleta parou. |
| **Todas** as impressoras offline de repente | Rede, ou `SNMP_COMMUNITY`. |
| Contadores de página parados | As leituras não estão chegando. |
| Frota encolheu | Alguém sincronizou. Confira o log. |

---

### Como reverter, em ordem de gravidade

| Situação | Ação |
|---|---|
| Algo estranho, sem certeza | **Pare o backend** (`Ctrl+C`). Nada é perdido; o painel só para de atualizar. |
| Dado errado no banco | Pare → restaure o backup (`OPERATIONS.md` §5) → suba. |
| A frota foi desativada por engano | Restaure o backup. **Não tente consertar à mão** — são dezenas de registros. |
| Suspeita de acesso indevido | **Desative a conta** em Usuários. Trocar a senha **não** derruba crachás ativos (D4). |
| Precisa parar tudo, agora | `Ctrl+C`, ou `scripts\Servico-PrinterControl.ps1 -Acao parar`. |

**A regra que resume tudo:** *na dúvida, pare o backend e restaure o backup.*
Parar não causa dano — só congela o painel. Deixar rodar com dado errado, sim.

---

## 8. Onde está o resto da documentação

| Arquivo | Para quê |
|---|---|
| [`OPERATIONS.md`](OPERATIONS.md) | Runbook completo: instalar como serviço, diagnóstico, backup, restauração. |
| [`TECHNICAL_DEBT.md`](TECHNICAL_DEBT.md) | **Registro único** da dívida técnica (D1–D13) e do que foi resolvido. |
| [`USER_GUIDE.md`](USER_GUIDE.md) | Guia de uso do painel, tela a tela. |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Arquitetura em detalhe técnico. |
| [`DEPLOYMENT_ARCHITECTURE.md`](DEPLOYMENT_ARCHITECTURE.md) | Plano de exposição externa (Cloudflare Tunnel, Vercel). |
| [`API_MAP.md`](API_MAP.md) | Todas as rotas da API. |
| [`DATA_FLOW.md`](DATA_FLOW.md) | Como o dado caminha, da impressora ao painel. |
| [`DEVELOPER_GUIDE.md`](DEVELOPER_GUIDE.md) | Para quem for mexer no código. |
| [`FEATURE_MATRIX.md`](FEATURE_MATRIX.md) | O que é funcional e o que é maquete. |

Com o backend no ar, a documentação **viva** da API fica em
`http://127.0.0.1:8000/docs` — todas as rotas, com botão para testar.
