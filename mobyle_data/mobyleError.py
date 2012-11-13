# -*- coding: utf-8 -*-
'''
Created on Nov. 12, 2012

@author: E. LEGROS
@contact: emeline.legros@ibcp.fr
@license: GPLv3
'''



from exceptions import Exception

class MobyleError(Exception):
    """
    MobyleError is a class that manages exceptions. 
    """
    
    def __init__(self, msg = None):
	"""
	:param msg: exception information message
	:type msg: string
	"""
	
        self._message = str( msg )
    
    def _get_message(self):
	"""
	:return: exception information message
	:rtype: string
	"""
	
        return self._message
    #workaround to ensure Mobyle compatibility
    #with either python 2.5 and python 2.6
    #as self.message is deprecated in python 2.6
    message = property( fget = _get_message )
    
    def __str__(self, *args, **kwargs):
	"""
	:return: exception information message
	:rtype: string
	"""
	
        return self.message

