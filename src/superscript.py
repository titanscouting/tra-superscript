# Titan Robotics Team 2022: Superscript Script
# Written by Arthur Lu, Jacob Levine, and Dev Singh
# Notes:
# setup:

__version__ = "1.0.0"

# changelog should be viewed using print(analysis.__changelog__)
__changelog__ = """changelog:
	1.0.0:
		- superscript now runs in PEP 3143 compliant well behaved daemon on Linux systems
		- linux superscript daemon has integrated websocket output to monitor progress/status remotely
		- linux daemon now sends stderr to errorlog.log
		- added verbose option to linux superscript to allow for interactive output
		- moved pymongo import to superscript.py
		- added profile option to linux superscript to profile runtime of script
		- reduced memory usage slightly by consolidating the unwrapped input data
		- added debug option, which performs one loop of analysis and dumps results to local files
		- added event and time delay options to config
			- event delay pauses loop until even listener recieves an update
			- time delay pauses loop until the time specified has elapsed since the BEGINNING of previous loop
		- added options to pull config information from database (reatins option to use local config file)
			- config-preference option selects between prioritizing local config and prioritizing database config
			- synchronize-config option selects whether to update the non prioritized config with the prioritized one
			- divided config options between persistent ones (keys), and variable ones (everything else)
		- generalized behavior of various core components by collecting loose functions in several dependencies into classes
			- module.py contains classes, each one represents a single data analysis routine
			- config.py contains the Configuration class, which stores the configuration information and abstracts the getter methods
	0.9.3:
		- improved data loading performance by removing redundant PyMongo client creation (120s to 14s)
		- passed singular instance of PyMongo client as standin for apikey parameter in all data.py functions
	0.9.2:
		- removed unessasary imports from data
		- minor changes to interface
	0.9.1:
		- fixed bugs in configuration item loading exception handling
	0.9.0:
		- moved printing and logging related functions to interface.py (changelog will stay in this file)
		- changed function return files for load_config and save_config to standard C values (0 for success, 1 for error)
		- added local variables for config location
		- moved dataset getting and setting functions to dataset.py (changelog will stay in this file)
		- moved matchloop, metricloop, pitloop and helper functions (simplestats) to processing.py
	0.8.6:
		- added proper main function
	0.8.5:
		- added more gradeful KeyboardInterrupt exiting
		- redirected stderr to errorlog.txt
	0.8.4:
		- added better error message for missing config.json
		- added automatic config.json creation
		- added splash text with version and system info
	0.8.3:
		- updated matchloop with new regression format (requires tra_analysis 3.x)
	0.8.2:
		- readded while true to main function
		- added more thread config options
	0.8.1:
		- optimized matchloop further by bypassing GIL
	0.8.0:
		- added multithreading to matchloop
		- tweaked user log
	0.7.0:
		- finished implementing main function
	0.6.2:
		- integrated get_team_rankings.py as get_team_metrics() function
		- integrated visualize_pit.py as graph_pit_histogram() function
	0.6.1:
		- bug fixes with analysis.Metric() calls
		- modified metric functions to use config.json defined default values
	0.6.0:
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
	0.5.2:
		- made changes due to refactoring of analysis
	0.5.1:
		- text fixes
		- removed matplotlib requirement
	0.5.0:
		- improved user interface
	0.4.2:
		- removed unessasary code
	0.4.1:
		- fixed bug where X range for regression was determined before sanitization
		- better sanitized data
	0.4.0:
		- fixed spelling issue in __changelog__
		- addressed nan bug in regression
		- fixed errors on line 335 with metrics calling incorrect key "glicko2"
		- fixed errors in metrics computing 
	0.3.0:
		- added analysis to pit data
	0.2.1:
		- minor stability patches
		- implemented db syncing for timestamps
		- fixed bugs
	0.2.0:
		- finalized testing and small fixes
	0.1.4:
		- finished metrics implement, trueskill is bugged
	0.1.3:
		- working
	0.1.2:
		- started implement of metrics
	0.1.1:
		- cleaned up imports
	0.1.0:
		- tested working, can push to database
	0.0.9:
		- tested working
		- prints out stats for the time being, will push to database later
	0.0.8:
		- added data import
		- removed tba import
		- finished main method
	0.0.7:
		- added load_config
		- optimized simpleloop for readibility
		- added __all__ entries
		- added simplestats engine
		- pending testing
	0.0.6:
		- fixes
	0.0.5:
		- imported pickle
		- created custom database object
	0.0.4:
		- fixed simpleloop to actually return a vector
	0.0.3:
		- added metricsloop which is unfinished
	0.0.2:
		- added simpleloop which is untested until data is provided
	0.0.1:
		- created script
		- added analysis, numba, numpy imports
"""

