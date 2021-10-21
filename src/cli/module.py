import data as d

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
					match_data = d.get_team_match_data(self.apikey, competition, team) # needs modified implementation
					self.data.append((team, competition, variable, match_data))

	def process_data(self, exec_threads):
		pass

	def push_results(self):
		pass