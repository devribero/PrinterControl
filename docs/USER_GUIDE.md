# Guia de Uso do PrinterControl

Este guia descreve o comportamento atual, incluindo limitações, fallbacks e telas ainda não implementadas.

## Como acessar

Frontend:

```text
npm run dev
```

Backend:

```text
uvicorn app.main:app --reload
```

O comando de desenvolvimento do backend também aparece na entrada direta de `backend/app/main.py`, que usa a porta `8000`.

## Login — FUNCIONAL

A tela envia e-mail e senha para:

```text
POST /api/auth/login
```

A autenticação atual é real no backend: a senha é comparada com o hash armazenado e o backend retorna JWT.

O token fica no `localStorage` quando “lembrar” é selecionado, ou no `sessionStorage` caso contrário. O frontend também armazena localmente o nome/e-mail para exibição.

Não há login client-side fixo no fluxo atual, embora documentação legada mencione contas mockadas.

## Dashboard — FUNCIONAL/PARCIAL

O dashboard carrega:

```text
GET /api/printers/with-status
GET /api/alerts?resolved=false
GET /api/printers/monthly-report
```

Exibe:

- total de impressoras;
- online;
- offline;
- atenção;
- alertas ativos;
- tabela resumida;
- toner global;
- impressora com menor toner;
- gráficos mensais.

### Verificar agora

O botão **Verificar agora** somente repete as consultas GET. Ele não:

- faz scan de rede;
- consulta o Print Server;
- chama SNMP diretamente;
- executa `/api/collect`;
- executa `/api/servers/discover`;
- sincroniza o banco.

Se o backend estiver indisponível, o painel mostra dados de demonstração.

## Impressoras — FUNCIONAL/PARCIAL

A tela permite:

- pesquisar por texto;
- filtrar status;
- filtrar tipo;
- alternar lista/grade;
- paginar;
- abrir detalhes;
- visualizar toner;
- abrir o endereço web do IP.

### Ações

#### Acessar via web — PARCIAL

Abre:

```text
http://<ip>
```

Depende de o navegador ter rota para a rede corporativa e de a impressora aceitar HTTP.

#### Imprimir página de teste — SIMULADA

O botão apenas exibe um toast informando que o job foi enviado. Não há chamada para FastAPI, Windows, Print Server ou spooler.

#### Configurações — COMING SOON

A ação apenas informa que o gerenciamento remoto chegará em breve.

#### Adicionar impressora — AUSENTE/PARCIAL

Há indicação visual, mas a interface não executa o `POST /api/printers`.

## Toner — FUNCIONAL/PARCIAL

A página deriva os níveis dos dados retornados por `/api/printers/with-status`.

Classificação atual:

- até 10%: crítico;
- até 20%: atenção;
- acima de 20%: normal.

Sem leitura de toner, a impressora aparece sem comunicação ou sem dados de suprimento. Etiquetadoras e portáteis podem não consultar Printer-MIB.

O botão de atualização repete o carregamento geral; não inicia coleta SNMP.

## Alertas — FUNCIONAL na leitura; PARCIAL nas ações

Os alertas podem representar:

- impressora offline;
- toner preto baixo/crítico;
- toner ciano baixo/crítico;
- toner magenta baixo/crítico;
- toner amarelo baixo/crítico.

O backend gera alertas após cada leitura persistida. A tela consulta apenas alertas ativos por padrão.

A resolução e o envio manual de webhook existem como endpoints, mas não estão ligados a botões funcionais na tela atual.

## Relatórios — PARCIAL

O relatório mensal do backend é calculado com leituras acumulativas:

```text
maior contador do período - menor contador do período
```

A página apresenta:

- resumo da frota;
- contadores mensais;
- ranking;
- consumo por departamento;
- impressoras desativadas/devolvidas;
- exportação CSV.

O consumo por departamento e a lista de devolvidas/desativadas vêm de dados locais de demonstração, não de uma fonte completa do backend.

### Exportar CSV — FUNCIONAL

A exportação é feita no navegador usando os dados atualmente exibidos. Não existe endpoint dedicado de exportação.

## Histórico — PARCIAL

A matriz histórico × impressora usa os dados mensais mesclados no contexto. Pode usar relatório da API, mas mantém fallback para dados locais e JSON estático.

Não existe uma tela que consulte diretamente `GET /api/printers/{id}/readings` para construir um histórico detalhado por impressora.

## Mapeamento de Rede — COMING SOON

A página atual é apenas um placeholder. Não há topologia, ping sweep ou descoberta SNMP por subnet.

## Notificações — COMING SOON

A página atual é placeholder. O backend possui webhook opcional, mas a tela não oferece preferências nem botão de envio.

## Configurações, Usuários e Integrações — COMING SOON

As páginas atuais exibem “Em breve”.

## Interpretação dos dados

O painel pode estar em três situações:

1. **API real:** dados vindos do SQLite através do FastAPI.
2. **JSON legado/simulado:** dados em `public/data`.
3. **Demonstração:** arrays fixos em `src/data/printers.ts`.

O indicador de API respondida não prova que houve coleta SNMP real. A origem depende de como o banco ou os JSONs foram populados.
