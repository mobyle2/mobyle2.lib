# -*- coding: utf-8 -*-

import mobyle_data

from ming.datastore import DataStore
from ming import Session
from ming import Document, Field, schema


class User(Document):
    class __mongometa__:
        session = mobyle_data.session
        name = "user"
    
    _id = Field(schema.ObjectId)
    name = Field(str)
    
    

    