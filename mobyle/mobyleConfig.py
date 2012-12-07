# -*- coding: utf-8 -*-
'''
Created on Nov. 28, 2012

@author: Olivier Sallou
@contact: olivier.sallou@irisa.fr
@license: GPLv3
'''

import sys
import os

from mobyle import session

import logging
import logging.config

import json
from bson import json_util


from mobyleError import MobyleError

from datetime import datetime

from ming.datastore import DataStore
from ming import Session
from ming import Document, Field, schema

class MobyleConfig(Document):
    """
    Config loads mobyle configuration from database.
    It contains configuration that can be updated by administrators
    """

    class __mongometa__:
        session = session
        name = "config"

    _id = Field(schema.ObjectId)
    # Allowed Authentication modes
    auth_mode = Field('auth_mode',[str])
    # Mail
    mail = Field('mail', dict(gateway=str, user=str, password=str, origin=str))
    # URL
    url = Field('url', str, if_missing="http://localhost")
    # Data dir
    datadir = Field('datadir', str, if_missing="/var/lib/mobyle")
    # Mobyle root dir
    rootdir = Field('rootdir', str, if_missing="/usr/share/mobyle")
    # Various options
    options  = Field('options', dict( apikey = bool ))

    def to_json(self):
        """"
        Return JSON representation of the object

        :return: JSON representation of the config
        :rtype: str
        """
        return json.dumps(self, default=json_util.default)


