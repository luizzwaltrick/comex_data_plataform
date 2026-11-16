from pathlib import Path

from comex.extractors import EXTRACTORS
from comex.models import Fluxo, Operacao

FIX = Path(__file__).parent / "fixtures"


def _ler(fluxo: str, arquivo: str) -> list[Operacao]:
    with open(FIX / arquivo, "rb") as f:
        return list(EXTRACTORS[fluxo](2024, sessao=object()).ler(f))


def test_exportacao_normaliza_ncm_com_8_digitos():
    ops = _ler("exp", "exp_amostra.csv")
    assert [o.co_ncm for o in ops] == ["02071200", "09011110"]
    assert ops[0].fluxo is Fluxo.EXPORTACAO and ops[0].vl_frete is None


def test_importacao_traz_frete_e_seguro():
    (op,) = _ler("imp", "imp_amostra.csv")
    assert (op.vl_frete, op.vl_seguro) == (3000.0, 150.0)


def test_json_ida_e_volta():
    op = _ler("imp", "imp_amostra.csv")[0]
    assert Operacao.from_json(op.to_json()) == op
    assert op.chave == "85171300-160"
