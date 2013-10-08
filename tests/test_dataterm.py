# -*- coding: utf-8 -*-

import pymongo
import unittest
import os.path

from mobyle.common.config import Config

config = Config( os.path.join( os.path.dirname(__file__), 'test.conf'))

from mongokit import ValidationError

from mobyle.common.connection  import connection
from mobyle.common.term import *




class TestDataTerm(unittest.TestCase):
    """ Tests for the DataTerm class
    """

    def setUp(self):
        objects = connection.DataTerm.find({})
        for object in objects:
            object.delete()
            
    def tearDown(self):
        objects = connection.DataTerm.find({})
        for object in objects:
            object.delete()


    def test_insert(self):
         """
        test basic creation of a fake EDAM data term
        """
         data_term_test = connection.DataTerm()
         data_term_test['id'] = "test_data_term"
         data_term_test.save()
         data_terms_list = connection.DataTerm.find({'id':'test_data_term'})
         count = 0
         for data_term_test in data_terms_list:
             count+=1
         self.assertEqual(count,1)
    
