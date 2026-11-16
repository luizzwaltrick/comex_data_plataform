import json
from unittest.mock import MagicMock

import pytest

from comex.streaming.consumer import BronzeConsumer
from comex.streaming.dlq import DlqProducer


class Msg:
    def __init__(self, valor: bytes | None, offset: int = 0):
        self._valor, self._offset = valor, offset

    def value(self): return self._valor
    def key(self): return b"k"
    def offset(self): return self._offset
    def error(self): return None


def _consumer(mensagens: list, lote: int = 100):
    kafka = MagicMock()
    kafka.poll.side_effect = [*mensagens, None, None, None]
    writer = MagicMock()
    producer = MagicMock()
    dlq = DlqProducer(producer, "dlq")
    return BronzeConsumer(kafka, writer, dlq, lote), kafka, writer, producer


def test_valido_vai_para_o_bronze_e_invalido_para_a_dlq(evento_cdc):
    bom = Msg(json.dumps(evento_cdc).encode())
    ruim = Msg(json.dumps(evento_cdc | {"co_ncm": "1"}).encode())
    lixo = Msg(b"nao-e-json")
    consumer, kafka, writer, producer = _consumer([bom, ruim, lixo, Msg(None)])
    gravados = []
    writer.gravar.side_effect = lambda eventos: gravados.extend(e.id for e in eventos)

    consumer.rodar()

    assert gravados == [42]
    assert producer.produce.call_count == 2
    assert "motivo" in producer.produce.call_args.kwargs["headers"]
    kafka.commit.assert_called_once_with(asynchronous=False)
    kafka.close.assert_called_once()


def test_offset_so_e_confirmado_depois_de_gravar(evento_cdc):
    consumer, kafka, writer, _ = _consumer([Msg(json.dumps(evento_cdc).encode())])
    writer.gravar.side_effect = RuntimeError("volume fora do ar")

    with pytest.raises(RuntimeError):
        consumer.rodar()

    kafka.commit.assert_not_called()
    kafka.close.assert_called_once()


def test_sem_mensagem_nao_faz_commit():
    consumer, kafka, writer, _ = _consumer([])
    consumer.rodar()
    writer.gravar.assert_not_called()
    kafka.commit.assert_not_called()
