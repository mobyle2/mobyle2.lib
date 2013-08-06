# -*- coding: utf-8 -*-

import pymongo
import unittest
import os.path

from mobyle.common.config import Config

config = Config( os.path.join( os.path.dirname(__file__), 'test.conf'))

from mongokit import ValidationError

from mobyle.common.connection  import connection
from mobyle.common.type import *




class TestType(unittest.TestCase):
    """ Tests for the Type class
    """

    def setUp(self):
        objects = connection.Type.find({})
        for object in objects:
            object.delete()
            
    def tearDown(self):
        objects = connection.Type.find({})
        for object in objects:
            object.delete()


    def test_insert(self):
         """
        test basic creation of a fake EDAM type
        """
         typetest = connection.Type()
         typetest['id'] = "test_type"
         typetest.save()
         types_list = connection.Type.find({'id':'test_type'})
         count = 0
         for typetest in types_list:
             count+=1
         self.assertEqual(count,1)
    
