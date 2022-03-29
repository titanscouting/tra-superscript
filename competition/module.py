import abc
import data as d
import signal
import numpy as np
from tra_analysis import Analysis as an
from tqdm import tqdm

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
	def run(self, *args, **kwargs):
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

	def run(self):
		self._load_data()
		self._process_data()
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

	def _process_data(self):

		tests = self.config["tests"]
		data = self.data

		input_vector = []

		for team in data:

			for variable in data[team]:

				if variable in tests:

					for test in tests[variable]:

						input_vector.append((team, variable, test, data[team][variable]))

		self.data = input_vector
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

	def run(self):
		self._load_data()
		self._process_data()
		self._push_results()

	def _load_data(self):
		self.data = d.pull_new_tba_matches(self.tbakey, self.competition, self.timestamp)

	def _process_data(self):

		self.results = {}

		matches = self.data

		red = {}
		blu = {}
		for match in tqdm(matches, desc="Metrics"): # grab matches and loop through each one
			red = d.load_metric(self.apikey, self.competition, match, "red", self.config["tests"]) # get the current ratings for red
			blu = d.load_metric(self.apikey, self.competition, match, "blue", self.config["tests"]) # get the current ratings for blue

			gl2_red_score_total = 0
			gl2_blu_score_total = 0

			gl2_red_rd_total = 0
			gl2_blu_rd_total = 0

			gl2_red_vol_total = 0
			gl2_blu_vol_total = 0

			for team in red: # for each team in red, add up gl2 score components

				gl2_red_score_total += red[team]["gl2"]["score"]
				gl2_red_rd_total += red[team]["gl2"]["rd"]
				gl2_red_vol_total += red[team]["gl2"]["vol"]

			for team in blu: # for each team in blue, add up gl2 score components

				gl2_blu_score_total += blu[team]["gl2"]["score"]
				gl2_blu_rd_total += blu[team]["gl2"]["rd"]
				gl2_blu_vol_total += blu[team]["gl2"]["vol"]


			red_gl2 = {"score": gl2_red_score_total / len(red), "rd": gl2_red_rd_total / len(red), "vol": gl2_red_vol_total / len(red)} # average the scores by dividing by 3
			blu_gl2 = {"score": gl2_blu_score_total / len(blu), "rd": gl2_blu_rd_total / len(blu), "vol": gl2_blu_vol_total / len(blu)} # average the scores by dividing by 3


			if match["winner"] == "red": # if red won, set observations to {"red": 1, "blu": 0}

				observations = {"red": 1, "blu": 0}

			elif match["winner"] == "blue": # if blue won, set observations to {"red": 0, "blu": 1}

				observations = {"red": 0, "blu": 1}

			else: # otherwise it was a tie and observations is {"red": 0.5, "blu": 0.5}

				observations = {"red": 0.5, "blu": 0.5}


			new_red_gl2_score, new_red_gl2_rd, new_red_gl2_vol = an.Metric().glicko2(red_gl2["score"], red_gl2["rd"], red_gl2["vol"], [blu_gl2["score"]], [blu_gl2["rd"]], [observations["red"], observations["blu"]]) # calculate new scores for gl2 for red
			new_blu_gl2_score, new_blu_gl2_rd, new_blu_gl2_vol = an.Metric().glicko2(blu_gl2["score"], blu_gl2["rd"], blu_gl2["vol"], [red_gl2["score"]], [red_gl2["rd"]], [observations["blu"], observations["red"]]) # calculate new scores for gl2 for blue

			red_gl2_delta = {"score": new_red_gl2_score - red_gl2["score"], "rd": new_red_gl2_rd - red_gl2["rd"], "vol": new_red_gl2_vol - red_gl2["vol"]} # calculate gl2 deltas for red
			blu_gl2_delta = {"score": new_blu_gl2_score - blu_gl2["score"], "rd": new_blu_gl2_rd - blu_gl2["rd"], "vol": new_blu_gl2_vol - blu_gl2["vol"]} # calculate gl2 deltas for blue

			for team in red: # for each team on red, add the previous score with the delta to find the new score

				red[team]["gl2"]["score"] = red[team]["gl2"]["score"] + red_gl2_delta["score"]
				red[team]["gl2"]["rd"] = red[team]["gl2"]["rd"] + red_gl2_delta["rd"]
				red[team]["gl2"]["vol"] = red[team]["gl2"]["vol"] + red_gl2_delta["vol"]

			for team in blu: # for each team on blue, add the previous score with the delta to find the new score

				blu[team]["gl2"]["score"] = blu[team]["gl2"]["score"] + blu_gl2_delta["score"]
				blu[team]["gl2"]["rd"] = blu[team]["gl2"]["rd"] + blu_gl2_delta["rd"]
				blu[team]["gl2"]["vol"] = blu[team]["gl2"]["vol"] + blu_gl2_delta["vol"]

			temp_vector = {}
			temp_vector.update(red) # update the team's score with the temporay vector
			temp_vector.update(blu)

			self.results[match['match']] = temp_vector

			d.push_metric(self.apikey, self.competition, temp_vector) # push new scores to db

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

	def run(self):
		self._load_data()
		self._process_data()
		self._push_results()

	def _load_data(self):
		self.data = d.load_pit(self.apikey, self.competition)

	def _process_data(self):
		tests = self.config["tests"]
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