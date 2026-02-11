from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/solana_swap_dex"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: list[str] = Field(default=["http://localhost:3000", "http://localhost:8080"])

    # Jupiter
    jupiter_api_url: str = "https://quote-api.jup.ag/v6"

    # Signal Processing
    signal_cooldown_seconds: int = 300
    signal_max_retries: int = 3

    # Logging
    log_level: str = "INFO"
    log_dir: str = "logs"


settings = Settings()
