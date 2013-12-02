.. _objectmanager:


**************
Object Manager
**************

The ObjectManager makes use of an *options* dict to specify the current options to
manage the file(s):

    options[‘project’] = id of the project, as str
    options[‘uncompress’] = bool , is the base file an archive uncompressed
    if uncompress is True:
        options[‘name’] = name of the base file (‘test.zip’ for ex) to detect the unarchiver to use
        options[‘group’] = bool , if uncompress is True, should all files be a single dataset or one dataset per file (group of files or independent files)
       options[‘files’] = list of file paths to copy in the dataset(s) according to group
    else:
        options[‘file’] = path to the file to copy in the dataset

    options[‘format’] = EDAM format or “auto” . If auto, a call to BioFormat detector will be done to try to detect the format and type
    options[‘type’] = EDAM type

Create one dataset in the pairtree
=================================

To create a projectdata from a file available on local filesystem::

    options = {}
    options['project'] = project_id  # as str

    # optional set status to go directly in STATUS instead of QUEUED
    # options["status"] = READY

    my_dataset = ObjectManager.add("my file name", options, is_persistent)
    # now, my dataset status is "QUEUED"

    # Get path to the objects
    my_path = my_dataset.get_file_path() 
    ...
    write file(s) in my_path
    ...
    # Update the schema according to the files, example:
    my_schema = RefData()
    my_schema[‘path’] = relative_path_in_directory
    my_schema[‘size’] = size_of_the_data_element
    my_schema[‘format’] = "EDAM:..."
    my_schema[‘type’] = "EDAM:..."

    my_dataset.schema(my_schema)
    my_dataset.status(ObjectManager.READY)

    my_dataset.save_with_history([ List_of_new_or_updated_relative_files_path ], "message why")

Create one dataset with data in an existing directory
=====================================================

If the project data must refer to a data located i a specific place, but should
not be copied::

    options = {}
    options['type'] = "EDAM:.."
    options['format'] = "EDAM:..."
    options['project'] = project_id

    options["path"] = path_to_my_job_result_dir # for example

    // Optionally set the schema
    options["schema"] = StructData(....) or RefData or … (the schema defining the data)
    my_dataset = ObjectManager.add("my file name", options, is_persistent)

    # Will return path_to_my_job_result_dir
    my_path = my_dataset.get_file_path() 

    ...
    # Update the schema according to the files
    my_dataset.schema(my_schema)

    my_dataset.status(ObjectManager.READY)

    my_dataset.save_with_history([ List_of_new_or_updated_relative_files_path ], "message why")

Get/update dataset/ dataset info
================================

To get an existing dataset (ProjectData) ::

    my_dataset = ObjectManager.get(my_dataset_id) #to get an existing dataset
    ...
    my_path = my_dataset.get_file_path() 
    # write new files, delete ,... in path
    ....
    # Update the schema according to the files
    my_dataset.schema(my_schema)

    my_dataset.save_with_history([ List_of_new_or_updated_relative_files_path ], "message why")

Delete dataset
==============

Delete dataset in data and all data in the pairtree
If *path* is set (data not in pairtree), data are not deleted ::

     ObjectManager.delete(my_dataset_id)

Request a token
===============

To request a token for limited access in time to a file ::

    my_token = manager.get_token(my_dataset_id, file_path, AccessMode.READ or AccessMode.READWRITE)  

This will grant access to token *my_token* during a default period with READ or
WRITE access.

ObjectManager API reference
=========================
 .. automodule:: mobyle.common.objectmanager
   :members:
   :private-members:
   :special-members:

