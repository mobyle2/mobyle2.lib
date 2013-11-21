# -*- coding: utf-8 -*-
'''
Created on Nov. 12, 2012

@author: O. Doppelt
@author: E. Legros
@author: H. Menager
@author: B. Neron
@author: O. Sallou
@license: GPLv3
'''

from .mk_struct import MKStruct, MKStructAdapter
from .type import *

class AbstractData(MKStruct):
    """
    Abstract super class for all kinds of data
    """
    
    structure = {
                 "_type": unicode,
                 "type": TypeAdapter() 
                }

    def check_value(self):
        raise NotImplementedError()

class RefData(AbstractData):
    """
    A data whose value is stored on the file system
    """

    structure = {'path': basestring,
                 'size': int
                }

class ValueData(AbstractData):
    """
    A data whose value is stored directly in the object
    """

    structure = {
                 'value':any
                }

    def check_value(self):
        self['type'].check_value(self['value'])

class ListData(AbstractData):
    """
    A data formed by a list of data sharing the same type/format
    """

    structure = {
                 'value':[MKStructAdapter(MKStruct)]
                }

class StructData(AbstractData):
    """
    A data formed by a list properties referencing different data
    """

    structure = {
                 'properties':{basestring:MKStructAdapter(MKStruct)}
                }

