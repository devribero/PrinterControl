"use client";

/**
 * Dependências externas: react (useEffect/useState, para o mês selecionado
 * no gráfico) e lucide-react (ícones). Dependências locais: Modal (casca
 * genérica), PrinterStatusBadge, lib/tonerColor (cor de cada canal de toner).
 * O bloco "Impressões por mês" lê printer.monthlyPages — populado a partir
 * da planilha em modo demo, ou do relatório mensal real do backend em
 * produção (ver lib/fetchMonthlyReport.ts).
 */
import { useEffect, useState } from "react";
import { Copy, ExternalLink, FileText, Lightbulb, MonitorDown, Printer as PrinterIcon } from "lucide-react";
import type { Printer } from "../types";
import Modal from "./Modal";
import PrinterStatusBadge from "./PrinterStatusBadge";
import { tonerChannelColor } from "../lib/tonerColor";
import { useToast } from "../lib/toast";
import { useTheme } from "../lib/theme";
import { useAppData } from "../lib/app-data";
import { installPath, isGenericDriver } from "../lib/printerInstall";
import { testPrintBlockReason } from "../lib/testPrint";
import { cn } from "../lib/cn";
import styles from "./PrinterDetailsModal.module.css";

interface PrinterDetailsModalProps {
  printer: Printer | null;
  onClose: () => void;
}

/**
 * Copia texto para a área de transferência. A API moderna só existe em
 * contexto seguro (HTTPS ou localhost) — aberto pelo IP da rede
 * (http://10.x.x.x:3000) `navigator.clipboard` nem existe, então cai no
 * método antigo com um campo temporário.
 */
async function copiarTexto(texto: string): Promise<boolean> {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(texto);
      return true;
    }
  } catch {
    // cai no método antigo abaixo
  }
  const campo = document.createElement("textarea");
  campo.value = texto;
  campo.setAttribute("readonly", "");
  campo.style.position = "fixed";
  campo.style.opacity = "0";
  document.body.appendChild(campo);
  campo.select();
  try {
    return document.execCommand("copy");
  } catch {
    return false;
  } finally {
    document.body.removeChild(campo);
  }
}

const IPV4 = /^(\d{1,3}\.){3}\d{1,3}$/;

/**
 * Por que esta impressora não tem gráfico mensal. O histórico sai do
 * contador de páginas lido por SNMP (e da planilha para os meses antigos);
 * sem contador não há o que contar, e o card diz o motivo em vez de sumir.
 */
function motivoSemHistorico(printer: Printer): string {
  if (printer.printerType === "Etiqueta" || printer.printerType === "Portatil") {
    return "Etiquetadoras e portáteis não informam contador de páginas pela rede, então não entram no relatório mensal.";
  }
  if (!IPV4.test(printer.ip)) {
    return `A porta desta fila (${printer.ip}) não tem IP, então não há equipamento para ler o contador.`;
  }
  if (!printer.lastSeenAt || printer.pagesPrinted <= 0) {
    return printer.status === "offline"
      ? "Sem leitura de contador ainda: a impressora não responde a partir do servidor do sistema. O gráfico aparece assim que ela for lida."
      : "Sem leitura de contador ainda: a impressora responde, mas não informou o contador de páginas (SNMP desligado ou sem suporte).";
  }
  return "Contador lido, mas ainda sem leituras suficientes para fechar o mês. O gráfico aparece nas próximas coletas.";
}

function Fact({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className={styles.factLabel}>{label}</p>
      <p className={styles.factValue}>{value}</p>
    </div>
  );
}

