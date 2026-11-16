import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def evento_cdc() -> dict:
    return json.loads((FIXTURES / "evento_cdc.json").read_text())
