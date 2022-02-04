import math
import json
from multiprocessing import Pool
import os
from cerberus import Validator
from exceptions import ConfigurationError

from data import set_database_config, get_database_config
from interface import stderr, stdout, INF, ERR

config_path = "config.json"

sample_json = """
{
   "persistent":{
      "key":{
         "database":"",
         "tba":"",
         "tra":{
            "CLIENT_ID":"",
            "CLIENT_SECRET":"",
			"url": ""
         }
      },
      "config-preference":"local",
      "synchronize-config":false
   },
   "variable":{
      "max-threads":0.5,
      "team":"",
      "event-delay":false,
      "loop-delay":0,
      "reportable":true,
      "teams":[
         
      ],
      "modules":{
         "match":{
            "tests":{
               "balls-blocked":[
                  "basic_stats",
                  "historical_analysis",
                  "regression_linear",
                  "regression_logarithmic",
                  "regression_exponential",
                  "regression_polynomial",
                  "regression_sigmoidal"
               ],
               "balls-collected":[
                  "basic_stats",
                  "historical_analysis",
                  "regression_linear",
                  "regression_logarithmic",
                  "regression_exponential",
                  "regression_polynomial",
                  "regression_sigmoidal"
               ],
               "balls-lower-teleop":[
                  "basic_stats",
                  "historical_analysis",
                  "regression_linear",
                  "regression_logarithmic",
                  "regression_exponential",
                  "regression_polynomial",
                  "regression_sigmoidal"
               ],
               "balls-lower-auto":[
                  "basic_stats",
                  "historical_analysis",
                  "regression_linear",
                  "regression_logarithmic",
                  "regression_exponential",
                  "regression_polynomial",
                  "regression_sigmoidal"
               ],
               "balls-started":[
                  "basic_stats",
                  "historical_analyss",
                  "regression_linear",
                  "regression_logarithmic",
                  "regression_exponential",
                  "regression_polynomial",
                  "regression_sigmoidal"
               ],
               "balls-upper-teleop":[
                  "basic_stats",
                  "historical_analysis",
                  "regression_linear",
                  "regression_logarithmic",
                  "regression_exponential",
                  "regression_polynomial",
                  "regression_sigmoidal"
               ],
               "balls-upper-auto":[
                  "basic_stats",
                  "historical_analysis",
                  "regression_linear",
                  "regression_logarithmic",
                  "regression_exponential",
                  "regression_polynomial",
                  "regression_sigmoidal"
               ]
            }
         },
         "metric":{
            "tests":{
               "elo":{
                  "score":1500,
                  "N":400,
                  "K":24
               },
               "gl2":{
                  "score":1500,
                  "rd":250,
                  "vol":0.06
               },
               "ts":{
                  "mu":25,
                  "sigma":8.33
               }
            }
         },
         "pit":{
            "tests":{
               "wheel-mechanism":true,
               "low-balls":true,
               "high-balls":true,
               "wheel-success":true,
               "strategic-focus":true,
               "climb-mechanism":true,
               "attitude":true
            }
         }
      }
   }
}
"""

def parse_config_persistent(send, config):
	v = Validator(load_validation_schema(), allow_unknown = True)
	isValidated = v.validate(config)

	if not isValidated:
		raise ConfigurationError(v.errors, 101)

	apikey = config["persistent"]["key"]["database"]
	tbakey = config["persistent"]["key"]["tba"]
	preference = config["persistent"]["config-preference"]
	sync = config["persistent"]["synchronize-config"]

	return apikey, tbakey, preference, sync

def parse_config_variable(send, config):

	sys_max_threads = os.cpu_count()
	try:
		cfg_max_threads = config["variable"]["max-threads"]
	except:
		raise ConfigurationError("variable/max-threads field is invalid or missing, refer to documentation for configuration options", 109)
	if cfg_max_threads > -sys_max_threads and cfg_max_threads < 0 :
		alloc_processes = sys_max_threads + cfg_max_threads
	elif cfg_max_threads > 0 and cfg_max_threads < 1:
		alloc_processes = math.floor(cfg_max_threads * sys_max_threads)
	elif cfg_max_threads > 1 and cfg_max_threads <= sys_max_threads:
		alloc_processes = cfg_max_threads
	elif cfg_max_threads == 0:
		alloc_processes = sys_max_threads
	else:
		raise ConfigurationError("variable/max-threads must be between -" + str(sys_max_threads) + " and " + str(sys_max_threads) + ", but got " + cfg_max_threads, 110)
	try:
		exec_threads = Pool(processes = alloc_processes)
	except Exception as e:
		send(stderr, INF, e)
		raise ConfigurationError("unable to start threads", 200)
	send(stdout, INF, "successfully initialized " + str(alloc_processes) + " threads")

	try:
		modules = config["variable"]["modules"]
	except:
		raise ConfigurationError("variable/modules field is invalid or missing", 102)

	if modules == None:
		raise ConfigurationError("variable/modules field is empty", 106)

	send(stdout, INF, "found and loaded competition, match, metrics, pit from config")

	return exec_threads, modules

def resolve_config_conflicts(send, client, config, preference, sync):

	if sync:
		if preference == "local" or preference == "client":
			send(stdout, INF, "config-preference set to local/client, loading local config information")
			remote_config = get_database_config(client)
			if remote_config != config["variable"]:
				set_database_config(client, config["variable"])
				send(stdout, INF, "database config was different and was updated")
			return config
		elif preference == "remote" or preference == "database":
			send(stdout, INF, "config-preference set to remote/database, loading remote config information")
			remote_config= get_database_config(client)
			if remote_config != config["variable"]:
				config["variable"] = remote_config
				if save_config(config_path, config):
					raise ConfigurationError("local config was different but could not be updated", 121)
				send(stdout, INF, "local config was different and was updated")
			return config
		else:
			raise ConfigurationError("persistent/config-preference field must be \"local\"/\"client\" or \"remote\"/\"database\"", 120)
	else:
		if preference == "local" or preference == "client":
			send(stdout, INF, "config-preference set to local/client, loading local config information")
			return config
		elif preference == "remote" or preference == "database":
			send(stdout, INF, "config-preference set to remote/database, loading database config information")
			config["variable"] = get_database_config(client)
			return config
		else:
			raise ConfigurationError("persistent/config-preference field must be \"local\"/\"client\" or \"remote\"/\"database\"", 120)

def load_config(path, config_vector):
	try:
		f = open(path, "r")
		config_vector.update(json.load(f))
		f.close()
		return 0
	except:
		f = open(path, "w")
		f.write(sample_json)
		f.close()
		return 1

def load_validation_schema():
	try:
		with open("validation-schema.json", "r") as f:
			return json.load(f)
	except:
		raise FileNotFoundError("Validation schema not found at validation-schema.json")

def save_config(path, config_vector):
	f = open(path, "w+")
	json.dump(config_vector, f, ensure_ascii=False, indent=4)
	f.close()
	return 0