__author__ = (
	"Arthur Lu <learthurgo@gmail.com>",
	"Jacob Levine <jlevine@imsa.edu>",
)

# imports:

<<<<<<< HEAD
import os, sys, time
import pymongo # soon to be deprecated
import traceback
=======
from tra_analysis import analysis as an
import data as d
from collections import defaultdict
import json
import math
import numpy as np
import os
from os import system, name
from pathlib import Path
from multiprocessing import Pool
import platform
import sys
import time
>>>>>>> master
import warnings
from config import Configuration, ConfigurationError
from data import get_previous_time, set_current_time, check_new_database_matches
from interface import Logger
from module import Match, Metric, Pit
import zmq

<<<<<<< HEAD
config_path = "config.json"
=======
global exec_threads
>>>>>>> master

def main(logger, verbose, profile, debug, socket_send = None):

<<<<<<< HEAD
	def close_all():
		if "client" in locals():
			client.close()

	warnings.filterwarnings("ignore")

	logger.splash(__version__)

	modules = {"match": Match, "metric": Metric, "pit": Pit}

	while True:

		try:

			loop_start = time.time()

			logger.info("current time: " + str(loop_start))
			socket_send("current time: " + str(loop_start))

			config = Configuration(config_path)
			
			logger.info("found and loaded config at <" + config_path + ">")
			socket_send("found and loaded config at <" + config_path + ">")

			apikey, tbakey = config.database, config.tba

			logger.info("found and loaded database and tba keys")
			socket_send("found and loaded database and tba keys")

			client = pymongo.MongoClient(apikey)

			logger.info("established connection to database")
			socket_send("established connection to database")

			previous_time = get_previous_time(client)

			logger.info("analysis backtimed to: " + str(previous_time))
			socket_send("analysis backtimed to: " + str(previous_time))

			config.resolve_config_conflicts(logger, client)

			config_modules, competition = config.modules, config.competition

			for m in config_modules:
				if m in modules:
					start = time.time()
					current_module = modules[m](config_modules[m], client, tbakey, previous_time, competition)
					valid = current_module.validate_config()
					if not valid:
						continue
					current_module.run()
					logger.info(m + " module finished in " + str(time.time() - start) + " seconds")
					socket_send(m + " module finished in " + str(time.time() - start) + " seconds")
					if debug:
						logger.save_module_to_file(m, current_module.data, current_module.results) # logging flag check done in logger
