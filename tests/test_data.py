# -*- coding: utf-8 -*-

import unittest
import os.path
#a config object must be instantiated first for each entry point of the application
from mobyle.common.config import Config
config = Config( os.path.join( os.path.dirname(__file__), 'test.conf'))
from mobyle.common.data import *
from mobyle.common.type import *

class TestData(unittest.TestCase):

    def test_valueData(self):
        v = ValueData()
        v['type'] = IntegerType()
        with self.assertRaises(TypeError):
            v['value'] = 'ee'
            v.check_value()
        v['value'] = 3
        v.check_value()

if __name__=='__main__':
    unittest.main()

