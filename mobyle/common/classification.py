# -*- coding: utf-8 *-*
'''
Created on Nov. 23, 2012

@author: Hervé Ménager
@contact: hmenager@pasteur.fr
@license: GPLv3
'''
import logging
log = logging.getLogger(__name__)
from mongokit import Document
from mf.annotation import mf_decorator

from .connection import connection
from .config import Config
from mobyle.common.term import Term
from mobyle.common.service import Service

@mf_decorator
@connection.register
class Classification(Document):
    """
    Classification is a class that stores the service hierarchy in
    a classification based on EDAM topic or operation axes
    """

    __collection__ = 'classifications'
    __database__ = Config.config().get('app:main', 'db_name')

    structure = {'root_term': basestring,
                 'tree': None}


class ClassificationLoader(object):

    def __init__(self, key):
        """
        :param key: key use to generate the classification,
                    either 'topic' or 'operation'
        :type key: string
        """
        self.classification = connection.Classification()
        self.classification['root_term'] = key
        log.debug('started classification loading on %s' % key)
        self.load_all_services()
        self.classification['tree'] = self.load_level()
        self.classification.save()
        log.debug('ended classification loading on %s' % key)

    def load_all_services(self):
        """
        load all services in a dictionary sorted per classification key
        """
        self.services_by_key = {}
        for s in Service.find({}):
            if self.classification['root_term'] == 'EDAM_topic:0003':
                classification_field = 'topics'
            else:
                classification_field = 'operations'
            keys = [term for term in s.get(classification_field, [])]
            entry = {'name': s['name'],
                     'public_name': s.get('public_name'),
                     'version': s.get('version'),
                     '_id': s['_id']}
            # if no classification, assign service to root
            if not(keys):
                keys = [self.classification['root_term']]
            # otherwise add it to the nodes
            for key in keys:
                if not(key in self.services_by_key):
                    self.services_by_key[key] = [entry]
                else:
                    self.services_by_key[key].append(entry)

    def load_level(self, node_input=None):
        """
        load a classification level
        :param level_filter: query filter used to select the level
        :type level_filter: dict
        """
        node_output = {}

        if node_input:
            node_output['id'] = node_input['id']
            node_output['name'] = node_input['name']
            node_filter = {'subclassOf': {'$in': [node_input['id']]}}
        else:
            node_output['id'] = 'EDAM:0000'
            node_output['name'] = 'nowhere'
            node_filter = {'subclassOf': []}
        node_output['sublevels'] = []
        for t in Term.find(node_filter):
            if not ':' in t['id']:
                continue
            if t['is_obsolete'] is True:
                continue
            node_output['sublevels'].append(self.load_level(t))
        key = node_output['id']
        node_output['services'] = self.services_by_key.get(key, [])
        if not(node_input):
            node_output['services'] = self.services_by_key.get('EDAM:0000', [])
        return node_output

    def get_classification(self, node_input=None, filter=None):
        if not(node_input):
            node_input = self.root_node
        node_output = {'id': node_input['id'],
                       'name': node_input['name'],
                       'services': [], 'sublevels': []}
        for sublevel in node_input['sublevels']:
            n = self.get_classification(node_input=sublevel, filter=filter)
            if n:
                node_output['sublevels'].append(n)
        if filter is not None:
            node_output['services'] = [service for service in
                node_input['services'] if filter in service['name']]
        else:
            node_output['services'] = list(node_input['services'])
        node_output = self.prune(node_output)
        return node_output

    def prune(self, node):
        """
        prune classification tree to simplify it
        """
        if len(node['services']) == 0 and len(node['sublevels']) == 0:
            # do not load empty tree nodes
            return None
        if len(node['services']) == 0 and len(node['sublevels']) == 1:
            # replace current node with child node if there is only one
            return node['sublevels'][0]
        return node

