# Titan Robotics Team 2022: Superscript Script
# Written by Arthur Lu, Jacob Levine, and Dev Singh
# Notes:
# setup:

__version__ = "0.0.6.002"

# changelog should be viewed using print(analysis.__changelog__)
__changelog__ = """changelog:
	0.0.6.003:
		- rename analysis imports to tra_analysis for PyPI publishing
	0.0.6.002:
		- integrated get_team_rankings.py as get_team_metrics() function
		- integrated visualize_pit.py as graph_pit_histogram() function
	0.0.6.001:
		- bug fixes with analysis.Metric() calls
		- modified metric functions to use config.json defined default values
	0.0.6.000:
		- removed main function
		- changed load_config function
		- added save_config function
		- added load_match function
		- renamed simpleloop to matchloop
		- moved simplestats function inside matchloop
		- renamed load_metrics to load_metric
		- renamed metricsloop to metricloop
		- split push to database functions amon push_match, push_metric, push_pit
		- moved
	0.0.5.002:
		- made changes due to refactoring of analysis
	0.0.5.001:
		- text fixes
		- removed matplotlib requirement
	0.0.5.000:
		- improved user interface
	0.0.4.002:
		- removed unessasary code
	0.0.4.001:
		- fixed bug where X range for regression was determined before sanitization
		- better sanitized data
	0.0.4.000:
		- fixed spelling issue in __changelog__
		- addressed nan bug in regression
		- fixed errors on line 335 with metrics calling incorrect key "glicko2"
		- fixed errors in metrics computing 
	0.0.3.000:
		- added analysis to pit data
	0.0.2.001:
		- minor stability patches
		- implemented db syncing for timestamps
		- fixed bugs
	0.0.2.000:
		- finalized testing and small fixes
	0.0.1.004:
		- finished metrics implement, trueskill is bugged
	0.0.1.003:
		- working
	0.0.1.002:
		- started implement of metrics
	0.0.1.001:
		- cleaned up imports
	0.0.1.000:
		- tested working, can push to database
	0.0.0.009:
		- tested working
		- prints out stats for the time being, will push to database later
	0.0.0.008:
		- added data import
		- removed tba import
		- finished main method
	0.0.0.007:
		- added load_config
		- optimized simpleloop for readibility
		- added __all__ entries
		- added simplestats engine
		- pending testing
	0.0.0.006:
		- fixes
	0.0.0.005:
		- imported pickle
		- created custom database object
	0.0.0.004:
		- fixed simpleloop to actually return a vector
	0.0.0.003:
		- added metricsloop which is unfinished
	0.0.0.002:
		- added simpleloop which is untested until data is provided
	0.0.0.001:
		- created script
		- added analysis, numba, numpy imports
"""

__author__ = (
	"Arthur Lu <learthurgo@gmail.com>",
	"Jacob Levine <jlevine@imsa.edu>",
)

__all__ = [
	"load_config",
	"save_config",
	"get_previous_time",
	"load_match",
	"matchloop",
	"load_metric",
	"metricloop",
	"load_pit",
	"pitloop",
	"push_match",
	"push_metric",
	"push_pit",
]

# imports:

from tra_analysis import analysis as an
import data as d
import json
import numpy as np
from os import system, name
from pathlib import Path
import matplotlib.pyplot as plt
import time
import warnings

def load_config(file):

	config_vector = {}
	with open(file) as f:
		config_vector = json.load(f)

	return config_vector

def save_config(file, config_vector):

	with open(file) as f:
		json.dump(config_vector, f)

def get_previous_time(apikey):

	previous_time = d.get_analysis_flags(apikey, "latest_update")

	if previous_time == None:

		d.set_analysis_flags(apikey, "latest_update", 0)
		previous_time = 0

	else:

		previous_time = previous_time["latest_update"]

	return previous_time

def load_match(apikey, competition):

	return d.get_match_data_formatted(apikey, competition)

