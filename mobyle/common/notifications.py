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

    NOTIF_TYPE = { 0: 'mobyle',
                   1: 'project',
                   2: 'job',
                   3: 'data'
                 }

    __collection__ = 'notifications'
    __database__ = Config.config().get('app:main', 'db_name')

    structure = {'message': basestring,
                  'user': ObjectId,
                  'type': int,
                  'read': bool
                  'ref': ObjectId # the object the notification refers to (Project, Job, Data)
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
            if self.user_wants_notif(user, 'mail', self['type']):
                res = self.sendMail([user['email']])
        return res

    def user_wants_notif(user, notif_mean, notif_type):
        """
        Checks user preferences to get a notification

        :param user: User to check
        :type user: User
        :param notif_mean: Notif to use (mail)
        :type notif_mean: basestring
        :param notif_type: Type of notif (project, data, ...)
        :type notif_type: int
        :return: bool
        """
        user_pref = notif_mean+'_'+Notification.NOTIF_TYPE[notif_type]
        return user['notifications'][user_pref]

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
