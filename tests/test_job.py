# -*- coding: utf-8 -*-

import unittest
import os.path
#a config object must be instantiated first for each entry point of the application
from mobyle.common.config import Config
config = Config( os.path.join( os.path.dirname(__file__), 'test.conf'))
from mobyle.common.connection import connection
from mobyle.common.job import Status
from mobyle.common.job import CustomStatus
from mobyle.common.job import ClJob

class TestJob(unittest.TestCase):

    def setUp(self):
        objects = connection.ClJob.find({})
        for object in objects:
            object.delete()
       
    def tearDown(self):
       objects = connection.ClJob.find({})
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
        for user in user_list:
            count+=1
        self.assertEqual(count, 1)
    

    
if __name__ == '__main__':
    unittest.main()

