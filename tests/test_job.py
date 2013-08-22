# -*- coding: utf-8 -*-

import unittest
import os.path
import time
from datetime import datetime
from mongokit.schema_document import RequireFieldError
 
#a config object must be instantiated first for each entry point of the application
from mobyle.common.config import Config
config = Config( os.path.join( os.path.dirname(__file__), 'test.conf'))
from mobyle.common.connection import connection

from mobyle.common.users import User
from mobyle.common.project import Project
from mobyle.common.job import Status
from mobyle.common.job import CustomStatus
from mobyle.common.job import ClJob
from mobyle.common.mobyleError import MobyleError


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
        
        self.user = connection.User()
        self.user['email'] = 'foo@bar.fr'
        self.user.save()
        
        self.project = connection.Project()
        self.project['owner'] = self.user['_id']
        self.project['name'] = 'MyProject'
        self.project.save()
        
        self.status = Status(Status.INIT)

    def test_insert(self):
        job = connection.ClJob()
        #test that status is required
        job.project = self.project.id
        self.assertRaises(MobyleError, job.save)
        #test that project is required
        job = connection.ClJob()
        job.status = self.status
        self.assertRaises(RequireFieldError, job.save)
            
        job = connection.ClJob()
        job.project = self.project.id
        job.status = self.status
        job.name = "first job"
        job.status = self.status
        job.owner = {'id': self.project.id, 'klass': 'Project'}
        job.save()
        
        job_list = connection.Job.find({'name': 'first job'})
        count = 0
        for job in job_list:
            count+=1
        self.assertEqual(count, 1)
    
    def test_cmp(self):
        job_1 = connection.Job()
        job_1.project = self.project.id
        job_1.name = "first job"
        job_1.status = self.status
        job_1.owner = {'id': self.project.id, 'klass': 'Project'}
        job_1.save()
        time.sleep(1)
        job_2 = connection.Job()
        job_2.project = self.project.id
        job_2.name = "first job"
        job_2.status = self.status
        job_2.owner = {'id': self.project.id, 'klass': 'Project'}
        job_2.save()
        self.assertGreater(job_2 , job_1)
    
    def test_id(self):
        job = connection.Job()
        job.project = self.project.id
        job.name = "first job"
        job.status = self.status
        job.owner = {'id': self.project.id, 'klass': 'Project'}
        job.save()
        job_rcv = connection.Job.find_one({})
        j_id = job_rcv['_id']
        self.assertEqual(job.id, j_id)
        
    def test_dir(self):
        job = connection.Job()
        job.project = self.project.id
        job.name = "first job"
        job.status = self.status
        job.owner = {'id': self.project.id, 'klass': 'Project'}
        job.save()
        self.assertIsNone(job.dir)
        job.dir = '/tmp'
        self.assertEqual(job.dir, '/tmp')
        with self.assertRaises(MobyleError):
            job.dir = 'foo'
            
    def test_ClJob(self):
        job_send = connection.ClJob()
        job_send.project = self.project.id
        job_send.name = "first job"
        job_send.status = self.status
        job_send.owner = {'id': self.project.id, 'klass': 'Project'}
        
        #in mongo creation time does not record microsecond :((
        #need to remove them to be compare
        create_time = datetime(*datetime.utcnow().timetuple()[:6])
        job_send.save()
        
        job_rcv = connection.Job.find_one({'_id': job_send.id })
        self.assertEqual(job_send.id, job_rcv.id)
        self.assertEqual(create_time, job_rcv.create_time)
        self.assertEqual(job_send.name, job_rcv.name)
        self.assertEqual(job_send.status, job_rcv.status)
        self.assertEqual(job_send.owner, job_rcv.owner)
        self.assertEqual(job_send.message, None)
        self.assertEqual(job_send.owner, job_rcv.owner) 
        self.assertEqual(job_send.end_time, None)
        self.assertEqual(job_send.project, job_rcv.project)
        self.assertEqual(job_send.cmd_line, None)
        self.assertEqual(job_send.cmd_env, {})
                      
        job_send.message = "a message"
        job_send.end_time = datetime.now()
        job_send.cmd_line = "golden db:id" 
        job_send.cmd_env = {'GOLDENDATA': '/usr/local/golden'}
        job_send.save()
        job_rcv = connection.Job.find_one({'_id': job_send.id })
        self.assertEqual(job_send.message, job_send.message)
        self.assertEqual(job_send.end_time, job_send.end_time)
        self.assertEqual(job_send.cmd_line, job_send.cmd_line)
        self.assertEqual(job_send.cmd_env, job_send.cmd_env)
        
if __name__ == '__main__':
    unittest.main()

