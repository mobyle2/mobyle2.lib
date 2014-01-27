'''
This module manages object storage
'''
from pairtree import PairtreeStorageFactory

import traceback
import sys
import re
import pairtree
import logging
import os

import mobyle.common
from mobyle.common.connection import connection
from mobyle.common.config import Config
from mobyle.common.data import RefData, ListData, StructData
from mobyle.common import tokens

from bson.objectid import ObjectId

from git import Repo

from copy import deepcopy

from mobyle.common.detector import BioFormat


class AccessMode:
    """
    Defines the mode of access to a data
    """

    READONLY = 0
    READWRITE = 1


class ObjectManager:
    """
    Manager for datasets.

    This class store files in a pairtree filesystem and
    update status of objects in database.
    """

    storage = None
    # Git repo
    repo = None
    use_repo = False

    QUEUED = 0
    DOWNLOADING = 1
    DOWNLOADED = 2
    READY = 2
    UNCOMPRESS = 3
    FORMATCHECKING = 4
    ERROR = 5
    UNCOMPRESSED = 6
    SYMLINK = 7

    FILEROOT = 'data'

    def __init__(self):
        config = Config.config()
        logging.debug("store = " + str(ObjectManager.storage) +
            ", set to " + config.get("app:main", "store"))

        if config.has_option("app:main", "use_history"):
            ObjectManager.use_repo = config.getboolean("app:main",
                                                       "use_history")
        else:
            ObjectManager.use_repo = False

        if ObjectManager.storage is None:
            config = Config.config()
            fstore = PairtreeStorageFactory()
            ObjectManager.storage = fstore.get_store(
                store_dir=config.get("app:main", "store"), uri_base="http://")
            logging.debug("store = " + str(config.get("app:main", "store")))
            #if ObjectManager.use_repo:
            #    ObjectManager.repo = Repo.init(self.get_storage_path())

    @classmethod
    def _get_file_root(cls, uid):
        '''Get the file root to append to the pairtree path
        '''
        return ObjectManager.FILEROOT + '.' + uid

    @classmethod
    def get_repository(cls, uid):
        '''Get repository for the file. If it does not exists,
        create it. There is one repo per file path.

        :param uid: uid of the dataset
        :type uid: str
        :return: Repo for this dataset
        '''
        repo = ObjectManager.get_storage_path() + \
            pairtree.id2path(uid) + '/' + ObjectManager._get_file_root(uid)
        if not os.path.exists(repo + "/.git"):
            repository = Repo.init(repo)
        else:
            repository = Repo(repo)
        return repository

    @classmethod
    def get_repository_index(cls, uid):
        ''' Get repository index'''
        return ObjectManager.get_repository(uid).index

    @classmethod
    def get_storage_path(cls):
        '''Get path to the storage'''
        config = Config.config()
        return config.get("app:main", "store") + "/pairtree_root/"

    @classmethod
    def get_file_path(cls, uid):
        '''Get full path for a file uid'''
        return ObjectManager.get_storage_path() + pairtree.id2path(uid) + \
            "/" + ObjectManager._get_file_root(uid)

    @classmethod
    def get_relative_file_path(cls, uid):
        '''Get path for a file uid, relative to pairtree root'''
        return pairtree.id2path(str(uid)) + "/" + \
        ObjectManager._get_file_root(str(uid))

    @classmethod
    def get(cls, uid):
        '''
        Gets a dataset from its uid

        :param uid: Id of the dataset
        :type uid: basestring
        :return: ProjectData
        '''
        uid = str(uid)
        return connection.ProjectData.find_one({"_id": ObjectId(uid)})

    @classmethod
    def get_token(cls, uid, files_path,
                  mode=AccessMode.READONLY, lifetime=3600):
        '''
        Return a temporary token to serve a dataset file

        :param uid: Id of the dataset
        :type uid: basestring
        :param files_path: relative path to the files in the dataset
        :type files_path: list
        :param mode: allowed access mode
        :type mode: AccessMode.READONLY, AccessMode.READWRITE
        :param lifetime: duration of the token in seconds
        :type lifetime: int
        :return: basetring, token
        '''
        uid = str(uid)
        temptoken = connection.Token()
        temptoken.generate(lifetime)
        token_data = dict()
        token_data['id'] = uid
        token_data['file'] = files_path
        token_data['access'] = mode
        temptoken['data'] = token_data
        temptoken.save()
        return temptoken['token']

    @classmethod
    def _delete_file_only(cls, uid, path):
        '''
        Delete a file from a dataset, but does not delete dataset entry nor
        directory. Typical use case is a file replacement

        :param uid: id of the dataset
        :type uid: str
        :param path: relative path of the file
        :type path: str
        '''
        full_path = os.path.join(ObjectManager.get_file_path(uid), path)
        if os.path.exists(full_path):
            os.remove(os.path.join(ObjectManager.get_file_path(uid), path))
            if ObjectManager.use_repo:
                index = ObjectManager.get_repository_index(uid)
                index.remove([path])
                msg = "File removed: " + path.encode('utf8', 'replace')
                index.commit(msg)

    @classmethod
    def _delete_file(cls, uid, options=None):
        '''
        Delete file from storage directly or via repo
        '''
        obj = ObjectManager.storage.get_object(uid)
        #if ObjectManager.use_repo and not options['uncompress']:
        #    index = ObjectManager.get_repository_index(uid)
        #    index.remove([uid])
        #    if 'msg' in options:
        #        msg = options['msg']
        #    else:
        #        msg = "File removed"
        #    index.commit(msg + " " + options['name'])
        obj.del_path(ObjectManager._get_file_root(uid), True)

    @classmethod
    def delete(cls, uid, options=None):
        '''
        Delete a file from storage and database

        :param uid: Name of the file (uid)
        :type uid: str
        '''
        uid = str(uid)
        if options is None:
            options = {}
        if 'uncompress' not in options:
            options['uncompress'] = False
        dataset = None
        try:
            dataset = connection.ProjectData.find_one({"_id": ObjectId(uid)})
            if dataset is not None:
                if 'path' in dataset and dataset['path']:
                    dataset.delete()
                    return
                # Else remove all data in dataset
                ObjectManager._delete_file(uid, options)
        except Exception:
            logging.error("Error while trying to delete ")
            traceback.print_exc(file=sys.stdout)
        if dataset is not None:
            dataset.delete()

    @classmethod
    def add(cls, name, options=None, persistent=True):
        '''
        Adds a new dataset in status queued

        :param name: name fo the file
        :type name: str
        :param options: options related to file (project,...)
        :type options: dict with

            name: name of the file
            status: ObjectManager status
            project: id of the project
            path (optional): path the data, data is not stored in pairtree.

        :return: data database id
        '''
        if options is None:
            options = {'uncompress': False}
        if 'uncompress' not in options:
            options['uncompress'] = False
        Config.config()
        dataset = connection.ProjectData()
        if 'schema' in options:
            dataset['data'] = options['schema']
        else:
            dataset['data'] = RefData()
        dataset['name'] = name
        if 'description' in options:
            dataset['description'] = options['description']
        if 'public' in options:
            dataset['public'] = options['public']
        dataset['status'] = ObjectManager.QUEUED
        if 'path' in options:
            dataset['path'] = options['path']
        dataset['persistent'] = persistent
        if 'project' in options:
            dataset['project'] = ObjectId(options['project'])
        dataset.save()
        uid = str(dataset['_id'])
        if ObjectManager.use_repo and not options['uncompress']:
            ObjectManager.get_repository_index(uid)
        #return str(dataset['_id'])
        # Create root storage for the dataset
        ObjectManager.storage.get_object(uid)
        if not os.path.exists(ObjectManager.get_file_path(uid)):
            os.makedirs(ObjectManager.get_file_path(uid))
        return dataset

    @classmethod
    def isarchive(cls, filepath):
        ''' Check if file is a supported archive format

        :param filepath: path of the file
        :type filepath: str
        :return: None if don't match a known/supported archive type
        '''
        filetypes = re.compile('\.(tar\.gz|bz2|zip)')
        return filetypes.search(filepath)

    @classmethod
    def update(cls, status, options):
        '''
        Update the status of the object

        :param status: Status of the  upload/download \
                    (QUEUED,DOWNLOADING,DOWNLOADED,ERROR)
        :type status: int
        :return: list of updated datasets
        '''

        dataset = connection.ProjectData.find_one({"_id":
                                                   ObjectId(options['id'])})
        updated_datasets = [dataset]

        if status == ObjectManager.DOWNLOADED and\
        'uncompress' in options and options['uncompress'] and\
        'name' in options and ObjectManager.isarchive(options['name']):
            status = ObjectManager.UNCOMPRESS

        if status == ObjectManager.SYMLINK:
            options['uncompress'] = False

        if status == ObjectManager.DOWNLOADED or \
             status == ObjectManager.UNCOMPRESSED or \
             status == ObjectManager.SYMLINK:
            # Data is downloaded and eventually uncompressed
            Config.config()
            uid = str(dataset['_id'])
            path = ObjectManager._get_file_root(uid)
            obj = ObjectManager.storage.get_object(uid)
            if options['uncompress'] or len(options['files']) > 1:
                msg = 'Add: '
                if 'msg' in options:
                    msg = options['msg']
                if options['group']:
                    dataset['data'] = ListData()

                else:
                    updated_datasets = []

                dataset['data']['type'] = options['type']

                for filepath in options['files']:
                    if options['group']:
                        # Copy files
                        fullsize = 0
                        with open(filepath, 'rb') as stream:
                            obj.add_bytestream(os.path.basename(filepath),
                                                stream, path)
                        filespath = pairtree.id2path(uid) + '/' + path +\
                                     '/' + os.path.basename(filepath)
                        subdata = RefData()
                        subdata['path'] = os.path.basename(filepath)
                        subdata['name'] = os.path.basename(filepath)
                        subdata['size'] = \
                            os.path.getsize(ObjectManager.get_storage_path() +
                                            filespath)
                        fullsize += subdata['size']
                        subdata['type'] = options['type']
                        dataset['data']['value'].append(subdata)
                        # Update history
                        if ObjectManager.use_repo:
                            index = ObjectManager.get_repository_index(uid)
                            index.add([os.path.basename(filepath)])
                            if 'msg' not in options:
                                msg += os.path.basename(filepath) + ","
                        status = ObjectManager.DOWNLOADED
                        # TODO manage Data object complexity, subdir etc...
                    else:
                        # Create a new data for this file
                        newoptions = deepcopy(options)
                        newoptions['uncompress'] = False
                        newoptions['group'] = False
                        newoptions['id'] = None
                        new_dataset = ObjectManager.store(
                                          os.path.basename(filepath),
                                          filepath, newoptions)
                        updated_datasets.append(new_dataset)
                if not options['group']:
                    # remove current obj, each sub file is a new independant
                    # object
                    ObjectManager.delete(uid, options)
                    # We have managed child object
                    # now we can leave
                    return updated_datasets
                else:
                    # Commit history
                    if ObjectManager.use_repo:
                        index = ObjectManager.get_repository_index(uid)
                        index.commit(msg)

            else:
                file_name = uid
                if 'name' in options and options['name'] is not None:
                    file_name = options['name']

                filepath = os.path.join(dataset.get_file_path(), file_name)
                if status == ObjectManager.SYMLINK:
                    # Not taken into account for quota
                    dataset['data']['size'] = 0
                    if os.path.isdir(options['files'][0]):
                        # Create schema for files in directory
                        symdirfiles = os.listdir(options['files'][0])
                        dataset['data']['value'] = []
                        st_path = ObjectManager.get_storage_path()
                        for symdirfile in symdirfiles:
                            relative_file = os.path.join(file_name, symdirfile)
                            subdata = RefData()
                            subdata['path'] = relative_file
                            subdata['name'] = relative_file
                            subdata['size'] = \
                            os.path.getsize(os.path.join(options['files'][0],
                                            symdirfile))
                            #fullsize += subdata['size']
                            subdata['type'] = dataset['data']['type']
                            dataset['data']['value'].append(subdata)
                    else:
                        dataset['data']['path'] = file_name
                    dir_name = os.path.dirname(filepath)
                    if not os.path.exists(dir_name):
                        os.mkdir(dir_name)
                    os.symlink(options['files'][0], filepath)
                    status = ObjectManager.READY
                else:
                    dataset['data']['path'] = file_name
                    with open(options['files'][0], 'rb') as stream:
                        obj.add_bytestream(file_name, stream, path)
                    dataset['data']['size'] = \
                        os.path.getsize(filepath)

                dataset['data']['type'] = options['type']

                if ObjectManager.use_repo:
                    index = ObjectManager.get_repository_index(uid)
                    index.add([file_name])
                    if 'msg' in options:
                        msg = options['msg']
                    else:
                        msg = "Update file content"
                    index.commit(msg + " " + dataset['name'].encode('utf8',
                                 'replace'))

            if 'project' in options:
                dataset['project'] = ObjectId(options['project'])
            fformat = None
            mime = None

            if 'name' in options:
                dataset['name'] = options['name']
            if 'description' in options:
                dataset['description'] = options['description']
            if 'public' in options:
                dataset['public'] = options['public']

            if options['format'] == 'auto':
                # Try auto-detect
                detector = BioFormat()
                if dataset['data'].__class__.__name__ == 'ListData':
                    for subdata in dataset['data']['value']:
                        fformat = detector.detect_by_extension(subdata['name'])
                        if fformat is not None:
                            break
                    # This is a group, get the path where are the files
                    #datapath = os.path.dirname(dataset['data']['value'][0]['path'])
                    datapath = dataset.get_file_path()
                else:
                    fformat = detector.detect_by_extension(dataset['name'])
                    datapath = os.path.join(dataset.get_file_path(),
                                            dataset['data']['path'])
                if fformat is None:
                    (fformat, mime) = detector.detect(
                                          ObjectManager.get_storage_path() +
                                          datapath)
            else:
                fformat = options['format']

            dataset['data']['format'] = fformat

        dataset['status'] = status
        dataset.save()

        return updated_datasets

    @classmethod
    def store(cls, name, infile, options=None):
        '''
        Adds a new dataset and store input file

        :param name: name fo the file
        :type name: str
        :param infile: Path to the input file
        :type infile: str
        :param options: options related to file (project,...)
        :type options: dict
        :return: dataset
        '''
        dataset = None
        if options is None:
            options = {}
        Config.config()
        if 'id' in options and options['id']:
            dataset = connection.ProjectData.find_one({'_id': ObjectId(
                                                       options['id'])})
            if not 'data' in dataset:
                dataset['data'] = RefData()
            else:
                if 'path' in dataset:
                    # Remove existing file
                    ObjectManager._delete_file_only(options['id'],
                        dataset['data']['path'])
        else:
            dataset = connection.ProjectData()
            dataset['data'] = RefData()
            dataset.save()
        uid = str(dataset['_id'])
        obj = ObjectManager.storage.get_object(uid)
        file_name = uid
        if 'name' in options and options['name'] is not None:
            file_name = options['name']
        with open(infile, 'rb') as stream:
            obj.add_bytestream(file_name, stream,
                               ObjectManager._get_file_root(uid))
        dataset['name'] = name

        if 'description' in options:
            dataset['description'] = options['description']

        if 'public' in options:
            dataset['public'] = options['public']

        dataset['data']['path'] = file_name

        filepath = os.path.join(dataset.get_file_path(),
                                dataset['data']['path'])
        dataset['status'] = ObjectManager.DOWNLOADED
        if options['uncompress'] and ObjectManager.isarchive(name) is not None:
            dataset['status'] = ObjectManager.UNCOMPRESS
            options['original_format'] = options['format']
            options['format'] = 'archive'

        dataset['data']['size'] = os.path.getsize(filepath)
        if 'project' in options:
            dataset['project'] = ObjectId(options['project'])

        if options['format'] == 'auto':
            # Try auto-detect
            detector = BioFormat()
            fformat = detector.detect_by_extension(dataset['name'])
            if fformat is None:
                (fformat, mime) = detector.detect(filepath)
        else:
            fformat = options['format']

        dataset['data']['format'] = fformat
        dataset['data']['type'] = options['type']

        dataset.save()

        if ObjectManager.use_repo and not options['uncompress']:
            index = ObjectManager.get_repository_index(uid)
            index.add([dataset['data']['path']])
            if 'msg' in options:
                msg = options['msg']
            else:
                msg = "Update file content"
            index.commit(msg + " " + dataset['name'])

        #return str(dataset['_id'])
        return dataset

    @classmethod
    def history(cls, fid):
        '''
        Get historical data from repository commits

        :param fid: Id of the dataset needing historical operations
        :type fid: str
        :return: array of commit date and message dict
        '''
        fid = str(fid)
        if not ObjectManager.use_repo:
            return []
        dataset = connection.ProjectData.find_one({'_id': ObjectId(fid)})
        uid = str(dataset['_id'])
        repo = ObjectManager.get_repository(uid)
        commits = []
        #for commit in head.commit.iter_parents(paths='', skip=0):
        for commit in repo.iter_commits():
            commits.append({'committed_date': commit.committed_date,
                            'message': commit.message})
        return commits


