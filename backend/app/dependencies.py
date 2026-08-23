"""
Dependencias compartilhadas pelas rotas.

Autorizacao (Fase 1) fica CENTRALIZADA aqui — nenhuma rota deve comparar
`user.role` por conta propria:

    require_user      -> qualquer conta autenticada e ativa
    require_viewer    -> leitura autenticada (hoje == require_user)
    require_operator  -> operacao do dia a dia (operator ou admin)
    require_admin     -> operacao administrativa/perigosa
    require_roles(...) -> fabrica generica, para casos novos

Fase 2: as rotas GET de printers e alerts deixaram de ser publicas. O painel
Next.js so busca dados depois de confirmar a sessao em GET /api/auth/me, entao
sempre ha token para enviar. A exigencia esta declarada no proprio APIRouter
(printers e alerts), para que nenhuma rota nova nasca publica por esquecimento.

Continuam publicas apenas: POST /api/auth/login, GET / e GET /health.
"""
from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from app.database import get_session
from app.models.user import Role, User
from app.services.auth import decode_token

bearer_scheme = HTTPBearer(auto_error=False)


def require_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: Session = Depends(get_session),
) -> User:
    """
    Usuario dono do JWT do header Authorization. 401 se ausente/invalido.

    O usuario e SEMPRE relido do banco a cada requisicao (o JWT carrega
    apenas o e-mail). E isso que faz uma conta desativada perder o acesso
    imediatamente, sem precisar de revogacao/blacklist de token: o token
    continua criptograficamente valido, mas a conta por tras dele nao passa
    mais na checagem de `is_active`.
    """
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

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta desativada. Procure um administrador.",
        )

    return user


def require_roles(*roles: str) -> Callable[..., User]:
    """
    Fabrica de dependencia: exige que o usuario tenha (ou herde) um dos
    papeis informados. admin herda operator e viewer — ver ROLE_IMPLIES.
    """
    allowed = tuple(roles)

    def dependency(user: User = Depends(require_user)) -> User:
        if not user.has_role(*allowed):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Permissao insuficiente para esta operacao. "
                    f"Exigido: {' ou '.join(allowed)}."
                ),
            )
        return user

    return dependency


#: Leitura autenticada. Hoje equivale a require_user (todo papel le), mas
#: existe como nome proprio para que fechar as rotas GET no futuro seja uma
#: troca de dependencia e nao uma decisao espalhada.
require_viewer = require_roles(Role.VIEWER.value)

#: Operacoes do dia a dia: coleta real, resolver/notificar alertas, leituras.
require_operator = require_roles(Role.OPERATOR.value)

#: Operacoes administrativas/perigosas: usuarios, cadastro de impressoras,
#: discovery/sync do Print Server, coleta simulada, estado do agendador.
require_admin = require_roles(Role.ADMIN.value)
