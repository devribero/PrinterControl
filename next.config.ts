import type { NextConfig } from "next";
import { hostname } from "node:os";

/**
 * Origens liberadas para o servidor de DESENVOLVIMENTO.
 *
 * O PROBLEMA QUE ISTO RESOLVE
 * ---------------------------
 * O Next bloqueia `/_next/*` vindo de uma origem que não esteja nesta lista.
 * Quando ele bloqueia, os scripts do cliente não carregam, o React nunca
 * hidrata, e a página fica parada no primeiro HTML renderizado — que é a
 * tela "Restaurando sessão...". O sintoma não parece rede: parece a
 * aplicação travada.
 *
 * A lista era um IP fixo (`["10.36.1.34"]`), anotado no dia em que o
 * problema apareceu. O endereço vem de DHCP corporativo; quando o lease
 * mudou para `10.36.1.35`, a tela travou de novo, exatamente igual.
 *
 * COMO O NEXT COMPARA (node_modules/next/dist/server/app-render/csrf-protection.js)
 * --------------------------------------------------------------------------------
 * O padrão é comparado por segmentos separados por ponto, e `*` casa um
 * segmento não vazio. Um IPv4 tem quatro segmentos, então `*.*.*.*` casa com
 * QUALQUER IPv4 — que é o que se quer aqui.
 *
 * `"*"` sozinho NÃO funciona: o matcher recusa padrões de um único segmento
 * curinga de propósito (a guarda `patternParts.length === 1`), justamente
 * para um curinga não valer por um domínio inteiro.
 *
 * ALCANCE E RISCO
 * ---------------
 * `*.*.*.*` libera qualquer IP, e só isso: `evil.com` continua bloqueado,
 * porque tem três segmentos e não quatro. O que se abre é um site hospedado
 * em um IP nu conseguir ler recursos deste servidor de desenvolvimento
 * enquanto ele estiver no ar. É aceitável aqui porque `allowedDevOrigins`
 * não existe em produção — o painel publicado é build estático servido pela
 * Vercel ou pelo Cloudflare Tunnel, e nada desta configuração o alcança.
 *
 * `localhost` e `**.localhost` já são liberados pelo próprio Next; não
 * precisam estar aqui.
 */
function origensDeDesenvolvimento(): string[] {
  const origens = new Set<string>([
    // Qualquer IPv4: o endereço desta máquina pode mudar por DHCP a qualquer
    // momento, e quem abre o painel pode chegar por qualquer interface.
    "*.*.*.*",
  ]);

  // Acesso pelo NOME da máquina (http://NOME-DA-MAQUINA:3000), comum em rede
  // de domínio. Um nome de rótulo único não pode ser coberto por curinga —
  // a mesma guarda que recusa `"*"` recusa qualquer padrão de um segmento —
  // então o nome real entra na lista explicitamente.
  const nome = hostname();
  if (nome) {
    origens.add(nome.toLowerCase());

    // E o FQDN, quando a máquina está em um domínio.
    const sufixo = process.env.USERDNSDOMAIN;
    if (sufixo) origens.add(`${nome}.${sufixo}`.toLowerCase());
  }

  return [...origens];
}

/**
 * Origem do backend do ponto de vista do SERVIDOR Next — nao do navegador.
 *
 * E a diferenca que faz o painel funcionar de outra maquina sem abrir porta
 * nenhuma: quem fala com `127.0.0.1:8000` e o processo do Next, que roda na
 * mesma maquina do backend. O navegador de quem acessa nunca precisa
 * alcancar a 8000 — ele so conhece a 3000.
 */
const BACKEND_ORIGIN = (process.env.BACKEND_ORIGIN?.trim() || "http://127.0.0.1:8000").replace(/\/$/, "");

const nextConfig: NextConfig = {
  allowedDevOrigins: origensDeDesenvolvimento(),

  /**
   * O painel chama a API pelo proprio endereco (`/api/...`, `/health`) e o
   * Next repassa para o backend.
   *
   * O PROBLEMA QUE ISTO RESOLVE
   * ---------------------------
   * Com `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000`, esse endereco ia
   * compilado no bundle: o navegador de OUTRA maquina tentava falar com o
   * proprio localhost dela e nao achava backend nenhum. A tela abria e
   * anunciava "servidor indisponivel" — sintoma que parece backend fora do
   * ar, mas e o painel procurando no lugar errado.
   *
   * A alternativa seria subir o backend em 0.0.0.0 e liberar a porta 8000
   * no firewall. Aqui isso nao e possivel (maquina corporativa, sem
   * permissao para mexer em regra de firewall), e o proxy dispensa as duas
   * coisas: o backend continua so em 127.0.0.1 e nenhuma porta nova e
   * aberta.
   *
   * De quebra, some o CORS: para o navegador as chamadas passam a ser da
   * mesma origem do painel, entao `CORS_ORIGINS` deixa de precisar conhecer
   * cada IP de onde alguem abre a tela.
   *
   * `/health` fica fora de `/api` no backend (main.py inclui `health.router`
   * sem `api_prefix`), por isso tem regra propria — a exata e a com
   * sub-caminho, para pegar `/health/print-server` tambem.
   *
   * ALCANCE: quem alcanca a porta 3000 alcanca a API inteira por ela. E a
   * mesma superficie de expor a 8000, so que por uma porta so — e a
   * autenticacao (JWT) continua valendo em todas as rotas protegidas.
   */
  async rewrites() {
    return [
      { source: "/api/:path*", destination: `${BACKEND_ORIGIN}/api/:path*` },
      { source: "/health", destination: `${BACKEND_ORIGIN}/health` },
      { source: "/health/:path*", destination: `${BACKEND_ORIGIN}/health/:path*` },
    ];
  },
};

export default nextConfig;
