# -*- coding: utf-8 -*-

import abc
from abc import ABCMeta
from abc import abstractmethod
from mobyleError import MobyleError

from mongokit import Document

from mobyle.common import session
from mobyle.common.config import Config

import mf.annotation
from mf.annotation import *

@mf_decorator
class Program(Document):
    """
    Empty class for the moment, only used as reference
    """

    __collection__ = 'programs'
    __database__ = Config.config().get('app:main','db_name')

    structure = { 'name' : basestring, 'public' : bool }

    default_values = { 'public': True }

    required_fields = [ 'name' ]


session.register([Program])

