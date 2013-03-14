.. _connection:


**********
connection
**********

Create a new MongoKit class
===========================

   #. Create your class using MongoKit syntax ;-)
   #. import object connection from the ``mobyle.common.connection`` module.
   #. to register the class in mongokit add the decorator ``@connection.register``
   #. if you need to use an object from mongokit you need to import the corresponding module. The registration of the class in the mongokit connection is made at the import step.
   #. If object need to be added to the web dashboard, on ``mobyle.web://mobyle/web/__init__.py``, add the decorator ``@mf_decorator`` to your class.

for instance ::

    from mongokit import Document
    from mf.annotation import mf_decorator

    from .connection import connection
    from .config import Config

    @mf_decorator
    @connection.register
    class User(Document):

        __collection__ = 'users'
        __database__ = Config.config().get('app:main','db_name')

How to use a MongoKit class
===========================

Following an example to retrieve User object in mongodb. 
If the module is an entry point of the application then instantiate a config object with a the path of a configuration file::

   from mobyle.common.config import Config
   config = Config( os.path.join( os.path.dirname(__file__), 'test.conf'))

Import the Mongokit connection object::

   from mobyle.common.connection import connection

By importing users all class in users which are decorated with @connection.register are registered in connection::

   from mobyle.common import users

Use Mongokit to retrieve User::

   objects = connection.User.find({})


connection API reference
=========================
 .. automodule:: mobyle.common.connection
   :members:
   :private-members:
   :special-members:

