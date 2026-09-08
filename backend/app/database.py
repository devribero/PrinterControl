import logging
import shutil
from datetime import datetime
from pathlib import Path

from sqlmodel import create_engine, Session, SQLModel
from app.config import settings

logger = logging.getLogger("printercontrol.database")

engine = create_engine(
    settings.database_url,
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
)


# ---------------------------------------------------------------------------
#  PRAGMAs de producao (Fase 10)
#
#  Aplicados por conexao — no SQLite, `journal_mode` e persistente no arquivo,
#  mas `busy_timeout` e `synchronous` valem por conexao e precisam ser
#  reaplicados sempre.
# ---------------------------------------------------------------------------
if "sqlite" in settings.database_url:
    from sqlalchemy import event

    @event.listens_for(engine, "connect")
    def _sqlite_pragmas(dbapi_connection, _record):
        cursor = dbapi_connection.cursor()
        try:
            # WAL: leitor nao bloqueia escritor e vice-versa. Importa por dois
            # motivos aqui — o ciclo de coleta escreve enquanto o painel le, e
            # o backup online consegue rodar com o servico no ar. Tambem
            # sobrevive melhor a uma queda abrupta do processo: o journal fica
            # separado do banco e e reaplicado na proxima abertura.
            cursor.execute("PRAGMA journal_mode=WAL")

            # Sem isto, duas escritas simultaneas devolvem "database is locked"
            # IMEDIATAMENTE. Com 5s, a segunda espera a primeira terminar — que
            # e o comportamento que se espera de um ciclo de coleta rodando
            # junto com alguem usando o painel.
            cursor.execute("PRAGMA busy_timeout=5000")

            # NORMAL (e nao OFF) mantem a durabilidade contra queda do
            # PROCESSO, que e o cenario real aqui: o servico morre e a tarefa
            # agendada o reergue. FULL so acrescentaria protecao contra queda
            # de energia do sistema inteiro, ao custo de um fsync por
            # transacao em cada leitura gravada.
            cursor.execute("PRAGMA synchronous=NORMAL")

            # foreign_keys CONTINUA DESLIGADO — mas por um motivo diferente
            # do que estava escrito aqui antes (QA-01).
            #
            # O motivo ANTIGO acabou: as FKs de `printer_readings`,
            # `printer_monthly`, `alerts` e `toner_history` apontavam para
            # "printers_old", tabela que a migracao da Etapa 4 renomeou e
            # descartou, e ligar a checagem fazia todo INSERT de leitura
            # falhar com "no such table: main.printers_old".
            # _migrate_child_foreign_keys() corrigiu isso: o schema agora
            # descreve as relacoes reais e `PRAGMA foreign_key_check` passa
            # limpo (eram 33.859 violacoes).
            #
            # O motivo ATUAL e que LIGAR a checagem quebra quatro caminhos que
            # funcionam hoje, e cada um precisa de decisao propria:
            #
            #   1. _finish_printer_migration() faz `DELETE FROM printers` com
            #      as leituras ainda apontando para elas — a migracao da
            #      Etapa 4 deixa de rodar em bancos que ainda nao passaram
            #      por ela;
            #   2. apagar um alerta que ja gerou Notification passa a ser
            #      recusado, em vez de deixar a notificacao com referencia
            #      pendurada (que e o que a interface hoje trata como null);
            #   3. `POST /api/notifications` aceita `alert_id` do cliente sem
            #      conferir se existe: um id inventado viraria 500 em vez de
            #      ser gravado e exibido sem referencia;
            #   4. as fixtures de tests_printer_sync e tests_webhook apagam
            #      linhas em ordem incompativel com a checagem.
            #
            # Nenhum dos quatro e dificil; todos mudam comportamento
            # observavel e merecem um passo proprio, com teste. Ate la o
            # schema esta correto — o que faltava para essa mudanca sequer
            # ser possivel — e a integridade referencial continua sustentada
            # pelo codigo, como sempre foi (nada apaga impressora: o que some
            # do Print Server vira active=False).
        finally:
            cursor.close()


