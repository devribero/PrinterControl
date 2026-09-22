/**
 * Textos do resultado de um teste de webhook do Teams. Compartilhado entre o
 * "Testar alerta" global (NotificationsView) e o teste por unidade
 * (UnitsView): os dois recebem o mesmo `ApiWebhookTestResult`, e o motivo de
 * uma falha precisa ser explicado igual nos dois lugares.
 */
import type { ApiWebhookTestResult } from "./api";

/** Por que o webhook nao recebeu, em linguagem de quem vai corrigir. */
export function motivoFalhaWebhook(detail: string): string {
  if (detail.startsWith("http_")) {
    return `o webhook respondeu erro ${detail.slice(5)} — confira se a URL está completa e ainda é válida`;
  }
  if (detail === "timeout") return "o webhook não respondeu a tempo";
  return "não foi possível alcançar o webhook (rede ou proxy da empresa)";
}

/** Toast do "Testar webhook" de uma unidade. */
export function avisoDoTesteDeUnidade(resultado: ApiWebhookTestResult, unidade: string) {
  if (resultado.sent) {
    return {
      variant: "success" as const,
      title: "Webhook recebeu o teste",
      description: `O card de teste de ${unidade} foi entregue ao canal do Teams.`,
    };
  }
  if (!resultado.configured) {
    return {
      variant: "warning" as const,
      title: "Sem webhook configurado",
      description: `${unidade} não tem webhook próprio — os alertas dela vão só para o canal central.`,
    };
  }
  const motivo = motivoFalhaWebhook(resultado.detail);
  return {
    variant: "warning" as const,
    title: "Webhook não recebeu o teste",
    description: `${motivo.charAt(0).toUpperCase()}${motivo.slice(1)}. Detalhes no log do backend.`,
  };
}
