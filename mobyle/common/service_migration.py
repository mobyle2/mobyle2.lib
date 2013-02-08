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
from service import Program

filemasks = sys.argv[1:]
for filename in filemasks: 
    print 'processing %s...' % filename
    elem = ET.fromstring(open(filename).read())
    print elem_to_internal(elem)
