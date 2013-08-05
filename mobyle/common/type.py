# -*- coding: utf-8 -*-
"""
Created on Mar 7, 2013

@author: Olivia Doppelt-Azeroual
@contact: odoppelt@pasteur.fr
@organization: Institut Pasteur, CIB
@license: GPLv3
"""

from mf.annotation import mf_decorator

from mobyle.common.connection import connection
from mobyle.common.term import Term

@mf_decorator
@connection.register
class Type(Term):
    """
    type information for data based on EDAM ontology
    """
    __collection__ = 'types'
    structure = {
        'has_topic': [basestring],
        'is_identifier_of': [basestring]
        }

@mf_decorator
@connection.register
class Format(Term):
    """
    format information based on EDAM ontology
    """
    __collection__ = 'formats'

    structure = {
        'is_format_of': [basestring]
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
