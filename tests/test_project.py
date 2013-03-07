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

    def tearDown(self):
       objects = session.Project.find({})
       for object in objects:
         object.delete()
	
    def test_project(self):
	my_project = session.Project()
        my_project['owner'] = 'Emeline'
        my_project['name'] = 'MyProject'
        my_project['date_creation'] = datetime.utcnow()
	my_project.save()
	
        self.assertEqual(my_project['name'], 'MyProject')
	self.assertEqual(my_project['owner'], 'Emeline')

    def test_add_users(self):
	my_project = session.Project()
        my_project['owner'] = 'Emeline'
        my_project['name'] = 'MyProject'
        my_project['date_creation'] = datetime.utcnow()

	my_project.save()
	user = session.User()
        user['email']='admin'
	user.save()

	my_project.add_user(user,"admin")
        print str(my_project)

        self.assertEqual(my_project['users'][0]['user']['_id'] , user['_id'])
	
	

if __name__=='__main__':
	unittest.main()

