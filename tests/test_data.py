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
    
    def test_expr_value(self):
        v = ValueData()
        v['type'] = IntegerType()
        v['value'] = 1
        self.assertEqual(v.expr_value(),1)
        v = ValueData()
        v['type'] = StringType()
        v['value'] = 'foo'
        self.assertEqual(v.expr_value(),'foo')
        v = RefData()
        v['type'] = FormattedType()
        v['path'] = 'foo.txt'
        self.assertEqual(v.expr_value(),'foo.txt')
        v = ListData()
        v['type'] = ArrayType(StringType())
        el1 = ValueData()
        el1['type'] = StringType()
        el1['value'] = 'foo'
        el2 = ValueData()
        el2['type'] = StringType()
        el2['value'] = 'bar'
        v['value'] = [el1, el2]
        self.assertEqual(v.expr_value(),['foo', 'bar'])
        v = StructData()
        v['type'] = StructType()
        el1 = ValueData()
        el1['type'] = IntegerType()
        el1['value'] = 2
        el2 = ValueData()
        el2['type'] = StringType()
        el2['value'] = 'bar'
        v['properties'] = {'integer':el1, 'string': el2}
        print v['properties']
        self.assertEqual(v.expr_value(),{'integer':2, 'string':'bar'})

if __name__=='__main__':
    unittest.main()

