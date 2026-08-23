"""
Fase 7 - Notificacoes internas.

Como tests_rbac.py/tests_users.py/tests_print_servers.py, NAO precisa do
backend rodando: TestClient contra um SQLite temporario. O banco real nunca
e aberto.

    .\\venv\\Scripts\\python.exe tests_notifications.py
"""
import os
import tempfile
from pathlib import Path

# Antes de importar app.config: as Settings leem o ambiente no import.
_TMP = Path(tempfile.mkdtemp(prefix="printercontrol-notif-"))
os.environ["DATABASE_URL"] = f"sqlite:///{(_TMP / 'notif_test.db').as_posix()}"
os.environ["ENVIRONMENT"] = "development"
os.environ["PRINT_SERVER_MODE"] = "mock"

from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import Session, select  # noqa: E402

from app.database import create_db_and_tables, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models.alert import Alert  # noqa: E402
from app.models.notification import Notification  # noqa: E402
from app.models.printer import Printer  # noqa: E402
from app.models.user import Role, User  # noqa: E402
from app.services.auth import hash_password  # noqa: E402

_falhas = []


def check(nome, obtido, esperado):
    ok = obtido == esperado
    print(f"  [{'OK  ' if ok else 'FALHA'}] {nome}: {obtido!r}" + ("" if ok else f" (esperado {esperado!r})"))
    if not ok:
        _falhas.append(nome)


def check_true(nome, cond, detalhe=""):
    print(f"  [{'OK  ' if cond else 'FALHA'}] {nome}" + (f": {detalhe}" if detalhe else ""))
    if not cond:
        _falhas.append(nome)


SENHA = "senha-de-teste-123"
CONTAS = {
    "admin": ("admin@teste-notif.com", Role.ADMIN.value),
    "operator": ("operator@teste-notif.com", Role.OPERATOR.value),
    "viewer": ("viewer@teste-notif.com", Role.VIEWER.value),
    "inativo": ("inativo@teste-notif.com", Role.VIEWER.value),
}


def h(token):
    return {"Authorization": f"Bearer {token}"}


