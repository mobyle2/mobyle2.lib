# -*- coding: utf-8 -*-
"""
Created on May 28, 2013

@author: Olivia Doppelt-Azeroual
@contact: olivia.doppelt@pasteur.fr
@organization: Institut Pasteur, CIB
@license: GPLv3
"""

import re
import logging

import argparse
from rdflib import Graph
from rdflib.term import URIRef
from rdflib.resource import Resource
from rdflib.namespace import RDFS


from mobyle.common.config import Config

logger = logging.getLogger('mobyle.edam_integration')
logger.setLevel(logging.INFO)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=
                        "Integration of EDAM ontology in Mobyle2 DB")
    parser.add_argument('--config', help=
                        "path to the Mobyle2 config file for DB injection")
    parser.add_argument('--edamfile', help=
                        "path to EDAM ontology file (owl format) to process")
    parser.add_argument('--logfile', help=
                        "outputs each edam element in a file")
    parser.add_argument('action', choices=['init', 'update'], help=
                        "select which action to launch")
    args = parser.parse_args()

    if args.config:
        # Init config
        config = Config(args.config).config()
        # init db connection
        from mobyle.common.connection import connection
        from mobyle.common.term import DataTerm, FormatTerm,\
                                       OperationTerm, TopicTerm
        DataTerm = connection.DataTerm
        FormatTerm = connection.FormatTerm
        TopicTerm = connection.TopicTerm
        OperationTerm = connection.OperationTerm
        # action definition
        if args.action == 'init':
            # empty collections
            DataTerm.collection.drop()
            FormatTerm.collection.drop()
            TopicTerm.collection.drop()
            OperationTerm.collection.drop()
        else:
            pass
    else:
        from mobyle.common.term import DataTerm, FormatTerm,\
                                       OperationTerm, TopicTerm

    def get_edam_short_id(long_id):
        if long_id is None:
            return None
        return re.sub('http://edamontology.org/([a-zA-Z][a-zA-Z0-9]*)_([0-9]*)',
               'EDAM_\g<1>:\g<2>', long_id)

    g = Graph().parse(source=args.edamfile)

    for row in g.query("""
    SELECT ?class ?namespace ?name ?definition
           ?is_format_of ?has_topic ?is_identifier_of
    WHERE {
           ?class oboOther:namespace ?namespace .
           ?class rdfs:label ?name .
           OPTIONAL {
                      ?class oboInOwl:hasDefinition ?definition .
           }
    }
    """):

        namespace = str(row[1])
        if namespace == 'data':
            term = DataTerm()
        elif namespace == 'format':
            term = FormatTerm()
        elif namespace == 'topic':
            term = TopicTerm()
        elif namespace == 'operation':
            term = OperationTerm()
        else:
            continue

        long_id = row[0]
        name = row[2]
        definition = row[3]

        term['id'] = get_edam_short_id(long_id)
        term['name'] = name
        term['definition'] = definition

        synonyms = []
        for inner_row in g.query("""
            SELECT ?synonym WHERE {?class oboInOwl:hasExactSynonym ?synonym}
            """, initBindings={'class': long_id}):
            synonyms.append(get_edam_short_id(inner_row[0]))
        term['synonyms'] = synonyms

        superclasses = []
        for inner_row in g.query("""
            SELECT ?superclass WHERE {?class rdfs:subClassOf ?superclass.
                MINUS {
                ?class rdfs:subClassOf
                <http://www.geneontology.org/formats/oboInOwl#ObsoleteClass> .
                }
            }
            """, initBindings={'class': long_id}):
            superclasses.append(get_edam_short_id(inner_row[0]))
        term['subclassOf'] = superclasses

        is_format_of = []
        for inner_row in g.query("""
            SELECT ?is_format_of WHERE {
                      ?class rdfs:subClassOf ?format_sc .
                      ?format_sc owl:onProperty
                          <http://edamontology.org/is_format_of> .
                      ?format_sc owl:someValuesFrom ?is_format_of .
                      }
            """, initBindings={'class': long_id}):
            is_format_of.append(get_edam_short_id(inner_row[0]))
        if is_format_of:
            term['is_format_of'] = is_format_of

        has_topic = []
        for inner_row in g.query("""
            SELECT ?has_topic WHERE {
                      ?class rdfs:subClassOf ?format_sc .
                      ?format_sc owl:onProperty
                          <http://edamontology.org/has_topic> .
                      ?format_sc owl:someValuesFrom ?has_topic .
                      }
            """, initBindings={'class': long_id}):
            has_topic.append(get_edam_short_id(inner_row[0]))
        if has_topic:
            term['has_topic'] = has_topic
        term['is_obsolete'] = False

        # FIXME: exploring the ontology from top classes does not retrieve
        # obsolete classes which are not subclasses
        # of EDAM data, format, etc.
        if args.config:
            term.save()
        if args.logfile:
            log = open(args.logfile, 'a')
            log.write(term['id'])
            log.close()
