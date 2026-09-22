"use client";

/**
 * Operações administrativas sobre o registro de Print Servers: criar,
 * editar, ativar/desativar e excluir em definitivo.
 *
 * Cada função devolve `null` em caso de sucesso ou a mensagem de erro já
 * exibível — os diálogos a mostram inline, onde dá para corrigir sem perder
 * o que foi digitado (o toast de erro sai pelo useApiErrorReporter).
 */
import { useCallback } from "react";
import {
  createPrintServer,
  deletePrintServer,
  updatePrintServer,
  type PrintServerUpdateInput,
} from "../../lib/api";
import { useApiErrorReporter } from "../../lib/apiErrors";
import { useAppData } from "../../lib/app-data";
import { useToast } from "../../lib/toast";
import type { PrintServer } from "../../types";

/**
 * Estado do formulário de registro/edição.
 *
 * `active` NÃO está aqui de propósito, mesmo padrão do UsersView: desativar
 * um servidor para a operação contra ele e some com a frota do painel, então
 * tem fluxo próprio com confirmação.
 */
export interface ServerFormState {
  host: string;
  name: string;
  mode: "mock" | "real";
  /** Unidade dona do servidor; null = sem unidade. */
  unitId: number | null;
}

export function formInicial(server: PrintServer | null): ServerFormState {
  if (!server) return { host: "", name: "", mode: "mock", unitId: null };
  // `name` cai no host quando vazio (adaptPrintServer); mostrar o host como
  // se fosse rótulo digitado faria o admin "confirmar" um nome que ele não
  // escreveu, então o campo abre vazio nesse caso.
  return {
    host: server.host,
    name: server.name === server.host ? "" : server.name,
    mode: server.mode,
    unitId: server.unitId,
  };
}

export function validarForm(editing: PrintServer | null, form: ServerFormState): string | null {
  if (editing) return null;
  if (!form.host.trim()) return "Informe o host do Print Server.";
  if (/\s/.test(form.host.trim())) return "O host não pode conter espaços.";
  return null;
}

export function useServerAdmin() {
  const { refreshServers, refreshUnits, serverScope, setServerScope } = useAppData();
  const { push } = useToast();
  const relatarErro = useApiErrorReporter();

  const save = useCallback(
    async (editing: PrintServer | null, form: ServerFormState): Promise<string | null> => {
      const invalido = validarForm(editing, form);
      if (invalido) return invalido;
      try {
        if (editing) {
          // Só o que mudou. `host` nunca é enviado — imutável por design.
          const mudancas: PrintServerUpdateInput = {};
          const rotulo = form.name.trim();
          const rotuloAtual = editing.name === editing.host ? "" : editing.name;
          if (rotulo !== rotuloAtual) mudancas.name = rotulo || editing.host;
          if (form.mode !== editing.mode) mudancas.mode = form.mode;
          if (form.unitId !== editing.unitId) mudancas.unit_id = form.unitId;
          if (Object.keys(mudancas).length === 0) return null;

          const atualizado = await updatePrintServer(editing.id, mudancas);
          await Promise.all([refreshServers(), refreshUnits()]);
          push({
            variant: "success",
            title: "Print Server atualizado",
            description: `${atualizado.name || atualizado.host} salvo.`,
          });
        } else {
          const criado = await createPrintServer({
            host: form.host.trim(),
            name: form.name.trim(),
            mode: form.mode,
            ...(form.unitId !== null ? { unit_id: form.unitId } : {}),
          });
          await Promise.all([refreshServers(), refreshUnits()]);
          // Passa a operar sobre o que acabou de registrar.
          setServerScope(criado.host);
          push({
            variant: "success",
            title: "Print Server registrado",
            description:
              form.mode === "real"
                ? `${criado.host} entrou no registro. A primeira sincronização começa automaticamente.`
                : `${criado.host} entrou no registro em modo simulado.`,
          });
        }
        return null;
      } catch (error) {
        // 409 (host duplicado) e 422 (modo inválido) ficam no formulário.
        return relatarErro(error, "Não foi possível salvar");
      }
    },
    [push, refreshServers, refreshUnits, relatarErro, setServerScope],
  );

  const toggleActive = useCallback(
    async (server: PrintServer): Promise<string | null> => {
      try {
        const atualizado = await updatePrintServer(server.id, { active: !server.active });
        await refreshServers();
        push({
          variant: "success",
          title: atualizado.active ? "Print Server reativado" : "Print Server desativado",
          description: atualizado.active
            ? `${server.host} voltou a aceitar descoberta e sincronização.`
            : `${server.host} para de ser consultado. As impressoras seguem no cadastro.`,
        });
        return null;
      } catch (error) {
        return relatarErro(error, "Não foi possível alterar o status");
      }
    },
    [push, refreshServers, relatarErro],
  );

  const remove = useCallback(
    async (server: PrintServer, confirmHost: string): Promise<string | null> => {
      if (confirmHost.trim() !== server.host) return "O host digitado não corresponde ao deste Print Server.";
      try {
        await deletePrintServer(server.id, confirmHost.trim());
        // O escopo apontava para o que acabou de sumir: volta para a frota
        // inteira em vez de deixar o painel num servidor inexistente.
        if (serverScope === server.host) setServerScope(null);
        await Promise.all([refreshServers(), refreshUnits()]);
        push({
          variant: "success",
          title: "Print Server excluído",
          description: `${server.host} e suas impressoras foram apagados em definitivo.`,
        });
        return null;
      } catch (error) {
        return relatarErro(error, "Não foi possível excluir");
      }
    },
    [push, refreshServers, refreshUnits, relatarErro, serverScope, setServerScope],
  );

  return { save, toggleActive, remove };
}
