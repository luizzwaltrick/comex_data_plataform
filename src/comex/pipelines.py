"""Encadeia as etapas; as dependências entram pelo construtor (facilita teste)."""
from comex.extractors.base import BaseComexExtractor
from comex.repositories.operacao_repository import OperacaoRepository
from comex.streaming.consumer import BronzeConsumer


class SimulacaoPipeline:
    """Comex Stat -> Postgres. Faz o papel do sistema transacional que o CDC observa."""

    def __init__(self, extractor: BaseComexExtractor, repositorio: OperacaoRepository):
        self.extractor = extractor
        self.repositorio = repositorio

    def executar(self, limite: int | None = None) -> int:
        return self.repositorio.salvar(self.extractor.extrair(limite))


class BronzePipeline:
    """Kafka (eventos de CDC) -> Volume do Databricks."""

    def __init__(self, consumer: BronzeConsumer):
        self.consumer = consumer

    def executar(self) -> None:
        self.consumer.rodar()
