# -*- coding: utf-8 -*-
import unittest

import pymongo
import mobyle

import json

from mobyle.common.config import Config

from mobyle.common.config import mobyleConfig

mobyle.common.init_mongo(["mongodb://localhost/", "test"])

class TestMobyleConfig(unittest.TestCase):

    def setUp(self):
       c = pymongo.Connection()
       self.db = c.test
       #make sure users is empty
       self.db.config.remove({})
       
    def tearDown(self):
        self.db.config.remove({})

    def test_insert(self):
        config = mobyleConfig.MobyleConfig()
        config.m.save()
        config_list = list(self.db.config.find({'datadir': '/var/lib/mobyle'}))
        self.assertTrue(len(config_list) ==1 )
    
