# coding:utf-8

from collections import defaultdict
from rdflib import URIRef
from rdflib.graph import Graph
from rdflib.namespace import OWL, SKOS, DOAP, FOAF, DC, DCTERMS, VOID
from isodate import parse_datetime
import os
import json
from .utils import parse_literal, i18n_t
from tqdm import tqdm
import threading
import sys
import time
from .validate import validate_graph, GraphValidationError

RDFS_CLASS = URIRef('http://rdfs.org/ns/void#class')
RDFS_ENTITIES = URIRef('http://rdfs.org/ns/void#entities')


def labels_lang(labels):
    return {literal.language if literal.language else '': literal for literal in labels}


class ClassResource(object):
    def __init__(self, uri):
        super(ClassResource, self).__init__()
        self.uri = uri
        self.label = []
        self.subClassOf = None

    def serialize(self):
        result = {'label': labels_lang(self.label)}
        if self.subClassOf:
            result['subClassOf'] = self.subClassOf
        return result


class SMBResource(object):
    def __init__(self, graph, node):
        super(SMBResource, self).__init__()
        self._graph = graph
        self._node = node

    def serialize(self):
        return {}


class SBMClassPartition(SMBResource):

    def __init__(self, graph, node):
        super(SBMClassPartition, self).__init__(graph, node)
        self.label = []
        self.subClassOf = None
        self.rhs = set()
        self.lhs = set()

    def __hash__(self, *args, **kwargs):
        return self.uri.__hash__()

    def __eq__(self, other):
        return self.uri == other.uri

    @property
    def uri(self):
        objects = [o for o in self._graph.objects(self._node, RDFS_CLASS)]
        return objects[0].n3(self._graph.namespace_manager).strip('<>') if objects else None

    @property
    def entities(self):
        if self._node:
            objects = [o for o in self._graph.objects(self._node, RDFS_ENTITIES)]
            return int(objects[0]) if objects else None

    def serialize(self):
        result = {}

        if self.entities:
            result['entities'] = self.entities

        if self.label:
            result['label'] = labels_lang(self.label)

        if self.subClassOf:
            result['subClassOf'] = self.subClassOf

        if self.rhs:
            result['rhs'] = sorted(self.rhs, key=lambda x: x[0])

        if self.lhs:
            result['lhs'] = sorted(self.lhs, key=lambda x: x[1])
        return result


RDFS_PROPERTY = URIRef('http://rdfs.org/ns/void#property')
RDFS_TRIPLES = URIRef('http://rdfs.org/ns/void#triples')
CLASS_RELATION = URIRef('http://sparqlbuilder.org/2015/09/rdf-metadata-schema#classRelation')


class SBMPropertyPartition(SMBResource):
    RDFS_PROPERTY = URIRef('http://rdfs.org/ns/void#property')
    RDFS_TRIPLES = URIRef('http://rdfs.org/ns/void#triples')
    CLASS_RELATION = URIRef('http://sparqlbuilder.org/2015/09/rdf-metadata-schema#classRelation')

    def __init__(self, graph, node):
        super(SBMPropertyPartition, self).__init__(graph, node)
        self.label = []

    @property
    def uri(self):
        objects = [o for o in self._graph.objects(self._node, RDFS_PROPERTY)]
        return objects[0].n3(self._graph.namespace_manager).strip('<>') if objects else None

    @property
    def triples(self):
        objects = [o for o in self._graph.objects(self._node, RDFS_TRIPLES)]
        return int(objects[0]) if objects else None

    @property
    def class_relations(self):
        support_map = {}
        for node in self._graph.objects(self._node, CLASS_RELATION):
            relation = SBMClassRelation(self._graph, node)
            same_relation = support_map.get((relation.triples, relation.subject_class))
            if same_relation:
                if None not in [same_relation.object_datatype, relation.object_class] and same_relation.object_datatype == relation.object_class:
                    continue
            else:
                support_map[(relation.triples, relation.subject_class)] = relation
        return sorted(support_map.values(), key=lambda x: x.triples, reverse=True)

    def serialize(self, classes_detail):
        result = {
            'uri': self.uri,
            'triples': self.triples,
            'class_relations': [relation.serialize(classes_detail) for relation in self.class_relations]
        }
        if self.label:
            result['label'] = labels_lang(self.label)

        return result


OBJECT_CLASS = URIRef('http://sparqlbuilder.org/2015/09/rdf-metadata-schema#objectClass')
OBJECT_DATATYPE = URIRef('http://sparqlbuilder.org/2015/09/rdf-metadata-schema#objectDatatype')
SUBJECT_CLASS = URIRef('http://sparqlbuilder.org/2015/09/rdf-metadata-schema#subjectClass')


