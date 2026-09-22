r"""
Unidades (21/09/2026): CRUD de /api/units, vinculo de servidores e usuarios,
e roteamento dos avisos (webhook da unidade + central; sino filtrado pela
unidade da impressora).

Nao precisa do backend rodando e nunca chama o webhook de verdade: httpx.post
e substituido por um duble em todo teste que poderia disparar. O banco real
nunca e aberto.

    .\venv\Scripts\python.exe tests_units.py
"""
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

_TMP = Path(tempfile.mkdtemp(prefix="printercontrol-units-"))
os.environ["DATABASE_URL"] = f"sqlite:///{(_TMP / 'units.db').as_posix()}"
os.environ["ENVIRONMENT"] = "development"
os.environ["PRINT_SERVER_MODE"] = "mock"

import httpx  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import Session, select  # noqa: E402

from app.config import settings  # noqa: E402
from app.database import create_db_and_tables, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models.alert import Alert  # noqa: E402
from app.models.audit_log import AuditLog  # noqa: E402
from app.models.notification import Notification  # noqa: E402
from app.models.print_server import PrintServer  # noqa: E402
from app.models.printer import Printer, PrinterReading  # noqa: E402
from app.models.user import Role, User  # noqa: E402
from app.services import alert_engine  # noqa: E402
from app.services.auth import hash_password  # noqa: E402

URL_CENTRAL = "https://central.invalid/workflows/central?sig=ASSINATURA-CENTRAL"
URL_MANAUS = "https://manaus.invalid/workflows/mao?sig=ASSINATURA-MANAUS"
URL_VILA = "https://vila.invalid/workflows/vo?sig=ASSINATURA-VILA"
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


def _sem_segredo(texto: str) -> bool:
    return "ASSINATURA" not in texto and "/workflows/" not in texto


