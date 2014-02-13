'''
Initialise database content
'''


import argparse
import sys
from hashlib import sha1
from random import randint
import bcrypt

from mobyle.common.config import Config

parser = argparse.ArgumentParser(description='Initialize database content.')
parser.add_argument('--config')
parser.add_argument('--rootpwd')

args = parser.parse_args()

if not args.config:
    print "config argument is missing"
    sys.exit(2)

# Init config
my_config = Config(args.config).config()

# Init connection
from mobyle.common.connection import connection as conn
from mobyle.common import *


# Create root user
if conn.User.find({'first_name': 'root'}).count() == 0:
    if args.rootpwd:
        pwd = args.rootpwd
    else:
        pwd = sha1("%s" % randint(1, 1e99)).hexdigest()
    Config.logger().warn('root user created with password: ' + pwd)
    user = conn.User()
    user['first_name'] = 'root'
    user['last_name'] = 'root'
    user['email'] = my_config.get("app:main", 'root_email')
    user['hashed_password'] = pwd
    user['admin'] = True
    user['type'] = 'registered'
    user['groups'] = ['admin']
    hashed = bcrypt.hashpw(user['hashed_password'], bcrypt.gensalt())
    user['hashed_password'] = hashed
    user.save()

    # Create default project for root
    project = conn.Project()
    project['name'] = 'admin_project'
    project['owner'] = user['_id']
    project['users'].append({'user': user['_id'], 'role': u'manager'})
    project['public'] = True
    project.save()

    user['default_project'] = project['_id']
    user.save()

# create indexes
db_name = my_config.get('app:main', 'db_name')
for document_name, obj in conn._registered_documents.iteritems():
    Config.logger().warn("generate index for collection %s"
                         % obj._obj_class.__name__)
    obj.generate_index(conn[db_name][obj._obj_class.__collection__])

#Create default config
if conn.MobyleConfig.find().count() == 0:
    Config.logger().warn("creating default mobyle config ")
    cf = conn.MobyleConfig()
    cf['active'] = True
    cf.save()

