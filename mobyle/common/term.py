# -*- coding: utf-8 -*-
"""
Created on Mar 7, 2013

@author: Olivia Doppelt-Azeroual
@author: Hervé Ménager
@contact: odoppelt@pasteur.fr
@contact: hmenager@pasteur.fr
@organization: Institut Pasteur, CIB
@license: GPLv3
"""

from mongokit import Document
from itertools import chain

from mf.annotation import mf_decorator

from mobyle.common.connection import connection
from mobyle.common.config import Config

from mf.views import MF_READ


class AbstractTerm(Document):
    """
    Abstract class for term storage
    should not be used to define Term classes,
    please inherit from Term class instead
    """

    __database__ = Config.config().get('app:main', 'db_name')

    structure = {
        'id': basestring,
        'name': basestring,
        'definition': basestring,
        'synonyms': [basestring],
        'comment': basestring,
        'is_obsolete': bool
        }

    def my(self, control, request, authenticated_userid=None):
        user = connection.User.find_one({'email': authenticated_userid})
        admin_mode = 'adminmode' in request.session
        if control == MF_READ or (user and user['admin'] and admin_mode):
            return {}
        else:
            return None


@mf_decorator
@connection.register
class Term(AbstractTerm):
    """
    Term information storage, including subclass references
    """
    __collection__ = 'terms'

    structure = {
        '_type': unicode,
        'subclassOf': [basestring]
        }
    indexes = [
         {
             'fields':'subclassOf',
             'unique':False,
         },
     ]

    def self_and_ancestors_list(self):
        """
        Retrieve a flattened list of the term and all its ancestors
        """
        terms = [self]
        for superclass_id in self['subclassOf']:
            superclass_terms = connection.Term.fetch_one(
                {'id': superclass_id}).self_and_ancestors_list()
            for term in superclass_terms:
                if term not in terms:
                    terms.append(term)
        return terms


@mf_decorator
@connection.register
class DataTerm(Term):
    """
    type information for data based on EDAM ontology
    """
    #__collection__ = 'types'
    structure = {
        'has_topic': [basestring],
        }

DataTerm.search_by('id')


@mf_decorator
@connection.register
class IdentifierTerm(DataTerm):
    """
    type identifier information for data based on EDAM ontology
    """
    #__collection__ = 'types'
    structure = {
        'is_identifier_of': [basestring]
        }

IdentifierTerm.search_by('id')


@mf_decorator
@connection.register
class FormatTerm(Term):
    """
    format information based on EDAM ontology
    """
    #__collection__ = 'formats'

    structure = {
        'is_format_of': [basestring]
        }

    def represents_dataterms(self):
        """
        Retrieve a flattened list of the data terms
        it can represent (using terms hierarchy)
        """
        data_terms = []
        format_terms_hierarchy = self.self_and_ancestors_list()
        for format_term in format_terms_hierarchy:
            for format_id in format_term['is_format_of']:
                data_term = connection.DataTerm.fetch_one(
                                {'id': format_id})
                for data_term_item in data_term.self_and_ancestors_list():
                    if data_term_item not in data_terms:
                        data_terms.append(data_term_item)
        return data_terms


FormatTerm.search_by('id')


@mf_decorator
@connection.register
class TopicTerm(Term):
    """
    Topic term
    in EDAM: "A general bioinformatics subject or category, such as a field of
    study, data, processing, analysis or technology"
    """
    #__collection__ = 'topics'

TopicTerm.search_by('id')


@mf_decorator
@connection.register
class OperationTerm(Term):
    """
    Operation term
    in EDAM: "A function or process performed by a tool; what is done,
    but not (typically) how or in what context"
    """
    #__collection__ = 'operations'

    structure = {
        'has_input': [basestring],
        'has_output': [basestring],
        'has_topic': [basestring]
    }

OperationTerm.search_by('id')
