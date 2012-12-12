import unittest
from mobyle.common.project import *
import pymongo

	
from mobyle.common import project
import mobyle.common

import datetime
from ming import schema
from mobyle.common import users

mobyle.common.init_mongo(["mongodb://localhost/", "test"])

	
	
class TestProject(unittest.TestCase):

    def setUp(self):
	c = pymongo.Connection()
        self.db = c.test
        #make sure projects is empty
        self.db.projects.remove({})	

    def tearDown(self):
	self.db.projects.remove({})
	
    def test_project(self):
	my_project = project.Project("Emeline","MyProject")
	my_project.m.save()
	
        self.assertEqual(my_project.name, 'MyProject')
	self.assertEqual(my_project.owner, 'Emeline')

    def test_get_creation_time(self):
	my_project = project.Project("Emeline","MyProject")
	my_project.m.save()
	
	date = str(my_project.get_creation_time())
	current_date = str(datetime.datetime.utcnow()).split('.')[0]+"+00:00"
	self.assertEqual(date, current_date)
	
    def test_add_users(self):
	my_project = project.Project("Emeline","MyProject")
	my_project.m.save()
	user = users.User()
	user.m.save()
	
	my_project.add_user(user,"admin")
	
	
	
	

if __name__=='__main__':
	unittest.main()

