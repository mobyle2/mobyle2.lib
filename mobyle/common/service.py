# -*- coding: utf-8 -*-

import abc
from abc import ABCMeta
from abc import abstractmethod

from mongokit import Document

from mobyle.common import session
from mobyle.common.config import Config

import mf.annotation
from mf.annotation import *

@mf_decorator
class Service(Document):
    """
    
    """

    __collection__ = 'service'
    __database__ = Config.config().get('app:main','db_name')

    structure = { 'name' : basestring,
                  'version' : basestring,
                  'title' : basestring,
                  'description' : basestring,
                  'authors' : basestring,
                  'references' : [{'label':basestring,
                                   'doi':basestring,
                                   'url':basestring
                                 }],
                  'documentation_links' : [basestring],
                  'source_links' : [basestring],
                  'homepage_links' : [basestring],
                  'comment': basestring,
                  'classifications': [{'type':basestring,'classification':basestring}],
                }

    default_values = {}

    required_fields = [ 'name' ]


