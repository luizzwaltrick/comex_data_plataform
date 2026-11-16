"""Dead letter queue: evento inválido vai para um tópico à parte, com o motivo no header."""
import logging

from confluent_kafka import Producer

log = logging.getLogger(__name__)


def criar_producer(bootstrap: str) -> Producer:
    return Producer({"bootstrap.servers": bootstrap, "enable.idempotence": True,
                     "acks": "all", "compression.type": "zstd"})


class DlqProducer:
    def __init__(self, producer: Producer, topico: str):
        self.producer = producer
        self.topico = topico
        self.falhas = 0

    def _callback(self, err, msg) -> None:
        if err:
            self.falhas += 1
            log.error("Falha ao entregar na DLQ: %s", err)

    def enviar(self, chave: bytes | None, valor: bytes | None, motivo: str) -> None:
        self.producer.produce(self.topico, key=chave, value=valor,
                              headers={"motivo": motivo.encode()}, on_delivery=self._callback)
        self.producer.poll(0)

    def confirmar(self) -> None:
        """Garante a entrega antes do commit do offset; senão o evento inválido se perde."""
        self.producer.flush()
        if self.falhas:
            raise RuntimeError(f"{self.falhas} mensagens não entregues na DLQ")
