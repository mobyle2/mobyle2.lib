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

class AbstractData(SchemaDocument):
    """
    Abstract super class for all kinds of data
    """
    
    use_dot_notation = True

    structure = {
                 "_type": unicode,
                }

    def get_format(self):
        raise NotImplementedError

    def get_type(self):
        raise NotImplementedError

    @staticmethod
    def get_instance(dict):
        #TODO instanciate the right AbstractData subclass instance
        # depending on the _type field
        pass

class SimpleData(AbstractData):
    """
    A data which has a simple type/format definition
    """

    structure = {'type': basestring,
                 'format': basestring,
                 #'_type': 'SimpleData',
                }

    def get_format(self):
        return self.format

    def get_type(self):
        return self.type

class RefData(SimpleData):
    """
    A data whose value is stored on the file system
    """

    structure = {'path': basestring,
                 'size': int
                 #'_type': 'RefData',
                }

class ValueData(SimpleData):
    """
    A data whose value is stored directly in the object
    """

    structure = {'value':basestring,
                 #'_type': 'ValueData',
                }

class ListData(AbstractData):
    """
    A data formed by a list of data sharing the same type/format
    """

    structure = {'value':[AbstractData],
                 #'_type': 'ListData',
                }

    def get_format(self):
        return self.value[0].get_format()

    def get_type(self):
        return self.value[0].get_type()

class StructData(AbstractData):
    """
    A data formed by a list properties referencing different data
    """

    structure = {'properties':{basestring:AbstractData},
                 #'_type': 'StructData',
                }

    def get_format(self):
        format = {property: value.get_format() \
                  for (property, value) in self.properties.items()}
        return format

    def get_type(self):
        typ = {property: value.get_type() \
               for (property, value) in self.properties.items()}
        return typ
