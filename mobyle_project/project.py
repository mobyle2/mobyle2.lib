# -*- coding: utf-8 -*-
'''
Created on Nov. 23, 2012

@author: E. LEGROS
@contact: emeline.legros@ibcp.fr
@license: GPLv3
'''

import pymongo
import datetime
import sys


connection_string = "mongodb://localhost"

class Project:
    """
    Project is a class that stores all information about a project (owner username, inputs, outputs, job id). 
    It's initialized by three parameters: the name of the owner of the project, the project name itself, and a list of Data objects.
    """

    def __init__(self, owner = None, project_name = None):
	"""
	:param owner: name of the project owner 
	:type owner: string
	:param project_name: name of the project 
	:type project_name: string
	"""

	# Database management
	connection = pymongo.Connection(connection_string, safe=True)
	# database name: mobyle
	db = connection.mobyle
	# collection name: projects
	projects = db.projects	

        self._project_name = project_name
	self._project_owner = owner
	
	project = {"name": project_name, 
		"owner": owner,
		"date": datetime.datetime.utcnow()}

	try:
		projects.insert(project)
		print "Inserting the project"
	
	except:
		print "Error inserting project"
		print "Unexpected error:", sys.exc_info()[0]
		

    def add_data(self, data_name, data, provenance_info = None):	
        """
	add_data is a method defined to add a new data into the project. 
        :param data_name: name of the data.
        :type data_name: string.
	:param data: data to be associated to the project.
        :type data: Data object.
	:param provenance_info: information about the data.
        :type data: string.
        """
	
	# Database management
	connection = pymongo.Connection(connection_string, safe=True)
	# database name: mobyle
	db = connection.mobyle
	# collections name
	projects = db.projects	
	data = db.data
	
	data_entry = {"name": data_name, 
		"value": data.value,
		"provenance_info": provenance_info}
	
	try:
		data_id = data.insert(data_entry)
		print "Inserting the data"
	
	except:
		print "Error inserting data"
		print "Unexpected error:", sys.exc_info()[0]
		
	
	try:
		project = projects.update({"name": self._project_name, "owner": self._project_owner},{'$set':{"data_id":data_id}})
		print "Inserting the data"
	
	except:
		print "Error inserting data in the project"
		print "Unexpected error:", sys.exc_info()[0]
	
	self._data_ids.append(data_id)
	
	
	

    def add_list_of_data(self, data_list, provenance_info):
        """
	add_list_of_data is a method defined to add a set of data into the project.
        :param data_list: list of data
        :type data_list: 2D array containing data name, Data object itself.
	:param provenance_info: information about the data.
	:type data: string.
	"""
	
	# Database management
	connection = pymongo.Connection(connection_string, safe=True)
	# database name: mobyle
	db = connection.mobyle
	# collections name
	projects = db.projects	
	data = db.data
	
	try:
		
		#insert data in the data and return corresponding ids.
		for i in range(len(data_list)):
			data_entry = {"name": data_list[i][0],
				"value": data_list[i][1].value,
				"provenance_info": provenance_info}
				
			data_id.append(data.insert(data_entry))
			print "Inserting the data"
	
	except:
		print "Error inserting data"
		print "Unexpected error:", sys.exc_info()[0]
		
	
	try:
		project = projects.update({"name": self._project_name, "owner": self._project_owner},{'$set':{"data_id":data_id}})
		print "Inserting the data"
	
	except:
		print "Error inserting data in the project"
		print "Unexpected error:", sys.exc_info()[0]
	
	for i in range(len(data_id)):
		self._data_ids.append(data_id[i])


    def add_job(self, job_name, description = None):	
        """
	add_job is a method defined to add a new job into the project. 
        :param job_name: name of the job.
        :type data_name: string.
	:param description: short description of the job.
        :type description: string.
        """
	
	# Database management
	connection = pymongo.Connection(connection_string, safe=True)
	# database name: mobyle
   	db = connection.mobyle
	# collections name
    	projects = db.projects	
	jobs = db.jobs
	
	job = {"name": job_name, 
		"description": description}
	
	try:
		job_id = jobs.insert(job)
		print "Inserting the job"
	
	except:
		print "Error inserting job"
		print "Unexpected error:", sys.exc_info()[0]
		
	
	try:
		project = projects.update({"name": self._project_name, "owner": self._project_owner},{'$set':{"job_id":job_id}})
		print "Inserting the job"
	
	except:
		print "Error inserting job in the project"
		print "Unexpected error:", sys.exc_info()[0]
	
	self._job_ids.append(job_id)
	
	
   
    @property
    def project_name(self):
        """
	:return: the name associated to the project.
	:rtype: string.
	"""
        return self._project_name

    @property
    def project_owner(self):
        """
	:return: the owner associated to the project.
	:rtype: string.
	"""
        return self._project_owner
    
    @property
    def data_ids(self):
        """
	:return: the array of ids of data.
	:rtype: array of string.
	"""
        return self._data_ids

    @property
    def job_ids(self):
        """
	:return: the array of job ids.
	:rtype: array of string.
	"""
        return self._job_ids


