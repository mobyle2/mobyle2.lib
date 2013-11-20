# -*- coding: utf-8 -*-
'''
Created on Nov. 13, 2013

@license: GPLv3
'''

import unittest
import os.path

from mobyle.common.type import *
from mongokit import Document, SchemaDocument

from mobyle.common.config import Config
config = Config( os.path.join( os.path.dirname(__file__), 'test.conf'))

from mobyle.common.connection import connection

from mobyle.common.mk_struct import MKStruct, MKStructAdapter

class TestType(unittest.TestCase):
    """
    Test the Type class
    """

    def setUp(self):
        self.type = Type()
        self.type_adapter = TypeAdapter()
        self.data_terms = ['test', 'test2']
        self.type['data_terms'] = self.data_terms
        self.encoded_type = self.type_adapter.to_bson(self.type)
        self.decoded_type = self.type_adapter.to_python(self.encoded_type)

    def test_encode(self):
        self.assertEqual(self.encoded_type,
                         {'_type':None,
                          'data_terms':self.data_terms})                

    def test_decode(self):
        self.assertIs(type(self.decoded_type),Type)
        self.assertIs(self.decoded_type['data_terms'],self.data_terms)

class TestBooleanType(unittest.TestCase):
    """
    Test the BooleanType class
    """

    def setUp(self):
        self.type = BooleanType()
        self.type_adapter = TypeAdapter()
        self.encoded_type = self.type_adapter.to_bson(self.type)
        self.decoded_type = self.type_adapter.to_python(self.encoded_type)

    def test_decode(self):
        self.assertIs(type(self.decoded_type),BooleanType)

class TestStructType(unittest.TestCase):
    """
    Test the StructType class
    """

    def setUp(self):
        self.type = StructType()
        self.type_adapter = TypeAdapter()
        self.properties = {'a':BooleanType(), 'b': BooleanType()}
        self.type['properties'] = self.properties
        self.encoded_type = self.type_adapter.to_bson(self.type)
        self.decoded_type = self.type_adapter.to_python(self.encoded_type)

    def test_encode(self):
        self.assertIs(type(self.encoded_type),dict)
        self.assertIs(type(self.encoded_type['properties']['a']),dict)
        self.assertIs(type(self.encoded_type['properties']['b']),dict)


    def test_decode(self):
        self.assertIs(type(self.decoded_type),StructType)
        self.assertIs(type(self.decoded_type['properties']['a']),BooleanType)
        self.assertIs(type(self.decoded_type['properties']['b']),BooleanType)

class TypeMKStruct(MKStruct):
    structure = {'nested_type':MKStructAdapter(BooleanType)}

@connection.register
class TypeAdapterDoc(Document):
    __collection__ = 'type_adapter_documents'
    __database__ = Config.config().get('app:main','db_name')
    structure = {'test_type':TypeAdapter(),
                 'test_schemadoc_type':MKStructAdapter(TypeMKStruct)}

class TestTypeAdapter(unittest.TestCase):
    """
    Test the "TypeAdapter" CustomType
    to make sure it is serializable/unserializable
    """

    def setUp(self):
        connection.TypeAdapterDoc.collection.remove({})

    def test_create_document(self):
        self.doc = connection.TypeAdapterDoc()
        self.doc.save()
        self.type = BooleanType()
        self.doc['test_type'] = self.type
        self.doc.save()
        self.doc['test_schemadoc_type'] = TypeMKStruct()
        self.doc.save()
        self.doc['test_schemadoc_type']['nested_type'] = self.type
        self.doc.save()
        self.doc2 = connection.TypeAdapterDoc.find_one()
        self.assertIs(type(self.doc2['test_type']),BooleanType)

if __name__=='__main__':
    unittest.main()
