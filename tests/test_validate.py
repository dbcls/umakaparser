# coding:utf-8


import pytest
from click.testing import CliRunner
from umakaparser.services import build
from os import path, getenv
import i18n
import tempfile
import shutil

LOCALE = getenv('LANG').split('_')[0]
FILE_DIR = path.dirname(path.abspath(__file__))
FIXTURE_DIR = path.join(FILE_DIR, 'fixture')
TESTDATA_DIR = path.join(FIXTURE_DIR, 'validate')


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def message():
    def format(prefix, cause, item):
        return prefix + ': ' + i18n.t('cmd.build.error_validation_required', cause=cause, item=item)
    return format


def test_validate_metadata(runner, message):
    TARGET = 'metadata'
    ASSETS_DIR = path.join(TESTDATA_DIR, TARGET, 'assets')
    DIST_DIR = tempfile.mkdtemp(dir=path.join(TESTDATA_DIR, TARGET))

    def make_path(filename):
        testdata = path.join(TESTDATA_DIR, TARGET, '{}.ttl'.format(filename))
        dist = path.join(DIST_DIR, '{}.json'.format(filename))
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
        assert result.exit_code == 0
        assert '>> ' + DIST not in result.output
        assert 'Validation failed.' in result.output
        assert message('Reason', 'metadata', 'endpoint') in result.output
        assert not path.exists(DIST)

    def check_crawl_log():
        TESTDATA, DIST = make_path('error_crawl_log')
        result = runner.invoke(build, [TESTDATA, '--assets', ASSETS_DIR, '--dist', DIST])
        assert result.exit_code == 0
        assert '>> ' + DIST not in result.output
        assert 'Validation failed.' in result.output
        assert message('Reason', 'metadata', 'crawlLog') in result.output
        assert not path.exists(DIST)

    def check_crawl_start_time():
        TESTDATA, DIST = make_path('error_crawl_start_time')
        result = runner.invoke(build, [TESTDATA, '--assets', ASSETS_DIR, '--dist', DIST])
        assert result.exit_code == 0
        assert '>> ' + DIST not in result.output
        assert 'Validation failed.' in result.output
        assert message('Reason', 'metadata', 'crawlStartTime') in result.output
        assert not path.exists(DIST)

    def check_default_dataset():
        TESTDATA, DIST = make_path('error_default_dataset')
        result = runner.invoke(build, [TESTDATA, '--assets', ASSETS_DIR, '--dist', DIST])
        assert result.exit_code == 0
        assert '>> ' + DIST not in result.output
        assert 'Validation failed.' in result.output
        assert message('Reason', 'metadata', 'defaultDataset') in result.output
        assert not path.exists(DIST)

    def check_triples():
        TESTDATA, DIST = make_path('error_triples')
        result = runner.invoke(build, [TESTDATA, '--assets', ASSETS_DIR, '--dist', DIST])
        assert result.exit_code == 0
        assert '>> ' + DIST not in result.output
        assert 'Validation failed.' in result.output
        assert message('Reason', 'metadata', 'triples') in result.output
        assert not path.exists(DIST)

    def check_errors():
        TESTDATA, DIST = make_path('errors')
        result = runner.invoke(build, [TESTDATA, '--assets', ASSETS_DIR, '--dist', DIST])
        assert result.exit_code == 0
        assert '>> ' + DIST not in result.output
        assert 'Validation failed.' in result.output
        messages = [
            message('Reason', 'metadata', 'endpoint'),
            message('Reason', 'metadata', 'crawlStartTime'),
            message('Reason', 'metadata', 'triples'),
        ]
        for m in messages:
            assert m in result.output
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

    shutil.rmtree(DIST_DIR)


