# -*- coding: utf-8 -*-
"""
Created on Mar 7, 2013

@author: Olivia Doppelt-Azeroual
@contact: odoppelt@pasteur.fr
@author: Hervé Ménager
@contact: hmenager@pasteur.fr
@organization: Institut Pasteur, CIB
@license: GPLv3
"""

from mf.annotation import mf_decorator

from mobyle.common.connection import connection
from mobyle.common.term import Term

@mf_decorator
@connection.register
class Topic(Term):
    """
    Topic term
    in EDAM: "A general bioinformatics subject or category, such as a field of
    study, data, processing, analysis or technology"
    """
    __collection__ = 'topics'

Topic.search_by('id')
