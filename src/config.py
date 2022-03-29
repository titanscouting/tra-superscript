import json
from exceptions import ConfigurationError
from cerberus import Validator

from data import set_database_config, get_database_config

class Configuration:

	path = None
	config = {}

	_sample_config = {
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
			"synchronize-config":False
		},
		"variable":{
			"event-delay":False,
			"loop-delay":0,
			"competition": "2020ilch",
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
						"wheel-mechanism":True,
						"low-balls":True,
						"high-balls":True,
						"wheel-success":True,
						"strategic-focus":True,
						"climb-mechanism":True,
						"attitude":True
					}
				}
			}
		}
	}

	_validation_schema = {
		"persistent": {
			"type": "dict",
			"required": True,
			"require_all": True,
			"schema": {
				"key": {
					"type": "dict",
					"require_all":True,
					"schema": {
						"database": {"type":"string"},
						"tba": {"type": "string"},
						"tra": {
							"type": "dict",
							"require_all": True,
							"schema": {
								"CLIENT_ID": {"type": "string"},
								"CLIENT_SECRET": {"type": "string"},
								"url": {"type": "string"}
							}
						}
					}
				},
				"config-preference": {"type": "string", "required": True},
				"synchronize-config": {"type": "boolean", "required": True}
			}
		}
	}	

	def __init__(self, path):
		self.path = path
		self.load_config()
		self.validate_config()

	def load_config(self):
		try:
			f = open(self.path, "r")
			self.config.update(json.load(f))
			f.close()
		except:
			self.config = self._sample_config
			self.save_config()
			f.close()
			raise ConfigurationError("could not find config file at <" + self.path + ">, created new sample config file at that path")

	def save_config(self):
		f = open(self.path, "w+")
		json.dump(self.config, f, ensure_ascii=False, indent=4)
		f.close()

	def validate_config(self):
		v = Validator(self._validation_schema, allow_unknown = True)
		isValidated = v.validate(self.config)

		if not isValidated:
			raise ConfigurationError("config validation error: " + v.errors)

	def __getattr__(self, name): # better hashed lookup method for common multikey-value paths, TYPE UNSAFE
		attr_lookup = {
			"persistent": self.config["persistent"],
			"key": self.config["persistent"]["key"],
			"database": self.config["persistent"]["key"]["database"],
			"tba": self.config["persistent"]["key"]["tba"],
			"tra": self.config["persistent"]["key"]["tra"],
			"priority": self.config["persistent"]["config-preference"],
			"sync": self.config["persistent"]["synchronize-config"],
			"variable": self.config["variable"],
			"event_delay": self.config["variable"]["event-delay"],
			"loop_delay": self.config["variable"]["loop-delay"],
			"competition": self.config["variable"]["competition"],
			"modules": self.config["variable"]["modules"]
		}
		if name in attr_lookup.keys():
			return attr_lookup[name]
		else:
			return None

	def __getitem__(self, key):
		return self.config[key]

	def resolve_config_conflicts(self, logger, client): # needs improvement with new localization scheme
		sync = self.sync
		priority = self.priority

		if sync:
			if priority == "local" or priority == "client":
				logger.info("config-preference set to local/client, loading local config information")
				remote_config = get_database_config(client)
				if remote_config != self.config["variable"]:
					set_database_config(client, self.config["variable"])
					logger.info("database config was different and was updated")
				# no change to config
			elif priority == "remote" or priority == "database":
				logger.info("config-preference set to remote/database, loading remote config information")
				remote_config = get_database_config(client)
				if remote_config != self.config["variable"]:
					self.config["variable"] = remote_config
					self.save_config()
					# change variable to match remote
					logger.info("local config was different and was updated")
			else:
				raise ConfigurationError("persistent/config-preference field must be \"local\"/\"client\" or \"remote\"/\"database\"")
		else:
			if priority == "local" or priority == "client":
				logger.info("config-preference set to local/client, loading local config information")
				# no change to config
			elif priority == "remote" or priority == "database":
				logger.info("config-preference set to remote/database, loading database config information")
				self.config["variable"] = get_database_config(client)
				# change variable to match remote without updating local version
			else:
				raise ConfigurationError("persistent/config-preference field must be \"local\"/\"client\" or \"remote\"/\"database\"")