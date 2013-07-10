# -*- coding: utf-8 -*-

import unittest
import os.path
#a config object must be instantiated first for each entry point of the application
from mobyle.common.config import Config
config = Config( os.path.join( os.path.dirname(__file__), 'test.conf'))
from mobyle.common.connection import connection
from mobyle.common import users

from mf.views import MF_READ, MF_EDIT

from mobyle.common.users import User

class RequestMock(object):

    def __init__(self, adminmode=False):
        self.session = {}
        if adminmode:
            self.session['adminmode']=True

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

    def test_my(self):
        user = connection.User()
        user['first_name'] = "Walter"
        user['last_name'] = "Bishop"
        user['email'] = "Bishop@nomail"
        user['admin'] = False
        user.save()
        admin_request = RequestMock(adminmode=True)
        msg = "unauthenticated user should not be able to read anything"
        test_filter = user.my(MF_READ, None, None)
        self.assertIs(test_filter, None, msg)
        msg = "non-admin user should be able to read only itself"
        test_filter = user.my(MF_READ, {'email':user['email']}, user['email'])
        self.assertEquals(test_filter, {'email': user['email']}, msg)
        user['admin'] = True
        user.save()
        msg = "admin user should be able to read everything in admin Mode"
        test_filter = user.my(MF_READ, admin_request, user['email'])
        self.assertEquals(test_filter, {}, msg)
        msg = "admin user should be able to read only itself in non-admin Mode"
        test_filter = user.my(MF_READ, None, user['email'])
        self.assertEquals(test_filter, {'email': user['email']}, msg)
        user['admin'] = True
        user.save()
        msg = "unauthenticated user should not be able to edit anything"
        test_filter = user.my(MF_EDIT, None, None)
        self.assertIs(test_filter, None, msg)
        msg = "non-admin user should be able to edit only itself"
        test_filter = user.my(MF_EDIT, {'email':user['email']}, user['email'])
        self.assertEquals(test_filter, {'email': user['email']}, msg)
        user['admin'] = True
        user.save()
        msg = "admin user should be able to edit everything in admin Mode"
        test_filter = user.my(MF_EDIT, admin_request, user['email'])
        self.assertEquals(test_filter, {}, msg)
        msg = "admin user should be able to edit only itself in non-admin Mode"
        test_filter = user.my(MF_EDIT, None, user['email'])
        self.assertEquals(test_filter, {'email': user['email']}, msg)
 
if __name__ == '__main__':
    unittest.main()

