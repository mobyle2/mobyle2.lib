# -*- coding: utf-8 -*-

from datetime import datetime

from abstract_test import AbstractMobyleTest
from mobyle.common import connection
from mobyle.common.project import Project
from mobyle.common.users import User

class TestProject(AbstractMobyleTest):


    def setUp(self):
        objects = connection.User.find({})
        for object in objects:
            object.delete()
        self.example_user = connection.User()
        self.example_user['email'] = 'Emeline@example.com'
        self.example_user.save()
       
    def tearDown(self):
        objects = connection.User.find({})
        for object in objects:
            object.delete()
        self.example_user.delete()
    
    def test_project(self):
        my_project = connection.Project()
        my_project['owner'] = self.example_user
        my_project['name'] = 'MyProject'
        my_project.save()
        self.assertEqual(my_project['name'], 'MyProject')
        self.assertEqual(my_project['owner'], self.example_user)

    def test_add_users(self):
        my_project = connection.Project()
        my_project['owner'] = self.example_user
        my_project['name'] = 'MyProject'
        my_project.save()
        user = connection.User()
        user['email'] = 'admin'
        user.save()
        my_project.add_user(user, "admin")
        self.assertEqual(my_project['users'][0]['user'], user)



if __name__ == '__main__':
    import unittest
    unittest.main()
