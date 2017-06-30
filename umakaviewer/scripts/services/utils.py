# coding:utf-8

from rdflib.plugins.parsers.ntriples import r_literal
from rdflib import Literal
from mimetypes import guess_type
import os


def parse_literal(literal):
    return Literal(*[l if l else None for l in r_literal.match(literal).groups()])


def get_type(file_path):
    mimetype, _ = guess_type(file_path)
    if mimetype:
        return mimetype.split('/')[1]

    _, ext = os.path.splitext(file_path)
    if ext == '.ttl':
        return 'turtle'
    elif ext == ('.n3', '.nt'):
        return 'n3'
