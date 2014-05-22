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

    def test_a_true_or_b_true(self):
        self.assertTrue(self.evaluator.test({'#or': [{'a': True},
            {'b': True}]}))

    def test_not_a_false(self):
        self.assertTrue(self.evaluator.test({'#not': {'a': False}}))

    def test_not_a_true(self):
        self.assertFalse(self.evaluator.test({'#not': {'a': True}}))

    def test_a_false_nor_b_true(self):
        self.assertTrue(self.evaluator.test({'#nor': [{'a': False},
            {'b': True}]}))

    def test_a_true_nor_b_true(self):
        self.assertFalse(self.evaluator.test({'#nor': [{'a': True},
            {'b': True}]}))

    def test_c_1(self):
        self.assertTrue(self.evaluator.test({'c': 1}))

    def test_c_gte_1(self):
        self.assertTrue(self.evaluator.test({'c': {'#gte': 1}}))

    def test_c_gt_1(self):
        self.assertFalse(self.evaluator.test({'c': {'#gt': 1}}))

    def test_c_lte_1(self):
        self.assertTrue(self.evaluator.test({'c': {'#lte': 1}}))

    def test_c_lt_1(self):
        self.assertFalse(self.evaluator.test({'c': {'#lt': 1}}))

    def test_c_in_0_1(self):
        self.assertTrue(self.evaluator.test({'c': {'#in': [0, 1]}}))

    def test_c_in_minus1_0(self):
        self.assertFalse(self.evaluator.test({'c': {'#in': [-1, 0]}}))

    def test_c_nin_minus1_0(self):
        self.assertTrue(self.evaluator.test({'c': {'#nin': [-1, 0]}}))

    def test_c_nin_0_1(self):
        self.assertFalse(self.evaluator.test({'c': {'#nin': [0, 1]}}))

    def test_c_ne_0(self):
        self.assertTrue(self.evaluator.test({'c': {'#ne': 0}}))

    def test_c_ne_1(self):
        self.assertFalse(self.evaluator.test({'c': {'#ne': 1}}))

    def test_c_ne_2_gt_0(self):
        self.assertTrue(self.evaluator.test({'c': {'#ne': 2, '#gt': 0}}))

    def test_c_ne_1_gt_0(self):
        self.assertFalse(self.evaluator.test({'c': {'#ne': 1, '#gt': 0}}))

if __name__ == '__main__':
    unittest.main()

