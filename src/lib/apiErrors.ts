"use client";

/**
 * Tratamento padronizado de erro de API nas telas administrativas.
 *
 * A regra vem da Fase 2 e não pode divergir entre telas:
 *
 *   401 -> a sessão morreu (token inválido/expirado). Volta ao estado
 *          anônimo pelo mesmo caminho do logout.
 *   403 -> papel insuficiente ou conta desativada. **Continua logado** —
 *          nunca deslogar por 403.
 *   resto -> avisa e segue.
 *
 * Devolve a mensagem já exibível, para a tela poder mostrá-la inline (num
 * formulário, num painel de resultado) além do toast.
 */
import { useCallback } from "react";
import { ApiError } from "./api";
import { useAppData } from "./app-data";
import { useToast } from "./toast";

export function useApiErrorReporter() {
  const { handleLogout } = useAppData();
  const { push } = useToast();

  return useCallback(
    (error: unknown, titulo: string): string => {
      if (error instanceof ApiError && error.status === 401) {
        handleLogout();
        push({
          variant: "warning",
          title: "Sessão expirada",
          description: "Faça login novamente para continuar.",
        });
        return "Sessão expirada.";
      }

      const mensagem = error instanceof Error ? error.message : "Erro inesperado.";
      if (error instanceof ApiError && error.status === 403) {
        push({ variant: "warning", title: "Sem permissão", description: mensagem });
      } else {
        push({ variant: "warning", title: titulo, description: mensagem });
      }
      return mensagem;
    },
    [handleLogout, push],
  );
}
