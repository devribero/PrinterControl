# Dívida técnica — registro único

Este é o **lugar único** onde a dívida técnica do PrinterControl fica
registrada. `OPERATIONS.md`, `DEVELOPER_GUIDE.md` e `CONTEXTO-DESENVOLVIMENTO.md`
apontam para cá em vez de manterem listas próprias — foi assim que itens já
resolvidos continuaram aparecendo como pendentes em três documentos ao mesmo
tempo.

> **Sobre a numeração D1–D13.** A auditoria que levantou esta lista aconteceu
> numa sessão que foi interrompida antes de a lista ser gravada em arquivo.
> A numeração abaixo foi **reconstruída a partir do código atual**, não copiada
> da sessão perdida. Ela é fiel ao que o sistema é hoje; se você tiver a lista
> original em mãos e a ordem divergir, a original manda e esta deve ser
> renumerada.

**Data desta revisão:** 24 de agosto de 2026, após as correções da Fase 10.

---

## Como ler

| Coluna | Significado |
|---|---|
| **Impacto** | O que acontece de ruim, na prática, se nada for feito |
| **Bloqueia produção?** | Se a resposta é *sim*, não vá para produção sem resolver |
| **Custo** | Ordem de grandeza do trabalho para quitar |

Nada nesta lista está **bloqueando produção hoje**. As três coisas que
bloqueavam — injeção de comando no host do Print Server, escrita de leitura
sem validação nem guarda, e login sem limite de tentativas — foram corrigidas
e estão registradas na seção "Resolvido" no fim deste documento.

---

## D1 — Chave estrangeira órfã para `printers_old`

**Impacto:** `printer_readings` e `alerts` carregam FK apontando para
`printers_old`, uma tabela que a migração de schema renomeou e descartou.
Enquanto `PRAGMA foreign_keys` estiver **desligado** (o padrão do SQLite),
isso é inofensivo. Ligado, todo `INSERT` de leitura falha com
`no such table: main.printers_old` e **a coleta inteira para**.

**A armadilha:** alguém "consertando" o banco liga `foreign_keys=ON` por
achar que é boa prática e derruba a coleta sem entender por quê.

**Bloqueia produção?** Não — desde que ninguém ligue o pragma.
**Custo:** médio (reconstruir as duas tabelas, com backup e janela).
**Onde está documentado em detalhe:** `OPERATIONS.md` §8.
**Como verificar:** `PRAGMA foreign_key_check;`

---

## D2 — Sem migrações de banco versionadas

**Impacto:** o schema nasce de `SQLModel.metadata.create_all()` mais
migrações escritas à mão em `app/database.py`. Não existe histórico de
versões do banco, nem forma de aplicar/reverter uma mudança de forma
controlada. Cada alteração futura de schema é um script manual, testado uma
vez, sem rollback.

`create_all()` também **não altera tabela existente**: adicionar uma coluna a
um modelo não faz nada no banco já criado, e o erro só aparece em runtime.

**Bloqueia produção?** Não hoje. Vira crítico na primeira mudança de schema
depois que houver dados reais que importem.
**Custo:** médio (adotar Alembic, gerar a baseline do schema atual).

**Menor, do mesmo tipo:** `COLLECTION_PRINTER_IDS` existe em `config.py` e no
`.env.example` mas **não é lido por nada** — o scheduler coleta a frota ativa
inteira. Configuração morta que parece viva. (`SNMP_RETRIES` estava na mesma
situação; passou a ter efeito de verdade na Fase 17 — ver `snmp.py:_exchange`.)

---

## D3 — SQLite: um escritor por vez, um nó só

**Impacto:** o banco é um arquivo. Consequências concretas:

- **Um escritor por vez.** WAL + `busy_timeout=5000` fazem a segunda escrita
  esperar em vez de falhar, o que resolve o caso real (coleta escrevendo
  enquanto alguém usa o painel). Mas é uma fila, não paralelismo.
- **Um nó só.** Não dá para rodar duas instâncias do backend contra o mesmo
  banco em máquinas diferentes.
- **Backup e restauração são de arquivo inteiro** — não há point-in-time
  recovery.

Para ~85 impressoras coletadas a cada 5 minutos, com um punhado de pessoas no
painel, isto é **adequado** e a decisão de manter é consciente. O ponto de
virada seria multi-site ou dezenas de usuários simultâneos.

**Bloqueia produção?** Não.
**Custo:** alto para trocar (PostgreSQL); zero para manter.

---

## D4 — JWT sem revogação e sem refresh

