# -*- coding: utf-8 -*-
"""
Created on Feb 08, 2013

@author: Hervé Ménager
@contact: hmenager@pasteur.fr
@organization: Institut Pasteur
@license: GPLv3
"""
import os
import ast
import xml.etree.cElementTree as ET
import xml.etree.ElementInclude as EI
from xml2json import elem_to_internal, internal_to_elem
import logging
import argparse
from importlib import import_module

from mobyle.common.config import Config

# pylint: disable=C0103
#        Invalid name "logger" for type constant
logger = logging.getLogger('mobyle.service_migration')


class JSONProxy(object):
    """
    JSONProxy is a wrapper for the XML elements represented as
    JSON structures generated by xml2json.py
    that facilitates the access to the different properties given
    the specific needs of this script
    """

    def __init__(self, json_dict):
        self.json_dict = json_dict

    def tag(self):
        """
        Get the name of the element corresponding to the current structure
        :returns: the name of the element
        :rtype: string
        """
        return self.json_dict.get('#tag')

    def get(self, key, default=None):
        """
        Get a child element of the current one wrapped in a JSONProxy instance
        :param key: name of the child element to be returned
        :type key: string
        :param default: default value to be returned
        :type default: anything
        :returns: the child element requested
        :rtype: JSONProxy
        """
        try:
            el = [n for n in self.json_dict['#children']
                  if isinstance(n, dict) and n['#tag'] == key]
            return JSONProxy(el[0])
        except IndexError:
            return default

    def att(self, key, default=None):
        """
        Get the value of an attribute of the current element
        :param key: name of the attribute value to be returned
        :type key: string
        :param default: default value to be returned
        :type default: anything
        :returns: the attribute value
        :rtype: string
        """
        try:
            return self.json_dict['@%s' % key]
        except KeyError:
            return default

    def text(self, key=None, default=None):
        """
        Get the text value of the current element or one of its
        children selected by element name
        :param key: name of the child element to be optionally
                    selected
        :type key: string
        :param default: default value to be returned
        :type default: anything
        :returns: the text value
        :rtype: string
        """
        try:
            if key is not None:
                text = [n['#children'][0] for n in self.json_dict['#children']
                        if isinstance(n, dict) and n['#tag'] == key]
                return text[0]
            else:
                return self.json_dict['#children'][0]
        except IndexError:
            return default

    def list(self, key=None):
        """
        Get the child elements of the current one wrapped in JSONProxy
        instances, optionally selected by tag name.
        :param key: name of the child elements to be optionally
                    selected
        :type key: string
        :returns: the child elements selected
        :rtype: list
        """
        if key is not None:
            el = [n for n in self.json_dict['#children']
                  if isinstance(n, dict) and n['#tag'] == key]
            return [JSONProxy(item) for item in el]
        else:
            return [JSONProxy(item)
                    for item in self.json_dict['#children']]

    def has(self, key):
        """
        Tests if the current element has at least one child element
        whose name is "key"
        :param key: name of the child element(s) to be optionally
                    detected
        :type key: string
        :returns: yes if at least one exists
        :rtype: bool
        """
        return len([n for n in self.json_dict['#children']
                    if isinstance(n, dict) and n['#tag'] == key]) > 0

    def text_or_html(self):
        """
        Returns the children of the current element as
        1) concatenated text strings or
        2) concatenated XHTML equivalent of the child elements
        :returns: the string value of the current element
        :rtype: string
        """
        s = ''
        for d in self.json_dict['#children']:
            if isinstance(d, basestring):
                s += d
            elif d['#tag'] == 'text' and len(d['#children']) == 1:
                s += d['#children'][0]
            else:
                s += ET.tostring(internal_to_elem(d))
        return s


