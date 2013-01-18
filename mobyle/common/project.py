# -*- coding: utf-8 -*-
'''
Created on Nov. 23, 2012

@author: E. LEGROS
@contact: emeline.legros@ibcp.fr
@license: GPLv3
'''

from datetime import datetime
from mongokit import Document

from mobyle.common import session
from mobyle.common.config import Config

from mobyle.common.job import Job
from mobyle.common.data import Data
from mobyle.common.users import User

import mf.annotation
from mf.annotation import *


@mf_decorator
class Project(Document):
    """
    Project is a class that stores all information about a project (owner username, inputs, outputs, job id). 
    It's initialized by two parameters: the name of the owner of the project and the project name itself.
    """

    __collection__ = 'projects'
    __database__ = Config.config().get('app:main','db_name')

    structure = { 'name' : basestring, 'owner' : basestring, 'job_ids' : [ Job ], 'data_ids' : [ basestring ], 'users' : [ { 'user' : User, 'role' : basestring } ], 'date_creation': datetime }

    required_fields = ['name', 'owner']

    use_autorefs = True
	

    def add_data(self, data):	
        """
	add_data is a method defined to attach a new data_id into the project. 
	:param data: data to be associated to the project.
        :type data: :class:`Data` object.
        """
	self['data_ids'].append(data)


    def add_list_of_data(self, data_list):
        """
	add_list_of_data is a method defined to attach a set of data_ids into the project.
        :param data_list: list of :class:`Data` object
        :type data_list: array containing :class:`Data` object.
	"""
	for i in range(len(data_list)):
		self['data_ids'].append(data_list[i])


    def add_job(self, job):	
        """
	add_job is a method defined to attach a new job_id into the project. 
        :param job: job to be associated to the project.
        :type job: :class:`Job` object.
        """
	self['job_ids'].append(job)
	
	
    def get_creation_time(self):
	"""
	get_creation_time returns the project creation date time according to the _id
	:return: the project creation datetime.
	:rtype: string.
	"""
	return self['creation_time']
	

    def add_user(self,user,role):
	"""
	add_user is a method defined to attach a new user and its role into the project.
	:param user: user to be associated to the project.
        :type user: :class:`User` object.
	:param role: user's role in the project.
        :type role: string.
	"""
	self['users'].append({ 'user' : user, 'role' : role})



session.register([Project])