**Impacto:** o token é *stateless* e vale 24 horas. Não existe lista de
tokens revogados, nem `logout` do lado do servidor, nem versão de senha no
usuário. Portanto:

- **trocar a senha NÃO derruba as sessões antigas** — quem tem um token
  emitido antes continua entrando até ele expirar;
- **desativar uma conta (`is_active=false`) tem efeito imediato** — isso é
  verificado a cada requisição em `require_user`, então este caminho funciona;
- um token vazado é válido por até 24h e não há como cancelá-lo.

Note a assimetria: **desativar a conta funciona; trocar a senha não basta.**
Se um token vazar, o procedimento correto hoje é **desativar a conta**, não
trocar a senha.

**Bloqueia produção?** Não, mas muda o procedimento de resposta a incidente —
está escrito em `VISAO_GERAL.md`, seção "se algo der errado".
**Custo:** baixo (campo `token_version` no usuário + checagem em `require_user`).

---

## D5 — Limite de tentativas de login vive na memória do processo

**Impacto:** a contagem de tentativas (`services/rate_limit.py`) é um
dicionário dentro do processo. Portanto:

- **reiniciar o serviço zera todas as contagens** — quem estava bloqueado
  volta a ter as 5 tentativas;
- se um dia houver mais de um worker do uvicorn, **cada um conta por si**, e
  o limite efetivo multiplica pelo número de workers;
- atrás do Cloudflare Tunnel, todo request chega com o mesmo IP de origem, e
  a contagem por IP vira praticamente uma contagem global. **É a contagem por
  e-mail que protege de verdade nesse cenário.**

A proteção é real e muito melhor que a ausência dela, mas não é à prova de um
atacante paciente que saiba reiniciar o serviço (o que exigiria acesso à
máquina — e nesse caso o login é o menor dos problemas).

**Bloqueia produção?** Não.
**Custo:** médio (mover para uma tabela no banco, ou Redis).

---

## D6 — O backend não fala HTTPS; depende inteiramente do túnel

**Impacto:** o uvicorn serve HTTP puro. A criptografia é **inteiramente**
responsabilidade do Cloudflare Tunnel na frente. Isso está correto para o
desenho atual — o backend não deve ser acessível de fora sem o túnel — mas
significa que, se a porta 8000 ficar exposta na rede, o tráfego **incluindo o
token no header `Authorization`** passa a trafegar em claro. O backend não tem
como se defender disso sozinho.

**✅ Corrigido (2026-08-24) o caminho que fazia exatamente isso.** O bloco de
execução direta no fim de `app/main.py` era:

```python
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
```

`0.0.0.0` significa "responda em **todas** as interfaces de rede" — a API
ficava acessível de qualquer máquina da rede, sem TLS, no momento em que
alguém rodasse o arquivo direto. `reload=True` ainda por cima ligava o
recarregamento automático, que não deve rodar em produção (reinicia o
processo a cada arquivo salvo e derruba a coleta agendada junto).

Hoje o bloco sobe em `127.0.0.1` fixo — o host **não** é configurável ali de
propósito: quem precisa expor a API tem o caminho oficial (serviço do Windows
+ Cloudflare Tunnel), e a execução direta não deve ser esse caminho. O reload
nasce desligado e só liga com `DEV_RELOAD=true` no ambiente.

Os dois comandos abaixo passaram a ser equivalentes em exposição de rede; o do
runbook continua sendo o de produção porque é o que o serviço usa.

- ✅ **produção:** `.\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000`
- ✅ **desenvolvimento:** `.\venv\Scripts\python.exe app/main.py` (com `DEV_RELOAD=true` se quiser reload)

**Bloqueia produção?** Não. O restante do D6 — HTTP puro dependendo do túnel
para TLS — continua válido: é o desenho aceito.

**Verificação obrigatória depois de subir:**
`netstat -ano | findstr :8000` deve mostrar `127.0.0.1:8000`, **nunca**
`0.0.0.0:8000`.
**Custo:** o do bloco de execução direta já foi pago (duas linhas). TLS próprio no backend continua fora de escopo.

---

## D7 — Testes são scripts soltos, sem framework, sem CI

**Impacto:** as ~18 suítes em `backend/tests_*.py` são scripts que imprimem
`[OK]`/`[FALHA]` e terminam com `SystemExit`. Não usam pytest. Consequências:

- **não existe um comando único** que rode tudo e dê um veredito;
- não há CI: nada roda os testes automaticamente antes de um commit;
- é fácil uma suíte quebrar e ninguém notar por semanas (foi exatamente o que
  aconteceu com D8 e D9);
