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
                  'users' : [{'user': ObjectId, 'role': basestring}],
                  'notebook' : basestring,
                  'public' : bool
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

    @staticmethod
    def my_project_acl_filter(control, request, authenticated_userid=None):
        # find the user corresponding to the provided email
        user = connection.User.find_one({'email' : authenticated_userid})
        # id is set if user exists, otherwise set to None so that the filter
        # works even for unauthenticated users.
        user_id = user['_id'] if user else None
        # admin_mode tells wether the admin user is in admin mode and should access everything
        admin_mode = hasattr(request,'session') and 'adminmode' in request.session
        if user and user['admin'] and admin_mode:
            # admin_mode = provide everything
            project_filter = {}
        elif control == MF_READ:
            # read: elements for projects where the user is active or where he 
            project_filter = {"$or": [{"users": {"$elemMatch": {'user': user_id}}},{'public':True}]}
        elif control == MF_EDIT:
            # User must be one of project contributors or managers
            if user is None:
                project_filter = None
            else:
                project_filter = {"users": {"$elemMatch": {'user': user_id, "$or": [ {'role': 'contributor'},{ 'role': 'manager'}]}}}
        return project_filter

    def my(self, control, request, authenticated_userid=None):
        return self.my_project_acl_filter(control, request, authenticated_userid)
            
class ProjectDocument(Document):
    """
    ProjectDocument is an abstract class which defines the ACLs of project-contained elements.
    The ACLs of such documents are completely defined by the users of the containing project
    """

    def my(self, control, request, authenticated_userid=None):
        project_filter = Project.my_project_acl_filter(control, request, authenticated_userid)
        if project_filter == {}:
            return project_filter
        else:
            project_ids_curs = connection.Project.find(project_filter,{'_id':1})
            project_ids = []
            for project_id in project_ids_curs:
                project_ids.append(project_id['_id'])
            return {"project": {"$in": project_ids}}

@mf_decorator
@connection.register
class ProjectData(ProjectDocument):

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

