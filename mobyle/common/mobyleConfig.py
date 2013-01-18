# -*- coding: utf-8 -*-
'''
Created on Nov. 28, 2012

@author: Olivier Sallou
@contact: olivier.sallou@irisa.fr
@license: GPLv3
'''

import sys
import os

from mobyle.common import session

import logging
import logging.config

import json
from bson import json_util
import mf.annotation
from mf.annotation import *


from mobyleError import MobyleError

from datetime import datetime

from mongokit import Document, Connection

from mobyle.common.config import Config

@mf_decorator
class MobyleConfig(Document):
    """
    Config loads mobyle configuration from database.
    It contains configuration that can be updated by administrators
    """

    __collection__ = 'config'
    __database__ = Config.config().get('app:main','db_name')

    structure = { 'auth_mod' : basestring , 'mail' : { 'gateway' : basestring, 'user' : basestring, 'password' : basestring, 'origin' : basestring },
                  'url' : basestring, 'datadir' : basestring, 'rootdir' : basestring, 'options' :  { 'apikey' : bool }
    }

    default_values = {
        'options.apikey': False,
        'url': 'http://localhost',
        'datadir' : '/var/lib/mobyle',
        'rootdir' : '/usr/share/mobyle'
    }


    def to_json(self):
        """"
        Return JSON representation of the object

        :return: JSON representation of the config
        :rtype: str
        """
        return json.dumps(self, default=json_util.default)



session.register([MobyleConfig])
