# -*- coding: utf-8 -*-
'''
Created on Nov. 12, 2012

@author: E. LEGROS
@contact: emeline.legros@ibcp.fr
@license: GPLv3
'''



import abc
from abc import ABCMeta
from abc import abstractmethod
from mobyleError import MobyleError


class Data:
    """
    Data is a class that stores and manipulates data. 
    It's composed by two parameters: one data format and one value.
    """

    def __init__(self, data_format = None, value = None):
	"""
	:param data_format: the identifier name of the data format
	:type data_format: DataFormat
	:param value: the value associated to the data
	:type value: not defined specifically. Could be anything.
	"""

	if(not isinstance(data_format, DataFormat)):
	    msg = "Programming error! Input data format must be an instance of DataFormat class"
	    raise MobyleError , msg 
        self._data_format = data_format.__class__.__name__
	self._data_type = data_format.get_data_type()
	self._value = value 


    @property
    def data_type(self):
        """
	:return: the data_type of a :class:`Data` object.
	:rtype: DataType
	"""
        return self._data_type

    @property
    def data_format(self):
        """
	:return: the data_format of a :class:`Data` object.
	:rtype: DataFormat
	"""
        return self._data_format

    @property
    def value(self):
        """
	:return: the value associated to the dataType.
	:rtype: not defined specifically. could be anything.
	"""
        return self._value


class StructData(Data):
    """
    StructData is a class that stores and manipulates structure of data. 
    It's composed by a set of :class:`Data` of any kinds.
    """
    def __init__(self, input_dict = None):
	"""
	:param input_dict: dictionary that contains input names and values of the structure
	:type input_dict: python dictionary (ex: dict = { 'zero': 0, 'one': 1, 'two': 2 })
	"""
        self._input_struct = input_dict
	
    def __getitem__(self, key):
	"""
	:param key: name of the parameter in the dictionary
	:type key: string
	:return: the value associated to the key.
	:rtype: not defined specifically. Could be anything.
	"""
        return self._input_struct[key]._data_type


class CollectionData():
    """
    CollectionData is a class that stores and manipulates a set of :class:`Data` of a kind. 
    """
    def __init__(self, list_of_data = None):
	"""
	:param list_of_data: list of input :class:`Data` objects.
	:type list_of_data: array
	"""
	temp_data_type = list_of_data[0].data_type
	for data in range( len(list_of_data) ):
	    if(list_of_data[data].data_type!=temp_data_type):
		msg = "Programming error! Every entries of the list must have the same data type"
		raise MobyleError , msg 
        self._data_type = temp_data_type

    @property
    def data_type(self):
        """
	:return: the data_type of a :class:`Data` object.
	:rtype: string
	"""
        return self._data_type


#----------------------
# DATA TYPE MANAGEMENT

class DataType(object):
    """
    DataType is an abstract class that defines the type of a :class:`Data`.
    """ 
    __metaclass__ = ABCMeta

    @abstractmethod
    def check(self, value):
	"""check is an abstract method defined in each :class:`DataType`'s subclasses. 
	This method controls if a value really belongs to a :class:`DataType`.
	
	:param value: the value to be controled.
	:type value: not defined specifically. Could be anything.
	"""
	pass
    
    @abstractmethod
    def get_formats(self):
	"""
	get_formats is an abstract method defined in each :class:`DataType`'s subclasses.
	This method returns all formats available for a :class:`DataType`.
	"""
        pass


class SimpleDataType(DataType):
    """
    SimpleDataType is a class that inherits from :class:`DataType` and contains simple data types as Integer, String... 
    """
    def check(self, value):
	"""check is defined in each :class:`SimpleDataType`'s subclasses.
	This method controls if a value really belongs to a :class:`DataType`.
	
	:param value: the value to be controled.
	:type value: not defined specifically. Could be anything.
	"""
	pass
    
    def get_formats(self):
	"""get_formats method returns all formats available for a :class:`SimpleDataType`.
	
	:return: the data_format of a :class:`SimpleDataType` object.
	:rtype: string
	"""
	return self._data_format.__class__.__name__

    def get_data_type(self):
	"""get_data_type returns the data type of the :class:`SimpleDataType`.
	
	:return: the data_type of a :class:`SimpleDataType` object.
	:rtype: string
	"""
	return self.__class__.__name__



class EDAMDataType(DataType):
    """
    EDAMDataType is a class that inherits from :class:`DataType` and contains data types defined in EDAM ontology (http://edamontology.org/). 
    """
    def __init__(self, EDAM_id = None):
	"""
	:param EDAM_id: EDAM ontology identifier.
	:type EDAM_id: integer
	"""
	self._id = EDAM_id
	self._formats = get_formats( )
	
    def check(self, value):
	"""check method controls if a value really belongs to an :class:`EDAMDataType`.
	
	:param value: the value to be controled.
	:type value: not defined specifically. Could be anything.
	:return: True if the value parameter is an :class:`EDAMDataType` False otherwise.
	:rtype: boolean
	"""	
        return True
    
    def get_formats(self):
	"""get_formats method returns all formats available for an :class:`EDAMDataType`.
	Remark: results must be read in a database.
	
	:return: the data_formats of an :class:`EDAMDataType` object.
	:rtype: string array
	"""
	# results must be read in a database
	return formats["PDB", "mol2"]

