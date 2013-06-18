# -*- coding: utf-8 -*-
"""
Created on Mar 7, 2013

@author: Olivia Doppelt-Azeroual
@contact: odoppelt@pasteur.fr
@organization: Institut Pasteur, CIB
@license: GPLv3
"""

from mongokit import Document

from mf.annotation import mf_decorator

from mobyle.common.connection import connection
from mobyle.common.config import Config


class AbstractType(Document):
    """
    Abstract class for type information based on EDAM ontology
    """

    __collection__ = 'types'
    __database__ = Config.config().get('app:main','db_name')

    structure = {
        'id': basestring,
        'name': basestring,
        'definition': basestring,
        'synonyms': [basestring],
        'is_obsolete': bool
        }

@mf_decorator
@connection.register
class Type(AbstractType):
    """
    type information for data based on EDAM ontology
    """


    structure = {
        'subclassOf': [AbstractType]
        }

class AbstractFormat(Document):
    """
    Abstract class for format information based on EDAM ontology
    """
    structure = {
        'id': basestring,
        'name': basestring,
        'definition': basestring,
        'comment': basestring, 
        'synonyms': [basestring], 
        'isFormatOf': [Type]
        }

@mf_decorator
@connection.register
class Format(AbstractFormat):
    """
    format information based on EDAM ontology
    """
    __collection__ = 'formats'
    __database__ = Config.config().get('app:main','db_name')

    structure = {
        'subclassOf': [AbstractFormat]
        }

    
#    Voir si nécéssaire plus tard
    # default_values = {}
    # required_fields = [ 'id']
    
    # indexes = [
    #     {
    #         'fields':[id],
    #         'unique':True
    #         }
    #     ]