=======
	global exec_threads

	sys.stderr = open("errorlog.txt", "w")

	warnings.filterwarnings("ignore")

	splash()

	while (True):

		try:

			current_time = time.time()
			print("[OK] time: " + str(current_time))

			config = load_config("config.json")
			competition = config["competition"]
			match_tests = config["statistics"]["match"]
			pit_tests = config["statistics"]["pit"]
			metrics_tests = config["statistics"]["metric"]
			print("[OK] configs loaded")

			print("[OK] starting threads")
			cfg_max_threads = config["max-threads"]
			sys_max_threads = os.cpu_count()
			if cfg_max_threads > -sys_max_threads and cfg_max_threads < 0 :
				alloc_processes = sys_max_threads + cfg_max_threads
			elif cfg_max_threads > 0 and cfg_max_threads < 1:
				alloc_processes = math.floor(cfg_max_threads * sys_max_threads)
			elif cfg_max_threads > 1 and cfg_max_threads <= sys_max_threads:
				alloc_processes = cfg_max_threads
			elif cfg_max_threads == 0:
				alloc_processes = sys_max_threads
			else:
				print("[ERROR] Invalid number of processes, must be between -" + str(sys_max_threads) + " and " + str(sys_max_threads))
				exit()
			exec_threads = Pool(processes = alloc_processes)
			print("[OK] " + str(alloc_processes) + " threads started")

			apikey = config["key"]["database"]
			tbakey = config["key"]["tba"]
			print("[OK] loaded keys")

			previous_time = get_previous_time(apikey)
			print("[OK] analysis backtimed to: " + str(previous_time))

			print("[OK] loading data")
			start = time.time()
			match_data = load_match(apikey, competition)
			pit_data = load_pit(apikey, competition)
			print("[OK] loaded data in " + str(time.time() - start) + " seconds")

			print("[OK] running match stats")
			start = time.time()
			matchloop(apikey, competition, match_data, match_tests)
			print("[OK] finished match stats in " + str(time.time() - start) + " seconds")

			print("[OK] running team metrics")
			start = time.time()
			metricloop(tbakey, apikey, competition, previous_time, metrics_tests)
			print("[OK] finished team metrics in " + str(time.time() - start) + " seconds")

			print("[OK] running pit analysis")
			start = time.time()
			pitloop(apikey, competition, pit_data, pit_tests)
			print("[OK] finished pit analysis in " + str(time.time() - start) + " seconds")
			
			set_current_time(apikey, current_time)
			print("[OK] finished all tests, looping")

			print_hrule()
		
		except KeyboardInterrupt:
			print("\n[OK] caught KeyboardInterrupt, killing processes")
			exec_threads.terminate()
			print("[OK] processes killed, exiting")
			exit()

		else:
			pass

		#clear()
>>>>>>> master

			set_current_time(client, loop_start)
			close_all()

<<<<<<< HEAD
			logger.info("closed threads and database client")
			logger.info("finished all tasks in " + str(time.time() - loop_start) + " seconds, looping")
			socket_send("closed threads and database client")
			socket_send("finished all tasks in " + str(time.time() - loop_start) + " seconds, looping")

			if profile:
				return 0
=======
def print_hrule():

	print("#"+38*"-"+"#")

def print_box(s):

	temp = "|"
	temp += s
	temp += (40-len(s)-2)*" "
	temp += "|"
	print(temp)

def splash():

	print_hrule()
	print_box(" superscript version: " + __version__)
	print_box(" os: " + platform.system())
	print_box(" python: " + platform.python_version())
	print_hrule()

def load_config(file):

	config_vector = {}

	try:
		f = open(file)
	except:
		print("[ERROR] could not locate config.json, generating blank config.json and exiting")
		f = open(file, "w")
		f.write(sample_json)
		exit()
	
	config_vector = json.load(f)
