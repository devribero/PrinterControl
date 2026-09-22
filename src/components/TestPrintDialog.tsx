"use client";

/**
 * Confirmação da página de teste. Montado uma vez no AppShell; abre quando
 * alguém pede o teste pela tabela ou pelo modal de detalhes
 * (`requestTestPrint` no AppDataProvider).
 *
 * Confirmar antes é de propósito: o clique gasta papel numa impressora
 * física, possivelmente em outro prédio, e o botão fica ao lado de outros
 * na linha da tabela.
 *
 * O envio vai direto ao IP (porta 9100), sem passar pela fila do print
 * server — o diálogo e a própria página impressa dizem isso, para ninguém
 * concluir que a fila do Windows está ok a partir deste teste.
 */
import { useState } from "react";
import { Loader2, Printer as PrinterIcon } from "lucide-react";
import Modal from "./Modal";
import { sendTestPrint, type ApiTestPrintResult } from "../lib/api";
import { useApiErrorReporter } from "../lib/apiErrors";
import { useAppData } from "../lib/app-data";
import { useToast } from "../lib/toast";
import type { Printer } from "../types";
import styles from "./TestPrintDialog.module.css";

function avisoDoResultado(printer: Printer, r: ApiTestPrintResult) {
  switch (r.detail) {
    case "enviado":
      return {
        variant: "success" as const,
        title: "Página de teste enviada",
        description: `${printer.name} aceitou o trabalho. Confira se a página saiu — por este caminho não dá para confirmar o papel.`,
      };
    case "porta_fechada":
      return {
        variant: "warning" as const,
        title: "Impressora recusou a conexão",
        description: `A porta 9100 de ${r.ip} está fechada. A impressão direta pode estar desativada no equipamento.`,
      };
    case "sem_resposta":
      return {
        variant: "warning" as const,
        title: `Sem resposta de ${r.ip}`,
        description: "A impressora não respondeu a tempo. Pode estar desligada ou fora da rede.",
      };
    default:
      return {
        variant: "warning" as const,
        title: `Falha de rede ao falar com ${r.ip}`,
        description: "O servidor do painel não conseguiu alcançar a impressora.",
      };
  }
}

export default function TestPrintDialog() {
  const { testPrintTarget: printer, closeTestPrint } = useAppData();
  const { push } = useToast();
  const relatarErro = useApiErrorReporter();
  const [enviando, setEnviando] = useState(false);

  async function confirmar() {
    if (!printer) return;
    setEnviando(true);
    try {
      push(avisoDoResultado(printer, await sendTestPrint(printer.id)));
      closeTestPrint();
    } catch (error) {
      // 422 (não suportada), 409 (inativa), 429 (limite de ações), 403.
      relatarErro(error, "Não foi possível enviar a página de teste");
      closeTestPrint();
    } finally {
      setEnviando(false);
    }
  }

  return (
    <Modal
      open={printer !== null}
      onClose={() => (enviando ? undefined : closeTestPrint())}
      title="Imprimir página de teste?"
      subtitle={printer?.name}
      maxWidth="28rem"
      footer={
        <div className={styles.footer}>
          <button onClick={closeTestPrint} disabled={enviando} className={styles.secondaryButton}>
            Cancelar
          </button>
          <button onClick={() => void confirmar()} disabled={enviando} className={styles.primaryButton}>
            {enviando ? <Loader2 size={15} className="animate-spin" /> : <PrinterIcon size={15} />}
            {enviando ? "Enviando..." : "Imprimir"}
          </button>
        </div>
      }
    >
      {printer && (
        <div className={styles.body}>
          <p>
            Vai sair <strong>1 página</strong> em <strong>{printer.name}</strong> ({printer.ip}), com o nome da
            fila, a data e quem pediu.
          </p>
          <p className={styles.note}>
            O envio é direto ao IP do equipamento: confirma que a impressora recebe trabalhos pela rede, mas não
            passa pela fila do servidor de impressão nem pelo driver.
          </p>
        </div>
      )}
    </Modal>
  );
}
