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
from mobyle.common.service import *
from mobyle.common.type import *

class TestJobSubmit(unittest.TestCase):

    def setUp(self):
        connection.ProgramJob.collection.remove({})
        connection.User.collection.remove({})
        connection.Project.collection.remove({})
        
        self.user = connection.User()
        self.user['email'] = 'foo@bar.fr'
        self.user.save()
        
        self.project = connection.Project()
        self.project['owner'] = self.user['_id']
        self.project['name'] = 'MyProject'
        self.project.save()
        
        self.status = Status(Status.INIT)

        #build a test service
        self.program = connection.Program()
        self.program['name'] = 'echo'
        self.program['command'] = 'echo '
        inputs = InputParagraph()
        outputs = OutputParagraph()
        self.program['inputs'] = InputParagraph()
        self.program['outputs'] = OutputParagraph()
        input_string = InputProgramParameter()
        input_string['name'] = 'string'
        input_string['argpos'] = 99
        input_string['format'] = '" " + value'
        input_string_type = StringType()
        input_string['type'] = input_string_type
        input_options = InputProgramParagraph()
        input_options['argpos'] = 2
        input_n = InputProgramParameter()
        # n has no argpos, its argpos will be 2
        input_n['type'] = BooleanType()
        input_n['name'] = 'n'
        input_n['format'] = '"-n" if value else ""'
        input_options['children'].append(input_n)
        # e has an argpos of 3
        input_e = InputProgramParameter()
        input_e['type'] = BooleanType()
        input_e['argpos'] = 3
        input_e['name'] = 'e'
        input_e['format'] = '"-e" if value else ""'
        input_e['precond'] = {'n': True}
        input_options['children'].append(input_e)
        self.program['inputs']['children'].append(input_string)
        self.program['inputs']['children'].append(input_options)
        output_stdout = OutputProgramParameter()
        output_stdout['name'] = 'stdout'
        output_stdout['output_type'] = 'stdout'
        output_stdout_type = FormattedType()
        output_stdout['type'] = output_stdout_type
        self.program['outputs']['children'].append(output_stdout)
        self.program.save()

    def test_submit(self):
        job = connection.ProgramJob()
        job['status'] = self.status
        job['project'] = self.project.id
        job['service'] = self.program
        job['inputs'] = {}
        parameter_values = {'string':'hello world'}
        job.process_inputs(parameter_values)
        job.save()
 
if __name__ == '__main__':
    unittest.main()
