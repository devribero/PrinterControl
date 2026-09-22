"use client";

/**
 * Avisos sobre o servidor selecionado: desativado, ou última consulta com
 * falha (motivo legível + mensagem crua recolhida, para quem for depurar).
 */
import type { PrintServer } from "../../types";
import { motivoDaFalha } from "./format";
import shared from "./shared.module.css";

export default function SelectedServerNotice({ server, canAdmin }: { server: PrintServer; canAdmin: boolean }) {
  if (!server.active) {
    return (
      <p className={shared.warnBox}>
        <strong>{server.host}</strong> está desativado: descoberta e sincronização (manual ou automática) não
        rodam contra ele.{" "}
        {canAdmin ? "Use Reativar no menu do cartão para voltar a operar." : "Peça a um administrador para reativá-lo."}
      </p>
    );
  }

  if (server.lastStatus === "error" && server.lastError) {
    const motivo = motivoDaFalha(server.lastError);
    return (
      <div className={shared.errorBox} role="status">
        <strong>Última consulta a {server.host} falhou:</strong> {motivo}
        {motivo !== server.lastError && (
          <details className={shared.rawError}>
            <summary>Mensagem técnica</summary>
            <code>{server.lastError}</code>
          </details>
        )}
      </div>
    );
  }

  return null;
}
