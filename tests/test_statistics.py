# -*- coding: utf-8 -*-


import logging
import pymongo
import json
import unittest
import os.path
#a config object must be instantiated first for each entry point of the application
from mobyle.common.config import Config
config = Config( os.path.join( os.path.dirname(__file__), 'test.conf'))
from mobyle.common.connection import connection
from mobyle.common.stats.stat import HourlyStatistic, DailyStatistic, MonthlyStatistic


class TestMobyleStatistics(unittest.TestCase):

    def setUp(self):
       objects = connection.HourlyStatistic.find({})
       for object in objects:
           object.delete()
       
    def tearDown(self):
       objects = connection.HourlyStatistic.find({})
       for object in objects:
           object.delete()

    def test_insert(self):
        stat = connection.HourlyStatistic()
        status = stat.add('test1','188.224.22.213')
        status = stat.add('test1','188.224.22.213')
        status = stat.add('test2','188.224.22.213')
        stats = connection.HourlyStatistic.find_one()
        for s in stats:
            logging.debug(str(s))
        self.assertEqual(stats['total'], 3)
        self.assertEqual(stats['jobs']['test1'], 2)
    
