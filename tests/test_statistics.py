# -*- coding: utf-8 -*-


import logging
import pymongo
import mobyle
import json

from abstract_test import AbstractMobyleTest
from mobyle.common  import session
from mobyle.common.stats.stat import HourlyStatistic,DailyStatistic,MonthlyStatistic
from mobyle.common.mobyleConfig import MobyleConfig
import mobyle.common.connection
from mobyle.common.config import Config
mobyle.common.connection.init_mongo(Config.config().get('app:main','db_uri'))

class TestMobyleStatistics(AbstractMobyleTest):

    def setUp(self):
       objects = mobyle.common.session.User.find({})
       for object in objects:
           object.delete()
       
    def tearDown(self):
       objects = mobyle.common.session.User.find({})
       for object in objects:
           object.delete()

    def test_insert(self):
        stat = mobyle.common.session.HourlyStatistic()
        status = stat.add('test1','188.224.22.213')
        status = stat.add('test1','188.224.22.213')
        status = stat.add('test2','188.224.22.213')
        stats = mobyle.common.session.HourlyStatistic.find_one()
        for s in stats:
            logging.debug(str(s))
        self.assertEqual(stats['total'], 3)
        self.assertEqual(stats['jobs']['test1'], 2)
    
if __name__ == '__main__':
    import unittest
    unittest.main()