def create_db_and_tables():
    # Garante que TODOS os modelos estejam registrados em SQLModel.metadata
    # antes do create_all. Sem isto, o create_all so cria as tabelas dos
    # modelos que alguem ja tenha importado por acaso — quem chama esta
    # funcao de um script enxuto (ou de um teste) acabaria com um banco
    # incompleto, e as migracoes abaixo falhariam procurando uma tabela que
    # nunca foi criada.
    import app.models  # noqa: F401

    # A migracao de printers PRECISA rodar antes do create_all: se ela
    # rodasse depois, o create_all encontraria uma tabela "printers" com o
    # schema antigo (nome de indice `ix_printers_ip` de um UNIQUE INDEX) e
    # tentaria recriar o indice homonimo (agora nao-unico) por cima,
    # colidindo com "index ix_printers_ip already exists". Rodando antes,
    # quando o create_all chegar em printers ela ja esta no schema atual
    # (ou nao existe ainda e ele a cria do zero, sem colisao).
    _migrate_printer_schema()
    SQLModel.metadata.create_all(engine)
    _migrate_alert_type()
    _migrate_alert_value()
    _migrate_reading_uptime()
    _migrate_user_rbac()
    _migrate_user_login_fields()
    _migrate_user_token_version()
    _migrate_print_servers()
    _migrate_child_foreign_keys()


def _migrate_alert_type():
    """Adiciona alerts.alert_type em bancos criados antes da Etapa 8A."""
    from sqlalchemy import text

    with engine.connect() as conn:
        cols = {row[1] for row in conn.execute(text("PRAGMA table_info(alerts)"))}
        if cols and "alert_type" not in cols:
            conn.execute(text("ALTER TABLE alerts ADD COLUMN alert_type VARCHAR"))
            conn.commit()


def _migrate_alert_value():
    """
    Adiciona alerts.value em bancos criados antes da escada de re-alerta de
    toner. Puramente aditiva e idempotente, mesmo padrao de
    _migrate_alert_type(): so roda ALTER TABLE se a coluna ainda nao existe.
    Alertas antigos ficam com value=NULL — o alert_engine trata isso como
    "sem referencia anterior", entao o proximo alerta de toner dessa
    impressora dispara normalmente.
    """
    from sqlalchemy import text

    with engine.connect() as conn:
        cols = {row[1] for row in conn.execute(text("PRAGMA table_info(alerts)"))}
        if cols and "value" not in cols:
            conn.execute(text("ALTER TABLE alerts ADD COLUMN value INTEGER"))
            conn.commit()


def _migrate_reading_uptime():
    """
    Etapa 7: adiciona printer_readings.uptime em bancos criados antes desta
    etapa. Puramente aditiva e idempotente — mesmo padrao de
    _migrate_alert_type(): so roda ALTER TABLE se a coluna ainda nao existe,
    nunca recria/renomeia/apaga a tabela. Leituras antigas ficam com
    uptime=NULL; nenhuma linha existente e reescrita.
    """
    from sqlalchemy import text

    with engine.connect() as conn:
        cols = {row[1] for row in conn.execute(text("PRAGMA table_info(printer_readings)"))}
        if cols and "uptime" not in cols:
            conn.execute(text("ALTER TABLE printer_readings ADD COLUMN uptime VARCHAR"))
            conn.commit()


def _migrate_user_rbac():
    """
    Fase 1 (RBAC): adiciona users.role e users.is_active em bancos criados
    antes desta fase. Puramente aditiva e idempotente, mesmo padrao de
    _migrate_alert_type(): so roda ALTER TABLE se a coluna ainda nao existe,
    nunca recria/renomeia/apaga a tabela — nenhum usuario, senha ou historico
    e perdido.

    Backfill deliberado: contas que ja existiam recebem role="admin". Ate
    esta fase, qualquer usuario autenticado podia executar toda e qualquer
    operacao; rebaixa-las para "viewer" tiraria acesso de quem opera o
    sistema hoje. Contas NOVAS nascem como "viewer" (default do modelo) e
    precisam de um admin para serem promovidas.
    """
    from sqlalchemy import text

    with engine.connect() as conn:
        cols = {row[1] for row in conn.execute(text("PRAGMA table_info(users)"))}
        if not cols:
            return  # tabela ainda nao existe; create_all ja cuidou/cuidara

        changed = False

        if "role" not in cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR"))
            conn.execute(text("UPDATE users SET role = 'admin' WHERE role IS NULL"))
            logger.warning(
                "Migracao RBAC: coluna users.role criada; usuarios existentes "
                "promovidos a 'admin' para preservar o acesso atual."
            )
            changed = True

        if "is_active" not in cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN is_active BOOLEAN"))
            conn.execute(text("UPDATE users SET is_active = 1 WHERE is_active IS NULL"))
            logger.warning("Migracao RBAC: coluna users.is_active criada (todos ativos).")
            changed = True

        # Rede de seguranca para bancos migrados por uma versao anterior desta
        # funcao e que possam ter linhas com valor nulo.
        conn.execute(text("UPDATE users SET role = 'viewer' WHERE role IS NULL OR role = ''"))
        conn.execute(text("UPDATE users SET is_active = 1 WHERE is_active IS NULL"))

        if changed:
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_users_role ON users (role)"))

        conn.commit()


