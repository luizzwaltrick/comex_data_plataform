from unittest.mock import MagicMock

from comex.models import EventoOperacao
from comex.writers.volume_parquet import VolumeParquetWriter

DIA_MS = 86_400_000


def test_um_arquivo_por_dia_do_evento(evento_cdc):
    hoje = EventoOperacao.from_cdc(evento_cdc)
    amanha = EventoOperacao.from_cdc(evento_cdc | {"__ts_ms": evento_cdc["__ts_ms"] + DIA_MS})
    cliente = MagicMock()

    caminhos = VolumeParquetWriter("/Volumes/comex/bronze/landing/", cliente).gravar(
        [hoje, hoje, amanha])

    assert len(caminhos) == 2
    assert caminhos[0].startswith("/Volumes/comex/bronze/landing/operacao/dt=2026-11-16/")
    assert cliente.files.upload.call_count == 2
