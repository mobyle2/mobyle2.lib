# -*- coding: utf-8 -*-
'''
Created on Nov. 28, 2012

@author: Olivier Sallou
@contact: olivier.sallou@irisa.fr
@license: GPLv3
'''

import logging
import logging.config
import json
from bson import json_util
from mongokit import Document
from mf.annotation import mf_decorator

from .connection import connection
from .config import Config

@mf_decorator
@connection.register
class MobyleConfig(Document):
    """
    Config loads mobyle configuration from database.
    It contains configuration that can be updated by administrators
    """

    __collection__ = 'config'

    __database__ = Config.config().get('app:main','db_name')

    structure = { 'active' : bool,
                  'maintenance': bool,
                  #'auth_mod' : basestring ,
                  'mail' : { 'gateway' : basestring, # smtp gateway
                             'list' : basestring, # mailing list
                             'user' : basestring, # if auth required
                             'password' : basestring,
                             'origin' : basestring }, # From in the email
                  'url' : basestring,
                  #'datadir' : basestring,
                  #'rootdir' : basestring,
                  'options' :  { 'apikey' : bool },
                  'auth': { 'ldap' : {
                                'allow': bool,
                                'host': basestring,
                                'port': int,
                                'dn': basestring,
                                'filter': basestring
                            }
                    },
                  'data': {
                    'remote': {
                      'allowed_protocols': basestring
                    },
                    'local': {
                      'allowed_copy': bool
                    }
                  }
    }

    default_values = {
        'active': False,
        'maintenance': False,
        'options.apikey': False,
        'auth.ldap.allow': False,
        'auth.ldap.host': 'localhost',
        'auth.ldap.port': 389,
        'data.remote.allowed_protocols': 'http,ftp',
        'data.local.allowed_copy': False,
        'url': 'http://localhost'
        #'datadir' : '/var/lib/mobyle',
        #'rootdir' : '/usr/share/mobyle'
    }

    @classmethod
    def get_current(cls):
        """
        Return current active configuration

        :return: active MobyleConfig
        """
        return connection.MobyleConfig.find_one({'active': True})


    def to_json(self):
        """"
        Return JSON representation of the object

        :return: JSON representation of the config
        :rtype: str
        """
        return json.dumps(self, default=json_util.default)
