# -*- coding: utf-8 -*-

import unittest
import os
from mongokit import Document, SchemaDocument
 
#a config object must be instantiated first for each entry point of the application
from mobyle.common.config import Config
config = Config( os.path.join( os.path.dirname(__file__), 'test.conf'))
from mobyle.common.connection import connection

from mobyle.common.myaml import myaml


@myaml.register
@connection.register
class Test(Document):
    __collection__ = 'test'
    __database__ = Config.config().get('app:main', 'db_name')
    structure = {
                 '_type': unicode,
                 'a': [],
                }

@myaml.register
@connection.register
class EmbeddedTest(SchemaDocument):
    structure = {
                 '_type': unicode,
                 'x': basestring,
                }

@myaml.register
@connection.register
class EmbeddingTest(Document):
    __collection__ = 'test'
    __database__ = Config.config().get('app:main', 'db_name')
    structure = {
                 '_type': unicode,
                 'embedded': EmbeddedTest,
                }

@connection.register
class UnregisteredTest(Document):
    __collection__ = 'test'
    __database__ = Config.config().get('app:main', 'db_name')
    structure = {
                 '_type': unicode,
                 'a': [],
                }

class TestJobSubmit(unittest.TestCase):

    def equal(self, test_object):
        test_yaml = myaml.dump(test_object)
        test_reloaded = myaml.load(test_yaml)
        self.assertEqual(test_object, test_reloaded)

    def test_dump_reload(self):
        test = connection.Test()
        self.equal(test)

    def test_with_property(self):
        test = connection.Test()
        test['a'] = [1, 2]
        self.equal(test)

    def test_embedded(self):
        embedded = EmbeddedTest()
        embedded['x'] = 'i am clearly embedded'
        embedding = connection.EmbeddingTest()
        embedding['embedded'] = embedded
        self.equal(embedded)

    def test_unregistered(self):
        unregistered = connection.UnregisteredTest()
        with self.assertRaises(TypeError):
            myaml.dump(unregistered)

if __name__ == '__main__':
    unittest.main()
