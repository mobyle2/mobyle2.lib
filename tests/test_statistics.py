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
from mobyle.common.stats.stat import HourlyStatistic, DailyStatistic, MonthlyStatistic, Statistic, ServiceUsageStatistic


class TestMobyleStatistics(unittest.TestCase):

    def setUp(self):
       connection.HourlyStatistic.collection.remove({})
       connection.ServiceUsageStatistic.collection.remove({})

    def test_insert(self):
        status = Statistic.add('test1','188.224.22.213')
        status = Statistic.add('test1','188.224.22.213')
        status = Statistic.add('test2','188.224.22.213')
        stats = connection.HourlyStatistic.find_one()
        for s in stats:
            logging.debug(str(s))
        self.assertEqual(stats['total'], 3)
        self.assertEqual(stats['jobs']['test1'], 2)

    def test_serviceusage(self):
        ServiceUsageStatistic.add('test1', 'test2')
        ServiceUsageStatistic.add('test1', 'test2')
        ServiceUsageStatistic.add('test1', 'test3')
        stats = connection.ServiceUsageStatistic.find_one({'service': 'test1'})
        self.assertEqual(stats['follows']['test2'], 2)
        self.assertEqual(stats['follows']['test3'], 1)
    
