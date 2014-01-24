# -*- coding: utf-8 -*-

import unittest
import os.path

from mobyle.common.config import Config

config = Config(os.path.join(os.path.dirname(__file__), 'test.conf'))

from mobyle.common.connection import connection
from mobyle.common.term import *


class TestTerm(unittest.TestCase):
    """ Tests for the Term class """

    def setUp(self):
        connection.DataTerm.collection.remove({})

    def test_self_and_ancestors(self):
        grandpa_term = connection.Term()
        grandpa_term['id'] = "grandpa"
        grandpa_term.save()
        grandpa2_term = connection.Term()
        grandpa2_term['id'] = "grandpa2"
        grandpa2_term.save()
        grandma_term = connection.Term()
        grandma_term['id'] = "grandma"
        grandma_term.save()
        pa_term = connection.Term()
        pa_term['id'] = "pa"
        pa_term['subclassOf'] = ["grandpa", "grandma"]
        pa_term.save()
        ma_term = connection.Term()
        ma_term['subclassOf'] = ["grandpa2", "grandma"]
        ma_term['id'] = "ma"
        ma_term.save()
        self_term = connection.Term()
        self_term['id'] = "self"
        self_term['subclassOf'] = ["pa", "ma"]
        self_term.save()
        ancestors_and_self_list = set([grandpa_term, grandpa2_term,
                                  grandma_term, pa_term, ma_term, self_term])
        self.assertEqual(ancestors_and_self_list,
                         set(self_term.self_and_ancestors_list()))
        #print [term['id'] for term in ]


class TestDataTerm(unittest.TestCase):
    """ Tests for the DataTerm class
    """

    def setUp(self):
        connection.DataTerm.collection.remove({})

    def test_insert(self):
        """
        test basic creation of a fake EDAM data term
        """
        data_term_test = connection.DataTerm()
        data_term_test['id'] = "test_data_term"
        data_term_test.save()
        data_terms_list = connection.DataTerm.find({'id': 'test_data_term'})
        count = 0
        for data_term_test in data_terms_list:
            count += 1
        self.assertEqual(count, 1)