class TypeConversionMap(object):

    def __init__(self):
        self.mapping = {}
        mapping_file = open(os.path.join(os.path.dirname(__file__),
                            'types_mapping.txt'), 'r')
        self.missing = set()
        for line in iter(mapping_file):
            if not(line.startswith('#')):
                key, value = line.strip().split('/')
                self.mapping[key] = value
        mapping_file.close()

    def get_type(self, datatype_class, biotype):
        key = datatype_class
        if biotype is not None:
            key += '-%s' % str(biotype)
        value = self.mapping.get(key)
        if not(value):
            self.missing.add('%s/%s' % (datatype_class, biotype))
            logger.error(
                ("[not implemented] parameter class %s / biotype %s not " +
                "mapped (key %s)") % (datatype_class, biotype, key))
            return None
        mapped = value.split('-')
        if len(mapped) == 1:
            return {'_type': mapped[0]}
        elif len(mapped) == 2:
            return {'_type': mapped[0],
                    'data_terms': mapped[1]}
        else:
            return {'_type': mapped[0],
                    'data_terms': mapped[1],
                    'format_terms': mapped[2]}

types_map = TypeConversionMap()


class FormatConversionMap(object):

    def __init__(self):
        self.mapping = {}
        mapping_file = open(os.path.join(os.path.dirname(__file__),
                            'formats_mapping.txt'), 'r')
        self.missing = set()
        for line in iter(mapping_file):
            if not(line.startswith('#')):
                key, value = line.strip().split('/')
                self.mapping[key] = value
        mapping_file.close()

    def get_format(self, mobyle1_format):
        try:
            value = self.mapping.get(mobyle1_format)
            if not(value):
                self.missing.add(mobyle1_format)
                logger.error("[not implemented] format %s not found in mapping"
                             % (mobyle1_format))
            return value
        except:
            logger.error("error retrieving format %s in mapping" %
                         (mobyle1_format))
            return None

formats_map = FormatConversionMap()


class TopicConversionMap(object):

    def __init__(self):
        self.mapping = {}
        mapping_file = open(os.path.join(os.path.dirname(__file__),
                            'topic_mapping.txt'), 'r')
        self.missing = set()
        for line in iter(mapping_file):
            if not(line.startswith('#')):
                key, value = line.strip().split('/')
                self.mapping[key] = value.split(',')
        mapping_file.close()

    def get_topic(self, service_name):
        values = self.mapping.get(service_name)
        if not(values):
            self.missing.add(service_name)
            logger.error(
                "[not implemented] topic for service %s not mapped"
                % (service_name))
        return values

topics_map = TopicConversionMap()


class OperationConversionMap(object):

    def __init__(self):
        self.mapping = {}
        mapping_file = open(os.path.join(os.path.dirname(__file__),
                            'operation_mapping.txt'), 'r')
        self.missing = set()
        for line in iter(mapping_file):
            if not(line.startswith('#')):
                key, value = line.strip().split('/')
                self.mapping[key] = value.split(',')
        mapping_file.close()

    def get_operation(self, service_name):
        values = self.mapping.get(service_name)
        if not(values):
            self.missing.add(service_name)
            logger.error(
                "[not implemented] operation for service %s not mapped"
                % (service_name))
        return values

operations_map = OperationConversionMap()


