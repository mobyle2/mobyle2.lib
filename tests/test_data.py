# -*- coding: utf-8 -*-

import unittest
import os.path
#a config object must be instantiated first for each entry point of the application
from mobyle.common.config import Config
config = Config( os.path.join( os.path.dirname(__file__), 'test.conf'))
from mobyle.common.data import *

class TestData(unittest.TestCase):

    def setUp(self):
        v = ValueData()
        v.value = '3'
        v.type = 'int'
        v.format = 'int en string'

if __name__=='__main__':
    unittest.main()

