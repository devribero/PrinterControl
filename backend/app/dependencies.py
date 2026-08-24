"""
Dependencias compartilhadas pelas rotas.

Autorizacao (Fase 1) fica CENTRALIZADA aqui — nenhuma rota deve comparar
`user.role` por conta propria:

    require_user         -> qualquer conta autenticada e ativa
    require_active_user  -> require_user + sem troca de senha pendente
    require_viewer       -> leitura autenticada (hoje == require_active_user)
    require_operator     -> operacao do dia a dia (operator ou admin)
    require_admin        -> operacao administrativa/perigosa
    require_roles(...)   -> fabrica generica, para casos novos

Fase 2: as rotas GET de printers e alerts deixaram de ser publicas. O painel
Next.js so busca dados depois de confirmar a sessao em GET /api/auth/me, entao
sempre ha token para enviar. A exigencia esta declarada no proprio APIRouter
(printers e alerts), para que nenhuma rota nova nasca publica por esquecimento.

Continuam publicas apenas: POST /api/auth/login, GET / e GET /health.

Troca de senha obrigatoria: `require_active_user` bloqueia com 403 toda conta
com `must_change_password=True`. As DUAS excecoes (GET /api/auth/me e POST
/api/auth/change-password) usam `require_user` direto, nao esta fabrica —
sao a unica saida de uma conta trancada.
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


#: Mensagem devolvida pelo 403 de must_change_password. String fixa (nao um
#: HTTPException global) para que routes/auth.py possa comparar `detail` e
#: decidir, no login, se deve orientar o cliente a trocar a senha — ver
#: docstring de require_active_user.
MUST_CHANGE_PASSWORD_DETAIL = (
    "Troca de senha obrigatoria antes de continuar. "
    "Use POST /api/auth/change-password."
)


def require_active_user(user: User = Depends(require_user)) -> User:
    """
    `require_user` + bloqueio de conta com troca de senha pendente.

    Toda rota do sistema passa por aqui, EXCETO as duas que uma conta
    trancada ainda precisa alcançar para se destrancar sozinha:
    `GET /api/auth/me` (o frontend usa para saber que a troca esta
    pendente) e `POST /api/auth/change-password` (a propria troca). As duas
    continuam usando `require_user` direto em routes/auth.py.

    403 e nao 401: a sessao e valida e a senha esta certa (json a passou por
    /login) — o que falta e uma acao da propria pessoa, nao uma nova
    autenticacao. Um 401 faria o frontend deslogar quem so precisa trocar a
    senha.
    """
    if user.must_change_password:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=MUST_CHANGE_PASSWORD_DETAIL,
        )
    return user


def require_roles(*roles: str) -> Callable[..., User]:
    """
    Fabrica de dependencia: exige que o usuario tenha (ou herde) um dos
    papeis informados. admin herda operator e viewer — ver ROLE_IMPLIES.

    Base e `require_active_user`, nao `require_user`: nenhuma rota criada com
    esta fabrica deve ficar acessivel enquanto a troca de senha obrigatoria
    estiver pendente.
    """
    allowed = tuple(roles)

    def dependency(user: User = Depends(require_active_user)) -> User:
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
