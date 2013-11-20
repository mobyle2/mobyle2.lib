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
from mobyle.common.mobyleError import MobyleError

from mf.views import MF_READ, MF_EDIT

class RequestMock(object):

    def __init__(self, adminmode=False):
        self.session = {}
        if adminmode:
            self.session['adminmode']=True

class TestProject(unittest.TestCase):

    def setUp(self):
        connection.User.collection.remove({})
        connection.Project.collection.remove({})
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
    
    def test_dir(self):
        my_project = connection.Project()
        my_project['owner'] = self.example_user['_id']
        my_project['name'] = 'MyProject'
        my_project.save()
        self.assertIsNone(my_project.dir)
        my_project.dir = '/tmp'
        self.assertEqual(my_project.dir, '/tmp')
        with self.assertRaises(MobyleError):
            my_project.dir = 'foo'
    
    def test_id(self):
        my_project = connection.Project()
        my_project['owner'] = self.example_user['_id']
        my_project['name'] = 'MyProject'
        my_project.save()
        project_rcv = connection.Project.find_one({})
        p_id = project_rcv['_id']
        self.assertEqual(my_project.id, p_id)
        
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
        connection.User.collection.remove({})
        connection.Project.collection.remove({})
        connection.ProjectData.collection.remove({})
        self.example_user = connection.User()
        self.example_user['email'] = 'Emeline@example.com'
        self.example_user.save()
        self.example_project = connection.Project()
        self.example_project['owner'] = self.example_user['_id']
        self.example_project['name'] = 'MyProject'
        self.example_project['users'] = [{'user': self.example_user['_id'], 'role': 'developper'}]
        self.example_project.save()
    
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

class TestProjectDocument(unittest.TestCase):
    """
    TestProjectDocument tests the ProjectDocument ACL functionality
    using ProjectData subclass because ProjectDocument is abstract
    (not registered in MF)
    """

    def _setUpTestUser(self,userid,admin=False):
        """
        set up a test user, save it and return it
        """
        user = connection.User()
        user['first_name'] = "first_name_%s" % str(userid)
        user['last_name'] = "last_name_%s" % str(userid)
        user['email'] = "user_%s@nomail" % str(userid)
        user['admin'] = admin
        user.save()
        return user

    def _setUpTestProject(self, projectid, owner, users):
        """
        set up a test project, save it and return it
        """
        project = connection.Project()
        project['owner'] = owner['_id']
        project['name'] = "project_%s" % str(projectid)
        project['users'] = users
        project.save()
        return project

    def setUp(self):
        """
        Set up the test case as follows:
        Projects       1 | 2 | 3 Administrator?
        User 1         M | C | W True
        User 2         C | C | W False
        User 3         x | x | x False
        M=Manager, C=Contributor, W=Watcher
        """
        connection.User.collection.remove({})
        connection.Project.collection.remove({})
        connection.ProjectData.collection.remove({})
        self.user1 = self._setUpTestUser(1,True)
        self.user2 = self._setUpTestUser(2)
        self.user3 = self._setUpTestUser(3)
        self.project1 = self._setUpTestProject(1,self.user1,\
                [{'user': self.user1['_id'], 'role': 'manager'},\
                 {'user': self.user2['_id'], 'role': 'contributor'}])
        self.project2 = self._setUpTestProject(2,self.user1,\
                [{'user': self.user1['_id'], 'role': 'contributor'},\
                 {'user': self.user2['_id'], 'role': 'contributor'}])
        self.project3 = self._setUpTestProject(3,self.user1,\
                [{'user': self.user1['_id'], 'role': 'watcher'},\
                 {'user': self.user2['_id'], 'role': 'watcher'}])
        self.admin_request = RequestMock(adminmode=True)

    def test_my(self):
        """
        test MF-based ACLs
        """
        v = ValueData()
        v.value = "test"
        projectdoc = connection.ProjectData()
        projectdoc['name'] = 'MyProject'
        projectdoc['data'] = v
        projectdoc['project'] = self.project1['_id']
        projectdoc.save()
        msg = "edit should be forbidden to unauthenticated users"
        test_filter = projectdoc.my(MF_EDIT, None, None)
        self.assertIs(test_filter, None, msg)
        msg = "user1 should have an access to projects 1 and 2 in edit mode"
        test_filter = projectdoc.my(MF_EDIT, None, self.user1['email'])
        self.assertEqual(test_filter, {'project': \
                {'$in': [self.project1["_id"], self.project2["_id"]]}}, msg)
        msg = "user1 should have an access to all projects "+\
              "in edit mode when admin"
        test_filter = projectdoc.my(MF_EDIT, self.admin_request, \
              self.user1['email'])
        self.assertEqual(test_filter, {}, msg)
        msg = "user2 should have an access to projects 1 and 2 in edit mode"
        test_filter = projectdoc.my(MF_EDIT, None, self.user2['email'])
        self.assertEqual(test_filter, {'project': \
                {'$in': [self.project1["_id"], self.project2["_id"]]}}, msg)
        msg = "user2 should have an access to projects 1 and 2 "+\
              "in edit mode when pretending admin"
        test_filter = projectdoc.my(MF_EDIT, self.admin_request, \
              self.user2['email'])
        self.assertEqual(test_filter, {'project': \
                {'$in': [self.project1["_id"], self.project2["_id"]]}}, msg)
        msg = "user3 should have an access to no project in edit mode"
        test_filter = projectdoc.my(MF_EDIT, None, self.user3['email'])
        self.assertEqual(test_filter, {'project': \
                {'$in': []}}, msg)
        msg = "user3 should have an access to no project "+\
              "in edit mode when pretending admin"
        test_filter = projectdoc.my(MF_EDIT, self.admin_request, \
              self.user3['email'])
        self.assertEqual(test_filter, {'project': \
                {'$in': []}}, msg)
        msg = "user1 should have an access to projects 1 2 3 in read mode"
        test_filter = projectdoc.my(MF_READ, None, self.user1['email'])
        self.assertEqual(test_filter, {'project': \
                {'$in': [self.project1["_id"], self.project2["_id"],\
                 self.project3["_id"]]}}, msg)
        msg = "user1 should have an access to all projects "+\
              "in read mode when admin"
        test_filter = projectdoc.my(MF_READ, self.admin_request, \
              self.user1['email'])
        self.assertEqual(test_filter, {}, msg)
        msg = "user2 should have an access to projects 1 2 3 in read mode"
        test_filter = projectdoc.my(MF_READ, None, self.user2['email'])
        self.assertEqual(test_filter, {'project': \
                {'$in': [self.project1["_id"], self.project2["_id"],\
                 self.project3["_id"]]}}, msg)
        msg = "user2 should have an access to projects 1 2 3 "+\
              "in read mode when pretending admin"
        test_filter = projectdoc.my(MF_READ, self.admin_request, \
              self.user2['email'])
        self.assertEqual(test_filter, {'project': \
                {'$in': [self.project1["_id"], self.project2["_id"],\
                 self.project3["_id"]]}}, msg)
        msg = "user3 should have an access to no project in read mode"
        test_filter = projectdoc.my(MF_READ, None, self.user3['email'])
        self.assertEqual(test_filter, {'project': \
                {'$in': []}}, msg)
        msg = "user3 should have an access to no project "+\
              "in edit mode when pretending admin"
        test_filter = projectdoc.my(MF_READ, self.admin_request, \
              self.user3['email'])
        self.assertEqual(test_filter, {'project': \
                {'$in': []}}, msg)

if __name__ == '__main__':
    unittest.main()
