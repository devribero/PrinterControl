"""
Notificacao de alerta critico via webhook (Etapa 6).

Equivalente a Send-AlertaWebhook do Main.ps1: Adaptive Card MS Teams/Power
Automate, mesma estrutura (Container + TextBlock + FactSet), disparado
quando um alerta de toner nasce ou escala para critico.

Seguranca: a URL do webhook vem exclusivamente de settings.webhook_url (env).
Nunca aparece em log ou mensagem de excecao — so o host (via httpx.URL) e
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


def send_toner_alert_webhook(
    printer_name: str,
    model: str,
    color: str,
    level_text: str,
    manual: bool = False,
) -> bool:
    """
    Envia o Adaptive Card ao webhook configurado. Nunca levanta excecao —
    retorna False em qualquer falha (desabilitado, timeout, erro HTTP, rede).

    Args:
        color: sigla ("K","C","M","Y") ou ja um rotulo pronto.
        level_text: texto do nivel, ex. "8%".
        manual: True para o disparo do endpoint manual (card "bom"/informativo).
    """
    webhook_url = settings.webhook_url
    if not webhook_url:
        logger.debug("Webhook desabilitado (WEBHOOK_URL vazio) — notificacao ignorada.")
        return False

    color_label = COLOR_LABELS.get(color, color)
    card = _build_adaptive_card(printer_name, model, color_label, level_text, manual)

    try:
        response = httpx.post(
            webhook_url,
            json=card,
            timeout=settings.webhook_timeout_seconds,
            headers={"Content-Type": "application/json; charset=utf-8"},
        )
        if response.status_code >= 400:
            logger.warning(
                "Webhook respondeu erro | host=%s status=%s impressora=%s",
                _safe_host(webhook_url),
                response.status_code,
                printer_name,
            )
            return False

        logger.info("Webhook enviado com sucesso | host=%s impressora=%s", _safe_host(webhook_url), printer_name)
        return True

    except httpx.TimeoutException:
        logger.warning("Timeout ao enviar webhook | host=%s impressora=%s", _safe_host(webhook_url), printer_name)
        return False
    except Exception as exc:
        logger.warning(
            "Falha ao enviar webhook | host=%s impressora=%s erro=%s",
            _safe_host(webhook_url),
            printer_name,
            type(exc).__name__,
        )
        return False
