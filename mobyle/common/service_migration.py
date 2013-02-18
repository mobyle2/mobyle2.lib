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
logger.setLevel(logging.DEBUG)

def parse_text_or_html(struct):
    """
    parse Mobyle1 "XHTML or text" elements
    :param struct: the json dictionary containing the Mobyle1 "XHTML or text" elements
    :type struct: dict 
    :returns: the result of the parsing
    :rtype: string
    """
    s = ''
    for d in to_list(struct):
        if isinstance(d,basestring):
            s += d
        elif d.has_key('text'):
            s += ''.join([e['#text'] for e in to_list(d['text'])])
        else:
            s += ET.tostring(internal_to_elem(d))
    return s

def to_list(val):
    """
    convert a JSON value to a list
    if it is a string
    (useful as many converted JSON values
    are strings OR lists depending on the
    number of values)
    """
    if not(isinstance(val,list)):
        return [val]
    else:
        return [v for v in val if v is not None]

def parse_software(d, s):
    """
    parse top-level elements of the software
    """
    s['name'] = d['name']
    s['version'] = d.get('version', 'unspecified')
    s['title'] = d['doc']['title']
    s['description'] = parse_text_or_html(d['doc']['description'])
    s['authors'] = d['doc'].get('authors', 'unspecified')
    for r in to_list(d['doc'].get('reference',[])):
        refdic = {}
        if isinstance(r, basestring):
            refdic['label']=r
            refdic['doi']=None
            refdic['url']=None
        else:
            refdic['label']=r['#text'] if r.has_key('#text') else None
            refdic['doi']=r['@doi'] if r.has_key('@doi') else None
            refdic['url']=r['@url'] if r.has_key('@url') else None
        s['references'].append(refdic)
    for link in to_list(d['doc'].get('sourcelink',[])):
        s['source_links'].append(link)
    for link in to_list(d['doc'].get('doclink',[])):
        s['documentation_links'].append(link)
    for link in to_list(d['doc'].get('homepagelink',[])):
        s['homepage_links'].append(link)
    if d['doc'].has_key('comment'):
        s['comment']=parse_text_or_html(d['doc']['comment'])
    for cat in to_list(d.get('category',[])):
        s['classifications'].append({'type':'mobyle1','classification':cat})
    for cat in to_list(d.get('edam_cat',[])):
        s['classifications'].append({'type':'EDAM','classification':cat['@ref']})
    return s

def parse_parameter(p_dict):
    logger.info("processing parameter %s" % p_dict['name'])
    if p_dict.has_key('@isout') or p_dict.has_key('@isstdout'):
        parameter = OutputParameter()
    else:
        parameter = InputParameter()
    parameter['name']=p_dict['name']
    return parameter

def parse_paragraph(p_dict):
    logger.info("processing paragraph %s" % p_dict['name'])
    input_paragraph = InputParagraph()
    input_paragraph['name']=p_dict['name']
    output_paragraph = OutputParagraph()
    output_paragraph['name']=p_dict['name']
    parse_parameters(p_dict['parameters'],(input_paragraph, output_paragraph))
    return (input_paragraph, output_paragraph)

def parse_parameters(s_dict,containers):
    for p in s_dict.get('contents',[]):
        if p[0]=='paragraph':
            input_paragraph, output_paragraph = parse_paragraph(p[1])
            if len(input_paragraph['children'])>0:
                containers[0]['children'].append(input_paragraph)
            if len(output_paragraph['children'])>0:
                containers[1]['children'].append(output_paragraph)
        elif p[0]=='parameter':
            parameter = parse_parameter(p[1])
            if isinstance(parameter,InputParameter):
                containers[0]['children'].append(parameter)
            else:
                containers[1]['children'].append(parameter)

def program_parse(s_dict):
    """
    create a program object from a dictionary
    "Mobyle1-style"
    """
    p = mobyle.common.session.Program()
    p = parse_software(s_dict['head'], p)
    p['inputs']=InputParagraph()
    p['outputs']=OutputParagraph()
    parse_parameters(s_dict['parameters'],(p['inputs'],p['outputs']))
    p.save()

if __name__ == '__main__':
    filenames = sys.argv[1:]
    for filename in filenames: 
        logger.info('processing %s...' % filename)
        try:
            # parse the XML into memory
            elem = ET.fromstring(open(filename).read())
            # create the JSON object
            service = elem_to_internal(elem,list_elems=['parameters'])
            if service.has_key('program'):
                program_parse(service['program'])
        except Exception, exc:
            logger.error("Error processing file %s: %s" % (filename, exc.message),exc_info=True)
