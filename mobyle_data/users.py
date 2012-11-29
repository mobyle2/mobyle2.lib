# -*- coding: utf-8 -*-

from mobyle_data import session

from ming.datastore import DataStore
from ming import Session
from ming import Document, Field, schema

import bcrypt


class User(Document):
    class __mongometa__:
        session = session
        name = "user"
    
    _id = Field(schema.ObjectId)
    first_name = Field(str, if_missing='')
    last_name = Field(str, if_missing='')
    email = Field(str, if_missing='')
    hashed_password = Field(str, if_missing='')
    
    def set_password(self, clear_password):
        self.hashed_password = bcrypt.hashpw(clear_password, bcrypt.gensalt())
    
    def check_password(self, password):
        hashed = bcrypt.hashpw(password, self.hashed_password)
        return hashed == self.hashed_password
    
    

    