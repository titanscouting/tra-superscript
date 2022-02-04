import abc
import data as d
import signal
import numpy as np
from tra_analysis import Analysis as an

class Module(metaclass = abc.ABCMeta):

	@classmethod
	def __subclasshook__(cls, subclass):
		return (hasattr(subclass, '__init__') and 
				callable(subclass.__init__) and 
				hasattr(subclass, 'validate_config') and 
				callable(subclass.validate_config) and
				hasattr(subclass, 'run') and 
				callable(subclass.run)
				)
	@abc.abstractmethod
	def __init__(self, config, apikey, tbakey, timestamp, competition, *args, **kwargs):
		raise NotImplementedError
	@abc.abstractmethod
	def validate_config(self, *args, **kwargs):
		raise NotImplementedError
	@abc.abstractmethod
	def run(self, exec_threads, *args, **kwargs):
		raise NotImplementedError

class Match (Module):

	config = None
	apikey = None
	tbakey = None
	timestamp = None
	competition = None

	data = None
	results = None
	
	def __init__(self, config, apikey, tbakey, timestamp, competition):
		self.config = config
		self.apikey = apikey
		self.tbakey = tbakey
		self.timestamp = timestamp
		self.competition = competition

	def validate_config(self):
		return True, ""

	def run(self, exec_threads):
		self._load_data()
		self._process_data(exec_threads)
		self._push_results()

	def _load_data(self):
		self.data = d.load_match(self.apikey, self.competition)

	def _simplestats(self, data_test):

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

	def _process_data(self, exec_threads):

		tests = self.config["tests"]
		data = self.data

		input_vector = []

		for team in data:

			for variable in data[team]:

				if variable in tests:

					for test in tests[variable]:

						input_vector.append((team, variable, test, data[team][variable]))

		self.data = input_vector
		#self.results = list(exec_threads.map(self._simplestats, self.data))
		self.results = []
		for test_var_data in self.data:
			self.results.append(self._simplestats(test_var_data))

	def _push_results(self):

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