def main():
    create_db_and_tables()

    ids = {}
    with Session(engine) as s:
        for papel, (email, role) in CONTAS.items():
            u = User(
                email=email,
                password_hash=hash_password(SENHA),
                name=papel,
                role=role,
                is_active=(papel != "inativo"),
            )
            s.add(u)
            s.commit()
            s.refresh(u)
            ids[papel] = u.id

        # Impressora + alerta reais, para o vinculo opcional ser testado
        # contra um alerta que existe de verdade.
        p = Printer(name="IMP_TESTE", ip="10.0.0.9", model="Elgin TT042", server="srv-teste")
        s.add(p)
        s.commit()
        s.refresh(p)
        printer_id = p.id

        a = Alert(
            printer_id=printer_id,
            alert_type="toner:K",
            severity="critical",
            message="Toner K critico: 4%",
        )
        s.add(a)
        s.commit()
        s.refresh(a)
        alert_id = a.id

    client = TestClient(app)
    tokens = {
        papel: client.post("/api/auth/login", json={"email": email, "password": SENHA}).json().get("access_token")
        for papel, (email, _) in CONTAS.items()
    }

    print("\n[1] A tabela nasce com o create_all (modelo registrado em models/__init__)")
    with Session(engine) as s:
        s.exec(select(Notification)).all()  # estoura se a tabela nao existir
    check_true("tabela notifications existe", True)
    r = client.get("/api/notifications", headers=h(tokens["viewer"]))
    check("caixa nova esta vazia", r.json(), [])

    print("\n[2] Autenticacao e papeis")
    check("GET sem token -> 401", client.get("/api/notifications").status_code, 401)
    check("POST sem token -> 401",
          client.post("/api/notifications", json={"user_ids": [ids["viewer"]], "message": "oi"}).status_code, 401)
    check("POST viewer -> 403",
          client.post("/api/notifications", json={"user_ids": [ids["viewer"]], "message": "oi"},
                      headers=h(tokens["viewer"])).status_code, 403)
    check("POST operator -> 403",
          client.post("/api/notifications", json={"user_ids": [ids["viewer"]], "message": "oi"},
                      headers=h(tokens["operator"])).status_code, 403)

    print("\n[3] Varios destinatarios viram uma linha por pessoa (fan-out)")
    r = client.post(
        "/api/notifications",
        json={"user_ids": [ids["viewer"], ids["operator"]], "message": "Manutencao no sabado", "severity": "info"},
        headers=h(tokens["admin"]),
    )
    check("POST admin -> 201", r.status_code, 201)
    criadas = r.json()
    check("uma notificacao por destinatario", len(criadas), 2)
    check_true("ids distintos", criadas[0]["id"] != criadas[1]["id"])
    check("sem alerta vinculado", criadas[0]["alert_id"], None)
    check("referencia de alerta ausente", criadas[0]["alert"], None)

    print("\n[4] Cada um enxerga so a propria caixa")
    do_viewer = client.get("/api/notifications", headers=h(tokens["viewer"])).json()
    do_operator = client.get("/api/notifications", headers=h(tokens["operator"])).json()
    do_admin = client.get("/api/notifications", headers=h(tokens["admin"])).json()
    check("viewer recebeu 1", len(do_viewer), 1)
    check("operator recebeu 1", len(do_operator), 1)
    check("admin (remetente) nao recebeu nada", len(do_admin), 0)
    check_true("as duas linhas sao mensagens diferentes no banco",
               do_viewer[0]["id"] != do_operator[0]["id"])
    check("mesma mensagem para os dois", do_viewer[0]["message"], do_operator[0]["message"])

    print("\n[5] Status de leitura e individual")
    nid_viewer = do_viewer[0]["id"]
    check("nasce nao lida", do_viewer[0]["read_at"], None)
    check("contador do viewer antes", client.get("/api/notifications/unread-count",
                                                 headers=h(tokens["viewer"])).json()["unread"], 1)
    r = client.patch(f"/api/notifications/{nid_viewer}/read", headers=h(tokens["viewer"]))
    check("PATCH read -> 200", r.status_code, 200)
    lido_em = r.json()["read_at"]
    check_true("read_at preenchido", lido_em is not None, str(lido_em))
    check("contador do viewer depois", client.get("/api/notifications/unread-count",
                                                  headers=h(tokens["viewer"])).json()["unread"], 0)
    check("contador do operator intacto", client.get("/api/notifications/unread-count",
                                                     headers=h(tokens["operator"])).json()["unread"], 1)

    # Idempotencia: reler nao pode reescrever o instante da primeira leitura.
    r2 = client.patch(f"/api/notifications/{nid_viewer}/read", headers=h(tokens["viewer"]))
    check("reler -> 200", r2.status_code, 200)
    check("read_at preservado na releitura", r2.json()["read_at"], lido_em)

    print("\n[6] Caixa alheia responde 404, nunca 403")
    # 403 confirmaria que o id existe; numa caixa pessoal isso ja e vazamento.
    nid_operator = do_operator[0]["id"]
    check("PATCH em notificacao de outro -> 404",
          client.patch(f"/api/notifications/{nid_operator}/read", headers=h(tokens["viewer"])).status_code, 404)
    check("id inexistente -> 404",
          client.patch("/api/notifications/999999/read", headers=h(tokens["viewer"])).status_code, 404)
    check("a do operator continua nao lida",
          client.get("/api/notifications", headers=h(tokens["operator"])).json()[0]["read_at"], None)

    print("\n[7] unread_only filtra a propria caixa")
    client.post("/api/notifications",
                json={"user_ids": [ids["viewer"]], "message": "Segunda mensagem"},
                headers=h(tokens["admin"]))
    todas = client.get("/api/notifications", headers=h(tokens["viewer"])).json()
    naolidas = client.get("/api/notifications?unread_only=true", headers=h(tokens["viewer"])).json()
    check("viewer tem 2 no total", len(todas), 2)
    check("so 1 nao lida", len(naolidas), 1)
    check("mais recente primeiro", todas[0]["message"], "Segunda mensagem")

    print("\n[8] Vinculo opcional com um alerta")
    r = client.post(
        "/api/notifications",
        json={"user_ids": [ids["operator"]], "message": "Toner K critico na IMP_TESTE",
              "severity": "critical", "alert_id": alert_id},
        headers=h(tokens["admin"]),
    )
    check("POST com alert_id -> 201", r.status_code, 201)
    com_alerta = r.json()[0]
    check("alert_id gravado", com_alerta["alert_id"], alert_id)
    check_true("referencia preenchida", com_alerta["alert"] is not None)
    check("referencia aponta a impressora", com_alerta["alert"]["printer_id"], printer_id)
    check("referencia traz o tipo", com_alerta["alert"]["alert_type"], "toner:K")
    check("alerta ainda aberto", com_alerta["alert"]["resolved"], False)
    check("severidade copiada no momento da criacao", com_alerta["severity"], "critical")

    print("\n[9] Resolver o alerta nao reescreve a notificacao")
    # O ponto do desacoplamento: a mensagem e um instantaneo. So a REFERENCIA
    # acompanha o estado atual do alerta.
    check("resolve o alerta -> 200",
          client.patch(f"/api/alerts/{alert_id}/resolve", headers=h(tokens["operator"])).status_code, 200)
    depois = client.get("/api/notifications", headers=h(tokens["operator"])).json()[0]
    check("mensagem intacta", depois["message"], "Toner K critico na IMP_TESTE")
    check("severidade da notificacao intacta", depois["severity"], "critical")
    check("referencia reflete o alerta resolvido", depois["alert"]["resolved"], True)

    print("\n[10] Alerta apagado deixa a notificacao legivel (referencia vira null)")
    with Session(engine) as s:
        orfa = Notification(user_id=ids["viewer"], message="Aponta para alerta inexistente", alert_id=999999)
        s.add(orfa)
        s.commit()
    caixa = client.get("/api/notifications", headers=h(tokens["viewer"])).json()
    orfa_resp = next(n for n in caixa if n["message"] == "Aponta para alerta inexistente")
    check("alert_id preservado", orfa_resp["alert_id"], 999999)
    check("referencia nula, sem quebrar", orfa_resp["alert"], None)

    print("\n[11] Validacao do envio")
    check("user_ids vazio -> 422",
          client.post("/api/notifications", json={"user_ids": [], "message": "x"},
                      headers=h(tokens["admin"])).status_code, 422)
    check("mensagem em branco -> 422",
          client.post("/api/notifications", json={"user_ids": [ids["viewer"]], "message": "   "},
                      headers=h(tokens["admin"])).status_code, 422)
    check("severidade invalida -> 422",
          client.post("/api/notifications",
                      json={"user_ids": [ids["viewer"]], "message": "x", "severity": "urgentissimo"},
                      headers=h(tokens["admin"])).status_code, 422)
    check("destinatario inexistente -> 404",
          client.post("/api/notifications", json={"user_ids": [999999], "message": "x"},
                      headers=h(tokens["admin"])).status_code, 404)
    check("alerta inexistente -> 404",
          client.post("/api/notifications",
                      json={"user_ids": [ids["viewer"]], "message": "x", "alert_id": 999999},
                      headers=h(tokens["admin"])).status_code, 404)
    check("conta desativada -> 409",
          client.post("/api/notifications", json={"user_ids": [ids["inativo"]], "message": "x"},
                      headers=h(tokens["admin"])).status_code, 409)

    # Destinatario repetido nao pode virar duas linhas iguais na mesma caixa.
    r = client.post("/api/notifications",
                    json={"user_ids": [ids["operator"], ids["operator"]], "message": "uma vez so"},
                    headers=h(tokens["admin"]))
    check("destinatario duplicado gera 1 linha", len(r.json()), 1)

    print("\n[12] O motor de alertas continua intocado")
    # A Fase 7 nao pode ter mexido no historico tecnico: os alertas seguem
    # sendo listados por /api/alerts, sem campo novo nem filtro por usuario.
    # O alerta do teste foi resolvido em [9], entao ele esta na lista de
    # resolvidos. Confere-se o status ANTES de indexar: um 422 devolve um
    # dict de erro cujo len() tambem e 1 e passaria despercebido.
    r = client.get("/api/alerts?resolved=true", headers=h(tokens["viewer"]))
    check("GET /api/alerts -> 200", r.status_code, 200)
    corpo = r.json()
    check_true("resposta e uma lista", isinstance(corpo, list), type(corpo).__name__)
    check("o alerta do teste continua no historico tecnico", len(corpo), 1)
    check("e o mesmo alerta", corpo[0]["id"], alert_id)
    check_true("alerta nao ganhou campo de usuario", "user_id" not in corpo[0],
               str(sorted(corpo[0].keys())))
    with Session(engine) as s:
        total_notif = len(s.exec(select(Notification)).all())
    check_true("notificacoes vivem em tabela propria", total_notif > 0, f"{total_notif} linha(s)")

    print("\n" + "=" * 70)
    if _falhas:
        print(f"{len(_falhas)} FALHA(S): {_falhas}")
    else:
        print("TODOS OS TESTES PASSARAM")
    print("=" * 70)
    return 1 if _falhas else 0


if __name__ == "__main__":
    raise SystemExit(main())
