from unittest.mock import MagicMock

from comex.models import Fluxo, Operacao
from comex.repositories.operacao_repository import OperacaoRepository


def test_grava_em_lotes_com_uma_transacao_por_lote():
    conexao = MagicMock()
    cursor = conexao.cursor.return_value.__enter__.return_value
    ops = [Operacao(Fluxo.EXPORTACAO, 2024, 1, "02071200", 160, "SC", 1, 927800, 1.0, 2.0)] * 5

    total = OperacaoRepository(conexao, lote=2).salvar(iter(ops))

    assert total == 5
    assert conexao.transaction.call_count == 3
    parametros = cursor.executemany.call_args_list[0].args[1]
    assert parametros[0]["fluxo"] == "EXP" and len(parametros) == 2
