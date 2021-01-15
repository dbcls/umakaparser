from rdflib import URIRef
import i18n
from click import UsageError


def validate_meta_data(graph):

    errors = []

    def error_message(predicate=None):
        item = str(predicate).split('#')[1]
        message = i18n.t('cmd.build.error_validation_required', cause='metadata', item=item)
        info = '(predicate = {})'.format(predicate)
        return message + info

    def graph_objects(predicate=None, subject=None):
        return [o for o in graph.objects(subject, predicate)]

    endpoint_predicate = URIRef('http://www.w3.org/ns/sparql-service-description#endpoint')
    endpoints = graph_objects(endpoint_predicate)
    if len(endpoints) == 0:
        errors.append(error_message(endpoint_predicate))

    clawl_log_predicate = URIRef('http://sparqlbuilder.org/2015/09/rdf-metadata-schema#crawlLog')
    clawl_logs = graph_objects(clawl_log_predicate)
    if len(clawl_logs) == 0:
        errors.append(error_message(clawl_log_predicate))
    else:
        clawl_start_time_predicate = URIRef('http://sparqlbuilder.org/2015/09/rdf-metadata-schema#crawlStartTime')
        clawl_start_times = sum([graph_objects(clawl_start_time_predicate, o) for o in clawl_logs], [])
        if len(clawl_start_times) == 0:
            errors.append(error_message(clawl_start_time_predicate))

    default_dataset_predicate = URIRef('http://www.w3.org/ns/sparql-service-description#defaultDataset')
    default_datasets = graph_objects(default_dataset_predicate)
    if len(default_datasets) == 0:
        errors.append(error_message(default_dataset_predicate))
    else:
        triples_predicate = URIRef('http://rdfs.org/ns/void#triples')
        triples = sum([graph_objects(triples_predicate, o) for o in default_datasets], [])
        if len(triples) == 0:
            errors.append(error_message(triples_predicate))

    return errors


def validate_class_partition(graph):

    errors = []

    def error_message(subject=None, predicate=None):
        item = str(predicate).split('#')[1]
        message = i18n.t('cmd.build.error_validation_required', cause='ClassPartition', item=item)
        info = '(subject = {}, predicate = {})'.format(subject, predicate)
        return message + ' ' + info

    class_partition = URIRef('http://rdfs.org/ns/void#classPartition')
    class_subjects = [o for o in graph.objects(predicate=class_partition)]
    class_predicates = [[p for p in graph.predicates(s)] for s in class_subjects]

    required_predicates = [
        URIRef('http://rdfs.org/ns/void#class'),
        URIRef('http://rdfs.org/ns/void#entities'),
    ]

    for rp in required_predicates:
        for subject, predicates in zip(class_subjects, class_predicates):
            filterd_predicates = [p for p in predicates if p == rp]
            if len(filterd_predicates) == 0:
                errors.append(error_message(subject, rp))

    return errors


def validate_property_partition(graph):

    errors = []

    def error_message(predicate=None):
        item = str(predicate).split('#')[1]
        message = i18n.t('cmd.build.error_validation_required', cause='PropertyPartition', item=item)
        info = '(predicate = {})'.format(predicate)
        return message + ' ' + info

    property_partition = URIRef('http://rdfs.org/ns/void#propertyPartition')
    property_subjects = [o for o in graph.objects(predicate=property_partition)]
    property_predicates = [[p for p in graph.predicates(s)] for s in property_subjects]

    required_predicates = [
        URIRef('http://rdfs.org/ns/void#triples'),
    ]

    for rp in required_predicates:
        for subject, predicates in zip(property_subjects, property_predicates):
            filterd_predicates = [p for p in predicates if p == rp]
            if len(filterd_predicates) == 0:
                errors.append(error_message(subject, rp))

    return errors


def validate_graph(graph):

    errors = []
    errors.extend(validate_meta_data(graph))

    if 0 < len(errors):
        raise UsageError('Validation failed.\n' + '\n'.join(['Cause: ' + e for e in errors]))

    warns = []
    warns.extend(validate_class_partition(graph))
    warns.extend(validate_property_partition(graph))

    for w in warns:
        print('Warn: ' + w)
