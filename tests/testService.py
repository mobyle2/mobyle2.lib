# -*- coding: utf-8 -*-
import unittest
from mobyle.common.service import *

import pymongo

from mongokit import ValidationError
from mobyle.common import users
import mobyle.common
from mobyle.common  import session

import mobyle.common.connection
mobyle.common.connection.init_mongo("mongodb://localhost/")

class TestUser(unittest.TestCase):

    def setUp(self):
       objects = mobyle.common.session.Service.find({})
       for object in objects:
         object.delete()
       
    def tearDown(self):
       objects = mobyle.common.session.Service.find({})
       for object in objects:
         object.delete()

    def test_insert(self):
        """
        test basic creation of an almost empty service
        """
        service = mobyle.common.session.Service()
        service['name'] = "test_service"
        service.save()
        services_list = mobyle.common.session.Service.find({'name': 'test_service'})
        count = 0
        for service in services_list:
          count+=1
        self.assertTrue(count==1)

    def test_inputs_creation(self):
        """
        test creation of a service with an input
        """
        service = mobyle.common.session.Service()
        service['name'] = "test_service_with_inputs"
        inputs = InputParagraph()
	service['inputs']=inputs
	input_1 = InputParameter()
        input_1['name']='test_input'
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
        #service = mobyle.common.session.Service()
        #service['name'] = "test_service_with_inputs"
        inputs = InputParagraph()
        #service['inputs']=inputs
        output = OutputParameter()
        output['name']='test_output'     
        inputs['children'].append(output)
        self.assertRaises(ValidationError,inputs.validate)
        #service.validate()
        #service.save()
