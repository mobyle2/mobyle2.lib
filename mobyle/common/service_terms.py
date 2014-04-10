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
from mobyle.common.type import FormattedType, StructType, ArrayType


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
        'format_terms': [{'edam': basestring, 'name': basestring}]
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
        self.load_services_data_format_term()

    def append_format_terms(self,existing_list, new_list):
        for i in new_list:
            length = len(existing_list)
            cpt = 0
            for j in existing_list:
                if i['edam_term'] != j['edam_term']:
                    cpt = cpt + 1
            if cpt == length:
                existing_list.append(i)
        return existing_list

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
                    try:
                        data_term_id = i['type']['data_terms']
                        format_terms = []
                        for format_term in i['type']['format_terms']:
                            term = connection.Term.fetch_one({'id': str(format_term)})
                            format_terms.append({"edam_term": format_term, "name": term['name']})
                        service_type_term = connection.ServiceTypeTerm.fetch_one({'data_term_id':data_term_id})
                        if service_type_term is None:
                            service_type_term = connection.ServiceTypeTerm()
                            service_type_term['data_term_id'] = data_term_id
                            data_term =\
                                connection.Term.fetch_one({'id': data_term_id})
                            if data_term:
                                service_type_term['data_term_name'] = data_term['name']
                            else:
                                log.error('data term cannot be found for id %s' % data_term_id)
                                continue
                            service_type_term['format_terms'] = format_terms
                        service_type_term['format_terms'] = self.append_format_terms(service_type_term['format_terms'], format_terms)
                        service_type_term.save()
                    except Exception, TypeError:
                        log.error("error while processing type for parameter %s"
                                   % i['name'], exc_info=True)
            # If not Parameter, calls the fonction on it's children'"
            else:
                self.fill_terms_list(i, children_list)

