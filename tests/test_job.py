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
from mobyle.common.job import ProgramJob
from mobyle.common.mobyleError import MobyleError
from mobyle.common.service import Program, InputParagraph, InputProgramParameter
from mobyle.common.type import StringType
from mobyle.common.data import ValueData

class TestJob(unittest.TestCase):

    def setUp(self):
        objects = connection.ProgramJob.collection.remove({})
        objects = connection.User.collection.remove({})
        objects = connection.Project.collection.remove({})
        
        self.user = connection.User()
        self.user['email'] = 'foo@bar.fr'
        self.user.save()
        
        self.project = connection.Project()
        self.project['owner'] = self.user['_id']
        self.project['name'] = 'MyProject'
        self.project.save()
        
        self.status = Status(Status.INIT)

    def test_insert(self):
        job = connection.ProgramJob()
        #test that status is required
        job.project = self.project.id
        self.assertRaises(MobyleError, job.save)
        #test that project is required
        job = connection.ProgramJob()
        job.status = self.status
        self.assertRaises(RequireFieldError, job.save)
            
        job = connection.ProgramJob()
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
            
    def test_ProgramJob(self):
        job_send = connection.ProgramJob()
        job_send.project = self.project.id
        job_send.name = "first job"
        job_send.status = self.status
        job_send.owner = {'id': self.project.id, 'klass': 'Project'}
        
        job_send.save()
        
        job_rcv = connection.Job.find_one({'_id': job_send.id })
        self.assertEqual(job_send.id, job_rcv.id)
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
        #because MongoDB does not store microseconds...
        end_time = datetime(*datetime.utcnow().timetuple()[:6])
        job_send.end_time = end_time
        job_send.cmd_line = "golden db:id" 
        job_send.cmd_env = {'GOLDENDATA': '/usr/local/golden'}
        job_send.save()
        job_rcv = connection.Job.find_one({'_id': job_send.id })
        self.assertEqual(job_send.message, job_rcv.message)
        self.assertEqual(job_send.end_time, job_rcv.end_time)
        self.assertEqual(job_send.cmd_line, job_rcv.cmd_line)
        self.assertEqual(job_send.cmd_env, job_rcv.cmd_env)

    def test_restore_service(self):
        job = connection.ProgramJob()
        job.project = self.project.id
        job.name = "restore job service test"
        job.status = self.status
        job.owner = {'id': self.project.id, 'klass': 'Project'}
        program = connection.Program()
        program['name'] = "test_program_service"
        inputs = InputParagraph()
        program['inputs'] = inputs
        input_string = InputProgramParameter()
        input_string['name'] = 'string'
        input_string['argpos'] = 99
        input_string['format'] = '" " + value'
        input_string_type = StringType()
        input_string['type'] = input_string_type
        program['inputs']['children'].append(input_string)
        program.save()
        job['service'] = program
        job.process_inputs({'string':'toto'})
        job.save()
        restored_job = connection.Job.fetch_one({'name': "restore job service test"})
        self.assertIsInstance(restored_job.get_input_value('string'), ValueData)
        #print "job.get_input_value('string')=", type(job.get_input_value('string'))
        #print "restored_job.get_input_value('string')=", type(restored_job.get_input_value('string'))
        #print "job.inputs=", type(job.inputs)
        #print "restored_job.inputs=", type(restored_job.inputs)
        #print type(restored_job)
 
if __name__ == '__main__':
    unittest.main()