class MobyleExprTranslator(object):
    class MyTransformer(ast.NodeTransformer):

        def visit_Expression(self, node):
            return ast.NodeVisitor.visit(self, node.body)

        def visit_Compare(self, node):
            left = ast.NodeVisitor.visit(self, node.left)
            comparators = ast.NodeVisitor.visit(self, node.comparators[0])
            if isinstance(node.ops[0], ast.Eq):
                return {left: comparators}
            else:
                ops = ast.NodeVisitor.visit(self, node.ops[0])
                return {left: {ops: comparators}}

        def visit_Num(self, node):
            return str(node.n)

        def visit_Name(self, node):
            return str(node.id)

        def visit_List(self, node):
            return [ast.NodeVisitor.visit(self, elt) for elt in node.elts]

        def visit_Tuple(self, node):
            return [ast.NodeVisitor.visit(self, elt) for elt in node.elts]

        def visit_Call(self, node):
            function_name = ast.NodeVisitor.visit(self, node.func)
            if function_name == 'bool':
                return ast.NodeVisitor.visit(self, node.args[0])
            elif function_name == 'int':
                return ast.NodeVisitor.visit(self, node.args[0])
            else:
                raise NotImplementedError(
                     "translation of node %s is not yet implemented" % node)

        def visit_In(self, node):
            return '#in'

        def visit_NotIn(self, node):
            return '#nin'

        def visit_And(self, node):
            return '#and'

        def visit_Or(self, node):
            return '#or'

        def visit_Not(self, node):
            return '#not'

        def visit_IsNot(self, node):
            return '#ne'

        def visit_NotEq(self, node):
            return '#ne'

        def visit_Is(self, node):
            return '#eq'

        def visit_Str(self, node):
            return node.s

        def visit_Gt(self, node):
            return '#gt'

        def visit_Lt(self, node):
            return '#lt'

        def visit_GtE(self, node):
            return '#gte'

        def visit_LtE(self, node):
            return '#lte'

        def visit_BoolOp(self, node):
            return {ast.NodeVisitor.visit(self, node.op):
                    [ast.NodeVisitor.visit(self, val) for val in node.values]}

        def visit_UnaryOp(self, node):
            return {ast.NodeVisitor.visit(self, node.op):
                    ast.NodeVisitor.visit(self, node.operand)}

        def generic_visit(self, node):
            raise NotImplementedError(
                 "translation of node %s is not yet implemented" % node)

    def translate(self, python_str):
        my_ast = ast.parse(python_str, mode="eval")
        try:
            expr = self.MyTransformer().visit(my_ast)
        except NotImplementedError, err:
            logger.error("Error translating expression '%s'" % python_str,
                exc_info=True)
            raise err
        return expr


def parse_software(d, s):
    """
    parse top-level elements of the software
    :param d: the dictionary containing the Mobyle1 "head" element
    :type struct: dict
    :param s: the software object to be filled
    :type struct: Software
    """
    s['name'] = d.text('name')
    s['version'] = d.text('version')
    s['title'] = d.get('doc').text('title')
    if d.get('doc').get('description'):
        s['description'] = d.get('doc').get('description').text_or_html()
    if d.get('doc').get('authors'):
        s['authors'] = d.get('doc').get('authors').text_or_html()
    for r in d.get('doc').list('reference'):
        refdic = {}
        refdic['label'] = r.text_or_html()
        refdic['doi'] = r.att('doi')
        refdic['url'] = r.att('url')
        s['references'].append(refdic)
    for link in d.get('doc').list('sourcelink'):
        s['source_links'].append(link.text())
    for link in d.get('doc').list('doclink'):
        s['documentation_links'].append(link.text())
    for link in d.get('doc').list('homepagelink'):
        s['homepage_links'].append(link.text())
    if d.get('doc').has('comment'):
        s['comment'] = d.get('doc').get('comment').text_or_html()
    for cat in d.list('category'):
        s['classifications'].append({'type': 'mobyle1',
                                     'classification': cat.text()})
    s['operations'] = operations_map.get_operation(s['name']) or []
    s['topics'] = topics_map.get_topic(s['name']) or []
    if d.get('package'):
        package_name = d.get('package').text('name')
        logger.info('software %s belongs to package %s, linking...' %
                   (s['name'], package_name))
        package = Package.fetch_one({'name': package_name})
        if package:
            s['package'] = package
        else:
            logger.warning('missing package %s in software %s' %
                          (s['name'], package_name))
    return s


def parse_para(p_dict, para, service_type):
    """
    parse Mobyle1 common "parameter" or "paragraph" element properties
    :param p_dict: the dictionary representing the Mobyle1 "parameter" element
    :type p_dict: dict
    :param para: the Parameter or Paragraph object
    :type para: Para
    :param service_type: 'program', 'workflow' or 'widget'
    :type service_type: string
    """
    para['name'] = p_dict.text('name')
    para['prompt'] = p_dict.text('prompt')
    if p_dict.has('comment'):
        para['comment'] = p_dict.get('comment').text_or_html()
    if p_dict.has('precond'):
        para['precond'] = {}
        for code in p_dict.get('precond').list('code'):
            if code.att('proglang') == 'python':
                para['precond'] = MobyleExprTranslator().translate(
                    code.text())