class IntegerDataType(SimpleDataType):
    """
    IntegerDataType is a class that inherits from :class:`SimpleDataType` and contains all values of Integer type. 
    """
    def __init__(self):
	"""
	Defines _data_format parameter as an :class:`IntegerDataFormat` object.
	"""
	self._data_format = IntegerDataFormat()
	
    def check(self, value):
	"""check method controls if a value really belongs to :class:`IntegerDataType` (ie, is an integer).
	
	:param value: the value to be controled.
	:type value: not defined specifically. Could be anything.
	:return: True if the value parameter is an integer False otherwise.
	:rtype: boolean
	"""	
        return True

class StringDataType(SimpleDataType):
    """
    StringDataType is a class that inherits from :class:`SimpleDataType` and contains all values of String type. 
    """
    def check(self, value):
	"""check method controls if a value really belongs to :class:`StringDataType` (ie, is a string).
	
	:param value: the value to be controled.
	:type value: not defined specifically. Could be anything.
	:return: True if the value parameter is a string False otherwise.
	:rtype: boolean
	"""	
        return True
	


#------------------------
# DATA FORMAT MANAGEMENT

class DataFormat(object):
    """
    DataFormat is an abstract class that defines the format of a data.
    """ 
    __metaclass__ = ABCMeta

    @abstractmethod
    def convert(self, data):
	"""convert is defined in each :class:`DataFormat`'s subclasses.
	This method creates a new object with the same value as the input but in another data format.
	
	:param data: the value to be converted into another data format.
	:type data: not defined specifically.
	"""
	pass
    
    @abstractmethod
    def validate(self, value):
	"""validate is defined in each :class:`DataFormat`'s subclasses.
	This method controls if a value is in the right data format or not.
	
	:param value: the value to be controled.
	:type value: not defined specifically. Could be anything.
	"""
	pass
    
    @abstractmethod
    def get_data_type(self):
	"""
	get_data_type is defined in each :class:`DataFormat`'s subclasses.
	This method returns the data type associated to a :class:`DataFormat`.
	"""
    	pass
    

class SimpleDataFormat(DataFormat):
    """
    SimpleDataFormat inherits form :class:`DataFormat` class and contains simple data format as Integer, String... 
    """ 
    def convert(self, data):
	"""convert is defined in each :class:`SimpleDataFormat`'s subclasses.
	This method creates a new object with the same value as the input but in another data format.
	
	:param data: the value to be converted into another data format.
	:type data: not defined specifically.
	"""
	pass
    
    def validate(self, value):
	"""validate is defined in each :class:`SimpleDataFormat`'s subclasses.
	This method controls if a value is a simple data format or not.
	
	:param value: the value to be controled.
	:type value: not defined specifically. Could be anything.

	"""
	pass
    
    def get_data_type(self):
	"""get_data_type method returns the data type associated to a :class:`SimpleDataFormat`.
	
	:return: The data type associated to this data format.
	:rtype: string
	"""
	return self.__class__.__name__


class IntegerDataFormat(SimpleDataFormat):
    """
    IntegerDataFormat inherits form :class:`SimpleDataFormat` class and defined Integers. 
    """ 
    def convert (self, data):
	"""convert method creates a new object with the same value as the input but in another data format.
	
	:param data: the value to be converted into another data format.
	:type data: not defined specifically.
	"""
	pass

    def validate(self, value):
	"""validate controls if a value is an integer or not.
	
	:param value: the value to be controled.
	:type value: not defined specifically. Could be anything.
	:return: True if the value parameter is an integer False otherwise.
	:rtype: boolean
	"""
        return True
    
    def get_data_type(self):
	"""get_data_type method returns the data type associated to an :class:`IntegerDataFormat`.
	
	:return: The data type associated to this data format.
	:rtype: string
	"""
    	return IntegerDataType().__class__.__name__
    
class TextDataFormat(DataFormat):
    """
    TextDataFormat inherits form :class:`DataFormat` class and defined all kind of text files. 
    """ 
    def convert (self, data):
	"""convert method creates a new object with the same value as the input but in a text data format.
	
	:param data: the value to be converted into text data format.
	:type data: not defined specifically.
	:return: create a new object from data converted in a :class:`TextDataFormat` format.
	:rtype: Data object
	"""
	return Data(TextDataFormat(), data.value)
     
    def validate(self, value):
	"""validate controls if a value is a text file or not.
	
	:param value: the value to be controled.
	:type value: not defined specifically. Could be anything.
	:return: True if the value parameter is a text file False otherwise.
	:rtype: boolean
	"""
        return True
    
    def get_data_type(self):
	"""get_data_type method returns the data type associated to a :class:`TextDataFormat`.
	
	:return: The data type associated to this data format.
	:rtype: string
	"""
    	return StringDataType().__class__.__name__ # return an instance of the specific associated data type not necessarily StringDataType!

class BinaryDataFormat(DataFormat):
    """
    BinaryDataFormat inherits form :class:`DataFormat` class and defined all kind of binary files. 
    """ 	
    def convert (self, data):
	"""convert method creates a new object with the same value as the input but in a binary data format.

	:param data: the value to be converted into binary data format.
	:type data: not defined specifically.
	:return: create a new object from data converted in a :class:`BinaryDataFormat` format.
	:rtype: Data object
	"""
	return Data(BinaryDataFormat(), data.value)
     
    def validate(self, value):
	"""validate controls if a value is a binary file or not.
	
	:param value: the value to be controled.
	:type value: not defined specifically. Could be anything.
	:return: True if the value parameter is a binary file False otherwise.
	:rtype: boolean
	"""
        return True
    
    def get_data_type(self):
	"""get_data_type method returns the data type associated to a :class:`BinaryDataFormat`.
	
	:return: The data type associated to this data format.
	:rtype: string
	"""
    	return 0 # return an instance of the specific associated data type

