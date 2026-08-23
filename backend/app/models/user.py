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
    password_hash: str
    name: str
    # Default conservador: uma conta criada sem papel explicito so le.
    # Contas que ja existiam antes desta fase sao migradas para "admin"
    # (ver _migrate_user_rbac em app/database.py), preservando o
    # comportamento anterior, em que todo autenticado podia tudo.
    role: str = Field(default=Role.VIEWER.value, index=True)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def has_role(self, *required: str) -> bool:
        """True se o papel do usuario satisfaz qualquer um dos exigidos."""
        granted = ROLE_IMPLIES.get(self.role, set())
        return any(r in granted for r in required)
