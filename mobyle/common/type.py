# -*- coding: utf-8 -*-
'''
Created on Nov. 13, 2013

@license: GPLv3
'''
from mongokit import CustomType

# pylint: disable=W0201,R0904,R0913

class _Type(object):
    """
    A superclass representing any of the types
    """

    def __init__(self, dict_repr=None):
        self._type = _CLASS_TO_TYPE[self.__class__]
        self.data_terms = []
        if dict_repr:
            self.set_structure(dict_repr)

    def encode(self):
        """
        encode this object as a python dictionary
        """
        return {'_type': _CLASS_TO_TYPE[self.__class__],
                'data_terms': self.data_terms}
    
    def set_structure(self, dict_repr):
        """
        decode the properties of this object from a python dictionary
        """
        self.data_terms = dict_repr['data_terms']

class _SimpleType(_Type):
    """
    A type which has a simple data/format definition
    """
    pass

class BooleanType(_SimpleType):
    """
    A boolean
    """
    pass

class IntegerType(_SimpleType):
    """
    An integer
    """
    pass

class FloatType(_SimpleType):
    """
    A float
    """
    pass

class StringType(_SimpleType):
    """
    A string
    """
    pass

class FormattedType(_SimpleType):
    """
    Type describing data formatted according to an EDAM reference
    """

    def encode(self):
        dict_repr = super(FormattedType, self).encode()
        dict_repr['format_term'] = self.format_term
        return dict_repr
    
    def set_structure(self, dict_repr):
        super(FormattedType, self).set_structure(dict_repr)
        self.format_term = dict_repr['format_term']

class ArrayType(_Type):
    """
    Type describing data formed by a array of data items sharing
    the same type/format
    """

    def encode(self):
        dict_repr = super(ArrayType, self).encode()
        dict_repr['items_type'] = self.items_type.encode()
        return dict_repr
    
    def set_structure(self, dict_repr):
        super(ArrayType, self).set_structure(dict_repr)
        self.items_type = get_type(dict_repr['items_type'])


class StructType(_Type):
    """
    Type describing data formed by a object containing properties
    referencing different data
    """

    def encode(self):
        dict_repr = super(StructType, self).encode()
        dict_repr['properties'] = {}
        for property_name, property_type in self.properties.items():
            dict_repr['properties'][property_name] = property_type.encode()
        return dict_repr

    
    def set_structure(self, dict_repr):
        super(StructType, self).set_structure(dict_repr)
        self.properties = {}
        for property_name, property_type in dict_repr['properties'].items():
            self.properties[property_name] = get_type(property_type)

_TYPE_TO_CLASS = {
        None: _Type,
        'boolean': BooleanType,
        'integer': IntegerType,
        'float': FloatType,
        'string': StringType,
        'formatted': FormattedType,
        'array': ArrayType,
        'struct': StructType
    }

_CLASS_TO_TYPE = dict((v, k) for k, v in _TYPE_TO_CLASS.iteritems())

def get_type(dict_repr):
    """
    factory function to get a type object from its dict representation
    """        
    type_object = _TYPE_TO_CLASS[dict_repr["_type"]](dict_repr=dict_repr)
    return type_object

class TypeAdapter(CustomType):
    
    mongo_type = dict
    python_type = _Type
 
    def to_bson(self, value):
        return value.encode()
    
    def to_python(self, value):
        if value is not None:
            return get_type(value)

