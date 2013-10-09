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

from mongokit import SchemaDocument, OR
from .term import FormatTerm, DataTerm

class AbstractData(SchemaDocument):
    """
    Abstract super class for all kinds of data
    """
    
    use_dot_notation = True

    structure = {
                 "data_terms": [basestring]
                }
    @property
    def schema(self):
        return {'type':self._type}

    def to_json(self):
        return json.dumps(dict(self.items() + {'schema': self.schema}.items()))

class SimpleData(AbstractData):
    """
    A data which has a simple data/format definition
    """

    structure = {
                 'value': None
                }    

class BooleanData(SimpleData):
    """
    A boolean data
    """
    _type='boolean'

class IntegerData(SimpleData):
    """
    A boolean data
    """
    _type='integer'

class FloatData(SimpleData):
    """
    A boolean data
    """
    _type='float'

class StringData(SimpleData):
    """
    A boolean data
    """
    _type='float'

class FormattedData(SimpleData):
    """
    A boolean data
    """
    _type='formatted'
    structure = {
                 "format_term": basestring
                }

    @property
    def schema(self):
        d = super(FormattedData, self).schema
        d['format'] = self.format_term
        return d

class ArrayData(AbstractData):
    """
    A data formed by a array of data items sharing the same type/format
    """

    structure = {
                 'value':[AbstractData],
                }

    _type = 'array' 

    @property
    def schema(self):
        d = super(ArrayData, self).schema
        d['items'] = self.value[0].schema
        return d

class ObjectData(AbstractData):
    """
    A data formed by a object containing properties referencing different data
    """

    structure = {'properties':{basestring:AbstractData},
                }

    _type = 'object'

    @property
    def schema(self):
        d = super(ObjectData, self).schema
        d['properties'] = {property: value.schema \
                  for (property, value) in self.properties.items()}
        return d

#el1 = BooleanData()
#el1.value = True
#el2 = IntegerData()
#el2.value = 2
#el3 = ObjectData()
#el3.properties['b'] = el1
#el3.properties['c'] = el2
#for el in [el1, el2, el3]:
#    print el.to_json()
#    print el.schema
