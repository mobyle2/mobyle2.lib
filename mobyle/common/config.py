# -*- coding: utf-8 -*-
'''
Created on Nov. 27, 2012

@author: Olivier Sallou
@contact: olivier.sallou@irisa.fr
@license: GPLv3
'''



import sys
import os

import ConfigParser

import logging
import logging.config


from mobyle.common.error import MobyleError


class Config:
    """
    Config loads mobyle configuration file.

    Configuration file can be specified or loaded in $HOME/.mobyle or current directory if not specified.
    File also contains configuration for the logger

    Config object must be instanciated once at application startup

    :Example:

    Config('path_to_my_configfile')

    To get access to a Config element, one must specify the section and key.

    :Example:

    Config.get("app:main","db_uri")

    To get a logger, just use the following.

    :Example:

    Config.logger("mylogger") or Config.logger() for defaults
    """

    # File holding the configuration
    _file = None
    # Configuration parser
    _config = None

    _log = None

    def __init__(self, file = None):
        """
        :param file: Path to the configuration file
        :type file: String
        """

        if file is None:
            if os.path.exists( os.path.join(os.getcwd(),"mobyle.conf")):
                Config._file =  os.path.join(os.getcwd(),"mobyle.conf")
            elif os.path.exists(os.path.expanduser(".mobyle")):
                Config._file = os.path.expanduser(".mobyle")
        else:
            if os.path.exists(file):
                Config._file = file

        Config.__parse_config_file(Config._file)

        if Config._file is None:
            Config.logger().warn( "No configuration file available, using defaults" )


    @staticmethod
    def __parse_config_file(file = None):
        """
        Parse the configuration file

        :param file: Configuration file to parse
        :type file: String
        """


        config = ConfigParser.ConfigParser()
        if file is not None:
            # If config file, load Logger config
            Config._log = logging
            logging.config.fileConfig(file)
            config.readfp(open(file))
        else:
            # Set defaults
            config.add_section("app:main")
            config.set("app:main","db_uri","mongodb://localhost")
            config.set("app:main","db_name","mobyle")

        Config._config = config



    @staticmethod
    def reload():
        """
        Reload configuration file
        """
        Config.__parse_config_file(Config._file)
        

    @staticmethod
    def logger(mylogger = "mobyle"):
        """
        Gets a logger from configuration file.
        If no logger is defined, create a default one.

        :param mylogger: name of the Logger, defaults to mobyle
        :type: String
        :return: logger
        :rtype: Logger
        """
        if Config._log is None:
            # Set default log handler on console with level WARN
            logger = logging.getLogger("mobyle")
            if not logger.handlers:
                logger.setLevel(logging.WARN)
                # create console handler and set level to info
                ch = logging.StreamHandler()
                ch.setLevel(logging.WARN)
                # create formatter
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                # add formatter to ch
                ch.setFormatter(formatter)
                # add ch to logger
                logger.addHandler(ch)
                return logger
            else:
                Config._log = logging

        return Config._log.getLogger( mylogger)


    @staticmethod
    def config():
        """
        Get the configuration parser

        :return: the config parser
        :rtype: ConfigParser

        ..  seealso:: ConfigParser
        """
        if Config._config is None:
            # If not config, initialize with defaults
            Config()
        return Config._config

