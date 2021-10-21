import data as d
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

	data = None
	results = None
	
	def __init__(self, config, apikey, tbakey, timestamp, teams):
		self.config = config
		self.apikey = apikey
		self.tbakey = tbakey
		self.timestamp = timestamp
		self.teams = teams

	def validate_config(self):
		if self.config == None:
			return "config cannot be empty"
		elif self.apikey == None or self.apikey == "":
			return "apikey cannot be empty"
		elif self.tbakey == None or self.tbakey == "":
			return "tbakey cannot be empty"
		elif not(self.config["scope"] in ["competition", "season", "none"]):
			return "scope must be one of: (competition, season, none)"
		elif not(self.config["agglomeration"] in ["none", "mean"]):
			return "agglomeration must be one of: (none, mean)"
		else:
			return None

	def load_data(self):
		pass

	def process_data(self, exec_threads):
		pass

	def push_results(self):
		pass