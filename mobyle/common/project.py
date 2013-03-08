# -*- coding: utf-8 -*-
'''
Created on Nov. 23, 2012

@author: E. LEGROS
@contact: emeline.legros@ibcp.fr
@license: GPLv3
'''

from mongokit import Document, IS

from mobyle.common.config import Config

from mobyle.common.job import Job
#TODO: reimport as soon as Data object is MongoKit-compatible
#from mobyle.common.data import Data
from mobyle.common.users import User

from mf.annotation import mf_decorator




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
                  #TODO: switch to Data list as soon as 
                  # Data is MongoKit-compatible 
                  'data' : [basestring],
                  #TODO: role may be modified for ACLs implementation?
                  'users' : [{'user': User, 'role': basestring}],
                  'notebook' : basestring
                }

    required_fields = ['name', 'owner']

    use_autorefs = True

    @property	
    def creation_date(self):
        """
        Get project creation date
        :returns: the attribute value
        :rtype: datetime
        """
        return self['_id'].generation_time

    def add_user(self, user, role):
        """
	add_user is a method defined to attach a new user and its role into the project.
	:param user: user to be associated to the project.
        :type user: :class:`User` object.
	:param role: user's role in the project.
        :type role: string.
	"""
        self['users'].append({'user': user, 'role': role})

