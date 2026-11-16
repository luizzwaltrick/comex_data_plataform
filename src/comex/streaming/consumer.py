"""Consome os eventos de CDC e grava lotes no bronze.

Entrega pelo menos uma vez: o offset só é confirmado depois que o lote está no Volume
e os inválidos estão na DLQ. Se cair no meio, o lote é relido (a silver deduplica).
"""
import json
import logging

from confluent_kafka import Consumer, KafkaError

from comex.models import EventoInvalido, EventoOperacao
from comex.streaming.dlq import DlqProducer
from comex.writers.volume_parquet import VolumeParquetWriter

log = logging.getLogger(__name__)


def criar_consumer(bootstrap: str, grupo: str, topico: str) -> Consumer:
    c = Consumer({"bootstrap.servers": bootstrap, "group.id": grupo,
                  "enable.auto.commit": False, "auto.offset.reset": "earliest"})
    c.subscribe([topico])
    return c


class BronzeConsumer:
    def __init__(self, consumer: Consumer, writer: VolumeParquetWriter, dlq: DlqProducer,
                 lote: int):
        self.consumer = consumer
        self.writer = writer
        self.dlq = dlq
        self.lote = lote

    def rodar(self, ocioso_max: int = 3) -> None:
        """Lê até ficar `ocioso_max` polls sem mensagem (execução agendada, não daemon)."""
        buffer: list[EventoOperacao] = []
        pendente = False
        ocioso = 0
        try:
            while ocioso < ocioso_max:
                msg = self.consumer.poll(5.0)
                if msg is None:
                    ocioso += 1
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    raise RuntimeError(msg.error())
                ocioso = 0
                pendente = True
                self._processar(msg, buffer)
                if len(buffer) >= self.lote:
                    self._descarregar(buffer)
                    pendente = False
            if pendente:
                self._descarregar(buffer)
        finally:
            self.consumer.close()

    def _processar(self, msg, buffer: list[EventoOperacao]) -> None:
        if msg.value() is None:  # tombstone
            return
        try:
            buffer.append(EventoOperacao.from_cdc(json.loads(msg.value())))
        except (EventoInvalido, json.JSONDecodeError) as e:
            log.warning("Evento inválido no offset %s: %s", msg.offset(), e)
            self.dlq.enviar(msg.key(), msg.value(), str(e))

    def _descarregar(self, buffer: list[EventoOperacao]) -> None:
        if buffer:
            self.writer.gravar(buffer)
        self.dlq.confirmar()
        self.consumer.commit(asynchronous=False)
        buffer.clear()
