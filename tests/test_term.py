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


class TestFormatTerm(unittest.TestCase):
    """ Tests for the FormatTerm class
    """

    def setUp(self):
        connection.DataTerm.collection.remove({})
        connection.FormatTerm.collection.remove({})

    def test_represents_dataterms(self):
        """
        test retrieving the list of data terms
        associated to the data it can represent
        """
        data_term_test = connection.DataTerm()
        data_term_test['id'] = "test_data_term"
        data_term_test['subclassOf'] = ["test_data_ancestor"]
        data_term_test.save()

        data_term_test_ancestor = connection.DataTerm()
        data_term_test_ancestor['id'] = "test_data_ancestor"
        data_term_test_ancestor.save()

        data_term_test_other = connection.DataTerm()
        data_term_test_other['id'] = "test_data_other"
        data_term_test_other.save()

        format_term_test = connection.FormatTerm()
        format_term_test['id'] = "test_format_term"
        format_term_test['subclassOf'] = ["test_format_ancestor"]
        format_term_test['is_format_of'] = ["test_data_term"]
        format_term_test.save()

        format_term_ancestor_test = connection.FormatTerm()
        format_term_ancestor_test['id'] = "test_format_ancestor"
        format_term_ancestor_test['is_format_of'] = ["test_data_ancestor",
                                           "test_data_other"]
        format_term_ancestor_test.save()

        data_terms_list = set([data_term_test,
                               data_term_test_ancestor,
                               data_term_test_other])
        self.assertEqual(data_terms_list,
                         set(format_term_test.represents_dataterms()))
