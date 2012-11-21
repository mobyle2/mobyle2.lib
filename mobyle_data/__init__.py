# -*- coding: utf-8 -*-
'''
Created on Nov. 12, 2012

@author: E. LEGROS
@contact: emeline.legros@ibcp.fr
@license: GPLv3
'''

from ming.datastore import DataStore
from ming import Session


bind = DataStore('mongodb://localhost', database='test')
session = Session(bind)

