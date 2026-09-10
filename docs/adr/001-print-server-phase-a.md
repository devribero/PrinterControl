# ADR 001 — Diagnóstico e proteção do Print Server

Status: aceito em 2026-09-10.

Backend permanece Python/FastAPI com comandos inline via powershell.exe,
sem agente, WinRM ou arquivo .ps1 de execução. Main.ps1 não tem dependência
ativa; removê-lo da árvore preserva auditoria no Git sem distribuir legado
executável. Isso não remove o webhook legado do histórico.

Erros terão categoria estável e evidência estruturada; RPC indisponível não
prova firewall nem Spooler parado. Identidade é a do processo (whoami), não
uma afirmação sobre a identidade autenticada no servidor remoto.

Bloquear todo sync com queda estritamente superior a 20% das filas ativas
do host, antes de mutações. Sem bypass. Reduções legítimas também bloqueiam;
quedas graduais e substituições com contagem semelhante não são detectadas.

Diagnóstico real separado do sync, admin e rate limit existentes, sem escrita
no banco. Mock só permitido em development/demo. Se ENVIRONMENT também faltar,
o default development não permite inferir implantação de produção.

Fase B depende de evidência em domínio e nova solicitação do operador.
