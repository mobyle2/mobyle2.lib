'''
This module manages object storage
'''
from pairtree import PairtreeStorageFactory

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
            ObjectManager.use_repo = config.getboolean("app:main", "use_history")
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
            "/" + ObjectManager._get_file_root(uid) + "/" + uid

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
    def get_token(cls, uid, file_path, mode=AccessMode.READONLY, lifetime=3600):
        '''
        Return a temporary token to serve a dataset file

        :param uid: Id of the dataset
        :type uid: basestring
        :param file_path: relative path to the file in the dataset
        :type file_path: basetring
        :param mode: allowed access mode
        :type mode: AccessMode.READONLY, AccessMode.READWRITE
        :param lifetime: duration of the token in seconds
        :type lifetime: int
        :return: basetring, token
        '''
        uid = str(uid)
        token_path = os.path.join(ObjectManager.get_storage_path(uid),file_path)
        temptoken = connection.Token()
        temptoken.generate(lifetime)
        token_data  = dict()
        token_data['file'] = token_path
        token_data['access'] = mode
        temptoken['data'] = token_data
        temptoken.save()
        return temptoken['token']

    @classmethod
    def _delete_file(cls, uid, options=None):
        '''
        Delete file from storage directly or via repo
        '''
        obj = ObjectManager.storage.get_object(uid)

        # If origin is a archive, it has not been added
        # to the repository
        if ObjectManager.use_repo and not options['uncompress']:
            index = ObjectManager.get_repository_index(uid)
            index.remove([uid])
            if 'msg' in options:
                msg = options['msg']
            else:
                msg = "File removed"
            index.commit(msg + " " + options['name'])
        path = ObjectManager._get_file_root(uid)
        obj.del_file(uid, path)

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
                #TODO: manage removal of List or Struct data types
                # we should be able to detect from _type, bu not for the moment
                # This is a RefData
                if 'path' in dataset['data']:
                    options['name'] = dataset['name']
                    ObjectManager._delete_file(uid, options)
                else:
                    for value in dataset['data']['value']:
                        if 'path' in value:
                            fpath = os.path.basename(value['path'])
                            options['name'] = fpath
                            ObjectManager._delete_file(fpath, options)
        except Exception:
            logging.error("Error while trying to delete ")
            #traceback.print_exc(file=sys.stdout)
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
        Config.config()
        #uid = uuid.uuid4().hex
        dataset = connection.ProjectData()
        if 'schema' in options:
            dataset['data'] = options['schema']
        else:
            dataset['data'] = RefData()
        dataset['name'] = name
        dataset['status'] = ObjectManager.QUEUED
        if 'path' in options:
            dataset['path'] = options['path']
        dataset['persistent'] = persistent
        if 'project' in options:
            dataset['project'] = ObjectId(options['project'])
        dataset.save()
        if ObjectManager.use_repo and not options['uncompress']:
            ObjectManager.get_repository_index(str(dataset['_id']))
        #return str(dataset['_id'])
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

        :param id: Database id of the data
        :type id: str
        :param status: Status of the  upload/download \
                    (QUEUED,DOWNLOADING,DOWNLOADED,ERROR)
        :type status: int
        '''
        dataset = connection.ProjectData.find_one({"_id": ObjectId(options['id'])})

        if status == ObjectManager.DOWNLOADED and options['uncompress'] and\
        ObjectManager.isarchive(options['name']):
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
            if options['uncompress']:
                msg = 'Add: '
                if 'msg' in options:
                    msg = options['msg']
                if options['group']:
                    dataset['data'] = ListData()
                #    dataset['data']['path'] = pairtree.id2path(uid) + path
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
                        subdata['path'] = filespath
                        subdata['size'] = \
                                os.path.getsize(ObjectManager.get_storage_path() +
                                subdata['path'])
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
                        ObjectManager.store(os.path.basename(filepath),
                            filepath, newoptions)
                if not options['group']:
                    # remove current obj, each sub file is a new independant
                    # object
                    ObjectManager.delete(uid, options)
                    # We have managed child object
                    # now we can leave
                    return
                else:
                    # Commit history
                    if ObjectManager.use_repo:
                        index = ObjectManager.get_repository_index(uid)
                        index.commit(msg)
            else:
                dataset['data']['path'] = \
                    pairtree.id2path(uid) + "/" + \
                    ObjectManager._get_file_root(uid) + "/" + uid

                if status == ObjectManager.SYMLINK:
                    # Not taken into account for quota
                    dataset['data']['size'] = 0
                    dirname = os.path.dirname(os.path.join(ObjectManager.get_storage_path(),dataset['data']['path']))
                    if not os.path.exists(dirname):
                        os.mkdir(dirname)
                    os.symlink(options['file'],
                                ObjectManager.get_storage_path() +
                                dataset['data']['path'])
                else:
                    with open(options['file'], 'rb') as stream:
                        obj.add_bytestream(uid, stream, path)
                    dataset['data']['size'] = \
                        os.path.getsize(ObjectManager.get_storage_path() +
                        dataset['data']['path'])

                dataset['data']['type'] = options['type']

                if ObjectManager.use_repo:
                    index = ObjectManager.get_repository_index(uid)
                    index.add([uid])
                    if 'msg' in options:
                        msg = options['msg']
                    else:
                        msg = "Update file content"
                    index.commit(msg + " " + dataset['name'])

            if 'project' in options:
                dataset['project'] = ObjectId(options['project'])
            fformat = None
            mime = None

            if options['format'] == 'auto':
                # Try auto-detect
                detector = BioFormat()
                if dataset['data']['_type'].__class__.__name__ == 'ListData':
                    for subdata in dataset['data']['value']:
                        fformat = detector.detect_by_extension(subdata['name'])
                        if fformat is not None:
                            break
                    # This is a group, get the path where are the files
                    datapath = os.path.dirname(dataset['data']['value'][0]['path'])
                else:
                    fformat = detector.detect_by_extension(dataset['name'])
                    datapath = dataset['data']['path']
                if fformat is None:
                    (fformat, mime) = detector.detect(ObjectManager.get_storage_path() +
                                        datapath)
            else:
                fformat = options['format']

            dataset['data']['format'] = fformat

        dataset['status'] = status
        dataset.save()
        if status == ObjectManager.UNCOMPRESS:
            # delay decompression
            from mobyle.data.manager.background import uncompress
            uncompress.delay(options['file'], options)

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
        :return: data database id
        '''
        dataset = None
        if options is None:
            options = {}
        Config.config()
        if 'id' in options and options['id']:
            dataset = connection.ProjectData.find_one({'_id': ObjectId(options['id'])})
            if not 'data' in dataset:
                dataset['data'] = RefData()
            #uid = dataset['_id']
        else:
            dataset = connection.ProjectData()
            dataset['data'] = RefData()
            dataset.save()
            #uid = uuid.uuid4().hex
        uid = str(dataset['_id'])
        obj = ObjectManager.storage.get_object(uid)
        with open(infile, 'rb') as stream:
            obj.add_bytestream(uid, stream, ObjectManager._get_file_root(uid))

        dataset['name'] = name
        #dataset['uid'] = uid
        dataset['data']['path'] = pairtree.id2path(uid) +\
                                "/" + ObjectManager._get_file_root(uid) + "/" + uid
        dataset['status'] = ObjectManager.DOWNLOADED
        if options['uncompress'] and ObjectManager.isarchive(name) is not None:
            dataset['status'] = ObjectManager.UNCOMPRESS
            options['original_format'] = options['format']
            options['format'] = 'archive'

        dataset['data']['size'] = os.path.getsize(ObjectManager.get_storage_path() + dataset['data']['path'])
        if 'project' in options:
            dataset['project'] = ObjectId(options['project'])

        if options['format'] == 'auto':
            # Try auto-detect
            detector = BioFormat()
            fformat = detector.detect_by_extension(dataset['name'])
            if fformat is None:
                (fformat, mime) =
                detector.detect(ObjectManager.get_storage_path() + dataset['data']['path'])
        else:
            fformat = options['format']

        dataset['data']['format'] = fformat
        dataset['data']['type'] = options['type']

        dataset.save()

        if dataset['status'] == ObjectManager.UNCOMPRESS:
            # delay decompression
            from mobyle.data.manager.background import uncompress
            newoptions = deepcopy(options)
            newoptions['id'] = str(dataset['_id'])
            newoptions['format'] = options['original_format']
            uncompress.delay(ObjectManager.get_file_path(str(dataset['_id'])), newoptions)

        if ObjectManager.use_repo and not options['uncompress']:
            index = ObjectManager.get_repository_index(uid)
            index.add([uid])
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
        if not ObjectManager.use_repo:
            return []
        dataset = connection.ProjectData.find_one({'_id': ObjectId(fid)})
        uid = str(dataset['_id'])
        repo = ObjectManager.get_repository(uid)
        head = repo.head
        commits = []
        for commit in head.commit.iter_parents(paths='', skip=0):
            commits.append({'committed_date': commit.committed_date,
                            'message': commit.message})
        return commits


