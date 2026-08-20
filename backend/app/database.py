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


def create_db_and_tables():
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
