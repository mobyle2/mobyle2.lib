from mobyle.common.users import User
from mobyle.common.project import Project
from mobyle.common.mobyleConfig import MobyleConfig
from mobyle.common.job import Job
from mongokit import Connection

from mobyle.common import session
from mobyle.common.config import Config

import logging


def init_mongo(server):
    '''Reset connection to mongodb using MongoKit. Register objects for MongoKit

    :param server: URL to mongo server
    :type server: str

    '''
    global session
    session = Connection(server)
    session.register([User, Project, MobyleConfig, Job])

