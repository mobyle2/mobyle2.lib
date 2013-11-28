# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import unittest
import os.path
from mobyle.common.config import Config
config = Config( os.path.join( os.path.dirname(__file__), 'test.conf'))

from mobyle.common.connection import connection
from mobyle.common.objectmanager import ObjectManager

class TestObjectManager(unittest.TestCase):
    
    def test_add_new_data(self):
        pass
