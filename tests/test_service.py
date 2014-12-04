# -*- coding: utf-8 -*-

import unittest

from mongokit import ValidationError
import os.path
#a config object must be instantiated first for each entry point of the application
from mobyle.common.config import Config
config = Config( os.path.join( os.path.dirname(__file__), 'test.conf'))

from mobyle.common.connection import connection
from mobyle.common.service import *
from mobyle.common.type import *

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

    @unittest.expectedFailure
    def test_service_embedded_paragraphs_reload(self):
        par_x = InputProgramParagraph()
        par_x['name'] = 'x'
        program = connection.Program()
        program['name'] = 'test'
        program['inputs'] = par_x
        program.save()
        # this works since we use fetch which restores correctly
        # embedded documents
        program2 = connection.Program.fetch_one({'name':'test'})
        # this fails since we use find that does *not* restore
        # embedded documents
        program2 = connection.Program.find_one({'name':'test'})

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
        input_b['argpos'] = 2
        x_parameters = [input_b, input_a]
        par_x['children'].append(input_a)
        par_x['children'].append(input_b)
        par_y = InputProgramParagraph()
        par_y['name'] = 'y'
        input_c = InputProgramParameter()
        input_c['name'] = 'c'
        par_y['argpos'] = 1
        par_y['children'].append(input_c)
        par_x['children'].append(par_y)
        x_parameters = [input_c, input_b, input_a]
        program = Program()
        program['inputs'] = par_x
        self.assertEqual(sorted(program.inputs_list()), sorted(x_parameters),
            "service.inputs_list() is the three nested input parameters contained")        
        # we need to call init_ancestors manually here because ancestors are linked
        # only during service creation (by __init__)
        program.init_ancestors()
        self.assertEqual(input_a.ancestors,[par_x])
        self.assertEqual(input_c.ancestors,[par_y, par_x])
        self.assertEqual(input_c.argpos,1)
        self.assertEqual(input_b.argpos,2)
        self.assertEqual(input_a.argpos,3)
        self.assertEqual(program.parameters_list_by_argpos(), [input_c, input_b, input_a])

    def test_program_get_env(self):
        program = Program()
        program['env'] = {'a':'alpha', 'b':'beta'}
        self.assertEqual(program.env, {'a':'alpha', 'b':'beta'}) 

    def test_input_mandatory(self):
        input_a = InputParameter()
        self.assertFalse(input_a.mandatory)
        input_a['mandatory'] = True
        self.assertTrue(input_a.mandatory)

    def test_input_argpos(self):
        program = connection.Program()
        program['name'] = 'echo'
        
        inputs = InputParagraph()
        outputs = OutputParagraph()
        program['inputs'] = inputs
        program['outputs'] = outputs

        input_string = InputProgramParameter()
        input_string['name'] = 'string'
        input_string['argpos'] = 99
        input_string['format'] = '" " + value'
        input_string_type = StringType()
        input_string['type'] = input_string_type

        input_first = InputProgramParameter()
        input_first['name'] = 'string'
        input_first['argpos'] = -10
        input_first['format'] = '"ln -s toto titi && "'
        input_first_type = StringType()
        input_first['type'] = input_first_type

        input_options = InputProgramParagraph()

        input_options['argpos'] = 2
        input_n = InputProgramParameter()
        # n has no argpos, its argpos will be 2
        input_n['type'] = BooleanType()
        input_n['name'] = 'n'
        input_n['format'] = '" -n " if value else ""'
        input_options['children'].append(input_n)

        input_options_2 = InputProgramParagraph()

        input_options_2['argpos'] = None
        input_n2 = InputProgramParameter()
        # n2 has no argpos, its argpos will be 1
        input_n2['type'] = BooleanType()
        input_n2['name'] = 'n2'
        input_n2['format'] = '" -n " if value else ""'
        input_options_2['children'].append(input_n2)

        # e has an argpos of 3
        input_e = InputProgramParameter()
        input_e['type'] = BooleanType()
        input_e['argpos'] = 3
        input_e['name'] = 'e'
        input_e['format'] = '" -e " if value else ""'
        input_e['precond'] = {'n': True}
        input_options['children'].append(input_e)

        program['inputs']['children'].append(input_string)
        program['inputs']['children'].append(input_first)
        program['inputs']['children'].append(input_options)
        program['inputs']['children'].append(input_options_2)

        p_cmd = InputProgramParameter()
        p_cmd['name'] = 'cmd'
        p_cmd['command'] = True
        p_cmd['format'] = '"echo "'
        p_cmd_type = StringType()
        p_cmd['type'] = p_cmd_type      
        program['inputs']['children'].append(p_cmd)

        output_stdout = OutputProgramParameter()
        output_stdout['name'] = 'stdout'
        output_stdout['output_type'] = u'stdout'
        output_stdout_type = FormattedType()
        output_stdout['type'] = output_stdout_type
        program['outputs']['children'].append(output_stdout)
        program.init_ancestors()
        
        program.save()
        self.assertEqual(input_string.argpos, 99)
        self.assertEqual(input_e.argpos, 3)
        self.assertEqual(input_n.argpos, 2)
        self.assertEqual(input_first.argpos, -10)
        self.assertEqual(p_cmd.argpos, 0)
        self.assertEqual(input_n2.argpos, 1)

                
        
    def test_preconds(self):
        input_a = InputParameter()
        input_a['precond'] = {'a': True}
        par_x = InputParagraph()
        par_x['precond'] = {'x': True}
        par_x['children'].append(input_a)
        par_y = InputParagraph()
        par_y['precond'] = {'y': True}
        par_y['children'].append(par_x)
        par_y._init_ancestors()
        self.assertEqual(input_a.preconds,[par_y['precond'], par_x['precond'], input_a['precond']])

    def test_format(self):
        input_a = InputProgramParameter()
        self.assertFalse(input_a.has_format())
        self.assertEqual(input_a.format, None)
        input_a['format'] = '-t'
        self.assertTrue(input_a.has_format())
        self.assertEqual(input_a.format, '-t')
        
    def test_paramfile(self):
        input_a = InputProgramParameter()
        self.assertFalse(input_a.has_paramfile())
        self.assertEqual(input_a.paramfile, None)
        input_a['paramfile'] = 'test.in'
        self.assertTrue(input_a.has_paramfile())
        self.assertEqual(input_a.paramfile, 'test.in')

    def test_default_value(self):
        input_a = InputProgramParameter()
        self.assertIsNone(input_a.default_value)
        input_a['type'] = BooleanType()
        input_a['type']['default'] = True
        self.assertTrue(input_a.default_value)
        input_a['type']['default'] = False
        self.assertFalse(input_a.default_value.expr_value())

    
        
        
if __name__ == '__main__':
    unittest.main()
