# -*- coding: utf-8 -*-
'''
Created on Nov. 13, 2013

@license: GPLv3
'''
from mongokit import SchemaDocument
from .connection import connection
from .myaml import myaml

# pylint: disable=W0201,R0904,R0913

import json

@myaml.register
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

    @staticmethod
    def from_json(value):
        return value

@myaml.register
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

    @staticmethod
    def from_json(value):
        return json.loads(value)

@myaml.register
@connection.register
class IntegerType(Type):
    """
    An integer
    """
    structure = {
                 'min': int,
                 'max': int
                }

    def check_value(self, value):
        if not(type(value) == int):
            raise TypeError("value %s is not an integer" % value)
        if self['min'] is not None and value < self['min']:
            raise TypeError("value %s should be > to min value %s"
                % (value, self['min']))
        if self['max'] is not None and value > self['max']:
            raise TypeError("value %s should be < to max value %s"
                % (value, self['max']))


@myaml.register
@connection.register
class FloatType(Type):
    """
    A float
    """
    pass


@myaml.register
@connection.register
class StringType(Type):
    """
    A string
    """
    structure = {
                 'options': []
                }


@myaml.register
@connection.register
class FormattedType(Type):
    """
    Type describing data formatted according to an EDAM reference
    """
    structure = {
                 'format_terms': []
                }


@myaml.register
@connection.register
class ArrayType(Type):
    """
    Type describing data formed by a array of data items sharing
    the same type/format
    """
    structure = {
                 'items_type': Type
                }


@myaml.register
@connection.register
class StructType(Type):
    """
    Type describing data formed by a object containing properties
    referencing different data
    """
    structure = {
                 'properties': {unicode: Type}
                }
