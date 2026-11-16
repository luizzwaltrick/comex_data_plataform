"""Fluxo comum de download e leitura dos CSVs do Comex Stat."""
import io
import logging
from abc import ABC, abstractmethod
from collections.abc import Iterator

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from comex.models import Fluxo, Operacao

log = logging.getLogger(__name__)


def _sessao() -> requests.Session:
    s = requests.Session()
    retry = Retry(total=5, backoff_factor=2, status_forcelist=(429, 500, 502, 503, 504))
    s.mount("https://", HTTPAdapter(max_retries=retry))
    return s


class BaseComexExtractor(ABC):
    FLUXO: Fluxo
    URL = "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/ncm/{fluxo}_{ano}.csv"
    TIMEOUT = 300
    CHUNK = 100_000

    def __init__(self, ano: int, sessao: requests.Session | None = None):
        self.ano = ano
        self.sessao = sessao or _sessao()

    def baixar(self) -> io.BytesIO:
        url = self.URL.format(fluxo=self.FLUXO.value, ano=self.ano)
        log.info("Baixando %s", url)
        r = self.sessao.get(url, timeout=self.TIMEOUT)
        r.raise_for_status()
        return io.BytesIO(r.content)

    def ler(self, arquivo: io.IOBase) -> Iterator[Operacao]:
        for chunk in pd.read_csv(arquivo, sep=";", dtype={"CO_NCM": str}, chunksize=self.CHUNK,
                                 encoding="latin-1"):
            for linha in chunk.itertuples(index=False):
                yield self._para_operacao(linha._asdict())

    def extrair(self, limite: int | None = None) -> Iterator[Operacao]:
        for i, op in enumerate(self.ler(self.baixar())):
            if limite is not None and i >= limite:
                return
            yield op

    def _base(self, r: dict) -> dict:
        return {"fluxo": self.FLUXO, "ano": int(r["CO_ANO"]), "mes": int(r["CO_MES"]),
                    "co_ncm": str(r["CO_NCM"]).zfill(8), "co_pais": int(r["CO_PAIS"]),
                    "sg_uf": r["SG_UF_NCM"], "co_via": int(r["CO_VIA"]), "co_urf": int(r["CO_URF"]),
                    "kg_liquido": float(r["KG_LIQUIDO"]), "vl_fob": float(r["VL_FOB"])}

    @abstractmethod
    def _para_operacao(self, r: dict) -> Operacao: ...
