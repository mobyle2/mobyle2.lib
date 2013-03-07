# -*- coding: utf-8 -*-
import unittest
from abstract_test import AbstractMobyleTest

from mobyle.common.data import *

import pymongo

from mobyle.common import users

import mobyle.common

from mobyle.common  import session

import mobyle.common.connection
mobyle.common.connection.init_mongo("mongodb://localhost/")

class TestUser(AbstractMobyleTest):

    def setUp(self):
       objects = mobyle.common.session.User.find({})
       for object in objects:
         object.delete()
       
    def tearDown(self):
       objects = mobyle.common.session.User.find({})
       for object in objects:
         object.delete()


    def test_insert(self):
        user = mobyle.common.session.User()
        print
        print user
        user['first_name'] = "Walter"
        user['last_name'] = "Bishop"
        user['email'] = "Bishop@nomail"
        user.save()
        print
        print user
        user_list = mobyle.common.session.User.find({'first_name': 'Walter'})
        count = 0
        for user in user_list:
          count+=1
          print
          print user
          self.assertTrue(user["apikey"] is not None)
        self.assertTrue(count ==1 )
    
    def test_password(self):
        user = mobyle.common.session.User()
        user['email'] = "Bishop@nomail"
        user.save()
        self.assertTrue(user['hashed_password'] == '')        
        user.set_password("verySecret")        
        self.assertTrue(user['hashed_password'] != '')
        
        self.assertTrue(user.check_password("verySecret") )
        self.assertFalse(user.check_password("incorrect") )
        
        user.save()
    
if __name__=='__main__':
    unittest.main()

