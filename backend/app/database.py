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

            # foreign_keys FICA DESLIGADO (o padrao do SQLite). NAO e
            # esquecimento — ligar quebra a aplicacao HOJE.
            #
            # `printer_readings` e `alerts` carregam FK para "printers_old",
            # tabela que a migracao de schema das etapas anteriores renomeou e
            # descartou. Com a checagem desligada isso e inofensivo; ligada,
            # todo INSERT de leitura falha com
            #     no such table: main.printers_old
            # e a coleta inteira para. Verificavel com PRAGMA foreign_key_check.
            #
            # Consertar exige reconstruir as duas tabelas com a FK correta —
            # migracao de banco, com backup e janela, decidida a parte. Ate la,
            # a integridade referencial continua garantida pelo codigo (nada
            # apaga impressora: o que some vira active=False), que e como
            # sempre funcionou.
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
    _migrate_reading_uptime()
    _migrate_user_rbac()
    _migrate_print_servers()


def _migrate_alert_type():
    """Adiciona alerts.alert_type em bancos criados antes da Etapa 8A."""
    from sqlalchemy import text

    with engine.connect() as conn:
        cols = {row[1] for row in conn.execute(text("PRAGMA table_info(alerts)"))}
        if cols and "alert_type" not in cols:
            conn.execute(text("ALTER TABLE alerts ADD COLUMN alert_type VARCHAR"))
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
