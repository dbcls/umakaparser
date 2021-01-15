import pytest
from click.testing import CliRunner
from umakaparser.services import build
from os.path import abspath, dirname

FILE_DIR = dirname(abspath(__file__))
FIXTURE_DIR = FILE_DIR + '/fixture'
ASSETS_DIR = FIXTURE_DIR + '/meshdataset'
TESTDATA_DIR = FIXTURE_DIR + '/validate'
DIST_DIR = TESTDATA_DIR + '/dist'


@pytest.fixture
def runner():
    return CliRunner()


def test_validate_metadata(runner):
    result = runner.invoke(build, [])
    assert 'Error: Missing argument' in result.output

    TESTDATA_01 = TESTDATA_DIR + '/test.ttl'
    DIST_FILE = DIST_DIR + '/test_01.json'
    result = runner.invoke(build, [TESTDATA_01, '--assets', ASSETS_DIR, '--dist', DIST_FILE])
    assert '>> ' + DIST_FILE in result.output
