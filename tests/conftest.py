import pytest
from beet import run_beet


@pytest.fixture(scope="session")
def ctx():
    with run_beet({"require": ["bolt_expressions"]}) as ctx:
        yield ctx
