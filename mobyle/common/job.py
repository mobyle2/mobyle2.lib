# -*- coding: utf-8 -*-

import abc
from abc import ABCMeta
from abc import abstractmethod
from mobyleError import MobyleError

from mongokit import Document

from mobyle.common import session
from mobyle.common.config import Config

class Job(Document):
    """
    Empty class for the moment, only used as reference
    """

    __collection__ = 'jobs'
    __database__ = Config.config().get('app:main','db_name')

    structure = { 'name' : basestring }

session.register([Job])