def main():
    create_db_and_tables()
    ids = {}
    with Session(engine) as s:
        for papel, role, ativo in (
            ("admin", Role.ADMIN.value, True),
            ("viewer", Role.VIEWER.value, True),
            ("mao", Role.VIEWER.value, True),
            ("vo", Role.VIEWER.value, True),
            ("inativo", Role.VIEWER.value, False),
        ):
            u = User(email=f"{papel}@teste-unidades.com", password_hash=hash_password(SENHA),
                     name=papel, role=role, is_active=ativo)
            s.add(u)
            s.commit()
            s.refresh(u)
            ids[papel] = u.id

    client = TestClient(app)

    def token(papel):
        r = client.post("/api/auth/login", json={"email": f"{papel}@teste-unidades.com", "password": SENHA})
        return {"Authorization": f"Bearer {r.json()['access_token']}"}

    admin = token("admin")
    viewer = token("viewer")

    print("--- 1. criar unidades, validacao e permissoes ---")
    r = client.post("/api/units", json={"name": "  Manaus  ", "webhook_url": URL_MANAUS}, headers=admin)
    check("POST 201", r.status_code, 201)
    manaus = r.json()
    check("nome aparado", manaus["name"], "Manaus")
    check("webhook_configured", manaus["webhook_configured"], True)
    check("webhook_host so o host", manaus["webhook_host"], "manaus.invalid")
    check("campos do contrato", sorted(manaus.keys()), sorted([
        "id", "name", "active", "webhook_configured", "webhook_host",
        "server_hosts", "server_count", "user_count", "created_at",
    ]))
    check("URL nunca na resposta (POST)", _sem_segredo(r.text), True)

    r = client.post("/api/units", json={"name": "Vila Olimpia"}, headers=admin)
    check("POST sem webhook 201", r.status_code, 201)
    vila = r.json()
    check("sem webhook: configured False", vila["webhook_configured"], False)
    check("sem webhook: host vazio", vila["webhook_host"], "")

    check("nome duplicado (maiusculas) 409",
          client.post("/api/units", json={"name": "MANAUS"}, headers=admin).status_code, 409)
    check("http:// recusado 422",
          client.post("/api/units", json={"name": "X", "webhook_url": "http://inseguro.invalid/x"},
                      headers=admin).status_code, 422)
    check("lixo recusado 422",
          client.post("/api/units", json={"name": "X", "webhook_url": "nao e url"}, headers=admin).status_code, 422)
    check("nome vazio 422", client.post("/api/units", json={"name": "   "}, headers=admin).status_code, 422)
    check("nome longo 422", client.post("/api/units", json={"name": "x" * 81}, headers=admin).status_code, 422)

    check("viewer POST 403", client.post("/api/units", json={"name": "Nova"}, headers=viewer).status_code, 403)
    check("viewer PATCH 403",
          client.patch(f"/api/units/{manaus['id']}", json={"name": "Z"}, headers=viewer).status_code, 403)
    check("viewer DELETE 403", client.delete(f"/api/units/{manaus['id']}", headers=viewer).status_code, 403)
    with patch.object(httpx, "post") as post:
        check("viewer test-webhook 403",
              client.post(f"/api/units/{manaus['id']}/test-webhook", headers=viewer).status_code, 403)
    check("viewer nao dispara webhook", post.call_count, 0)
    check("sem token 401", client.get("/api/units").status_code, 401)

    r = client.get("/api/units", headers=viewer)
    check("viewer GET 200", r.status_code, 200)
    check("ordenado por nome", [u["name"] for u in r.json()], ["Manaus", "Vila Olimpia"])
    check("URL nunca na resposta (GET)", _sem_segredo(r.text), True)

    print("\n--- 2. PATCH: nome, webhook (omitido/limpo/novo), ativacao ---")
    r = client.patch(f"/api/units/{vila['id']}", json={"name": "Vila Olímpia"}, headers=admin)
    check("renomear 200", r.status_code, 200)
    check("webhook omitido mantem (vazio)", r.json()["webhook_configured"], False)
    check("renomear para nome existente 409",
          client.patch(f"/api/units/{vila['id']}", json={"name": "manaus"}, headers=admin).status_code, 409)
    check("renomear para o proprio nome 200",
          client.patch(f"/api/units/{vila['id']}", json={"name": "VILA OLÍMPIA"}, headers=admin).status_code, 200)
    client.patch(f"/api/units/{vila['id']}", json={"name": "Vila Olímpia"}, headers=admin)
    check("PATCH http:// 422",
          client.patch(f"/api/units/{vila['id']}", json={"webhook_url": "http://x.invalid"}, headers=admin).status_code,
          422)
    r = client.patch(f"/api/units/{vila['id']}", json={"webhook_url": URL_VILA}, headers=admin)
    check("webhook novo", (r.json()["webhook_configured"], r.json()["webhook_host"]), (True, "vila.invalid"))
    check("URL nunca na resposta (PATCH)", _sem_segredo(r.text), True)
    r = client.patch(f"/api/units/{vila['id']}", json={"active": False}, headers=admin)
    check("desativar", r.json()["active"], False)
    check("webhook omitido mantem (URL)", r.json()["webhook_configured"], True)
    r = client.patch(f"/api/units/{vila['id']}", json={"webhook_url": ""}, headers=admin)
    check("\"\" limpa o webhook", r.json()["webhook_configured"], False)
    client.patch(f"/api/units/{vila['id']}", json={"webhook_url": URL_VILA, "active": True}, headers=admin)
    check("PATCH inexistente 404",
          client.patch("/api/units/9999", json={"active": True}, headers=admin).status_code, 404)

    with Session(engine) as s:
        detalhes = " ".join(
            (a.before or "") + (a.after or "")
            for a in s.exec(select(AuditLog).where(AuditLog.target_type == "unit")).all()
        )
        acoes = {a.action for a in s.exec(select(AuditLog).where(AuditLog.target_type == "unit")).all()}
    check("auditoria create/update", {"unit.create", "unit.update"} <= acoes, True)
    check("URL nunca na auditoria", _sem_segredo(detalhes), True)
    check("auditoria registra 'webhook alterado'", "webhook alterado" in detalhes, True)

    print("\n--- 3. servidores e usuarios ligados a unidade ---")
    r = client.post("/api/servers", json={"host": "srv-manaus", "mode": "mock", "unit_id": manaus["id"]},
                    headers=admin)
    check("servidor criado com unidade", (r.status_code, r.json().get("unit_id"), r.json().get("unit_name")),
          (201, manaus["id"], "Manaus"))
    srv_manaus = r.json()["id"]
    r = client.post("/api/servers", json={"host": "srv-vila", "mode": "mock"}, headers=admin)
    check("servidor sem unidade", (r.json()["unit_id"], r.json()["unit_name"]), (None, None))
    srv_vila = r.json()["id"]
    check("servidor com unidade inexistente 404",
          client.post("/api/servers", json={"host": "srv-x", "mode": "mock", "unit_id": 9999},
                      headers=admin).status_code, 404)
    r = client.patch(f"/api/servers/{srv_vila}", json={"unit_id": vila["id"]}, headers=admin)
    check("PATCH servidor -> unidade", r.json()["unit_name"], "Vila Olímpia")
    r = client.patch(f"/api/servers/{srv_vila}", json={"name": "Vila"}, headers=admin)
    check("PATCH sem unit_id mantem", r.json()["unit_id"], vila["id"])
    check("PATCH servidor unidade inexistente 404",
          client.patch(f"/api/servers/{srv_vila}", json={"unit_id": 9999}, headers=admin).status_code, 404)
    client.post("/api/servers", json={"host": "srv-central", "mode": "mock"}, headers=admin)

    r = client.patch(f"/api/users/{ids['mao']}", json={"unit_id": manaus["id"]}, headers=admin)
    check("usuario -> unidade", (r.status_code, r.json()["unit_id"], r.json()["unit_name"]),
          (200, manaus["id"], "Manaus"))
    r = client.patch(f"/api/users/{ids['vo']}", json={"unit_id": vila["id"]}, headers=admin)
    check("usuario vila", r.json()["unit_name"], "Vila Olímpia")
    check("usuario unidade inexistente 404",
          client.patch(f"/api/users/{ids['vo']}", json={"unit_id": 9999}, headers=admin).status_code, 404)
    r = client.post("/api/users", json={"email": "novo@teste-unidades.com", "password": SENHA, "name": "Novo",
                                        "unit_id": manaus["id"]}, headers=admin)
    check("criar usuario com unidade", (r.status_code, r.json()["unit_name"]), (201, "Manaus"))
    novo_id = r.json()["id"]
    r = client.patch(f"/api/users/{novo_id}", json={"unit_id": None}, headers=admin)
    check("unit_id null tira da unidade", (r.json()["unit_id"], r.json()["unit_name"]), (None, None))
    check("viewer nao altera a propria unidade",
          client.patch(f"/api/users/{ids['viewer']}", json={"unit_id": manaus["id"]}, headers=viewer).status_code, 403)
    lista = {u["id"]: u for u in client.get("/api/users", headers=admin).json()}
    check("GET /users traz unit_name", lista[ids["mao"]]["unit_name"], "Manaus")

    r = client.get("/api/auth/me", headers=token("mao"))
    check("/auth/me traz unidade", (r.json()["unit_id"], r.json()["unit_name"]), (manaus["id"], "Manaus"))
    r = client.get("/api/auth/me", headers=admin)
    check("/auth/me sem unidade", (r.json()["unit_id"], r.json()["unit_name"]), (None, None))
    r = client.post("/api/auth/login", json={"email": "mao@teste-unidades.com", "password": SENHA})
    check("login traz unidade", r.json()["user"]["unit_name"], "Manaus")

    unidades = {u["id"]: u for u in client.get("/api/units", headers=admin).json()}
    check("server_hosts", unidades[manaus["id"]]["server_hosts"], ["srv-manaus"])
    check("server_count", unidades[manaus["id"]]["server_count"], 1)
    check("user_count", unidades[manaus["id"]]["user_count"], 1)

    print("\n--- 4. roteamento do webhook e do sino ---")
    with Session(engine) as s:
        impressoras = {}
        for chave, host in (("mao", "srv-manaus"), ("vo", "srv-vila"),
                            ("central", "srv-central"), ("solta", "srv-sem-registro")):
            p = Printer(server=host, name=f"IMP_{chave.upper()}", ip="10.255.0.1", model="Modelo")
            s.add(p)
            s.commit()
            s.refresh(p)
            impressoras[chave] = p.id

    def disparar(chave):
        """Leitura com toner critico; devolve (URLs chamadas, ids notificados)."""
        pid = impressoras[chave]
        with Session(engine) as s:
            for a in s.exec(select(Alert).where(Alert.printer_id == pid)).all():
                # Sem isto um id de alerta reaproveitado herdaria notificacoes antigas.
                for n in s.exec(select(Notification).where(Notification.alert_id == a.id)).all():
                    s.delete(n)
                s.delete(a)
            s.commit()
            leitura = PrinterReading(printer_id=pid, status="atencao", page_count=10, toner_k=5)
            s.add(leitura)
            s.commit()
            s.refresh(leitura)
            with patch.object(httpx, "post", return_value=_Resposta(200)) as post:
                alert_engine.evaluate_reading(s, pid, leitura)
            alerta = s.exec(select(Alert).where(Alert.printer_id == pid, Alert.resolved_at == None)).first()  # noqa: E711
            destinatarios = {n.user_id for n in s.exec(
                select(Notification).where(Notification.alert_id == alerta.id)).all()}
        return [c.args[0] for c in post.call_args_list], destinatarios

    todos_ativos = {ids["admin"], ids["viewer"], ids["mao"], ids["vo"], novo_id}
    central_users = {ids["admin"], ids["viewer"], novo_id}

    with patch.object(settings, "webhook_url", URL_CENTRAL):
        urls, dest = disparar("mao")
        check("unidade + central", sorted(urls), sorted([URL_MANAUS, URL_CENTRAL]))
        check("sino: central + Manaus", dest, central_users | {ids["mao"]})

        urls, dest = disparar("central")
        check("servidor sem unidade -> so central", urls, [URL_CENTRAL])
        check("sino: servidor sem unidade -> todos", dest, todos_ativos)

        urls, dest = disparar("solta")
        check("sem PrintServer -> so central", urls, [URL_CENTRAL])
        check("sino: sem PrintServer -> todos", dest, todos_ativos)
        check("inativo nunca recebe", ids["inativo"] in dest, False)

        client.patch(f"/api/units/{vila['id']}", json={"active": False}, headers=admin)
        urls, dest = disparar("vo")
        check("unidade inativa -> so central", urls, [URL_CENTRAL])
        check("sino: unidade inativa ainda filtra", dest, central_users | {ids["vo"]})
        client.patch(f"/api/units/{vila['id']}", json={"active": True, "webhook_url": ""}, headers=admin)
        urls, _ = disparar("vo")
        check("unidade sem URL -> so central", urls, [URL_CENTRAL])

        client.patch(f"/api/units/{vila['id']}", json={"webhook_url": URL_CENTRAL}, headers=admin)
        urls, _ = disparar("vo")
        check("mesma URL da central -> um envio", urls, [URL_CENTRAL])
        client.patch(f"/api/units/{vila['id']}", json={"webhook_url": URL_VILA}, headers=admin)

    with patch.object(settings, "webhook_url", ""):
        urls, _ = disparar("mao")
        check("central vazia -> so unidade", urls, [URL_MANAUS])

    print("\n--- 5. offline nunca vai para webhook ---")
    with patch.object(settings, "webhook_url", URL_CENTRAL), patch.object(settings, "offline_alert_consecutive", 1):
        pid = impressoras["mao"]
        with Session(engine) as s:
            leitura = PrinterReading(printer_id=pid, status="offline", page_count=10)
            s.add(leitura)
            s.commit()
            s.refresh(leitura)
            with patch.object(httpx, "post", return_value=_Resposta(200)) as post:
                acoes = alert_engine.evaluate_reading(s, pid, leitura)
        check("offline criado", acoes["offline"], "created")
        check("offline sem webhook", post.call_count, 0)

    print("\n--- 6. notify manual: unidade + central ---")
    with Session(engine) as s:
        alerta = s.exec(select(Alert).where(Alert.printer_id == impressoras["mao"],
                                            Alert.alert_type == "toner:K")).first()
    with patch.object(settings, "webhook_url", URL_CENTRAL), \
            patch.object(httpx, "post", return_value=_Resposta(200)) as post:
        r = client.post(f"/api/alerts/{alerta.id}/notify", headers=admin)
    check("notify 200 sent", (r.status_code, r.json()["sent"]), (200, True))
    check("notify unidade + central", sorted(c.args[0] for c in post.call_args_list),
          sorted([URL_MANAUS, URL_CENTRAL]))
    with patch.object(settings, "webhook_url", URL_CENTRAL), \
            patch.object(httpx, "post", return_value=_Resposta(200)) as post:
        client.post("/api/notifications/test", headers=admin)
    check("/notifications/test continua so central", [c.args[0] for c in post.call_args_list], [URL_CENTRAL])

    print("\n--- 7. POST /api/units/{id}/test-webhook ---")
    with patch.object(settings, "webhook_url", URL_CENTRAL), \
            patch.object(httpx, "post", return_value=_Resposta(202)) as post:
        r = client.post(f"/api/units/{manaus['id']}/test-webhook", headers=admin)
    check("test-webhook enviado", r.json(), {"sent": True, "configured": True, "detail": "enviado"})
    check("so o webhook da unidade", [c.args[0] for c in post.call_args_list], [URL_MANAUS])
    card = post.call_args.kwargs["json"]
    conteudo = str(card)
    check("card diz TESTE", "TESTE" in conteudo, True)
    check("card cita a unidade", "Manaus" in conteudo, True)
    check("URL nunca na resposta (test)", _sem_segredo(r.text), True)
    with patch.object(httpx, "post", return_value=_Resposta(401)):
        r = client.post(f"/api/units/{manaus['id']}/test-webhook", headers=admin)
    check("erro HTTP -> http_401", r.json(), {"sent": False, "configured": True, "detail": "http_401"})
    with patch.object(httpx, "post", side_effect=httpx.ReadTimeout("t")):
        r = client.post(f"/api/units/{manaus['id']}/test-webhook", headers=admin)
    check("timeout", r.json()["detail"], "timeout")
    client.patch(f"/api/units/{vila['id']}", json={"webhook_url": ""}, headers=admin)
    with patch.object(settings, "webhook_url", URL_CENTRAL), patch.object(httpx, "post") as post:
        r = client.post(f"/api/units/{vila['id']}/test-webhook", headers=admin)
    check("sem webhook -> nao_configurado", r.json(), {"sent": False, "configured": False, "detail": "nao_configurado"})
    check("sem webhook nao chama a central", post.call_count, 0)
    check("test-webhook inexistente 404",
          client.post("/api/units/9999/test-webhook", headers=admin).status_code, 404)

    print("\n--- 8. DELETE desliga servidores e usuarios ---")
    r = client.delete(f"/api/units/{manaus['id']}", headers=admin)
    check("DELETE 204", r.status_code, 204)
    with Session(engine) as s:
        check("servidor desligado", s.get(PrintServer, srv_manaus).unit_id, None)
        check("usuario desligado", s.get(User, ids["mao"]).unit_id, None)
        check("usuario continua ativo", s.get(User, ids["mao"]).is_active, True)
        acoes = {a.action for a in s.exec(select(AuditLog).where(AuditLog.target_type == "unit")).all()}
    check("auditoria delete", "unit.delete" in acoes, True)
    check("DELETE de novo 404", client.delete(f"/api/units/{manaus['id']}", headers=admin).status_code, 404)
    check("unidade some da lista", [u["name"] for u in client.get("/api/units", headers=admin).json()],
          ["Vila Olímpia"])

    print()
    if _falhas:
        print(f"FALHOU: {_falhas}")
        raise SystemExit(1)
    print("Todos os testes de unidades passaram.")


if __name__ == "__main__":
    main()
