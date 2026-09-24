"""
Envio de e-mail (SMTP) — alerta de toner critico e relatorio mensal
(24/09/2026). Canal paralelo ao webhook do Teams (webhook_notifier.py): os
mesmos eventos, para quem nao acompanha o canal.

Mesmas regras do webhook:
  - NUNCA levanta excecao para quem chama: devolve (enviado, motivo). Um
    SMTP fora do ar nao pode derrubar a coleta nem o scheduler.
  - A senha nunca aparece em log nem em mensagem de erro — so o host.
  - SMTP_HOST vazio = desligado ("nao_configurado"), sem aviso em log a
    cada evento.

Os alertas automaticos saem por uma fila de UMA thread (`enviar_em_segundo_plano`):
um SMTP lento (timeout de 15s) segurava a coleta inteira se o envio fosse
feito na mesma thread que grava as leituras.

Motivos devolvidos: "enviado", "nao_configurado", "sem_destinatarios",
"autenticacao", "recusado", "timeout", "erro_de_rede".
"""
import logging
import smtplib
import socket
import ssl
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from email.message import EmailMessage
from email.utils import formataddr, make_msgid
from html import escape
from pathlib import Path

from sqlmodel import Session, or_, select

from app.config import settings
from app.models.email_recipient import EmailRecipient

logger = logging.getLogger("printercontrol.email")

COLOR_LABELS = {"K": "Preto", "C": "Ciano", "M": "Magenta", "Y": "Amarelo"}

