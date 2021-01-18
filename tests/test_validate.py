# coding:utf-8


import pytest
from click.testing import CliRunner
from umakaparser.services import build
from os import path, getenv

FILE_DIR = path.dirname(path.abspath(__file__))
FIXTURE_DIR = path.join(FILE_DIR, 'fixture')
ASSETS_DIR = path.join(FIXTURE_DIR, 'meshdataset')
TESTDATA_DIR = path.join(FIXTURE_DIR, 'validate')
DIST_DIR = path.join(TESTDATA_DIR, 'dist')


@pytest.fixture
def runner():
    return CliRunner()


def test_validate_metadata(runner):
    LOCALE = getenv('LANG').split('_')[0]

    TESTDATA_01 = path.join(TESTDATA_DIR, 'success.ttl')
    DIST_01 = path.join(DIST_DIR, 'success.json')
    result = runner.invoke(build, [TESTDATA_01, '--assets', ASSETS_DIR, '--dist', DIST_01])
    assert '>> ' + DIST_01 in result.output

    TESTDATA_02 = path.join(TESTDATA_DIR, 'error_default_dataset.ttl')
    DIST_02 = path.join(DIST_DIR, 'error_default_dataset.json')
    result = runner.invoke(build, [TESTDATA_02, '--assets', ASSETS_DIR, '--dist', DIST_02])
    assert '>> ' + DIST_02 not in result.output
    assert result.exit_code == 2
    assert 'Error: Validation failed.' in result.output
    message_ja = 'Cause: metadata'
    message_en = 'Cause: defaultDataset'
    message = message_ja if LOCALE == 'ja' else message_en
    assert message in result.output
    assert not path.exists(DIST_02)
