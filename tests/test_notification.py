# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import unittest
import os.path
#a config object must be instantiated first for each entry point of the application
from mobyle.common.config import Config
config = Config( os.path.join( os.path.dirname(__file__), 'test.conf'))

from mobyle.common.connection import connection
from mobyle.common.notifications import Notification

class TestNotification(unittest.TestCase):

    user = None

    def setUp(self):
        connection.Notification.collection.remove({})
        if not TestNotification.user:
            user = connection.User()
            user['first_name'] = "Walter"
            user['last_name'] = "Bishop"
            user['email'] = "Bishop@nomail"
            user.save()
            TestNotification.user = user

    
    def test_new_notification(self):
        my_notif = connection.Notification()
        my_notif['message'] = 'test'
        my_notif['type'] = 0
        my_notif['user'] = TestNotification.user['_id']
        my_notif.save()
        nb_notif = connection.Notification.find().count()
        self.assertTrue(nb_notif==1)


