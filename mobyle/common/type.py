# -*- coding: utf-8 -*-
'''
Created on Nov. 13, 2013

@license: GPLv3
'''
from mongokit import CustomType

from .mk_struct import MKStruct, MKStructAdapter

# pylint: disable=W0201,R0904,R0913

class Type(MKStruct):
    """
    A superclass representing any of the types
    """
    structure = {
                 '_type':None,
                 'data_terms':[],
                 'default':None
                }

    def to_bson(self):
        value = self
        value['_type'] = _CLASS_TO_TYPE[value.__class__]
        if value is not None:
            return dict(value)

    @classmethod
    def to_python(cls, value):
        return cls(value)

    def __repr__(self):
        return "[%s]%s" % (self.__class__.__name__,dict(self)) 

class BooleanType(Type):
    """
    A boolean
    """
    structure = {
                 'default':bool
                }

class IntegerType(Type):
    """
    An integer
    """
    pass

class FloatType(Type):
    """
    A float
    """
    pass

class StringType(Type):
    """
    A string
    """
    structure = {
                 'options':[]
                }
    pass

class FormattedType(Type):
    """
    Type describing data formatted according to an EDAM reference
    """
    structure = {
                 'format_terms':[]
                }

class ArrayType(Type):
    """
    Type describing data formed by a array of data items sharing
    the same type/format
    """
    structure = {
                 'items_type':[]
                }

class StructType(Type):
    """
    Type describing data formed by a object containing properties
    referencing different data
    """
    structure = {
                 'properties':{}
                }

    def to_bson(self):
        bson_struct = super(StructType, self).to_bson()
        bson_struct['properties']={}
        for key, value in self['properties'].items():
            bson_struct['properties'][key]=value.to_bson()
        return bson_struct

    @classmethod
    def to_python(cls, value):
        obj = cls(value)
        obj['properties']={}
        for key, value in value['properties'].items():
            obj['properties'][key]=TypeAdapter.to_python(value)
        return obj

_TYPE_TO_CLASS = {
        None: Type,
        'boolean': BooleanType,
        'integer': IntegerType,
        'float': FloatType,
        'string': StringType,
        'formatted': FormattedType,
        'array': ArrayType,
        'struct': StructType
    }

_CLASS_TO_TYPE = dict((v, k) for k, v in _TYPE_TO_CLASS.iteritems())

class TypeAdapter(CustomType):

    mongo_type = dict
    python_type = Type
 
    def to_bson(self, value):
        if value is not None:
            return value.to_bson()
    
    @staticmethod
    def to_python(value):
        if value is not None:
            return _TYPE_TO_CLASS[value["_type"]].to_python(value)
