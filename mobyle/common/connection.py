from mongokit import Connection

from mobyle.common import session
from mobyle.common.config import Config
import mobyle.common

import logging



def init_mongo(server):
    '''Reset connection to mongodb using MongoKit. Register objects for MongoKit

    :param server: URL to mongo server
    :type server: str

    '''
    session = Connection(server)
    from mobyle.common.users import User
    from mobyle.common.project import Project
    from mobyle.common.mobyleConfig import MobyleConfig
    from mobyle.common.job import Job
    from mobyle.common.service import Service
    session.register([User, Project, MobyleConfig, Job, Service])
    mobyle.common.session = session