def matchloop(apikey, competition, data, tests): # expects 3D array with [Team][Variable][Match]

	def simplestats(data, test):

		data = np.array(data)
		data = data[np.isfinite(data)]
		ranges = list(range(len(data)))

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

	return_vector = {}
	for team in data:
		variable_vector = {}
		for variable in data[team]:
			test_vector = {}
			variable_data = data[team][variable]
			if variable in tests:
				for test in tests[variable]:
					test_vector[test] = simplestats(variable_data, test)
			else:
				pass      
			variable_vector[variable] = test_vector
		return_vector[team] = variable_vector

	push_match(apikey, competition, return_vector)

def load_metric(apikey, competition, match, group_name, metrics):

	group = {}

	for team in match[group_name]:

		db_data = d.get_team_metrics_data(apikey, competition, team)

		if d.get_team_metrics_data(apikey, competition, team) == None:

			elo = {"score": metrics["elo"]["score"]}
			gl2 = {"score": metrics["gl2"]["score"], "rd": metrics["gl2"]["rd"], "vol": metrics["gl2"]["vol"]}
			ts = {"mu": metrics["ts"]["mu"], "sigma": metrics["ts"]["sigma"]}

			group[team] = {"elo": elo, "gl2": gl2, "ts": ts}

		else:

			metrics = db_data["metrics"]

			elo = metrics["elo"]
			gl2 = metrics["gl2"]
			ts = metrics["ts"]

			group[team] = {"elo": elo, "gl2": gl2, "ts": ts}

	return group

def metricloop(tbakey, apikey, competition, timestamp, metrics): # listener based metrics update

	elo_N = metrics["elo"]["N"]
	elo_K = metrics["elo"]["K"]

	matches = d.pull_new_tba_matches(tbakey, competition, timestamp)

	red = {}
	blu = {}

	for match in matches:

		red = load_metric(apikey, competition, match, "red", metrics)
		blu = load_metric(apikey, competition, match, "blue", metrics)
 
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

		push_metric(apikey, competition, temp_vector)

def load_pit(apikey, competition):

	return d.get_pit_data_formatted(apikey, competition)

def pitloop(apikey, competition, pit, tests):

	return_vector = {}
	for team in pit:
		for variable in pit[team]:
			if variable in tests:
				if not variable in return_vector:
					return_vector[variable] = []
				return_vector[variable].append(pit[team][variable])

	push_pit(apikey, competition, return_vector)

def push_match(apikey, competition, results):

	for team in results:

		d.push_team_tests_data(apikey, competition, team, results[team])

def push_metric(apikey, competition, metric):

	for team in metric:

			d.push_team_metrics_data(apikey, competition, team, metric[team])

def push_pit(apikey, competition, pit):

	for variable in pit:

		d.push_team_pit_data(apikey, competition, variable, pit[variable])

def get_team_metrics(apikey, tbakey, competition):

	metrics = d.get_metrics_data_formatted(apikey, competition)

	elo = {}
	gl2 = {}

	for team in metrics:

		elo[team] = metrics[team]["metrics"]["elo"]["score"]
		gl2[team] = metrics[team]["metrics"]["gl2"]["score"]

	elo = {k: v for k, v in sorted(elo.items(), key=lambda item: item[1])}
	gl2 = {k: v for k, v in sorted(gl2.items(), key=lambda item: item[1])}

	elo_ranked = []

	for team in elo:

		elo_ranked.append({"team": str(team), "elo": str(elo[team])})

	gl2_ranked = []

	for team in gl2:

		gl2_ranked.append({"team": str(team), "gl2": str(gl2[team])})

	return {"elo-ranks": elo_ranked, "glicko2-ranks": gl2_ranked}

def graph_pit_histogram(apikey, competition, figsize=(80,15)):

	pit = d.get_pit_variable_formatted(apikey, competition)

	fig, ax = plt.subplots(1, len(pit), sharey=True, figsize=figsize)

	i = 0

	for variable in pit:

		ax[i].hist(pit[variable])
		ax[i].invert_xaxis()

		ax[i].set_xlabel('')
		ax[i].set_ylabel('Frequency')
		ax[i].set_title(variable)

		plt.yticks(np.arange(len(pit[variable])))

		i+=1

	plt.show()