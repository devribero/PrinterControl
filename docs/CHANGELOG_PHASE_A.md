# Fase A — Print Server (2026-09-10)

Plano aprovado: remover Main.ps1; categorizar erros e registrar identidade,
tempos e contagens; bloquear sync com queda >20%; reforçar recusa de mock;
adicionar diagnóstico real autenticado independente do modo configurado.

Contrato: queda calculada sobre filas ativas do mesmo servidor, com descoberta
deduplicada. Bloqueio antes de qualquer escrita nas impressoras, HTTP 409 e
log de alerta. Diagnóstico: GET /health/print-server, admin, limite de ações de
rede, HTTP 200/503, identidade, categoria e modo efetivamente consultado.

Implementado: legado removido (histórico Git preservado), erros estruturados
e logs por comando, proteção de sync, validação explícita de modo/timeout e
diagnóstico real com admin/rate limit. Documentação de arquitetura, API e
operação atualizada. Sem migração de banco ou mudança de identidade.

Validação executada: 23 testes da suíte `tests_print_server_phase_a.py`,
incluindo subprocess simulado, SQLite em memória, API e PowerShell Windows
local (JSON Unicode, whoami, cmdlet inexistente, acesso negado simulado por
exceção e saída inválida). Todos passaram.

Regressões aprovadas: `tests_print_server.py`,
`tests_print_server_discovery.py` (6 testes), `tests_printer_sync.py`,
`tests_print_servers.py`, `tests_environment.py`, `tests_production.py`,
`tests_network_rate_limit.py` e `tests_rbac.py`.
O teste antigo de sync passou a esperar bloqueio na queda 3→2. A suíte de
discovery ganhou isolamento de DATABASE_URL, pois herdava configuração de
outro projeto no Windows. A migração foi testada em cópia temporária do banco.

Gaps conhecidos: consulta bem-sucedida ao Print Server do domínio e identidade
remota ainda não validadas; o teste local não comprova permissões de SYSTEM.
O teste best-effort real de `tests_print_server.py` foi pulado em modo mock;
`tests_print_servers.py` exercitou erro DNS no host de teste `srv-filial`.
O limiar não detecta quedas graduais ou trocas com contagem semelhante;
reduções legítimas >20% também bloqueiam. RPC genérico não prova firewall ou
Spooler parado; whoami identifica o processo, não a autenticação remota.
Sem ENVIRONMENT, o default development não detecta produção por inferência.
Avisos preexistentes de depreciação e proxy não foram alterados nesta fase.

Fase B pendente: testar na máquina de domínio usando backend/.env.dominio;
SYSTEM sem permissão continua hipótese. Nenhuma alteração de identidade.
backend/.env de desenvolvimento permanece intacto. READMEs por pasta adiados.
