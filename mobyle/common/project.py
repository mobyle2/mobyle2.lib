# -*- coding: utf-8 -*-
'''
Created on Nov. 23, 2012

@author: E. LEGROS
@contact: emeline.legros@ibcp.fr
@license: GPLv3
'''
import os
from ConfigParser import Error as ConfigParserError
import logging
_log = logging.getLogger(__name__)

from mongokit import Document, ObjectId, IS
from mf.annotation import mf_decorator
from mf.views import MF_READ, MF_EDIT

from .connection import connection
from .config import Config
from .data import AbstractData
from .objectmanager import ObjectManager


@mf_decorator
@connection.register
class Project(Document):
    """
    Project is a class that stores all information about a project
    (owner username, inputs, outputs, job id).
    It's initialized by two parameters: the name of the owner of
    the project and the project name itself.
    """

    __collection__ = 'projects'
    __database__ = Config.config().get('app:main', 'db_name')

    structure = {'name': basestring,
                 'description': basestring,
                 'owner': ObjectId,
                 'users': [{'user': ObjectId, 'role': IS(u'manager',
                                                         u'contributor',
                                                         u'watcher')}],
                 'notebook': basestring,
                 'public': bool,
                 '_dir': basestring
                }

    required_fields = ['name', 'owner']

    default_values = {'_dir': None}

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
        add_user is a method defined to attach a new user
        and its role into the project.
        :param user: user to be associated to the project.
        :type user: :class:`User` object.
        :param role: user's role in the project.
        :type role: string.
        """
        self['users'].append({'user': user['_id'], 'role': role})

    @property
    def dir(self):
        """
        :return: the project directory
        :rtype: string
        """
        try:
            pid_file_path = Config.config().get("DEFAULT","projects_store")
        except ConfigParserError:
            _log.warning("cannot compute a project directory path from the config file",
                      exc_info=True)
            return None 
        return os.path.join(pid_file_path, 'projects', str(self['_id']))


    @property
    def id(self):
        """
        :return: the unique identifier of this project
        :rtype:
        """
        return self['_id']

    @staticmethod
    def my_project_acl_filter(control, request, authenticated_userid=None):
        # find the user corresponding to the provided email
        user = connection.User.find_one({'email': authenticated_userid})
        # id is set if user exists, otherwise set to None so that the filter
        # works even for unauthenticated users.
        user_id = user['_id'] if user else None
        # admin_mode tells wether the admin user
        # is in admin mode and should access everything
        admin_mode = hasattr(request, 'session') \
                     and 'adminmode' in request.session
        if user and user.get('admin') and admin_mode:
            # admin_mode = provide everything
            project_filter = {}
        elif control == MF_READ:
            # read: elements for projects where the user is active or where he
            if user is None:
                project_filter = {'public': True}
            else:
                project_filter = {"$or": [{"users": {"$elemMatch":
                                  {'user': user_id}}}, {'public':True}]}
        elif control == MF_EDIT:
            # User must be one of project contributors or managers
            if user is None:
                project_filter = None
            else:
                project_filter = {"users": {"$elemMatch": {'user': user_id,
                                  "$or": [{'role': 'contributor'},
                                          {'role': 'manager'}]}}}
        return project_filter

    def my(self, control, request, authenticated_userid=None):
        return self.my_project_acl_filter(control,
                                          request, authenticated_userid)


class ProjectDocument(Document):
    """
    ProjectDocument is an abstract class which defines the ACLs of
    project-contained elements. The ACLs of such documents are completely
    defined by the users of the containing project
    """

    def my(self, control, request, authenticated_userid=None):
        project_filter = Project.my_project_acl_filter(control, request,
                                                       authenticated_userid)
        # return directly project filter if it allows everything or nothing
        if project_filter == {} or project_filter is None:
            return project_filter
        # otherwise select the ids of the allowed projects
        else:
            project_ids_curs = connection.Project.find(project_filter,
                                                       {'_id': 1})
            project_ids = []
            for project_id in project_ids_curs:
                project_ids.append(project_id['_id'])
            return {"project": {"$in": project_ids}}


@mf_decorator
@connection.register
class ProjectData(ProjectDocument):
    """
    ProjectData describes a data linked to a project. It is referenced by jobs
    and user data manager. A ProjectData can be persistent or not.
    Data contains an AbstractData structure defining the data available.
    """

    __collection__ = 'projects_data'
    __database__ = Config.config().get('app:main', 'db_name')

    structure = {'name': basestring,
                 'description': basestring,
                 'tags': [basestring],
                 'project': ObjectId,
                 'data': AbstractData,
                 # see ObjectManager. Only READY data can be used
                 'status': int,
                 # set to True to avoid automatic deletion
                 # by cleanup tasks
                 'persistent': bool,
                 # path to the container directory for the data
                 # if it is not stored in the datamanager pairtree
                 'path': basestring,
                 # set to True to override project visibility
                 'public': bool
                 #TODO: add data provenance information
                }

    default_values = {'persistent': False, 'public': False}

    @property
    def default_value(self):
        """
        return default_value, delegated to data property
        """
        return self['data'].default_value

    def expr_value(self):
        """
        return expr_value(), delegated to data property
        """
        return self['data'].expr_value()

    def get_file_path(self):
        '''Get root path for files of the dataset'''
        if self['path']:
            return self['path']
        return ObjectManager.get_file_path(str(self['_id']))

    def schema(self, schema=None):
        '''Update schema if parameter is not None, return schema'''
        if schema is not None:
            self['data'] = schema
            self.save()
        return self['data']

    def status(self, status=None):
        '''Update status if parameter is not None, return status'''
        if status is not None:
            self['status'] = status
            self.save()
        return self['status']

    def save_with_history(self, files=None, msg=None):
        '''
        Save object and update git repo if available

        :param files: List of relative path of new or updated files in dataset
        :type files: list
        :param msg: optional msg for the update
        :type msg: str
        '''
        if files is not None and files and ObjectManager.use_repo:
            index = ObjectManager.get_repository_index(str(self['_id']))
            index.add(files)
            if msg is None:
                msg = "Update data"
            index.commit(msg)
        self.save()
