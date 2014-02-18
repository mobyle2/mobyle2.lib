# -*- coding: utf-8 -*-
"""
Created on Fev 12, 2014
@author: Olivia Doppelt-Azeroual
@contact: odoppelt@pasteur.fr
@organization: Institut Pasteur, CIB
@license: GPLv3
"""

import logging
log = logging.getLogger(__name__)

from mongokit import Document
from .connection import connection
from .config import Config

from mf.annotation import mf_decorator


from mobyle.common.service import Service, Parameter
from mobyle.common.term import Term
from mobyle.common.type import FormattedType


from mf.views import MF_READ


@mf_decorator
@connection.register
class ServiceTypeTerm(Document):
    """
    Class for data and format terms contained in Mobyle Services.
    """
    __collection__ = 'service_type_terms'
    __database__ = Config.config().get('app:main', 'db_name')

    structure = {
        'data_term_id': basestring,
        'data_term_name': basestring,
        'format_term_ids': [basestring]
        }

    indexes = [
        {
        'fields': 'data_term_id',
        'unique': True
            }
        ]

    def remove(self, query):
        self.collection.remove(query)

ServiceTypeTerm.search_by('data_term_id')


class ServiceTypeTermLoader(object):

    def __init__(self):
        self.service_type_term = connection.ServiceTypeTerm()
        log.debug('starting data and format retrieval')
        self.service_type_term.remove({})
        #log.debug(connection.db)
        self.load_services_data_format_term()

    def load_services_data_format_term(self):
        """Empties the collection service_type_term
           And fills it when Mobyle Services are updated
        """

        children_list = []

        for i in connection.Service.fetch({}):
            children_list.append(i['outputs'])
            children_list.append(i['inputs'])

        for index in children_list:
            self.fill_terms_list(index, children_list)

    def fill_terms_list(self, children, children_list):
        for i in children['children']:
            # Checks if the children is a Class Parameter
            if isinstance(i, Parameter):
                if i['type'] is not None and isinstance(i['type'], FormattedType):
                    data_term_id = i['type']['data_terms']

                    format_term_ids = i['type']['format_terms']

                    service_type_term = connection.ServiceTypeTerm.fetch_one({'data_term_id':data_term_id})
                    if service_type_term is None:
                        service_type_term = connection.ServiceTypeTerm()
                        service_type_term['data_term_id'] = data_term_id
                        service_type_term['data_term_name'] =\
                            connection.Term.fetch_one({'id': data_term_id})['name']
                        service_type_term['format_term_ids'] =\
                            format_term_ids
                    service_type_term['format_term_ids'] = list(set(service_type_term['format_term_ids'] + format_term_ids))
                    service_type_term.save()
            # If not Parameter, calls the fonction on it's children'"
            else:
                self.fill_terms_list(i, children_list)

