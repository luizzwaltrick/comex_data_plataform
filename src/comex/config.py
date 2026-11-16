"""Configuração única, lida do ambiente (.env)."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    kafka_bootstrap: str = "localhost:9092"
    kafka_topic: str = "comex.operacoes"
    kafka_group: str = "comex-bronze-s3"
    # Volume do Unity Catalog (Databricks Free Edition) usado como landing do bronze.
    volume_landing: str = "/Volumes/comex/bronze/landing"
    comex_ano: int = 2024
    lote_landing: int = 50_000


@lru_cache
def get_settings() -> Settings:
    return Settings()