def test_validate_class_partition(runner, message):
    TARGET = 'class_partition'
    ASSETS_DIR = path.join(TESTDATA_DIR, TARGET, 'assets')
    DIST_DIR = tempfile.mkdtemp(dir=path.join(TESTDATA_DIR, TARGET))

    def make_path(filename):
        testdata = path.join(TESTDATA_DIR, TARGET, '{}.ttl'.format(filename))
        dist = path.join(DIST_DIR, '{}.json'.format(filename))
        return testdata, dist

    def check_success():
        TESTDATA, DIST = make_path('success')
        result = runner.invoke(build, [TESTDATA, '--assets', ASSETS_DIR, '--dist', DIST])
        assert result.exit_code == 0
        assert '>> ' + DIST in result.output
        assert path.exists(DIST)

    def check_class():
        TESTDATA, DIST = make_path('warn_class')
        result = runner.invoke(build, [TESTDATA, '--assets', ASSETS_DIR, '--dist', DIST])
        assert result.exit_code == 0
        assert '>> ' + DIST in result.output
        assert message('Warn', 'ClassPartition', 'class') in result.output
        assert path.exists(DIST)

    def check_entities():
        TESTDATA, DIST = make_path('warn_entities')
        result = runner.invoke(build, [TESTDATA, '--assets', ASSETS_DIR, '--dist', DIST])
        assert result.exit_code == 0
        assert '>> ' + DIST in result.output
        assert message('Warn', 'ClassPartition', 'entities') in result.output
        assert path.exists(DIST)

    def check_warns():
        TESTDATA, DIST = make_path('warns')
        result = runner.invoke(build, [TESTDATA, '--assets', ASSETS_DIR, '--dist', DIST])
        assert result.exit_code == 0
        assert '>> ' + DIST in result.output
        messages = [
            message('Warn', 'ClassPartition', 'class'),
            message('Warn', 'ClassPartition', 'entities'),
        ]
        for m in messages:
            assert m in result.output
        error_message = 'Validation failed.'
        assert error_message not in result.output
        assert path.exists(DIST)

    check_success()
    check_class()
    check_entities()
    check_warns()

    shutil.rmtree(DIST_DIR)


def test_validate_property_partition(runner, message):
    TARGET = 'property_partition'
    ASSETS_DIR = path.join(TESTDATA_DIR, TARGET, 'assets')
    DIST_DIR = tempfile.mkdtemp(dir=path.join(TESTDATA_DIR, TARGET))

    def make_path(filename):
        testdata = path.join(TESTDATA_DIR, TARGET, '{}.ttl'.format(filename))
        dist = path.join(DIST_DIR, '{}.json'.format(filename))
        return testdata, dist

    def check_success():
        TESTDATA, DIST = make_path('success')
        result = runner.invoke(build, [TESTDATA, '--assets', ASSETS_DIR, '--dist', DIST])
        assert result.exit_code == 0
        assert '>> ' + DIST in result.output
        assert path.exists(DIST)

    def check_property():
        TESTDATA, DIST = make_path('warn_property')
        result = runner.invoke(build, [TESTDATA, '--assets', ASSETS_DIR, '--dist', DIST])
        assert result.exit_code == 0
        assert '>> ' + DIST in result.output
        assert message('Warn', 'PropertyPartition', 'property') in result.output
        assert path.exists(DIST)

    def check_triples():
        TESTDATA, DIST = make_path('warn_triples')
        result = runner.invoke(build, [TESTDATA, '--assets', ASSETS_DIR, '--dist', DIST])
        assert result.exit_code == 0
        assert '>> ' + DIST in result.output
        assert message('Warn', 'PropertyPartition', 'triples') in result.output
        assert path.exists(DIST)

    def check_warns():
        TESTDATA, DIST = make_path('warns')
        result = runner.invoke(build, [TESTDATA, '--assets', ASSETS_DIR, '--dist', DIST])
        assert result.exit_code == 0
        assert '>> ' + DIST in result.output
        messages = [
            message('Warn', 'PropertyPartition', 'property'),
            message('Warn', 'PropertyPartition', 'triples'),
        ]
        for m in messages:
            assert m in result.output
        error_message = 'Validation failed.'
        assert error_message not in result.output
        assert path.exists(DIST)

    check_success()
    check_property()
    check_triples()
    check_warns()

    shutil.rmtree(DIST_DIR)
