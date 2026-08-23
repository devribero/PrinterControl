import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.database import create_db_and_tables
from app.routes import auth, printers, alerts, collect, servers, users
from app.services.scheduler import shutdown_scheduler, start_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    logging.getLogger("printercontrol").info("Database initialized")
    start_scheduler()
    yield
    shutdown_scheduler()


TAGS_METADATA = [
    {"name": "auth", "description": "Login e dados da conta logada. O token vai no header `Authorization: Bearer <token>`."},
    {"name": "users", "description": "Gestao de contas (Fase 3). Somente admin: listar, criar, alterar papel/nome/senha e ativar/desativar."},
    {"name": "printers", "description": "Cadastro das impressoras, leituras e relatorio mensal. Toda rota exige sessao; cadastro/edicao exigem admin; registrar leitura exige operator."},
    {"name": "alerts", "description": "Alertas gerados automaticamente apos cada coleta (offline e niveis de toner). Leitura exige sessao; resolver/notificar exigem operator."},
    {"name": "collect", "description": "Disparo manual de coleta e estado do agendador. Coleta real exige operator; coleta simulada e o agendador exigem admin."},
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
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Erro nao tratado: o detalhe vai para o log do servidor, o cliente recebe
    apenas uma mensagem generica — stack trace e texto de excecao podem
    revelar caminhos de arquivo e estrutura interna.
    """
    logging.getLogger("printercontrol").exception(
        "Erro nao tratado em %s %s", request.method, request.url.path
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor. Consulte os logs do backend."},
    )

# Rotas
app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(users.router, prefix=settings.api_prefix)
app.include_router(printers.router, prefix=settings.api_prefix)
app.include_router(alerts.router, prefix=settings.api_prefix)
app.include_router(collect.router, prefix=settings.api_prefix)
app.include_router(servers.router, prefix=settings.api_prefix)


@app.get("/")
def read_root():
    return {"message": "Printer Control API - Backend"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
