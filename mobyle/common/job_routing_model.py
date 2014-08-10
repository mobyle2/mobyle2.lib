# -*- coding: utf-8 -*-

#========================
# :Date: Jul 29, 2014
# :Authors: Bertrand Néron
# :Contact: bneron<at>pasteur<dot>fr
# :Organization: Institut Pasteur
# :license: GPLv3
#========================

from mongokit import Document, SchemaDocument
from mf.annotation import mf_decorator

from .config import Config
from .connection import connection

@mf_decorator
@connection.register
class ExecutionSystem(Document):
    
    __collection__ = 'exec_system'
    __database__ = Config.config().get('app:main', 'db_name')
    
    structure = { '_id' : basestring,
                 'class' : basestring,
                 'drm_options' : None,
                 'native_specifications' : basestring
                }


class ExecutionRule(SchemaDocument):
    
    structure = {'name' : basestring,
                 'parameters': dict
                 }
    
    
@mf_decorator
@connection.register
class ExecutionRoutes(Document):
    
    __collection__ = 'exec_routes'
    __database__ = Config.config().get('app:main', 'db_name')
    
    structure = {"map" : [
                         {'name' : basestring,
                          'rules' : [ExecutionRule],
                          'exec_system' : basestring
                         }
                        ]
                 }    
