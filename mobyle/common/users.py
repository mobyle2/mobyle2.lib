# -*- coding: utf-8 -*-

from mongokit import Document, ObjectId
import bcrypt
from mf.annotation import mf_decorator, MF_READ, MF_EDIT
import uuid

from .connection import connection
from .config import Config

@mf_decorator
@connection.register
class User(Document):
    """
    Base user of Mobyle. User can be a registered user or
    authenticated via external endpoints.

    """

    __collection__ = 'users'
    __database__ = Config.config().get('app:main','db_name')

    structure = { 'first_name' : basestring,
                 'last_name' : basestring,
                 'email' : basestring,
                 'hashed_password' : basestring,
                 'type' : basestring,
                 'admin': bool,
                 'groups' : [ basestring ],
                 'apikey' : basestring,
                 'home_dir': basestring,
                 'default_project': ObjectId,
                 'notifications': {
                                    'mail_project': bool,
                                    'mail_job': bool,
                                    'mail_data': bool
                                  }
                 }

    default_values = { 'hashed_password' : '',
                        'admin': False,
                        'apikey' : uuid.uuid4().hex ,
                        'notifications.mail_project': False,
                        'notifications.mail_job': False,
                        'notifications.mail_data': False
                    }
    
    required_fields = [ 'email' ]    
    
    def set_password(self, clear_password):
        """
        Sets the password of the user

        :param clear_password: Password, not encrypted
        :type clear_password: str
        """
        self['hashed_password'] = bcrypt.hashpw(clear_password, bcrypt.gensalt())
    
    def check_password(self, password):
        """
        Get encrypted value of the input password for comparison

        :param password: input password of the user for registered users
        :type password: str
        :return: encrypted valueof the password
        """
        hashed = bcrypt.hashpw(password, self['hashed_password'])
        return hashed == self['hashed_password']

    def my(self,control,request,authenticated_userid):
        # Get user
        user = connection.User.find_one({'email': authenticated_userid})
        if user is None:
            project_filter = None
        else:
            # admin_mode tells wether the admin user is in admin mode and should access everything
            admin_mode = hasattr(request,'session') and 'adminmode' in request.session
            if user and user.get('admin') and admin_mode:
                # admin_mode = provide everything
                project_filter = {}
            else:
                project_filter = {'email' : authenticated_userid}
        return project_filter

