"""
Notificacao de alerta critico via webhook (Etapa 6).

Equivalente a Send-AlertaWebhook do Main.ps1: Adaptive Card MS Teams/Power
Automate, mesma estrutura (Container + TextBlock + FactSet), disparado
quando um alerta de toner nasce ou escala para critico.

Seguranca: a URL do webhook central vem de settings.webhook_url (env); a de
cada unidade vem do banco (Unit.webhook_url, 21/09/2026). Nenhuma aparece em log ou mensagem de excecao — so o host (via httpx.URL) e
usado nas mensagens de erro, nunca a URL completa (que carrega assinatura).

Idempotencia: NENHUMA nesta etapa. Quem decide "e novo, mande" e o chamador
(alert_engine.evaluate_reading, que so passa acao "created"/"escalated") —
este modulo nao consulta nem grava estado de entrega. Sem coluna nova, sem
tabela nova, conforme decidido para a Etapa 6.

Falha aqui NUNCA pode derrubar a coleta: toda excecao e capturada e vira
False + log seguro, nunca propaga para evaluate_reading/collect_fleet.
"""
import logging
from datetime import datetime

import httpx

from app.config import settings

logger = logging.getLogger("printercontrol.webhook")

COLOR_LABELS = {"K": "Preto", "C": "Ciano", "M": "Magenta", "Y": "Amarelo"}


def _safe_host(url: str) -> str:
    """Host da URL, para logar sem expor path/assinatura."""
    try:
        return httpx.URL(url).host or "?"
    except Exception:
        return "?"


def _build_adaptive_card(
    printer_name: str,
    model: str,
    color_label: str,
    level_text: str,
    manual: bool,
) -> dict:
    """
    Mesmo corpo de Send-AlertaWebhook (Main.ps1:1319): titulo/cor conforme
    manual ou automatico, um FactSet com equipamento/cor/nivel/data.
    """
    titulo = "AVISO MANUAL DE TONER" if manual else "ALERTA CRITICO DE TONER"
    cor_titulo = "Good" if manual else "Attention"
    msg_intro = (
        "Um alerta de suprimento foi disparado manualmente a partir do NOC."
        if manual
        else (
            "Foi detectado um nivel muito baixo de suprimento em uma das "
            "impressoras monitoradas. A substituicao e recomendada em breve "
            "para evitar interrupcoes."
        )
    )

    facts = [
        {"title": "Equipamento:", "value": f"{model} ({printer_name})"},
        {"title": "Cor do Toner:", "value": color_label},
        {"title": "Nivel Atual:", "value": f"**{level_text}**"},
        {"title": "Data do Alerta:", "value": datetime.now().strftime("%d/%m/%Y %H:%M")},
    ]

    return {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "msteams": {"width": "Full"},
                    "body": [
                        {
                            "type": "Container",
                            "style": "good" if manual else "attention",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": titulo,
                                    "weight": "Bolder",
                                    "size": "Large",
                                    "color": cor_titulo,
                                }
                            ],
                        },
                        {"type": "TextBlock", "text": msg_intro, "wrap": True, "spacing": "Medium"},
                        {"type": "FactSet", "spacing": "Medium", "facts": facts},
                    ],
                },
            }
        ],
    }


def _post_card(card: dict, contexto: str, url: str | None = None) -> tuple[bool, str]:
    """
    Envia um Adaptive Card ao webhook. Nunca levanta excecao.

    Devolve (enviado, motivo). `motivo` e um codigo curto e seguro para
    mostrar na interface — nunca a URL, que carrega assinatura:
    "enviado", "nao_configurado", "http_<status>", "timeout", "erro_de_rede".
    `contexto` so entra no log (nome da impressora, "teste"...).

    `url` explicita (webhook de uma unidade, 21/09/2026); None = central
    (`settings.webhook_url`), comportamento de sempre.
    """
    webhook_url = settings.webhook_url if url is None else url
    if not webhook_url:
        logger.debug("Webhook desabilitado (WEBHOOK_URL vazio) — %s ignorado.", contexto)
        return False, "nao_configurado"

    try:
        response = httpx.post(
            webhook_url,
            json=card,
            timeout=settings.webhook_timeout_seconds,
            headers={"Content-Type": "application/json; charset=utf-8"},
        )
        if response.status_code >= 400:
            logger.warning(
                "Webhook respondeu erro | host=%s status=%s contexto=%s",
                _safe_host(webhook_url),
                response.status_code,
                contexto,
            )
            return False, f"http_{response.status_code}"

        logger.info("Webhook enviado com sucesso | host=%s contexto=%s", _safe_host(webhook_url), contexto)
        return True, "enviado"

    except httpx.TimeoutException:
        logger.warning("Timeout ao enviar webhook | host=%s contexto=%s", _safe_host(webhook_url), contexto)
        return False, "timeout"
    except Exception as exc:
        logger.warning(
            "Falha ao enviar webhook | host=%s contexto=%s erro=%s",
            _safe_host(webhook_url),
            contexto,
            type(exc).__name__,
        )
        return False, "erro_de_rede"