def parse_parameter(p_dict, service_type):
    """
    parse Mobyle1 "parameter" element
    :param p_dict: the dictionary representing the Mobyle1 "parameter" element
    :type p_dict: dict
    :param service_type: 'program', 'workflow' or 'widget'
    :type service_type: string
    :returns: the InputParameter or OutputParameter object
    :rtype: Parameter
    """
    logger.debug("processing parameter %s" % p_dict.text('name'))
    if p_dict.att('isout') or p_dict.att('isstdout'):
        if service_type == 'program':
            parameter = OutputProgramParameter()
        else:
            parameter = OutputParameter()
        parse_output_parameter(p_dict, parameter, service_type)
    else:
        if service_type == 'program':
            parameter = InputProgramParameter()
        else:
            parameter = InputParameter()
        parse_input_parameter(p_dict, parameter, service_type)
    parse_para(p_dict, parameter, service_type)
    parameter['main'] = p_dict.att('ismain') in ['1', 'true', 'True']
    parameter['hidden'] = p_dict.att('ishidden') in ['1', 'true', 'True']
    parameter['simple'] = p_dict.att('issimple') in ['1', 'true', 'True']
    # Mobyle2 type
    t_dict = p_dict.get('type')
    m1_class = t_dict.get('datatype').text('class')
    m1_biotypes = [biotype.text() for biotype in t_dict.list('biotype')]
    m1_biotype = m1_biotypes[0] if len(m1_biotypes) == 1 else None
    type_ds = types_map.get_type(m1_class, m1_biotype)
    if type_ds:
        m2_type = getattr(type_module, type_ds['_type'])()
        if 'data_terms' in type_ds:
            m2_type['data_terms'] = type_ds['data_terms']
        for data_format in t_dict.list('dataFormat'):
            df = formats_map.get_format(data_format.text())
            if df:
                m2_type['format_terms'].append(df)
        vlist = p_dict.get('vlist')
        if vlist:
            for velem in vlist.list('velem'):
                m2_type['options'].append({'label': velem.get('label').text(),
                                           'value': velem.get('value').text()})
        elif p_dict.get('flist'):
            logger.error("[not implemented] flist skipped for parameter %s" %
                         p_dict.text('name'))
        vdef = p_dict.get('vdef')
        if vdef:
            values = [v.text() for v in vdef.list('value')]
            m2_type['default'] = values[0] if len(values) == 1 else values
            if m2_type.get('_type') == 'BooleanType':
                # standardize default value for boolean types to true or false
                m2_type['default'] = True if m2_type['default']\
                                          in ['true', 1, True] else False
            elif m2_type.get('_type') == 'IntegerType':
                # cast integer default values to correct type
                m2_type['default'] = int(m2_type['default'])
            elif m2_type.get('_type') == 'FloatType':
                # cast float default values to correct type
                m2_type['default'] = float(m2_type['default'])
        parameter['type'] = m2_type
    return parameter


def parse_input_parameter(p_dict, parameter, service_type):
    """
    parse Mobyle1 parameter element properties for inputs
    :param p_dict: the dictionary representing the Mobyle1 "parameter" element
    :type p_dict: dict
    :param para: the InputParameter
    :type para: InputParameter
    :param service_type: 'program', 'workflow' or 'widget'
    :type service_type: string
    """
    parameter['mandatory'] = p_dict.att('ismandatory') in ['1', 'true', 'True']
    if p_dict.has('ctrl'):
        parameter['ctrl'] = {}
        for code in p_dict.get('ctrl').list('code'):
            parameter['ctrl'][code.att('proglang')] = code.text()
    if service_type == 'program':
        parameter['command'] = p_dict.att('iscommand') in ['1', 'true', 'True']
        parameter['argpos'] = p_dict.text('argpos')
        if p_dict.has('format'):
            parameter['format'] = {}
            for code in p_dict.get('format').list('code'):
                parameter['format'][code.att('proglang')] = code.text()
        parameter['paramfile'] = p_dict.text('paramfile')