XLSX_MIME = ("application", "vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Uma thread so: os e-mails saem em ordem e nunca abrem varias conexoes
# SMTP ao mesmo tempo (o Gmail/M365 limitam conexoes simultaneas).
_fila = ThreadPoolExecutor(max_workers=1, thread_name_prefix="email")


def _unir(*listas: list[str]) -> list[str]:
    """Junta listas sem repetir endereco (sem diferenciar maiusculas), na ordem."""
    vistos: set[str] = set()
    saida: list[str] = []
    for lista in listas:
        for endereco in lista or []:
            chave = endereco.strip().lower()
            if chave and chave not in vistos:
                vistos.add(chave)
                saida.append(endereco.strip())
    return saida


def alert_recipients(session: Session, unit_id: int | None) -> list[str]:
    """
    Quem recebe o alerta de toner de uma impressora da unidade `unit_id`:
    ALERT_EMAIL_TO do .env + cadastrados sem unidade + os da propria unidade.
    """
    filtro = EmailRecipient.unit_id.is_(None)
    if unit_id is not None:
        filtro = or_(filtro, EmailRecipient.unit_id == unit_id)
    cadastrados = session.exec(
        select(EmailRecipient.email).where(EmailRecipient.kind == "alert", filtro).order_by(EmailRecipient.id)
    ).all()
    return _unir(settings.alert_email_to, list(cadastrados))


def report_recipients(session: Session) -> list[str]:
    """Quem recebe o relatorio mensal: REPORT_EMAIL_TO do .env + cadastrados."""
    cadastrados = session.exec(
        select(EmailRecipient.email).where(EmailRecipient.kind == "report").order_by(EmailRecipient.id)
    ).all()
    return _unir(settings.report_email_to, list(cadastrados))


def _remetente() -> str:
    endereco = (settings.smtp_from or settings.smtp_user).strip()
    # "Nome <endereco>" ja pronto no .env e respeitado como veio.
    if "<" in endereco:
        return endereco
    return formataddr(("PrinterControl", endereco))


def send_email(
    destinatarios: list[str],
    assunto: str,
    texto: str,
    html: str | None = None,
    anexos: list[tuple[str, bytes, tuple[str, str]]] | None = None,
) -> tuple[bool, str]:
    """
    Envia um e-mail. `anexos` = [(nome_do_arquivo, bytes, (maintype, subtype))].

    Os destinatarios vao em Bcc quando sao mais de um: ninguem da lista ve o
    endereco dos outros, e responder "a todos" nao dispara para a empresa.
    """
    if not settings.email_configurado:
        return False, "nao_configurado"
    destinatarios = [d for d in destinatarios if d]
    if not destinatarios:
        return False, "sem_destinatarios"

    msg = EmailMessage()
    msg["Subject"] = assunto
    msg["From"] = _remetente()
    if len(destinatarios) == 1:
        msg["To"] = destinatarios[0]
    else:
        msg["To"] = _remetente()
        msg["Bcc"] = ", ".join(destinatarios)
    msg["Message-ID"] = make_msgid(domain="printercontrol")
    msg.set_content(texto)
    if html:
        msg.add_alternative(html, subtype="html")
    for nome, dados, (maintype, subtype) in anexos or []:
        msg.add_attachment(dados, maintype=maintype, subtype=subtype, filename=nome)

    host = settings.smtp_host.strip()
    timeout = settings.smtp_timeout_seconds
    contexto_tls = ssl.create_default_context()
    try:
        if settings.smtp_ssl:
            conexao = smtplib.SMTP_SSL(host, settings.smtp_port, timeout=timeout, context=contexto_tls)
        else:
            conexao = smtplib.SMTP(host, settings.smtp_port, timeout=timeout)
        with conexao as smtp:
            if not settings.smtp_ssl and settings.smtp_starttls:
                smtp.starttls(context=contexto_tls)
            if settings.smtp_user:
                smtp.login(settings.smtp_user, settings.smtp_password)
            smtp.send_message(msg)
    except smtplib.SMTPAuthenticationError:
        logger.warning("E-mail: usuario/senha recusados pelo SMTP | host=%s", host)
        return False, "autenticacao"
    except (smtplib.SMTPRecipientsRefused, smtplib.SMTPSenderRefused, smtplib.SMTPDataError) as e:
        logger.warning("E-mail: SMTP recusou a mensagem | host=%s | %s", host, type(e).__name__)
        return False, "recusado"
    except (socket.timeout, TimeoutError):
        logger.warning("E-mail: timeout falando com o SMTP | host=%s", host)
        return False, "timeout"
    except (OSError, smtplib.SMTPException) as e:
        # OSError cobre DNS, conexao recusada e firewall; SMTPException o
        # resto do protocolo (ex.: servidor sem STARTTLS).
        logger.warning("E-mail: falha de rede/SMTP | host=%s | %s", host, type(e).__name__)
        return False, "erro_de_rede"

    logger.info("E-mail enviado | host=%s | destinatarios=%d | assunto=%s", host, len(destinatarios), assunto)
    return True, "enviado"


def enviar_em_segundo_plano(*args, **kwargs) -> None:
    """send_email na fila de fundo; o resultado so vai para o log."""

    def tarefa():
        try:
            send_email(*args, **kwargs)
        except Exception:  # noqa: BLE001 — defesa extra: nunca derruba a fila
            logger.exception("E-mail: erro inesperado no envio em segundo plano")

    _fila.submit(tarefa)


# ─────────────────────────────────────────────────────────────────────────
#  Mensagens
# ─────────────────────────────────────────────────────────────────────────

def _moldura(titulo: str, cor: str, corpo_html: str) -> str:
    """HTML simples e com estilo inline: e o que Outlook e Gmail renderizam igual."""
    return f"""\
<div style="font-family:Segoe UI,Arial,sans-serif;max-width:560px;margin:0 auto;color:#1f2937">
  <div style="border-left:6px solid {cor};padding:12px 16px;background:#f9fafb">
    <h2 style="margin:0;font-size:18px">{escape(titulo)}</h2>
  </div>
  <div style="padding:16px">{corpo_html}</div>
  <p style="font-size:12px;color:#6b7280;padding:0 16px">
    Mensagem automatica do PrinterControl. Nao responda este e-mail.
  </p>
</div>"""


def _tabela(linhas: list[tuple[str, str]]) -> str:
    celulas = "".join(
        f'<tr><td style="padding:4px 12px 4px 0;color:#6b7280">{escape(k)}</td>'
        f'<td style="padding:4px 0"><b>{escape(v)}</b></td></tr>'
        for k, v in linhas
    )
    return f'<table style="border-collapse:collapse;font-size:14px">{celulas}</table>'


def send_toner_alert_email(
    printer_name: str,
    model: str,
    color: str,
    level_text: str,
    unit_name: str | None = None,
    destinatarios: list[str] | None = None,
) -> None:
    """
    Alerta de toner critico por e-mail, na fila de fundo (nao bloqueia a
    coleta). `destinatarios` vem de alert_recipients() — quem chama tem a
    sessao do banco; None = so ALERT_EMAIL_TO do .env.
    """
    if not settings.email_configurado:
        return
    destinos = _unir(settings.alert_email_to if destinatarios is None else destinatarios)
    if not destinos:
        return

    cor = COLOR_LABELS.get(color, color)
    linhas = [("Impressora", printer_name), ("Modelo", model or "-"), ("Toner", cor), ("Nivel", level_text)]
    if unit_name:
        linhas.insert(1, ("Unidade", unit_name))
    quando = datetime.now().strftime("%d/%m/%Y %H:%M")
    linhas.append(("Detectado em", quando))

    assunto = f"[PrinterControl] Toner {cor} em {level_text} - {printer_name}"
    texto = "Toner critico detectado.\n\n" + "\n".join(f"{k}: {v}" for k, v in linhas)
    html = _moldura(
        "Toner critico",
        "#dc2626",
        "<p>Um cartucho chegou ao nivel critico e precisa ser trocado em breve.</p>" + _tabela(linhas),
    )
    enviar_em_segundo_plano(destinos, assunto, texto, html)


def send_monthly_report_email(
    relatorio: dict,
    caminho_planilha: Path | None,
    destinatarios: list[str] | None = None,
) -> tuple[bool, str]:
    """
    Relatorio mensal (levantamento) com a planilha em anexo. `destinatarios`
    vem de report_recipients(); None = so REPORT_EMAIL_TO do .env.
    Sincrono: roda no job mensal do scheduler, que nao tem pressa.
    """
    if not settings.email_configurado:
        return False, "nao_configurado"
    destinos = _unir(settings.report_email_to if destinatarios is None else destinatarios)
    if not destinos:
        return False, "sem_destinatarios"

    # Formato de levantamento._gerar: "preenchidas" e {"linhas", "paginas", ...}.
    mes = str(relatorio.get("mes") or relatorio.get("arquivo") or "")
    periodo = (relatorio.get("periodo") or {}).get("texto") or mes
    preenchidas = relatorio.get("preenchidas") or {}
    paginas = preenchidas.get("paginas")
    linhas = [
        ("Periodo", periodo),
        ("Impressoras com leitura", str(preenchidas.get("linhas", "-"))),
        ("Paginas impressas", f"{paginas:,}".replace(",", ".") if isinstance(paginas, int) else "-"),
        ("Sem leitura no periodo", str(len(relatorio.get("vazias") or []))),
        ("Impressoras novas", str(len(relatorio.get("novos") or []))),
    ]
    anexos = []
    if caminho_planilha and caminho_planilha.is_file():
        anexos.append((caminho_planilha.name, caminho_planilha.read_bytes(), XLSX_MIME))

    assunto = f"[PrinterControl] Relatorio mensal de impressoes - {mes}"
    texto = (
        "Segue o levantamento mensal de impressoes"
        + (" em anexo" if anexos else " (planilha indisponivel - baixe pelo painel)")
        + ".\n\n"
        + "\n".join(f"{k}: {v}" for k, v in linhas)
    )
    html = _moldura(
        f"Relatorio mensal - {mes}",
        "#2563eb",
        "<p>Segue o levantamento mensal de impressoes"
        + (" em anexo." if anexos else ". A planilha nao foi encontrada; baixe pelo painel.")
        + "</p>"
        + _tabela(linhas),
    )
    return send_email(destinos, assunto, texto, html, anexos)


def send_test_email(destinatario: str, requested_by: str) -> tuple[bool, str]:
    """E-mail de teste (botao nas Configuracoes). Sincrono: a tela espera o resultado."""
    quando = datetime.now().strftime("%d/%m/%Y %H:%M")
    linhas = [("Pedido por", requested_by), ("Enviado em", quando), ("Servidor SMTP", settings.smtp_host)]
    texto = "TESTE - se voce recebeu esta mensagem, o e-mail do PrinterControl esta funcionando.\n\n" + "\n".join(
        f"{k}: {v}" for k, v in linhas
    )
    html = _moldura(
        "TESTE - e-mail do PrinterControl",
        "#16a34a",
        "<p>Se voce recebeu esta mensagem, o envio de e-mail esta funcionando. "
        "Nenhuma impressora esta com problema.</p>" + _tabela(linhas),
    )
    return send_email([destinatario], "[PrinterControl] TESTE de e-mail", texto, html)


def status() -> dict:
    """
    Resumo para a tela de Configuracoes — nunca inclui a senha. As listas do
    .env aparecem inteiras: sao so leitura no painel (mudam no servidor).
    """
    return {
        "configured": settings.email_configurado,
        "smtp_host": settings.smtp_host.strip(),
        "sender": (settings.smtp_from or settings.smtp_user).strip(),
        "env_alert_recipients": list(settings.alert_email_to),
        "env_report_recipients": list(settings.report_email_to),
    }