def send_toner_alert_webhook(
    printer_name: str,
    model: str,
    color: str,
    level_text: str,
    manual: bool = False,
    unit_url: str | None = None,
) -> bool:
    """
    Envia o Adaptive Card ao webhook configurado. Nunca levanta excecao —
    retorna False em qualquer falha (desabilitado, timeout, erro HTTP, rede).

    Destinos (21/09/2026): o webhook central (`settings.webhook_url`) e, se
    informado, o da unidade da impressora (`unit_url`) — mesma URL recebe
    uma vez so. True se ao menos um recebeu.

    Args:
        color: sigla ("K","C","M","Y") ou ja um rotulo pronto.
        level_text: texto do nivel, ex. "8%".
        manual: True para o disparo do endpoint manual (card "bom"/informativo).
    """
    color_label = COLOR_LABELS.get(color, color)
    card = _build_adaptive_card(printer_name, model, color_label, level_text, manual)
    enviado = False
    for destino in _destinos(unit_url):
        ok, _motivo = _post_card(card, f"impressora={printer_name}", url=destino)
        enviado = enviado or ok
    return enviado


def _destinos(unit_url: str | None) -> list[str]:
    """
    URLs que recebem um alerta de toner: a da unidade (se houver) e a
    central, sem repetir — unidade configurada com a mesma URL da central
    recebe UM card so. Sem nenhuma configurada, devolve [""] para o
    _post_card registrar "nao_configurado" como sempre fez.
    """
    urls: list[str] = []
    for url in ((unit_url or "").strip(), settings.webhook_url or ""):
        if url and url not in urls:
            urls.append(url)
    return urls or [""]


def _build_test_card(requested_by: str, unit_name: str | None = None) -> dict:
    """
    Card do botao "Testar alerta". Diz com todas as letras que e TESTE, no
    titulo e no texto: um card identico ao de toner critico, visto de
    relance no canal, faria alguem correr atras de um cartucho que nao
    acabou.

    Com `unit_name`, e o teste do webhook de uma unidade (21/09/2026): o
    texto diz de qual unidade, para o canal certo reconhecer o card.
    """
    if unit_name:
        texto = (
            f"Este e um alerta de TESTE do webhook da unidade {unit_name}, enviado pela "
            "tela de Unidades. Nenhuma impressora precisa de atencao. Se ele chegou, os "
            f"alertas de toner critico das impressoras de {unit_name} tambem vao chegar "
            "neste canal."
        )
    else:
        texto = (
            "Este e um alerta de TESTE, enviado pelo botao da aba Notificacoes. "
            "Nenhuma impressora precisa de atencao. Se ele chegou, os alertas "
            "de toner critico tambem vao chegar neste canal."
        )
    facts = [{"title": "Enviado por:", "value": requested_by}]
    if unit_name:
        facts.append({"title": "Unidade:", "value": unit_name})
    facts.append({"title": "Data:", "value": datetime.now().strftime("%d/%m/%Y %H:%M")})
    return {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "msteams": {"width": "Full"},
                    "body": [
                        {
                            "type": "Container",
                            "style": "accent",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": "TESTE DE ALERTA - PrinterControl",
                                    "weight": "Bolder",
                                    "size": "Large",
                                }
                            ],
                        },
                        {
                            "type": "TextBlock",
                            "text": texto,
                            "wrap": True,
                            "spacing": "Medium",
                        },
                        {
                            "type": "FactSet",
                            "spacing": "Medium",
                            "facts": facts,
                        },
                    ],
                },
            }
        ],
    }


def send_test_webhook(requested_by: str) -> tuple[bool, str]:
    """Envia o card de teste. Devolve (enviado, motivo) — ver _post_card."""
    return _post_card(_build_test_card(requested_by), "teste")


def send_unit_test_webhook(unit_name: str, url: str, requested_by: str) -> tuple[bool, str]:
    """
    Card de teste SO para o webhook de uma unidade (a central nao recebe).
    Devolve (enviado, motivo) — ver _post_card. URL vazia = "nao_configurado".
    """
    return _post_card(
        _build_test_card(requested_by, unit_name=unit_name),
        f"teste unidade={unit_name}",
        url=url or "",
    )
