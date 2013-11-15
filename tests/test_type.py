# -*- coding: utf-8 -*-
'''
Created on Nov. 13, 2013

@license: GPLv3
'''

import unittest

from mobyle.common.type import _Type
from mobyle.common.type import *

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
        self.assertEqual(type(self.decoded_type),_Type)
        self.assertEqual(self.decoded_type.data_terms,self.data_terms)

class TestBooleanType(unittest.TestCase):
    """
    Test the BooleanType class
    """

    def setUp(self):
        self.type = BooleanType()
        self.encoded_type = self.type.encode()
        self.decoded_type = get_type(self.encoded_type)

    def test_decode(self):
        self.assertEqual(type(self.decoded_type),BooleanType)

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
        self.assertEqual(type(self.encoded_type['properties']['a']),dict)
        self.assertEqual(type(self.decoded_type.properties['a']),BooleanType)
        self.assertEqual(type(self.decoded_type),StructType)
        self.assertEqual(type(self.decoded_type.properties['a']),BooleanType)
        self.assertEqual(type(self.decoded_type.properties['b']),BooleanType)

if __name__=='__main__':
    unittest.main()

