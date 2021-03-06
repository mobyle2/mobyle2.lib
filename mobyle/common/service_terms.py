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

from mf.annotation import mf_decorator, MF_READ

from mobyle.common.service import Service, Parameter
from mobyle.common.term import Term
from mobyle.common.type import FormattedType, StructType, ArrayType

@mf_decorator
@connection.register
class ServiceTypeTerm(Document):

    __collection__ = 'service_type_terms'
    __database__ = Config.config().get('app:main', 'db_name')

    structure = {
        'name': basestring
        }

    def remove(self, query):
        self.collection.remove(query)


@mf_decorator
@connection.register
class FormattedTypeTerm(ServiceTypeTerm):
    """
    Class for data and format terms contained in Mobyle Services.
    """

    structure = {
        'term_id': basestring,
        'format_terms': [{'edam': basestring, 'name': basestring}]
        }

    indexes = [
        {
        'fields': 'term_id',
        'unique': True
            }
        ]

ServiceTypeTerm.search_by('term_id')


@mf_decorator
@connection.register
class StructTypeTerm(ServiceTypeTerm):
    """
    Class for structType terms contained in Mobyle Services
    """
    structure = {
        'properties': {
            unicode: {
                'term_id': basestring,
                'name': basestring,
                'format_terms': [{'edam': basestring, 'name': basestring}]
        }}
        }


class ServiceTypeTermLoader(object):

    def __init__(self):
        self.service_type_term = connection.ServiceTypeTerm()
      #  self.service_struct_type_term = connection.ServiceStructTypeTerm()
        log.debug('starting data and format retrieval')
        self.service_type_term.remove({})
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
        try:
            for i in children['children']:

                # Checks if the children is a Class Parameter
                if isinstance(i, Parameter):
                    if i['type'] is not None and isinstance(i['type'], FormattedType):
                        try:
                            term_id = i['type']['data_terms'][0]
                            formatted_type = connection.FormattedTypeTerm.fetch_one({'term_id':term_id})
                            if formatted_type is None:
                                formatted_type = connection.FormattedTypeTerm()
                                fill_formatted_type_term(i['type'], formatted_type)

                            formatted_type.save()

                        except Exception:
                            log.debug("error while processing type for parameter %s"
                                       % i['name'], exc_info=True)

                    elif isinstance(i['type'], StructType):

                        struct_type_term = connection.StructTypeTerm()
                        name = ""

                        for k, v in i['type']['properties'].items():
                            if name == "":
                                name = k
                            else:
                                name = k + "+" + name

                            term_id = v['data_terms'][0]

                            formatted_type = connection.FormattedTypeTerm.fetch_one({'term_id':term_id})
                            if formatted_type is None:
                                formatted_type = connection.FormattedTypeTerm()
                                fill_formatted_type_term(v[0], formatted_type)

                            formatted_type.save()

                            struct_type_term['properties'][k] = {}
                            fill_formatted_type_term(v[0],struct_type_term['properties'] [k])

                        struct_type_term['name'] = name

                        struct_type_term.save()

                # If not Parameter, calls the fonction on it's children'"
                else:
                    self.fill_terms_list(i, children_list)
        except Exception:
            log.debug("missing children key")

def append_format_terms(existing_list, new_list):
    for i in new_list:
        length = len(existing_list)
        cpt = 0
        for j in existing_list:
            if i['term_id'] != j['term_id']:
                cpt = cpt + 1
        if cpt == length:
            existing_list.append(i)
    return existing_list


def fill_formatted_type_term(formatted_type, formatted_type_term):
    term_id = formatted_type['data_terms'][0]
    format_terms = []

    if type(formatted_type['format_terms']) == list:
        for format_term in formatted_type['format_terms']:
            try:
                term = connection.Term.fetch_one({'id': str(format_term)})
                format_terms.append({"term_id": format_term, "name": term['name']})
            except TypeError:

                log.debug('format_terms: %s is not found in the term collections' % str(format_term))
                continue

        formatted_type_term['term_id'] = term_id
        data_term =\
            connection.Term.fetch_one({'id': term_id})
        if data_term:
            formatted_type_term['name'] = data_term['name']
        else:
            log.error('data term cannot be found for id %s' % term_id)

        formatted_type_term['format_terms'] = format_terms
        formatted_type_term['format_terms'] = append_format_terms(formatted_type_term['format_terms'], format_terms)
    else:
        log.error('format_terms %s are not stored in a list, Check the service json format' % str(formatted_type['format_terms']))

    return formatted_type_term
