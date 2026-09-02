import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.config import settings
from app.database import create_db_and_tables, engine
from app.logging_config import setup_logging
from app.routes import audit_log, auth, printers, alerts, collect, servers, users, notifications, ping
from app.services.scheduler import scheduler_status, shutdown_scheduler, start_scheduler

setup_logging()

logger = logging.getLogger("printercontrol")

APP_VERSION = "0.1.0"

#: Momento em que o processo subiu — usado por /health para reportar uptime.
#: Serve para detectar reinicio em laco: um uptime que nunca passa de poucos
#: minutos significa que o servico esta caindo e sendo reerguido.
_INICIADO_EM = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "Subindo | ambiente=%s print_server=%s scheduler=%s",
        settings.environment,
        settings.print_server_mode,
        settings.collection_enabled,
    )
    create_db_and_tables()
    logger.info("Database initialized")
    start_scheduler()
    yield
    logger.info("Encerrando")
    shutdown_scheduler()


TAGS_METADATA = [
    {"name": "auth", "description": "Login e dados da conta logada. O token vai no header `Authorization: Bearer <token>`."},
    {"name": "users", "description": "Gestao de contas (Fase 3). Somente admin: listar, criar, alterar papel/nome/senha e ativar/desativar."},
    {"name": "printers", "description": "Cadastro das impressoras, leituras e relatorio mensal. Toda rota exige sessao; cadastro/edicao exigem admin; registrar leitura exige operator."},
    {"name": "alerts", "description": "Alertas gerados automaticamente apos cada coleta (offline e niveis de toner). Leitura exige sessao; resolver/notificar exigem operator."},
    {"name": "collect", "description": "Disparo manual de coleta e estado do agendador. Coleta real exige operator; coleta simulada e o agendador exigem admin."},
        {"name": "notifications", "description": "Caixa pessoal de notificacoes do usuario logado. Admin envia; cada um le a sua."},
    {"name": "servers", "description": "Print Server: descoberta e sincronizacao de impressoras (Get-Printer/Get-PrinterPort). Operacoes administrativas."},
]

DESCRIPTION = """
Backend do painel de monitoramento de impressoras.

**Fluxo:** coleta (SNMP real ou simulada) → `PrinterReading` no SQLite →
motor de alertas → estes endpoints → painel Next.js.

**Autenticacao e permissoes:** faca `POST /api/auth/login`, copie o
`access_token` e use o botao *Authorize* acima. O papel da conta vem em
`GET /api/auth/me`.

* `viewer` — somente leitura
* `operator` — coleta real, resolver/notificar alertas, registrar leituras
* `admin` — usuarios, cadastro de impressoras, discovery/sync, coleta
  simulada e agendador

Sem token -> 401; papel insuficiente ou conta desativada -> 403.

Desde a Fase 2 **todas** as rotas de `/api` exigem sessao — as unicas rotas
publicas sao `POST /api/auth/login`, `GET /` e `GET /health`.

**Ambiente local:** sem acesso a rede das impressoras, use as coletas simuladas
(`mode="mock"` ou `POST /api/collect/fleet`), disponiveis apenas quando
`ALLOW_MOCK_COLLECT=true` no `.env`.
"""

app = FastAPI(
    title="Printer Control API",
    version="0.1.0",
    description=DESCRIPTION,
    openapi_tags=TAGS_METADATA,
    lifespan=lifespan,
)

