import re
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import Role

#: 3 a 32 caracteres, minusculas: letras, numeros, ponto, hifen ou underscore.
#: Sem `@` de proposito — e o que o login usa para decidir se o texto digitado
#: e um e-mail ou um username (ver `routes/auth.py`), entao os dois formatos
#: nao podem se confundir.
_USERNAME_RE = re.compile(r"^[a-z0-9._-]{3,32}$")


def normalizar_username(value: str) -> str:
    """
    Normaliza e valida um username: minusculas, formato `_USERNAME_RE`.

    Usada nos dois lados que gravam a coluna (`UserCreate`, `UserUpdate`) —
    nunca no login, que so PRECISA normalizar para comparar (o valor gravado
    ja esta no formato canonico).
    """
    cleaned = value.strip().lower()
    if not _USERNAME_RE.fullmatch(cleaned):
        raise ValueError(
            "Nome de usuario deve ter 3 a 32 caracteres: letras minusculas, "
            "numeros, ponto (.), hifen (-) ou underscore (_)."
        )
    return cleaned


class UserCreate(BaseModel):
    email: EmailStr
    # Segunda porta de login, opcional. Ver User.username (models/user.py)
    # para o porque de ser opcional e nao afetar o `sub` do JWT.
    username: str | None = None
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

    @field_validator("username")
    @classmethod
    def _username_valido(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return normalizar_username(value)


class ProfileUpdate(BaseModel):
    """
    O que o DONO da conta pode alterar em si mesmo (Fase 8).

    So `name`. Nao e timidez:
      - `email` e o `sub` do JWT — troca-lo invalidaria a propria sessao em
        silencio (mesma razao da Fase 3, que ja o proibiu no UserUpdate);
      - `username` e uma segunda porta de entrada, mas ainda e identificador
        de login unico — trocar a propria conta e a mesma decisao
        administrativa que trocar o e-mail, entao fica em `PATCH
        /api/users/{id}` (admin), nao aqui;
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

    Tambem e o unico caminho que desliga `must_change_password`: uma troca
    feita pelo proprio dono, com a senha atual conferida, e a prova de que a
    conta deixou de estar em posse de quem a criou/resetou.
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

    `username` PODE ser alterado aqui: ao contrario do e-mail, ele nao e o
    `sub` do JWT — trocar o username de alguem nao derruba a sessao dessa
    pessoa.

    Todos opcionais: um PATCH pode mexer em um campo so.
    """

    name: str | None = Field(default=None, min_length=1)
    username: str | None = None
    role: Role | None = None
    is_active: bool | None = None
    # Redefinicao de senha pelo admin. Sem recuperacao por e-mail (fora do
    # escopo), este e o unico caminho de recuperacao do sistema. Marca
    # `must_change_password` (ver routes/users.py): quem definiu esta senha
    # foi o admin, nao o dono da conta.
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

    @field_validator("username")
    @classmethod
    def _username_valido(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return normalizar_username(value)


class UserLogin(BaseModel):
    """
    Credenciais de login.

    `email` aceita e-mail OU username — o nome do campo foi mantido (em vez
    de "identifier") para nao quebrar nenhum cliente que ja envia esta forma.
    Deixou de ser `EmailStr` de proposito: essa validacao rejeitava
    "pedro.ribeiro" com 422 antes mesmo da rota decidir o que fazer com ele.
    A distincao entre e-mail e username e feita em `routes/auth.py`, pela
    presenca de "@".
    """

    email: str = Field(min_length=1)
    password: str


class UserResponse(BaseModel):
    """Usuario exposto pela API. `password_hash` nunca aparece aqui."""

    id: int
    email: str
    username: str | None
    name: str
    role: str
    is_active: bool
    # Sinaliza ao frontend que a conta precisa trocar a senha antes de
    # liberar qualquer outra tela. Vem tambem no login (dentro de
    # `TokenResponse.user`), que e onde o painel realmente decide se mostra a
    # tela de troca — ver AuthGate.tsx.
    must_change_password: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    # Dados do usuario logado, para o frontend nao precisar de outra chamada.
    user: UserResponse | None = None
