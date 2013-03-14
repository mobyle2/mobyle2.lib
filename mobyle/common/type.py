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

from .connection import connection
from .config import Config


class AbstractType(Document):
    """
    Abstract class for type information based on EDAM ontology
    """

    __collection__ = 'type'
    __database__ = Config.config().get('app:main','db_name')

    structure = {
        'id': basestring,
        'label': basestring,
        'definition': basestring,
        'synonyms': [basestring]
        }

@mf_decorator
@connection.register
class Type(AbstractType):
    """
    type information based on EDAM ontology
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
        'comments': basestring, 
        'synonyms': [basestring], 
        'isFormatOf': [Type]
        }

@mf_decorator
@connection.register
class Format(AbstractFormat):
    """
    format information based on EDAM ontology
    """
    __collection__ = 'format'
    __database__ = Config.config().get('app:main','db_name')

    structure = {
        'subclassOf': [AbstractFormat]
        }

