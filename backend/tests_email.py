"""
E-mail (24/09/2026) — alerta de toner, relatorio mensal e teste.

Nao fala com servidor SMTP nenhum: `smtplib.SMTP` e trocado por um falso
que so guarda o que receberia. Nao precisa do backend rodando.

    .\\venv\\Scripts\\python.exe tests_email.py
"""
import io
import logging
import os
import smtplib
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="printercontrol-email-"))
os.environ["DATABASE_URL"] = f"sqlite:///{(_TMP / 'email.db').as_posix()}"
os.environ["ENVIRONMENT"] = "development"
os.environ["PRINT_SERVER_MODE"] = "mock"

from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import Session  # noqa: E402

from app.config import settings  # noqa: E402
from app.database import create_db_and_tables, engine  # noqa: E402
from app.logging_config import RedactSecretsFilter  # noqa: E402
from app.main import app  # noqa: E402
from app.models.user import Role, User  # noqa: E402
from app.services import email_notifier  # noqa: E402
from app.services.auth import hash_password  # noqa: E402

_falhas = []
SENHA_SMTP = "senha-do-smtp-NAO-PODE-VAZAR"


def check(nome, obtido, esperado):
    ok = obtido == esperado
    print(f"  [{'OK  ' if ok else 'FALHA'}] {nome}: {obtido!r}" + ("" if ok else f" (esperado {esperado!r})"))
    if not ok:
        _falhas.append(nome)


class SMTPFalso:
    """Guarda cada conexao; `falha` simula o erro que o servidor daria."""

    enviados: list = []
    conexoes: list = []
    falha: Exception | None = None

    def __init__(self, host, port, timeout=None, **_):
        self.host, self.port = host, port
        self.tls = False
        self.login_feito = None
        SMTPFalso.conexoes.append(self)
        if isinstance(SMTPFalso.falha, OSError):
            raise SMTPFalso.falha

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def starttls(self, context=None):
        self.tls = True

    def login(self, user, password):
        if isinstance(SMTPFalso.falha, smtplib.SMTPAuthenticationError):
            raise SMTPFalso.falha
        self.login_feito = (user, password)

    def send_message(self, msg):
        SMTPFalso.enviados.append(msg)


def configurar(**valores):
    base = dict(
        smtp_host="smtp.exemplo.com", smtp_port=587, smtp_user="impressoras@exemplo.com",
        smtp_password=SENHA_SMTP, smtp_from="", smtp_starttls=True, smtp_ssl=False,
        alert_email_to=["ti@exemplo.com"], report_email_to=["gestor@exemplo.com", "financeiro@exemplo.com"],
    )
    base.update(valores)
    for k, v in base.items():
        setattr(settings, k, v)
    SMTPFalso.enviados, SMTPFalso.conexoes, SMTPFalso.falha = [], [], None


def esperar_fila():
    """Espera a fila de fundo esvaziar (um no-op enfileirado depois de tudo)."""
    email_notifier._fila.submit(lambda: None).result(timeout=10)


smtplib.SMTP = SMTPFalso
smtplib.SMTP_SSL = SMTPFalso

# Captura o log COM o filtro de redacao, como em producao.
_log = io.StringIO()
_handler = logging.StreamHandler(_log)
_handler.addFilter(RedactSecretsFilter())
logging.getLogger("printercontrol").addHandler(_handler)
logging.getLogger("printercontrol").setLevel(logging.INFO)


print("\n[1] Desligado quando SMTP_HOST esta vazio")
configurar(smtp_host="")
check("send_email nao envia", email_notifier.send_email(["a@x.com"], "s", "t"), (False, "nao_configurado"))
email_notifier.send_toner_alert_email("P1", "M", "K", "5%")
esperar_fila()
check("alerta de toner nao abre conexao", len(SMTPFalso.conexoes), 0)

print("\n[2] Envio normal: STARTTLS + login + destinatario")
configurar()
check("enviado", email_notifier.send_email(["a@x.com"], "Assunto", "texto"), (True, "enviado"))
c = SMTPFalso.conexoes[0]
check("porta 587", c.port, 587)
check("STARTTLS ligado", c.tls, True)
check("login com o usuario do .env", c.login_feito, ("impressoras@exemplo.com", SENHA_SMTP))
check("To", SMTPFalso.enviados[0]["To"], "a@x.com")
check("remetente com nome", SMTPFalso.enviados[0]["From"], "PrinterControl <impressoras@exemplo.com>")

