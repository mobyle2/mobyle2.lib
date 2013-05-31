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

from mf.views import MF_LIST, MF_MANAGE

class TestProject(unittest.TestCase):


    def setUp(self):
        objects = connection.User.find({})
        for object in objects:
            object.delete()
        objects = connection.Project.find({})
        for object in objects:
            object.delete()

        self.example_user = connection.User()
        self.example_user['email'] = 'Emeline@example.com'
        self.example_user.save()
       
    
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

    def test_my(self):
        user = connection.User()
        user['first_name'] = "Walter"
        user['last_name'] = "Bishop"
        user['email'] = "Bishop@nomail"
        user['admin'] = False
        user.save()
        my_project = connection.Project()
        my_project['owner'] = user['_id']
        my_project['name'] = 'MyProject'
        my_project.save()
        my_project2 = connection.Project()
        my_project2['owner'] = self.example_user['_id']
        my_project2['name'] = 'MyAdminProject'
        my_project2.save()
        filter = my_project.my(MF_LIST, None, user['email'])
        # {'users': {'$elemMatch': {'user':
        # ObjectId('51a8b1192e71a87907e7fb76')}}}
        assert(filter is not None) 
        assert(filter['users']['$elemMatch']['user'] == user['_id'])
        filter = my_project.my(MF_MANAGE, None, user['email'])
        assert(filter is not None)
        assert(filter['users']['$elemMatch']['user'] == user['_id'])
        assert(filter['users']['$elemMatch']['role'] == 'admin')
        user['admin'] = True
        user.save()
        filter = my_project.my(MF_LIST, None, user['email'])
        assert(filter is not None)
        filter = my_project.my(MF_MANAGE, None, user['email'])
        assert(filter is not None)


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
        self.example_project['users'] = [{'user': self.example_user['_id'], 'role': 'developper'}]
        self.example_project.save()


    def test_my(self):
        my_project2 = connection.Project()
        my_project2['owner'] = self.example_user['_id']
        my_project2['name'] = 'MyAdminProject'
        my_project2['users'] = [{'user': self.example_user['_id'], 'role': 'admin'}]
        my_project2.save()

        v = ValueData()
        v.value = "test"

        my_projectdata = connection.ProjectData()
        my_projectdata['name'] = 'MyProject'
        my_projectdata['data'] = v
        my_projectdata['project'] = self.example_project['_id']
        my_projectdata.save()

        my_projectdata2 = connection.ProjectData()
        my_projectdata2['name'] = 'MyProject'
        my_projectdata2['data'] = v
        my_projectdata2['project'] = my_project2['_id']
        my_projectdata2.save()

        self.example_user['admin'] = False
        self.example_user.save()
        filter = my_projectdata.my(MF_LIST, None, self.example_user['email'])
        # {'users': {'$elemMatch': {'user':
        # ObjectId('51a8b1192e71a87907e7fb76')}}}
        print "## "+str(filter)
        print "# "+str(my_projectdata['_id'])
        assert(filter is not None)
        assert(self.example_project['_id'] in filter['project']['$in'])
        assert(my_project2['_id'] in filter['project']['$in'])
        filter = my_projectdata.my(MF_MANAGE, None, self.example_user['email'])
        assert(filter is not None)
        assert(my_project2['_id'] in filter['project']['$in'])
        assert(self.example_project['_id'] not in filter['project']['$in'])
        self.example_user['admin'] = True
        self.example_user.save()
        filter = my_projectdata.my(MF_LIST, None, self.example_user['email'])
        assert(filter is not None)
        filter = my_projectdata.my(MF_MANAGE, None, self.example_user['email'])
        assert(filter is not None)
       
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
