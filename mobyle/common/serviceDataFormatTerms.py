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
class ServiceDataFormatTerm(Document):
    """
    Class for data and format terms contained in Mobyle Services.
    """
    __collection__ = 'service_data_format_terms'
    __database__ = Config.config().get('app:main', 'db_name')

    structure = {
        'data_term_id': basestring,
        'data_term_name': basestring,
        'format_terms_ids': [basestring]
        }

    def remove(self, query):
        self.collection.remove(query)

ServiceDataFormatTerm.search_by('data_term_id')

class ServiceDataFormatTermsLoader(object):

    def __init__(self):
        self.serviceDataFormatTerms = connection.ServiceDataFormatTerms()
        log.debug('starting data and format retrieval')
        self.serviceDataFormatTerms.remove({})
        #log.debug(connection.db)
        self.load_services_data_format_terms()


    def load_services_data_format_terms(self):
        """Empties the collection ServiceDataFormatTerms
           And fills it when Mobyle Services are updated
        """
        edam_dict = {}
        children_list = []

        for edam in connection.Term.fetch():
            edam_dict[edam['id']] = edam['name']

        for i in connection.Service.fetch({}):
            children_list.append(i['outputs'])
            children_list.append(i['inputs'])

        self.existing_data_terms = []

        for index in children_list:
            self.fill_terms_list(index, edam_dict, children_list)

    def fill_terms_list(self, children, edam_dict, children_list):
        for i in children['children']:
            # Checks if the children is a Class Parameter
            if isinstance(i, Parameter):
                if i['type'] is not None and isinstance(i['type'], FormattedType):
                    data_term_id = str(i['type']['data_terms'])
                    data_term_name = edam_dict[data_term_id]
                    format_terms_ids = i['type']['format_terms']
                    # Addition of the first EDAM_data term
                    # and its associated EDAM_formats
                    if len(self.existing_data_terms) == 0:
                      #  self.serviceDataFormatTerms = connection.ServiceDataFormatTerms()
                        self.serviceDataFormatTerms ['data_term_id'] = data_term_id
                        self.serviceDataFormatTerms ['data_term_name'] = data_term_name
                        self.serviceDataFormatTerms ['format_terms_ids'] = format_terms_ids

                        self.serviceDataFormatTerms.save()
                        self.existing_data_terms.append(data_term_id)
                    # Addition of the other EDAM_data TERMS:
                    else:
                        for ind in range(0, len(self.existing_data_terms)):
                            #1 - A Check for data term dublons,
                            #if the data_term doesn't exist, this part adds it
                            if data_term_id not in self.existing_data_terms:
                                self.serviceDataFormatTerms = connection.ServiceDataFormatTerms()

                                self.serviceDataFormatTerms ['data_term_id'] = data_term_id
                                self.serviceDataFormatTerms ['data_term_name'] = data_term_name
                                self.serviceDataFormatTerms ['format_terms_ids'] = format_terms_ids
                                self.serviceDataFormatTerms.save()
                                self.existing_data_terms.append(data_term_id)

                            # if it already exists:
                                # 2nd Check: if the format_term is
                                #already associated to this data_term
                            else:
                                if len(format_terms_ids) > 0:
                                    db_items = connection.ServiceDataFormatTerms.find({'data_term_id':data_term_id})
                                    for item in db_items:
                                        item['format_terms_ids'] = list(set(item['format_terms_ids'] + format_terms_ids))
                                        item.save()
            # If not Parameter, calls the fonction on it's children'"
            else:
                self.fill_terms_list(i, edam_dict, children_list)