>>>>>>> master

			if debug:
				return 0

			event_delay = config["variable"]["event-delay"]
			if event_delay:
				logger.info("loop delayed until database returns new matches")
				socket_send("loop delayed until database returns new matches")
				new_match = False
				while not new_match:
					time.sleep(1)
					new_match = check_new_database_matches(client, competition)
				logger.info("database returned new matches")
				socket_send("database returned new matches")
			else:
				loop_delay = float(config["variable"]["loop-delay"])
				remaining_time = loop_delay - (time.time() - loop_start)
				if remaining_time > 0:
					logger.info("loop delayed by " + str(remaining_time) + " seconds")
					socket_send("loop delayed by " + str(remaining_time) + " seconds")
					time.sleep(remaining_time)

		except KeyboardInterrupt:
			close_all()
			logger.info("detected KeyboardInterrupt, exiting")
			socket_send("detected KeyboardInterrupt, exiting")
			return 0

		except ConfigurationError as e:
			str_e = "".join(traceback.format_exception(e))
			logger.error("encountered a configuration error: " + str(e))
			logger.error(str_e)
			socket_send("encountered a configuration error: " + str(e))
			socket_send(str_e)
			close_all()
			return 1

		except Exception as e:
			str_e = "".join(traceback.format_exception(e))
			logger.error("encountered an exception while running")
			logger.error(str_e)
			socket_send("encountered an exception while running")
			socket_send(str_e)
			close_all()
			return 1

def start(pid_path, verbose, profile, debug):

	if profile:

		def send(msg):
			pass

		logger = Logger(verbose, profile, debug)

		import cProfile, pstats, io
		profile = cProfile.Profile()
		profile.enable()
		exit_code = main(logger, verbose, profile, debug, socket_send = send)
		profile.disable()
		f = open("profile.txt", 'w+')
		ps = pstats.Stats(profile, stream = f).sort_stats('cumtime')
		ps.print_stats()
		sys.exit(exit_code)

	elif verbose:

		def send(msg):
			pass

		logger = Logger(verbose, profile, debug)

		exit_code = main(logger, verbose, profile, debug, socket_send = send)
		sys.exit(exit_code)

	elif debug:

		def send(msg):
			pass

		logger = Logger(verbose, profile, debug)

		exit_code = main(logger, verbose, profile, debug, socket_send = send)
		sys.exit(exit_code)

	else:

<<<<<<< HEAD
		logfile = "logfile.log"

		f = open(logfile, 'w+')
		f.close()

		e = open('errorlog.log', 'w+')
		with daemon.DaemonContext(
				working_directory = os.getcwd(),
				pidfile = pidfile.TimeoutPIDLockFile(pid_path),
				stderr = e
			):

			context = zmq.Context()
			socket = context.socket(zmq.PUB)
			socket.bind("tcp://*:5678")
			socket.send(b'status')

			def send(msg):
				socket.send(bytes("status: " + msg, "utf-8"))

			logger = Logger(verbose, profile, debug, file = logfile)

			exit_code = main(logger, verbose, profile, debug, socket_send = send)

			socket.close()
			f.close()
			
			sys.exit(exit_code)

def stop(pid_path):
	try:
		pf = open(pid_path, 'r')
		pid = int(pf.read().strip())
		pf.close()
	except IOError:
		sys.stderr.write("pidfile at <" + pid_path + "> does not exist. Daemon not running?\n")
		return

	try:
		while True:
			os.kill(pid, SIGTERM)
			time.sleep(0.01)
	except OSError as err:
		err = str(err)
		if err.find("No such process") > 0:
			if os.path.exists(pid_path):
				os.remove(pid_path)
=======
		previous_time = previous_time["latest_update"]

	return previous_time

def set_current_time(apikey, current_time):

	d.set_analysis_flags(apikey, "latest_update", {"latest_update":current_time})

def load_match(apikey, competition):

	return d.get_match_data_formatted(apikey, competition)

def simplestats(data_test):

	data = np.array(data_test[0])
	data = data[np.isfinite(data)]
	ranges = list(range(len(data)))

	test = data_test[1]

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

