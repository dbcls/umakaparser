# coding:utf-8


from rdflib import URIRef
import i18n
from .utils import auto_encode


def create_triple(s=None, p=None, o=None):
    return {'subject': s, 'predicate': p, 'object': o}


def error_message(cause, triple):
    item = str(triple['predicate']).split('#')[1]
    message = i18n.t('cmd.build.error_validation_required', cause=cause, item=item)
    info = []
    if triple['subject'] is not None:
        info.append('subject = {}'.format(triple['subject']))
    if triple['predicate'] is not None:
        info.append('predicate = {}'.format(triple['predicate']))
    if triple['object'] is not None:
        info.append('object = {}'.format(triple['object']))

    return message + ' ' + '({})'.format(', '.join(info))


def validate_meta_data(graph):

    error_triples = []

    def graph_objects(predicate=None, subject=None):
        return [o for o in graph.objects(subject, predicate)]

    endpoint_predicate = URIRef('http://www.w3.org/ns/sparql-service-description#endpoint')
    endpoints = graph_objects(endpoint_predicate)
    if len(endpoints) == 0:
        error_triples.append(create_triple(p=endpoint_predicate))

    crawl_log_predicate = URIRef('http://sparqlbuilder.org/2015/09/rdf-metadata-schema#crawlLog')
    crawl_logs = graph_objects(crawl_log_predicate)
    if len(crawl_logs) == 0:
        error_triples.append(create_triple(p=crawl_log_predicate))
    else:
        crawl_start_time_predicate = URIRef('http://sparqlbuilder.org/2015/09/rdf-metadata-schema#crawlStartTime')
        crawl_start_times = sum([graph_objects(crawl_start_time_predicate, o) for o in crawl_logs], [])
        if len(crawl_start_times) == 0:
            error_triples.append(create_triple(p=crawl_start_time_predicate))

    default_dataset_predicate = URIRef('http://www.w3.org/ns/sparql-service-description#defaultDataset')
    default_datasets = graph_objects(default_dataset_predicate)
    if len(default_datasets) == 0:
        error_triples.append(create_triple(p=default_dataset_predicate))
    else:
        triples_predicate = URIRef('http://rdfs.org/ns/void#triples')
        triples = sum([graph_objects(triples_predicate, o) for o in default_datasets], [])
        if len(triples) == 0:
            error_triples.append(create_triple(p=triples_predicate))

    return error_triples


def validate_class_partition(graph):

    error_triples = []

    class_partition = URIRef('http://rdfs.org/ns/void#classPartition')
    class_subjects = [o for o in graph.objects(predicate=class_partition)]
    class_predicates = [[p for p in graph.predicates(s)] for s in class_subjects]

    required_predicates = [
        URIRef('http://rdfs.org/ns/void#class'),
        URIRef('http://rdfs.org/ns/void#entities'),
    ]

    for predicates in class_predicates:
        missing_triples = [create_triple(p=rp) for rp in required_predicates if rp not in predicates]
        error_triples.extend(missing_triples)

    return error_triples


def validate_property_partition(graph):

    error_triples = []

    property_partition = URIRef('http://rdfs.org/ns/void#propertyPartition')
    property_subjects = [o for o in graph.objects(predicate=property_partition)]
    property_predicates = [[p for p in graph.predicates(s)] for s in property_subjects]

    required_predicates = [
        URIRef('http://rdfs.org/ns/void#property'),
        URIRef('http://rdfs.org/ns/void#triples'),
    ]

    for predicates in property_predicates:
        missing_triples = [create_triple(p=rp) for rp in required_predicates if rp not in predicates]
        error_triples.extend(missing_triples)

    return error_triples


class GraphValidationError(Exception):
    pass


def validate_graph(graph):

    errors = []
    errors.extend([error_message('metadata', t) for t in validate_meta_data(graph)])

    if 0 < len(errors):
        message = 'Validation failed.\n' + '\n'.join(['Reason: ' + e for e in errors])
        raise GraphValidationError(auto_encode(message))

    warns = []
    warns.extend([error_message('ClassPartition', t) for t in validate_class_partition(graph)])
    warns.extend([error_message('PropertyPartition', t) for t in validate_property_partition(graph)])

    if 0 < len(warns):
        message = '\n'.join(['Warn: ' + w for w in warns])
        print(auto_encode(message))
