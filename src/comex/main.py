"""CLI: python -m comex.main produzir exp | consumir"""
import argparse

from comex.config import get_settings
from comex.extractors import EXTRACTORS
from comex.log import configurar_log
from comex.streaming.consumer import BronzeConsumer
from comex.streaming.producer import OperacaoProducer
from comex.writers.volume_parquet import VolumeParquetWriter


def main() -> None:
    configurar_log()
    p = argparse.ArgumentParser(prog="comex")
    sub = p.add_subparsers(dest="cmd", required=True)
    prod = sub.add_parser("produzir")
    prod.add_argument("fluxo", choices=EXTRACTORS)
    prod.add_argument("--ano", type=int)
    sub.add_parser("consumir")
    args = p.parse_args()
    cfg = get_settings()

    if args.cmd == "produzir":
        extractor = EXTRACTORS[args.fluxo](args.ano or cfg.comex_ano)
        OperacaoProducer(cfg.kafka_bootstrap, cfg.kafka_topic).publicar(extractor.extrair())
    else:
        writer = VolumeParquetWriter(cfg.volume_landing)
        BronzeConsumer(cfg.kafka_bootstrap, cfg.kafka_topic, cfg.kafka_group, writer,
                       cfg.lote_landing).rodar()


if __name__ == "__main__":
    main()
