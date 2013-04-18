# -*- coding: utf-8 -*-

from datetime import datetime
import unittest
import os.path
#a config object must be instantiated first for each entry point of the application
from mobyle.common.config import Config
config = Config( os.path.join( os.path.dirname(__file__), 'test.conf'))

from mobyle.common.connection import connection
from mobyle.common.data import ValueData
from mobyle.common.project import Project, ProjectData
from mobyle.common.users import User

class TestProject(unittest.TestCase):


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
        my_project['owner'] = self.example_user['_id']
        my_project['name'] = 'MyProject'
        my_project.save()
        self.assertEqual(my_project['name'], 'MyProject')
        self.assertEqual(my_project['owner'], self.example_user['_id'])

    def test_add_users(self):
        my_project = connection.Project()
        my_project['owner'] = self.example_user['_id']
        my_project['name'] = 'MyProject'
        my_project.save()
        user = connection.User()
        user['email'] = 'admin'
        user.save()
        my_project.add_user(user, "admin")
        self.assertEqual(my_project['users'][0]['user'], user['_id'])

class TestProjectData(unittest.TestCase):


    def setUp(self):
        objects = connection.User.find({})
        for o in objects:
            o.delete()
        objects = connection.Project.find({})
        for o in objects:
            o.delete()
        objects = connection.ProjectData.find({})
        for o in objects:
            o.delete()
        self.example_user = connection.User()
        self.example_user['email'] = 'Emeline@example.com'
        self.example_user.save()
        self.example_project = connection.Project()
        self.example_project['owner'] = self.example_user['_id']
        self.example_project['name'] = 'MyProject'
        self.example_project.save()
       
    #def tearDown(self):
        #objects = connection.User.find({})
        #for object in objects:
        #    object.delete()
        #objects = connection.Project.find({})
        #for object in objects:
        #    object.delete()
    
    def test_projectdata(self):
        v = ValueData()
        v.value = "test"
        my_projectdata = connection.ProjectData()
        my_projectdata['name'] = 'MyProject'
        my_projectdata['data'] = v
        my_projectdata['project'] = self.example_project['_id']
        my_projectdata.save()
        my_projectdata = connection.ProjectData.fetch()[0]
        print my_projectdata['data'].__class__
        #TODO: ProjectData unit tests are not implemented at all...
if __name__ == '__main__':
    unittest.main()
