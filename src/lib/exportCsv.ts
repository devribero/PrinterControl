/**
 * Sem libs externas. Gera CSV client-side (Blob + <a download>) — funciona
 * no app real, mas NÃO num Artifact/preview sandboxado (link de download é
 * bloqueado lá).
 *
 * Formato pensado para o Excel em pt-BR: separador `;` (a vírgula é o
 * separador decimal do locale), BOM UTF-8 (sem ele o Excel lê os acentos
 * como Latin-1) e quebra de linha CRLF. Números saem crus, sem separador de
 * milhar, para o Excel tratá-los como número.
 */
import type { Printer } from "../types";

type Cell = string | number | null | undefined;

const STATUS_LABEL: Record<Printer["status"], string> = {
  online: "Online",
  offline: "Offline",
  atencao: "Atenção",
};

function escapeCell(value: Cell): string {
  if (value === null || value === undefined) return "";
  if (typeof value === "number") return Number.isFinite(value) ? String(value) : "";
  let text = value;
  // Texto que começa com = + - @ vira fórmula no Excel ("injeção de CSV").
  if (/^[=+\-@\t\r]/.test(text)) text = `'${text}`;
  return /[";\r\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
}

function fileStamp(): string {
  const d = new Date();
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}-${pad(d.getHours())}${pad(d.getMinutes())}`;
}

/** Baixa `rows` como CSV. `baseName` sem extensão; o carimbo de data é acrescentado. */
export function downloadCsv(baseName: string, rows: Cell[][]) {
  const csv = rows.map((row) => row.map(escapeCell).join(";")).join("\r\n");
  const blob = new Blob(["﻿" + csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${baseName}-${fileStamp()}.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

/** Cadastro atual das impressoras (botão do Topbar). */
export function exportPrintersCsv(printers: Printer[]) {
  const header = ["Nome", "IP", "Modelo", "Departamento", "Status", "Toner", "Contador acumulado", "Última atividade"];
  const rows: Cell[][] = printers.map((p) => [
    p.name,
    p.ip,
    p.model,
    p.department,
    STATUS_LABEL[p.status],
    p.toner ? p.toner.map((t) => `${t.label}: ${t.percent}%`).join(" | ") : "N/A",
    p.pagesPrinted,
    p.lastSeen,
  ]);
  downloadCsv("impressoras", [header, ...rows]);
}

export interface MonthlyReportCsvInput {
  scopeLabel: string;
  periodLabel: string;
  months: {
    period: string;
    label: string;
    inProgress: boolean;
    pages: number;
    estimated: number | null;
    devices: number;
  }[];
  rows: {
    name: string;
    ip: string;
    model: string;
    department: string;
    unit: string;
    server: string;
    active: boolean;
    byPeriod: Map<string, number>;
    total: number;
  }[];
}

/**
 * Relatório mensal como está na tela: uma linha por equipamento, uma coluna
 * por mês do período escolhido, e as linhas de total/cobertura no fim.
 */
export function exportMonthlyReportCsv({ scopeLabel, periodLabel, months, rows }: MonthlyReportCsvInput) {
  const monthHeaders = months.map((m) => (m.inProgress ? `${m.label} (em andamento)` : m.label));
  const lines: Cell[][] = [
    ["Relatório mensal de páginas por equipamento"],
    ["Escopo", scopeLabel],
    ["Período", periodLabel],
    ["Gerado em", new Date().toLocaleString("pt-BR")],
    [],
    ["Impressora", "IP", "Modelo", "Departamento", "Unidade", "Servidor", "Situação", ...monthHeaders, "Total do período"],
  ];

  for (const r of rows) {
    lines.push([
      r.name,
      r.ip,
      r.model,
      r.department,
      r.unit,
      r.server,
      r.active ? "Ativa" : "Inativa",
      ...months.map((m) => r.byPeriod.get(m.period) ?? null),
      r.total,
    ]);
  }

  const pad: Cell[] = ["", "", "", "", "", ""];
  lines.push([]);
  lines.push(["Total", ...pad, ...months.map((m) => m.pages), months.reduce((s, m) => s + m.pages, 0)]);
  lines.push(["Equipamentos com dado", ...pad, ...months.map((m) => m.devices), null]);
  if (months.every((m) => m.estimated !== null)) {
    lines.push([
      "Páginas estimadas (dias sem coleta)",
      ...pad,
      ...months.map((m) => m.estimated ?? 0),
      months.reduce((s, m) => s + (m.estimated ?? 0), 0),
    ]);
  }

  downloadCsv("relatorio-mensal", lines);
}
