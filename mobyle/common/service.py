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

class Para(SchemaDocument):
    """
    parent class for parameters and paragraphs
    """
    structure = {
                'name': basestring
                }

class Parameter(Para):
    """
    a service parameter
    """
    structure = {
                }

class Paragraph(Para):
    """
    a service paragraph
    """
    structure = {
                 'children': [Para]
                }

class InputParameter(Parameter):
   """
   input parameter
   """
   structure = {}

class OutputParameter(Parameter):
   """ 
   output parameter
   """
   structure = {}

def inputs_validator(paras_list):
   """
   checks that all parameters and paragraphs in the list are inputs
   """
   for para in paras_list:
       if not(isinstance(para,InputParameter) or isinstance(para, InputParagraph)):
           raise ValueError('%%s should contain only input parameters and paragraphs, but %s is not an input' % para['name'])
   return True

def outputs_validator(paras_list):
   """
   checks that all parameters and paragraphs in the list are outputs
   """
   for para in paras_list:
       if not(isinstance(para,OutputParameter) or isinstance(para, OutputParagraph)):
           raise ValueError('%%s should contain only output parameters and paragraphs, but %s is not an output' % para['name'])
   return True

class InputParagraph(Paragraph):
   """
   inputs container paragraph
   """
   structure = {} 
   validators = {
                'children':inputs_validator
                }

class OutputParagraph(Paragraph):
   """
   outputs container paragraph
   """
   structure = {}
   validators = {
                'children':outputs_validator
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
                  'inputs': InputParagraph,
                  # outputs
                  'outputs': OutputParagraph
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


