.. _config:


******
config
******

Each entry point of the application must instantiate a config object with an explicit 
path to a configuration file before any other mobyle module import. 
for instance::

  import mobyle.common.config
  cfg = mobyle.common.config.Config(file = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'development.ini')))

This will create a kind of singleton of the config object, so the other calls to config just return this object. 
If you have a warning like the following message::

   2013-03-14 11:37:08,345 - mobyle - WARNING - No configuration file available, using defaults  

then you need to check carefully the config object.


config API reference
=========================
 .. automodule:: mobyle.common.config
   :members:
   :private-members:
   :special-members:

