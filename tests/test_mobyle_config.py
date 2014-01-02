# -*- coding: utf-8 -*-

import pymongo
import mobyle
import json

import unittest
import os.path
#a config object must be instantiated first for each entry point of the application
from mobyle.common.config import Config
config = Config( os.path.join( os.path.dirname(__file__), 'test.conf'))

from mobyle.common.connection import connection
from mobyle.common.config import Config
from mobyle.common.mobyleConfig import MobyleConfig

class TestMobyleConfig(unittest.TestCase):

    def setUp(self):
       objects = connection.MobyleConfig.collection.remove({})

    def test_insert(self):
        import logging
        Config.logger().setLevel(logging.ERROR)
        config = connection.MobyleConfig()
        config.save()
        config_list = connection.MobyleConfig.find_one({'datadir': '/var/lib/mobyle'})
        self.assertIsNotNone(config_list)

    def test_get_current(self):
        config = connection.MobyleConfig()
        config['active'] = True
        config.save()
        self.assertTrue(config['_id'] == MobyleConfig.get_current()['_id'])
