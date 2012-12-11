# -*- coding: utf-8 -*-
'''
Created on Nov. 12, 2012

@author: E. LEGROS
@contact: emeline.legros@ibcp.fr
@license: GPLv3
'''
__import__('pkg_resources').declare_namespace('mobyle')

from ming.datastore import DataStore
from ming import create_datastore
from ming import Session


session = Session()

def init_mongo(engine):
    global session
    server, database = engine
    session.bind = create_datastore("%s%s"%(server, database))


