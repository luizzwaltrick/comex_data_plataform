"""Evento publicado no Kafka: uma linha da base Comex Stat (MDIC)."""
import json
from dataclasses import asdict, dataclass
from enum import StrEnum


class Fluxo(StrEnum):
    EXPORTACAO = "EXP"
    IMPORTACAO = "IMP"


@dataclass(frozen=True, slots=True)
class Operacao:
    fluxo: Fluxo
    ano: int
    mes: int
    co_ncm: str
    co_pais: int
    sg_uf: str
    co_via: int
    kg_liquido: float
    vl_fob: float
    vl_frete: float | None = None
    vl_seguro: float | None = None

    @property
    def chave(self) -> str:
        """Chave de partição: mesmo NCM+país cai na mesma partição (ordem garantida)."""
        return f"{self.co_ncm}-{self.co_pais}"

    def to_json(self) -> bytes:
        return json.dumps(asdict(self), ensure_ascii=False).encode()

    @classmethod
    def from_json(cls, dado: bytes) -> "Operacao":
        d = json.loads(dado)
        d["fluxo"] = Fluxo(d["fluxo"])
        return cls(**d)
