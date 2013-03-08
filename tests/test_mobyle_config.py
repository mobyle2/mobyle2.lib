# -*- coding: utf-8 -*-

import pymongo
import mobyle
import json

from abstract_test import AbstractMobyleTest
from mobyle.common.config import Config
from mobyle.common.mobyleConfig import MobyleConfig
import mobyle.common
import mobyle.common.connection
mobyle.common.connection.init_mongo(Config.config().get('app:main','db_uri'))

class TestMobyleConfig(AbstractMobyleTest):

    def setUp(self):
       objects = mobyle.common.session.MobyleConfig.find({})
       for object in objects:
           object.delete()
       
    def tearDown(self):
       objects = mobyle.common.session.MobyleConfig.find({})
       for object in objects:
           object.delete()

    def test_insert(self):
        import logging
        Config.logger().setLevel(logging.ERROR)
        config = mobyle.common.session.MobyleConfig()
        config.save()
        config_list = mobyle.common.session.MobyleConfig.find_one({'datadir': '/var/lib/mobyle'})
        self.assertIsNotNone(config_list)
    
if __name__ == '__main__':
    import unittest
    unittest.main()