def _migrate_user_login_fields():
    """
    Login por username e troca de senha obrigatoria (2026-08-24).

    Adiciona `users.username` e `users.must_change_password` em bancos
    criados antes desta mudanca. Aditiva e idempotente, mesmo padrao de
    _migrate_alert_type(): so roda ALTER TABLE se a coluna ainda nao existe,
    e nunca recria/renomeia/apaga a tabela.

    Os defaults sao os conservadores:

      username = NULL              a conta continua entrando so por e-mail,
                                   exatamente como antes. Preencher e ato
                                   deliberado (seed, ou PATCH /api/users).
      must_change_password = 0     nenhuma conta existente e trancada fora do
                                   sistema por causa desta migracao. A flag
                                   passa a valer para contas criadas ou
                                   resetadas DEPOIS daqui.

    O indice de `username` e UNIQUE e leva o mesmo nome que o SQLModel daria
    a ele num banco criado do zero (`ix_users_username`), para que os dois
    caminhos — banco novo e banco migrado — cheguem ao mesmo schema. No
    SQLite um indice UNIQUE aceita varias linhas com NULL, entao contas sem
    username convivem sem excecao.
    """
    from sqlalchemy import text

    with engine.connect() as conn:
        cols = {row[1] for row in conn.execute(text("PRAGMA table_info(users)"))}
        if not cols:
            return  # tabela ainda nao existe; create_all ja cuidou/cuidara

        if "username" not in cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN username VARCHAR"))
            logger.warning(
                "Migracao de login: coluna users.username criada (vazia; "
                "contas existentes continuam entrando pelo e-mail)."
            )

        if "must_change_password" not in cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN must_change_password BOOLEAN"))
            logger.warning(
                "Migracao de login: coluna users.must_change_password criada "
                "(0 para todas as contas existentes)."
            )

        # Rede de seguranca: nulo aqui viraria None em Python e um `if
        # user.must_change_password` silenciosamente falso — o que por acaso
        # e o comportamento desejado, mas depender de acaso em algo que
        # tranca ou destranca o sistema nao e aceitavel.
        conn.execute(
            text("UPDATE users SET must_change_password = 0 WHERE must_change_password IS NULL")
        )

        conn.execute(
            text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username ON users (username)")
        )
        conn.commit()


def _migrate_user_token_version():
    """
    QA-04: adiciona `users.token_version` em bancos criados antes da
    revogacao de sessao. Aditiva e idempotente, mesmo padrao de
    _migrate_alert_type(): so roda ALTER TABLE se a coluna ainda nao existe,
    e nunca recria/renomeia/apaga a tabela.

    Toda conta comeca em 0, igual a uma conta nova. Tokens emitidos antes
    desta mudanca nao carregam o campo `ver` e sao recusados por
    decode_token — ou seja, o deploy desta correcao desloga todo mundo uma
    vez. E deliberado: aceitar os tokens antigos manteria de pe exatamente
    as sessoes que a correcao existe para poder encerrar.
    """
    from sqlalchemy import text

    with engine.connect() as conn:
        cols = {row[1] for row in conn.execute(text("PRAGMA table_info(users)"))}
        if not cols:
            return  # tabela ainda nao existe; create_all ja cuidou/cuidara

        if "token_version" not in cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN token_version INTEGER"))
            logger.warning(
                "Migracao QA-04: coluna users.token_version criada. As sessoes "
                "abertas no momento do deploy precisarao de novo login."
            )

        # Rede de seguranca: NULL viraria None em Python e a comparacao com o
        # `ver` do token (int) daria sempre diferente — a conta nao entraria
        # mais em lugar nenhum.
        conn.execute(text("UPDATE users SET token_version = 0 WHERE token_version IS NULL"))
        conn.commit()


