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

import mobyle.common.connection
mobyle.common.connection.init_mongo("mongodb://localhost/")

def parse_text_or_html(struct):
    """
    parse Mobyle1 "XHTML or text" elements
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
        try:
            # parse the XML into memory
            elem = ET.fromstring(open(filename).read())
            # create the JSON object
            service = elem_to_internal(elem)
            if service.has_key('program'):
                program_parse(service['program'])
        except Exception, exc:
            print "Error processing file %s: %s" % (filename, exc.message)
