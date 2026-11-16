"""Grava lotes em Parquet particionado por fluxo/ano/mes num Volume do Databricks.

Autenticação pelo databricks-sdk (DATABRICKS_HOST e DATABRICKS_TOKEN no ambiente).
"""
import io
import logging
import uuid
from dataclasses import asdict

import pandas as pd
from databricks.sdk import WorkspaceClient

from comex.models import Operacao

log = logging.getLogger(__name__)


class VolumeParquetWriter:
    def __init__(self, volume: str, cliente: WorkspaceClient | None = None):
        self.volume = volume.rstrip("/")
        self.cliente = cliente or WorkspaceClient()

    def gravar(self, ops: list[Operacao]) -> list[str]:
        df = pd.DataFrame([asdict(o) for o in ops])
        df["fluxo"] = df["fluxo"].astype(str)
        caminhos = []
        for (fluxo, ano, mes), parte in df.groupby(["fluxo", "ano", "mes"]):
            caminho = (f"{self.volume}/operacoes/fluxo={fluxo}/ano={ano}/mes={mes:02d}/"
                       f"{uuid.uuid4().hex}.parquet")
            buf = io.BytesIO()
            parte.to_parquet(buf, index=False)
            buf.seek(0)
            self.cliente.files.upload(caminho, buf, overwrite=False)
            caminhos.append(caminho)
        log.info("%s linhas gravadas em %s arquivos", len(df), len(caminhos))
        return caminhos
