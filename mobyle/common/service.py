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
                  # version of the software
                  'version' : basestring,
                  # title
                  'title' : basestring,
                  # description
                  'description' : basestring,
                  # authors of the software
                  'authors' : basestring,
                  # bibliographic references to be cited when using
                  # this software
                  'references' : [{
                                   # citation text
                                   'label':basestring,
                                   # citation DOI
                                   'doi':basestring,
                                   # citation URL
                                   'url':basestring
                                 }],
                  # software documentation links
                  'documentation_links' : [basestring],
                  # software sources links
                  'source_links' : [basestring],
                  # software homepage links
                  'homepage_links' : [basestring],
                  # miscelaneous comments
                  'comment': basestring,
                  # software classifications
                  'classifications': [{
                                       # type of classification
                                       'type':basestring,
                                       # classification value
                                       'classification':basestring
                                     }],
                }

    default_values = {}

    required_fields = [ 'name' ]


