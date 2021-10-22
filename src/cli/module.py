import data as d
import signal
import numpy as np
import tra_analysis as an

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
	competition = None

	data = []
	results = []
	
	def __init__(self, config, apikey, tbakey, timestamp, competition):
		self.config = config
		self.apikey = apikey
		self.tbakey = tbakey
		self.timestamp = timestamp
		self.competition = competition

	def validate_config(self):
		return True, ""

	def load_data(self):
		self.data = d.load_match(self.apikey, self.competition)

	def simplestats(data_test):

		signal.signal(signal.SIGINT, signal.SIG_IGN)

		data = np.array(data_test[3])
		data = data[np.isfinite(data)]
		ranges = list(range(len(data)))

		test = data_test[2]

		if test == "basic_stats":
			return an.basic_stats(data)

		if test == "historical_analysis":
			return an.histo_analysis([ranges, data])

		if test == "regression_linear":
			return an.regression(ranges, data, ['lin'])

		if test == "regression_logarithmic":
			return an.regression(ranges, data, ['log'])

		if test == "regression_exponential":
			return an.regression(ranges, data, ['exp'])

		if test == "regression_polynomial":
			return an.regression(ranges, data, ['ply'])

		if test == "regression_sigmoidal":
			return an.regression(ranges, data, ['sig'])

	def process_data(self, exec_threads):

		tests = self.config["tests"]
		data = self.data

		input_vector = []

		for team in data:

			for variable in data[team]:

				if variable in tests:

					for test in tests[variable]:

						input_vector.append((team, variable, test, data[team][variable]))

		self.data = input_vector
		self.results = list(exec_threads.map(self.simplestats, self.data))

	def push_results(self):

		short_mapping = {"regression_linear": "lin", "regression_logarithmic": "log", "regression_exponential": "exp", "regression_polynomial": "ply", "regression_sigmoidal": "sig"}

		class AutoVivification(dict):
			def __getitem__(self, item):
				try:
					return dict.__getitem__(self, item)
				except KeyError:
					value = self[item] = type(self)()
					return value

		result_filtered = self.results
		input_vector = self.data

		return_vector = AutoVivification()

		i = 0

		for result in result_filtered:

			filtered = input_vector[i][2]

			try:
				short = short_mapping[filtered]
				return_vector[input_vector[i][0]][input_vector[i][1]][input_vector[i][2]] = result[short]
			except KeyError: # not in mapping
				return_vector[input_vector[i][0]][input_vector[i][1]][input_vector[i][2]] = result

			i += 1

		self.results = return_vector

		d.push_match(self.apikey, self.competition, self.results)