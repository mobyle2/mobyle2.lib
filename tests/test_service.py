# -*- coding: utf-8 -*-

import unittest
import pymongo
from mongokit import ValidationError
import os.path
#a config object must be instantiated first for each entry point of the application
from mobyle.common.config import Config
config = Config( os.path.join( os.path.dirname(__file__), 'test.conf'))

from mobyle.common.connection import connection
from mobyle.common.service import *

class TestService(unittest.TestCase):

    def setUp(self):
        objects = connection.Service.find({})
        for object in objects:
            object.delete()
       
    def tearDown(self):
        objects = connection.Service.find({})
        for object in objects:
            object.delete()

    def test_insert(self):
        """
        test basic creation of an almost empty service
        """
        service = connection.Service()
        service['name'] = "test_service"
        service.save()
        services_list = connection.Service.find({'name': 'test_service'})
        count = 0
        for service in services_list:
            count += 1
        self.assertEqual(count, 1)

    def test_polymorphism(self):
        """
        test that the instance of the correct
        service subclass is retrieved when querying
        """
        program = connection.Program()
        program['name'] = "test_program_service"
        program.save()
        workflow = connection.Workflow()
        workflow['name'] = "test_workflow_service"
        workflow.save()
        service = connection.Service.find_one({'name': 'test_program_service'})
        self.assertTrue(isinstance(service,Program))
        service = connection.Service.find_one({'name': 'test_program_service'})
        self.assertTrue(isinstance(workflow,Workflow))

    def test_inputs_creation(self):
        """
        test creation of a service with an input
        """
        service = connection.Service()
        service['name'] = "test_service_with_inputs"
        inputs = InputParagraph()
        service['inputs'] = inputs
        input_1 = InputParameter()
        input_1['name'] = 'test_input'
        inputs['children'].append(input_1)
        inputs.validate()
        service.validate()
        service.save()
        

    def test_invalid_inputs_creation(self):
        """
        test creation of a service with an output
        in the inputs list, which should raise
        an error
        """
        #TODO: service creation code below is commented for now,
        # as the validation for inputs paragraph
        # is not automatically triggered when
        # validating or saving the Service object
        #service = connection.Service()
        #service['name'] = "test_service_with_inputs"
        inputs = InputParagraph()
        #service['inputs']=inputs
        output = OutputParameter()
        output['name'] = 'test_output'     
        inputs['children'].append(output)
        self.assertRaises(ValidationError, inputs.validate)
        #service.validate()
        #service.save()

if __name__ == '__main__':
    unittest.main() 
