"""
Hash de senha e emissao/validacao do JWT.

POR QUE PyJWT E NAO python-jose (Fase 10)
-----------------------------------------
Ate aqui o token era assinado com `python-jose==3.3.0`, que acumulava dois
problemas conhecidos e um estrutural:

    CVE-2024-33663  confusao de algoritmo — um token podia ser aceito com um
                    algoritmo diferente do esperado;
    CVE-2024-33664  bomba de descompressao em JWE, capaz de consumir toda a
                    memoria do processo ao decodificar um token hostil;
    ecdsa           dependencia arrastada pelo jose, com a CVE-2024-23342
                    (Minerva, ataque de tempo) que os proprios mantenedores
                    declararam que NAO sera corrigida.

Atualizar o jose resolveria as duas primeiras. Trocar por PyJWT resolve as
tres — o `ecdsa` sai junto — e ainda troca uma biblioteca pouco mantida pela
que a propria documentacao de seguranca do FastAPI usa. O custo foi baixo
porque este projeto so usa HS256 com segredo compartilhado: duas chamadas,
`encode` e `decode`. Nenhum token emitido antes deixou de valer: o formato e
o algoritmo sao os mesmos, so mudou quem assina.
"""
from datetime import datetime, timedelta, timezone

import jwt
from jwt import InvalidTokenError
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()

    # Aware em UTC, em vez de datetime.utcnow(): o naive de antes dependia de
    # a biblioteca ADIVINHAR que aquilo era UTC (as duas adivinham certo, mas
    # e uma suposicao) e utcnow() esta descontinuado desde o Python 3.12.
    # O instante gravado no `exp` e exatamente o mesmo de antes.
    agora = datetime.now(timezone.utc)
    expira = agora + (expires_delta or timedelta(hours=settings.access_token_expire_hours))

    to_encode.update({"exp": expira})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> dict | None:
    """
    Devolve {"email": ...} para um token valido, ou None.

    `algorithms` e uma lista de UM item de proposito: aceitar o algoritmo que
    o proprio token declara e a confusao de algoritmo da CVE-2024-33663.
    Assinatura invalida, token expirado e token malformado caem todos no
    mesmo None — quem chama (require_user) responde 401 sem distinguir,
    porque a diferenca so interessaria a quem esta atacando.
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except InvalidTokenError:
        return None

    email = payload.get("sub")
    if email is None:
        return None
    return {"email": email}
