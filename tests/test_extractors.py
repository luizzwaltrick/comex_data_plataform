from comex.extractors import EXTRACTORS
from comex.models import Fluxo, Operacao
from conftest import FIXTURES


def _ler(fluxo: str, arquivo: str) -> list[Operacao]:
    with open(FIXTURES / arquivo, "rb") as f:
        return list(EXTRACTORS[fluxo](2024, sessao=object()).ler(f))


def test_exportacao_normaliza_ncm_com_8_digitos():
    ops = _ler("exp", "exp_amostra.csv")
    assert [o.co_ncm for o in ops] == ["02071200", "09011110"]
    assert ops[0].fluxo is Fluxo.EXPORTACAO and ops[0].vl_frete is None
    assert ops[0].co_urf == 927800


def test_importacao_traz_frete_e_seguro():
    (op,) = _ler("imp", "imp_amostra.csv")
    assert (op.vl_frete, op.vl_seguro) == (3000.0, 150.0)
