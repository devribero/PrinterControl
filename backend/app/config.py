from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings
from pathlib import Path


# Raiz do backend (…/backend), independente de onde o uvicorn foi iniciado.
BACKEND_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = BACKEND_DIR / "printer_control.db"


# Valor historico do secret_key. Continua sendo o default para nao quebrar o
# ambiente de desenvolvimento, mas e explicitamente recusado em producao.
DEV_SECRET_KEY = "dev-secret-key-change-in-production"
MIN_PRODUCTION_SECRET_LENGTH = 32


class Settings(BaseSettings):
    # Ambiente de execucao: "development" (padrao, local) ou "production".
    # Em producao a validacao de seguranca abaixo passa a ser obrigatoria.
    environment: str = "development"

    # Database — caminho ABSOLUTO de proposito: com um caminho relativo o
    # SQLite seguiria o cwd e um `uvicorn` iniciado da raiz do projeto criaria
    # um banco vazio no lugar errado.
    database_url: str = f"sqlite:///{DEFAULT_DB_PATH.as_posix()}"

    # JWT
    secret_key: str = DEV_SECRET_KEY
    algorithm: str = "HS256"
    access_token_expire_hours: int = 24

    # SNMP
    snmp_community: str = "public"
    snmp_timeout: float = 1.5
    snmp_retries: int = 1

    # Coleta simulada: habilita mode="mock" em /api/collect.
    # Deve permanecer False em producao — com ele ligado a API grava
    # leituras ficticias no banco como se fossem reais.
    allow_mock_collect: bool = False

    # Coleta agendada (APScheduler, dentro do proprio FastAPI)
    collection_enabled: bool = False
    collection_interval_minutes: int = 5
    # "real" = SNMP de verdade; "mock" = cenario simulado (exige allow_mock_collect)
    collection_mode: str = "real"
    # Ids das impressoras coletadas a cada ciclo, separados por virgula.
    # LEGADO (Etapa 5): desde que o scheduler passou a coletar toda a frota
    # ativa (active=True), este campo nao e mais lido pelo scheduler. Mantido
    # sem uso conhecido fora daqui para nao remover configuracao existente
    # sem necessidade comprovada.
    collection_printer_ids: str = "1"
    # Cenario usado quando collection_mode="mock"
    collection_scenario: str = "online_mono"
    # Paralelismo da coleta de frota (Etapa 5): consultas de rede/SNMP por
    # IP unico rodam em ate N threads simultaneas. A persistencia no banco
    # continua sequencial, numa unica Session no thread principal.
    collection_max_workers: int = 4

    # ------------------------------------------------------------------
    # Print Server (Etapa 3) — fonte real das impressoras, como no Main.ps1
    # (Get-Printer -ComputerName / Get-PrinterPort -ComputerName).
    # "mock" simula o retorno sem tocar em rede/Windows; "real" dispara
    # PowerShell via subprocess contra print_server_host.
    # ------------------------------------------------------------------
    print_server_mode: str = "mock"
    print_server_host: str = "elgjunprt"
    print_server_timeout_seconds: int = 30

    # ------------------------------------------------------------------
    # Webhook de alerta critico de toner (Etapa 6), equivalente a
    # Send-AlertaWebhook do Main.ps1 (Adaptive Card via Power Automate/Teams).
    # Vazio = desabilitado — nunca commitar a URL real aqui nem em .env.example.
    # ------------------------------------------------------------------
    webhook_url: str = ""
    webhook_timeout_seconds: float = 5.0

    @property
    def is_production(self) -> bool:
        return self.environment.strip().lower() == "production"

    @model_validator(mode="after")
    def _validate_production_secrets(self) -> "Settings":
        """
        Impede que um ambiente de producao suba silenciosamente com o secret
        de desenvolvimento. Em development nada muda — o default continua
        valendo, apenas fica claramente identificado como tal.
        """
        if not self.is_production:
            return self

        if self.secret_key == DEV_SECRET_KEY or not self.secret_key.strip():
            raise ValueError(
                "SECRET_KEY invalida para ENVIRONMENT=production: defina uma chave "
                "propria (ex.: `python -c \"import secrets;print(secrets.token_urlsafe(48))\"`). "
                "O valor de desenvolvimento e publico e permitiria forjar JWTs."
            )

        if len(self.secret_key) < MIN_PRODUCTION_SECRET_LENGTH:
            raise ValueError(
                f"SECRET_KEY muito curta para producao: use ao menos "
                f"{MIN_PRODUCTION_SECRET_LENGTH} caracteres."
            )

        return self

    @field_validator("database_url")
    @classmethod
    def _absolute_sqlite_path(cls, value: str) -> str:
        """
        Normaliza um DATABASE_URL sqlite relativo (ex.: sqlite:///./x.db) para
        um caminho absoluto sob backend/, para que o banco seja sempre o mesmo
        arquivo, nao importa o cwd de quem iniciou o servidor.
        """
        prefix = "sqlite:///"
        if not value.startswith(prefix):
            return value

        raw = value[len(prefix) :]
        if not raw or raw.startswith("/"):  # ":memory:" ou ja absoluto no POSIX
            return value

        path = Path(raw)
        if path.is_absolute():
            return value

        return f"{prefix}{(BACKEND_DIR / path).resolve().as_posix()}"

    @property
    def collection_printer_id_list(self) -> list[int]:
        return [int(p) for p in self.collection_printer_ids.split(",") if p.strip()]

    # API
    api_prefix: str = "/api"
    cors_origins: list = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ]

    class Config:
        # Caminho absoluto pelo mesmo motivo do database_url: um `.env`
        # relativo so seria encontrado se o servidor fosse iniciado de dentro
        # de backend/, e o resto das configuracoes cairia silenciosamente no
        # default (scheduler desligado, mock bloqueado...).
        env_file = str(BACKEND_DIR / ".env")
        case_sensitive = False


settings = Settings()
