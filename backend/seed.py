"""
Semeia o banco: contas iniciais + a frota de printers_data.json.

SENHAS (Fase 10)
----------------
Ate aqui as duas contas de administrador nasciam com a senha "123" — tres
caracteres, abaixo do minimo de 8 que a propria API exige de qualquer conta
criada por `POST /api/users`. Era a contradicao mais perigosa do sistema: as
UNICAS contas capazes de criar usuarios, mudar papeis e sincronizar Print
Servers eram tambem as unicas que podiam ter uma senha que a API recusaria.

Agora ha dois caminhos, nesta ordem:

    1. SEED_ADMIN_PASSWORD no ambiente -> usada como esta (validada: >= 8).
    2. nada definido -> uma senha aleatoria forte e gerada e IMPRESSA UMA
       UNICA VEZ no console. Ela nao e gravada em lugar nenhum em texto
       claro; se a janela for fechada sem anotar, o caminho e rodar
       `python seed.py --resetar-senhas` e gerar outra.

TROCA DE SENHA OBRIGATORIA (2026-08-24)
----------------------------------------
Toda conta criada ou resetada por este script nasce com
`must_change_password=True`: quem definiu a senha foi quem rodou o seed, nao
a pessoa dona da conta. O backend recusa qualquer rota alem de
`GET /api/auth/me` e `POST /api/auth/change-password` ate a troca (ver
app/dependencies.py, require_active_user).

LOGIN POR USERNAME (2026-08-24)
--------------------------------
Cada conta semeada agora tambem tem um `username` (derivado do e-mail: a
parte antes do "@"), para poder entrar como "pedro.ribeiro" alem de
"pedro.ribeiro@elgin.com.br". O `sub` do JWT continua sendo o e-mail —
username e so uma segunda porta de entrada (ver app/models/user.py).

IDEMPOTENCIA E O SEU LIMITE
---------------------------
Semear de novo NAO altera conta que ja existe — o comportamento de sempre, e
o correto: um seed nao pode sobrescrever a senha que alguem ja trocou. A
consequencia e que um banco criado antes desta mudanca CONTINUA com a senha
antiga ate alguem agir. Para esses bancos existe a flag:

    python seed.py --resetar-senhas

que redefine a senha das contas semeadas, imprime a nova, religa
`must_change_password` e preenche o `username` de quem ainda nao tiver (conta
que ja existia antes desta mudanca).

MIGRACAO DE DOMINIO (2026-08-24, uso unico)
--------------------------------------------
As contas deste projeto nasceram com e-mail `@example.com`. A flag

    python seed.py --migrar-dominio

renomeia TODAS as contas do banco (nao so as semeadas) de `@example.com` para
`@elgin.com.br`, preservando a parte antes do "@". Operacao de dados, nao de
schema — por isso fica aqui e nao em `_migrate_*` de app/database.py, e por
isso e manual: trocar o e-mail de alguem troca o `sub` do JWT e invalida a
sessao aberta dessa pessoa (esperado, documentado, decisao de quem roda o
comando). Idempotente: rodar de novo nao encontra mais nada em @example.com
e nao faz nada.

    python seed.py                    # cria o que falta
    python seed.py --migrar-dominio   # + renomeia @example.com -> @elgin.com.br
    python seed.py --resetar-senhas   # + rotaciona a senha das contas semeadas
"""
import json
import os
import secrets
import sys

from sqlmodel import Session, select

from app.database import create_db_and_tables, engine
from app.models.printer import Printer
from app.models.user import Role, User
from app.services.auth import hash_password

# Mesmo minimo do schema (UserCreate.password, Field(min_length=8)). Definido
# aqui de novo, e nao importado, porque o seed roda fora do ciclo da API — mas
# se um dia divergirem, o schema e a autoridade.
MIN_SENHA = 8

#: (email, username, nome). O username e a parte antes do "@" — mesma
#: convencao que a UI ja usa para exibir a conta (ver src/lib/auth.ts).
CONTAS_SEMEADAS = [
    ("mateus.vicentino@elgin.com.br", "mateus.vicentino", "Mateus Vicentino"),
    ("pedro.ribeiro@elgin.com.br", "pedro.ribeiro", "Pedro Ribeiro"),
]

DOMINIO_ANTIGO = "@example.com"
DOMINIO_NOVO = "@elgin.com.br"


def obter_senha_admin() -> tuple[str, bool]:
    """
    Devolve (senha, foi_gerada).

    `foi_gerada` decide se a senha precisa ser MOSTRADA: quando veio do
    ambiente, quem rodou o seed ja a conhece, e imprimi-la so a espalharia
    pelo historico do terminal e pelos logs de quem capturar a saida.
    """
    do_ambiente = os.environ.get("SEED_ADMIN_PASSWORD", "").strip()

    if do_ambiente:
        if len(do_ambiente) < MIN_SENHA:
            raise SystemExit(
                f"[ERRO] SEED_ADMIN_PASSWORD tem {len(do_ambiente)} caracteres; "
                f"o minimo e {MIN_SENHA} - o mesmo que a API exige de qualquer "
                f"outra conta. Escolha uma senha maior."
            )
        return do_ambiente, False

    # token_urlsafe(18) -> 24 caracteres, ~143 bits de entropia. Longa o
    # bastante para nao ser adivinhada e curta o bastante para ser copiada a
    # mao de uma tela, que e como ela vai ser usada.
    return secrets.token_urlsafe(18), True


