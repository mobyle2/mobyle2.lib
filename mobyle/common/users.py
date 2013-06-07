# -*- coding: utf-8 -*-

from mongokit import Document
import bcrypt
from mf.annotation import mf_decorator
from mf.views import MF_LIST, MF_MANAGE
import uuid

from .connection import connection
from .config import Config

@mf_decorator
@connection.register
class User(Document):

    __collection__ = 'users'
    __database__ = Config.config().get('app:main','db_name')

    structure = { 'first_name' : basestring,
                 'last_name' : basestring,
                 'email' : basestring,
                 'hashed_password' : basestring,
                 'type' : basestring,
                 'admin': bool,
                 'groups' : [ basestring ],
                 'apikey' : basestring }

    default_values = { 'hashed_password' : '', 'admin': False, 'apikey' : uuid.uuid4().hex }
    
    required_fields = [ 'email' ]    
    
    def set_password(self, clear_password):
        self['hashed_password'] = bcrypt.hashpw(clear_password, bcrypt.gensalt())
    
    def check_password(self, password):
        hashed = bcrypt.hashpw(password, self['hashed_password'])
        return hashed == self['hashed_password']

    def my(self,control,request,authenticated_userid):
        # Get user
        user  = connection.User.find_one({'email': authenticated_userid})
        if user and user['admin']:
            return {}
        if control == MF_LIST:
                return None
        if control == MF_MANAGE:
            return {'email' : authenticated_userid}



    
if __name__ == '__main__':
    print connection.User