class SBMClassRelation(SMBResource):
    @property
    def triples(self):
        objects = [o for o in self._graph.objects(self._node, RDFS_TRIPLES)]
        return int(objects[0]) if objects else None

    @property
    def object_class(self):
        objects = [o for o in self._graph.objects(self._node, OBJECT_CLASS)]
        return objects[0].n3(self._graph.namespace_manager).strip('<>') if objects else None

    @property
    def object_datatype(self):
        objects = [o for o in self._graph.objects(self._node, OBJECT_DATATYPE)]
        return objects[0].n3(self._graph.namespace_manager).strip('<>') if objects else None

    @property
    def subject_class(self):
        objects = [o for o in self._graph.objects(self._node, SUBJECT_CLASS)]
        return objects[0].n3(self._graph.namespace_manager).strip('<>') if objects else None

    def serialize(self, classes_detail):
        object_class = self.object_class
        object_datatype = self.object_datatype
        if object_class not in classes_detail:
            object_class, object_datatype = object_datatype, object_class
        return {
            'triples': self.triples,
            'object_class': object_class,
            'object_datatype': object_datatype,
            'subject_class': self.subject_class
        }


class AssetReader(object):
    def __init__(self, assets_dir):
        super(AssetReader, self).__init__()
        self.assets_dir = assets_dir

    def read_subject_object(self, filename, graph):
        if not self.assets_dir:
            return
        try:
            with open(os.path.join(self.assets_dir, filename)) as fp:
                for row in fp:
                    row = row.strip()
                    obj = json.loads(row)
                    so = obj['s'], obj['o']
                    yield tuple(map(lambda x: URIRef(x[1:-1]).n3(graph.namespace_manager).strip('<>'), so))
        except IOError:
            return

    def read_subject_literal(self, filename, graph):
        if not self.assets_dir:
            return
        try:
            with open(os.path.join(self.assets_dir, filename)) as fp:
                for row in fp:
                    obj = json.loads(row)
                    s, o = obj['s'], obj['o']
                    yield URIRef(s[1:-1]).n3(graph.namespace_manager).strip('<>'), parse_literal(o)
        except IOError:
            return

    def load_prefix(self, graph):
        if not self.assets_dir:
            return
        try:
            path = os.path.join(self.assets_dir, 'prefix.ttl')
            with open(path) as fp:
                graph.parse(file=fp, format='turtle')
        except IOError:
            pass


def extraction_classes(graph):
    class_partition = URIRef('http://rdfs.org/ns/void#classPartition')
    classes = []
    for node in graph.objects(predicate=class_partition):
        classes.append(SBMClassPartition(graph, node))
    return classes


def extraction_properties(graph):
    property_partition = URIRef('http://rdfs.org/ns/void#propertyPartition')
    properties = []
    for node in graph.objects(predicate=property_partition):
        prop = SBMPropertyPartition(graph, node)
        if not any(prop.uri == i.uri for i in properties):
            properties.append(prop)
    return properties


def inheritance_structure(graph, classes, sub_class_map, asset_reader):
    same_as_group = {}
    for s, o in asset_reader.read_subject_object('sameAs', graph):
        group = same_as_group.get(s) or same_as_group.get(o) or set()
        group.add(s)
        group.add(o)
        same_as_group[s] = same_as_group[o] = group
    classes_map = {}
    for c in classes:
        classes_map[c.uri] = c
        for c_uri in same_as_group.get(c.uri, ()):
            classes_map[c_uri] = c

    top_level_uri = set()
    sub_class_nodes = defaultdict(set)

    def recursive_parent_node(uri):
        parent_classes = sub_class_map.get(uri)

        if uri in classes_map:
            value = classes_map[uri].uri
        else:
            value = uri

        if not parent_classes:
            top_level_uri.add(value)
        else:
            for parent_class in parent_classes:
                sub_class_nodes[parent_class].add(value)
                recursive_parent_node(parent_class)

    for c in classes:
        for c_uri in same_as_group.get(c.uri, (c.uri, )):
            if c_uri in sub_class_map:
                recursive_parent_node(c_uri)
                break
        else:
            top_level_uri.add(c.uri)

    def recursive_dig_node(uri):
        node = {
            'uri': uri,
        }
        if uri in sub_class_nodes:
            node['children'] = [recursive_dig_node(parent) for parent in sub_class_nodes[uri]]
        return node

    obj = [recursive_dig_node(top) for top in top_level_uri]
    return obj, classes_map