- não há relatório de cobertura.

A qualidade do que os testes *verificam* é boa — o problema é o
empacotamento, não o conteúdo.

**Bloqueia produção?** Não.
**Custo:** médio (converter para pytest é mecânico mas são 18 arquivos).

---

## D8 — Duas suítes esperam 73 impressoras; o banco tem 79

**Impacto:** `tests_fleet.py` e `tests_printers_crud.py` têm o número **73**
escrito no código como expectativa. O banco real acumulou 79 impressoras.
As duas suítes **falham hoje**, e falhavam antes das mudanças da Fase 10 —
não é regressão, é expectativa desatualizada.

Isso é pior do que parece: **duas suítes vermelhas por um motivo conhecido
treinam a pessoa a ignorar suíte vermelha.** Quando uma delas quebrar por um
motivo real, ninguém vai olhar.

A intenção real desses testes é "todas as impressoras foram coletadas" e "a
contagem voltou ao que era antes", não "são exatamente 73" — a correção é
capturar a contagem no início do teste em vez de fixá-la.

**Bloqueia produção?** Não.
**Custo:** baixo (uma linha em cada arquivo).

---

## D9 — `tests_collect_api.py` não roda: `requests` não está instalado

**Impacto:** essa suíte importa `requests`, que não está no `requirements.txt`
nem instalado no venv. Ela **não roda desde que o venv foi recriado** e
ninguém notou — sintoma direto de D7.

A decisão pendente: portar para `httpx` (já é dependência declarada) ou assumir
`requests` como dependência. Portar é melhor — evita duas bibliotecas HTTP para
a mesma coisa.

**Bloqueia produção?** Não.
**Custo:** baixo.

---

## D10 — O frontend não tem nenhum teste automatizado

**Impacto:** zero cobertura de teste no painel. A única verificação automática
é `npm run lint` (oxlint) e `npm run build` (checagem de tipos do TypeScript).
Regressões de comportamento — um botão que para de chamar a API, um filtro que
some, o badge de demonstração que deixa de aparecer — só aparecem se alguém
clicar.

O badge "dados de demonstração" é o caso mais sensível: é a única coisa que
impede alguém de confundir a frota fictícia com a real, e nada garante
automaticamente que ele continue funcionando.

**Bloqueia produção?** Não.
**Custo:** médio (montar Vitest + Testing Library do zero).

---

## D11 — O painel cai em dados de demonstração quando a API não responde

**Impacto:** quando o backend não responde, o frontend exibe o conjunto de
demonstração em vez de uma tela vazia. Há mitigação real — faixa de aviso,
badge permanente, mensagem "Exibindo dados de demonstração" — e o rótulo do
ambiente vem de `GET /health`, ou seja, do **servidor que respondeu**, e não
de uma variável do build (que descreveria o bundle, não o servidor).

Ainda assim, o risco residual é de **interpretação humana**: alguém de
relance vê números plausíveis num painel e conclui que a frota está saudável,
quando na verdade o backend está fora do ar.

**Bloqueia produção?** Não — a mitigação é adequada.
**Custo:** baixo, se um dia for decidido substituir o fallback por um estado
vazio explícito. É uma **decisão de produto**, não um bug.

---

## D12 — Datas ingênuas no servidor, hora do navegador no cliente

**Impacto:** duas metades do mesmo problema.

No **backend**, quase todo timestamp usa `datetime.utcnow()`, que devolve uma
data *sem fuso* ("ingênua"). Ela é gravada e comparada como se fosse UTC — o
que é verdade, mas por convenção, não por declaração. Além disso `utcnow()`
está descontinuado desde o Python 3.12. (A emissão do JWT já foi migrada para
`datetime.now(timezone.utc)`; o resto não.)

No **frontend**, "última verificação há 5 minutos" é calculado com o relógio
do navegador contra um timestamp do servidor. Se o relógio da máquina de quem
olha estiver adiantado ou atrasado, **o painel mostra tempos errados** — e
"última coleta há 3 horas" errado é exatamente o tipo de informação que faz
alguém tomar a decisão errada.

**Bloqueia produção?** Não, mas é fonte de confusão difícil de diagnosticar.
**Custo:** médio (é mecânico, mas toca muitos arquivos).

---

## D13 — `/health` existe, mas nada o consulta

**Impacto:** o endpoint `/health` foi construído para monitoramento: reporta
`status: ok|degraded`, se o banco respondeu, se o scheduler está rodando, e
há quanto tempo o processo está de pé. **Nada consulta isso automaticamente.**

