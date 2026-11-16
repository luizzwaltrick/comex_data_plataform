"""Registros que trafegam pelo pipeline."""
from dataclasses import dataclass
from enum import StrEnum


class Fluxo(StrEnum):
    EXPORTACAO = "EXP"
    IMPORTACAO = "IMP"


@dataclass(frozen=True, slots=True)
class Operacao:
    """Uma linha do Comex Stat, gravada no Postgres como se fosse o sistema transacional."""
    fluxo: Fluxo
    ano: int
    mes: int
    co_ncm: str
    co_pais: int
    sg_uf: str
    co_via: int
    co_urf: int
    kg_liquido: float
    vl_fob: float
    vl_frete: float | None = None
    vl_seguro: float | None = None


class EventoInvalido(ValueError):
    """Evento do CDC que não passa na validação; vai para a DLQ."""


@dataclass(frozen=True, slots=True)
class EventoOperacao:
    """Mudança capturada pelo Debezium na tabela operacao (formato achatado pelo SMT unwrap)."""
    id: int
    op: str            # c = insert, u = update, d = delete, r = carga inicial (snapshot)
    ts_ms: int
    deletado: bool
    operacao: Operacao

    OPS_VALIDAS = frozenset("cudr")

    @classmethod
    def from_cdc(cls, d: dict) -> "EventoOperacao":
        try:
            op = Operacao(
                fluxo=Fluxo(d["fluxo"]), ano=int(d["ano"]), mes=int(d["mes"]),
                co_ncm=str(d["co_ncm"]), co_pais=int(d["co_pais"]), sg_uf=str(d["sg_uf"]),
                co_via=int(d["co_via"]), co_urf=int(d["co_urf"]),
                kg_liquido=float(d["kg_liquido"]), vl_fob=float(d["vl_fob"]),
                vl_frete=_opcional(d.get("vl_frete")), vl_seguro=_opcional(d.get("vl_seguro")),
            )
            evento = cls(id=int(d["id"]), op=str(d["__op"]), ts_ms=int(d["__ts_ms"]),
                         deletado=str(d.get("__deleted", "false")).lower() == "true",
                         operacao=op)
        except (KeyError, TypeError, ValueError) as e:
            raise EventoInvalido(f"evento malformado: {e!r}") from e
        evento._validar()
        return evento

    def _validar(self) -> None:
        o = self.operacao
        if self.op not in self.OPS_VALIDAS:
            raise EventoInvalido(f"op desconhecida: {self.op}")
        if len(o.co_ncm) != 8 or not o.co_ncm.isdigit():
            raise EventoInvalido(f"NCM inválido: {o.co_ncm}")
        if not 1 <= o.mes <= 12:
            raise EventoInvalido(f"mês inválido: {o.mes}")
        if o.vl_fob < 0 or o.kg_liquido < 0:
            raise EventoInvalido("valor ou peso negativo")

    def to_row(self) -> dict:
        o = self.operacao
        return {"id": self.id, "op": self.op, "ts_ms": self.ts_ms, "deletado": self.deletado,
                "fluxo": o.fluxo.value, "ano": o.ano, "mes": o.mes, "co_ncm": o.co_ncm,
                "co_pais": o.co_pais, "sg_uf": o.sg_uf, "co_via": o.co_via, "co_urf": o.co_urf,
                "kg_liquido": o.kg_liquido, "vl_fob": o.vl_fob, "vl_frete": o.vl_frete,
                "vl_seguro": o.vl_seguro}


def _opcional(v) -> float | None:
    return None if v is None else float(v)
