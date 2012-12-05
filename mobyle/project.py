# -*- coding: utf-8 -*-
'''
Created on Nov. 23, 2012

@author: E. LEGROS
@contact: emeline.legros@ibcp.fr
@license: GPLv3
'''

from mobyle import session

from ming.datastore import DataStore
from ming import Session
from ming import Document, Field, schema

from ming.odm import ODMSession
from ming.odm.declarative import MappedClass
from ming.odm.property import FieldProperty, RelationProperty
from ming.odm.property import ForeignIdProperty



class Project(Document):
    """
    Project is a class that stores all information about a project (owner username, inputs, outputs, job id). 
    It's initialized by two parameters: the name of the owner of the project and the project name itself.
    """

    class __mongometa__:
        session = session
        name = "projects"
	
    _id = Field(schema.ObjectId)
    name = Field(str,required=True)
    owner = Field(str,required=True)
    job_ids = Field([schema.ObjectId],if_missing=[])
    data_ids = Field([schema.ObjectId],if_missing=[])
    users = Field([dict(user=[schema.ObjectId],role=[str])],if_missing=[])

	
    def __init__(self, project_owner = None, project_name = None):
	"""
	:param project_owner: name of the project owner 
	:type project_owner: string
	:param project_name: name of the project 
	:type project_name: string
	"""
        self.name = project_name
	self.owner = project_owner
	

    def add_data(self, data):	
        """
	add_data is a method defined to attach a new data_id into the project. 
	:param data: data to be associated to the project.
        :type data: :class:`Data` object.
        """
	self.data_ids.append(data._id)


    def add_list_of_data(self, data_list):
        """
	add_list_of_data is a method defined to attach a set of data_ids into the project.
        :param data_list: list of :class:`Data` object
        :type data_list: array containing :class:`Data` object.
	"""
	for i in range(len(data_list)):
		self.data_ids.append(data_list[i]._id)


    def add_job(self, job):	
        """
	add_job is a method defined to attach a new job_id into the project. 
        :param job: job to be associated to the project.
        :type job: :class:`Job` object.
        """
	self.job_ids.append(job._id)
	
	
    def get_creation_time(self):
	"""
	get_creation_time returns the project creation date time according to the _id
	:return: the project creation datetime.
	:rtype: string.
	"""
	return self._id.generation_time
	

    def add_user(self,user,role):
	"""
	add_user is a method defined to attach a new user and its role into the project.
	:param user: user to be associated to the project.
        :type user: :class:`User` object.
	:param role: user's role in the project.
        :type role: string.
	"""
	self.users.append({user._id : role})




