r"""
Botao "Testar alerta" (POST /api/notifications/test), 21/09/2026.

Cobre: notificacao critica so na caixa de quem clicou; card de teste no
webhook com os desfechos que a tela precisa distinguir (nao configurado,
enviado, erro HTTP, timeout); a URL do webhook nunca volta na resposta; e
so admin pode disparar.

Nao precisa do backend rodando e nunca chama o webhook de verdade: httpx.post
e substituido por um dublê. O banco real nunca e aberto.

    .\venv\Scripts\python.exe tests_test_alert.py
"""
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

_TMP = Path(tempfile.mkdtemp(prefix="printercontrol-testalert-"))
os.environ["DATABASE_URL"] = f"sqlite:///{(_TMP / 'test_alert.db').as_posix()}"
os.environ["ENVIRONMENT"] = "development"
os.environ["PRINT_SERVER_MODE"] = "mock"

import httpx  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import Session, select  # noqa: E402

from app.config import settings  # noqa: E402
from app.database import create_db_and_tables, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models.alert import Alert  # noqa: E402
from app.models.notification import Notification  # noqa: E402
from app.models.user import Role, User  # noqa: E402
from app.services.auth import hash_password  # noqa: E402

URL_SECRETA = "https://exemplo.invalid/workflows/abc?sig=ASSINATURA-SECRETA"
SENHA = "senha-de-teste-123"
_falhas = []


def check(nome, obtido, esperado):
    ok = obtido == esperado
    print(f"  [{'OK  ' if ok else 'FALHA'}] {nome}: {obtido!r}" + ("" if ok else f" (esperado {esperado!r})"))
    if not ok:
        _falhas.append(nome)


class _Resposta:
    def __init__(self, status_code):
        self.status_code = status_code


def main():
    create_db_and_tables()
    ids = {}
    with Session(engine) as s:
        for papel, role in (("admin", Role.ADMIN.value), ("colega", Role.ADMIN.value), ("viewer", Role.VIEWER.value)):
            u = User(email=f"{papel}@teste-alerta.com", password_hash=hash_password(SENHA), name=papel, role=role)
            s.add(u)
            s.commit()
            s.refresh(u)
            ids[papel] = u.id

    client = TestClient(app)

    def token(papel):
        r = client.post("/api/auth/login", json={"email": f"{papel}@teste-alerta.com", "password": SENHA})
        return {"Authorization": f"Bearer {r.json()['access_token']}"}

    admin = token("admin")

    print("--- 1. webhook nao configurado: notificacao chega, webhook reporta ---")
    with patch.object(settings, "webhook_url", ""), patch.object(httpx, "post") as post:
        r = client.post("/api/notifications/test", headers=admin)
    check("status 201", r.status_code, 201)
    corpo = r.json()
    check("notificacao critica", corpo["notification"]["severity"], "critical")
    check("webhook.configured", corpo["webhook"]["configured"], False)
    check("webhook.sent", corpo["webhook"]["sent"], False)
    check("webhook.detail", corpo["webhook"]["detail"], "nao_configurado")
    check("nao tentou chamar a rede", post.call_count, 0)

    print("\n--- 2. webhook configurado e aceita ---")
    with patch.object(settings, "webhook_url", URL_SECRETA), patch.object(httpx, "post", return_value=_Resposta(202)) as post:
        r = client.post("/api/notifications/test", headers=admin)
    corpo = r.json()
    check("webhook.sent", corpo["webhook"]["sent"], True)
    check("webhook.detail", corpo["webhook"]["detail"], "enviado")
    check("uma chamada ao webhook", post.call_count, 1)
    card = post.call_args.kwargs["json"]
    titulo = card["attachments"][0]["content"]["body"][0]["items"][0]["text"]
    check("card se anuncia como TESTE", "TESTE" in titulo, True)
    check("URL nunca volta na resposta", URL_SECRETA in r.text or "ASSINATURA" in r.text, False)

    print("\n--- 3. webhook responde erro / timeout ---")
    with patch.object(settings, "webhook_url", URL_SECRETA), patch.object(httpx, "post", return_value=_Resposta(401)):
        r = client.post("/api/notifications/test", headers=admin)
    check("erro HTTP vira http_401", r.json()["webhook"]["detail"], "http_401")
    check("notificacao gravada mesmo com webhook falhando", r.status_code, 201)
    with patch.object(settings, "webhook_url", URL_SECRETA), patch.object(httpx, "post", side_effect=httpx.ReadTimeout("t")):
        r = client.post("/api/notifications/test", headers=admin)
    check("timeout vira 'timeout'", r.json()["webhook"]["detail"], "timeout")

    print("\n--- 4. escopo: so a caixa de quem clicou; nada em /alerts ---")
    with Session(engine) as s:
        do_admin = s.exec(select(Notification).where(Notification.user_id == ids["admin"])).all()
        do_colega = s.exec(select(Notification).where(Notification.user_id == ids["colega"])).all()
        alertas = s.exec(select(Alert)).all()
    check("4 testes na caixa do admin", len(do_admin), 4)
    check("nada na caixa do colega", len(do_colega), 0)
    check("nenhum alerta criado", len(alertas), 0)

    print("\n--- 5. so admin ---")
    with patch.object(httpx, "post") as post:
        r = client.post("/api/notifications/test", headers=token("viewer"))
    check("viewer recebe 403", r.status_code, 403)
    check("viewer nao dispara webhook", post.call_count, 0)
    check("sem token recebe 401", client.post("/api/notifications/test").status_code, 401)

    print()
    if _falhas:
        print(f"FALHOU: {_falhas}")
        raise SystemExit(1)
    print("Todos os testes do botao Testar alerta passaram.")


if __name__ == "__main__":
    main()
