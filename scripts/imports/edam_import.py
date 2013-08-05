# -*- coding: utf-8 -*-
"""
Created on May 28, 2013

@author: Olivia Doppelt-Azeroual
@contact: olivia.doppelt@pasteur.fr
@organization: Institut Pasteur, CIB
@license: GPLv3
"""

import os, sys,string
import logging

import argparse

from mobyle.common.config import Config

logger = logging.getLogger('mobyle.edam_integration')
logger.setLevel(logging.INFO)

def parse_term(o,edamElement):
    """
    parse EDAM term from edam information extracted from a .obo file
    :param o: term object to be filled
    :type o: Term
    :param edamElement: dictionary containing the EDAM information
    :type edamElement: dict
    """
    for attribute in edamElement:
        at = attribute.split(': ')
        try:
            if at[0]=="id":
                o['id']=at[1]
            if at[0]=="name":
                o['name']=at[1]
            if at[0]=="def":
                # removes the edam ontology url from definition
                o['definition']=at[1].replace("[http://edamontology.org]","").replace("\"","")
            if at[0]=="synonym":
                o['synonyms'].append(at[1])
            if at[0]=="is_a":
                o['subclassOf'].append(at[1].split(' ')[0])
            if at[0]=="is_obsolete":
                o['is_obsolete']= True
            if at[0]=="relationship":
                relation = at[1].split(' ')
                o[relation[0]].append(relation[1])
        except Exception, e:
            logger.error("Error while parsing term information %s" % str(attribute), exc_info=True)
            logger.error(o['id'])
            pass
    if not o['is_obsolete']:
        o['is_obsolete'] = False
    return o

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Integration of EDAM ontology in Mobyle2 DB")
    parser.add_argument('--config', help="path to the Mobyle2 config file for DB injection")
    parser.add_argument('--edamfile', help="path to EDAM ontology file (obo format) to process")
    parser.add_argument('--logfile', help="outputs each edam element in a file")
    parser.add_argument('action', choices=['init','update'], help="select which action to launch")
    args = parser.parse_args()

    if args.config:
        # Init config
        config = Config(args.config).config()
        # init db connection
        from mobyle.common.connection import connection
        from mobyle.common.type import Type, Format
        from mobyle.common.operation import Operation
        from mobyle.common.topic import Topic
        Type=connection.Type
        Format=connection.Format
        Topic=connection.Topic
        Operation=connection.Operation
        # action definition
        if args.action == 'init':
            # empty collections
            Type.collection.drop()
            Format.collection.drop()
            Topic.collection.drop()
            Operation.collection.drop()
        else:
            pass
                

    else:
        from mobyle.common.type import Type, Format
        from mobyle.common.operation import Operation
        from mobyle.common.topic import Topic
    # opens the edam obo file
    edam=open(args.edamfile,'r')

    # parses the edam file
    edam_lines=edam.read()

    # separated the edam element from each other
    edam_elements=edam_lines.split('[Term]')
    
    nbtype=0
    nbformat=0
    nbtopic=0
    nboperation=0
    o = None
    for edam_element in edam_elements:
        # One element is a list of different edam field
        element=edam_element.split('\n')
        
        if len(element)>1:
            field=element[1].split(': ')
            if field[1][0:9]=="EDAM_data":
                o=Type()
                parse_term(o,element)
                nbtype=nbtype+1

            elif field[1][0:11]=="EDAM_format":
                o=Format()
                parse_term(o,element)
                nbformat=nbformat+1
            elif field[1][0:10]=="EDAM_topic":
                o=Topic()
                parse_term(o,element)
                nbtopic+=1 
            elif field[1][0:14]=="EDAM_operation":
                o=Operation()
                parse_term(o,element)
                nboperation+=1
        if o is not None:            
            if args.config:
		try:
                    o.save()
                except Exception, e:
                    print o #TODO add real logging
                    raise e
            if args.logfile:
                log=open(args.logfile,'a')
                log.write(o['id'])
                log.close()
            o=None
                    
        

