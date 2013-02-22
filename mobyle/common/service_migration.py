# -*- coding: utf-8 -*-
"""
Created on Feb 08, 2013

@author: Hervé Ménager
@contact: hmenager@pasteur.fr
@organization: Institut Pasteur
@license: GPLv3
"""
import sys
import xml.etree.cElementTree as ET
from xml2json import elem_to_internal, internal_to_elem
import logging

import mobyle.common.connection
mobyle.common.connection.init_mongo("mongodb://localhost/")
from service import InputParagraph, OutputParagraph, InputParameter, OutputParameter

logger = logging.getLogger('mobyle.service_migration')
logger.setLevel(logging.INFO)

class JSONDictProxy:

    def __init__(self, json_dict):
        self.json_dict = json_dict

    def tag(self):
        return self.json_dict.get('#tag')

    def get(self, key, default=None):
        try:
            el = [n for n in self.json_dict['#children'] if isinstance(n, dict) and n['#tag'] == key]
            return JSONDictProxy(el[0])
        except IndexError:
            return default

    def att(self, key, default=None):
        try:
            return self.json_dict['@%s' % key]
        except KeyError:
            return default

    def text(self, key=None, default=None):
        try:
            if key is not None:
                text = [n['#children'][0] for n in self.json_dict['#children'] if isinstance(n, dict) and n['#tag'] == key]
                return text[0]
            else:
                return self.json_dict['#children'][0]
        except IndexError:
            return default

    def list(self, key=None):
        """
        convert a JSON value to a list
        if it is a string
        (useful as many converted JSON values
        are strings OR lists depending on the
        number of values)
        """
        if key is not None:
            el = [n for n in self.json_dict['#children'] if isinstance(n, dict) and n['#tag'] == key]
            return [JSONDictProxy(item) for item in el]
        else:
            return [JSONDictProxy(item) for item in self.json_dict['#children']]

    def has(self, key):
        return len([n for n in self.json_dict['#children'] if isinstance(n, dict) and n['#tag'] == key])>0

    def text_or_html(self):
        s = ''
        for d in self.json_dict['#children']:
            if isinstance(d, basestring):
                s += d
            elif d['#tag'] == 'text' and len(d['#children']) == 1:
                s += d['#children'][0]
            else:
                s += ET.tostring(internal_to_elem(d))
        return s

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
    s['description'] = d.get('doc').get('description').text_or_html()
    s['authors'] = d.get('doc').text('authors', 'unspecified')
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
        s['classifications'].append({'type':'mobyle1', 'classification':cat.text()})
    for cat in d.list('edam_cat'):
        s['classifications'].append({'type':'EDAM', 'classification':cat['@ref']})
    return s

def parse_para(p_dict, para):
    """
    parse Mobyle1 common "parameter" or "paragraph" element properties
    :param p_dict: the dictionary representing the Mobyle1 "parameter" element
    :type p_dict: dict 
    :param para: the Parameter or Paragraph object 
    :type para: Para
    """
    para['name'] = p_dict.text('name')
    para['prompt'] = p_dict.text('prompt')
    if p_dict.has('comment'):
        para['comment'] = p_dict.get('comment').text_or_html()
    if p_dict.has('precond'):
        para['precond'] = {}
        for code in p_dict.get('precond').list('code'):
            para['precond'][code.att('proglang')] = code.text()
        #for 
        #para['precond'] = p_dict.get('precond').list('code')

def parse_parameter(p_dict):
    """
    parse Mobyle1 "parameter" element
    :param p_dict: the dictionary representing the Mobyle1 "parameter" element
    :type p_dict: dict 
    :returns: the InputParameter or OutputParameter object 
    :rtype: Parameter
    """
    logger.debug("processing parameter %s" % p_dict.text('name'))
    if p_dict.att('isout') or p_dict.att('isstdout'):
        parameter = OutputParameter()
    else:
        parameter = InputParameter()
    parse_para(p_dict, parameter)
    parameter['ismain'] = p_dict.att('ismain') in ['1','true','True']
    parameter['hidden'] = p_dict.att('ishidden') in ['1','true','True']
    return parameter

def parse_paragraph(p_dict):
    """
    parse Mobyle1 "paragraph" element
    :param p_dict: the dictionary representing the Mobyle1 "paragraph" element
    :type p_dict: dict 
    :returns: tuple containing an InputParagraph and an OutputParagraph object
              corresponding to the Mobyle1 paragraph 
    :rtype: tuple
    """
    logger.debug("processing paragraph %s" % p_dict.text('name'))
    input_paragraph = InputParagraph()
    parse_para(p_dict, input_paragraph)
    output_paragraph = OutputParagraph()
    parse_para(p_dict, output_paragraph)
    parse_parameters(p_dict.get('parameters'), (input_paragraph, output_paragraph))
    return (input_paragraph, output_paragraph)

def parse_parameters(s_dict, containers):
    """
    parse Mobyle1 "parameters" element and add the resulting paragraphs/parameters
    to the relevant containers
    :param s_dict: the dictionary representing the Mobyle1 "parameters" element
    :type s_dict: dict
    :param containers: a tuple containing the corresponding InputParagraph and 
                       OutputParagraph containers
    :type containers: tuple
    """
    for p in s_dict.list():
        if p.tag() == 'paragraph':
            input_paragraph, output_paragraph = parse_paragraph(p)
            if len(input_paragraph['children']) > 0:
                containers[0]['children'].append(input_paragraph)
            if len(output_paragraph['children']) > 0:
                containers[1]['children'].append(output_paragraph)
        elif p.tag() == 'parameter':
            parameter = parse_parameter(p)
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
    p = mobyle.common.session.Program()
    parse_software(s_dict.get('head'), p)
    p['inputs'] = InputParagraph()
    p['outputs'] = OutputParagraph()
    parse_parameters(s_dict.get('parameters'), (p['inputs'], p['outputs']))
    p.save()

if __name__ == '__main__':
    filenames = sys.argv[1:]
    for filename in filenames: 
        logger.info('processing %s...' % filename)
        try:
            # parse the XML into memory
            elem = ET.fromstring(open(filename).read())
            # create the JSON object
            service = elem_to_internal(elem)
            if service.get('#tag')=='program':
                parse_program(JSONDictProxy(service)) 
        except Exception, exc:
            logger.error("Error processing file %s: %s" % (filename, exc.message), exc_info=True)
