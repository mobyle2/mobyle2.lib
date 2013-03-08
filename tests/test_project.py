# -*- coding: utf-8 -*-

from datetime import datetime
from abstract_test import AbstractMobyleTest

from mobyle.common.project import *
from mobyle.common import project
import mobyle.common
from mobyle.common import users
import mobyle.common.connection
mobyle.common.connection.init_mongo(Config.config().get('app:main','db_uri'))
from mobyle.common  import session

class TestProject(AbstractMobyleTest):


    def setUp(self):
        objects = mobyle.common.session.User.find({})
        for object in objects:
            object.delete()
        self.example_user = session.User()
        self.example_user['email'] = 'Emeline@example.com'
        self.example_user.save()
       
    def tearDown(self):
        objects = mobyle.common.session.User.find({})
        for object in objects:
            object.delete()
        self.example_user.delete()
    
    def test_project(self):
        my_project = session.Project()
        my_project['owner'] = self.example_user
        my_project['name'] = 'MyProject'
        my_project.save()
        self.assertEqual(my_project['name'], 'MyProject')
        self.assertEqual(my_project['owner'], self.example_user)

    def test_add_users(self):
        my_project = session.Project()
        my_project['owner'] = self.example_user
        my_project['name'] = 'MyProject'
        my_project.save()
        user = session.User()
        user['email'] = 'admin'
        user.save()
        my_project.add_user(user, "admin")
        self.assertEqual(my_project['users'][0]['user'], user)



if __name__ == '__main__':
    import unittest
    unittest.main()
