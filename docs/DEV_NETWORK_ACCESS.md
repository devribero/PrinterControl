# Correção do acesso por IP em desenvolvimento

## Design — 2026-09-08

O Next.js bloqueia recursos `/_next/*` requisitados pela origem `10.36.1.34`.
Sem os scripts do cliente, a tela inicial pode permanecer em “Restaurando sessão”.
Adicionar esse host explicitamente a `allowedDevOrigins` em `next.config.ts`.
É um ajuste de configuração de desenvolvimento, sem mudança arquitetural.

## Roadmap e backlog desta correção

- [x] Diagnosticar o bloqueio e registrar o design.
- [x] Liberar o host `10.36.1.34` em desenvolvimento.
- [x] Validar o carregamento da configuração e executar o lint.
- [ ] Confirmar no navegador após reiniciar o servidor.

## Operação e critérios de aceite

Validação automatizada: importação de `next.config.ts` pelo Node com assert da
lista de hosts aprovada. `npm run lint` passou com sete avisos de Fast Refresh
em arquivos existentes. A confirmação da sessão no navegador permanece pendente.

Reiniciar `npm run dev` e abrir `http://10.36.1.34:3000` com recarga completa
(`Ctrl+F5`). Os scripts `/_next/static/*` e a conexão `/_next/hmr` não devem
mais apresentar bloqueio de origem para esse IP. Sem sessão salva, deve aparecer
o login; com sessão válida e backend disponível, deve aparecer o painel.
Se o IP mudar, atualizar a lista explícita e reiniciar o servidor.

O 404 de `/data/monthly-report.json` é tratado pelo fallback do relatório e é
independente do bloqueio dos scripts. Se houver falhas de API após a recarga,
verificar separadamente a URL pública da API e o CORS do backend.

Referência: https://nextjs.org/docs/app/api-reference/config/next-config-js/allowedDevOrigins
