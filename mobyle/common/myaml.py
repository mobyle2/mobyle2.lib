# -*- coding: utf-8 -*-
'''
Created on Aug. 21, 2014

@license: GPLv3
'''
from collections import OrderedDict
import yaml
from mongokit import SchemaDocument, Document, ObjectId

from .config import Config
from .connection import connection

# pylint: disable=W0201,R0904,R0913
#FIXME the Myaml class is useless because it pollutes the
# yaml global space anyway, refactor this at level module instead?

_PREFIX = '!mobyle/'

class Myaml(object):

    def __init__(self):
        self._mongokit_classes = {}
        self._yaml_prefixes = {}
        obj = self
        def schemadoc_representer( self, data):
            if data.__class__ not in obj._yaml_prefixes:
                raise TypeError('Cannot serialize objects of class %s' % 
                    data.__class__.__name__)
            ordered_data = OrderedDict()
            def set_value(key):
                if data[key] is not None and data[key] != [] and\
                    not(isinstance(data[key], ObjectId)):
                    if hasattr(data, 'default_values') and \
                        key in data.default_values and \
                        data.default_values[key]==data[key]:
                        return
                    ordered_data[key] = data[key]
            if hasattr(data,'keys_order'):
                keys = data.keys_order
                keys += [key for key in data.structure 
                    if key not in data.keys_order]
            else:
                keys = data.structure.keys()
            if '_type' in keys:
                keys.remove('_type')
            for key in keys:
                set_value(key)
            return self.represent_mapping(
                _PREFIX +obj._yaml_prefixes[data.__class__], ordered_data.items())
        yaml.add_multi_representer(SchemaDocument, schemadoc_representer)
        yaml.add_representer(unicode, 
            yaml.representer.SafeRepresenter.represent_unicode)
        def schemadoc_constructor(loader, tag_suffix, node):
            value = loader.construct_mapping(node, deep=True)
            mk_class = self._mongokit_classes[node.tag[len(_PREFIX):]]
            if mk_class.__name__ in connection._registered_documents:
                connected_class = connection[mk_class.__name__]
            elif mk_class.__name__ in connection._registered_schema_documents:
                connected_class = mk_class
            schema_doc = connected_class()
            if isinstance(schema_doc, Document):
                schema_doc.__init__(value, gen_skel=True, 
                    collection=schema_doc.collection)
            else:
                schema_doc.__init__(value, gen_skel=True)
            for key in connected_class.structure.keys():
                if key not in schema_doc:
                    schema_doc[key] = None
            return schema_doc
        yaml.add_multi_constructor(_PREFIX, schemadoc_constructor)

    def register(self, mongokit_class, prefix=None):
        if prefix is None:
            prefix = mongokit_class.__name__.lower()
        self._mongokit_classes[prefix] = mongokit_class
        self._yaml_prefixes[mongokit_class] = prefix
        return mongokit_class

    @property
    def registered_classes(self):
        return self._mongokit_classes

    def dump(self, schemadoc, filename=None, indent=4, tags=None):
        return yaml.dump(schemadoc, filename, indent=indent, tags=tags)

    def load(self, schemadoc):
        return yaml.load(schemadoc)

myaml = Myaml()
