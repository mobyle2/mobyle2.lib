import unittest
from mobyle.common.data import *

class TestDataType(unittest.TestCase):

    def setUp(self):
	self.type_1 = IntegerDataType()
	self.type_2 = StringDataType()

    def test_check_method(self):
        self.assertTrue(self.type_1.check(4))

    def test_get_formats_method(self):
        self.assertEqual(self.type_1.get_formats(), 'IntegerDataFormat')

class TestDataFormat(unittest.TestCase):

    def setUp(self):
	self.format_1 = BinaryDataFormat()
	self.data_1 = Data(TextDataFormat(), 'file1')
	self.format_2 = IntegerDataFormat()
	
    def test_convert_method(self):
        self.assertEqual(self.format_1.convert(self.data_1).data_format, 'BinaryDataFormat')
	
    def test_validate_method(self):
        self.assertTrue(self.format_2.validate(4))
	
    def test_is_format_of_method(self):
        self.assertEqual(self.format_2.get_data_type(), 'IntegerDataType')
	
	
	
class TestData(unittest.TestCase):

    def setUp(self):
	type_1 = IntegerDataType()
	format_1 = IntegerDataFormat()
	self.nb_of_it = Data(format_1, 3)

    def test_data_type(self):
        self.assertEqual(self.nb_of_it.data_type, 'IntegerDataType')
	self.assertEqual(self.nb_of_it.value, 3)

class TestStructData(unittest.TestCase):

    def setUp(self):
	format_1 = IntegerDataFormat()
	format_2 = TextDataFormat()
	nb_of_it = Data(format_1, 5)
	filename = Data(format_2, 'toto')
	names = ['nb_it', 'file']
	data = [nb_of_it,filename]
	dico = dict(zip(names,data))
	self.structure = StructData(dico)

    def test_value(self):
        self.assertEqual(self.structure['file'], 'StringDataType')


class TestCollectionData(unittest.TestCase):

    def setUp(self):
	data_1 = Data(TextDataFormat(), 'file1')
	data_2 = Data(TextDataFormat(), 'file2')
	data_3 = Data(TextDataFormat(), 'file3')
	list_of_data_1 = [data_1, data_2, data_3]
	self.my_collection_1 = CollectionData(list_of_data_1)

    
    def test_dataType(self):
        self.assertEqual(self.my_collection_1.data_type, 'StringDataType')


	

if __name__=='__main__':
	unittest.main()


