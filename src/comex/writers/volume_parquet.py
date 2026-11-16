"""Grava lotes de eventos em Parquet num Volume do Databricks, particionado pela data do evento.

Autenticação pelo databricks-sdk (DATABRICKS_HOST e DATABRICKS_TOKEN no ambiente).
"""
import io
import logging
import uuid
from datetime import UTC, datetime

import pandas as pd
from databricks.sdk import WorkspaceClient

from comex.models import EventoOperacao

log = logging.getLogger(__name__)


class VolumeParquetWriter:
    def __init__(self, volume: str, cliente: WorkspaceClient):
        self.volume = volume.rstrip("/")
        self.cliente = cliente

    def gravar(self, eventos: list[EventoOperacao]) -> list[str]:
        df = pd.DataFrame([e.to_row() for e in eventos])
        dt = df["ts_ms"].map(lambda ms: datetime.fromtimestamp(ms / 1000, UTC).date().isoformat())
        caminhos = []
        for dia, parte in df.groupby(dt):
            caminho = f"{self.volume}/operacao/dt={dia}/{uuid.uuid4().hex}.parquet"
            buf = io.BytesIO()
            parte.to_parquet(buf, index=False)
            buf.seek(0)
            self.cliente.files.upload(caminho, buf, overwrite=False)
            caminhos.append(caminho)
        log.info("%s eventos gravados em %s arquivos", len(df), len(caminhos))
        return caminhos
