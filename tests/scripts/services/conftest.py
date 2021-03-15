import pytest
from os import path


@pytest.fixture
def fixture_dir():
    file_dir = path.dirname(path.abspath((__file__)))
    return path.join(file_dir, 'fixture')