def parse_output_parameter(p_dict, parameter, service_type):
    """
    parse Mobyle1 parameter element properties for outputs
    :param p_dict: the dictionary representing the Mobyle1 "parameter" element
    :type p_dict: dict
    :param para: the OutputParameter
    :type para: OutputParameter
    :param service_type: 'program', 'workflow' or 'widget'
    :type service_type: string
    """
    if p_dict.att('isout') in ['1', 'true', 'True']:
        parameter['output_type'] = u'file'
    elif p_dict.att('isstdout') in ['1', 'true', 'True']:
        parameter['output_type'] = u'stdout'
    elif p_dict.att('isstderr') in ['1', 'true', 'True']:
        parameter['output_type'] = u'stderr'
    if service_type == 'program':
        if p_dict.has('filenames'):
            parameter['filenames'] = {}
            for code in p_dict.get('filenames').list('code'):
                parameter['filenames'][code.att('proglang')] = code.text()


def parse_paragraph(p_dict, service_type):
    """
    parse Mobyle1 "paragraph" element
    :param p_dict: the dictionary representing the Mobyle1 "paragraph" element
    :type p_dict: dict
    :param service_type: 'program', 'workflow' or 'widget'
    :type service_type: string
    :returns: tuple containing an InputParagraph and an OutputParagraph object
              corresponding to the Mobyle1 paragraph
    :rtype: tuple
    """
    logger.debug("processing paragraph %s" % p_dict.text('name'))
    input_paragraph = InputParagraph()
    parse_para(p_dict, input_paragraph, service_type)
    output_paragraph = OutputParagraph()
    parse_para(p_dict, output_paragraph, service_type)
    parse_parameters(p_dict.get('parameters'),
                     (input_paragraph, output_paragraph), service_type)
    return (input_paragraph, output_paragraph)


def parse_parameters(s_dict, containers, service_type):
    """
    parse Mobyle1 "parameters" element and add the resulting
    paragraphs/parameters to the relevant containers
    :param s_dict: the dictionary representing the Mobyle1 "parameters" element
    :type s_dict: dict
    :param containers: a tuple containing the corresponding InputParagraph and
                       OutputParagraph containers
    :type containers: tuple
    :param service_type: 'program', 'workflow' or 'widget'
    :type service_type: string
    """
    for p in s_dict.list():
        if p.tag() == 'paragraph':
            input_paragraph, output_paragraph = parse_paragraph(p, service_type)
            if len(input_paragraph['children']) > 0:
                containers[0]['children'].append(input_paragraph)
            if len(output_paragraph['children']) > 0:
                containers[1]['children'].append(output_paragraph)
        elif p.tag() == 'parameter':
            parameter = parse_parameter(p, service_type)
            if isinstance(parameter, InputParameter):
                containers[0]['children'].append(parameter)
            else:
                containers[1]['children'].append(parameter)


def parse_program(s_dict):
    """
    create a program object from a dictionary
    "Mobyle1-style"
    parse Mobyle1 "program" element
    :param p_dict: the dictionary representing the Mobyle1 "program" element
    :type p_dict: dict
    :returns: the corresponding Program object
    :rtype: Program
    """
    p = Program()
    parse_software(s_dict.get('head'), p)
    p['inputs'] = InputParagraph()
    p['outputs'] = OutputParagraph()
    parse_parameters(s_dict.get('parameters'), (p['inputs'], p['outputs']),
                     'program')
    if s_dict.get('head').has('command'):
        p['command'] = {'path': s_dict.get('head').get('command').att('path'),
                        'value': s_dict.get('head').text('command')
                       }
    for env in s_dict.get('head').list('env'):
        p['env'].append({'name': env.att('name'), 'value': env.text()})
    return p


def parse_package(s_dict):
    """
    create a package object from a dictionary
    "Mobyle1-style"
    parse Mobyle1 "package" element
    :param p_dict: the dictionary representing the Mobyle1 "program" element
    :type p_dict: dict
    :returns: the corresponding Package object
    :rtype: Package
    """
    p = Package()
    parse_software(s_dict, p)
    return p


