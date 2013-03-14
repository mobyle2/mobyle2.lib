# -*- coding: utf-8 -*-

#===============================================================================
#   Created on Aug 13, 2012           
#                                     
# @author: Bertrand Néron              
# @contact: bneron@pasteur.fr          
# @organization: Institut Pasteur      
# @license: GPLv3                      
#===============================================================================

from mongokit import Document, SchemaDocument, IS 
import datetime
from mf.annotation import mf_decorator
import inspect
import types
import logging
_log = logging.getLogger(__name__)

from .config import Config
from .connection import connection
from .mobyleError import MobyleError


class Status(SchemaDocument):
    """reflect the different steps of a job life"""

    use_dot_notation = True
    
    """the system is not able to determine the status of the job"""
    UNKNOWN = u'unknown'
    """init the job creation (working directory creation, job settings,...) the status changed for BUILDING when the user click on "run" """
    INIT = u'init'
    """the environment of the job is building ( building command line, ...)"""
    BUILDING = u'building'
    """The job is ready to be handle by the execution engine"""
    TO_BE_SUBMITTED = u'to be submitted'
    """the job has been submitted to the execution system"""
    SUBMITTED = u'submitted'
    """the job is pending in the execution system note that some system cannot pend a job (SYS)""" 
    PENDING = u'pending'
    """the job is running"""
    RUNNING = u'running'
    """the job is completed without error"""
    FINISHED = u'finished'
    """an error occurred the job is stopped"""
    ERROR = u'error'
    """the job was stopped by an administrator or the user"""
    KILLED = u'killed'
    """the job is hold by the execution system"""
    HOLD = u'hold'
    """the job is suspended by the user. when the user resume a paused job the status become TO_BE_SUBMITTED"""
    PAUSE = u'pause'
        
    structure = {
                  'code' : IS(UNKNOWN,
                              INIT,
                              BUILDING,
                              TO_BE_SUBMITTED,
                              SUBMITTED,
                              PENDING,
                              RUNNING,
                              FINISHED,
                              ERROR,
                              KILLED,
                              HOLD,
                              PAUSE
                              )
                  }
    
    required_fields = ['code']
    
    def __init__(self, **kwargs):
        if not 'code' in kwargs:
            raise MobyleError( "keyword code is mandatory to instanciate a Status")
        auth_values = [  m[1] for m in inspect.getmembers( Status ) if type(m[1]) == types.UnicodeType ]
        if kwargs['code'] not in  auth_values:
            raise MobyleError( "keyword code must be in %s" % auth_values )
        self.code = kwargs['code']
        
        
    def __eq__(self , other):
        """
        two Status instances are equals if there code and message are equals
        
        :return: True if this object is equal to the other, False otherwise
        :rtype: boolean
        """
        return self.code == other.code

    
    def __ne__(self , other ):
        """
        two Status instances are not equals if they are different code
        
        :return: True if this object is not equal to the other, False otherwise
        :rtype: boolean
        """
        return self.code != other.code

    
    def __str__(self):
        """
        :return: The string representation of a Status instance.
        :rtype: string
        """
        return self.code 
        
    
    def is_ended(self):
        """
        :return: True if the status is among the following ones :
        
                 * "finished", the job is finished without error from Mobyle
                 * "error", the job has failed due to a MobyleError 
                 * "killed", the job has been removed by the user, or killed by the admin
        
        :rtype: boolean
        """
        return self.code in ( self.FINISHED, self.ERROR, self.KILLED )


    def is_on_error(self):
        """
        :return: True if the status is among the following ones :
        
                 * "error", the job has failed due to a MobyleError 
                 * "killed", the job has been removed by the user, or killed by the admin
        
        :rtype: boolean
        """
        return self.code in ( self.ERROR, self.KILLED )

        
    def is_queryable(self):
        """
        :return: True if the status is among the following ones :
        
                 * "submitted", the job.run method has been called
                 * "pending", the job has been submitted to the batch manager but wait for a slot 
                 * "running", the job is running in the batch manager
                 * "hold", the job is hold by the batch manager
        
        :rtype: bool
        
        """
        return self.code in( self.SUBMITTED, self.PENDING, self.RUNNING, self.HOLD )

    
    def is_known(self):
        """
        :return: True if the system know the status of the job, False otherwise
        :rtype: bool
        """
        return self.code != self.UNKNOWN

    
    def is_submittable(self):
        """
        :return: True if the job is ready to be submitted to a batch system.
        :rtype: bool
        """
        return self.code == self.BUILDING



class Job(Document):
    """
    Job is an abstract class that describes the common interface of all jobs
    """     
    use_dot_notation = True
    
    __collection__ = 'jobs'
    __database__ = Config.config().get('app:main','db_name')

    structure = {
                 'name' : basestring,
                 'status' : Status,
                 'owner' : basestring,
                 'message' : basestring,
                 'end_time' : datetime.datetime,
                  }

    required_fields = ['status']
    
        
    def __cmp__(self, other):
        """
        :param other: a :class:`mobyle.common.job.Job` object I want to comared with self
        :type other: an AbstractJobRef instance
        :return: negative int if the other object was created before this one, 
                 positive integer if other is newer, or 0 if they are created at the same time.
        :rtype: Integer 
        """
        return cmp( self.create_time , other.create_time )


    @property
    def owner(self):
        """
        :return: the owner of a job. It can be a user space or a workflow
        :rtype: ???
         
        """
        return self._owner

    
    @property
    def create_time(self):
        """
        :return: the time of job creation
        :rtype: datetime.datetime object
        """
        return self._id.generation_time
    

    def must_be_notified(self):
        """
        :return: True if a notification must be send a the end of job. False otherwise 
        :rtype: boolean
        """
        return NotImplementedError
        
        
@mf_decorator   
@connection.register
class ClJob(Job):
    """
    Job implementation for a Command line  job
    """ 
    
    use_dot_notation = True
    
    structure = { 
                'has_been_notified' : bool
                }
    
    def must_be_notified(self):
        """
        :return: True if a notification must be send a the end of job. False otherwise 
        :rtype: bool
        """
        delay = 60
        if self.end_time:
            return True if self.end_time - self.create_time > delay else False 
        else:
            return False

    
@mf_decorator   
@connection.register
class WorkflowJob(Job):
    """
    not implemented for now
    """
    pass
