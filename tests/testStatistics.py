# -*- coding: utf-8 -*-
import unittest

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
        print('test '+str(stat))
        status = stat.add('test1','188.224.22.213')
        print str(status)
        assertTrue(1==0)
    
