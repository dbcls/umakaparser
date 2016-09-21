# coding:utf-8

from rdflib.graph import Graph
from .utils import get_type
from os.path import splitext


def convert2ttl(owl_files):
    for owl_file in owl_files:
        graph = Graph()
        graph.parse(location=owl_file, format=get_type(owl_file))
        ttl_file = splitext(owl_file)[0] + '.ttl'
        with open(ttl_file, 'wb') as fp:
            hoge = graph.serialize(format='turtle')
            fp.write(hoge)
        print('>>>', ttl_file)
