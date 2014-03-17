# -*- coding: utf-8 -*-
"""
Created on Feb 13, 2013

@author: Olivia Doppelt-Azeroual
@author Hervé Ménager
@contact: odoppelt@pasteur.fr
@contact: hmenager@pasteur.fr
@organization: Institut Pasteur
@license: GPLv3
"""
import logging
import argparse

from mobyle.common.config import Config

logger = logging.getLogger('mobyle.data_format_terms_list')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                 description='Retrieve EDAM data terms and associated format')
    parser.add_argument('--config', required=True,
                        help="path to the Mobyle2 config file for DB injection")
    parser.add_argument('--loglevel', help=
                        "logging level for the import script," +
                        "use this to override the configuration")
    args = parser.parse_args()
    # Init config
    config = Config(args.config).config()
    # init db connection
    from mobyle.common.service_terms import ServiceTypeTermLoader

    if args.loglevel:
        try:
            logger.setLevel(args.loglevel)
        except ValueError, ve:
            logger.error(("invalid logging level specified %s," +
                         "loglevel is ignored") % args.loglevel)
    ServiceTypeTermLoader()