def get_loader(path):
    """
    return a loader function that works relatively to the specified path,
    as a workaround for ElementInclude's baseurl limitation
    :param path: the baseURL path
    :type path: string
    :returns: the loader function
    :rtype: function
    """
    def correct_loader(href, parse, encoding=None):
        """
        the loader function returned by get_loader
        :param href: Resource reference.
        :type href: string
        :param parse: Parse mode.  Either "xml" or "text".
        :type parse: string
        :param encoding: Optional text encoding.
        :type encoding: string
        :returns: The expanded resource.  If the parse mode is "xml", this
                  is an ElementTree instance.  If the parse mode is "text",
                  this is a Unicode string.  If the loader fails, it can return
                  or raise an IOError exception.
        :rtype: ElementTree or unicode
        :throws IOError: If the loader fails to load the resource.
        """
        href_file = open(os.path.join(path, href))
        if parse == "xml":
            data = ET.parse(href_file).getroot()
        else:
            data = href_file.read()
            if encoding:
                data = data.decode(encoding)
        href_file.close()
        return data
    return correct_loader


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                 description='Migrate Mobyle1 XML files to Mobyle2')
    parser.add_argument('--config',
                        help="path to the Mobyle2 config file for DB injection")
    parser.add_argument('--loglevel', help=
                        "logging level for the import script," +
                        "use this to override the configuration")
    parser.add_argument('--storeto', help=
                        "output the generated objects as JSON files")
    parser.add_argument('filenames', help=
                        "files you want to convert", nargs='+')
    parser.add_argument('-public', action="store_true", default=False)
    parser.add_argument('-init', action="store_true", default=False)
    args = parser.parse_args()
    if args.config:
        # Init config
        config = Config(args.config).config()
        # init db connection
        from mobyle.common.connection import connection
        from mobyle.common.service import Service, Program, Package
        from mobyle.common import users
        from mobyle.common import project
        Program = connection.Program
        Package = connection.Package
    else:
        from mobyle.common.service import Service, Program, Package
    from mobyle.common.service import InputParagraph, OutputParagraph, \
                                      InputParameter, OutputParameter, \
                                      InputProgramParameter, \
                                      OutputProgramParameter
    type_module = import_module('mobyle.common.type')
    if args.loglevel:
        try:
            logger.setLevel(args.loglevel)
        except ValueError, ve:
            logger.error(("invalid logging level specified %s," +
                         "loglevel is ignored") % args.loglevel)
    if args.config:
        user = connection.User.find_one({'email': config.get("app:main",
                                         'root_email')})
        project = connection.Project.find_one({ 'owner' : user['_id'] })
        if args.init:
            connection.Program.collection.remove()
            connection.Package.collection.remove()
    if args.storeto:
        import json
    filenames = args.filenames
    for filename in filenames:
        logger.info('processing %s...' % filename)
        try:
            # s stores the result of the parsing
            s = None
            # parse the XML into memory
            elem = ET.parse(filename)
            # process XInclude chunks
            root = elem.getroot()
            EI.include(root, get_loader(os.path.dirname(filename)))
            elem = root
            # create the JSON object
            service = elem_to_internal(elem)
            if service.get('#tag') == 'program':
                s = parse_program(JSONProxy(service))
            elif service.get('#tag') == 'package':
                s = parse_package(JSONProxy(service))
            if s:
                if args.public:
                    s['public_name'] = s['name']
                if args.config:
                    s['project'] = project['_id']
                    s.save()
                if args.storeto:
                    fh = open(os.path.join(args.storeto, s['name'] + '.json'),
                              'w')
                    fh.write(json.dumps(s, sort_keys=True,
                                        indent=4, separators=(',', ': ')))
                    fh.close()

        # pylint: disable=W0703
        #        Invalid name "logger" for type constant
        except Exception, exc:
            logger.error("Error processing file %s: %s" %
                         (filename, exc.message), exc_info=True)
    for variable, file_name in [(types_map, 'missing_mapped_types'),
                                (formats_map, 'missing_mapped_formats'),
                                (topics_map, 'missing_mapped_topics'),
                                (operations_map, 'missing_mapped_operations')]:
        report_file = open(file_name, 'w')
        report_file.writelines([item + '\n' for item in variable.missing])
        report_file.close()
