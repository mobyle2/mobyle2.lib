# -*- coding: utf-8 -*-
'''
Created on Nov. 18, 2013

@license: GPLv3
'''
from mongokit import CustomType, ValidationError

class MKStruct(dict):

    structure = {}

    def __init__(self, values={}):
        super(MKStruct, self).__init__(self)
        self.structure = self._populate_structure()
        for key, value in self.structure.items():
            if type(value) in [int, str]:
                self[key]=value
            elif type(value) is list:
                self[key] = []
            elif type(value) is dict:
                self[key] = {}
        if values:
            for key, value in values.items():
                self[key]=value

    def _populate_structure(self):
        new_structure = {}
        for cls in self.__class__.mro()[::-1]:
            if cls is not object:
                if hasattr(cls,'structure'):
                    new_structure.update(cls.structure)
        return new_structure

    def __setitem__(self, key, val):
    	if key not in self.structure.keys():
            raise KeyError("Trying to set key '%s' in object, not part of authorized properties %s" % (key, self.structure.keys()))
        #elif not(isinstance(val,self.structure[key])):
        #    raise ValueError   
    	super(MKStruct, self).__setitem__(key, val)

    validators = {}

    def validate(self):
        for key, validator in self.validators.items():
            try:
                validator(self[key])
            except Exception, exc:
                raise ValidationError(exc)

    def to_bson(self):
        self.validate()
        return self

    @classmethod
    def to_python(cls, value):
        return cls(value)

class MKStructAdapter(CustomType):
    structure = {
                }

    mongo_type = dict
    python_type = MKStruct

    def __init__(self, python_class):
        super(MKStructAdapter, self).__init__()
        self.python_class = python_class

    def to_bson(self, value):
        if value is not None:
            return value.to_bson()
    
    def to_python(self, value):
        if value is not None:
            return self.python_class.to_python(value)
