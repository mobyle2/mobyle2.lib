# -*- coding: utf-8 -*-
"""
Created on Jan 22, 2013

@author: Hervé Ménager
@contact: hmenager@pasteur.fr
@organization: Institut Pasteur
@license: GPLv3
"""
import abc
from abc import ABCMeta
from abc import abstractmethod
from bson.dbref import DBRef
from mongokit import Document, SchemaDocument, CustomType, OR

from mobyle.common import session
from mobyle.common.config import Config

import mf.annotation
from mf.annotation import *

class Parameter(SchemaDocument):
    """
    a service parameter
    """
    structure = {
                 'name': basestring
                }

    def __setitem__(self, key, value):
        # optional processing here
        super(Parameter, self).__setitem__(key, value)

    structure = {
                 'name': basestring
                }

    def to_bson(self, value):
        """convert type to a mongodb type"""
        return structure

    def to_python(self, value):
        """convert type to a python object"""
        return structure

class Paragraph(SchemaDocument):
    structure = {
                 'name': basestring,
		 #'parameters': OR(Parameter, Paragraph)
                }

@mf_decorator
class Software(Document):
    """
    top-level abstract element for different services and packages
    describes the common properties of these levels.     
    """

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
                  # inputs
                  'inputs': [Parameter],
                  # output
                  #'outputs': [OR(Parameter, Paragraph)]
                }

    default_values = {}

    required_fields = [ 'name' ]

@mf_decorator
class Package(Software):
    """
    a package is a group of services.
    """
    __collection__ = 'packages'
    pass

@mf_decorator
class Service(Software):
    """
    a service is an executable piece of software
    """
    __collection__ = 'services'
    structure = {
                  # package reference
                  'package' : Package
                }

@mf_decorator
class Program(Service):
    """
    a program is a command line tool
    """
    structure = {}


