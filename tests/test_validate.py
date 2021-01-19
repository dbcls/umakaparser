# coding:utf-8


import pytest
from click.testing import CliRunner
from umakaparser.services import build
from os import path, getenv

LOCALE = getenv('LANG').split('_')[0]
FILE_DIR = path.dirname(path.abspath(__file__))
FIXTURE_DIR = path.join(FILE_DIR, 'fixture')
TESTDATA_DIR = path.join(FIXTURE_DIR, 'validate')


@pytest.fixture
def runner():
    return CliRunner()


def test_validate_metadata(runner):
    TARGET = 'metadata'
    ASSETS_DIR = path.join(TESTDATA_DIR, TARGET, 'assets')

    def make_path(filename):
        testdata = path.join(TESTDATA_DIR, TARGET, '{}.ttl'.format(filename))
        dist = path.join(TESTDATA_DIR, TARGET, 'dist', '{}.json'.format(filename))
        return testdata, dist

    def check_success():
        TESTDATA, DIST = make_path('success')
        result = runner.invoke(build, [TESTDATA, '--assets', ASSETS_DIR, '--dist', DIST])
        assert result.exit_code == 0
        assert '>> ' + DIST in result.output
        assert path.exists(DIST)

    def check_endpoint():
        TESTDATA, DIST = make_path('error_endpoint')
        result = runner.invoke(build, [TESTDATA, '--assets', ASSETS_DIR, '--dist', DIST])
        assert result.exit_code == 2
        assert '>> ' + DIST not in result.output
        assert 'Error: Validation failed.' in result.output
        message_ja = 'Cause: metadata'
        message_en = 'Cause: endpoint'
        message = message_ja if LOCALE == 'ja' else message_en
        assert message in result.output
        assert not path.exists(DIST)

    def check_crawl_log():
        TESTDATA, DIST = make_path('error_crawl_log')
        result = runner.invoke(build, [TESTDATA, '--assets', ASSETS_DIR, '--dist', DIST])
        assert result.exit_code == 2
        assert '>> ' + DIST not in result.output
        assert 'Error: Validation failed.' in result.output
        message_ja = 'Cause: metadata'
        message_en = 'Cause: crawlLog'
        message = message_ja if LOCALE == 'ja' else message_en
        assert message in result.output
        assert not path.exists(DIST)

    def check_crawl_start_time():
        TESTDATA, DIST = make_path('error_crawl_start_time')
        result = runner.invoke(build, [TESTDATA, '--assets', ASSETS_DIR, '--dist', DIST])
        assert result.exit_code == 2
        assert '>> ' + DIST not in result.output
        assert 'Error: Validation failed.' in result.output
        message_ja = 'Cause: metadata'
        message_en = 'Cause: crawlStartTime'
        message = message_ja if LOCALE == 'ja' else message_en
        assert message in result.output
        assert not path.exists(DIST)

    def check_default_dataset():
        TESTDATA, DIST = make_path('error_default_dataset')
        result = runner.invoke(build, [TESTDATA, '--assets', ASSETS_DIR, '--dist', DIST])
        assert result.exit_code == 2
        assert '>> ' + DIST not in result.output
        assert 'Error: Validation failed.' in result.output
        message_ja = 'Cause: metadata'
        message_en = 'Cause: defaultDataset'
        message = message_ja if LOCALE == 'ja' else message_en
        assert message in result.output
        assert not path.exists(DIST)

    def check_triples():
        TESTDATA, DIST = make_path('error_triples')
        result = runner.invoke(build, [TESTDATA, '--assets', ASSETS_DIR, '--dist', DIST])
        assert result.exit_code == 2
        assert '>> ' + DIST not in result.output
        assert 'Error: Validation failed.' in result.output
        message_ja = 'Cause: metadata'
        message_en = 'Cause: triples'
        message = message_ja if LOCALE == 'ja' else message_en
        assert message in result.output
        assert not path.exists(DIST)

    def check_errors():
        TESTDATA, DIST = make_path('errors')
        result = runner.invoke(build, [TESTDATA, '--assets', ASSETS_DIR, '--dist', DIST])
        assert result.exit_code == 2
        assert '>> ' + DIST not in result.output
        assert 'Error: Validation failed.' in result.output
        messages_ja = ['Cause: metadata']
        messages_en = ['Cause: endpoint', 'Cause: crawlStartTime', 'Cause: triples']
        messages = messages_ja if LOCALE == 'ja' else messages_en
        for message in messages:
            assert message in result.output
        warn_message = 'Warn: '
        assert warn_message not in result.output
        assert not path.exists(DIST)

    check_success()
    check_endpoint()
    check_crawl_log()
    check_crawl_start_time()
    check_default_dataset()
    check_triples()
    check_errors()
