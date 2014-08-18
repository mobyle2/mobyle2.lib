# -*- coding: utf-8 -*-
"""
Created on Jan 22, 2013

@author: Hervé Ménager
@contact: hmenager@pasteur.fr
@organization: Institut Pasteur
@license: GPLv3
"""
from mongokit import ObjectId, SchemaDocument, IS, ValidationError
from mf.annotation import mf_decorator

from .connection import connection
from .config import Config
from .project import ProjectDocument
from .type import Type


@connection.register
class Para(SchemaDocument):
    """
    parent class for parameters and paragraphs
    """
    structure = {
                'name': basestring,
                'prompt': basestring,
                #TODO: add a schema for preconds
                'precond': None,
                'comment': basestring
                }

@connection.register
class Parameter(Para):
    """
    a service parameter
    """
    structure = {
                'main': bool,
                'hidden': bool,
                'simple': bool,
                'type': Type
                }

    default_values = {
                     'main': False,
                     'hidden': False,
                     'simple': False,
                     }

@connection.register
class Paragraph(Para):
    """
    a service paragraph
    """
    structure = {
                'children': [Para]
                }

    def _init_ancestors(self, ancestors=[]):
        """
        Store the ordered list of ancestor paragraphs in each
        "Para" object, as the "ancestors" property.
        This is especially usefull in Command line generation.
        It should be automatically called by the Service constructor
        when a service is fetched from the DB.
        """
        for child_para in self['children']:
            if isinstance(child_para, Parameter):
                child_para.ancestors = [self]+ancestors
            else:
                child_para._init_ancestors([self]+ancestors)

    def parameters_list(self):
        """
        Return a flattened list of all the contained Parameters
        """
        paras_list = []
        for child_para in self['children']:
            if isinstance(child_para, Parameter):
                paras_list.append(child_para)
            else:
                paras_list.extend(child_para.parameters_list())
        return paras_list


@connection.register
class InputProgramParagraph(Paragraph):
    """
    a program input paragraph
    """
    structure = {
                'argpos': int
                }


@connection.register
class InputParameter(Parameter):
    """
    input parameter
    """
    structure = {
                'mandatory': bool,
                'ctrl': None
                }

    default_values = {
                     'mandatory': False,
                     }


@connection.register
class OutputParameter(Parameter):
    """
    output parameter
    """
    structure = {
                # output type:
                # stdout: standard output
                # stderr: standard error
                # file: a specific file
                # progress: a progress report file
                'output_type': IS(u'stdout',
                                  u'stderr',
                                  u'file',
                                  u'progress')
                }
    default_values = {'output_type': u'file'}


@connection.register
class OutputProgramParameter(OutputParameter):
    """
    output parameter for a program
    """
    structure = {
                'filenames': basestring
                }


@connection.register
class InputProgramParameter(InputParameter):
    """
    input parameter for a program
    """
    structure = {
                'command': bool,
                'argpos': int,
                'format': basestring,
                'paramfile': basestring
                }

    default_values = {
                     'command': False,
                     }

    @property
    def argpos(self):
        """
        returns the argpos of the parameter, exploring the ancestor
        paragraphs if necessary
        """
        if self['argpos'] is not None:
            return self['argpos']
        elif hasattr(self,'ancestors'):
            for ancestor in self.ancestors:
                if ancestor['argpos'] is not None:
                    return ancestor['argpos']
        else:
            return 1

def inputs_validator(paras_list):
    """
    checks that all parameters and paragraphs in the list are inputs
    """
    for para in paras_list:
        if not(isinstance(para, InputParameter) or
         isinstance(para, InputParagraph)):
            raise ValueError(
             '%%s should contain only input parameters and paragraphs, '
             'but %s is not an input' % para['name'])
    return True


def outputs_validator(paras_list):
    """
    checks that all parameters and paragraphs in the list are outputs
    """
    for para in paras_list:
        if not(isinstance(para, OutputParameter) or
         isinstance(para, OutputParagraph)):
            raise ValueError(
             '%%s should contain only output parameters and paragraphs, '
             'but %s is not an output' % para['name'])
    return True


