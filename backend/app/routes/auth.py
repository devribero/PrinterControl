import logging
import secrets
from ipaddress import ip_address

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import Session, select

from app.config import settings
from app.database import get_session
from app.dependencies import require_active_user, require_user
from app.models.user import User
from app.schemas.user import (
    PasswordChange,
    PasswordChangeResponse,
    ProfileUpdate,
    TokenResponse,
    UserLogin,
    UserResponse,
)
from app.services.auth import create_access_token, hash_password, verify_password
from app.services.rate_limit import RateLimiter
from app.services.units import user_response

logger = logging.getLogger("printercontrol.auth")

router = APIRouter(prefix="/auth", tags=["auth"])

# Uma instancia por processo. Ver o docstring de services/rate_limit.py para
# o que isso implica (contagem zera no restart, nao e compartilhada entre
# workers) e por que e aceitavel neste deploy.
login_limiter = RateLimiter(
    max_tentativas=settings.login_max_attempts,
    janela_segundos=settings.login_window_seconds,
)

# Separado do login_limiter: errar a senha atual na tela de troca nao deve
# consumir a cota de login da conta, e vice-versa.
password_change_limiter = RateLimiter(
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

    `X-Forwarded-For` e escolhido pelo cliente. Ler esse cabecalho de quem
    quer que seja permite trocar de identidade a cada tentativa e zerar a
    contagem por IP — exatamente o que o limite existe para impedir (QA-10:
    sete tentativas com um XFF diferente a cada chamada nao chegavam ao 429
    que cinco tentativas honestas provocavam).

    Por isso a leitura exige DUAS condicoes, nao mais so a primeira:

      1. TRUST_PROXY_HEADERS=true — ha um proxy na frente;
      2. a CONEXAO ter chegado de um endereco em TRUSTED_PROXY_IPS.

    A (2) e o que faltava. O cabecalho passa a ser aceito so quando quem o
    entregou e o proxy conhecido; um cliente que alcance a porta do backend
    por fora e identificado pelo IP real da conexao, invente ele o cabecalho
    que quiser.

    TRUSTED_PROXY_IPS vazio com TRUST_PROXY_HEADERS=true mantem o
    comportamento antigo, para nao derrubar um deploy existente no meio de
    um upgrade — mas o startup registra um aviso (ver config.py).
    """
    if settings.trust_proxy_headers and settings.proxy_confiavel(_ip_da_conexao(request)):
        encaminhado = request.headers.get("x-forwarded-for", "")
        if encaminhado:
            # O primeiro da lista e o cliente original; o resto sao proxies.
            return encaminhado.split(",")[0].strip()

    return _ip_da_conexao(request)


def _ip_da_conexao(request: Request) -> str:
    """IP do peer TCP — o unico que o cliente nao escolhe."""
    return request.client.host if request.client else "desconhecido"


def _chaves_do_limite(request: Request, chave_conta: str) -> list[str]:
    """
    Chaves do limitador de login: a da conta sempre, a do IP so quando o IP
    identifica alguem.

    Origem LOOPBACK nao identifica ninguem. O painel chama a API pelo proxy
    do Next (next.config.ts, `rewrites`) e o Cloudflare Tunnel tambem roda
    na propria maquina: nos dois caminhos TODO login chega de 127.0.0.1.
    Contar por esse "IP" transformava o limite em um contador global — cinco
    senhas erradas de qualquer pessoa bloqueavam o login de todo mundo por
    LOGIN_WINDOW_SECONDS. A contagem por conta continua valendo e e ela que
    segura a forca bruta nesse cenario.

    Confiar no X-Forwarded-For vindo do Next NAO resolveria: o proxy do Next
    repassa o cabecalho que o cliente mandou (so preenche quando ausente),
    entao o valor seria escolhido pelo atacante.
    """
    chaves = [f"email:{chave_conta}"]
    origem = _identificar_origem(request)
    try:
        loopback = ip_address(origem).is_loopback
    except ValueError:
        loopback = False
    if not loopback:
        chaves.insert(0, f"ip:{origem}")
    return chaves


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
    chaves = _chaves_do_limite(request, chave_conta)

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
    access_token = create_access_token(data={"sub": user.email, "ver": user.token_version})
    return TokenResponse(access_token=access_token, user=user_response(session, user))


@router.get("/me", response_model=UserResponse)
def read_current_user(user: User = Depends(require_user), session: Session = Depends(get_session)):
    """Conta autenticada, papel e unidade — usado para decidir o que exibir/permitir."""
    return user_response(session, user)


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
    return user_response(session, user)


@router.post("/change-password", response_model=PasswordChangeResponse)
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

    Encerra TODAS as outras sessoes da conta (QA-04): `token_version` sobe
    um, e require_user passa a recusar qualquer token emitido antes desta
    chamada. Era a limitacao conhecida ate aqui — o JWT e stateless, e sem
    esse contador trocar a senha nao tirava de circulacao o token de quem ja
    estivesse dentro, que e justamente o motivo pelo qual se troca a senha
    as pressas.

    Quem trocou a senha tambem perde o proprio token: a resposta devolve um
    novo em `access_token`, para o painel substituir o antigo sem obrigar um
    novo login.
    """
    # Mesmo limite do login, por conta: sem ele, um token roubado virava um
    # oraculo ilimitado para descobrir a senha atual (e reusa-la em outros
    # sistemas onde a pessoa repita a senha).
    chave = [f"senha-atual:{user.email.strip().lower()}"]
    limite = password_change_limiter.verificar(chave)
    if limite.bloqueado:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                f"Muitas tentativas com a senha atual errada. Tente novamente em "
                f"{max(1, limite.retry_after // 60)} minuto(s)."
            ),
            headers={"Retry-After": str(limite.retry_after)},
        )

    if not verify_password(data.current_password, user.password_hash):
        password_change_limiter.registrar_falha(chave)
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

    password_change_limiter.limpar(chave)
    user.password_hash = hash_password(data.new_password)
    # Troca feita pelo proprio dono, com a senha atual conferida: e a prova
    # de que a conta deixou de estar so em posse de quem a criou/resetou.
    # Unico ponto do sistema que desliga esta flag.
    user.must_change_password = False
    # QA-04: derruba todas as sessoes abertas com a senha ANTIGA.
    user.token_version += 1
    session.add(user)
    session.commit()
    session.refresh(user)

    # Token novo para quem acabou de trocar. Sem isto a propria pessoa seria
    # deslogada pela correcao — o token que ela esta usando agora tambem foi
    # emitido com a versao antiga.
    return PasswordChangeResponse(
        access_token=create_access_token(data={"sub": user.email, "ver": user.token_version})
    )


@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
def logout_all_sessions(
    session: Session = Depends(get_session),
    user: User = Depends(require_user),
):
    """
    Encerra TODAS as sessoes da conta, inclusive a que fez a chamada.

    O JWT e stateless, entao "sair" no painel so apagava o token do
    navegador — uma copia roubada continuava valendo ate expirar. Subir
    `token_version` faz require_user recusar todo token emitido antes,
    o mesmo mecanismo da troca de senha (QA-04), sem exigir trocar a senha.

    `require_user` (nao `require_active_user`): quem esta com troca de senha
    pendente tambem precisa conseguir derrubar uma sessao suspeita.
    """
    user.token_version += 1
    session.add(user)
    session.commit()
