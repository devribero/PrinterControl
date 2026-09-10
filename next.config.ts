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

const nextConfig: NextConfig = {
  allowedDevOrigins: origensDeDesenvolvimento(),
};

export default nextConfig;
