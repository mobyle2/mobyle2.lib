import unittest
import os.path
from mobyle.common.config import Config

class AbstractMobyleTest(unittest.TestCase):
    
    def __init__(self, methodName = 'runTest', file = ''):
        super(AbstractMobyleTest, self).__init__(methodName = methodName)
        conf_file = file if file else os.path.join( os.path.dirname(__file__), 'test.conf')
        config = Config( conf_file )
        