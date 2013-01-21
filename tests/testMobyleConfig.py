# -*- coding: utf-8 -*-
import unittest

import pymongo
import mobyle

import json

from mobyle.common  import session

from mobyle.common.config import Config

from mobyle.common.mobyleConfig import MobyleConfig

import mobyle.common.connection

mobyle.common.connection.init_mongo("mongodb://localhost/")

class TestMobyleConfig(unittest.TestCase):

    def setUp(self):
       objects = mobyle.common.session.MobyleConfig.find({})
       for object in objects:
         object.delete()
       
    def tearDown(self):
       objects = mobyle.common.session.MobyleConfig.find({})
       for object in objects:
         object.delete()

    def test_insert(self):
        config = mobyle.common.session.MobyleConfig()
        config.save()
        config_list = mobyle.common.session.MobyleConfig.find_one({'datadir': '/var/lib/mobyle'})
        self.assertTrue(config_list is not None)
    