class Metric (Module):

	config = None
	apikey = None
	tbakey = None
	timestamp = None
	competition = None

	data = None
	results = None
	
	def __init__(self, config, apikey, tbakey, timestamp, competition):
		self.config = config
		self.apikey = apikey
		self.tbakey = tbakey
		self.timestamp = timestamp
		self.competition = competition

	def validate_config(self):
		return True, ""

	def run(self, exec_threads):
		self._load_data()
		self._process_data(exec_threads)
		self._push_results()

	def _load_data(self):
		self.data = d.pull_new_tba_matches(self.tbakey, self.competition, self.timestamp)

	def _process_data(self, exec_threads):

		elo_N = self.config["tests"]["elo"]["N"]
		elo_K = self.config["tests"]["elo"]["K"]

		matches = self.data

		red = {}
		blu = {}

		for match in matches:

			red = d.load_metric(self.apikey, self.competition, match, "red", self.config["tests"])
			blu = d.load_metric(self.apikey, self.competition, match, "blue", self.config["tests"])
	
			elo_red_total = 0
			elo_blu_total = 0

			gl2_red_score_total = 0
			gl2_blu_score_total = 0

			gl2_red_rd_total = 0
			gl2_blu_rd_total = 0

			gl2_red_vol_total = 0
			gl2_blu_vol_total = 0

			for team in red:

				elo_red_total += red[team]["elo"]["score"]

				gl2_red_score_total += red[team]["gl2"]["score"]
				gl2_red_rd_total += red[team]["gl2"]["rd"]
				gl2_red_vol_total += red[team]["gl2"]["vol"]

			for team in blu:

				elo_blu_total += blu[team]["elo"]["score"]

				gl2_blu_score_total += blu[team]["gl2"]["score"]
				gl2_blu_rd_total += blu[team]["gl2"]["rd"]
				gl2_blu_vol_total += blu[team]["gl2"]["vol"]

			red_elo = {"score": elo_red_total / len(red)}
			blu_elo = {"score": elo_blu_total / len(blu)}

			red_gl2 = {"score": gl2_red_score_total / len(red), "rd": gl2_red_rd_total / len(red), "vol": gl2_red_vol_total / len(red)}
			blu_gl2 = {"score": gl2_blu_score_total / len(blu), "rd": gl2_blu_rd_total / len(blu), "vol": gl2_blu_vol_total / len(blu)}


			if match["winner"] == "red":

				observations = {"red": 1, "blu": 0}

			elif match["winner"] == "blue":

				observations = {"red": 0, "blu": 1}

			else:

				observations = {"red": 0.5, "blu": 0.5}

			red_elo_delta = an.Metric().elo(red_elo["score"], blu_elo["score"], observations["red"], elo_N, elo_K) - red_elo["score"]
			blu_elo_delta = an.Metric().elo(blu_elo["score"], red_elo["score"], observations["blu"], elo_N, elo_K) - blu_elo["score"]

			new_red_gl2_score, new_red_gl2_rd, new_red_gl2_vol = an.Metric().glicko2(red_gl2["score"], red_gl2["rd"], red_gl2["vol"], [blu_gl2["score"]], [blu_gl2["rd"]], [observations["red"], observations["blu"]])
			new_blu_gl2_score, new_blu_gl2_rd, new_blu_gl2_vol = an.Metric().glicko2(blu_gl2["score"], blu_gl2["rd"], blu_gl2["vol"], [red_gl2["score"]], [red_gl2["rd"]], [observations["blu"], observations["red"]])

			red_gl2_delta = {"score": new_red_gl2_score - red_gl2["score"], "rd": new_red_gl2_rd - red_gl2["rd"], "vol": new_red_gl2_vol - red_gl2["vol"]}
			blu_gl2_delta = {"score": new_blu_gl2_score - blu_gl2["score"], "rd": new_blu_gl2_rd - blu_gl2["rd"], "vol": new_blu_gl2_vol - blu_gl2["vol"]}

			for team in red:

				red[team]["elo"]["score"] = red[team]["elo"]["score"] + red_elo_delta

				red[team]["gl2"]["score"] = red[team]["gl2"]["score"] + red_gl2_delta["score"]
				red[team]["gl2"]["rd"] = red[team]["gl2"]["rd"] + red_gl2_delta["rd"]
				red[team]["gl2"]["vol"] = red[team]["gl2"]["vol"] + red_gl2_delta["vol"]

			for team in blu:

				blu[team]["elo"]["score"] = blu[team]["elo"]["score"] + blu_elo_delta

				blu[team]["gl2"]["score"] = blu[team]["gl2"]["score"] + blu_gl2_delta["score"]
				blu[team]["gl2"]["rd"] = blu[team]["gl2"]["rd"] + blu_gl2_delta["rd"]
				blu[team]["gl2"]["vol"] = blu[team]["gl2"]["vol"] + blu_gl2_delta["vol"]

			temp_vector = {}
			temp_vector.update(red)
			temp_vector.update(blu)

			d.push_metric(self.apikey, self.competition, temp_vector)

	def _push_results(self):
		pass

class Pit (Module):

	config = None
	apikey = None
	tbakey = None
	timestamp = None
	competition = None

	data = None
	results = None
	
	def __init__(self, config, apikey, tbakey, timestamp, competition):
		self.config = config
		self.apikey = apikey
		self.tbakey = tbakey
		self.timestamp = timestamp
		self.competition = competition
	
	def validate_config(self):
		return True, ""

	def run(self, exec_threads):
		self._load_data()
		self._process_data(exec_threads)
		self._push_results()

	def _load_data(self):
		self.data = d.load_pit(self.apikey, self.competition)

	def _process_data(self, exec_threads):
		tests = self.config["tests"]
		print(tests)
		return_vector = {}
		for team in self.data:
			for variable in self.data[team]:
				if variable in tests:
					if not variable in return_vector:
						return_vector[variable] = []
					return_vector[variable].append(self.data[team][variable])

		self.results = return_vector

	def _push_results(self):
		d.push_pit(self.apikey, self.competition, self.results)

class Rating (Module):
	pass

class Heatmap (Module):
	pass

class Sentiment (Module):
	pass