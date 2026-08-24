import logging
import secrets

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import Session, select

from app.config import settings
from app.database import get_session
from app.dependencies import require_active_user, require_user
from app.models.user import User
from app.schemas.user import (
    PasswordChange,
    ProfileUpdate,
    TokenResponse,
    UserLogin,
    UserResponse,
)
from app.services.auth import create_access_token, hash_password, verify_password
from app.services.rate_limit import RateLimiter

logger = logging.getLogger("printercontrol.auth")

router = APIRouter(prefix="/auth", tags=["auth"])

# Uma instancia por processo. Ver o docstring de services/rate_limit.py para
# o que isso implica (contagem zera no restart, nao e compartilhada entre
# workers) e por que e aceitavel neste deploy.
login_limiter = RateLimiter(
    max_tentativas=settings.login_max_attempts,
    janela_segundos=settings.login_window_seconds,
)


# ─────────────────────────────────────────────────────────────────────────
#  Oraculo de tempo
# ─────────────────────────────────────────────────────────────────────────
#
# Hash descartavel, de uma senha aleatoria que ninguem conhece, usado APENAS
# para gastar o mesmo tempo quando o e-mail nao existe.
#
# O problema que ele resolve: `verify_password` com argon2 leva dezenas de
# milissegundos; consultar um e-mail inexistente leva microssegundos. Sem
# isto, "e-mail nao cadastrado" respondia visivelmente mais rapido que
# "senha errada", e comparar os tempos revelava QUAIS e-mails tem conta —
# a lista de alvos de um ataque de senha, entregue pela propria API. As
# duas respostas ja eram identicas em texto e status; faltava o tempo.
#
# Calculado uma vez, no import: gerar por requisicao adicionaria o custo de
# um hash a todo login valido, sem ganho nenhum.
_DUMMY_PASSWORD_HASH = hash_password(secrets.token_urlsafe(32))


def _identificar_origem(request: Request) -> str:
    """
    IP de origem da requisicao, para a contagem por IP.

    `X-Forwarded-For` so e lido com TRUST_PROXY_HEADERS=true: sem um proxy
    de confianca na frente, esse cabecalho e escolhido pelo cliente, e
    confiar nele permitiria trocar de identidade a cada tentativa —
    exatamente o que o limite existe para impedir.
    """
    if settings.trust_proxy_headers:
        encaminhado = request.headers.get("x-forwarded-for", "")
        if encaminhado:
            # O primeiro da lista e o cliente original; o resto sao proxies.
            return encaminhado.split(",")[0].strip()

    return request.client.host if request.client else "desconhecido"


@router.post("/login", response_model=TokenResponse)
def login(
    credentials: UserLogin,
    request: Request,
    session: Session = Depends(get_session),
):
    """
    Autentica e devolve o JWT. Aceita e-mail OU username em `credentials.email`
    (o nome do campo ficou por compatibilidade — ver docstring de UserLogin).

    Tres protecoes alem da conferencia da senha:
      - limite de tentativas por IP e por conta (429 quando estourado);
      - tempo de resposta constante entre "conta inexistente" e "senha
        errada", para nao revelar quais contas existem;
      - a chave do limite e sempre o E-MAIL CANONICO da conta encontrada
        (nunca o texto digitado) — ver nota abaixo.
    """
    identificador = credentials.email.strip()

    # Resolve a conta ANTES do limitador, por um motivo que nao existia
    # quando so havia e-mail: com username, "pedro.ribeiro" e
    # "pedro.ribeiro@elgin.com.br" sao a MESMA conta, mas so descobrimos
    # isso apos consultar o banco. Se o limitador checasse pelo texto
    # digitado (como antes), alternar entre as duas formas reabriria a
    # mesma brecha ja corrigida para variacao de maiusculas em e-mail
    # (contagens separadas por forma == cota dobrada).
    #
    # O custo extra e um SELECT indexado (microssegundos) antes do bloqueio
    # — nao o hash argon2, que continua condicionado a ele passar. E o hash
    # que a checagem de forca bruta precisa evitar pagar, e continua evitando.
    if "@" in identificador:
        user = session.exec(select(User).where(User.email == identificador)).first()
    else:
        user = session.exec(select(User).where(User.username == identificador.lower())).first()

    # Sem conta encontrada, a chave usada e o proprio texto digitado
    # (normalizado): nao ha e-mail canonico para agrupar as tentativas, e
    # ainda assim precisa de UMA chave estavel para o limitador funcionar.
    chave_conta = user.email.strip().lower() if user else identificador.lower()
    chaves = [f"ip:{_identificar_origem(request)}", f"email:{chave_conta}"]

    limite = login_limiter.verificar(chaves)
    if limite.bloqueado:
        logger.warning(
            "Login bloqueado por excesso de tentativas | conta=%s | origem=%s | retry_after=%ss",
            chave_conta,
            _identificar_origem(request),
            limite.retry_after,
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                f"Muitas tentativas de login. Tente novamente em "
                f"{max(1, limite.retry_after // 60)} minuto(s)."
            ),
            headers={"Retry-After": str(limite.retry_after)},
        )

    if user:
        senha_confere = verify_password(credentials.password, user.password_hash)
    else:
        # Conta inexistente: verifica contra o hash descartavel so para
        # gastar o mesmo tempo. O resultado e ignorado — nunca sera True,
        # porque a senha por tras dele e aleatoria e nao foi guardada.
        verify_password(credentials.password, _DUMMY_PASSWORD_HASH)
        senha_confere = False

    if not senha_confere:
        login_limiter.registrar_falha(chaves)
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

    # Acesso legitimo limpa o historico: quem errou algumas vezes e depois
    # acertou nao deve carregar essas falhas para a proxima sessao.
    login_limiter.limpar(chaves)

    # O `sub` do JWT e SEMPRE o e-mail, nunca o username usado para entrar —
    # e o que faz require_user/decode_token nao precisarem saber que
    # username existe. Ver models/user.py (User.username) para o resto da
    # decisao.
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
    user: User = Depends(require_active_user),
):
    """
    Perfil da PROPRIA conta (Fase 8). So o nome.

    `require_active_user` (nao `require_user`): editar o nome nao e uma das
    duas excecoes de uma conta com troca de senha pendente — so ver a conta
    (GET) e trocar a senha (POST /change-password) sao.

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

    Usa `require_user`, nao `require_active_user`, de proposito: e uma das
    duas rotas que uma conta com `must_change_password=True` PRECISA
    alcancar para se destrancar — a outra e GET /me. Bloquear esta rota
    tambem deixaria a conta sem saida.

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
    # Troca feita pelo proprio dono, com a senha atual conferida: e a prova
    # de que a conta deixou de estar so em posse de quem a criou/resetou.
    # Unico ponto do sistema que desliga esta flag.
    user.must_change_password = False
    session.add(user)
    session.commit()
