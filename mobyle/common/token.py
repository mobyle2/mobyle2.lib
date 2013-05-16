# -*- coding: utf-8 -*-

from mongokit import Document
from mf.annotation import mf_decorator

from .connection import connection
from .config import Config

from datetime import datetime, timedelta
from uuid import uuid4


@mf_decorator
@connection.register
class Token(Document):
    """
    Token are temporary tokens with a timestamp used a 
    validity periods. Used for temporary user interactions
    such as password reset.
    """

    __collection__ = 'tokens'
    __database__ = Config.config().get('app:main','db_name')

    structure = { 'token' : basestring, 
                  'timestamp' : datetime,
                  'user' : basestring
                }

    required_fields = ['token', 'timestamp']


    def generate(self, validity_period = 3600):
        """
        Create a token based on timestamp

        :param validity_period: Duration of token validity
        :type validity_period: int
        """
        token = str(uuid4())
        timestamp = datetime.now()
        self['token'] = token
        self['timestamp'] = timestamp + timedelta(seconds=validity_period)

    def check_validity(self, remove=True):
        """
        Checks the validity of a token against current time

        :param remove: Remove the token after the test, valid or not
        :type remove: bool
        :return: True if valid, else return False
        """
        curtime = datetime.now()
        if(curtime>self['timestamp']):
            if remove:
                self.delete()
            return False
        if remove:
            self.delete()
        return True

