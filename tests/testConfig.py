# -*- coding: utf-8 -*-
'''
Created on Nov. 27, 2012

@author: Olivier Sallou
@contact: olivier.sallou@irisa.fr
@license: GPLv3
'''


import unittest
from tempfile import mkstemp

from mobyle.config import *

class TestConfig(unittest.TestCase):
    """ Tests for the Config class
    """

    def setup(self):
        Config._config = None
        Config._log = None
        Config._file = None

    def test_default_config(self):
        myconfig = Config()
        Config.logger().setLevel(logging.ERROR)
        self.assertEqual(myconfig._config.get("app:main","db_uri"),"mongodb://localhost")

    def test_file_config(self):
        tmpconfig = os.path.join(os.path.dirname(os.path.realpath(__file__)),"test.conf")
        myconfig = Config(tmpconfig) 
        self.assertEqual(myconfig._config.get("app:main","db_uri"),"mongodb://samplehost")

    def test_reload_config(self):
        myconfig = Config()
        self.assertEqual(myconfig._config.get("app:main","db_uri"),"mongodb://samplehost")
        Config.config().set("app:main","db_uri","mongodb://localhost")	
        self.assertEqual(Config.config().get("app:main","db_uri"),"mongodb://localhost")
        Config.reload()
        self.assertEqual(myconfig._config.get("app:main","db_uri"),"mongodb://samplehost")



if __name__=='__main__':
    unittest.main()

