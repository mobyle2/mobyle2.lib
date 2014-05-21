# -*- coding: utf-8 -*-

import unittest
from mobyle.common.eval_bool import *


class TestEvalBool(unittest.TestCase):

    def setUp(self):
        values = {'a': True, 'b': False, 'c': 1, 'd': 0}
        self.evaluator = EvalBoolFactory(values)

    def test_a_true(self):
        self.assertTrue(self.evaluator.test({'a': True}))

    def test_a_false(self):
        self.assertFalse(self.evaluator.test({'a': False}))

    def test_b_false(self):
        self.assertTrue(self.evaluator.test({'b': False}))

    def test_b_true(self):
        self.assertFalse(self.evaluator.test({'b': True}))

    def test_a_true_and_b_false(self):
        self.assertTrue(self.evaluator.test({'#and': [{'a': True},
            {'b': False}]}))

    def test_a_true_and_b_true(self):
        self.assertFalse(self.evaluator.test({'#and': [{'a': True},
            {'b': True}]}))

    def test_implicit_a_true_and_b_true(self):
        self.assertFalse(self.evaluator.test({'a': True, 'b': True}))

    def test_implicit_a_false_and_b_false(self):
        self.assertFalse(self.evaluator.test({'a': False, 'b': False}))

if __name__ == '__main__':
    unittest.main()