def mostrar_senha_uma_vez(senha: str, emails: list[str]) -> None:
    """Imprime a senha em destaque. Unica vez que ela aparece em texto claro."""
    print()
    print("=" * 70)
    print("  SENHA DAS CONTAS DE ADMINISTRADOR - ANOTE AGORA")
    print("=" * 70)
    for email in emails:
        print(f"  usuario: {email}")
    print(f"  senha:   {senha}")
    print()
    print("  Esta senha NAO sera exibida de novo e nao esta gravada em lugar")
    print("  nenhum em texto claro. Se perder, rode:")
    print("      python seed.py --resetar-senhas")
    print()
    print("  O primeiro login com esta senha exige troca imediata")
    print("  (must_change_password) antes de liberar qualquer outra tela.")
    print("=" * 70)
    print()


def migrar_dominio(session: Session) -> int:
    """
    Renomeia TODAS as contas `...@example.com` para `...@elgin.com.br`.

    Uso unico, manual (ver docstring do modulo). Idempotente: uma conta ja em
    @elgin.com.br nao aparece na consulta e nao e tocada; se o e-mail novo ja
    existir por algum outro motivo, a conta e pulada (nunca gera duas linhas
    com o mesmo e-mail) e o conflito e impresso para decisao manual.
    """
    renomeadas = 0
    candidatas = session.exec(
        select(User).where(User.email.like(f"%{DOMINIO_ANTIGO}"))
    ).all()

    for user in candidatas:
        novo_email = user.email[: -len(DOMINIO_ANTIGO)] + DOMINIO_NOVO

        colisao = session.exec(select(User).where(User.email == novo_email)).first()
        if colisao:
            print(
                f"[!] Pulado: {user.email} -> {novo_email} ja existe "
                f"(id={colisao.id}). Resolva manualmente."
            )
            continue

        print(f"[~] E-mail migrado: {user.email} -> {novo_email}")
        user.email = novo_email
        session.add(user)
        renomeadas += 1

    if renomeadas:
        session.commit()

    return renomeadas


def seed_database(resetar_senhas: bool = False, migrar_dominio_flag: bool = False):
    create_db_and_tables()

    senha, foi_gerada = obter_senha_admin()
    senha_usada = False

    with Session(engine) as session:
        if migrar_dominio_flag:
            renomeadas = migrar_dominio(session)
            if renomeadas:
                print(f"[OK] {renomeadas} conta(s) migrada(s) para {DOMINIO_NOVO}.")
                print(
                    "[!] Sessoes abertas com o e-mail antigo pararam de valer "
                    "(o e-mail e o `sub` do JWT)."
                )
            else:
                print(f"[i] Nenhuma conta em {DOMINIO_ANTIGO} encontrada.")

        # Contas de desenvolvimento: admin, porque sao as unicas do banco
        # semeado e precisam poder criar as demais (POST /api/users e
        # administrativo desde a Fase 1). Contas criadas por elas nascem
        # como "viewer".
        for email, username, nome in CONTAS_SEMEADAS:
            existente = session.exec(select(User).where(User.email == email)).first()

            if existente is None:
                session.add(
                    User(
                        email=email,
                        username=username,
                        password_hash=hash_password(senha),
                        name=nome,
                        role=Role.ADMIN.value,
                        must_change_password=True,
                    )
                )
                senha_usada = True
                print(f"[+] Usuario criado: {email} (username={username})")
            elif resetar_senhas:
                existente.password_hash = hash_password(senha)
                existente.must_change_password = True
                # Backfill: conta criada antes do login por username ainda
                # nao tem um. Nao sobrescreve um username ja definido (por
                # exemplo, trocado por um admin depois da criacao).
                if not existente.username:
                    existente.username = username
                session.add(existente)
                senha_usada = True
                print(f"[~] Senha redefinida: {email} (username={existente.username})")
            else:
                print(f"[=] Usuario ja existe, senha preservada: {email}")

        session.commit()

        # Frota inicial a partir do JSON exportado da planilha.
        with open("printers_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        printers_count = 0
        for p_data in data.get("printers", []):
            existing = session.exec(
                select(Printer).where(Printer.ip == p_data["ip"])
            ).first()

            if not existing:
                session.add(
                    Printer(
                        ip=p_data["ip"],
                        name=p_data["name"],
                        model=p_data["model"],
                        department=p_data["department"],
                    )
                )
                printers_count += 1

        session.commit()
        print(f"[+] Impressoras criadas: {printers_count}")
        print("[OK] Banco semeado")

    if senha_usada and foi_gerada:
        mostrar_senha_uma_vez(senha, [email for email, _, _ in CONTAS_SEMEADAS])
    elif senha_usada:
        print("[i] Senha definida a partir de SEED_ADMIN_PASSWORD (nao exibida).")
    elif not resetar_senhas:
        print(
            "[i] Nenhuma conta criada ou alterada. Se as contas ainda usam a "
            "senha antiga, rode: python seed.py --resetar-senhas"
        )


if __name__ == "__main__":
    seed_database(
        resetar_senhas="--resetar-senhas" in sys.argv,
        migrar_dominio_flag="--migrar-dominio" in sys.argv,
    )
