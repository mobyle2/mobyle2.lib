.. _status:

******
status
******



state diagram of Status 
=======================
.. digraph:: state_diagram

     "INIT" -> "BUILDING" -> "TO_BE_SUBMITTED" -> "SUBMITTED";
     "SUBMITTED" -> "PENDING";
     "SUBMITTED" -> "RUNNING";
     "SUBMITTED" -> "HOLD";
     "SUBMITTED" -> "PAUSE";
     "RUNNING" -> "PAUSE"
     "PAUSE" -> "TO_BE_SUBMITTED";
     "RUNNING" -> "HOLD";
     "HOLD" -> "RUNNING";
     "RUNNING" -> "FINISHED";
     "INIT" -> "KILLED";
     "BUILDING" -> "KILLED";
     "TO_BE_SUBMITTED" -> "KILLED";
     "SUBMITTED" -> "KILLED";
     "PENDING" -> "KILLED";
     "PENDING" -> "RUNNING";
     "RUNNING" -> "KILLED";
     "HOLD" -> "KILLED";
     "PAUSE" -> "KILLED";
     "INIT" -> "ERROR";
     "BUILDING" -> "ERROR";
     "TO_BE_SUBMITTED" -> "ERROR";
     "SUBMITTED" -> "ERROR";
     "PENDING" -> "ERROR";
     "RUNNING" -> "ERROR";
     "HOLD" -> "ERROR";
     "PAUSE" -> "ERROR";
     "UNKNOWN";
     
     
Status API reference     
=====================
.. automodule:: mobyle.common.job
   :members: Status
   :private-members:
   :special-members:
   