Na prática:

- se o banco travar, `/health` diz `degraded` — e ninguém vê;
- se o serviço estiver reiniciando em laço, `uptime_seconds` nunca cresce — e
  ninguém vê;
- se a coleta parar, `scheduler.running` fica `false` — e ninguém vê.

A informação existe; falta alguém perguntando. Um monitor externo (o próprio
Cloudflare, ou um check gratuito de uptime) resolveria com pouca configuração.

**Atenção:** o endpoint responde **200 mesmo degradado**, de propósito — o
processo está de pé, e derrubar o healthcheck faria um supervisor reiniciá-lo
em laço sem corrigir a causa. Um monitor precisa ler o campo `status`, **não
apenas o código HTTP**.

**Bloqueia produção?** Não, mas é o item desta lista com melhor relação
benefício/custo.
**Custo:** baixo.

---

## D14 — `httpx` sem teto de versão quebrava todas as suítes que usam `TestClient`

**Impacto:** `requirements.txt` não fixa `httpx`. Um `pip install -r
requirements.txt` em venv limpo instalou `httpx 0.28.1`, que removeu o
parâmetro `app=` do `Client.__init__` — e `starlette==0.35.1` (fixo) ainda
depende dele em `TestClient`. Resultado: **11 das 18 suítes de teste** (as que
sobem `TestClient(app)`) quebravam com `TypeError` no import, antes de rodar
um único caso.

Verificado nesta sessão (24/08/2026): `pip install "httpx<0.28"` resolveu as
11 suítes imediatamente, sem tocar em código.

**Bloqueia produção?** Não — é dependência de teste, não de runtime do
servidor. Mas **bloqueia detectar regressão real**: um venv recriado do zero
(como o desta sessão) começa com 11 suítes vermelhas por um motivo que não é
bug de aplicação, o mesmo padrão de "aprender a ignorar vermelho" do D8.
**Custo:** baixo — adicionar `httpx<0.28` (ou atualizar para uma starlette
que suporte a nova API) em `requirements.txt`.

---

## D15 — `requirements.txt` está em UTF-16

**Impacto:** o arquivo é `UTF-16 little-endian` com CRLF, não UTF-8. `pip
install -r requirements.txt` funciona normalmente (pip lê o BOM), mas
qualquer ferramenta de texto Unix (`cat`, `grep`, editores que assumem UTF-8)
mostra bytes nulos entre cada caractere. Provável causa: gerado por
`pip freeze > requirements.txt` num PowerShell com `$OutputEncoding`/
`Out-File` padrão UTF-16.

**Bloqueia produção?** Não. **Custo:** trivial — reescrever o arquivo em
UTF-8 (`Get-Content -Encoding Unicode requirements.txt | Set-Content
-Encoding utf8 requirements.txt` ou equivalente).

---

## D16 — `backend/.env` em produção estava configurado como `demo`/`mock`, não `production`

**Impacto:** ao verificar a saúde do backend nesta sessão (24/08/2026),
`https://elginprint.devribero.online/health` respondeu **502** (processo
fora do ar — ver nota em `OPERATIONS.md` sobre o backend não estar mais
rodando como tarefa agendada). Ao subir o processo manualmente para
diagnosticar, `backend/.env` **na máquina de produção** continha:

```
ENVIRONMENT=demo
PRINT_SERVER_MODE=mock
ALLOW_MOCK_COLLECT=true
```

Isso contradiz `OPERATIONS.md`, que documenta a configuração de produção como
`ENVIRONMENT=production` / `PRINT_SERVER_MODE=real`. Ou o `.env` foi trocado
para teste local em algum momento e nunca revertido, ou a instância de
produção nunca teve os valores que a documentação descreve.

**O processo foi encerrado imediatamente** nesta sessão, sem restaurar os
valores de produção — restaurar exige `SECRET_KEY` própria e confirmação de
que é seguro apontar para o Print Server real, decisão que não deve ser
tomada sem quem opera o ambiente. **O backend de produção ficou fora do ar ao
final desta sessão**, no mesmo estado 502 em que foi encontrado.

**Bloqueia produção?** **Sim, até ser corrigido.** Ver roteiro de reativação
em `docs/GUIA_RAPIDO.md` §2 antes de subir o serviço de novo.
**Custo:** baixo se os valores de produção corretos estiverem anotados em
algum lugar seguro; alto (gerar nova `SECRET_KEY`, confirmar `CORS_ORIGINS`,
confirmar acesso real ao Print Server) se não estiverem.

---

