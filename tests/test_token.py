# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import unittest
import os.path
#a config object must be instantiated first for each entry point of the application
from mobyle.common.config import Config
config = Config( os.path.join( os.path.dirname(__file__), 'test.conf'))

from mobyle.common.connection import connection
from mobyle.common.tokens import Token

class TestToken(unittest.TestCase):

    def setUp(self):
        objects = connection.Token.find({})
        for object in objects:
            object.delete()
       
    
    def test_valid_token(self):
        my_token = connection.Token()
        my_token.generate()
        my_token.save()
        token = my_token['token']
        self.assertTrue(my_token.check_validity())
        is_token = connection.Token.find_one({'token': token})
        self.assertEqual(is_token, None)

    def test_invalid_token(self):
        my_token = connection.Token()
        my_token.generate()
        # Go back in time to get an old timestamp
        my_token['timestamp'] = my_token['timestamp'] - timedelta(seconds=7200)
        my_token.save()
        token = my_token['token']
        self.assertFalse(my_token.check_validity())
        is_token = connection.Token.find_one({'token': token})
        self.assertEqual(is_token, None)


