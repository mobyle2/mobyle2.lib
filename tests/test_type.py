# -*- coding: utf-8 -*-
'''
Created on Nov. 13, 2013

@license: GPLv3
'''

import unittest
import os.path

from mobyle.common.type import *
from mobyle.common.data import *

from mongokit import Document

from mobyle.common.config import Config
config = Config(os.path.join(os.path.dirname(__file__), 'test.conf'))

from mobyle.common.connection import connection

@connection.register
class DummyType(Type):
    pass

@connection.register
class TypeContainer(Document):
    """
    Class used in this unit test module to test "Type" class
    """
    __collection__ = 'type_container_tests'
    __database__ = Config.config().get('app:main', 'db_name')

    structure = {
                 "_type": unicode,
                 "type": Type
                }


class TestType(unittest.TestCase):
    """
    Test the Type class
    """

    def setUp(self):
        connection.TypeContainer.collection.remove({})
        self.container = connection.TypeContainer()
        self.type = DummyType()
        self.data_terms = ['test', 'test2']
        self.type['data_terms'] = self.data_terms
        self.container['type'] = self.type
        self.container.save()
        self.loaded_type_container = connection.TypeContainer.fetch_one()

    def test_loaded_class_type(self):
        self.assertIs(type(self.loaded_type_container['type']), DummyType)


class TestBooleanType(unittest.TestCase):
    """
    Test the BooleanType class
    """

    def setUp(self):
        connection.TypeContainer.collection.remove({})
        self.container = connection.TypeContainer()
        self.type = BooleanType()
        self.data_terms = ['test', 'test2']
        self.type['data_terms'] = self.data_terms
        self.container['type'] = self.type
        self.container.save()
        self.loaded_type_container = connection.TypeContainer.fetch_one()

    def test_loaded_class_type(self):
        self.assertIs(type(self.loaded_type_container['type']), BooleanType)


class TestStructType(unittest.TestCase):
    """
    Test the StructType class
    """

    def setUp(self):
        connection.TypeContainer.collection.remove({})
        self.container = connection.TypeContainer()
        self.type = StructType()
        self.properties = {u'a': BooleanType(),
                           u'b': BooleanType()}
        self.type['properties'] = self.properties
        self.container['type'] = self.type
        self.container.save()
        self.loaded_type_container = connection.TypeContainer.fetch_one()

    def test_loaded_class_type(self):
        self.assertIs(type(self.loaded_type_container['type']), StructType)
        self.assertIs(
            type(self.loaded_type_container['type']['properties'][u'a']),
            BooleanType)
        self.assertIs(
            type(self.loaded_type_container['type']['properties'][u'b']),
            BooleanType)
if __name__=='__main__':
    unittest.main()
