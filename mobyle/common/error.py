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
    This is the base class for all error produced by Mobyle
    """
    def __init__(self, message=None):
        self.properties = {}
        super(MobyleError, self).__init__(message)
        self.message = message

    @property
    def message(self):
        return self.properties['message']

    @message.setter
    def message(self, message):
        self.properties['message'] = message


class UserError(MobyleError):
    """
    UserError is the base class for error due to an invalid action of the user 
    """
    pass


class UserValueError(UserError):
    """
    Handle error due to a wrong value provide by the user
    This Error have a list of parameters which produces this error 
    """
    
    def __init__(self, parameters = None, message = None):
        if message is not None:
            super(UserValueError, self).__init__(message)
        else:
            super(UserValueError, self).__init__()
        if isinstance(parameters, (ListType, TupleType)): 
            self.parameters = parameters
        else:
            self.parameters = [parameters]

    @property
    def parameters(self):
        return self.properties['parameters']

    @parameters.setter
    def parameters(self, parameters):
        self.properties['parameters'] = parameters
        
class InternalError(MobyleError):
    """
    This is the base class for error which are not the consequence of user action.
    """
    pass

class ConfigError(InternalError):
    """
    Handle error due to a misconfiguration of Mobyle.
    """
    pass
