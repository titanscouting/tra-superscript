import data as d
import signal
import numpy as np
import tra_analysis as an

class AutoVivification(dict):
		def __getitem__(self, item):
			try:
				return dict.__getitem__(self, item)
			except KeyError:
				value = self[item] = type(self)()
				return value

class Module:
	config = None
	data = None
	results = None
	def __init__(self, config, apikey, tbakey, timestamp):
		pass
	def validate_config(self):
		pass
	def load_data(self):
		pass
	def process_data(self, exec_threads):
		pass
	def push_results(self):
		pass

class Match:
	config = None
	apikey = None
	tbakey = None
	timestamp = None
	teams = None

	data = []
	results = []
	
	def __init__(self, config, apikey, tbakey, timestamp, teams):
		self.config = config
		self.apikey = apikey
		self.tbakey = tbakey
		self.timestamp = timestamp
		self.teams = teams

	def validate_config(self):
		return True, ""
		"""
		if self.config == None:
			return False, "config cannot be empty"
		elif self.apikey == None or self.apikey == "":
			return False, "apikey cannot be empty"
		elif self.tbakey == None or self.tbakey == "":
			return False, "tbakey cannot be empty"
		elif not(self.config["scope"] in ["competition", "season", "none"]):
			return False, "scope must be one of: (competition, season, none)"
		elif not(self.config["agglomeration"] in ["none", "mean"]):
			return False, "agglomeration must be one of: (none, mean)"
		else:
			return True, ""
		"""

	def load_data(self):
		scope = self.config["scope"]
		for team in self.teams:
			competitions = d.get_team_conpetitions(self.apikey, team, scope) # unimplemented
			for competition in competitions:
				for variable in self.config["tests"]:
					match_data = d.get_team_match_data(self.apikey, competition, team, variable) # needs modified implementation
					variable_tests = self.config["tests"][variable]
					self.data.append({"team": team, "competition": competition, "variable": variable, "tests": variable_tests, "data": match_data})

	def tests(test_data):
		signal.signal(signal.SIGINT, signal.SIG_IGN)

		if(test_data["data"] == None):
			return None

		data = np.array(test_data["data"])
		data = data[np.isfinite(data)]
		ranges = list(range(len(data)))

		tests = test_data["tests"]

		results = AutoVivification()

		if "basic_stats" in tests:
			results["basic_stats"] = an.basic_stats(data)
		if "historical_analysis" in tests:
			results["historical_analysis"] = an.histo_analysis([ranges, data])
		if "regression_linear" in tests:
			results["regression_linear"] = an.regression(ranges, data, ['lin'])
		if "regression_logarithmic" in tests:
			results["regression_logarithmic"] = an.regression(ranges, data, ['log'])
		if "regression_exponential" in tests:
			results["regression_exponential"] = an.regression(ranges, data, ['exp'])
		if "regression_polynomial" in tests:
			results["regression_polynomial"] = an.regression(ranges, data, ['ply'])
		if "regression_sigmoidal" in tests:
			results["regression_sigmoidal"] = an.regression(ranges, data, ['sig'])

		return results

	def process_data(self, exec_threads):
		self.results = list(exec_threads.map(self.tests, self.data))

	def push_results(self):
		short_mapping = {"regression_linear": "lin", "regression_logarithmic": "log", "regression_exponential": "exp", "regression_polynomial": "ply", "regression_sigmoidal": "sig"}
		results_short = AutoVivification()
		i = 0
		for result in self.results:
			for variable in result:
				if variable in short_mapping:
					short = short_mapping[variable]
				else:
					short = variable
					d.push_team_match_results(self.data[i]["team"], self.data[i]["competition"], self.data[i]["variable"], short, result[variable])
				#results_short[ self.data["team"] ][ self.data["competition"] ][ self.data["variable"] ][short] = result[variable]
			i+=1