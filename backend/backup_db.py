"""
Backup do SQLite (Fase 10).

    .\\venv\\Scripts\\python.exe backup_db.py
    .\\venv\\Scripts\\python.exe backup_db.py --dir D:\\backups --keep 30

POR QUE NAO E UM `copy` DO ARQUIVO
-----------------------------------
Copiar printer_control.db com o backend no ar produz, com frequencia, um
arquivo corrompido ou incoerente: a copia pega paginas de meio de uma
transacao, e em modo WAL ela nem sequer inclui o conteudo que ainda esta no
arquivo -wal. O backup so seria confiavel com o servico parado — ou seja,
exigindo janela de indisponibilidade para algo que deveria rodar de hora em
hora.

Este script usa a API de backup ONLINE do SQLite (sqlite3.Connection.backup),
que copia pagina a pagina coordenando com quem estiver escrevendo. O
resultado e um banco consistente, tirado com o sistema rodando.

O arquivo gerado ja vem com `PRAGMA integrity_check` executado sobre ele: um
backup que ninguem verifica e uma suposicao, nao uma garantia — e o momento
de descobrir que ele nao presta nao pode ser o dia da restauracao.

RESTAURACAO
-----------
    1. pare o servico   (scripts\\Servico-PrinterControl.ps1 -Acao parar)
    2. copie o backup por cima de backend\\printer_control.db
       (apague tambem os arquivos -wal e -shm, se existirem)
    3. suba o servico   (scripts\\Servico-PrinterControl.ps1 -Acao iniciar)
"""
import argparse
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
DEFAULT_DIR = BACKEND_DIR / "backups"
PREFIXO = "printer_control-"


def _caminho_do_banco() -> Path:
    """
    Le DATABASE_URL pela configuracao da aplicacao, para o backup nunca sair
    de um banco diferente do que o backend usa — o erro classico e alguem
    mudar DATABASE_URL e continuar salvando o arquivo antigo por meses.
    """
    sys.path.insert(0, str(BACKEND_DIR))
    from app.config import settings  # noqa: PLC0415

    url = settings.database_url
    prefixo = "sqlite:///"
    if not url.startswith(prefixo):
        raise SystemExit(
            f"backup_db.py so suporta SQLite; DATABASE_URL atual: {url.split('://')[0]}://..."
        )
    return Path(url[len(prefixo) :])


def _progresso(status, restantes, total):
    if total:
        print(f"  copiando... {total - restantes}/{total} paginas", end="\r")


def fazer_backup(origem: Path, destino_dir: Path) -> Path:
    if not origem.exists():
        raise SystemExit(f"Banco nao encontrado: {origem}")

    destino_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    destino = destino_dir / f"{PREFIXO}{stamp}.db"

    print(f"Origem : {origem}")
    print(f"Destino: {destino}")

    # Somente leitura na origem: o backup jamais deve ser capaz de alterar o
    # banco de producao, nem por acidente de digitacao neste arquivo.
    src = sqlite3.connect(f"file:{origem}?mode=ro", uri=True)
    dst = sqlite3.connect(destino)
    try:
        src.backup(dst, pages=200, progress=_progresso)

        # O backup herda o journal_mode da origem, que e WAL. Sem colapsar
        # aqui, o backup fica sendo TRES arquivos (.db, -wal, -shm) e parte
        # dos dados vive no -wal. Quem restaurasse copiando so o .db — que e
        # exatamente o que a documentacao de restauracao pede — perderia o
        # que estivesse no -wal, silenciosamente.
        #
        # TRUNCATE esvazia o WAL aplicando tudo no .db; DELETE tira o banco
        # do modo WAL, e ai o arquivo unico basta.
        dst.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        dst.execute("PRAGMA journal_mode=DELETE")
    finally:
        dst.close()
        src.close()
    print()

    # Cinto e suspensorio: se por qualquer razao um -wal/-shm sobrar ao lado
    # do backup, ele so pode confundir uma restauracao futura.
    for sufixo in ("-wal", "-shm"):
        residuo = destino.with_name(destino.name + sufixo)
        if residuo.exists():
            residuo.unlink()

    verificar(destino)
    return destino


def verificar(caminho: Path) -> None:
    """integrity_check no ARQUIVO GERADO — ver docstring do modulo."""
    conn = sqlite3.connect(f"file:{caminho}?mode=ro", uri=True)
    try:
        resultado = conn.execute("PRAGMA integrity_check").fetchone()[0]
    finally:
        conn.close()

    if resultado != "ok":
        # Nao apaga o arquivo suspeito: ele e a evidencia de que algo esta
        # errado no banco de origem, e vai ser preciso olha-lo.
        raise SystemExit(f"FALHA: integrity_check do backup retornou {resultado!r} ({caminho})")

    tamanho = caminho.stat().st_size / (1024 * 1024)
    print(f"  integridade: ok ({tamanho:.1f} MB)")


def aplicar_retencao(destino_dir: Path, manter: int) -> None:
    """
    Mantem os N backups mais recentes. Ordena por NOME, nao por mtime: o nome
    carrega o timestamp da criacao, enquanto o mtime muda se alguem copiar os
    arquivos de lugar — e ai a retencao apagaria o backup errado.
    """
    if manter <= 0:
        return

    existentes = sorted(destino_dir.glob(f"{PREFIXO}*.db"))
    excedentes = existentes[:-manter] if len(existentes) > manter else []

    for antigo in excedentes:
        antigo.unlink()
        # Remove tambem eventuais companheiros de backups antigos, gerados
        # antes de o checkpoint acima existir.
        for sufixo in ("-wal", "-shm"):
            residuo = antigo.with_name(antigo.name + sufixo)
            if residuo.exists():
                residuo.unlink()
        print(f"  removido (retencao): {antigo.name}")

    print(f"  retencao: {min(len(existentes), manter)} de {manter} mantidos")


def main() -> int:
    parser = argparse.ArgumentParser(description="Backup online do SQLite do PrinterControl.")
    parser.add_argument("--dir", type=Path, default=DEFAULT_DIR, help="Pasta de destino.")
    parser.add_argument("--keep", type=int, default=14, help="Quantos backups manter (0 = todos).")
    args = parser.parse_args()

    inicio = datetime.now()
    print(f"[{inicio:%Y-%m-%d %H:%M:%S}] Backup do PrinterControl")

    destino = fazer_backup(_caminho_do_banco(), args.dir)
    aplicar_retencao(args.dir, args.keep)

    print(f"OK: {destino.name} ({(datetime.now() - inicio).total_seconds():.1f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
