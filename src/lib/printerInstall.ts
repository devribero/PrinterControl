/**
 * Caminho para instalar uma impressora no PC do usuário: \\servidor\compartilhamento.
 *
 * O navegador não consegue instalar impressora sozinho. O que funciona é
 * colar esse caminho no Executar (Win+R): o Windows conecta a fila e baixa
 * o driver do próprio print server (Point and Print). A política de domínio
 * da empresa permite isso para qualquer usuário, sem senha de admin, para os
 * print servers aprovados (análise de 21/09/2026).
 *
 * Por que o nome COMPLETO do servidor (elgjunprt.elgin.com.br): a lista de
 * servidores aprovados na política está nesse formato. Conectar pelo nome
 * curto pode não casar com a lista e pedir elevação.
 *
 * Por que o nome de COMPARTILHAMENTO e não o nome da fila: é o que o
 * Windows resolve no caminho, e os dois diferem em algumas filas. Enquanto o
 * compartilhamento não foi sincronizado, cai no nome da fila.
 */
import type { Printer } from "../types";

const DOMINIO_PADRAO = "elgin.com.br";
const DOMINIO = (process.env.NEXT_PUBLIC_PRINT_SERVER_DOMAIN?.trim() || DOMINIO_PADRAO).replace(/^\.+/, "");

/** Caminho UNC para o Win+R, ou null para impressora sem print server. */
export function installPath(printer: Pick<Printer, "server" | "name" | "shareName">): string | null {
  const servidor = printer.server?.trim();
  if (!servidor) return null;
  const host = servidor.includes(".") ? servidor : `${servidor}.${DOMINIO}`;
  const compartilhamento = printer.shareName?.trim() || printer.name;
  return `\\\\${host}\\${compartilhamento}`;
}

/** Driver genérico que só repassa texto cru — normal em etiquetadora, suspeito em laser. */
export function isGenericDriver(driverName: string | undefined): boolean {
  return /generic\s*\/\s*text/i.test(driverName ?? "");
}
