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
from .type import Type, FormattedType
from .myaml import myaml
from .data import new_data

@myaml.register
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

    @property
    def preconds(self):
        """
        returns the list of preconds, starting from
        the topmost ancestor and downwards
        """
        preconds = []
        if hasattr(self,'ancestors'):
            for ancestor in reversed(self.ancestors):
                if ancestor['precond'] is not None:
                    preconds.append(ancestor['precond'])
        if self['precond'] is not None:
            preconds.append(self['precond'])
        return preconds
    
    @property
    def name(self):
        return self['name']


@myaml.register
@connection.register
class Parameter(Para):
    """
    a service parameter
    """
    structure = {
                'main': bool,
                'hidden': bool,
                'simple': bool,
                'type': Type,
                'ctrls': None
                }

    default_values = {
                     'main': False,
                     'hidden': False,
                     'simple': False,
                     }

    @property
    def default_value(self):
        """
        Return the default value corresponding to a parameter
        :return: the value corresponding to the parameter name
                 or None
        """
        #FIXME default value should not be systematically a
        #      ValueData see task #62 in redmine
        if 'type' in self and self['type'] is not None \
            and 'default' in self['type']:
            data = new_data(self['type'])
            data['value'] = self['type']['default']            
            return data
        else:
            return None

    def has_ctrls(self):
        return True if self['ctrls'] is not None else False

    @property
    def ctrls(self):
        """
        :return: the ctrls
        """
        return self['ctrls']
    
    @property
    def type(self):
        """
        :return: the type
        :rtype: :class:`mobyle.comon.type.Type` object
        """
        return self['type']


@myaml.register
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

@myaml.register
@connection.register
class InputParameter(Parameter):
    """
    input parameter
    """
    structure = {
                'mandatory': bool
                }

    default_values = {
                     'mandatory': False,
                     }

    @property
    def mandatory(self):
        return self['mandatory'] or False

    
@myaml.register
@connection.register
class OutputParameter(Parameter):
    """
    output parameter
    """
    pass

@myaml.register
@connection.register
class ProgramParameter(Parameter):
    """
    parameter for a program
    """
    structure = {
                'argpos': int,
                'format': basestring,
                'paramfile': basestring
                }
    @property
    def argpos(self):
        """
        returns the argpos of the parameter, exploring the ancestor
        paragraphs if necessary
        """
        argpos = None
        if hasattr(self, 'command') and self['command']:
            argpos = 0
        elif self['argpos'] is not None:
            argpos = self['argpos']
        elif hasattr(self, 'ancestors'):
            for ancestor in self.ancestors:
                if 'argpos' in ancestor and ancestor['argpos'] is not None:
                    argpos = ancestor['argpos']
        return argpos if argpos is not None else 1
    
    def has_format(self):
        """
        return existence of the format property
        """
        return True if self['format'] is not None else False

    @property
    def format(self):
        """
        return the format value if it is defined
        """
        return self['format']

    def has_paramfile(self):
        """
        return existence of the paramfile property
        """
        return True if self['paramfile'] is not None else False

    @property
    def paramfile(self):
        """
        return the paramfile value if it is defined
        """
        return self['paramfile']
    
    


@myaml.register
@connection.register
class OutputProgramParameter(OutputParameter, ProgramParameter):
    """
    output parameter for a program
    """
    structure = {
                'filenames': basestring,
                # output type:
                # stdout: standard output
                # stderr: standard error
                # file: a specific file
                'output_type': IS(u'stdout',
                                  u'stderr',
                                  u'file'
                                 ),
                # progress: a progress report file
                'progress':bool
                }

    default_values = {'output_type': u'file'}

    @property
    def filenames(self):
        """
        return the filenames value if it defined
        """
        return self['filenames']

    @property
    def output_type(self):
        return self['output_type']


@myaml.register
@connection.register
class InputProgramParameter(InputParameter, ProgramParameter):
    """
    input parameter for a program
    """
    structure = {
                'command': bool
                }
    
    @property
    def command(self):
        """
        :return: True if parameter is command, False otherwise
        :rtype: boolean
        """
        return self['command'] or False


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


@myaml.register
@connection.register
class InputParagraph(Paragraph):
    """
    inputs container paragraph
    """
    structure = {}
    validators = {
                  'children': inputs_validator
                 }

@myaml.register
@connection.register
class InputProgramParagraph(InputParagraph):
    """
    a program inputs paragraph
    """
    structure = {
                'argpos': int
                }

