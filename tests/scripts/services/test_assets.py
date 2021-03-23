# coding:utf-8


import pytest
import shutil
import os
from os import path
from rdflib.term import URIRef
from umakaparser.scripts.services.assets import separate_large_owl, output_process, join_process, index_owl


@pytest.fixture
def testdata_paths(fixture_dir):
    filenames = ['first.nt', 'second.nt', 'third.nt', 'test.nt']
    testdata_dir = path.join(fixture_dir, 'assets')
    testdatas = [path.join(testdata_dir, f) for f in filenames]
    return testdatas


def test_saparate_large_owl(testdata_paths):
    comment_length = 1
    prefix_length = 3
    exclude_length = comment_length + prefix_length
    total_length = (100 - exclude_length) * 2 + 90 - exclude_length

    def check_separated_files(limit_of_lines):
        prefix, temp_files, temp_dir = separate_large_owl(testdata_paths[:-1], limit_of_lines)
        assert '@prefix rdf:' in prefix
        assert '@prefix rdfs:' in prefix
        assert '@prefix owl:' in prefix
        assert len(temp_files) == int(total_length / limit_of_lines + 1)
        assert len(list(open(temp_files[-1]))) == total_length % limit_of_lines
        shutil.rmtree(temp_dir)

    check_separated_files(100)
    check_separated_files(30)


def test_output_process(testdata_paths):
    prefix, temp_files, temp_dir = separate_large_owl(testdata_paths, 100)

    target_properties = {
        URIRef('http://www.w3.org/2002/07/owl#sameAs'): 'sameAs',
        URIRef('http://www.w3.org/2000/01/rdf-schema#label'): 'label',
        URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf'): 'subClassOf',
        URIRef('http://www.w3.org/2000/01/rdf-schema#domain'): 'domain',
        URIRef('http://www.w3.org/2000/01/rdf-schema#range'): 'range',
    }
    out_dirs = [path.join(temp_dir, t) for t in target_properties.values()]
    for out_dir in out_dirs:
        os.mkdir(out_dir)
    for temp_file in temp_files:
        output_process((prefix, temp_file, target_properties, temp_dir))

    for out_dir in out_dirs:
        child_files = os.listdir(out_dir)
        for cp in child_files:
            assert path.exists(path.join(out_dir, cp))

    shutil.rmtree(temp_dir)


def test_join_process(testdata_paths):
    prefix, temp_files, temp_dir = separate_large_owl(testdata_paths, 100)

    target_properties = {
        URIRef('http://www.w3.org/2002/07/owl#sameAs'): 'sameAs',
        URIRef('http://www.w3.org/2000/01/rdf-schema#label'): 'label',
        URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf'): 'subClassOf',
        URIRef('http://www.w3.org/2000/01/rdf-schema#domain'): 'domain',
        URIRef('http://www.w3.org/2000/01/rdf-schema#range'): 'range',
    }
    out_dirs = [path.join(temp_dir, t) for t in target_properties.values()]
    for out_dir in out_dirs:
        os.mkdir(out_dir)
    for temp_file in temp_files:
        output_process((prefix, temp_file, target_properties, temp_dir))
    empty_dirs = [od for od in out_dirs if len(os.listdir(od)) == 0]

    dist_dir = path.join(temp_dir, 'dist')
    os.mkdir(dist_dir)
    for op in target_properties.values():
        join_process((dist_dir, temp_dir, op))

    for out_dir in out_dirs:
        if out_dir in empty_dirs:
            continue
        dist_file = path.join(dist_dir, path.basename(out_dir))
        assert path.isfile(dist_file)

    shutil.rmtree(temp_dir)


def test_index_owl(testdata_paths):
    target_properties = {
        URIRef('http://www.w3.org/2002/07/owl#sameAs'): 'sameAs',
        URIRef('http://www.w3.org/2000/01/rdf-schema#label'): 'label',
        URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf'): 'subClassOf',
        URIRef('http://www.w3.org/2000/01/rdf-schema#domain'): 'domain',
        URIRef('http://www.w3.org/2000/01/rdf-schema#range'): 'range',
    }

    index_owl(testdata_paths, target_properties, 'dist')

    dist_dir = path.join(os.getcwd(), 'dist')
    filenames = list(target_properties.values())
    filenames.append('prefix.ttl')
    for child in os.listdir(dist_dir):
        assert child in filenames

    with open(path.join(dist_dir, 'sameAs'), 'r') as fp:
        assert len(list(fp)) == 3
    with open(path.join(dist_dir, 'label'), 'r') as fp:
        assert len(list(fp)) == 70
    with open(path.join(dist_dir, 'subClassOf'), 'r') as fp:
        assert len(list(fp)) == 4
    with open(path.join(dist_dir, 'domain'), 'r') as fp:
        assert len(list(fp)) == 2
    with open(path.join(dist_dir, 'range'), 'r') as fp:
        assert len(list(fp)) == 1
    with open(path.join(dist_dir, 'prefix.ttl'), 'r') as fp:
        assert len(list(fp)) == 12

    shutil.rmtree(dist_dir)