def class_reference(graph, classes, structure, classes_map, sub_class_map, asset_reader):
    def flat_structure(node):
        uri = node['uri']
        if uri not in classes_map:
            c = ClassResource(uri)
            classes_map[uri] = c
            classes.append(c)

        for child_node in node.get('children', ()):
            flat_structure(child_node)

    for top in structure:
        flat_structure(top)

    for s, o in asset_reader.read_subject_literal('label', graph):
        if s in classes_map:
            classes_map[s].label.append(o)

    for s, o in classes_map.items():
        if s in sub_class_map:
            o.subClassOf = sub_class_map[s]

    return {c.uri: c.serialize() for c in classes}


def make_meta_data(graph):
    meta_data = {}

    for o in graph.objects(predicate=URIRef('http://www.w3.org/ns/sparql-service-description#endpoint')):
        meta_data['endpoint'] = o
        break

    for o in graph.objects(predicate=URIRef('http://sparqlbuilder.org/2015/09/rdf-metadata-schema#crawlLog')):
        for start_time in graph.objects(o, URIRef('http://sparqlbuilder.org/2015/09/rdf-metadata-schema#crawlStartTime')):
            meta_data['crawl_date'] = parse_datetime(start_time).strftime('%Y/%m/%d %H:%M:%S')
            break

    for o in graph.objects(predicate=URIRef('http://www.w3.org/ns/sparql-service-description#defaultDataset')):
        for triples in graph.objects(o, URIRef('http://rdfs.org/ns/void#triples')):
            meta_data['triples'] = int(triples)
            break
    return meta_data


def property_complete(properties, assets_dir):
    properties_map = {p.uri: p for p in properties}

    for row in open(os.path.join(assets_dir, 'label')):
        row = row.strip()
        s, o = row.split(' ', 1)
        s = URIRef(s[1:-1])
        if s in properties_map:
            properties_map[s].label.append(parse_literal(o))


NAME_SPACE = (
    ('owl', OWL),
    ('skos', SKOS),
    ('doap', DOAP),
    ('foaf', FOAF),
    ('dc', DC),
    ('dcterms', DCTERMS),
    ('void', VOID)
)


def spinner_gen():
    while 1:
        yield '|'
        yield '/'
        yield '-'
        yield '\\'


def build_sbm_model(sbm_ttl, assets_dir, dist):
    graph = Graph()
    asset_reader = AssetReader(assets_dir)
    for prefix, uri in NAME_SPACE:
        graph.namespace_manager.bind(prefix, uri)
    asset_reader.load_prefix(graph)

    print(i18n_t('cmd.build.info_loading_data'))
    thread = threading.Thread(target=graph.parse, kwargs=dict(location=sbm_ttl, format='turtle'))
    thread.start()
    for spinner in spinner_gen():
        sys.stdout.write(spinner + '\033[1D')
        sys.stdout.flush()
        time.sleep(0.2)
        if not thread.is_alive():
            break
    try:
        validate_graph(graph)
    except GraphValidationError as e:
        print(e)
        return
    print(i18n_t('cmd.build.info_loaded_data'))

    print(i18n_t('cmd.build.info_preparing_classes'))
    classes = extraction_classes(graph)
    sub_class_map = defaultdict(list)
    for s, o in asset_reader.read_subject_object('subClassOf', graph):
        sub_class_map[s].append(o)
    structure, classes_map = inheritance_structure(graph, classes, sub_class_map, asset_reader)

    print(i18n_t('cmd.build.info_preparing_properties'))
    properties = extraction_properties(graph)
    for p in tqdm(properties):
        for relation in p.class_relations:
            s = relation.subject_class
            oc = relation.object_class
            if s in classes_map:
                classes_map[s].rhs.add((p.uri, oc))
            if oc in classes_map:
                classes_map[oc].lhs.add((s, p.uri))
    classes_detail = class_reference(graph, classes, structure, classes_map, sub_class_map, asset_reader)
    properties = sorted(properties, key=lambda x: x.triples, reverse=True)

    print(i18n_t('cmd.build.info_getting_metadata'))
    meta_data = make_meta_data(graph)
    meta_data['classes'] = len(classes)
    meta_data['properties'] = len(properties)
    result = {
        'inheritance_structure': structure,
        'classes': classes_detail,
        'properties': [p.serialize(classes_detail) for p in properties],
        'prefixes': {p: n for p, n in graph.namespace_manager.namespaces()},
        'meta_data': meta_data
    }
    print(i18n_t('cmd.build.info_writing_data'))
    with open(dist, 'w') as fp:
        json.dump(result, fp, indent=2, ensure_ascii=False)
    print(i18n_t('cmd.build.info_number_of_classes'), len(classes))
    print(i18n_t('cmd.build.info_number_of_properties'), len(properties))
    return dist
