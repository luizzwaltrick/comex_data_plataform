"""Consome o tópico e grava lotes no bronze (Volume do Databricks). Commit do offset só após gravar."""
import logging

from confluent_kafka import Consumer, KafkaError

from comex.models import Operacao
from comex.writers.volume_parquet import VolumeParquetWriter

log = logging.getLogger(__name__)


class BronzeConsumer:
    def __init__(self, bootstrap: str, topico: str, grupo: str, writer: VolumeParquetWriter,
                 lote: int):
        self.writer = writer
        self.lote = lote
        self._c = Consumer({"bootstrap.servers": bootstrap, "group.id": grupo,
                            "enable.auto.commit": False, "auto.offset.reset": "earliest"})
        self._c.subscribe([topico])

    def rodar(self, ocioso_max: int = 3) -> None:
        """Lê até ficar `ocioso_max` polls sem mensagem (modo batch; em produção, laço contínuo)."""
        buffer: list[Operacao] = []
        ocioso = 0
        try:
            while ocioso < ocioso_max:
                msg = self._c.poll(5.0)
                if msg is None:
                    ocioso += 1
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    raise RuntimeError(msg.error())
                ocioso = 0
                buffer.append(Operacao.from_json(msg.value()))
                if len(buffer) >= self.lote:
                    self._descarregar(buffer)
            if buffer:
                self._descarregar(buffer)
        finally:
            self._c.close()

    def _descarregar(self, buffer: list[Operacao]) -> None:
        self.writer.gravar(buffer)
        self._c.commit(asynchronous=False)
        buffer.clear()
