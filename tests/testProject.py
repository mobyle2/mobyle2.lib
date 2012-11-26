import unittest
from mobyle_project.project import *

	
	
class TestProject(unittest.TestCase):

    def setUp(self):
	self.my_project = Project('Emeline', 'MyProject')

    def test_project(self):
        self.assertEqual(self.my_project.project_name, 'MyProject')
	self.assertEqual(self.my_project.project_owner, 'Emeline')


	

if __name__=='__main__':
	unittest.main()


