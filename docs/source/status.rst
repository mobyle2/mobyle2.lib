.. _status:

******
status
******



state diagram of Status 
=======================
.. digraph:: state_diagram

     "INIT" -> "TO_BE_BUILT" -> "BUILDING" -> "TO_BE_SUBMITTED" -> "SUBMITTING" -> "SUBMITTED" -> "UPDATING";
     "UPDATING" -> "RUNNING" ;
     "RUNNING" -> "UPDATING";
     "UPDATING" -> "PENDING";
     "PENDING" -> "UPDATING";
     "UPDATING" -> "HOLD";
     "HOLD" -> "UPDATING";
     "UPDATING" -> "FINISHED ;
     
     "PAUSE" -> "TO_BE_SUBMITTED";
     
     "INIT" -> "KILLED";
     "TO_BE_BUILT" -> "KILLED";
     "TO_BE_SUBMITTED" -> "KILLED";
     "UPDATING" -> "KILLED";
     "PAUSE" -> "KILLED";
     
     "INIT" -> "ERROR";
     "TO_BE_BUILT" -> "ERROR";
     "TO_BE_SUBMITTED" -> "ERROR";
     "UPDATING" -> "ERROR";
     
     "PAUSE" -> "ERROR";
     "UNKNOWN";
     
     
Status API reference     
=====================
.. automodule:: mobyle.common.job
   :members: Status
   :private-members:
   :special-members:
   
