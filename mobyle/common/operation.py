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
from mobyle.common.type import Type
from mobyle.common.topic import Topic

@mf_decorator
@connection.register
class Operation(Term):
    """
    Operation term
    in EDAM: "A function or process performed by a tool; what is done, but not (typically) how or in what context"
    """
    __collection__ = 'operations'

    structure = {
        'has_input': [Type],
        'has_output': [Type]
        'has_topic': [Topic]
    }

