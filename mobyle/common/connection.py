# -*- coding: utf-8 -*-

#===============================================================================
# Created on Mar 13, 2013
# 
# @author: Bertrand Néron
# @contact: bneron <at> pasteur <dot> fr
# @organization: Institut Pasteur
# @license: GPLv3
#===============================================================================

from mongokit import Connection
from .config import Config
import os

class FakeConnection(object):
    """Fake connection when no db is present for doc generation"""

    def register(self, param):
        return param


if os.environ['MOBYLE_NODB'] == True:
    connection = FakeConnection() 
else:
    connection = Connection(host = Config.config().get('app:main','db_uri'))
