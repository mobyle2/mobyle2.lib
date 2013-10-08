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

from mf.annotation import mf_decorator

from mobyle.common.connection import connection
from mobyle.common.config import Config

from mf.views import MF_READ, MF_EDIT

class AbstractTerm(Document):
    """
    Abstract class for term storage
    should not be used to define Term classes,
    please inherit from Term class instead
    """

    __database__ = Config.config().get('app:main','db_name')

    structure = {
        'id': basestring,
        'name': basestring,
        'definition': basestring,
        'synonyms': [basestring],
        'comment': basestring,
        'is_obsolete': bool
        }

    def my(self, control, request, authenticated_userid=None):
        user = connection.User.find_one({'email' : authenticated_userid})
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
        'subclassOf': [AbstractTerm]
        }
    indexes = [
         {
             'fields':'subclassOf',
             'unique':False,
         },
     ]

@mf_decorator
@connection.register
class DataTerm(Term):
    """
    type information for data based on EDAM ontology
    """
    #__collection__ = 'types'
    structure = {
        'has_topic': [basestring],
        'is_identifier_of': [basestring]
        }

DataTerm.search_by('id')

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
    in EDAM: "A function or process performed by a tool; what is done, but not (typically) how or in what context"
    """
    #__collection__ = 'operations'

    structure = {
        'has_input': [DataTerm],
        'has_output': [DataTerm],
        'has_topic': [TopicTerm]
    }

OperationTerm.search_by('id')
