# -*- coding: utf-8 -*-
'''
Created on Nov. 18, 2013

@license: GPLv3
'''
from mongokit import CustomType

class MKStruct(dict):

    structure = {}

    def __init__(self, values={}):
        super(MKStruct, self).__init__(self)
        new_structure = {}
        if hasattr(super(MKStruct, self),'structure'):
            new_structure.update(super(MKStruct, self).structure)
        if hasattr(self,'structure'):
            new_structure.update(self.structure)
        self.structure = new_structure
        for key, value in self.structure.items():
            print key, value
            if type(value) in [int, str]:
                self[key]=value
        if values:
            for key, value in values.items():
                self[key]=value

    def __setitem__(self, key, val):
    	if key not in self.structure.keys():
            raise KeyError
        #elif not(isinstance(val,self.structure[key])):
        #    raise ValueError   
    	super(MKStruct, self).__setitem__(key, val)

class MKStructAdapter(CustomType):
    structure = {
                }

    mongo_type = dict
    python_type = MKStruct

    def __init__(self, python_class):
        super(MKStructAdapter, self).__init__()
        self.python_type = python_class

    def to_bson(self, value):
        return value
    
    def to_python(self, value):
        if value is not None:
            return self.python_type(value)
