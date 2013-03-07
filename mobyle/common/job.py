# -*- coding: utf-8 -*-

import abc

from mongokit import Document, SchemaDocument, IS 
import datetime
import mf.annotation
from mf.annotation import *
import logging
_log = logging.getLogger(__name__)

from mobyleError import MobyleError
from mobyle.common import session
from mobyle.common.config import Config

    

class Status(SchemaDocument):
    """reflect the different steps of a job life"""

    """the system is not able to determine the status of the job"""
    UNKNOWN = u'unknown'
    """the environment of the job is building (working directory creation, building command line, ...)"""
    BUILDING = u'building'
    """the job has been submitted to the execution system to be running"""
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
    
    structure = {
                  'code' : IS(UNKNOWN,
                              BUILDING,
                              SUBMITTED,
                              PENDING,
                              RUNNING,
                              FINISHED,
                              ERROR,
                              KILLED,
                              HOLD,
                              ),
                  'message' : basestring
                  }
    

    
    def __init__(self , code , message = '',
                 doc = None, gen_skel = True, gen_auth_types = True,
                 validate = True, lang = 'en', fallback_lang = 'en'):
        """
        :param code: the code of the status 
        :type code: integer 
        :param string: the code of the status representing by a string
        :type string: string
        :param message: the message associated to the status
        :type message: string
        """
        super(Status , self).__init__( doc = doc, gen_skel = gen_skel, gen_auth_types = gen_auth_types,
                                       validate = validate, lang = lang, fallback_lang = fallback_lang)
        self.code = code

        if message:
            try:
                str( message )
            except Exception , err:
                #s_log.error( "Status received an non valid message: %s : %s"%( message, err ) , exc_info = True )
                raise MobyleError , err
            self.message = message
        else:
            self.message = ''
    
    def __eq__(self , other):
        """
        two Status instances are equals if there code and message are equals
       
        """
        return self.code == other.code and self.message == other.message
    
    def __ne__(self , other ):
        """
        two Status instances are not equals if they are different code or message
       
        """
        return self.code != other.code or self.message != other.message
    
    def __str__(self):
        """
        string representation of a Status instance
       
        """
        return self.code 
        
    
    def is_ended(self):
        """
        :returns: True if the status is among the following ones :
                  * "finished", the job is finished without error from Mobyle
                  * "error", the job has failed due to a MobyleError 
                  * "killed", the job has been removed by the user, or killed by the admin
        
        :rtype: bool
        
        """
        return self.code in ( self.FINISHED, self.ERROR, self.KILLED )

    def is_on_error(self):
        """
        
        :returns: True if the status is among the following ones :
                  * "error", the job has failed due to a MobyleError 
                  * "killed", the job has been removed by the user, or killed by the admin
        
        :rtype: bool
        
        """
        return self.code in ( self.ERROR, self.KILLED )
        
    def is_queryable(self):
        """
        :returns: True if the status is among the following ones :
                 * "submitted", the job.run method has been called
                 * "pending", the job has been submitted to the batch manager but wait for a slot 
                 * "running", the job is running in the batch manager
                 * "hold", the job is hold by the batch manager
        
        :rtype: bool
        
        """
        return self.code in( self.SUBMITTED, self.PENDING, self.RUNNING, self.HOLD )
    
    def is_known(self):
        """if the system know the status of the job
        
        :rtype: bool
        
        """
        return self.code != self.UNKNOWN
    
    def is_submittable(self):
        """:returns: True if the job is ready to be submitted to a batch system :
        
        :rtype: bool
        
        """
        return self.code == self.BUILDING

class AbstractJob(Document):
    """
    AbstractJobRef is an abstract class that describes the common interface of JobRef and WorkflowRef
    """     
    __collection__ = 'jobs'
    __database__ = Config.config().get('app:main','db_name')

    structure = {
                 'name' : basestring,
                 'status' : Status,
                 'owner' : basestring,
                  }
    
    def __init__(self, status, owner, **kwargs):
        """
        :param id: the identifier of this jobRef
        :type id: string
        :param create_time: the time of job creation
        :type create_time: time.struct_time
        :param status: the status of this jobRef
        :type status: `:class:` object
        :param owner: owner id of the job: either a workflow (local|remote) or a userspace (local|remote)
        :type owner: string
        
        """
        super(AbstractJob , self).__init__(**kwargs)
        self._owner = owner
        self.status = status
        
    def __cmp__(self, other):
        """
        :param other: a JobRef I want to comared with self
        :type other: an AbstractJobRef instance
        :returns: negative int if the other object was created before this one, positive integer if other is newer, or 0 if they are created at the same time.
        :rtype: Integer 
        
        """
        return cmp( self.create_time , other.create_time )
    

    @property
    def owner(self):
        """
        :return: the owner of a job. It can be a user space or a workflow
        :rtype: ???
         
        """
        return self.owner
    
    @property
    def create_time(self):
        """
        :returns: the time of job creation
        :rtype: datetime.datetime object
        
        """
        return self["_id"].generation_time
    

    @abc.abstractmethod
    def must_be_notified(self):
        """
        :returns: True if a notification must be send a the end of job. False otherwise 
        
        """
        
        
        
@mf_decorator    
class Job(AbstractJob):
    """
    AbstractJob implementation for a simple job
    """ 
    structure = { 
                'end_time' : datetime,
                'has_been_notified' : bool
                }
    
    def __init__(self, name, status, owner, **kwargs ):
        """
        :param name: the user name of this job
        :type name: string
        :param status: the status of this jobRef
        :type status: L{status} instance
        :param owner: "owner" id of the job: either a workflow( local or remote) or a userspace(local or remote)
        :type owner: ???
        
        """
        super(JobRef , self).__init__(name, status, owner, **kwargs )
        self.end_time = None
        self.has_been_notified = False

    def must_be_notified(self):
        """
        :returns: True if a notification must be send a the end of job. False otherwise 
        
        """
        delay = 60
        if self.end_time:
            return True if self.end_time - self.create_time > delay else False 
        else:
            return False

    
