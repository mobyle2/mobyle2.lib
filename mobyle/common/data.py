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

from mongokit import SchemaDocument
from .type import *


class AbstractData(SchemaDocument):
    """
    Abstract super class for all kinds of data
    """

    structure = {
                 "_type": unicode,
                 "type": Type
                }

    def check_value(self):
        raise NotImplementedError()


@connection.register
class RefData(AbstractData):
    """
    A data whose value is stored on the file system
    """

    structure = {'path': basestring,
                 'size': int
                }


@connection.register
class ValueData(AbstractData):
    """
    A data whose value is stored directly in the object
    """

    structure = {
                 'value': None
                }

    def check_value(self):
        self['type'].check_value(self['value'])


@connection.register
class ListData(AbstractData):
    """
    A data formed by a list of data sharing the same type/format
    """

    structure = {
                 'value': [AbstractData]
                }


@connection.register
class StructData(AbstractData):
    """
    A data formed by a list properties referencing different data
    """

    structure = {
                 'properties': {basestring: AbstractData}
                }

