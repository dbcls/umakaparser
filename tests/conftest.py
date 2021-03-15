import pytest
from click.testing import CliRunner
from os import getenv


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def locale():
    return getenv('LANG').split('_')[0]
