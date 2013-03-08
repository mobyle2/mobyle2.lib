# -*- coding: utf-8 -*-

from abstract_test import AbstractMobyleTest

from mobyle.common import users
import mobyle.common
from mobyle.common import session
import mobyle.common.connection
from mobyle.common.config import Config
mobyle.common.connection.init_mongo(Config.config().get('app:main','db_uri'))

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
        user['first_name'] = "Walter"
        user['last_name'] = "Bishop"
        user['email'] = "Bishop@nomail"
        user.save()
        
        user_list = mobyle.common.session.User.find({'first_name': 'Walter'})
        count = 0
        for user in user_list:
            count+=1
            self.assertIsNotNone(user["apikey"])
        self.assertEqual(count, 1)
    
    def test_password(self):
        user = mobyle.common.session.User()
        user['email'] = "Bishop@nomail"
        user.save()
        self.assertEqual(user['hashed_password'], '')        
        user.set_password("verySecret")        
        self.assertNotEqual(user['hashed_password'], '')
        
        self.assertTrue(user.check_password("verySecret") )
        self.assertFalse(user.check_password("incorrect") )
        
        user.save()
    
if __name__ == '__main__':
    import unittest
    unittest.main()

