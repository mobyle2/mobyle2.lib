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
       objects = connection.MobyleConfig.find({})
       for object in objects:
           object.delete()
       
    def tearDown(self):
       objects = connection.MobyleConfig.find({})
       for object in objects:
           object.delete()

    def test_insert(self):
        import logging
        Config.logger().setLevel(logging.ERROR)
        config = connection.MobyleConfig()
        config.save()
        config_list = connection.MobyleConfig.find_one({'datadir': '/var/lib/mobyle'})
        self.assertIsNotNone(config_list)
