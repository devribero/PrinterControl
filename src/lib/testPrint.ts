/**
 * Quando o botão "Imprimir página de teste" fica habilitado, e por quê não.
 *
 * Quem decide se o EQUIPAMENTO suporta é o backend (`testPrintSupported`,
 * regra em backend/app/services/test_print.py) — aqui não existe lista de
 * marcas, para as duas pontas não divergirem. Este arquivo só junta essa
 * resposta com o que o painel sabe da sessão (papel, dado real ou demo).
 */
import type { Printer } from "../types";

/** Motivo para o botão ficar desabilitado, ou null quando pode imprimir. */
export function testPrintBlockReason(
  printer: Printer,
  opts: { canOperate: boolean; usingRealData: boolean },
): string | null {
  if (!opts.usingRealData) return "Disponível só com dados reais do servidor.";
  if (!opts.canOperate) return "Ação de operador ou administrador.";
  if (!printer.active) return "Impressora inativa.";
  if (!printer.testPrintSupported) {
    return "Só para impressoras laser. Etiquetadoras usam outra linguagem e ainda não são suportadas.";
  }
  return null;
}
