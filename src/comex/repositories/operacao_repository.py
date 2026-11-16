"""Grava operações no Postgres em lotes; cada lote é uma transação."""
import logging
from collections.abc import Iterable
from dataclasses import asdict
from itertools import batched

import psycopg

from comex.models import Operacao
from comex.repositories.queries import UPSERT_OPERACAO

log = logging.getLogger(__name__)


class OperacaoRepository:
    def __init__(self, conexao: psycopg.Connection, lote: int = 5_000):
        self.conexao = conexao
        self.lote = lote

    def salvar(self, operacoes: Iterable[Operacao]) -> int:
        total = 0
        for lote in batched(operacoes, self.lote):
            with self.conexao.transaction(), self.conexao.cursor() as cur:
                cur.executemany(UPSERT_OPERACAO, [self._parametros(o) for o in lote])
            total += len(lote)
            log.info("%s operações gravadas", total)
        return total

    @staticmethod
    def _parametros(o: Operacao) -> dict:
        return asdict(o) | {"fluxo": o.fluxo.value}