# CORS — apenas o que o painel local usa de fato. O token vai no header
# Authorization (nao em cookie), entao allow_credentials nao e necessario.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Erro nao tratado: o detalhe vai para o log do servidor, o cliente recebe
    apenas uma mensagem generica — stack trace e texto de excecao podem
    revelar caminhos de arquivo e estrutura interna.
    """
    logger.exception("Erro nao tratado em %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor. Consulte os logs do backend."},
    )

# Rotas
app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(users.router, prefix=settings.api_prefix)
app.include_router(notifications.router, prefix=settings.api_prefix)
app.include_router(printers.router, prefix=settings.api_prefix)
app.include_router(alerts.router, prefix=settings.api_prefix)
app.include_router(collect.router, prefix=settings.api_prefix)
app.include_router(servers.router, prefix=settings.api_prefix)
app.include_router(audit_log.router, prefix=settings.api_prefix)
app.include_router(ping.router, prefix=settings.api_prefix)


@app.get("/")
def read_root():
    return {"message": "Printer Control API - Backend"}


@app.get("/health")
def health_check():
    """
    Saude, identificacao do ambiente (Fase 9) e diagnostico (Fase 10).

    O ambiente sai por aqui, e nao por uma NEXT_PUBLIC_* no build do painel,
    de proposito: a variavel de build descreveria o bundle, nao o servidor a
    que ele acabou se conectando. Um painel compilado como "production" e
    apontado para o backend de demonstracao mentiria com toda a confianca.
    Vindo na resposta, o rotulo e sempre o do backend que respondeu.

    Continua publica (sem token): o painel precisa do rotulo ANTES do login,
    e um monitor externo (Cloudflare, uptime check) tambem nao tem token. Por
    isso o retorno segue sem NADA sensivel — nenhum secret, host de banco,
    caminho de arquivo ou origem de CORS. O que ha de novo aqui e diagnostico
    operacional, nao configuracao:

      status      "ok" ou "degraded" — degraded quando o banco nao responde.
                  Um monitor deve alertar por este campo, e nao so pelo 200.
      uptime      segundos desde que o processo subiu. Um valor que nunca
                  cresce denuncia servico reiniciando em laco.
      database    se um SELECT trivial respondeu agora.
      scheduler   ligado/rodando, para flagrar coleta parada sem ninguem ver.

    Responde 200 mesmo degradado, de proposito: o processo ESTA de pe e
    respondendo, e derrubar o healthcheck faria o supervisor reinicia-lo em
    laco sem corrigir a causa (banco travado, disco cheio). Quem monitora le
    o campo `status`.
    """
    banco_ok = True
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:  # noqa: BLE001
        banco_ok = False
        # exception() e nao error(): sem o traceback nao da para saber se o
        # arquivo sumiu, travou por lock ou o disco encheu.
        logger.exception("Healthcheck: banco nao respondeu")

    try:
        scheduler = scheduler_status()
        scheduler_info = {
            "enabled": scheduler["enabled"],
            "running": scheduler["running"],
            "next_run": scheduler["next_run"],
        }
    except Exception:  # noqa: BLE001
        logger.exception("Healthcheck: estado do scheduler indisponivel")
        scheduler_info = {"enabled": settings.collection_enabled, "running": False, "next_run": None}

    return {
        "status": "ok" if banco_ok else "degraded",
        "version": APP_VERSION,
        "environment": settings.environment,
        "is_demo": settings.is_demo,
        "is_production": settings.is_production,
        # Deixa a interface avisar que leituras ficticias podem estar sendo
        # gravadas, mesmo fora de producao.
        "mock_collect_enabled": settings.allow_mock_collect,
        "print_server_mode": settings.print_server_mode,
        "uptime_seconds": round(time.time() - _INICIADO_EM, 1),
        "database": "ok" if banco_ok else "erro",
        "scheduler": scheduler_info,
    }


if __name__ == "__main__":
    import os

    import uvicorn

    # POR QUE 127.0.0.1 E NAO 0.0.0.0
    # --------------------------------
    # `python -m app.main` existe para desenvolvimento; em producao quem sobe
    # o processo e o servico do Windows (ver docs/OPERATIONS.md), que ja
    # escuta em 127.0.0.1 e publica pela Cloudflare Tunnel. O 0.0.0.0 que
    # estava aqui expunha a API para TODA a rede da empresa no momento em que
    # alguem rodasse este arquivo direto — sem tunel, sem TLS, sem intencao.
    # O host deixou de ser configuravel de proposito: quem precisa expor a
    # API tem o caminho oficial, e este bloco nao deve ser esse caminho.
    HOST = "127.0.0.1"

    # Reload DESLIGADO por padrao. Ele reinicia o processo a cada arquivo
    # salvo — util editando codigo, ruim para qualquer execucao que precise
    # ficar de pe (a coleta agendada morre junto). Ligue explicitamente com
    # DEV_RELOAD=true quando estiver desenvolvendo.
    RELOAD = os.getenv("DEV_RELOAD", "").strip().lower() in {"1", "true", "yes", "sim"}

    uvicorn.run("app.main:app", host=HOST, port=8000, reload=RELOAD)
