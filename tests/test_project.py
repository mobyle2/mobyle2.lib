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

from mf.views import MF_READ, MF_EDIT

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
        """
        test MF-based ACLs
        """
        user1 = connection.User()
        user1['first_name'] = "Walter"
        user1['last_name'] = "Bishop"
        user1['email'] = "Bishop@nomail"
        user1['admin'] = True
        user1.save()
        class RequestMock(object):
            def __init__(self, adminmode=False):
                self.session = {}
                if adminmode:
                    self.session['adminmode']=True
        admin_request = RequestMock(adminmode=True)
        project1 = connection.Project()
        project1['owner'] = user1['_id']
        project1['name'] = 'Project 1'
        project1['users'] = [{'user': user1['_id'], 'role': 'manager'}]
        project1.save()
        msg1 = "edit should be forbidden to unauthenticated users" 
        filter1 = project1.my(MF_EDIT, None, None)
        self.assertIs(filter1, None, msg1)
        msg2 = "edit should be allowed to project contributors/managers"
        filter2 = project1.my(MF_EDIT, None, user1['email'])
        self.assertEqual(filter2, {'users': {'$elemMatch': \
             {'$or': [{'role': 'contributor'}, {'role': 'manager'}],\
               'user': user1['_id']}}}, msg2)
        msg3 = "edit should be allowed everywhere in admin mode"
        filter3 = project1.my(MF_EDIT, admin_request, user1['email'])
        self.assertEqual(filter3, {}, msg3)
        msg4 = "read should be allowed only on public projects for "\
               + "unauthenticated users"
        filter4 = project1.my(MF_READ, None, None)
        self.assertEqual(filter4, {'public': True}, msg4)
        msg5 = "read should be allowed on projects where user is member "\
               + "or public projects"
        filter5 = project1.my(MF_READ, None, user1['email'])
        self.assertEqual(filter5,{'$or': [{'users': {'$elemMatch': \
             {'user': user1['_id']}}},\
             {'public': True}]}, msg5)
        msg6 = "read should be allowed everywhere in admin mode"
        filter6 = project1.my(MF_READ, admin_request, user1['email'])
        self.assertEqual(filter6, {}, msg6)


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

    def tearDown(self):
        objects = connection.User.find({})
        for object in objects:
            object.delete()
        objects = connection.Project.find({})
        for object in objects:
            object.delete()
    
    def test_projectdata(self):
        v = ValueData()
        v.value = "test"
        my_projectdata = connection.ProjectData()
        my_projectdata['name'] = 'MyProject'
        my_projectdata['data'] = v
        my_projectdata['project'] = self.example_project['_id']
        my_projectdata.save()
        my_projectdata = connection.ProjectData.fetch()[0]
        #TODO: ProjectData unit tests are not implemented at all...

if __name__ == '__main__':
    unittest.main()
