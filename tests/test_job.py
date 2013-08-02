# -*- coding: utf-8 -*-

import unittest
import os.path
import time
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
        for obj in objects:
            obj.delete()
       
    def tearDown(self):
       objects = connection.ClJob.find({})
       for obj in objects:
           obj.delete()


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
    
