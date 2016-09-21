# coding:utf-8

from rdflib.plugins.parsers.ntriples import r_literal
from rdflib import Literal
from mimetypes import guess_type


def parse_literal(literal):
    return Literal(*[l if l else None for l in r_literal.match(literal).groups()])


def get_type(file_path):
    mimetype, _ = guess_type(file_path)
    return mimetype.split('/')[1]
