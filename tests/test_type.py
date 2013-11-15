# -*- coding: utf-8 -*-
'''
Created on Nov. 13, 2013

@license: GPLv3
'''

import unittest
import os.path

from mobyle.common.type import *
from mobyle.common.type import _Type
from mongokit import Document

from mobyle.common.config import Config
config = Config( os.path.join( os.path.dirname(__file__), 'test.conf'))

from mobyle.common.connection import connection

class TestType(unittest.TestCase):
    """
    Test the _Type class
    """

    def setUp(self):
        self.type = _Type()
        self.data_terms = ['test', 'test2']
	self.type.data_terms = self.data_terms
        self.encoded_type = self.type.encode()
        self.decoded_type = get_type(self.encoded_type)

    def test_encode(self):
	self.assertEqual(self.encoded_type,
                         {'_type':None,
                          'data_terms':self.data_terms})                


    def test_decode(self):
        self.assertIs(type(self.decoded_type),_Type)
        self.assertIs(self.decoded_type.data_terms,self.data_terms)

class TestBooleanType(unittest.TestCase):
    """
    Test the BooleanType class
    """

    def setUp(self):
        self.type = BooleanType()
        self.encoded_type = self.type.encode()
        self.decoded_type = get_type(self.encoded_type)

    def test_decode(self):
        self.assertIs(type(self.decoded_type),BooleanType)

class TestStructType(unittest.TestCase):
    """
    Test the StructType class
    """

    def setUp(self):
        self.type = StructType()
        self.properties = {'a':BooleanType(), 'b': BooleanType()}
        self.type.properties = self.properties
        self.encoded_type = self.type.encode()
        self.decoded_type = get_type(self.encoded_type)

    def test_decode(self):
        self.assertIs(type(self.encoded_type['properties']['a']),dict)
        self.assertIs(type(self.decoded_type.properties['a']),BooleanType)
        self.assertIs(type(self.decoded_type),StructType)
        self.assertIs(type(self.decoded_type.properties['a']),BooleanType)
        self.assertIs(type(self.decoded_type.properties['b']),BooleanType)



class TestTypeAdapter(unittest.TestCase):
    """
    Test the "TypeAdapter" CustomType
    to make sure it is serializable/unserializable
    """

    @connection.register     
    class TypeAdapterDoc(Document):
         use_dot_notation = True
         __collection__ = 'type_adapter_documents'
         __database__ = Config.config().get('app:main','db_name')
         structure = {'test_type':TypeAdapter()}

    def setUp(self):
        self.reset_db()

    def tearDown(self):
        self.reset_db()

    def reset_db(self):
        objects = connection.TypeAdapterDoc.find({})
        for object in objects:
            object.delete()

    def test_create_document(self):
        self.doc = connection.TypeAdapterDoc()
        self.type = BooleanType()
        self.doc.test_type = self.type
        self.doc.save()
        self.doc2 = connection.TypeAdapterDoc.find_one()
        self.assertIs(type(self.doc2.test_type),BooleanType)
        
    
if __name__=='__main__':
    unittest.main()

