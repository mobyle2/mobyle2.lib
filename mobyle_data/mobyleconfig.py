# -*- coding: utf-8 -*-
'''
Created on Nov. 28, 2012

@author: Olivier Sallou
@contact: olivier.sallou@irisa.fr
@license: GPLv3
'''



import sys
import os

from mobyle_data import session

import logging
import logging.config

import json


from mobyleError import MobyleError

from datetime import datetime

	
from ming.datastore import DataStore
from ming import Session
from ming import Document, Field, schema

class MobyleConfig(Document):
    """
    Config loads mobyle configuration from database.
    """


    class __mongometa__:
        session = session
        name = "config"

    _id = Field(schema.ObjectId)
    # Last-updated
    last_update = Field(datetime, if_missing=datetime.utcnow)
    # Allowed Authentication modes
    auth_mode = Field('auth_mode',[str])
    # Mail
    mail = Field(dict( gateway = str , user = str, password = str, from = str))
    # URL
    url = Field(str, if_missing="http://localhost")
    # Data dir
    data.dir = Field(str, if_missing="/var/lib/mobyle")
    # Various options
    options  = Field(dict( apikey = schema.Boolean ))


    def to_json(self):
    """"
    Return JSON representation of the object

    :return: JSON representation of the config
    :rtype: str
    """
    return json.dumps(self)


