# -*- coding: utf-8 -*-

from mobyle.common import session
from mobyle.common.config import Config

from mongokit import Document

import bcrypt


class User(Document):

    __collection__ = 'users'
    __database__ = Config.config().get('app:main','db_name')

    structure = { 'first_name' : basestring, 'last_name' : basestring, 'email' : basestring, 'hashed_password' : basestring, 'type' : basestring, 'admin': bool, 'groups' : [ basestring ] }

    default_values = { 'hashed_password' : '', 'admin': False }

    required_fields = [ 'email' ]    
    
    def set_password(self, clear_password):
        self['hashed_password'] = bcrypt.hashpw(clear_password, bcrypt.gensalt())
    
    def check_password(self, password):
        hashed = bcrypt.hashpw(password, self['hashed_password'])
        return hashed == self['hashed_password']
    
    
session.register([User])
