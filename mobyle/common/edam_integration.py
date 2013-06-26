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


def parse_type(t,edamElement):
    """
    parse EDAM type from an edam element extracted from a .obo file
    : param t_dict: dictionary containing the EDAM type element
    :type struct: dict
    :param t: format object to be filled
    : type
    """
    # @compléter
    #logger.debug("parsing edam type")

    for attribute in edamElement:
        at = attribute.split(': ')
        try:
            if at[0]=="id":
                t['id']=at[1]
            if at[0]=="name":
                t['name']=at[1]
            if at[0]=="def":
                # removes the edam ontology url from definition
                t['definition']=at[1].replace("[http://edamontology.org]","").replace("\"","")
            if at[0]=="synonym":
                 t['synonyms'].append(at[1])
            if at[0]=="is_a":
                 t['subclassOf'].append(at[1])
            if at[0]=="is_obsolete":
                 t['is_obsolete']= True
        except IndexError:
            logger.debug("IndexError in parse_type")
            pass
    if not t['is_obsolete']:
        t['is_obsolete'] = False
    return t
    
        
def parse_format(f,edamElement):
    """
    parse EDAM format from the edam.obo file
    :param f_dict: the dictionary containing the EDAM format element
    :type struct: dict
    :param f: format object to be filled
    : type
    """
    #logger.debug("parsing edam format")
                 
    for attribute in edamElement:
        at = attribute.split(': ')
        
        try:
            if at[0]=="id":
                f['id']=at[1]
            if at[0]=="name":
                f['name']=at[1]
            if at[0]=="def":
                f['definition']=at[1].replace("[http://edamontology.org]","").replace("\"","")
            if at[0]=="comment":
                f['comment']=at[1]
            if at[0]=="synonym":
                f['synonyms'].append(at[1])
            if at[0]=="relationship":
                f['isFormatOf'].append(at[1].split(' ')[1])
        except IndexError:
            print at


    
    return f


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Integration of EDAM ontology in Mobyle2 DB")
    parser.add_argument('--config', help="path to the Mobyle2 config file for DB injection")
    parser.add_argument('--edamfile', help="path to EDAM ontology file (obo format) to process")
    parser.add_argument('--logfile', help="outputs each edam element in a file")
    parser.add_argument('action', choices=['init','update'], help="select which action to launch")
    args = parser.parse_args()
    t=None
    f=None

    if args.config:
        # Init config
        config = Config(args.config).config()
        # init db connection
        from mobyle.common.connection import connection
        from mobyle.common.type import Type, Format
        Type=connection.Type
        Format=connection.Format

        # # action definition
        # if args.action == 'init':
        #      # vider la base
        #     print Type.drop()
        #     print Format
        # else:
        #     pass
                

    else:
        from mobyle.common.type import Type, Format
  
    #t=None
    #f=None
    # opens the edam obo file
    edam=open(args.edamfile,'r')

    # parses the edam file
    edam_lines=edam.read()

    # separated the edam element from each other
    edam_elements=edam_lines.split('[Term]')
    
    nbtype=0
    nbformat=0

    for edam_element in edam_elements:
        # One element is a list of different edam field
        element=edam_element.split('\n')
        
        if len(element)>1:
            field=element[1].split(': ')
            
            if field[1][0:9]=="EDAM_data":
                t=Type()
                parse_type(t,element)
                nbtype=nbtype+1

            else:
                if field[1][0:11]=="EDAM_format":
                    f=Format()
                    parse_format(f,element)
                    nbformat=nbformat+1
                    
        if t:
            if args.config:
                t.save()
            if args.logfile:
                log=open(args.logfile,'a')
                log.write(t['id'])
                log.close()
        if f:
            if args.config:
                f.save()
            if args.logfile:
                log=open(args.logfile,'a')
                log.write(f['id'])
                log.close()
                    
        

