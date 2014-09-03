# -*- coding: utf-8 -*-

import unittest
import os.path
import time
from datetime import datetime
from mongokit.schema_document import RequireFieldError
 
#a config object must be instantiated first for each entry point of the application
from mobyle.common.config import Config
config = Config( os.path.join( os.path.dirname(__file__), 'test.conf'))
from mobyle.common.connection import connection

from mobyle.common.job_routing_model import ExecutionSystem
from mobyle.common.job_routing_model import ExecutionRoutes, ExecutionRule

from mobyle.common.mobyleError import MobyleError


class TestExecutionSystem(unittest.TestCase):

    def setUp(self):
        objects = connection.ExecutionSystem.collection.remove({})

    def test_insert_N_get(self):
        big_one = {"_id" : "big_one",
                   "class" : "OgsDRMAA",
                    "drm_options" : {"drmaa_library_path" : "path/to/sge/libdrmaa.so",
                                     "cell" : '/usr/local/sge',
                                     "root" : 'default', 
                                    },
                   "native_specifications": " -q mobyle-long " 
                }
        exec_sys = connection.ExecutionSystem()
        exec_sys['_id'] = big_one['_id']
        exec_sys['class'] = big_one['class']
        exec_sys["drm_options"] = big_one["drm_options"]
        exec_sys["native_specifications"] = big_one["native_specifications"]
        exec_sys.save()
        
        cluster_two = {"_id" : "cluster_two",
                       "class" : "TorqueDRMAA", 
                       "drm_options" : {"drmaa_library_path" : "path/to/torque/libdrmaa.so",
                                        "server_name" : "localhost" 
                                        },
                       "native_specifications": None
                        }
        exec_sys = connection.ExecutionSystem()
        exec_sys['_id'] = cluster_two['_id']
        exec_sys['class'] = cluster_two['class']
        exec_sys["drm_options"] = cluster_two["drm_options"]
        exec_sys.save()
                                 
        local = {"_id" : "local",
                 "class" : "Local",
                 "drm_options" : None,
                 "native_specifications" : " nice -n 18 "
                }
        exec_sys = connection.ExecutionSystem()
        exec_sys['_id'] = local['_id']
        exec_sys['class'] = local['class']
        exec_sys["native_specifications"] = local["native_specifications"]
        exec_sys.save()
        
        exec_sys_list = connection.ExecutionSystem.find({})
        count = 0
        for exec_sys in  exec_sys_list:
            count += 1
        self.assertEqual(count, 3)
        
        big_one_received = connection.ExecutionSystem.find_one({"_id" : "big_one"})
        del big_one_received[u'_type']
        self.assertDictEqual(big_one, big_one_received)
        
        cluster_two_received = connection.ExecutionSystem.find_one({"_id" : "cluster_two"})
        del cluster_two_received[u'_type']
        self.assertDictEqual(cluster_two, cluster_two_received)
        
        local_received = connection.ExecutionSystem.find_one({"_id" : "local"})
        del local_received[u'_type']
        self.assertDictEqual(local, local_received)
        
class TestExecutionRoutes(unittest.TestCase):        
    
    def setUp(self):
        objects = connection.ExecutionRoutes.collection.remove({})
        
        def push_exec_sys_in_db(conf):
            exec_sys = connection.ExecutionSystem()
            exec_sys['_id'] = conf['_id']
            exec_sys['class'] = conf['class']
            if "drm_options" in conf:
                exec_sys["drm_options"] = conf["drm_options"]
            if "native_specifications" in conf:
                exec_sys["native_specifications"] = conf["native_specifications"]
            exec_sys.save()
        
        conf = { "execution_systems" : [{"_id" : "big_one",
                                         "class" : "OgsDRMAA",
                                         "drm_options" : {"drmaa_library_path" : "path/to/sge/libdrmaa.so",
                                                          "cell" : '/usr/local/sge',
                                                          "root" : 'default', 
                                                          },
                                         "native_specifications": " -q mobyle-long " 
                                         },
                                        {"_id" : "small_one",
                                         "class" : "OgsDRMAA", 
                                         "drm_options" : {"drmaa_library_path" : "path/to/sge/libdrmaa.so",
                                                          "cell" : '/usr/local/sge',
                                                          "root" : 'default' 
                                                          },
                                         "native_specifications": " -q mobyle-small " 
                                         },
                                        {"_id" : "cluster_two",
                                         "class" : "TorqueDRMAA", 
                                         "drm_options" : {"drmaa_library_path" : "path/to/torque/libdrmaa.so",
                                                          "server_name" : "localhost" 
                                                          },
                                         "native_specifications": " -q mobyle-small " 
                                         },
                                        {"_id" : "local",
                                         "class" : "Local",
                                         "native_specifications" : " nice -n 18 "
                                         }]
                }
        for exec_sys in conf["execution_systems"]:
            push_exec_sys_in_db(exec_sys)

    def test_insert_N_get(self):
        map = [ {"name": "route_1", 
                          "rules" : [{"name" : u"user_is_local"} , {"name" : u"job_name_match", 
                                                                   "parameters" : {u"name": u"Filochard"}
                                                                   }
                                     ],
                          "exec_system" : "big_one" 
                                      },
                         {"name" :"route_2",
                          "rules" : [{"name" : "project_match", "parameters" : {"name": u"dans le cambouis"}} ],
                          "exec_system" : "small_one" 
                         },
                         {"name" : "default",
                          "rules" : [],
                          "exec_system" : "cluster_two" 
                          }
                        ]
        
        routes = connection.ExecutionRoutes()
        routes["map"] = map
        _id = "to compare rcv and send"
        routes["_id"] = _id
        routes.save()
        
        map_received = connection.ExecutionRoutes.find_one({})
        del map_received[u'_type']
        map_send = {"map":map,
                    "_id" : _id}
        self.assertDictEqual(map_send, map_received)
        
if __name__ == '__main__':
    unittest.main()

