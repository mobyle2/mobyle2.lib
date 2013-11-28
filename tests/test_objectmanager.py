# -*- coding: utf-8 -*-

from shutil import copyfile
import unittest
import os.path
from mobyle.common.config import Config
config = Config(os.path.join(os.path.dirname(__file__), 'test.conf'))

from mobyle.common.connection import connection
from mobyle.common.objectmanager import ObjectManager
from mobyle.common.data import RefData, ListData, StructData
from mobyle.common.users import User
from mobyle.common.project import Project


# Initiliase object manager
objectManager = ObjectManager()

class TestObjectManager(unittest.TestCase):


    def setUp(self):
        objects = connection.User.find({})
        for object in objects:
            object.delete()
        objects = connection.Project.find({})
        for object in objects:
            object.delete()

        self.example_user = connection.User()
        self.example_user['email'] = 'mobyle@example.com'
        self.example_user.save()

        self.my_project = connection.Project()
        self.my_project['owner'] = self.example_user['_id']
        self.my_project['name'] = 'MyProject'
        self.my_project.save()

    def test_add_new_data_and_delete(self):
        options = {}
        options['project'] = str(self.my_project['_id'])

        my_dataset = ObjectManager.add("sample", options, False)
        # now, my dataset status is “QUEUED”
        self.assertEqual(my_dataset['status'], ObjectManager.QUEUED)
        # Get path to the objects
        my_path = my_dataset.get_file_path()
        # Write a file to the dataset directory
        sample_file = os.path.join(os.path.dirname(__file__), 'test.fake')
        data_file = os.path.join(my_path, 'test.fake')
        copyfile(sample_file, data_file)

        # Update the schema according to the files, example:
        my_schema = RefData()
        my_schema['path'] = 'test.fake'
        my_schema['size'] = os.path.getsize(data_file)
        my_schema['format'] = "EDAM:123"
        my_schema['type'] = "EDAM:456"

        my_dataset.schema(my_schema)
        my_dataset.status(ObjectManager.READY)
        my_dataset.save()
        self.assertEqual(my_dataset['status'], ObjectManager.READY)
        self.assertTrue(os.path.exists(os.path.join(my_path, 'test.fake')))
        ObjectManager.delete(my_dataset['_id'])
        self.assertFalse(os.path.exists(os.path.join(my_path, 'test.fake')))
        self.assertTrue(ObjectManager.get(my_dataset['_id']) is None)

    def test_add_existing_data_and_delete(self):
        options = {}
        options['project'] = str(self.my_project['_id'])

        my_dataset = ObjectManager.add("sample", options, False)
        # now, my dataset status is “QUEUED”
        self.assertEqual(my_dataset['status'], ObjectManager.QUEUED)
        # Get path to the objects
        my_path = my_dataset.get_file_path()
        #Set reference path as an existing path
        options['path'] = os.path.dirname(__file__)
        # Update the schema according to the files, example:
        my_schema = RefData()
        sample_file = os.path.join(os.path.dirname(__file__), 'test.conf')
        my_schema['path'] = 'test.conf'
        my_schema['size'] = os.path.getsize(sample_file)
        my_schema['format'] = "EDAM:123"
        my_schema['type'] = "EDAM:456"
        options['schema'] = my_schema
        my_dataset = ObjectManager.add("sample", options, False)
        my_dataset.status(ObjectManager.READY)
        my_dataset.save()
        self.assertTrue(os.path.exists(os.path.join(options['path'], 'test.fake')))
        ObjectManager.delete(my_dataset['_id'])
        self.assertTrue(os.path.exists(os.path.join(options['path'], 'test.fake')))
        self.assertTrue(ObjectManager.get(my_dataset['_id']) is None)
