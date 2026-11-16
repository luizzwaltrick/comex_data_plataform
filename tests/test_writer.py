from unittest.mock import MagicMock

from comex.models import Fluxo, Operacao
from comex.writers.volume_parquet import VolumeParquetWriter


def _op(mes: int) -> Operacao:
    return Operacao(Fluxo.EXPORTACAO, 2024, mes, "02071200", 160, "SC", 1, 10.0, 20.0)


def test_um_arquivo_por_particao():
    cliente = MagicMock()
    caminhos = VolumeParquetWriter("/Volumes/comex/bronze/landing/", cliente).gravar(
        [_op(1), _op(1), _op(2)])
    assert len(caminhos) == 2
    assert caminhos[0].startswith("/Volumes/comex/bronze/landing/operacoes/fluxo=EXP/ano=2024/mes=01/")
    assert cliente.files.upload.call_count == 2
