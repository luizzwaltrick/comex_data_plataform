"""Linha de comando.

    python -m comex simular exp --ano 2024 --limite 10000
    python -m comex consumir
"""
import argparse

from comex.config import Settings, get_settings
from comex.extractors import EXTRACTORS
from comex.log import configurar_log


def _argumentos() -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="comex")
    sub = p.add_subparsers(dest="cmd", required=True)
    sim = sub.add_parser("simular", help="Comex Stat -> Postgres (origem do CDC)")
    sim.add_argument("fluxo", choices=EXTRACTORS)
    sim.add_argument("--ano", type=int)
    sim.add_argument("--limite", type=int, help="grava só as N primeiras linhas")
    sub.add_parser("consumir", help="Kafka (CDC) -> Volume do Databricks")
    return p.parse_args()


def _simular(args: argparse.Namespace, cfg: Settings) -> None:
    import psycopg

    from comex.pipelines import SimulacaoPipeline
    from comex.repositories.operacao_repository import OperacaoRepository

    with psycopg.connect(cfg.postgres_dsn) as conexao:
        SimulacaoPipeline(
            extractor=EXTRACTORS[args.fluxo](args.ano or cfg.comex_ano),
            repositorio=OperacaoRepository(conexao),
        ).executar(args.limite)


def _consumir(cfg: Settings) -> None:
    from databricks.sdk import WorkspaceClient

    from comex.pipelines import BronzePipeline
    from comex.streaming.consumer import BronzeConsumer, criar_consumer
    from comex.streaming.dlq import DlqProducer, criar_producer
    from comex.writers.volume_parquet import VolumeParquetWriter

    BronzePipeline(BronzeConsumer(
        consumer=criar_consumer(cfg.kafka_bootstrap, cfg.kafka_group, cfg.kafka_topic_cdc),
        writer=VolumeParquetWriter(cfg.volume_landing, WorkspaceClient()),
        dlq=DlqProducer(criar_producer(cfg.kafka_bootstrap), cfg.kafka_topic_dlq),
        lote=cfg.lote_landing,
    )).executar()


def main() -> None:
    configurar_log()
    args = _argumentos()
    cfg = get_settings()
    if args.cmd == "simular":
        _simular(args, cfg)
    else:
        _consumir(cfg)
