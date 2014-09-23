# -*- coding: utf-8 -*-

from shutil import copyfile
import unittest
import os.path
from mobyle.common.config import Config
config = Config(os.path.join(os.path.dirname(__file__), 'test.conf'))

from mobyle.common.connection import connection
from mobyle.common.objectmanager import ObjectManager, AccessMode
from mobyle.common.data import RefData, ListData, StructData
from mobyle.common.users import User
from mobyle.common.project import Project
from mobyle.common.tokens import Token
from mobyle.common.type import FormattedType

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
        my_schema['type'] = FormattedType()
        my_schema['type']['format_terms'] = ["EDAM:123"]
        my_schema['type']['data_terms'] = ["EDAM:456"]

        my_dataset.schema(my_schema)
        my_dataset.status(ObjectManager.READY)
        my_dataset.save_with_history(['test.fake'],'new file')
        self.assertEqual(my_dataset['status'], ObjectManager.READY)
        self.assertTrue(os.path.isfile(os.path.join(my_path, 'test.fake')))
        ObjectManager.delete(my_dataset['_id'])
        self.assertFalse(os.path.isfile(os.path.join(my_path, 'test.fake')))
        self.assertTrue(ObjectManager.get(my_dataset['_id']) is None)

    def test_add_existing_data_and_delete(self):
        options = {}
        options['project'] = str(self.my_project['_id'])

        my_dataset = ObjectManager.add("sample", options, False)
        # now, my dataset status is “QUEUED”
        self.assertEqual(my_dataset['status'], ObjectManager.QUEUED)

        #Set reference path as an existing path
        options['path'] = os.path.dirname(__file__)
        # Update the schema according to the files, example:
        my_schema = RefData()
        sample_file = os.path.join(os.path.dirname(__file__), 'test.conf')
        my_schema['path'] = 'test.conf'
        my_schema['size'] = os.path.getsize(sample_file)
        my_schema['type'] = FormattedType()
        my_schema['type']['format_terms'] = ["EDAM:123"]
        my_schema['type']['data_terms'] = ["EDAM:456"]
        options['schema'] = my_schema
        my_dataset = ObjectManager.add("sample", options, False)
        my_dataset.status(ObjectManager.READY)
        my_dataset.save()
        self.assertTrue(os.path.isfile(os.path.join(options['path'],
                                                    'test.fake')))
        ObjectManager.delete(my_dataset['_id'])
        self.assertTrue(os.path.isfile(os.path.join(options['path'],
                                                    'test.fake')))
        self.assertTrue(ObjectManager.get(my_dataset['_id']) is None)

    def test_add_complex_object_and_delete(self):
        options = {}
        options['project'] = str(self.my_project['_id'])

        my_dataset = ObjectManager.add("sample", options, False)

        sample_bam = os.path.join(os.path.dirname(__file__), 'test.bam')
        sample_bai = os.path.join(os.path.dirname(__file__), 'test.bai')

        options['format'] = 'EDAM:bam_format+EDAM:bai_format'
        options['type'] = 'EDAM:bam+EDAM:bai'
        options['type_name']= 'bam_data+bai_data'
        options['uncompress'] = True
        options['group'] = True
        options['name'] = 'bam+bai'
        options['status'] = ObjectManager.UNCOMPRESSED
        options['files'] = [ sample_bam, sample_bai ]
        options['id'] = str(my_dataset['_id'])

        my_dataset_from_manager = ObjectManager.update(ObjectManager.UNCOMPRESSED, options)
        my_dataset_from_manager = my_dataset_from_manager[0]
        
        ObjectManager.delete(my_dataset['_id'])
        self.assertTrue(my_dataset_from_manager['status'] ==
        ObjectManager.NEED_EDIT)
        self.assertTrue(my_dataset_from_manager['data']['type']['data_terms'][0]==options['type'])
        self.assertTrue('properties' in my_dataset_from_manager['data'])
        self.assertTrue('bam_data' in my_dataset_from_manager['data']['properties'])
        self.assertTrue('bai_data' in my_dataset_from_manager['data']['properties'])
        self.assertTrue(my_dataset_from_manager['data']['properties']['bam_data']['type']['format_terms'][0]=='EDAM:bam_format')
        self.assertTrue(my_dataset_from_manager['data']['properties']['bam_data']['type']['data_terms'][0]=='EDAM:bam')


    def test_update_existing_projectdata(self):
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
        my_schema['type'] = FormattedType()
        my_schema['type']['format_terms'] = ["EDAM:123"]
        my_schema['type']['data_terms'] = ["EDAM:456"]

        my_dataset.schema(my_schema)
        my_dataset.status(ObjectManager.READY)
        my_dataset.save()
        self.assertEqual(my_dataset['status'], ObjectManager.READY)
        self.assertTrue(os.path.isfile(os.path.join(my_path, 'test.fake')))

        # Now extract my object from manager
        my_dataset_from_manager = ObjectManager.get(my_dataset['_id'])
        # Update files
        my_dataset_path = my_dataset.get_file_path()
        my_new_file = os.path.join(my_dataset_path, 'new.fake')
        f = open(my_new_file, 'w')
        f.write('hi there\n')
        f.close()
        my_dataset_schema_from_manager = my_dataset_from_manager.schema()
        my_dataset_schema_from_manager['path'] = 'new.fake'
        my_dataset_schema_from_manager['size'] = os.path.getsize(my_new_file)
        my_dataset_from_manager.save()
        # Get it from db again, to be sure everything is fine in db
        my_dataset_from_manager = ObjectManager.get(my_dataset['_id'])
        # Check schema has been updated
        self.assertTrue(my_dataset_from_manager['data']['path'] == 'new.fake')
        # Now clean up
        ObjectManager.delete(my_dataset['_id'])
        self.assertFalse(os.path.isfile(os.path.join(my_path, 'new.fake')))
        self.assertTrue(ObjectManager.get(my_dataset['_id']) is None)

    def test_get_token(self):
        options = {}
        options['project'] = str(self.my_project['_id'])

        my_dataset = ObjectManager.add("sample", options, False)
        token = ObjectManager.get_token(my_dataset['_id'], ['test.fake'],
                                        AccessMode.READONLY)
        data_token = connection.Token.find_one({"token": token})
        self.assertTrue(data_token['data']['id'] == str(my_dataset['_id']))
        self.assertTrue(data_token['data']['access'] == AccessMode.READONLY)
        self.assertTrue(data_token['data']['file'][0] == 'test.fake')

    def test_update_projectdata(self):
        options = {}
        options['project'] = str(self.my_project['_id'])

        my_dataset = ObjectManager.add("sample", options, False)
        # now, my dataset status is “QUEUED”
        self.assertEqual(my_dataset['status'], ObjectManager.QUEUED)
        # Get path to the objects
        my_path = my_dataset.get_file_path()

        # Write a file to the dataset directory
        sample_file = os.path.join(os.path.dirname(__file__), 'test.fake')

        options['id'] = str(my_dataset['_id'])
        options['format'] = 'text'
        options['type'] = 'text/plain'
        options['uncompress'] = False
        options['group'] = False
        options['files'] = [sample_file]
        ObjectManager.update(ObjectManager.DOWNLOADED, options)
        my_dataset_from_manager = ObjectManager.get(my_dataset['_id'])
        file_name = my_dataset_from_manager['data']['path']
        self.assertTrue(os.path.isfile(os.path.join(my_path, file_name)))
        self.assertEqual(my_dataset_from_manager['status'], ObjectManager.DOWNLOADED)

    def test_store_and_update_file_projectdata(self):
        options = {}
        options['project'] = str(self.my_project['_id'])

        # Write a file to the dataset directory
        sample_file = os.path.join(os.path.dirname(__file__), 'test.fake')

        options['format'] = 'text'
        options['type'] = 'text/plain'
        options['uncompress'] = False
        options['group'] = False
        options['name'] = 'test.fake'

        my_dataset_from_manager = ObjectManager.store('test.fake',sample_file, options)
        my_path = my_dataset_from_manager.get_file_path()
        self.assertTrue(os.path.isfile(os.path.join(my_path, 'test.fake')))
        self.assertEqual(my_dataset_from_manager['status'], ObjectManager.DOWNLOADED)

        sample_file2 = os.path.join(os.path.dirname(__file__), 'test.conf')

        options['id'] = str(my_dataset_from_manager['_id'])
        options['name'] = 'test.conf'
        my_updated_dataset_from_manager = ObjectManager.store('test.conf',
                                                                sample_file2,
                                                                options)

        my_path2 = my_dataset_from_manager.get_file_path()
        self.assertTrue(my_path == my_path2)
        self.assertTrue(os.path.isfile(os.path.join(my_path2, 'test.conf')))
        self.assertFalse(os.path.isfile(os.path.join(my_path, 'test.fake')))

    def test_update_projectdata_after_uncompress_not_grouped(self):
        options = {}
        options['project'] = str(self.my_project['_id'])

        my_dataset = ObjectManager.add("sample", options, False)
        # now, my dataset status is “QUEUED”
        self.assertEqual(my_dataset['status'], ObjectManager.QUEUED)

        # Write a file to the dataset directory
        sample_file1 = os.path.join(os.path.dirname(__file__), 'test.fake')
        sample_file2 = os.path.join(os.path.dirname(__file__), 'test.conf')

        options['id'] = str(my_dataset['_id'])
        options['format'] = 'auto'
        options['type'] = 'text/plain'
        options['uncompress'] = True
        options['group'] = False
        options['files'] = [sample_file1, sample_file2]
        new_datasets = ObjectManager.update(ObjectManager.DOWNLOADED, options)

        my_dataset_from_manager = ObjectManager.get(new_datasets[0]['_id'])
        self.assertTrue(my_dataset_from_manager['status'] == ObjectManager.DOWNLOADED)
        self.assertTrue(len(new_datasets) == 2)
        main_dataset_from_manager = ObjectManager.get(my_dataset['_id'])
        self.assertTrue(main_dataset_from_manager is None)

    def test_update_projectdata_after_uncompress_grouped(self):
        options = {}
        options['project'] = str(self.my_project['_id'])

        my_dataset = ObjectManager.add("sample", options, False)
        # now, my dataset status is “QUEUED”
        self.assertEqual(my_dataset['status'], ObjectManager.QUEUED)
        # Get path to the objects
        my_path = my_dataset.get_file_path()

        # Write a file to the dataset directory
        sample_file1 = os.path.join(os.path.dirname(__file__), 'test.fake')
        sample_file2 = os.path.join(os.path.dirname(__file__), 'test.conf')

        options['id'] = str(my_dataset['_id'])
        options['format'] = 'auto'
        options['type'] = 'text/plain'
        options['uncompress'] = True
        options['group'] = True
        options['files'] = [sample_file1, sample_file2]
        ObjectManager.update(ObjectManager.DOWNLOADED, options)

        main_dataset_from_manager = ObjectManager.get(my_dataset['_id'])
        self.assertTrue(main_dataset_from_manager is not None)
        keys = main_dataset_from_manager['data']['properties'].keys()
        self.assertTrue(len(keys) == 2)
        file_name = main_dataset_from_manager['data']['properties'][keys[0]]['path']
        self.assertTrue(os.path.isfile(os.path.join(my_path, file_name)))
        #self.assertEqual(file_name, 'test.fake')
        file_name = main_dataset_from_manager['data']['properties'][keys[1]]['path']
        self.assertTrue(os.path.isfile(os.path.join(my_path, file_name)))
        #self.assertEqual(file_name, 'test.conf')

    def test_history(self):
        options = {}
        options['project'] = str(self.my_project['_id'])

        my_dataset = ObjectManager.add("sample", options, False)
        # now, my dataset status is “QUEUED”
        self.assertEqual(my_dataset['status'], ObjectManager.QUEUED)

        # Write a file to the dataset directory
        sample_file1 = os.path.join(os.path.dirname(__file__), 'test.fake')
        sample_file2 = os.path.join(os.path.dirname(__file__), 'test.conf')

        options['id'] = str(my_dataset['_id'])
        options['format'] = 'text'
        options['type'] = 'text/plain'
        options['uncompress'] = True
        options['group'] = True
        options['files'] = [sample_file1, sample_file2]
        ObjectManager.update(ObjectManager.DOWNLOADED, options)
        history = ObjectManager.history(my_dataset['_id'])
        self.assertTrue(history is not None and len(history) == 1)

    def test_isarchive(self):
        self.assertTrue(ObjectManager.isarchive('test.zip') is not None)
        self.assertTrue(ObjectManager.isarchive('test.tar.gz') is not None)
        self.assertTrue(ObjectManager.isarchive('test.bz2') is not None)
        self.assertTrue(ObjectManager.isarchive('test.txt') is None)

