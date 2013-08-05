# -*- coding: utf-8 -*-

#===============================================================================
#   Created on Aug 13, 2012           
#                                     
# @author: Bertrand Néron              
# @contact: bneron@pasteur.fr          
# @organization: Institut Pasteur      
# @license: GPLv3                      
#===============================================================================

from mongokit import Document, CustomType 
from mongokit.database import Database
from mongokit.collection import Collection

import datetime
from mf.annotation import mf_decorator
import inspect
import types
import logging
_log = logging.getLogger(__name__)

from .config import Config
from .connection import connection
from .mobyleError import MobyleError

class MetatStatus(type):
    
    def __init__(cls, name, bases, classdict ): 
        cls.all_states = [attr[1] for attr in inspect.getmembers( cls ) if type(attr[1]) == types.UnicodeType]
        
class Status(object):
    """reflect the different steps of a job life"""
    __metaclass__ = MetatStatus
    
    UNKNOWN = u'unknown'
    """the system is not able to determine the status of the job"""
    INIT = u'init'
    """init the job creation (working directory creation, job settings,...) the status changed for BUILDING when the user click on "run" """
    BUILDING = u'building'
    """the environment of the job is building ( building command line, ...)"""
    TO_BE_SUBMITTED = u'to be submitted'
    """The job is ready to be handle by the execution engine"""
    SUBMITTED = u'submitted'
    """the job has been submitted to the execution system"""
    PENDING = u'pending'
    """the job is pending in the execution system note that some system cannot pend a job (SYS)"""
    RUNNING = u'running'
    """the job is running"""
    FINISHED = u'finished'
    """the job is completed without error"""
    ERROR = u'error'
    """an error occurred the job is stopped"""
    KILLED = u'killed'
    """the job was stopped by an administrator or the user"""
    HOLD = u'hold'
    """the job is hold by the execution system"""
    PAUSE = u'pause'
    """the job is suspended by the user. when the user resume a paused job the status become TO_BE_SUBMITTED"""
        
    _transitions = {
                    UNKNOWN : [],
                    INIT : [BUILDING, ERROR, KILLED, UNKNOWN],
                    BUILDING : [TO_BE_SUBMITTED, ERROR ,KILLED, UNKNOWN],
                    TO_BE_SUBMITTED : [SUBMITTED, ERROR ,KILLED, UNKNOWN],
                    SUBMITTED : [PENDING, ERROR, KILLED, UNKNOWN],
                    PENDING : [RUNNING, ERROR, KILLED, UNKNOWN],
                    RUNNING : [FINISHED, ERROR, KILLED, UNKNOWN],
                    FINISHED : [],
                    ERROR : [],
                    KILLED : [],
                    HOLD : [RUNNING, ERROR, KILLED, UNKNOWN],
                    PAUSE : [TO_BE_SUBMITTED, ERROR, KILLED, UNKNOWN]
                    }
    
       
    def __init__(self, state):
        if state in self.all_states :
            self._state = state
        else:
            raise MobyleError("invalid state: %s " % state)
    
    @property
    def state(self):
        return self._state
     
    @state.setter        
    def state(self, state): 
        if not state in self.all_states:
            raise MobyleError("invalid state: %s " % state)
        if state in self._transitions[self._state]:
            self._state = state
        else:
            raise MobyleError("transition from '%s' to '%s' is not allowed" % (self._state, state) ) 
        
    def __eq__(self , other):
        """
        two Status instances are equals if there states are equals
        
        :return: True if this object is equal to the other, False otherwise
        :rtype: boolean
        """
        if isinstance(other, Status):
            return self._state == other.state
        else:
            return False
    
    def __ne__(self , other ):
        """
        two Status instances are not equals if they are different states
        
        :return: True if this object is not equal to the other, False otherwise
        :rtype: boolean
        """
        if isinstance(other, Status):
            return self._state != other.state
        else:
            return True
    
    def __str__(self):
        """
        :return: The string representation of a Status instance.
        :rtype: string
        """
        return self._state 
        
    
    def is_ended(self):
        """
        :return: True if the status is among the following ones :
        
                 * "finished", the job is finished without error from Mobyle
                 * "error", the job has failed due to a MobyleError 
                 * "killed", the job has been removed by the user, or killed by the admin
        
        :rtype: boolean
        """
        return self._state in ( self.FINISHED, self.ERROR, self.KILLED )


    def is_on_error(self):
        """
        :return: True if the status is among the following ones :
        
                 * "error", the job has failed due to a MobyleError 
                 * "killed", the job has been removed by the user, or killed by the admin
        
        :rtype: boolean
        """
        return self._state in ( self.ERROR, self.KILLED )

        
    def is_queryable(self):
        """
        :return: True if the status is among the following ones :
        
                 * "submitted", the job.run method has been called
                 * "pending", the job has been submitted to the batch manager but wait for a slot 
                 * "running", the job is running in the batch manager
                 * "hold", the job is hold by the batch manager
        
        :rtype: bool
        
        """
        return self._state in( self.SUBMITTED, self.PENDING, self.RUNNING, self.HOLD )

    
    def is_known(self):
        """
        :return: True if the system know the status of the job, False otherwise
        :rtype: bool
        """
        return self._state != self.UNKNOWN

    
    def is_submittable(self):
        """
        :return: True if the job is ready to be submitted to a batch system.
        :rtype: bool
        """
        return self._state == self.TO_BE_SUBMITTED




class CustomStatus(CustomType):
    
    mongo_type = basestring
    python_type = Status
    
    @staticmethod
    def unserialize(value):
        """
        unserizalize from string to expected format

        :param value: input value
        :type value: string
        :return: a Status corresnonding to this value
        :rtype: :class:`mobyle.common.job.Status` object
        """
        return Status(value)
    
    def to_bson(self, value):
        return unicode(value)
    
    def to_python(self, value):
        if value is not None:
            return Status(value)
    
    def validate(self, value, path):
        return isinstance(value, Status)
    
    
@connection.register
class Job(Document):
    """
    Job is an abstract class that describes the common interface of all jobs
    """     
    use_dot_notation = True
    
    __collection__ = 'jobs'
    __database__ = Config.config().get('app:main','db_name')

    structure = {
                 'name' : basestring,
                 'status' : CustomStatus(),
                 'owner' : basestring,
                 'message' : basestring,
                 'end_time' : datetime.datetime,
                 'has_been_notified' : bool,
                  }

    required_fields = ['status']
    default_values = {'has_been_notified' : False}
    
    def __getstate__(self):
        """
        """
        d = {}
        d['name'] = self.name
        d['status'] = self.status
        d['owner'] = self.owner
        d['message'] = self.message
        d['end_time'] = self.end_time
        d['has_been_notified'] = self.has_been_notified
        d['_id'] = self._id
        return d
    
    def __setstate__(self, state):
        self.connection = connection
        self.db = Database(self.connection, self.__database__)
        self.collection = Collection( self.db, self.__collection__)
                
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
    def create_time(self):
        """
        :return: the time of job creation
        :rtype: datetime.datetime object
        
        :note: _id is available only after first mongokit save
        """
        return self._id.generation_time
    
    
    @property
    def id(self):
        """
        :return: the unique identifier of this job 
        :rtype: 
        """
        return self._id

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
