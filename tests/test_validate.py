# coding:utf-8


import pytest
from click.testing import CliRunner
from umakaparser.services import build
from os import path, getenv
import six

FILE_DIR = path.dirname(path.abspath(__file__))
FIXTURE_DIR = FILE_DIR + '/fixture'
ASSETS_DIR = FIXTURE_DIR + '/meshdataset'
TESTDATA_DIR = FIXTURE_DIR + '/validate'
DIST_DIR = TESTDATA_DIR + '/dist'


@pytest.fixture
def runner():
    return CliRunner()


def test_validate_metadata(runner):
    LOCALE = getenv('LANG').split('_')[0]

    TESTDATA_01 = TESTDATA_DIR + '/success.ttl'
    DIST_01 = DIST_DIR + '/success.json'
    result = runner.invoke(build, [TESTDATA_01, '--assets', ASSETS_DIR, '--dist', DIST_01])
    assert '>> ' + DIST_01 in result.output

    TESTDATA_02 = TESTDATA_DIR + '/error_default_dataset.ttl'
    DIST_02 = DIST_DIR + '/error_default_dataset.json'
    result = runner.invoke(build, [TESTDATA_02, '--assets', ASSETS_DIR, '--dist', DIST_02])
    assert '>> ' + DIST_02 not in result.output
    assert result.exit_code == 2
    assert 'Error: Validation failed.' in result.output
    assert ('Cause: metadataに必須の' if LOCALE == 'ja' else 'Cause: defaultDataset') in result.output
    assert not path.exists(DIST_02)