print("\n[3] Varios destinatarios vao em copia oculta")
configurar()
email_notifier.send_email(["a@x.com", "b@x.com"], "s", "t")
msg = SMTPFalso.enviados[0]
check("Bcc com os dois", msg["Bcc"], "a@x.com, b@x.com")
check("To nao expoe a lista", "a@x.com" in msg["To"], False)

print("\n[4] Erros viram motivo, nunca excecao")
configurar()
SMTPFalso.falha = smtplib.SMTPAuthenticationError(535, b"bad")
check("senha errada -> autenticacao", email_notifier.send_email(["a@x.com"], "s", "t"), (False, "autenticacao"))
configurar()
SMTPFalso.falha = ConnectionRefusedError()
check("servidor fora -> erro_de_rede", email_notifier.send_email(["a@x.com"], "s", "t"), (False, "erro_de_rede"))
configurar()
SMTPFalso.falha = TimeoutError()
check("timeout -> timeout", email_notifier.send_email(["a@x.com"], "s", "t"), (False, "timeout"))
configurar(alert_email_to=[])
check("sem destinatarios", email_notifier.send_email([], "s", "t"), (False, "sem_destinatarios"))

print("\n[5] Alerta de toner (fila de fundo)")
configurar()
email_notifier.send_toner_alert_email("VLO_Diretoria", "SP 5100", "K", "5%", unit_name="Vila <Olimpia>",
                                      destinatarios=["ti@exemplo.com", "TI@exemplo.com", "unidade@exemplo.com"])
esperar_fila()
check("um e-mail", len(SMTPFalso.enviados), 1)
msg = SMTPFalso.enviados[0]
check("assunto", msg["Subject"], "[PrinterControl] Toner Preto em 5% - VLO_Diretoria")
check("sem endereco repetido (maiusculas)", msg["Bcc"], "ti@exemplo.com, unidade@exemplo.com")
html = msg.get_body(preferencelist=("html",)).get_content()
check("HTML escapado", "Vila &lt;Olimpia&gt;" in html, True)

print("\n[6] Relatorio mensal com a planilha em anexo")
configurar()
planilha = _TMP / "Levantamento Setembro 2026.xlsx"
planilha.write_bytes(b"PK\x03\x04 planilha falsa")
relatorio = {
    "mes": "2026-09", "arquivo": planilha.name, "periodo": {"texto": "04/09 a 03/10"},
    "preenchidas": {"linhas": 70, "paginas": 123456}, "vazias": [1, 2], "novos": [],
}
check("enviado", email_notifier.send_monthly_report_email(relatorio, planilha), (True, "enviado"))
msg = SMTPFalso.enviados[0]
anexos = list(msg.iter_attachments())
check("um anexo", len(anexos), 1)
check("nome do anexo", anexos[0].get_filename(), planilha.name)
check("conteudo do anexo", anexos[0].get_content(), planilha.read_bytes())
check("paginas formatadas", "123.456" in msg.get_body(preferencelist=("plain",)).get_content(), True)
configurar(report_email_to=[])
check("sem lista de relatorio", email_notifier.send_monthly_report_email(relatorio, planilha), (False, "sem_destinatarios"))

print("\n[7] Rotas: status e teste (so admin)")
create_db_and_tables()
with Session(engine) as s:
    for papel, role in (("admin", Role.ADMIN.value), ("viewer", Role.VIEWER.value)):
        s.add(User(email=f"{papel}@teste-email.com", password_hash=hash_password("senha-123456"),
                   name=papel, role=role))
    s.commit()
client = TestClient(app)


