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
from xml2json import elem_to_internal
#from service import Program

#import mobyle.common
#from mobyle.common import session

import mobyle.common.connection
mobyle.common.connection.init_mongo("mongodb://localhost/")

def parse_software(d, s):
    """
    parse top-level elements of the software
    """
    s['name'] = d['name']
    s['version'] = d.get('version', 'unspecified')
    s['title'] = d['doc']['title']
    s['description'] = d['doc']['description']['text']['#text']
    s['authors'] = d['doc'].get('authors', 'unspecified')
    
    return s

def program_parse(s_dict):
    """
    create a program object from a dictionary
    "Mobyle1-style"
    """
    p = mobyle.common.session.Program()
    p = parse_software(s_dict['head'], p)
    p.save()

if __name__ == '__main__':
    filenames = sys.argv[1:]
    for filename in filenames: 
        print 'processing %s...' % filename
        # parse the XML into memory
        elem = ET.fromstring(open(filename).read())
        # create the JSON object
        service = elem_to_internal(elem)
        if service.has_key('program'):
            program_parse(service['program'])
