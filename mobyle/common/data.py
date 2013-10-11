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
import json, sys, inspect

from .term import FormatTerm, DataTerm


class AbstractData(SchemaDocument):
    """
    Abstract super class for all kinds of data
    """
    
    use_dot_notation = True

    structure = {
                 "data_terms": [basestring]
                }
    _type=None

    @property
    def schema(self):
        """
        get the schema for this data object
        
        :returns: the schema for the data object
        :rtype: dict
        """
        return {'type':self._type}

    def load_from_schema(self, contents_dict=None):
        """
        load prototype contents for the object from its properties schema 
        :param contents_dict: the contents dictionary
        :type contents_dict: dict
        """
        return

    def to_json(self):
        """
        serialize the object from its properties schema 
        :param contents_dict: the contents dictionary
        :type contents_dict: dict
        """
        return json.dumps({'schema': self.schema})

class SimpleData(AbstractData):
    """
    A data which has a simple data/format definition
    """

    structure = {
                 'value': basestring
                }    

class BooleanData(SimpleData):
    """
    A boolean data
    """
    _type='boolean'

class IntegerData(SimpleData):
    """
    An integer
    """
    _type='integer'

class FloatData(SimpleData):
    """
    A float
    """
    _type='float'

class StringData(SimpleData):
    """
    A string
    """
    _type='string'

class FormattedData(SimpleData):
    """
    Data formatted according to an EDAM reference
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

    def load_from_schema(self, d=None):
        for p, v in d["properties"].items():
            self.properties[p] = v	
        
    @property
    def schema(self):
        d = super(ObjectData, self).schema
        d['properties'] = {property: value.schema \
                  for (property, value) in self.properties.items()}
        return d

class DataJSONDecoder(json.JSONDecoder):

    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.dict_to_object)
	data_classes = inspect.getmembers(sys.modules[__name__], lambda member: inspect.isclass(member) and member.__module__ == __name__)
        self.map = {}
	for name, cls in data_classes:
            if hasattr(cls, '_type'):
	        self.map[cls._type] = cls

    def dict_to_object(self, d):
        if d.has_key("type"):
            t = self.map[d["type"]](d)
            t.load_from_schema(d)
        else:
            t = d
        return t
"""
el1 = BooleanData()
el1.value = True
el2 = IntegerData()
el2.value = 2
el3 = ObjectData()
el3.properties['b'] = el1
el3.properties['c'] = el2
decoder = DataJSONDecoder()
for el in [el1, el2, el3]:
    print "#  ", el.to_json()	
    print "## ", json.dumps(el.schema)
    print "###", type(decoder.decode(json.dumps(el.schema)))
o = decoder.decode(json.dumps(el.schema))
"""
