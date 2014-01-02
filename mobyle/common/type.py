# -*- coding: utf-8 -*-
'''
Created on Nov. 13, 2013

@license: GPLv3
'''
from mongokit import SchemaDocument
from .connection import connection

# pylint: disable=W0201,R0904,R0913


@connection.register
class Type(SchemaDocument):
    """
    A superclass representing any of the types
    """
    structure = {
                 'data_terms': [],
                 'default': None
                }

    def __repr__(self):
        return "[%s]%s" % (self.__class__.__name__, dict(self))

    def check_value(self, value):
        raise NotImplementedError()


@connection.register
class BooleanType(Type):
    """
    A boolean
    """
    structure = {
                 'default': bool
                }

    def check_value(self, value):
        if not(type(value) == bool):
            raise TypeError("value %s is not an boolean" % value)


@connection.register
class IntegerType(Type):
    """
    An integer
    """
    def check_value(self, value):
        if not(type(value) == int):
            raise TypeError("value %s is not an integer" % value)


@connection.register
class FloatType(Type):
    """
    A float
    """
    pass


@connection.register
class StringType(Type):
    """
    A string
    """
    structure = {
                 'options': []
                }


@connection.register
class FormattedType(Type):
    """
    Type describing data formatted according to an EDAM reference
    """
    structure = {
                 'format_terms': []
                }


@connection.register
class ArrayType(Type):
    """
    Type describing data formed by a array of data items sharing
    the same type/format
    """
    structure = {
                 'items_type': Type
                }


@connection.register
class StructType(Type):
    """
    Type describing data formed by a object containing properties
    referencing different data
    """
    structure = {
                 'properties': {unicode: Type}
                }