export default function PrinterDetailsModal({ printer, onClose }: PrinterDetailsModalProps) {
  const { push } = useToast();
  const { theme } = useTheme();
  const { can, usingRealData, requestTestPrint } = useAppData();
  const [selectedMonth, setSelectedMonth] = useState<string | null>(null);

  useEffect(() => {
    setSelectedMonth(null);
  }, [printer?.id]);

  if (!printer) return null;

  const lowest = printer.toner ? [...printer.toner].sort((a, b) => a.percent - b.percent)[0] : null;
  const needsAttention = lowest && lowest.percent <= 20;
  const doEquipamento = !printer.monthlyPages?.length && !!printer.deviceMonthlyPages?.length;
  const monthly = (printer.monthlyPages?.length ? printer.monthlyPages : printer.deviceMonthlyPages) ?? [];
  const activeMonth = monthly.find((m) => m.month === selectedMonth) ?? monthly[monthly.length - 1] ?? null;
  const maxMonthPages = Math.max(1, ...monthly.map((m) => m.pages));

  // Página de teste real (direto no IP). O pedido fecha este modal e abre a
  // confirmação global (TestPrintDialog, no AppShell) no lugar dele.
  const bloqueioTeste = testPrintBlockReason(printer, { canOperate: can.canOperate, usingRealData });
  const caminho = installPath(printer);

  async function copiarCaminho() {
    if (!caminho) return;
    const ok = await copiarTexto(caminho);
    push(
      ok
        ? { variant: "success", title: "Caminho copiado", description: "Agora Win+R, cole e Enter." }
        : { variant: "warning", title: "Não foi possível copiar", description: "Selecione o caminho e copie com Ctrl+C." },
    );
  }

  return (
    <Modal
      open={!!printer}
      onClose={onClose}
      title={printer.name}
      subtitle={printer.model}
      maxWidth="36rem"
      footer={
        <>
          <button
            onClick={() => requestTestPrint(printer)}
            disabled={bloqueioTeste !== null}
            title={bloqueioTeste ?? "Envia 1 página de teste direto ao IP da impressora"}
            className={styles.footerButton}
          >
            <FileText size={16} />
            Imprimir página de teste
          </button>
          <a href={`http://${printer.ip}`} target="_blank" rel="noreferrer" className={styles.footerLinkPrimary}>
            <ExternalLink size={16} />
            Acessar via web
          </a>
        </>
      }
    >
      <div className={styles.infoCard}>
        <div className={styles.infoIcon}>
          <PrinterIcon size={20} />
        </div>
        <div className={styles.infoText}>
          <p className={styles.infoIp}>{printer.ip}</p>
          <p className={styles.infoDept}>{printer.department}</p>
        </div>
        <PrinterStatusBadge status={printer.status} />
      </div>

      <div className={styles.factsGrid}>
        {/* QA-17: `pagesPrinted` é o `page_count` da última leitura — o
            contador ACUMULADO do equipamento desde que ele existe, não o
            consumo de um período. O rótulo antigo ("Páginas impressas
            (período)") fazia 5.000 páginas de vida inteira aparecerem como
            5.000 páginas do mês, enquanto o gráfico logo abaixo mostrava 0
            para o mesmo mês. O consumo por período continua sendo o bloco
            "Impressões por mês", que vem do relatório mensal. */}
        <Fact label="Contador acumulado" value={printer.pagesPrinted.toLocaleString("pt-BR")} />
        <Fact label="Última atividade" value={printer.lastSeen} />
        <Fact label="Endereço IP" value={printer.ip} />
      </div>

      {/* Fila no print server: driver e como instalar no próprio PC. Só para
          impressora que veio de um servidor — cadastro manual não tem fila. */}
      {printer.server && (
        <div className={styles.queueBlock}>
          <div className={styles.queueFacts}>
            <div>
              <p className={styles.factLabel}>Servidor</p>
              <p className={styles.factValue}>{printer.server}</p>
            </div>
            {printer.driverName && (
              <div>
                <p className={styles.factLabel}>Driver</p>
                <p className={styles.factValue}>
                  {printer.driverName}
                  {isGenericDriver(printer.driverName) && (
                    <span
                      className={styles.genericTag}
                      title="Driver que só repassa texto cru: normal para etiquetadora, suspeito para impressora A4."
                    >
                      genérico
                    </span>
                  )}
                </p>
              </div>
            )}
          </div>

          {caminho && (
            <div className={styles.installBlock}>
              <p className={styles.installTitle}>
                <MonitorDown size={15} aria-hidden="true" />
                Instalar no meu computador
              </p>
              <div className={styles.installPathRow}>
                <code className={styles.installPath}>{caminho}</code>
                <button type="button" onClick={() => void copiarCaminho()} className={styles.copyButton}>
                  <Copy size={14} aria-hidden="true" />
                  Copiar
                </button>
              </div>
              <p className={styles.installHint}>
                Aperte <kbd>Win</kbd> + <kbd>R</kbd>, cole o caminho e dê Enter. O Windows instala a impressora e
                o driver direto do servidor, sem precisar de administrador.
              </p>
            </div>
          )}
        </div>
      )}

      {monthly.length === 0 && (
        <div className={styles.monthlyBlock}>
          <div className={styles.monthlyHeader}>
            <p className={styles.factLabel}>Impressões por mês</p>
          </div>
          <p className={styles.monthlyEmpty}>{motivoSemHistorico(printer)}</p>
        </div>
      )}

      {monthly.length > 0 && (
        <div className={styles.monthlyBlock}>
          <div className={styles.monthlyHeader}>
            <p className={styles.factLabel}>Impressões por mês</p>
            {activeMonth && (
              <span className={styles.monthlyBadge}>
                {activeMonth.month}: {activeMonth.pages.toLocaleString("pt-BR")}
              </span>
            )}
          </div>
          {activeMonth && <p className={styles.monthlyPeriod}>Período: {activeMonth.period}</p>}
          {doEquipamento && (
            <p className={styles.monthlyPeriod}>
              Mesmo equipamento de outra fila com este IP; o relatório conta o equipamento uma vez.
            </p>
          )}
          <div className={styles.monthlyBars}>
            {monthly.map((m) => {
              const active = activeMonth?.month === m.month;
              return (
                <button
                  key={m.month}
                  onClick={() => setSelectedMonth(m.month)}
                  className={styles.monthlyBarButton}
                  title={`${m.month}: ${m.pages.toLocaleString("pt-BR")} páginas`}
                >
                  <span className={cn(styles.monthlyBarValue, active ? styles.monthlyBarValueActive : styles.monthlyBarValueInactive)}>
                    {m.pages > 999 ? `${Math.round(m.pages / 1000)}k` : m.pages}
                  </span>
                  <div
                    className={cn(styles.monthlyBar, active ? styles.monthlyBarActive : styles.monthlyBarInactive)}
                    style={{ height: `${8 + (m.pages / maxMonthPages) * 64}px` }}
                  />
                  <span className={cn(styles.monthlyBarLabel, active ? styles.monthlyBarLabelActive : styles.monthlyBarLabelInactive)}>
                    {m.month}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {printer.toner && printer.toner.length > 0 && (
        <div className={styles.tonerBlock}>
          <p className={styles.tonerBlockLabel}>Níveis de toner</p>
          <div className={styles.tonerBlockList}>
            {printer.toner.map((t) => {
              const cor = tonerChannelColor(t.color, theme);
              return (
                <div key={t.color}>
                  <div className={styles.tonerRow}>
                    <span className={styles.tonerRowLabel}>
                      <span className={styles.tonerDot} style={{ backgroundColor: cor }} />
                      {t.label}
                    </span>
                    <span className={styles.tonerRowPercent}>{t.percent}%</span>
                  </div>
                  <div className={styles.tonerTrack}>
                    <div className={styles.tonerFill} style={{ width: `${t.percent}%`, backgroundColor: cor }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {needsAttention && lowest && (
        <div className={styles.recommendation}>
          <Lightbulb size={18} className={styles.recommendationIcon} />
          <div>
            <p className={styles.recommendationTitle}>Recomendação</p>
            <p className={styles.recommendationText}>
              O nível de {lowest.label.toLowerCase()} está em {lowest.percent}%. Programe a troca do cartucho
              nos próximos dias para evitar interrupção no departamento {printer.department}.
            </p>
          </div>
        </div>
      )}
    </Modal>
  );
}