# Resolvido na Fase 10 (24/08/2026)

Registrado aqui para que estes itens **não voltem** às listas de pendências
dos outros documentos.

| Era | O que era | Como foi fechado |
|---|---|---|
| **Injeção de comando no Print Server** | O host ia direto para uma linha de PowerShell (`Get-Printer -ComputerName '<host>'`). Um host como `srv'; Remove-Item C:\ -Recurse -Force; '` executava comandos arbitrários com os privilégios do serviço. | *Allowlist* por regex (hostname/FQDN/IPv4) em `validar_host()`, aplicada em `_real_discover` **e** no cadastro do Print Server; escape de aspas simples como segunda camada. Cobertura em `tests_print_server.py` §8–10. |
| **Escrita de leitura sem validação** | `POST /api/printers/{id}/readings` aceitava status inventado, contador negativo e toner em 5000% — corrompendo painel, relatório mensal e motor de alertas de uma vez. | Validação em `PrinterReadingCreate`: status na lista conhecida, `page_count >= 0`, toner 0–100. Cobertura em `tests_environment.py` §14. |
| **Porta dos fundos da Fase 9** | A mesma rota era o único caminho de escrita que **não** passava pela guarda de ambiente: `/api/collect` recusava simulação em produção, mas dava para gravar a mesma leitura fictícia por ali. | `bloquear_mock_em_producao()` aplicada à rota (409 em produção). Cobertura em `tests_environment.py` §13. |
| **Login sem limite de tentativas** | Força bruta na velocidade da rede contra qualquer conta. | Janela deslizante por IP **e** por e-mail, 429 com `Retry-After`. Limitações conhecidas viraram **D5**. |
| **Oráculo de tempo no login** | E-mail inexistente respondia em microssegundos; senha errada, em dezenas de milissegundos. Comparar os tempos revelava **quais e-mails têm conta**. | `verify_password` roda contra um hash descartável quando a conta não existe. Medido: 65,2 ms vs 65,8 ms. |
| **Leituras sem teto** | `?limit=99999999` carregava o histórico inteiro; `/monthly-report` lia **a tabela inteira de leituras** a cada chamada — que cresce a cada ciclo de coleta, para sempre. | `Query(ge=1, le=500)` em readings/printers/alerts (+ `offset`), e janela em meses no relatório (padrão 12, máximo 60). |
| **Senha "123" nas contas de administrador** | As duas únicas contas capazes de criar usuários e sincronizar Print Servers tinham senha de três caracteres — abaixo do mínimo de 8 que a própria API exige das outras. | `seed.py` gera senha aleatória forte e a mostra **uma única vez**, ou usa `SEED_ADMIN_PASSWORD`. Bancos antigos: `python seed.py --resetar-senhas`. |
| **`python-jose 3.3.0` com CVE** | CVE-2024-33663 (confusão de algoritmo) e CVE-2024-33664 (bomba de descompressão em JWE), mais o `ecdsa` arrastado junto com a CVE-2024-23342, que os mantenedores declararam que **não** será corrigida. | Migrado para **PyJWT**; `python-jose` e `ecdsa` desinstalados. Tokens existentes continuam válidos (mesmo formato, mesmo HS256). |
| **`httpx` não declarado / `fastapi` sem versão** | `httpx` era usado diretamente (webhook + todos os testes) mas vinha só como dependência indireta; `fastapi` não tinha versão nenhuma. | Ambos declarados em `requirements.txt`, com teto de major. |

---

## Itens que os documentos antigos listavam e que **já não existem**

Corrigido em `DEVELOPER_GUIDE.md` §"Riscos conhecidos" e em
`CONTEXTO-DESENVOLVIMENTO.md`:

- ~~"`SECRET_KEY` padrão não é apropriado para produção"~~ → o backend
  **recusa subir** em produção com a chave de desenvolvimento ou com menos de
  32 caracteres.
- ~~"CORS atual é apenas local"~~ → CORS é por ambiente, e produção recusa
  subir com lista vazia, `*`, localhost ou origem sem HTTPS.
- ~~"resolução de alerta não está protegida por JWT"~~ → exige `operator`
  desde a Fase 1.
- ~~"o botão 'Verificar agora' não dispara coleta"~~ → dispara.
- ~~"Login não é autenticação real / contas hardcoded no frontend"~~ → JWT
  real contra o backend, contas no banco, três papéis.
- ~~"Sem backend/banco de dados"~~ → FastAPI + SQLite + SQLModel desde a
  Fase 1.
- ~~"Frontend puro Vite + React"~~ → Next.js 16.
