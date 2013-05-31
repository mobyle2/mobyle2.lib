# -*- coding: utf-8 -*-

import unittest
import os.path
import time
#a config object must be instantiated first for each entry point of the application
from mobyle.common.config import Config
config = Config( os.path.join( os.path.dirname(__file__), 'test.conf'))
from mobyle.common.connection import connection

from mobyle.common.users import User
from mobyle.common.project import Project
from mobyle.common.job import Status
from mobyle.common.job import CustomStatus
from mobyle.common.job import ClJob

from mf.views import MF_LIST, MF_MANAGE

class TestJob(unittest.TestCase):

    def setUp(self):
        objects = connection.ClJob.find({})
        for object in objects:
            object.delete()
        objects = connection.User.find({})
        for object in objects:
            object.delete()
        objects = connection.Project.find({})
        for object in objects:
            object.delete()
       

    def test_insert(self):
        status = Status(Status.INIT)
        job = connection.ClJob()
        job.name = "first job"
        job.status = status
        job.owner = "me"
        job.save()
        
        job_list = connection.ClJob.find({'name': 'first job'})
        count = 0
        for user in job_list:
            count+=1
        self.assertEqual(count, 1)
    
    def test_cmp(self):
        status = Status(Status.INIT)
        job_1 = connection.ClJob()
        job_1.name = "first job"
        job_1.status = status
        job_1.owner = "me"
        job_1.save()
        time.sleep(1)
        job_2 = connection.ClJob()
        job_2.name = "first job"
        job_2.status = status
        job_2.owner = "me"
        job_2.save()
        self.assertGreater(job_2 , job_1)

    def test_my(self):
        status = Status(Status.INIT)
        job_1 = connection.ClJob()
        job_1.name = "first job"
        job_1.status = status
        job_1.owner = "me"
        job_1.save()
        job_2 = connection.ClJob()
        job_2.name = "second job"
        job_2.status = status
        job_2.owner = "me"
        job_2.save()
        job_3 = connection.ClJob()
        job_3.name = "third job"
        job_3.status = status
        job_3.owner = "me"
        job_3.save()


        my_user = connection.User()
        my_user['email'] = 'bishop@walter'
        my_user['admin'] = False
        my_user.save()
        my_project = connection.Project()
        my_project['owner'] = my_user['_id']
        my_project['name'] = 'MyAdminProject'
        my_project['users'] = [{'user': my_user['_id'], 'role': 'admin'}]
        my_project['jobs'] = [ job_1['_id'] ]
        my_project.save()

        my_project2 = connection.Project()
        my_project2['owner'] = my_user['_id']
        my_project2['name'] = 'MyAdminProject'
        my_project2['users'] = [{'user': my_user['_id'], 'role': 'developper'}]
        my_project2['jobs'] = [ job_3['_id'] ]
        my_project2.save()



        filter = job_1.my(MF_LIST, None, my_user['email'])
        print "## "+str(filter)
        assert(filter is not None)
        assert(job_1['_id'] in filter['_id']['$in'])
        assert(job_2['_id'] not in filter['_id']['$in'])
        assert(job_3['_id'] in filter['_id']['$in'])
        filter = job_1.my(MF_MANAGE, None, my_user['email'])
        assert(filter is not None)
        assert(job_1['_id'] in filter['_id']['$in'])
        assert(job_2['_id'] not in filter['_id']['$in'])
        assert(job_3['_id'] not in filter['_id']['$in'])
        my_user['admin'] = True
        my_user.save()
        filter = job_1.my(MF_LIST, None, my_user['email'])
        assert(filter is not None)
        filter = job_1.my(MF_MANAGE, None, my_user['email'])
        assert(filter is not None)

    
if __name__ == '__main__':
    unittest.main()

