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
		return True

	def load_data(self):
		pass

	def process_data(self, exec_threads):
		pass

	def push_results(self):
		pass