import unittest
from tempfile import mkstemp

from mobyle.config import *

class TestConfig(unittest.TestCase):

    def setup(self):
	Config._config = None
	Config._log = None
	Config._file = None

    def test_default_config(self):
	myconfig = Config()
	Config.logger().setLevel(logging.ERROR)
        self.assertEqual(myconfig._config.get("main","mongo.url"),"mongodb://localhost")

    def test_file_config(self):
	tmpconfig = os.path.join(os.path.dirname(os.path.realpath(__file__)),"test.conf")
	myconfig = Config(tmpconfig) 
        self.assertEqual(myconfig._config.get("main","mongo.url"),"mongodb://samplehost")

    def test_reload_config(self):
	myconfig = Config()
        self.assertEqual(myconfig._config.get("main","mongo.url"),"mongodb://samplehost")
	Config.config().set("main","mongo.url","mongodb://localhost")	
        self.assertEqual(Config.config().get("main","mongo.url"),"mongodb://localhost")
	Config.reload()
        self.assertEqual(myconfig._config.get("main","mongo.url"),"mongodb://samplehost")
	


if __name__=='__main__':
	unittest.main()