def matchloop(apikey, competition, data, tests): # expects 3D array with [Team][Variable][Match]

	global exec_threads

	short_mapping = {"regression_linear": "lin", "regression_logarithmic": "log", "regression_exponential": "exp", "regression_polynomial": "ply", "regression_sigmoidal": "sig"}

	class AutoVivification(dict):
		def __getitem__(self, item):
			try:
				return dict.__getitem__(self, item)
			except KeyError:
				value = self[item] = type(self)()
				return value

	return_vector = {}
	
	team_filtered = []
	variable_filtered = []
	variable_data = []
	test_filtered = []
	result_filtered = []
	return_vector = AutoVivification()

	for team in data:

		for variable in data[team]:

			if variable in tests:

				for test in tests[variable]:

					team_filtered.append(team)
					variable_filtered.append(variable)
					variable_data.append((data[team][variable], test))
					test_filtered.append(test)

	result_filtered = exec_threads.map(simplestats, variable_data)
	i = 0

	result_filtered = list(result_filtered)

	for result in result_filtered:

		filtered = test_filtered[i]

		try:
			short = short_mapping[filtered]
			return_vector[team_filtered[i]][variable_filtered[i]][test_filtered[i]] = result[short]
		except KeyError: # not in mapping
			return_vector[team_filtered[i]][variable_filtered[i]][test_filtered[i]] = result
		i += 1

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

>>>>>>> master
		else:
			traceback.print_exc(file = sys.stderr)
			sys.exit(1)

def restart(pid_path):
	stop(pid_path)
	start(pid_path, False, False, False)

if __name__ == "__main__":

	if sys.platform.startswith("win"):
		start(None, verbose = True)

	else:
		import daemon
		from daemon import pidfile
		from signal import SIGTERM
		pid_path = "tra-daemon.pid"
		if len(sys.argv) == 2:
			if 'start' == sys.argv[1]:
				start(pid_path, False, False, False)
			elif 'stop' == sys.argv[1]:
				stop(pid_path)
			elif 'restart' == sys.argv[1]:
				restart(pid_path)
			elif 'verbose' == sys.argv[1]:
				start(None, True, False, False)
			elif 'profile' == sys.argv[1]:
				start(None, False, True, False)
			elif 'debug' == sys.argv[1]:
				start(None, False, False, True)
			else:
				print("usage: %s start|stop|restart|verbose|profile|debug" % sys.argv[0])
				sys.exit(2)
			sys.exit(0)
		else:
<<<<<<< HEAD
			print("usage: %s start|stop|restart|verbose|profile|debug" % sys.argv[0])
			sys.exit(2)
=======

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

sample_json = """{
	"max-threads": 0.5,
	"team": "",
	"competition": "2020ilch",
	"key":{
		"database":"",
		"tba":""
	},
	"statistics":{
		"match":{
			"balls-blocked":["basic_stats","historical_analysis","regression_linear","regression_logarithmic","regression_exponential","regression_polynomial","regression_sigmoidal"],
			"balls-collected":["basic_stats","historical_analysis","regression_linear","regression_logarithmic","regression_exponential","regression_polynomial","regression_sigmoidal"],
			"balls-lower-teleop":["basic_stats","historical_analysis","regression_linear","regression_logarithmic","regression_exponential","regression_polynomial","regression_sigmoidal"],
			"balls-lower-auto":["basic_stats","historical_analysis","regression_linear","regression_logarithmic","regression_exponential","regression_polynomial","regression_sigmoidal"],
			"balls-started":["basic_stats","historical_analyss","regression_linear","regression_logarithmic","regression_exponential","regression_polynomial","regression_sigmoidal"],
			"balls-upper-teleop":["basic_stats","historical_analysis","regression_linear","regression_logarithmic","regression_exponential","regression_polynomial","regression_sigmoidal"],
			"balls-upper-auto":["basic_stats","historical_analysis","regression_linear","regression_logarithmic","regression_exponential","regression_polynomial","regression_sigmoidal"]

		},
		"metric":{
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
		},
		"pit":{
			"wheel-mechanism":true,
			"low-balls":true,
			"high-balls":true,
			"wheel-success":true,
			"strategic-focus":true,
			"climb-mechanism":true,
			"attitude":true
		}
	}
}"""

if __name__ == "__main__":
	if sys.platform.startswith('win'):
		multiprocessing.freeze_support()
	main()
>>>>>>> master