def _migrate_print_servers():
    """
    Fase 4: registro de Print Servers.

    A tabela `print_servers` em si e criada pelo create_all. Esta migracao
    cuida do que o create_all nao faz, e e puramente ADITIVA e idempotente,
    no mesmo padrao de _migrate_user_rbac():

      1. adiciona `printers.print_server_id` se ainda nao existir;
      2. registra um PrintServer para cada host DISTINTO ja presente em
         `printers.server` (o servidor sempre existiu como string — aqui ele
         so passa a ter uma linha propria), mais o host configurado no .env,
         mesmo que ainda nao tenha impressoras;
      3. preenche `printers.print_server_id` casando pelo host.

    Nenhuma linha de `printers` e apagada ou reescrita alem dessa coluna
    nova; nenhuma impressora muda de servidor. Rodar duas vezes nao duplica
    servidor nem altera nada (os INSERTs sao condicionais e o UPDATE e
    idempotente).
    """
    from sqlalchemy import text

    now = datetime.utcnow().isoformat(sep=" ")

    with engine.connect() as conn:
        tabelas = {
            row[0]
            for row in conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        }
        if "print_servers" not in tabelas or "printers" not in tabelas:
            return  # banco novo: create_all ja criou tudo no schema atual

        cols = {row[1] for row in conn.execute(text("PRAGMA table_info(printers)"))}
        if cols and "print_server_id" not in cols:
            conn.execute(text("ALTER TABLE printers ADD COLUMN print_server_id INTEGER"))
            conn.execute(
                text("CREATE INDEX IF NOT EXISTS ix_printers_print_server_id "
                     "ON printers (print_server_id)")
            )
            logger.warning("Migracao Fase 4: coluna printers.print_server_id criada.")

        # Hosts que ja existem como string nas impressoras + o host do .env.
        hosts = {
            row[0]
            for row in conn.execute(text("SELECT DISTINCT server FROM printers WHERE server <> ''"))
            if row[0]
        }
        if settings.print_server_host:
            hosts.add(settings.print_server_host)

        for host in sorted(hosts):
            ja_existe = conn.execute(
                text("SELECT 1 FROM print_servers WHERE host = :host"), {"host": host}
            ).first()
            if ja_existe:
                continue
            conn.execute(
                text(
                    """
                    INSERT INTO print_servers
                        (host, name, mode, active, last_status, last_error,
                         last_seen_at, last_sync_at, created_at, updated_at)
                    VALUES
                        (:host, :host, :mode, 1, 'unknown', NULL,
                         NULL, NULL, :now, :now)
                    """
                ),
                # O modo global vigente vira o modo inicial de cada servidor
                # registrado: e o comportamento que o sistema ja tinha.
                {"host": host, "mode": settings.print_server_mode, "now": now},
            )
            logger.warning("Migracao Fase 4: Print Server registrado | host=%s", host)

        # Liga as impressoras ao registro. So preenche o que esta nulo.
        conn.execute(
            text(
                """
                UPDATE printers
                   SET print_server_id = (
                        SELECT ps.id FROM print_servers ps WHERE ps.host = printers.server
                   )
                 WHERE server <> '' AND print_server_id IS NULL
                """
            )
        )
        conn.commit()


