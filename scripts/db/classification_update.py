# -*- coding: utf-8 -*-
"""
Created on Feb 08, 2013

@author: Hervé Ménager
@contact: hmenager@pasteur.fr
@organization: Institut Pasteur
@license: GPLv3
"""
import os
import xml.etree.cElementTree as ET
import xml.etree.ElementInclude as EI
from xml2json import elem_to_internal, internal_to_elem
import logging
import argparse
from importlib import import_module

from mobyle.common.config import Config

# pylint: disable=C0103
#        Invalid name "logger" for type constant
logger = logging.getLogger('mobyle.classification_update')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                 description='Migrate Mobyle1 XML files to Mobyle2')
    parser.add_argument('--config', required=True,
                        help="path to the Mobyle2 config file for DB injection")
    parser.add_argument('--loglevel', help=
                        "logging level for the import script," +
                        "use this to override the configuration")
    args = parser.parse_args()
    # Init config
    config = Config(args.config).config()
    # init db connection
    from mobyle.common.classification import ClassificationLoader
    if args.loglevel:
        try:
            logger.setLevel(args.loglevel)
        except ValueError, ve:
            logger.error(("invalid logging level specified %s," +
                         "loglevel is ignored") % args.loglevel)
    classification_loader = ClassificationLoader('EDAM_topic:0003')
