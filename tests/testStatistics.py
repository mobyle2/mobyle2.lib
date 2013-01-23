# -*- coding: utf-8 -*-
import unittest
import logging
import pymongo
import mobyle

import json

from mobyle.common  import session

from mobyle.common.stats.stat import HourlyStatistic,DailyStatistic,MonthlyStatistic

from mobyle.common.mobyleConfig import MobyleConfig

import mobyle.common.connection

mobyle.common.connection.init_mongo("mongodb://localhost/")

class TestMobyleStatistics(unittest.TestCase):

    def setUp(self):
       objects = mobyle.common.session.HourlyStatistic.find({})
       for object in objects:
         object.delete()
       
    def tearDown(self):
       objects = mobyle.common.session.HourlyStatistic.find({})
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
        self.assertTrue(stats['total']==3)
        self.assertTrue(stats['jobs']['test1']==2)
    
