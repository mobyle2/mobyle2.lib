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

    structure = { 'name' : basestring, 
                  'owner' : User, 
                  'jobs' : [Job], 
                  'data' : [basestring], 
                  'users' : [{'user':User, 'role':basestring}],
                }

    required_fields = ['name', 'owner']

    use_autorefs = True

    @property	
    def creation_date():
        return self['_id'].generation_time

    def add_user(self,user,role):
	"""
	add_user is a method defined to attach a new user and its role into the project.
	:param user: user to be associated to the project.
        :type user: :class:`User` object.
	:param role: user's role in the project.
        :type role: string.
	"""
	self['users'].append({'user': user, 'role': role})


