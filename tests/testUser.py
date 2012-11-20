# -*- coding: utf-8 -*-
import unittest
from mobyle_data.data import *

import pymongo

class TestUser(unittest.TestCase):

    def setUp(self):
       c = pymongo.Connection()
       self.db = c.test
       #make sure users is empty
       self.db.user.remove({})

    def test_insert(self):
        from mobyle_data import users
        user = users.User()
        user.name = "Walter Bishop"
        user.m.save()
        
        users = list(self.db.user.find({'name': 'Walter Bishop'}))
        self.assertTrue(len(users) ==1 )