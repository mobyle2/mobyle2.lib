import unittest
from mobyle.common.project import *
import pymongo

	
from mobyle.common import project
import mobyle.common

from mobyle.common  import session

from datetime import datetime
from mobyle.common import users

import mobyle.common.connection
mobyle.common.connection.init_mongo("mongodb://localhost/")
	
class TestProject(unittest.TestCase):

    def setUp(self):
       objects = session.Project.find({})
       for object in objects:
         object.delete()
       self.example_user = session.User()
       self.example_user['email'] = 'Emeline@example.com'
       self.example_user.save()

    def tearDown(self):
       objects = session.Project.find({})
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
        user['email']='admin'
	user.save()
	my_project.add_user(user,"admin")

        self.assertEqual(my_project['users'][0]['user'], user)
	
	

if __name__=='__main__':
	unittest.main()

