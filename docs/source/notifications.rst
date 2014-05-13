.. _mobyleConfig:


************
notifications
************

Notifications are the messages raised by the Mobyle system, the Mobyle
administrator or one of the project members.
Notifications are stored in the database and can be read/managed in the
notification center. According to the preferences, messages will also be sent
via one or more channels (email, ...), according to their type.

Project members can only create project notifications.

Notification sending requires the setup of the mail gateway in the MobyleConfig
configuration.

mobyleConfig API reference
==========================
 .. automodule:: mobyle.common.notifications
   :members: 
   :private-members:
   :special-members:

