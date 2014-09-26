# -*- coding: utf-8 -*-
'''
Created on Nov. 12, 2012

@author: O. Doppelt
@author: E. Legros
@author: H. Menager
@author: B. Neron
@author: O. Sallou
@license: GPLv3
'''
import os, shutil, copy

from mongokit import SchemaDocument
from .type import *


class AbstractData(SchemaDocument):
    """
    Abstract super class for all kinds of data
    """

    structure = {
                 "_type": unicode,
                 "type": Type
                }

    def check_value(self):
        raise NotImplementedError()

    def clean(self):
        pass

    def expr_value(self):
        """
        Get the value used for evaluated
        expressions (precond, ctrl, format, etc.)
        """
        raise NotImplementedError()

    def import_to_job(self, job):
        return copy.deepcopy(self)

@connection.register
class RefData(AbstractData):
    """
    A data whose value is stored on the file system
    on one or more files
    """

    structure = {'path': basestring,
                 'size': int,
                }

    def clean():
        """
        Clean "text" data from Windows(TM) encoding
        """
        #TODO only clean if format is text
        return

    def expr_value(self):
        """
        Get the value used for evaluated
        expressions (precond, ctrl, format, etc.)
        i.e. the list of file names.
        """
        return self['path']

    def import_to_job(self, job, src_pref=None):
        src_path = self['path']
        #TODO, this is a naive implementation that does not handle
        # any potential copy problem
        if src_pref is not None:
            src_path = os.path.join(src_pref, src_path)
        # TODO, here insert "securing" of file name
        dst_file_name = self['path']
        dst_path = os.path.join(job.dir, dst_file_name)
        print job.dir
        shutil.copy(src_path, dst_path)
        data_object = copy.deepcopy(self)
        data_object['path'] = dst_file_name
        return data_object

@connection.register
class ValueData(AbstractData):
    """
    A data whose value is stored directly in the object
    """

    structure = {
                 'value': None
                }

    def check_value(self):
        self['type'].check_value(self['value'])

    def expr_value(self):
        return self['value']

@connection.register
class ListData(AbstractData):
    """
    A data formed by a list of data sharing the same type/format
    """

    structure = {
                 'value': [AbstractData]
                }

    def expr_value(self):
        """
        Get the value used for evaluated
        expressions (precond, ctrl, format, etc.)
        i.e. the list of its elements expr_values.
        """
        return [el.expr_value() for el in self['value']]

@connection.register
class StructData(AbstractData):
    """
    A data formed by a list properties referencing different data
    """

    structure = {
                 'properties': {basestring: AbstractData},
                 # Temporary storage to get list of files, waiting for user to map them
                 # with ontology terms
                 'files': None
                }

    def expr_value(self):
        """
        Get the value used for evaluated
        expressions (precond, ctrl, format, etc.)
        i.e. the dictionary of properties with their
        expr_values.
        """
        return {prop_name: prop_val.expr_value() for prop_name, prop_val in self['properties'].items()}


def new_data(new_data_type):
    if isinstance(new_data_type, FormattedType):
        data = RefData()
    elif isinstance(new_data_type, StructType):
        data = StructData()
    elif isinstance(new_data_type, ArrayType):
        data = ListData()
    else:
        data = ValueData()
    data['type'] = new_data_type
    return data
