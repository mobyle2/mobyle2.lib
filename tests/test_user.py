# -*- coding: utf-8 -*-

import unittest
import os.path
#a config object must be instantiated first for each entry point of the application
from mobyle.common.config import Config
config = Config( os.path.join( os.path.dirname(__file__), 'test.conf'))
from mobyle.common import connection
from mobyle.common import users

class TestUser(unittest.TestCase):

    def setUp(self):
        objects = connection.User.find({})
        for object in objects:
            object.delete()
       
    def tearDown(self):
       objects = connection.User.find({})
       for object in objects:
           object.delete()


    def test_insert(self):
        user = connection.User()
        user['first_name'] = "Walter"
        user['last_name'] = "Bishop"
        user['email'] = "Bishop@nomail"
        user.save()
        
        user_list = connection.User.find({'first_name': 'Walter'})
        count = 0
        for user in user_list:
            count+=1
            self.assertIsNotNone(user["apikey"])
        self.assertEqual(count, 1)
    
    def test_password(self):
        user = connection.User()
        user['email'] = "Bishop@nomail"
        user.save()
        self.assertEqual(user['hashed_password'], '')        
        user.set_password("verySecret")        
        self.assertNotEqual(user['hashed_password'], '')
        self.assertTrue(user.check_password("verySecret") )
        self.assertFalse(user.check_password("incorrect") )
        
        user.save()
    
if __name__ == '__main__':
    unittest.main()

