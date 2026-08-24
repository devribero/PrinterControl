from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import Role


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str = Field(min_length=1)
    # Sem papel explicito a conta nasce somente-leitura.
    role: Role = Role.VIEWER

    @field_validator("name")
    @classmethod
    def _name_not_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Nome nao pode ser vazio.")
        return cleaned


class ProfileUpdate(BaseModel):
    """
    O que o DONO da conta pode alterar em si mesmo (Fase 8).

    So `name`. Nao e timidez:
      - `email` e o `sub` do JWT — troca-lo invalidaria a propria sessao em
        silencio (mesma razao da Fase 3, que ja o proibiu no UserUpdate);
      - `role` e `is_active` sao decisao administrativa. Se o dono pudesse
        mexer neles, qualquer conta viraria admin e o /users existiria por
        decoracao;
      - `password` tem rota propria, porque exige a senha atual.
    """

    name: str = Field(min_length=1)

    @field_validator("name")
    @classmethod
    def _name_not_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Nome nao pode ser vazio.")
        return cleaned


class PasswordChange(BaseModel):
    """
    Troca da propria senha (Fase 8).

    `current_password` NAO e burocracia: sem ela, um token roubado viraria
    posse permanente da conta — bastaria trocar a senha e o dono perderia o
    acesso. Exigir a senha atual mantem o roubo limitado a validade do token.

    Ate aqui o unico caminho era um admin redefinir a senha por
    `PATCH /api/users/{id}`, o que obrigava a pessoa a contar a senha nova
    para outra. Esta rota fecha isso.
    """

    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=8)


class UserUpdate(BaseModel):
    """
    Campos que um admin pode alterar em outra conta (Fase 3).

    Deliberadamente NAO inclui `id`, `email` nem `password_hash`:
      - `id` e identidade da linha;
      - `email` e a chave usada pelo JWT (`sub`) — troca-lo invalidaria em
        silencio a sessao do dono da conta;
      - `password_hash` nunca entra pela API; so `password` (texto claro),
        que e passado pelo mesmo hash_password() do resto do projeto.

    Todos opcionais: um PATCH pode mexer em um campo so.
    """

    name: str | None = Field(default=None, min_length=1)
    role: Role | None = None
    is_active: bool | None = None
    # Redefinicao de senha pelo admin. Sem recuperacao por e-mail (fora do
    # escopo), este e o unico caminho de recuperacao do sistema.
    password: str | None = Field(default=None, min_length=8)

    @field_validator("name")
    @classmethod
    def _name_not_blank(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Nome nao pode ser vazio.")
        return cleaned


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Usuario exposto pela API. `password_hash` nunca aparece aqui."""

    id: int
    email: str
    name: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    # Dados do usuario logado, para o frontend nao precisar de outra chamada.
    user: UserResponse | None = None
