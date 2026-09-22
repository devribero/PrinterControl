/**
 * Levantamento mensal em Excel — contratos e chamadas de /api/levantamento
 * (backend/app/routes/levantamento.py).
 *
 * O JSON passa por `apiRequest` como o resto do painel. Upload (multipart) e
 * download (arquivo binario) nao cabem nele — `apiRequest` fixa JSON —, entao
 * usam fetch direto, com o MESMO Bearer de `getToken()` e o mesmo ApiError.
 */
import { API_BASE_URL, ApiError, apiRequest, getToken } from "./api";

export interface LevantamentoMes {
  mes: string; // "2026-09"
  nome: string; // "Setembro"
  periodo: string; // "04/09/26 a 03/10/26"
  fechado: boolean;
  em_andamento: boolean;
  preenchido: boolean;
}

export interface LevantamentoArquivo {
  nome: string;
  mes: string | null;
  gerado_em: string | null;
  previa: boolean;
  tipo: "gerado" | "base_anterior";
  automatico: boolean;
  tamanho: number;
}

export interface LevantamentoEstado {
  base: {
    enviada_em: string | null;
    atualizada_em: string | null;
    origem: string | null;
    nome_original: string | null;
    ano: number;
    meses_preenchidos: string[];
  } | null;
  erro_base: string | null;
  arquivos: LevantamentoArquivo[];
  meses: LevantamentoMes[];
  proximo_mes: string | null;
  ultimo_mes_fechado: string | null;
}

export interface LevantamentoLinha {
  unidade: string;
  linha: number;
  celula: string;
  ip: string | null;
  modelo: string | null;
  serial: string | null;
  departamento: string | null;
  motivo: string | null;
  valor?: string;
}

export interface LevantamentoNovo {
  ip: string;
  modelo: string | null;
  serial: string | null;
  servidor: string | null;
  unidade: string | null;
  departamento: string | null;
  tipo: string | null;
  fila: string;
  ativa: boolean;
  paginas: number;
  estimadas: number;
}

export interface LevantamentoRelatorio {
  mes: string;
  mes_nome: string;
  ano: number;
  arquivo: string;
  previa: boolean;
  automatico: boolean;
  gerado_em: string;
  periodo: { texto: string; inicio: string; fim: string; fechado: boolean };
  preenchidas: { linhas: number; paginas: number; estimadas: number };
  vazias: LevantamentoLinha[];
  mantidas: LevantamentoLinha[];
  novos: LevantamentoNovo[];
  correcoes_formula: { celula: string; bloco: string; antes: string | null; depois: string }[];
  base_atualizada: boolean;
  avisos: string[];
}

export interface LevantamentoBaseResultado {
  ano: number;
  meses_preenchidos: string[];
  blocos: number;
  linhas: number;
  backup: string | null;
}

export const fetchLevantamento = (signal?: AbortSignal) =>
  apiRequest<LevantamentoEstado>("/api/levantamento", { signal });

export const gerarLevantamento = (mes: string) =>
  apiRequest<LevantamentoRelatorio>("/api/levantamento/gerar", { method: "POST", body: { mes } });

export const fetchRelatorioLevantamento = (nome: string) =>
  apiRequest<LevantamentoRelatorio>(`/api/levantamento/relatorio/${encodeURIComponent(nome)}`);

function authHeaders(): Record<string, string> {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function erroDaResposta(res: Response): Promise<ApiError> {
  let mensagem = `Erro ${res.status} na requisicao.`;
  try {
    const data = (await res.json()) as { detail?: unknown };
    if (typeof data?.detail === "string") mensagem = data.detail;
  } catch {
    /* corpo nao e JSON */
  }
  return new ApiError(res.status, mensagem);
}

/** Envia uma nova planilha base (.xlsx). Admin. */
export async function enviarBaseLevantamento(arquivo: File): Promise<LevantamentoBaseResultado> {
  const form = new FormData();
  form.append("arquivo", arquivo);
  let res: Response;
  try {
    res = await fetch(`${API_BASE_URL}/api/levantamento/base`, { method: "POST", headers: authHeaders(), body: form });
  } catch {
    throw new ApiError(0, "Nao foi possivel conectar ao servidor. Verifique se o backend esta rodando.");
  }
  if (!res.ok) throw await erroDaResposta(res);
  return (await res.json()) as LevantamentoBaseResultado;
}

/**
 * Baixa um arquivo da lista: fetch com o token -> blob -> <a download>. Um
 * link direto nao serviria: o navegador nao envia o Bearer num href.
 */
export async function baixarArquivoLevantamento(nome: string): Promise<void> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE_URL}/api/levantamento/arquivos/${encodeURIComponent(nome)}`, {
      headers: authHeaders(),
    });
  } catch {
    throw new ApiError(0, "Nao foi possivel conectar ao servidor. Verifique se o backend esta rodando.");
  }
  if (!res.ok) throw await erroDaResposta(res);
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = nome;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}
