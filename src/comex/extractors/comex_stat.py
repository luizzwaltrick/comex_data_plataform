from comex.extractors.base import BaseComexExtractor
from comex.models import Fluxo, Operacao


class ExportacaoExtractor(BaseComexExtractor):
    FLUXO = Fluxo.EXPORTACAO

    def _para_operacao(self, r: dict) -> Operacao:
        return Operacao(**self._base(r))


class ImportacaoExtractor(BaseComexExtractor):
    """Importação traz frete e seguro (base CIF = FOB + frete + seguro)."""
    FLUXO = Fluxo.IMPORTACAO

    def _para_operacao(self, r: dict) -> Operacao:
        return Operacao(**self._base(r), vl_frete=float(r["VL_FRETE"]),
                        vl_seguro=float(r["VL_SEGURO"]))
