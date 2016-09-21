# coding:utf-8

from rdflib.graph import Graph, URIRef, BNode
from datetime import datetime
import tempfile
import os
from multiprocessing.pool import Pool
from time import time
from shutil import rmtree, move
import glob
from itertools import chain


# 複数のturtleファイルを5万tripleを1つのチャンクとして
# テンポラリファイルに分割する。
def separate_large_owl(owl_file_paths):
    fps = [open(file_path, 'r') for file_path in owl_file_paths]
    chain_fp = chain(*fps)
    text = None
    count = 0
    prefix = ''
    temp_dir = tempfile.mkdtemp(dir=os.getcwd())

    now = datetime.now()
    temp_files = []

    def output(content):
        t = tempfile.mkstemp(dir=temp_dir)
        with open(t[1], 'w') as temp_fp:
            temp_fp.write(content)
        return t

    for idx, row in enumerate(chain_fp):
        row = row.strip()
        if text is None:
            text = ''
            count = 0

        if not row or row.startswith('#'):
            continue

        if row[0:7].lower() == '@prefix':
            prefix += row
            continue

        text += row + '\n'
        if row.endswith(' .'):
            count += 1
            if count == 50000:
                num, name = output(text)
                text = None
                temp_files.append(name)
                print(num, idx, datetime.now() - now)
    else:
        num, name = output(text)
        temp_files.append(name)
        print(num, idx, datetime.now() - now)

    for fp in fps:
        fp.close()
    return prefix, temp_files, temp_dir


# turtleをパースして目的のプロパティが含まれているものを抽出して
# テンポラリファイルに書き出す。
# サブプロセスとして実行するので外のスコープにはアクセスしない。
def output_process(args):
    prefix, temp_file, output_properties, base_dir = args
    graph = Graph()
    with open(temp_file) as fp:
        graph.parse(format='turtle', data=prefix + fp.read())
    output_fp = {}
    for s, p, o in graph:
        exclude_if = all([
            isinstance(o, BNode),
            list(graph.objects(o, URIRef('http://www.w3.org/2002/07/owl#onProperty')))
        ])
        if p in output_properties and not exclude_if:
            output = output_properties[p]
            if not output in output_fp:
                _, file_path = tempfile.mkstemp(dir=os.path.join(base_dir, output))
                output_fp[output] = open(file_path, 'w')
            fp = output_fp[output]
            fp.write('{} {}\n'.format(s.n3(), o.n3()))
    for fp in output_fp.values():
        fp.close()
    print(temp_file)


# ディレクトリ内のファイルを全て連結する。
# サブプロセスとして実行するので外のスコープにはアクセスしない。
def join_process(args):
    base_dir, temp_dir, op = args
    temp_path = os.path.join(temp_dir, op)
    files = glob.glob1(temp_path, 'tmp*')
    if not files:
        os.rmdir(temp_path)
        return

    num, temp_file = tempfile.mkstemp(dir=temp_dir)
    text = ""
    for file_path in files:
        file_path = os.path.join(temp_path, file_path)
        with open(file_path, 'r') as fp:
            for row in fp:
                text += row
    with open(temp_file, 'w') as fp:
        fp.write(text)

    move(temp_file, os.path.join(base_dir, op))


def index_owl(owl_file_paths, output_properties, dist):
    prefix, temp_files, temp_dir = separate_large_owl(owl_file_paths)
    base_dir = os.path.join(os.getcwd(), dist)

    if os.path.exists(base_dir):
        rmtree(base_dir)

    for output_property in output_properties.values():
        os.mkdir(os.path.join(temp_dir, output_property))

    os.mkdir(base_dir)
    try:
        p = Pool()
        start_time = time()
        p.map(output_process, ((prefix, temp_file, output_properties, temp_dir) for temp_file in temp_files))
        finish_time = time()
        print(finish_time - start_time)
        for op in output_properties.values():
            join_process((base_dir, temp_dir, op))
        with open(os.path.join(base_dir, 'prefix.ttl'), 'w') as fp:
            fp.write(prefix)
    finally:
        rmtree(temp_dir)

    return base_dir
