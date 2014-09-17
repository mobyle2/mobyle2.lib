# -*- coding: utf-8 -*-

import datetime
import os
import pygeoip

from mongokit import Document
import logging

from ..connection import connection
from ..config import Config

@connection.register
class ServiceUsageStatistic(Document):
    """
    Service statistics

    Collects usage info on which service is used after an other service
    """

    __collection__ = 'serviceusage'
    __database__ = Config.config().get('app:main','db_name')

    structure = { 'service': basestring, 'follows': None }

    @classmethod
    def add(cls, service, next_service):
        """
        Add a new usage statistic

        :param service: name of the service
        :type service: str
        :param next_service: name of the following service
        :type next_service: str
        """
        connection.ServiceUsageStatistic.find_and_modify({'service': service},
            {'$inc' : { 'follows.'+next_service : 1 }},
            { 'upsert' : True })


class Statistic(Document):
    """
    Base statistic to create time related statistics.
    """

    gi = pygeoip.GeoIP(os.path.dirname(os.path.realpath(__file__))+'/GeoIP.dat',pygeoip.MEMORY_CACHE)

    __collection__ = 'statistics'
    __database__ = Config.config().get('app:main','db_name')

    structure = { 'timestamp' : datetime.datetime, 'total' : int , 'jobs' :  {
    } , 'location' :  {  } , 'year' : int, 'month' : int, 'hour' : int }

    @classmethod
    def add(cls,job,location):
        """
        Add a new stat for the job (hourly/daily/monthly).

        :param job: job name e.g. service name
        :type job: str
        :param location: IP address of the user
        :type location: str
        """
        HourlyStatistic.add(job,location)
        DailyStatistic.add(job,location)
        MonthlyStatistic.add(job,location)


@connection.register
class HourlyStatistic(Statistic):

    __collection__ = 'hourlystatistics'

    @classmethod
    def add(cls,job,location):
        import datetime
        date = datetime.datetime.utcnow()
        timestamp = datetime.datetime(date.year, date.month,date.day,date.hour)
        year = date.year
        month = date.month
        day = date.day
        hour = date.hour
        location = HourlyStatistic.gi.country_code_by_name(location)
        timestamp = datetime.datetime(year, month,day,hour)
        connection.HourlyStatistic.find_and_modify({'timestamp': timestamp}, {'$set':{ 'year' : year, 'month' : month, 'day' : day, 'hour' : hour}, '$inc' : { 'total' : 1, 'jobs.'+job : 1, 'location.'+location : 1 } },  { 'upsert' : True })


@connection.register
class DailyStatistic(Statistic):

    __collection__ = 'dailystatistics'

    @classmethod
    def add(cls,job,location):
        import datetime
        date = datetime.datetime.utcnow()
        timestamp = datetime.datetime(date.year, date.month,date.day)
        year = date.year
        month = date.month
        day = date.day
        hour = 0
        location = DailyStatistic.gi.country_code_by_name(location)
        timestamp = datetime.datetime(year, month,day,hour)
        connection.DailyStatistic.find_and_modify({'timestamp': timestamp}, {'$set':{ 'year' : year, 'month' : month, 'day' : day, 'hour' : hour}, '$inc' : { 'total' : 1, 'jobs.'+job : 1, 'location.'+location : 1 } },  { 'upsert' : True })


@connection.register
class MonthlyStatistic(Statistic):

    __collection__ = 'monthlystatistics'

    @classmethod
    def add(cls,job,location):
        import datetime
        date = datetime.datetime.utcnow()
        timestamp = datetime.datetime(date.year, date.month,date.day)
        year = date.year
        month = date.month
        day = 1
        hour = 0
        location = MonthlyStatistic.gi.country_code_by_name(location)
        timestamp = datetime.datetime(year, month,day,hour)
        connection.MonthlyStatistic.find_and_modify({'timestamp': timestamp}, {'$set':{ 'year' : year, 'month' : month, 'day' : day, 'hour' : hour}, '$inc' : { 'total' : 1, 'jobs.'+job : 1, 'location.'+location : 1 } },  { 'upsert' : True })


