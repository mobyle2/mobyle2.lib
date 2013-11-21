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

    def __init__(self, values={}):
        MKStruct.__init__(self, values=values)
        self['_type'] = _CLASS_TO_TYPE[self.__class__]

    def __repr__(self):
        return "[%s]%s" % (self.__class__.__name__,dict(self)) 

    def check_value(self, value):
        raise NotImplementedError()

class BooleanType(Type):
    """
    A boolean
    """
    structure = {
                 'default':bool
                }

    def check_value(self, value):
        if not(type(value)==bool):
            raise TypeError("value %s is not an boolean" % value)

class IntegerType(Type):
    """
    An integer
    """
    def check_value(self, value):
        if not(type(value)==int):
            raise TypeError("value %s is not an integer" % value)

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
