"""Configuração única, lida do ambiente (.env)."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    postgres_dsn: str = "postgresql://comex:comex@localhost:5432/comex"
    kafka_bootstrap: str = "localhost:9092"
    kafka_topic_cdc: str = "cdc.public.operacao"
    kafka_topic_dlq: str = "comex.operacao.dlq"
    kafka_group: str = "comex-bronze"
    # Volume do Unity Catalog (Databricks Free Edition) usado como landing do bronze.
    volume_landing: str = "/Volumes/comex/bronze/landing"
    lote_landing: int = 50_000
    comex_ano: int = 2024


@lru_cache
def get_settings() -> Settings:
    return Settings()