def _migrate_child_foreign_keys():
    """
    QA-01: reaponta para `printers` as FKs que ficaram em `printers_old`.

    O QUE ACONTECEU
    ---------------
    A Etapa 4 recriou `printers` para trocar a identidade de `ip UNIQUE` para
    (server, name). O caminho foi `ALTER TABLE printers RENAME TO
    printers_old` (ver _migrate_printer_schema). O SQLite moderno, ao
    renomear uma tabela, REESCREVE as referencias a ela nas outras tabelas —
    entao as quatro filhas passaram a declarar FK para `printers_old`, que na
    sequencia foi apagada. O resultado e um schema que descreve uma relacao
    com uma tabela inexistente: `PRAGMA foreign_key_check` acusava 33.859
    violacoes, e `PRAGMA integrity_check` continuava dizendo "ok" porque ele
    nao olha FK.

    Nao havia corrupcao de dado — nenhuma linha ficou orfa, os printer_id
    todos casam com `printers` — mas o schema mentia, e era essa mentira que
    obrigava a manter `PRAGMA foreign_keys` desligado.

    COMO CORRIGE
    ------------
    O procedimento de troca de schema documentado pelo proprio SQLite, por
    tabela e dentro de UMA transacao:

        renomeia X -> X_fk_old  ->  recria X pelo modelo (FK correta)
        -> copia os dados  ->  apaga X_fk_old

    Tres cuidados que nao sao opcionais aqui:

    `legacy_alter_table=ON` durante o RENAME. Sem ele o SQLite repete
    exatamente o erro original: ao renomear `alerts`, a FK de `notifications`
    seria reescrita para `alerts_fk_old` e o problema so mudaria de lugar.

    Os indices de X_fk_old sao apagados antes de recriar X. Nomes de indice
    sao globais no banco, nao por tabela; sem isso o CREATE INDEX da tabela
    nova colide com o indice homonimo ainda preso a antiga.

    Uma transacao por tabela. Uma interrupcao no meio (o `--reload` do uvicorn
    matando o processo, que ja aconteceu neste projeto — ver
    _migrate_printer_schema) reverte aquela tabela inteira; a proxima
    inicializacao refaz.

    Idempotente: le a FK atual e nao faz nada onde ela ja aponta para
    `printers`. Em banco novo tambem nao faz nada — o create_all ja o cria
    correto, porque os modelos sempre declararam `foreign_key="printers.id"`.
    """
    import app.models  # noqa: F401  (registra todo o metadata)

    from sqlalchemy import text
    from sqlalchemy.schema import CreateIndex, CreateTable

    # O metadata do SQLModel e a fonte do schema correto: toda tabela mapeada
    # pode ser reconstruida a partir dele. Varrer o metadata (em vez de uma
    # lista fixa de nomes) e o que faz esta migracao pegar tambem os casos que
    # ninguem previu — foi assim que `notifications`, apontando para um
    # `alerts_fk_old` deixado por uma tentativa interrompida, entrou aqui.
    modelos = {
        tabela.name: tabela for tabela in SQLModel.metadata.sorted_tables
    }

    with engine.connect() as conn:
        existentes = {
            row[0]
            for row in conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        }

        pendentes = []
        for tabela in existentes:
            if tabela not in modelos:
                continue  # tabela sem modelo: nao ha schema de referencia
            alvos = {
                row[2] for row in conn.execute(text(f"PRAGMA foreign_key_list({tabela})"))
            }
            # Alvo que nao existe como tabela = relacao declarada com algo que
            # nao esta la. `printers_old` e o caso historico; qualquer
            # `*_fk_old` de uma migracao interrompida cai na mesma rede.
            if alvos - existentes:
                pendentes.append((tabela, sorted(alvos - existentes)))

    if not pendentes:
        return

    logger.warning(
        "Migracao QA-01: %d tabela(s) com FK apontando para tabela inexistente: %s",
        len(pendentes),
        "; ".join(f"{t} -> {', '.join(a)}" for t, a in pendentes),
    )
    pendentes = [t for t, _ in pendentes]

    backup_path = _sqlite_backup_path()
    if backup_path and backup_path.exists():
        stamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        backup = backup_path.with_name(f"{backup_path.stem}.backup-fk-{stamp}{backup_path.suffix}")
        shutil.copyfile(backup_path, backup)
        logger.warning("Backup do banco criado em: %s", backup)

    # DDL da tabela nova, gerado a partir do modelo (fonte unica do schema) e
    # executado adiante pelo driver. E preciso te-lo como TEXTO porque o
    # rebuild inteiro roda numa conexao crua — ver a nota dos PRAGMAs abaixo.
    def _ddl(tabela_modelo):
        criar = [str(CreateTable(tabela_modelo).compile(engine)).strip()]
        criar += [str(CreateIndex(ix).compile(engine)).strip() for ix in tabela_modelo.indexes]
        return criar

    for tabela in pendentes:
        tabela_modelo = modelos[tabela]
        antiga = f"{tabela}_fk_old"

        # Conexao CRUA, e nao uma Connection do SQLAlchemy: `foreign_keys` e
        # `legacy_alter_table` sao ignorados silenciosamente dentro de uma
        # transacao, e a Connection abre uma implicitamente no primeiro
        # execute. Foi exatamente o que aconteceu na primeira tentativa desta
        # migracao: o legacy_alter_table nao pegou e o RENAME de `alerts`
        # reescreveu a FK de `notifications` para `alerts_fk_old` —
        # reproduzindo, em outra tabela, o defeito que estamos corrigindo.
        bruta = engine.raw_connection()
        try:
            driver = bruta.driver_connection
            isolamento_anterior = driver.isolation_level
            driver.isolation_level = None  # controle manual de BEGIN/COMMIT
            cur = driver.cursor()
            try:
                # OFF durante o rebuild e o procedimento que o proprio SQLite
                # documenta: a tabela antiga e a nova coexistem por alguns
                # comandos, e a checagem reclamaria desse estado intermediario.
                # A verificacao vem depois, com foreign_key_check.
                cur.execute("PRAGMA foreign_keys=OFF")
                cur.execute("PRAGMA legacy_alter_table=ON")

                cur.execute("BEGIN")
                try:
                    # Sobra de uma tentativa anterior interrompida.
                    cur.execute(f"DROP TABLE IF EXISTS {antiga}")
                    cur.execute(f"ALTER TABLE {tabela} RENAME TO {antiga}")

                    # Nomes de indice sao globais no banco, nao por tabela:
                    # sem apagar os da antiga, o CREATE INDEX da nova colide.
                    for indice in [
                        row[1]
                        for row in cur.execute(f"PRAGMA index_list('{antiga}')").fetchall()
                        if not row[1].startswith("sqlite_autoindex")
                    ]:
                        cur.execute(f"DROP INDEX IF EXISTS {indice}")

                    colunas_antigas = [
                        row[1] for row in cur.execute(f"PRAGMA table_info({antiga})").fetchall()
                    ]

                    for comando in _ddl(tabela_modelo):
                        cur.execute(comando)

                    # So as colunas presentes dos DOIS lados. Uma coluna que o
                    # modelo ganhou e a tabela antiga nao tem fica com o
                    # default; uma que so a antiga tem e descartada com ela.
                    colunas_novas = {c.name for c in tabela_modelo.columns}
                    comuns = [c for c in colunas_antigas if c in colunas_novas]
                    lista = ", ".join(comuns)
                    cur.execute(f"INSERT INTO {tabela} ({lista}) SELECT {lista} FROM {antiga}")
                    cur.execute(f"DROP TABLE {antiga}")
                    cur.execute("COMMIT")
                except Exception:
                    cur.execute("ROLLBACK")
                    raise
            finally:
                cur.execute("PRAGMA legacy_alter_table=OFF")
                cur.execute("PRAGMA foreign_keys=ON")
                cur.close()
                driver.isolation_level = isolamento_anterior
        finally:
            bruta.close()

        logger.warning("Migracao QA-01: %s reconstruida com FK para printers.", tabela)

    with engine.connect() as conn:
        violacoes = len(list(conn.execute(text("PRAGMA foreign_key_check"))))
    if violacoes:
        # Nao levanta: o banco esta em estado consistente (as copias foram
        # atomicas) e derrubar o boot aqui deixaria o sistema fora do ar por
        # causa de um dado preexistente. Registra alto para aparecer.
        logger.error(
            "Migracao QA-01: ainda ha %d violacao(oes) de FK apos a reconstrucao. "
            "Investigue com PRAGMA foreign_key_check antes de confiar na checagem.",
            violacoes,
        )
    else:
        logger.warning("Migracao QA-01 concluida: PRAGMA foreign_key_check limpo.")


