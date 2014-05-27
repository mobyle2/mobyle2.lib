# -*- coding: utf-8 -*-
"""
Created on Feb 08, 2013

@author: Hervé Ménager
@contact: hmenager@pasteur.fr
@organization: Institut Pasteur
@license: GPLv3
"""
import os
from collections import OrderedDict

import xml.etree.cElementTree as ET
import xml.etree.ElementInclude as EI
from xml2json import elem_to_internal, internal_to_elem
import logging
import argparse
from importlib import import_module
import yaml
from mongokit import SchemaDocument, ObjectId

from mobyle.common.config import Config

# pylint: disable=C0103
#        Invalid name "logger" for type constant
logger = logging.getLogger('mobyle.classification_update')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                 description='Mobyle2 services import/export')
    parser.add_argument('--config', required=True,
                        help="path to the Mobyle2 config file")
    parser.add_argument('--loglevel', help=
                        "logging level for the import script," +
                        "use this to override the configuration")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--dump', help=
                        "export services to specified directory")
    action.add_argument('--load', help=
                        "import services from specified directory")
    args = parser.parse_args()
    # Init config
    config = Config(args.config).config()
    # init db connection
    from mobyle.common.connection import connection
    from mobyle.common.service import Service, Program
    if args.loglevel:
        try:
            logger.setLevel(args.loglevel)
        except ValueError, ve:
            logger.error(("invalid logging level specified %s," +
                         "loglevel is ignored") % args.loglevel)

    def represent_schema_doc( self, data):
        d = OrderedDict()
        def set_value(key):
            if data[key] is not None and data[key]!=[] and\
                not(isinstance(data[key], ObjectId)):
                if hasattr(data, 'default_values') and \
                    key in data.default_values and \
                    data.default_values[key]==data[key]:
                        return
                d[key] = data[key]
        d['_type'] = data['_type']
        if hasattr(data,'keys_order'):
            keys = data.keys_order
            keys += [key for key in data.structure if key not in data.keys_order]
        else:
            keys = data.structure.keys()
        for key in keys:
            set_value(key)
        return self.represent_mapping('tag:yaml.org,2002:map', d.items())

    yaml.add_multi_representer(SchemaDocument, represent_schema_doc)
    yaml.add_representer(unicode, yaml.representer.SafeRepresenter.represent_unicode)

    if args.dump:
        for s in connection.Service.fetch():
            logger.info("exporting service %s/%s" % (s['name'], s['version']))
            basefilename = s['name']
            if s['version']:
                basefilename += "_%s" % s['version']
            filename = os.path.join(args.dump, basefilename + ".yaml")
            s_yaml = yaml.dump(s, file(filename, 'w'), indent=4, tags=None)
            logger.info("done exporting service to file %s" % (filename))
    elif args.load:
        filenames = args.load
        for filename in filenames:
            logger.info("importing service from file %s" % (filename))
            s_yaml = yaml.load(file(filename, 'r'))
            s = connection.Service(s_yaml)
            s.save()
            logger.info("done importing service %s/%s" % (s['name'], s['version']))
