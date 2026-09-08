from enum import Enum

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Role(str, Enum):
    """
    RBAC minimo (Fase 1). Tres papeis cobrem todas as rotas existentes hoje:

    - admin    : operacoes administrativas/perigosas (cadastro de usuarios e
                 impressoras, discovery/sync do Print Server, coleta simulada,
                 estado do agendador).
    - operator : operacoes do dia a dia (coleta real, resolver/notificar
                 alertas, registrar leituras).
    - viewer   : somente leitura.

    Guardado como string na coluna `users.role` — acrescentar um papel novo no
    futuro nao exige migracao de schema.
    """

    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


#: Papeis que herdam as permissoes de um papel (admin faz tudo que operator faz).
ROLE_IMPLIES: dict[str, set[str]] = {
    Role.ADMIN.value: {Role.ADMIN.value, Role.OPERATOR.value, Role.VIEWER.value},
    Role.OPERATOR.value: {Role.OPERATOR.value, Role.VIEWER.value},
    Role.VIEWER.value: {Role.VIEWER.value},
}


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)

    # Segundo identificador de login, OPCIONAL e unico. Existe para que
    # "pedro.ribeiro" e "pedro.ribeiro@elgin.com.br" levem a mesma conta.
    #
    # O que ele NAO e: identidade. O `sub` do JWT continua sendo o e-mail
    # (ver services/auth.py), e require_user continua relendo a conta por
    # e-mail. O username e apenas uma segunda PORTA de entrada — por isso
    # troca-lo nao derruba a sessao de ninguem, ao contrario do e-mail.
    #
    # Nulo e permitido de proposito: contas antigas seguem sem username, e o
    # SQLite aceita varios NULL num indice UNIQUE (a restricao so vale entre
    # valores preenchidos). Gravado sempre normalizado em minusculas — ver
    # `normalizar_username` em schemas/user.py, o unico lugar que valida o
    # formato.
    username: str | None = Field(default=None, unique=True, index=True)

    password_hash: str
    name: str
    # Default conservador: uma conta criada sem papel explicito so le.
    # Contas que ja existiam antes desta fase sao migradas para "admin"
    # (ver _migrate_user_rbac em app/database.py), preservando o
    # comportamento anterior, em que todo autenticado podia tudo.
    role: str = Field(default=Role.VIEWER.value, index=True)
    is_active: bool = Field(default=True)

    # Senha pendente de troca. Ligado quando a conta e criada por um admin e
    # quando a senha e redefinida por alguem que nao seja o dono (PATCH
    # /api/users/{id} e `seed.py --resetar-senhas`) — os dois casos em que a
    # senha atual passou pelas maos de outra pessoa.
    #
    # Enquanto vale True, require_user recusa TUDO menos ver a propria conta
    # e trocar a senha (403). Nao e cosmetico da interface: um cliente que
    # ignore a sinalizacao do login continua barrado no backend.
    #
    # Desligado em um unico ponto: POST /api/auth/change-password, depois da
    # troca confirmada.
    must_change_password: bool = Field(default=False)

    # Versao da credencial (QA-04). O JWT carrega este numero em `ver`;
    # require_user recusa qualquer token cujo `ver` nao seja o valor atual
    # da conta. Incrementar o campo invalida DE UMA VEZ todas as sessoes
    # abertas daquela conta.
    #
    # Existe porque o JWT e stateless: ate aqui trocar a senha nao derrubava
    # sessao nenhuma (o token antigo valia ate expirar), e desativar/reativar
    # a conta tambem nao — o 403 de `is_active` sumia assim que a conta
    # voltava, e o token antigo voltava a funcionar junto. A tela de
    # Configuracoes chegava a orientar "desative e reative para encerrar
    # sessoes suspeitas", conselho que nao fazia o que prometia.
    #
    # Incrementado em exatamente tres pontos, todos "esta credencial mudou
    # de maos": troca da propria senha, redefinicao de senha por um admin e
    # desativacao da conta. Reativar NAO incrementa (a desativacao ja
    # queimou as sessoes; incrementar de novo so gastaria um numero).
    #
    # Contas migradas comecam em 0, igual a uma conta nova. Tokens emitidos
    # antes desta mudanca nao carregam `ver` e sao recusados — ver
    # decode_token, que trata ausencia como incompativel de proposito.
    token_version: int = Field(default=0)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    def has_role(self, *required: str) -> bool:
        """True se o papel do usuario satisfaz qualquer um dos exigidos."""
        granted = ROLE_IMPLIES.get(self.role, set())
        return any(r in granted for r in required)
