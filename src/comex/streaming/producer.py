"""Publica operações no Kafka (idempotente, com chave NCM-país)."""
import logging
from collections.abc import Iterable

from confluent_kafka import Producer

from comex.models import Operacao

log = logging.getLogger(__name__)


class OperacaoProducer:
    def __init__(self, bootstrap: str, topico: str):
        self.topico = topico
        self.erros = 0
        self._p = Producer({"bootstrap.servers": bootstrap, "enable.idempotence": True,
                            "acks": "all", "compression.type": "zstd", "linger.ms": 50})

    def _callback(self, err, msg) -> None:
        if err:
            self.erros += 1
            log.error("Falha ao entregar %s: %s", msg.key(), err)

    def publicar(self, operacoes: Iterable[Operacao]) -> int:
        n = 0
        for op in operacoes:
            self._p.produce(self.topico, key=op.chave, value=op.to_json(), on_delivery=self._callback)
            self._p.poll(0)
            n += 1
        self._p.flush()
        if self.erros:
            raise RuntimeError(f"{self.erros} mensagens não entregues")
        log.info("%s mensagens publicadas em %s", n, self.topico)
        return n
