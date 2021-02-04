# coding:utf-8

from rdflib.plugins.parsers.ntriples import r_literal
from rdflib import Literal, URIRef
from mimetypes import guess_type
import os
import i18n
import six
from functools import wraps
import datetime


IGNORE_CLASSES = set([
    URIRef(c)
    for c in [
        "http://www.w3.org/2002/07/owl#Class",
        "http://www.w3.org/2002/07/owl#ObjectProperty",
        "http://www.w3.org/2002/07/owl#Ontology",
        "http://www.w3.org/2002/07/owl#Thing",
        "http://www.w3.org/2002/07/owl#NamedIndividual"
    ]])


def parse_literal(literal):
    return Literal(*[v if v else None for v in r_literal.match(literal).groups()])


def get_type(file_path):
    mimetype, _ = guess_type(file_path)
    if mimetype:
        return mimetype.split('/')[1]

    _, ext = os.path.splitext(file_path)
    if ext == '.ttl':
        return 'turtle'
    elif ext in ('.n3', '.nt'):
        return 'n3'


def auto_encode(msg):
    return msg.encode('utf-8') if six.PY2 else msg


def i18n_t(key, **kwargs):
    return auto_encode(i18n.t(key, **kwargs))


def timer(fn):
    @wraps(fn)
    def wrapper(*args, **kargs):
        start = datetime.datetime.now()
        result = fn(*args, **kargs)
        end = datetime.datetime.now()
        elapsed = end.timestamp() - start.timestamp()
        print('Debug: name -> {}, start -> {}, end -> {}, elapsed -> {} s'.format(fn.__name__, start, end, elapsed))
        return result
    return wrapper
