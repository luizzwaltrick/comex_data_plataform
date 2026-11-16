import pytest

from comex.models import EventoInvalido, EventoOperacao, Fluxo


def test_evento_valido(evento_cdc):
    e = EventoOperacao.from_cdc(evento_cdc)
    assert (e.id, e.op, e.deletado) == (42, "c", False)
    assert e.operacao.fluxo is Fluxo.IMPORTACAO
    assert e.to_row()["fluxo"] == "IMP"


def test_delete_vem_marcado(evento_cdc):
    e = EventoOperacao.from_cdc(evento_cdc | {"__op": "d", "__deleted": "true"})
    assert e.deletado


@pytest.mark.parametrize("mudanca", [
    {"co_ncm": "123"},
    {"vl_fob": -1},
    {"mes": 13},
    {"fluxo": "XXX"},
    {"__op": "z"},
    {"vl_fob": None},
])
def test_evento_invalido(evento_cdc, mudanca):
    with pytest.raises(EventoInvalido):
        EventoOperacao.from_cdc(evento_cdc | mudanca)


def test_campo_faltando(evento_cdc):
    del evento_cdc["co_pais"]
    with pytest.raises(EventoInvalido):
        EventoOperacao.from_cdc(evento_cdc)
