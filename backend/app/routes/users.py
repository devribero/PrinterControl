"""
Gestao administrativa de contas (Fase 3).

Todas as rotas exigem `require_admin` — declarado no proprio APIRouter, para
que nenhuma rota nova nasca sem protecao. A autorizacao continua vindo das
dependencias centralizadas da Fase 1; nada de comparar `user.role` aqui.

Nao existe DELETE de proposito: desativar (`is_active=False`) e a exclusao
deste sistema. Apagar a linha quebraria o historico (alertas e leituras nao
apontam para usuarios hoje, mas `created_at`/autoria futura sim) e, pior,
liberaria o e-mail para um cadastro novo herdar a identidade do antigo.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, func, select

from app.database import get_session
from app.dependencies import require_admin
from app.models.user import Role, User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.auth import hash_password

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(require_admin)],
)


def _active_admin_count(session: Session) -> int:
    return session.exec(
        select(func.count())
        .select_from(User)
        .where(User.role == Role.ADMIN.value, User.is_active == True)  # noqa: E712
    ).one()


def _ensure_not_last_admin(session: Session, target: User, update: UserUpdate) -> None:
    """
    Impede que a ultima conta admin ativa perca o proprio acesso administrativo.

    Sem isso, um unico PATCH ("me rebaixa para viewer" ou "me desativa") deixa
    o sistema sem ninguem capaz de gerenciar usuarios — e, como nao ha
    recuperacao por e-mail nem CLI de administracao, a saida seria editar o
    SQLite na mao.

    Com dois ou mais admins ativos a operacao e permitida: um admin PODE se
    rebaixar ou se desativar, porque outro consegue desfazer.
    """
    perde_admin = update.role is not None and update.role != Role.ADMIN
    sera_desativado = update.is_active is False
    if not (perde_admin or sera_desativado):
        return

    era_admin_ativo = target.role == Role.ADMIN.value and target.is_active
    if not era_admin_ativo:
        return

    if _active_admin_count(session) <= 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Esta e a ultima conta de administrador ativa. Promova ou ative "
                "outro administrador antes de rebaixar ou desativar esta."
            ),
        )


@router.get("", response_model=list[UserResponse])
def list_users(session: Session = Depends(get_session)):
    """Todas as contas, mais recentes por ultimo (ordem estavel de cadastro)."""
    return session.exec(select(User).order_by(User.id)).all()


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, session: Session = Depends(get_session)):
    """
    Cria uma conta. Substitui o antigo `POST /api/auth/register` (Fase 1), que
    ja era administrativo — o caminho mudou para o recurso a que pertence, sem
    duas formas de criar usuario convivendo.

    A senha vem em texto claro e e gravada apenas como hash Argon2, pelo mesmo
    `hash_password()` usado no login. Sem papel explicito a conta nasce viewer.

    Nasce com `must_change_password=True`: quem definiu esta senha foi o
    admin que preencheu o formulario, nao a pessoa dona da conta.
    """
    existing = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ja existe uma conta com o e-mail {user_data.email}.",
        )

    if user_data.username is not None:
        existing_username = session.exec(
            select(User).where(User.username == user_data.username)
        ).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ja existe uma conta com o nome de usuario {user_data.username}.",
            )

    user = User(
        email=user_data.email,
        username=user_data.username,
        password_hash=hash_password(user_data.password),
        name=user_data.name,
        role=Role(user_data.role).value,
        must_change_password=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    update: UserUpdate,
    session: Session = Depends(get_session),
    _admin: User = Depends(require_admin),
):
    """
    Altera nome, username, papel, ativacao e/ou senha de uma conta.

    Desativar aqui basta para cortar o acesso: `require_user` rele o usuario a
    cada requisicao, entao o JWT que a pessoa ja tem passa a receber 403 na
    hora (Fase 1) — sem lista de revogacao.

    Redefinir a senha aqui liga `must_change_password`: quem digitou a nova
    senha foi o admin, nao o dono da conta, entao a proxima entrada exige a
    troca — mesma regra de `create_user`.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")

    _ensure_not_last_admin(session, user, update)

    data = update.model_dump(exclude_unset=True)

    if "username" in data:
        username = data["username"]
        if username is not None:
            existing_username = session.exec(
                select(User).where(User.username == username, User.id != user_id)
            ).first()
            if existing_username:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Ja existe uma conta com o nome de usuario {username}.",
                )

    if "password" in data:
        password = data.pop("password")
        if password is not None:
            user.password_hash = hash_password(password)
            user.must_change_password = True

    if data.get("role") is not None:
        user.role = Role(data.pop("role")).value
    else:
        data.pop("role", None)

    for field, value in data.items():
        if value is not None:
            setattr(user, field, value)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user