def _sqlite_backup_path() -> Path | None:
    """Caminho do arquivo .db atual, se o banco for SQLite em disco (nao :memory:)."""
    prefix = "sqlite:///"
    if not settings.database_url.startswith(prefix):
        return None
    raw = settings.database_url[len(prefix):]
    if raw == ":memory:":
        return None
    return Path(raw)


def _migrate_printer_schema():
    """
    Etapa 4 — reconstroi `printers` para trocar a identidade de `ip UNIQUE`
    para (server, name), permitindo impressoras no mesmo IP (o Print Server
    do Main.ps1 tem casos assim).

    SQLite nao suporta `ALTER TABLE ... DROP CONSTRAINT`, entao a unica forma
    de remover o UNIQUE antigo e recriar a tabela:
        1. backup do arquivo .db inteiro (migracao reversivel: basta
           restaurar o backup se algo der errado)
        2. renomeia printers -> printers_old (instrucao unica, atomica)
        3. _finish_printer_migration(): cria a tabela nova + copia os dados
           + apaga printers_old, tudo dentro de UMA transacao

    O passo 3 e critico: um processo com `uvicorn --reload` pode ser morto
    no meio da migracao quando outro arquivo e salvo (foi exatamente o que
    aconteceu ao desenvolver esta etapa — o servidor local do usuario
    recarregou e interrompeu a copia, deixando `printers` vazia com
    `printers_old` intacta ao lado). Por isso o passo 3 roda inteiro dentro
    de `engine.begin()`: SQLite reverte DDL de uma transacao incompleta
    sozinho ao reabrir o arquivo, entao uma interrupcao no meio nunca deixa
    `printers` pela metade — na pior das hipoteses fica exatamente como
    estava antes do passo 3 comecar (com `printers_old` la), e a proxima
    inicializacao RETOMA em vez de considerar "ja migrado" so por existir a
    coluna `server`.
    """
    from sqlalchemy import text

    with engine.connect() as conn:
        tables = {
            row[0]
            for row in conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        }

    if "printers_old" in tables:
        logger.warning(
            "Migracao de printers estava incompleta (printers_old encontrada) — retomando..."
        )
        _finish_printer_migration()
        return

    with engine.connect() as conn:
        cols = {row[1] for row in conn.execute(text("PRAGMA table_info(printers)"))}

    if not cols or "server" in cols:
        return  # tabela nao existe ainda (create_all cuida) ou ja migrada

    logger.warning("Migrando schema de printers (Etapa 4: ip UNIQUE -> server+name)...")

    backup_path = _sqlite_backup_path()
    if backup_path and backup_path.exists():
        stamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        backup = backup_path.with_name(f"{backup_path.stem}.backup-{stamp}{backup_path.suffix}")
        shutil.copyfile(backup_path, backup)
        logger.warning("Backup do banco criado em: %s", backup)

    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE printers RENAME TO printers_old"))
        # SQLite mantem indices com o MESMO nome apos o RENAME (nomes de
        # indice sao globais no banco, nao por tabela) — sem isto,
        # "CREATE INDEX ix_printers_ip" na tabela nova colide com o indice
        # antigo (agora preso a printers_old) e a criacao falha.
        old_indexes = [
            row[1]
            for row in conn.execute(text("PRAGMA index_list('printers_old')"))
            if not row[1].startswith("sqlite_autoindex")
        ]
        for index_name in old_indexes:
            conn.execute(text(f"DROP INDEX IF EXISTS {index_name}"))
        conn.commit()

    _finish_printer_migration()