@connection.register
class InputParagraph(Paragraph):
    """
    inputs container paragraph
    """
    structure = {}
    validators = {
                  'children': inputs_validator
                 }


@connection.register
class OutputParagraph(Paragraph):
    """
    outputs container paragraph
    """
    structure = {}
    validators = {
                  'children': outputs_validator
                 }


@mf_decorator
class Software(ProjectDocument):
    """
    top-level abstract element for different services and packages
    describes the common properties of these levels.
    """
    __database__ = Config.config().get('app:main', 'db_name')

    keys_order = ['_type', 'name', 'version', 'title', 'description',
                  'authors']

    structure = {
                  '_type': unicode,
                  # software name
                  'name': basestring,
                  # version of the software
                  'version': basestring,
                  # public name, that allows permalinks
                  'public_name': basestring,
                  # title
                  'title': basestring,
                  # description
                  'description': basestring,
                  # authors of the software
                  'authors': basestring,
                  # bibliographic references to be cited when using
                  # this software
                  'references': [{
                                   # citation text
                                   'label':basestring,
                                   # citation DOI
                                   'doi':basestring,
                                   # citation URL
                                   'url':basestring
                                 }],
                  # software documentation links
                  'documentation_links': [basestring],
                  # software sources links
                  'source_links': [basestring],
                  # software homepage links
                  'homepage_links': [basestring],
                  # miscelaneous comments
                  'comment': basestring,
                  # operations
                  'operations': [basestring],
                  'topics': [basestring],
                  'project': ObjectId
                }

    default_values = {}

    required_fields = ['name']

    def validate(self, *args, **kwargs):
        """
        validate the public name of the service if it has one.

        :raise: :class:`ValidationError` if the public name is already used.
        """
        if (self['public_name'] is not None):
            if (self.collection.find({'public_name': self['public_name'],
                'version': self['version'],
                '_id': {'$ne': self.get('_id', None)}}).count() > 0):
                raise ValidationError('Public name / version already used.')
        super(Software, self).validate(*args, **kwargs)


@mf_decorator
@connection.register
class Package(Software):
    """
    a package is a group of services.
    """
    __collection__ = 'packages'


@mf_decorator
@connection.register
class Service(Software):
    """
    a service is an executable piece of software
    """
    __collection__ = 'services'

    keys_order = Software.keys_order + \
                 ['package', 'inputs', 'outputs']

    structure = {
                  # package reference
                  'package': Package,
                  # inputs
                  'inputs': InputParagraph,
                  # outputs
                  'outputs': OutputParagraph,
                  # project which the service belongs to
                  'project': ObjectId
                }

    #FIXME __init__ override does not work (must be a mongokit gotcha)
    #      for now init_ancestors() needs to be called manually.
    #def __init__(self, doc=None, gen_skel=True, gen_auth_types=False, collection=None, lang='en', fallback_lang='en'):
    #    super(Service, self).__init__(
    #      doc=doc, gen_skel=gen_skel, lang=lang,
    #      fallback_lang=fallback_lang
    #    )

    def init_ancestors(self):
        self['inputs']._init_ancestors()
        self['outputs']._init_ancestors()


    def inputs_list(self):
        """ 
        return the list of all parameters
        """
        if self['inputs'] is not None:
            return self['inputs'].parameters_list()
        else:
            return []

@mf_decorator
@connection.register
class Program(Service):
    """
    a program is a command line tool
    """
    structure = {
                  'command': {
                              'path': basestring,
                              'value': basestring
                             },
                  'env': [{
                           'name': basestring,
                           'value': basestring
                          }]
                }

    def inputs_list_by_argpos(self):
        """ 
        return the list of all parameters ordered by argpos
        """
        return []

@mf_decorator
@connection.register
class Workflow(Service):
    """
    a workflow is a composite service running
    multiple other workflows
    """
    structure = {
                }


@mf_decorator
@connection.register
class Widget(Service):
    """
    a widget is an interactive web component dedicated to the
    visualisation/edition of data multiple other workflows
    """
    structure = {
                }
