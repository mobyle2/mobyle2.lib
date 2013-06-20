# -*- coding: utf-8 -*-
'''
Created on Nov. 23, 2012

@author: E. LEGROS
@contact: emeline.legros@ibcp.fr
@license: GPLv3
'''

from mongokit import Document, ObjectId
from mf.annotation import mf_decorator
from mf.views import MF_READ, MF_EDIT

from .connection import connection
from .config import Config
#from .job import Job
#TODO: reimport as soon as Data object is MongoKit-compatible
#from .data import Data
#from .users import User
from .data import AbstractData


@mf_decorator
@connection.register
class Project(Document):
    """
    Project is a class that stores all information about a project (owner username, inputs, outputs, job id). 
    It's initialized by two parameters: the name of the owner of the project and the project name itself.
    """

    __collection__ = 'projects'
    __database__ = Config.config().get('app:main','db_name')

    structure = { 'name' : basestring, 
                  'owner' : ObjectId, 
                  'jobs' : [ObjectId],
                  'services' : [ObjectId],
                  #TODO: role may be modified for ACLs implementation?
                  'users' : [{'user': ObjectId, 'role': basestring}],
                  'notebook' : basestring
                }

    required_fields = ['name', 'owner']

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
        self['users'].append({'user': user['_id'], 'role': role})

    def my(self, control, request, authenticated_userid=None,admin=False):
        user = connection.User.find_one({'email' : authenticated_userid})
        if user and user['admin'] and admin:
            return {}
        if control == MF_READ:
            return {"users": {"$elemMatch": {'user': user['_id']}}}
        if control == MF_EDIT:
            # User must be one of project users
            return {"users": {"$elemMatch": {'user': user['_id'], "$or": [ {'role': 'contributor'},{ 'role': 'manager'}]}}}
            

@mf_decorator
@connection.register
class ProjectData(Document):

    __collection__ = 'projects_data'
    __database__ = Config.config().get('app:main','db_name')

    structure = { 'name' : basestring, 
                  'description' : basestring, 
                  'tags' : [basestring],
                  'project': ObjectId,
                  'data': AbstractData,
                  'status' : int
                  #TODO: add data provenance information
                }

    def my(self, control, request, authenticated_userid=None):
        user = connection.User.find_one({'email' : authenticated_userid})
        if user and user['admin'] and admin:
            return {}
        if control == MF_READ:
            project_filter = {"users": {"$elemMatch": {'user': user['_id']}}}
        if control == MF_EDIT:
            # User must be one of project users
            project_filter = {"users": {"$elemMatch": {'user': user['_id'], "$or": [ {'role': 'contributor'},{ 'role': 'manager'}]}}}
        project_ids_curs = connection.Project.find(project_filter,{'_id':1})
        project_ids = []
        for project_id in project_ids_curs:
            project_ids.append(project_id['_id'])
        return {"project": {"$in": project_ids}}
