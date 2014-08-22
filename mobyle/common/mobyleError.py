# -*- coding: utf-8 -*-

#===============================================================================
# Created on Aug 21, 2013
# 
# @author: Bertrand Néron
# @contact: bneron <at> pasteur <dot> fr
# @organization: Institut Pasteur
# @license: GPLv3
#===============================================================================


from exceptions import Exception
from types import ListType, TupleType


class MobyleError(Exception):
    """
    MobyleError is a class that manages Mobyle specific exceptions. 
    """
    pass


class UserValueError(MobyleError):
    
    def __init__(self, parameters = None, message = None):
        if message is not None:
            super(UserValueError, self).__init__(message)
        else:
            super(UserValueError, self).__init__()
        type_parameters = type(parameters)
        if isinstance(type_parameters, (ListType, TupleType)): 
            self.parameters = parameters
        else:
            self.parameters = [parameters]
        