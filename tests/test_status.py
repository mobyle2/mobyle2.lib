# -*- coding: utf-8 -*-

'''
Created on Aug 27, 2012

@author: Bertrand Néron
@contact: bneron@pasteur.fr
@organization: Institut Pasteur
@license: GPLv3
'''
import os
import sys

MOBYLE_HOME = os.path.abspath( os.path.join( os.path.dirname( __file__ ) , "../" ) )
os.environ[ 'MOBYLE_HOME' ] = MOBYLE_HOME
if ( MOBYLE_HOME ) not in sys.path:
    sys.path.append( MOBYLE_HOME )
    
import unittest
import inspect
import types
#a config object must be instantiated first for each entry point of the application
from mobyle.common.config import Config
config = Config( os.path.join( os.path.dirname(__file__), 'test.conf'))
from mobyle.common.job import Status


class StatusTest(unittest.TestCase):

    def setUp(self):
        #tuple (attribute , value)
        self.all_status_tuple = [ m  for m in inspect.getmembers( Status ) if type(m[1]) == types.UnicodeType ]
        self.all_status_object = [ Status(code = t[1]) for t in self.all_status_tuple]
        self.status_attr =  [ l[0] for l in self.all_status_tuple ] 
        self.status_string = {}
        for l in self.status_attr: 
            self.status_string [l] = l.lower()
            
        self.ended_status = [ Status(code = c) for c in (Status.FINISHED, Status.ERROR, Status.KILLED) ]
        self.error_status = [ Status(code = c) for c in (Status.ERROR, Status.KILLED) ]
        self.queryable_status = [ Status(code = c) for c in (Status.SUBMITTED, Status.PENDING, Status.RUNNING, Status.HOLD) ]
        self.known_status = [ s for s in self.all_status_object if s.code != Status.UNKNOWN ]
        self.submittable_status = [ Status(code = c) for c in [Status.BUILDING] ]
        
    def test_eq(self):
        """
        2 Status instance are equals if they have
         - the same status code 
        """
        print self.status_attr
        
        for l1 in self.status_attr:
            s1= Status( code = getattr( Status, l1 ) )
            for l2 in self.status_attr:
                s2= Status( code = getattr( Status, l2 ) )
                if l1 == l2:
                    self.assertTrue(s1 == s2)
                else:
                    self.assertTrue(s1 != s2)
    

    def test_is_ended(self):
        """
        a status is ended if it cannot evolved anymore (error, killed, finished,...)
        """
        not_ended = [ s for s in self.all_status_object if s not in self.ended_status]
        for s in self.ended_status:
            self.assertTrue( s.is_ended() )
        for s in not_ended:
            self.assertFalse( s.is_ended() )
    
    def test_is_on_error(self):
        not_error = [ s for s in self.all_status_object if s not in self.error_status]
        for s in self.error_status:
            self.assertTrue( s.is_on_error() )
        for s in not_error:
            self.assertFalse( s.is_on_error() )
            
    def test_is_known(self):
        not_known = [ s for s in self.all_status_object if s not in self.known_status]
        for s in self.known_status:
            self.assertTrue( s.is_known() )
        for s in not_known:
            self.assertFalse( s.is_known() )
            
    def test_is_queryable(self):
        not_queryable = [ s for s in self.all_status_object if s not in self.queryable_status]
        for s in self.queryable_status:
            self.assertTrue( s.is_queryable() )
        for s in not_queryable:
            self.assertFalse( s.is_queryable() )
            
    def test_is_submittable(self):
        not_submittable = [ s for s in self.all_status_object if s not in self.submittable_status]
        for s in self.submittable_status:
            self.assertTrue( s.is_submittable() )
        for s in not_submittable:
            self.assertFalse( s.is_submittable() )
            
    def test_str(self):
        for l, c in self.all_status_tuple:
            s = Status(code = c)
            self.assertEqual( str(s) , l.lower().replace('_', ' ') )
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()