@myaml.register
@connection.register
class OutputParagraph(Paragraph):
    """
    outputs container paragraph
    """
    structure = {}
    validators = {
                  'children': outputs_validator
                 }

@myaml.register
@connection.register
class OutputProgramParagraph(OutputParagraph):
    """
    a program outputs paragraph
    """
    structure = {
                'argpos': int
                }

@myaml.register
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
        if hasattr(self, 'collection') and (self['public_name'] is not None):
            if (self.collection.find({'public_name': self['public_name'],
                'version': self.get('version',None),
                '_id': {'$ne': self.get('_id', None)}}).count() > 0):
                raise ValidationError('Public name / version already used.')
        super(Software, self).validate(*args, **kwargs)

    @property
    def name(self):
        return self['name'] or ('anonymous_%s' % str(id(self)))

@myaml.register
@mf_decorator
@connection.register
class Package(Software):
    """
    a package is a group of services.
    """
    __collection__ = 'packages'


@myaml.register
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

    def __init__(self, doc=None, gen_skel=True, collection=None, 
                 lang='en', fallback_lang='en', schema_2_restore=None):
        """
        Service constructor, automatically calls the init_ancestors()
        method to link parameters and paragraphs to their ancestors 
        """
        super(Service, self).__init__(
          doc=doc, gen_skel=gen_skel, collection=collection, lang=lang, 
          fallback_lang=lang, schema_2_restore=schema_2_restore
        )
        self.init_ancestors()

    def init_ancestors(self):
        if self['inputs']:
            self['inputs']._init_ancestors()
        if self['outputs']:
            self['outputs']._init_ancestors()


    def inputs_list(self):
        """ 
        return the list of input parameters
        """
        if self['inputs'] is not None:
            return self['inputs'].parameters_list()
        else:
            return []

    def outputs_list(self):
        """ 
        return the list of output parameters
        """
        if self['outputs'] is not None:
            return self['outputs'].parameters_list()
        else:
            return []

    def parameters_list(self):
        return self.inputs_list() + self.outputs_list()

@myaml.register
@mf_decorator
@connection.register
class Program(Service):
    """
    a program is a command line tool
    """
    structure = {
                  'command': basestring,
                  'env': dict,
                  'cpu': int, # how many CPUs required to run the program 
                  'mem': int, # how much RAM required to run the program
                  'network': bool, # specify if the program requires a network access to run
                  'containers': [{'type': basestring,
                                  'id': basestring,
                                  'url': basestring}]
                }

    default_values = {'network': False}

    @property
    def command(self):
        return self['command']

    def parameters_list_by_argpos(self):
        """ 
        return the list of all parameters 
        ordered by argpos, in ascending order
        """
        return sorted(self.parameters_list(), 
            key=lambda x: x.argpos)

    @property
    def env(self):
        """
        return the environment variables as a dictionary
        """
        return self['env'] or {} 

    def outputs_list(self):
        """ 
        return the list of output parameters
        """
        outputs = super(Program, self).outputs_list()
        stdout = [parameter for parameter in outputs if parameter.output_type==u'stdout']
        stderr = [parameter for parameter in outputs if parameter.output_type==u'stderr']
        if len(stdout)==0:
            so = OutputProgramParameter()
            so['name'] = 'stdout'
            so['output_type'] = u'stdout'
            so_type = FormattedType()
            so_type['format_terms'] = ['EDAM_format:1964']
            so_type['data_terms'] = ['EDAM_data:2048']
            so['type'] = so_type
            so['filenames'] = "'" + self.name + ".out'"
            outputs.append(so)
        if len(stderr)==0:
            se = OutputProgramParameter()
            se['name'] = 'stderr'
            se['output_type'] = u'stderr'
            se_type = FormattedType()
            se_type['format_terms'] = ['EDAM_format:1964']
            se_type['data_terms'] = ['EDAM_data:2048']
            se['type'] = se_type
            se['filenames'] = "'" + self.name + ".err'"
            outputs.append(se)
        return outputs


@myaml.register
@mf_decorator
@connection.register
class Workflow(Service):
    """
    a workflow is a composite service running
    multiple other workflows
    """
    structure = {
                }


@myaml.register
@mf_decorator
@connection.register
class Widget(Service):
    """
    a widget is an interactive web component dedicated to the
    visualisation/edition of data multiple other workflows
    """
    structure = {
                }