def _finish_printer_migration():
    """
    Recria `printers` (schema atual) e copia `printers_old` para dentro
    dela, numa unica transacao atomica; so entao apaga `printers_old`.

    Idempotente: se `printers` ja tiver dados de uma tentativa anterior
    interrompida, o DELETE no inicio da transacao limpa antes de recopiar —
    `printers_old` continua sendo a fonte de verdade ate ser apagada no
    mesmo commit que confirma a copia.
    """
    from sqlalchemy import text

    from app.models.printer import Printer

    with engine.connect() as conn:
        # Retomando de uma interrupcao anterior: garante que nenhum indice
        # antigo (preso a printers_old, mesmo nome do indice novo) sobrou.
        old_indexes = [
            row[1]
            for row in conn.execute(text("PRAGMA index_list('printers_old')"))
            if not row[1].startswith("sqlite_autoindex")
        ]
        for index_name in old_indexes:
            conn.execute(text(f"DROP INDEX IF EXISTS {index_name}"))
        conn.commit()

        cols = {row[1] for row in conn.execute(text("PRAGMA table_info(printers)"))}
    if not cols:
        Printer.__table__.create(bind=engine)

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM printers"))
        conn.execute(
            text(
                """
                INSERT INTO printers
                    (id, server, name, ip, port_name, driver_name, model,
                     printer_type, department, active, last_seen_at,
                     created_at, updated_at)
                SELECT
                    id, :server, name, ip, '', '', model,
                    NULL, department, 1, NULL,
                    created_at, updated_at
                FROM printers_old
                """
            ),
            {"server": settings.print_server_host},
        )
        conn.execute(text("DROP TABLE printers_old"))

    logger.warning("Migracao de printers concluida.")


def get_session():
    with Session(engine) as session:
        yield session
