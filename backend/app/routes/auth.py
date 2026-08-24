from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.dependencies import require_user
from app.models.user import User
from app.schemas.user import (
    PasswordChange,
    ProfileUpdate,
    TokenResponse,
    UserLogin,
    UserResponse,
)
from app.services.auth import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == credentials.email)).first()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
        )

    if not user.is_active:
        # Mesma mensagem do 403 de require_user: a conta existe e a senha
        # esta certa, mas o acesso foi revogado por um administrador.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta desativada. Procure um administrador.",
        )

    access_token = create_access_token(data={"sub": user.email})
    return TokenResponse(access_token=access_token, user=UserResponse.model_validate(user))


@router.get("/me", response_model=UserResponse)
def read_current_user(user: User = Depends(require_user)):
    """Conta autenticada e seu papel — usado para decidir o que exibir/permitir."""
    return UserResponse.model_validate(user)


@router.patch("/me", response_model=UserResponse)
def update_current_user(
    update: ProfileUpdate,
    session: Session = Depends(get_session),
    user: User = Depends(require_user),
):
    """
    Perfil da PROPRIA conta (Fase 8). So o nome.

    Nao recebe id: o alvo e sempre a sessao, entao nao existe parametro capaz
    de editar o perfil alheio — mesmo principio de /api/notifications. Alterar
    outra conta continua sendo `PATCH /api/users/{id}`, que exige admin.
    """
    user.name = update.name
    session.add(user)
    session.commit()
    session.refresh(user)
    return UserResponse.model_validate(user)


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_own_password(
    data: PasswordChange,
    session: Session = Depends(get_session),
    user: User = Depends(require_user),
):
    """
    Troca da propria senha, exigindo a atual.

    LIMITACAO CONHECIDA: o JWT e stateless e nao guarda versao de senha,
    entao tokens emitidos antes desta troca continuam validos ate expirarem.
    Invalidar sessoes antigas exigiria um campo de versao no usuario e uma
    checagem em require_user — fora do escopo desta fase, registrado aqui
    para nao virar surpresa.
    """
    if not verify_password(data.current_password, user.password_hash):
        # 400, e nem 401 nem 403. A sessao e valida e tem permissao; o que
        # esta errado e o dado enviado. Um 401 faria o painel deslogar quem
        # so errou de digitacao, e um 403 apareceria como "sem permissao"
        # no relator de erros compartilhado (lib/apiErrors.ts) — as duas
        # mensagens mentiriam sobre o que aconteceu.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta.",
        )

    if verify_password(data.new_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A nova senha precisa ser diferente da atual.",
        )

    user.password_hash = hash_password(data.new_password)
    session.add(user)
    session.commit()