def token(papel):
    r = client.post("/api/auth/login", json={"email": f"{papel}@teste-email.com", "password": "senha-123456"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


admin, viewer = token("admin"), token("viewer")
configurar()
r = client.get("/api/notifications/email-status", headers=admin)
check("status 200", r.status_code, 200)
check("status sem senha", SENHA_SMTP in r.text, False)
check("listas do .env", (r.json()["env_alert_recipients"], len(r.json()["env_report_recipients"])), (["ti@exemplo.com"], 2))
check("viewer nao ve status", client.get("/api/notifications/email-status", headers=viewer).status_code, 403)

r = client.post("/api/notifications/test-email", headers=admin)
check("teste vai para quem clicou", (r.status_code, r.json()["sent"], r.json()["to"]), (200, True, "admin@teste-email.com"))
r = client.post("/api/notifications/test-email", json={"to": "outro@exemplo.com"}, headers=admin)
check("teste para outro endereco", r.json()["to"], "outro@exemplo.com")
r = client.post("/api/notifications/test-email", json={"to": "a@x.com\r\nBcc: todos@x.com"}, headers=admin)
check("injecao de cabecalho recusada", r.status_code, 422)
check("viewer nao dispara teste", client.post("/api/notifications/test-email", headers=viewer).status_code, 403)
configurar()
SMTPFalso.falha = smtplib.SMTPAuthenticationError(535, b"bad")
r = client.post("/api/notifications/test-email", headers=admin)
check("falha explicada na resposta", (r.json()["sent"], r.json()["detail"]), (False, "autenticacao"))

print("\n[9] Destinatarios cadastrados pelo painel")
from app.models.unit import Unit  # noqa: E402

with Session(engine) as s:
    manaus, vila = Unit(name="Manaus"), Unit(name="Vila")
    s.add(manaus)
    s.add(vila)
    s.commit()
    manaus_id, vila_id = manaus.id, vila.id

configurar(alert_email_to=["env@exemplo.com"], report_email_to=[])
url = "/api/notifications/email-recipients"
r = client.post(url, json={"email": "Central@Exemplo.com", "kind": "alert"}, headers=admin)
check("adiciona central (minusculo)", (r.status_code, r.json()["email"], r.json()["unit_id"]), (201, "central@exemplo.com", None))
central_id = r.json()["id"]
check("duplicado 409", client.post(url, json={"email": "central@exemplo.com", "kind": "alert"}, headers=admin).status_code, 409)
r = client.post(url, json={"email": "manaus@exemplo.com", "kind": "alert", "unit_id": manaus_id}, headers=admin)
check("adiciona por unidade", (r.status_code, r.json()["unit_name"]), (201, "Manaus"))
check("mesmo e-mail em outra lista ok",
      client.post(url, json={"email": "central@exemplo.com", "kind": "report"}, headers=admin).status_code, 201)
check("relatorio com unidade 400",
      client.post(url, json={"email": "x@exemplo.com", "kind": "report", "unit_id": manaus_id}, headers=admin).status_code, 400)
check("e-mail invalido 422", client.post(url, json={"email": "nao-e-email", "kind": "alert"}, headers=admin).status_code, 422)
check("tipo invalido 422", client.post(url, json={"email": "a@exemplo.com", "kind": "spam"}, headers=admin).status_code, 422)
check("unidade inexistente 404",
      client.post(url, json={"email": "a@exemplo.com", "kind": "alert", "unit_id": 999}, headers=admin).status_code, 404)
check("viewer nao lista", client.get(url, headers=viewer).status_code, 403)
check("viewer nao adiciona", client.post(url, json={"email": "v@exemplo.com", "kind": "alert"}, headers=viewer).status_code, 403)
check("lista tem 3", len(client.get(url, headers=admin).json()), 3)

with Session(engine) as s:
    check("impressora de Manaus: env + central + Manaus",
          email_notifier.alert_recipients(s, manaus_id), ["env@exemplo.com", "central@exemplo.com", "manaus@exemplo.com"])
    check("impressora de Vila: env + central", email_notifier.alert_recipients(s, vila_id), ["env@exemplo.com", "central@exemplo.com"])
    check("impressora sem unidade: env + central", email_notifier.alert_recipients(s, None), ["env@exemplo.com", "central@exemplo.com"])
    check("relatorio: cadastrados", email_notifier.report_recipients(s), ["central@exemplo.com"])

check("remove 204", client.delete(f"{url}/{central_id}", headers=admin).status_code, 204)
check("remove de novo 404", client.delete(f"{url}/{central_id}", headers=admin).status_code, 404)
with Session(engine) as s:
    check("removido nao recebe mais", email_notifier.alert_recipients(s, None), ["env@exemplo.com"])

check("excluir unidade apaga os e-mails dela", client.delete(f"/api/units/{manaus_id}", headers=admin).status_code, 204)
with Session(engine) as s:
    check("ex-Manaus nao virou central", "manaus@exemplo.com" in email_notifier.alert_recipients(s, None), False)
acoes = {a["action"] for a in client.get("/api/audit-log", headers=admin).json()}
check("trilha de auditoria registrou", {"email_recipient.create", "email_recipient.delete"} <= acoes, True)

print("\n[8] A senha do SMTP nunca vai para o log")
logging.getLogger("printercontrol.teste").info("config smtp_password=%s", SENHA_SMTP)
check("senha ausente do log", SENHA_SMTP in _log.getvalue(), False)

print("\n" + "=" * 70)
if _falhas:
    print(f"FALHAS: {_falhas}")
    raise SystemExit(1)
print("TODOS OS TESTES PASSARAM")
print("=" * 70)
