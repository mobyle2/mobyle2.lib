# -*- coding: utf-8 -*-

import datetime
import os
import pygeoip

from mongokit import Document

import mobyle.common
from mobyle.common import session
from mobyle.common.config import Config


class Statistic(Document):
    """
    Empty class for the moment, only used as reference
    """

    gi = pygeoip.GeoIP(os.path.dirname(os.path.realpath(__file__))+'/GeoIP.dat',pygeoip.MEMORY_CACHE)

    __collection__ = 'statistics'
    __database__ = Config.config().get('app:main','db_name')

    structure = { 'timestamp' : datetime.datetime, 'total' : int , 'jobs' : [ { 'name' : basestring , 'total' : int } ], 'location' : [ { 'name' : basestring , 'total' : int } ], 'year' : int, 'month' : int, 'hour' : int }


class HourlyStatistic(Statistic):

    __collection__ = 'hourlystatistics'
    
    def add(self,job,location):
        import datetime
        date = datetime.datetime.utcnow()
        timestamp = datetime.datetime(date.year, date.month,date.day)
        year = date.year
        month = date.month
        day = date.day
        hour = date.hour
        location = HourlyStatistic.gi.country_code_by_name('131.254.158.45')
        timestamp = datetime.datetime(year, month,day,hour)
        return mobyle.common.session.HourlyStatistic.find_and_modify({'timestamp': timestamp}, {'$set':{ 'year' : year, 'month' : month, 'day' : day, 'hour' : hour}}, { '$inc' : { 'total' : 1, 'jobs.'+job : 1, 'location.'+location : 1 } },  { 'upsert' : True })

class DailyStatistic(Statistic):

    __collection__ = 'dailystatistics'

class MonthlyStatistic(Statistic):

    __collection__ = 'monthlystatistics'


'''
timestamp = datetime.datetime(date.year, date.month,1)
facts_monthly.update({ "_id" : str(timestamp)},{ "$inc" : { "total" :  1, "jobs.
"+jobname : 1 , "authenticated" : isauthenticated }, "$set" : { "year" : date.ye
ar, "month" : date.month, "timestamp" : timestamp } },True)

timestamp = datetime.datetime(date.year, date.month,date.day)
facts_daily.update({ "_id" : str(timestamp)},{ "$inc" : { "total" :  1, "jobs."+
jobname : 1 , "authenticated" : isauthenticated }, "$set" : { "year" : date.year
, "month" : date.month, "timestamp" : timestamp } },True)
'''
