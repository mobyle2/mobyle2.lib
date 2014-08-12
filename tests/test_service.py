# -*- coding: utf-8 -*-

import unittest

from mongokit import ValidationError
import os.path
#a config object must be instantiated first for each entry point of the application
from mobyle.common.config import Config
config = Config( os.path.join( os.path.dirname(__file__), 'test.conf'))

from mobyle.common.connection import connection
from mobyle.common.service import *

class TestService(unittest.TestCase):

    def setUp(self):
        connection.Service.collection.remove({})

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
        service = connection.Service.fetch_one({'name': 'test_program_service'})
        self.assertTrue(isinstance(service,Program))
        service = connection.Service.fetch_one({'name': 'test_program_service'})
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

    def test_service_parameters_list_getters(self):
        """
        test if parameters lists methods return the right data
        """
        par_x = InputParagraph()
        par_x['name'] = 'x'
        input_a = InputParameter()
        input_a['name'] = 'a'
        input_b = InputParameter()
        input_b['name'] = 'b'
        x_parameters = [input_b, input_a]
        par_x['children'].append(input_a)
        par_x['children'].append(input_b)
        # using sorted to be order-independent in the test
        self.assertEqual(sorted(par_x.parameters_list()), sorted(x_parameters),
                         "par_x.parameters_list() is the two input parameters contained")
        par_y = InputParagraph()
        par_y['name'] = 'y'
        input_c = InputParameter()
        input_c['name'] = 'c'
        par_y['children'].append(input_c)
        par_x['children'].append(par_y)
        x_parameters = [input_b, input_a, input_c]
        self.assertEqual(sorted(par_x.parameters_list()), sorted(x_parameters),
                         "par_x.parameters_list() is the three nested input parameters contained")
        service = Program()
        service['inputs'] = par_x
        self.assertEqual(sorted(service.inputs_list()), sorted(x_parameters),
                         "service.inputs_list() is the three nested input parameters contained")

    def test_program_parameters_list_getters(self):
        """
        test if program-specific parameters lists methods return the right data
        """
        par_x = InputProgramParagraph()
        par_x['name'] = 'x'
        input_a = InputProgramParameter()
        input_a['name'] = 'a'
        input_a['argpos'] = 3
        input_b = InputProgramParameter()
        input_b['name'] = 'b'
        input_a['argpos'] = 2
        x_parameters = [input_b, input_a]
        par_x['children'].append(input_a)
        par_x['children'].append(input_b)
        par_y = InputProgramParagraph()
        par_y['name'] = 'y'
        input_c = InputProgramParameter()
        input_c['name'] = 'c'
        input_c['argpos'] = 1
        par_y['children'].append(input_c)
        par_x['children'].append(par_y)
        x_parameters = [input_c, input_b, input_a]
        program = Program()
        program['inputs'] = par_x
        self.assertEqual(sorted(program.inputs_list()), sorted(x_parameters),
                         "service.inputs_list() is the three nested input parameters contained")        
        program.init_ancestors()
        #TODO continue testing here...
        #for para in program.inputs_list():
        #    print para['name'], [ancestor['name'] for ancestor in para.ancestors]


if __name__ == '__main__':
    unittest.main()
