# -*- coding: utf-8 -*-

from mongokit import Document, ObjectId
from mf.annotation import mf_decorator

from .connection import connection
from .config import Config
from .mobyleConfig import MobyleConfig

import smtplib
from email.mime.text import MIMEText

import logging


@mf_decorator
@connection.register
class Notification(Document):
    """
    User notifications
    """

    MOBYLE_NOTIFICATION = 0
    PROJECT_NOTIFICATION = 1
    JOB_NOTIFICATION = 2
    DATA_NOTIFICATION = 3

    __collection__ = 'notifications'
    __database__ = Config.config().get('app:main', 'db_name')

    structure = {'message': basestring,
                  'user': ObjectId,
                  'type': int,
                  'read': bool
                }

    required_fields = ['message', 'user', 'type']
    default_values = {'read': False}

    is_debug = False

    def my(self, control, request, authenticated_userid):
        user = connection.User.find_one({'email': authenticated_userid})
        if user:
            return {'user': user['_id']}
        else:
            return None

    def notify(self):
        """
        Send notification to user according to its preferences

        :return: True is notification sent, False if an error occured.
        """
        if self['type'] == 0:
            res = self.sendMail()
        else:
            user = connection.User.find_one({'_id': self['user']})
            res = self.sendMail([user['email']])
        return res

    def sendMail(self, emails=[]):
        """
        Send notification by email
        """
        if Notification.is_debug:
            return True

        mconfig = MobyleConfig.get_current()
        if not emails:
            #Send to all users
            users = connection.User.find()
            for user in users:
                emails.append(user['email'])
        try: 
            s = smtplib.SMTP(mconfig['mail']['gateway'])
            if mconfig['mail']['user'] and mconfig['mail']['password']:
                s.login(str(mconfig['mail']['user']),
                        str(mconfig['mail']['password']))
        except Exception as e:
            logging.error("Failed to connect to SMTP gateway: "+str(e))
            return False


        for mail in emails:
            msg = MIMEText(self['message'])
            msg['Subject'] = 'Mobyle notification'
            msg['From'] = mconfig['mail']['origin']
            msg['To'] = mail
            s.sendmail(msg['From'], [mail], msg.as_string())
        s.quit()
        return True
