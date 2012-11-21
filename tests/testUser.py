# -*- coding: utf-8 -*-
import unittest
from mobyle_data.data import *

import pymongo

from mobyle_data import users

class TestUser(unittest.TestCase):

    def setUp(self):
       c = pymongo.Connection()
       self.db = c.test
       #make sure users is empty
       self.db.user.remove({})
       
    def tearDown(self):
        self.db.user.remove({})

    def test_insert(self):
        
        user = users.User()
        user.first_name = "Walter"
        user.last_name = "Bishop"
        user.m.save()
        
        user_list = list(self.db.user.find({'first_name': 'Walter'}))
        self.assertTrue(len(user_list) ==1 )
    
    def test_password(self):
        user = users.User()
        user.m.save()
        
        self.assertTrue(user.hashed_password == '')        
        user.set_password("verySecret")        
        self.assertTrue(user.hashed_password != '')
        
        self.assertTrue(user.check_password("verySecret") )
        self.assertFalse(user.check_password("incorrect") )
        
        user.m.save()