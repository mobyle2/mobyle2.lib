# -*- coding: utf-8 -*-
import unittest
from mobyle.common.service import *

import pymongo

from mobyle.common import users

import mobyle.common

from mobyle.common  import session

import mobyle.common.connection
mobyle.common.connection.init_mongo("mongodb://localhost/")

class TestUser(unittest.TestCase):

    def setUp(self):
       objects = mobyle.common.session.Service.find({})
       for object in objects:
         object.delete()
       
    def tearDown(self):
       objects = mobyle.common.session.Service.find({})
       for object in objects:
         object.delete()

    def test_insert(self):
        service = mobyle.common.session.Service()
        service['name'] = "test_service"
        service.save()
        services_list = mobyle.common.session.Service.find({'name': 'test_service'})
        count = 0
        for service in services_list:
          count+=1
        self.assertTrue(count==1)
