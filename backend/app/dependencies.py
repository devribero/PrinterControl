"""
Dependencias compartilhadas pelas rotas.

Autenticacao: `require_user` protege as operacoes que ALTERAM dados. As rotas
de leitura seguem abertas — o painel as consome antes de qualquer sessao e
travar isso agora quebraria a tela sem ganho real no ambiente local.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from app.database import get_session
from app.models.user import User
from app.services.auth import decode_token

bearer_scheme = HTTPBearer(auto_error=False)


def require_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: Session = Depends(get_session),
) -> User:
    """Usuario dono do JWT do header Authorization. 401 se ausente/invalido."""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Nao autenticado. Faca login para executar esta operacao.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None or not credentials.credentials:
        raise unauthorized

    payload = decode_token(credentials.credentials)
    if not payload:
        raise unauthorized

    user = session.exec(select(User).where(User.email == payload["email"])).first()
    if not user:
        raise unauthorized

    return user
