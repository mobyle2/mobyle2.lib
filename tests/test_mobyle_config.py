# -*- coding: utf-8 -*-

import pymongo
import mobyle
import json

from abstract_test import AbstractMobyleTest
from mobyle.common import connection
from mobyle.common.config import Config
from mobyle.common.mobyleConfig import MobyleConfig

class TestMobyleConfig(AbstractMobyleTest):

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
    
if __name__ == '__main__':
    import unittest
    unittest.main()
