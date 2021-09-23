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

__all__ = [
	"load_config",
	"save_config",
]

# imports:

import asyncio
import json
import math
from multiprocessing import Pool, freeze_support
import os
import pymongo
import sys
import threading
import time
import warnings
import websockets

from interface import splash, log, ERR, INF, stdout, stderr
from data import get_previous_time, pull_new_tba_matches, set_current_time, load_match, push_match, load_pit, push_pit, get_database_config, set_database_config
from processing import matchloop, metricloop, pitloop

config_path = "config.json"
sample_json = """{
	"persistent":{
		"key":{
			"database":"",
			"tba":""
		},
		"config-preference":"local",
		"synchronize-config":false
	},
	"variable":{
		"max-threads":0.5,
		"team":"",
		"competition": "2020ilch",
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
		},
		"even-delay":false,
		"loop-delay":60
	}
}"""

def main(send, verbose = False, profile = False, debug = False):

	def close_all():
		if "exec_threads" in locals():
			exec_threads.terminate()
			exec_threads.join()
			exec_threads.close()
		if "client" in locals():
			client.close()

	warnings.filterwarnings("ignore")
	sys.stderr = open("errorlog.log", "w")
	exit_code = 0

	if verbose:
		splash(__version__)

	while True:

		try:

			loop_start = time.time()

			send(stdout, INF, "current time: " + str(loop_start))

			config = {}

			if load_config(config_path, config):
				send(stderr, ERR, "could not find config at <" + config_path + ">, generating blank config and exiting", code = 100)
				exit_code = 1
				break
			
			send(stdout, INF, "found and loaded config at <" + config_path + ">")

			flag, apikey, tbakey, preference, sync = parse_config_persistent(send, config)
			if flag:
				exit_code = 1
				break
			send(stdout, INF, "found and loaded database and tba keys")

			client = pymongo.MongoClient(apikey)

			send(stdout, INF, "established connection to database")
			send(stdout, INF, "analysis backtimed to: " + str(get_previous_time(client)))

			resolve_config_conflicts(send, client, config, preference, sync)
			if config == 1:
				exit_code = 1
				break
			flag, exec_threads, competition, match_tests, metrics_tests, pit_tests = parse_config_variable(send, config)
			if flag:
				exit_code = 1
				break

			start = time.time()
			send(stdout, INF, "loading match, metric, pit data (this may take a few seconds)")
			match_data = load_match(client, competition)
			metrics_data = pull_new_tba_matches(tbakey, competition, loop_start)
			pit_data = load_pit(client, competition)
			send(stdout, INF, "finished loading match, metric, pit data in "+ str(time.time() - start) + " seconds")

			start = time.time()
			send(stdout, INF, "performing analysis on match, metrics, pit data")
			match_results = matchloop(client, competition, match_data, match_tests, exec_threads)
			metrics_results = metricloop(client, competition, metrics_data, metrics_tests)
			pit_results = pitloop(client, competition, pit_data, pit_tests)
			send(stdout, INF, "finished analysis in " + str(time.time() - start) + " seconds")

			start = time.time()
			send(stdout, INF, "uploading match, metrics, pit results to database")
			push_match(client, competition, match_results)
			push_pit(client, competition, pit_results)
			send(stdout, INF, "finished uploading results in " + str(time.time() - start) + " seconds")

			if debug:
				f = open("matchloop.log", "w+")
				json.dump(match_results, f, ensure_ascii=False, indent=4)
				f.close()

				f = open("pitloop.log", "w+")
				json.dump(pit_results, f, ensure_ascii=False, indent=4)
				f.close()

			set_current_time(client, loop_start)
			close_all()

			send(stdout, INF, "closed threads and database client")
			send(stdout, INF, "finished all tasks in " + str(time.time() - loop_start) + " seconds, looping")

			if profile:
				return # return instead of break to avoid sys.exit

			loop_delay = float(config["variable"]["loop-delay"])
			remaining_time = loop_delay - (time.time() - loop_start)
			if remaining_time > 0:
				send(stdout, INF, "loop delayed by " + str(remaining_time) + " seconds")
				time.sleep(remaining_time)

		except KeyboardInterrupt:
			send(stdout, INF, "detected KeyboardInterrupt, killing threads")
			close_all()
			send(stdout, INF, "terminated threads, exiting")
			loop_exit_code = 0
			break

		except Exception as e:
			send(stderr, ERR, "encountered an exception while running", code = 1)
			print(e, file = stderr)
			exit_code = 1
			close_all()
			break
	
	sys.exit(exit_code)

def parse_config_persistent(send, config):

	exit_flag = False
	try:
		apikey = config["persistent"]["key"]["database"]
	except:
		send(stderr, ERR, "database key field in config must be present", code = 111)
		exit_flag = True
	try:
		tbakey = config["persistent"]["key"]["tba"]
	except:
		send(stderr, ERR, "tba key field in config must be present", code = 112)
		exit_flag = True
	try:
		preference = config["persistent"]["config-preference"]
	except:
		send(stderr, ERR, "config-preference field in config must be present", code = 113)
		exit_flag = True
	try:
		sync = config["persistent"]["synchronize-config"]
	except:
		send(stderr, ERR, "synchronize-config field in config must be present", code = 114)
		exit_flag = True

	if apikey == None or apikey == "":
		send(stderr, ERR, "database key field in config must not be empty, please populate the database key", code = 115)
		exit_flag = True
	if tbakey == None or tbakey == "":
		send(stderr, ERR, "tba key field in config must not be empty, please populate the tba key", code = 116)
		exit_flag = True
	if preference == None or preference == "":
		send(stderr, ERR, "config-preference field in config must not be empty, please populate config-preference", code = 117)
		exit_flag = True
	if sync != True and sync != False:
		send(stderr, ERR, "synchronize-config field in config must be a boolean, please populate synchronize-config", code = 118)
		exit_flag = True

	return exit_flag, apikey, tbakey, preference, sync

def parse_config_variable(send, config):

	exit_flag = False

	sys_max_threads = os.cpu_count()
	try:
		cfg_max_threads = config["variable"]["max-threads"]
	except:
		send(stderr, ERR, "max-threads field in config must not be empty, refer to documentation for configuration options", code = 109)
		exit_flag = True

	if cfg_max_threads > -sys_max_threads and cfg_max_threads < 0 :
		alloc_processes = sys_max_threads + cfg_max_threads
	elif cfg_max_threads > 0 and cfg_max_threads < 1:
		alloc_processes = math.floor(cfg_max_threads * sys_max_threads)
	elif cfg_max_threads > 1 and cfg_max_threads <= sys_max_threads:
		alloc_processes = cfg_max_threads
	elif cfg_max_threads == 0:
		alloc_processes = sys_max_threads
	else:
		send(stderr, ERR, "max-threads must be between -" + str(sys_max_threads) + " and " + str(sys_max_threads) + ", but got " + cfg_max_threads, code = 110)
		exit_flag = True

	try:
		exec_threads = Pool(processes = alloc_processes)
	except Exception as e:
		send(stderr, ERR, "unable to start threads", code = 200)
		send(stderr, INF, e)
		exit_flag = True
	send(stdout, INF, "successfully initialized " + str(alloc_processes) + " threads")

	try:
		competition = config["variable"]["competition"]
	except:
		send(stderr, ERR, "could not find competition field in config", code = 101)
		exit_flag = True
	try:
		match_tests = config["variable"]["statistics"]["match"]
	except:
		send(stderr, ERR, "could not find match field in config", code = 102)
		exit_flag = True
	try:
		metrics_tests = config["variable"]["statistics"]["metric"]
	except:
		send(stderr, ERR, "could not find metrics field in config", code = 103)
		exit_flag = True
	try:
		pit_tests = config["variable"]["statistics"]["pit"]
	except:
		send(stderr, ERR, "could not find pit field in config", code = 104)
		exit_flag = True

	if competition == None or competition == "":
		send(stderr, ERR, "competition field in config must not be empty", code = 105)
		exit_flag = True
	if match_tests == None:
		send(stderr, ERR, "matchfield in config must not be empty", code = 106)
		exit_flag = True
	if metrics_tests == None:
		send(stderr, ERR, "metrics field in config must not be empty", code = 107)
		exit_flag = True
	if pit_tests == None:
		send(stderr, ERR, "pit field in config must not be empty", code = 108)
		exit_flag = True

	send(stdout, INF, "found and loaded competition, match, metrics, pit from config")

	return exit_flag, exec_threads, competition, match_tests, metrics_tests, pit_tests

def resolve_config_conflicts(send, client, config, preference, sync):

	if sync:
		if preference == "local" or preference == "client":
			send(stdout, INF, "config-preference set to local/client, loading local config information")
			remote_config = get_database_config(client)
			if remote_config != config["variable"]:
				set_database_config(client, config["variable"])
				send(stdout, INF, "database config was different and was updated")
			return
		elif preference == "remote" or preference == "database":
			send(stdout, INF, "config-preference set to remote/database, loading remote config information")
			remote_config= get_database_config(client)
			if remote_config != config["variable"]:
				config["variable"] = remote_config
				if save_config(config_path, config):
					send(stderr, ERR, "local config was different but could not be updated")
					config = 1
					return
				send(stdout, INF, "local config was different and was updated")
			return
		else:
			send(stderr, ERR, "config-preference field in config must be \"local\"/\"client\" or \"remote\"/\"database\"")
			config = 1
			return
	else:
		if preference == "local" or preference == "client":
			send(stdout, INF, "config-preference set to local/client, loading local config information")
			return
		elif preference == "remote" or preference == "database":
			send(stdout, INF, "config-preference set to remote/database, loading database config information")
			config["variable"] = get_database_config(client)
			return
		else:
			send(stderr, ERR, "config-preference field in config must be \"local\"/\"client\" or \"remote\"/\"database\"")
			config = 1
			return

def load_config(path, config_vector):
	try:
		f = open(path, "r")
		config_vector.update(json.load(f))
		f.close()
		return 0
	except:
		f = open(path, "w")
		f.write(sample_json)
		f.close()
		return 1

def save_config(path, config_vector):
	f = open(path, "w+")
	json.dump(config_vector, f, ensure_ascii=False, indent=4)
	f.close()
	return 0

def start(pid_path, verbose = False, profile = False, debug = False):

	if profile:

		def send(target, level, message, code = 0):
			pass

		import cProfile, pstats, io
		profile = cProfile.Profile()
		profile.enable()
		main(send, profile = True)
		profile.disable()
		f = open("profile.txt", 'w+')
		ps = pstats.Stats(profile, stream = f).sort_stats('cumtime')
		ps.print_stats()

	elif verbose:

		main(log, verbose = verbose)

	elif debug:

		main(log, verbose = True, profile = True, debug = debug)

	else:

		f = open('errorlog.txt', 'w+')
		with daemon.DaemonContext(
			working_directory=os.getcwd(),
			pidfile=pidfile.TimeoutPIDLockFile(pid_path),
			stderr=f
			):

			async def handler(client, path):
				clients.append(client)
				while True:
					try:
						pong_waiter = await client.ping()
						await pong_waiter
						time.sleep(3)
					except Exception as e:
						clients.remove(client)
						break

			async def send_one(client, data):
				await client.send(data)
				
			def send(target, level, message, code = 0):
				message_clients = clients.copy()
				for client in message_clients:
					try:
						asyncio.run(send_one(client, message))
					except:
						pass

			clients = []
			start_server = websockets.serve(handler, "0.0.0.0", 5678)

			asyncio.get_event_loop().run_until_complete(start_server)
			threading.Thread(target = asyncio.get_event_loop().run_forever).start()

			main(send)	

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
		else:
			print(str(err))
			sys.exit(1)

def restart(pid_path):
	stop(pid_path)
	start(pid_path)

if __name__ == "__main__":

	if sys.platform.startswith("win"):
		freeze_support()
		start(None, verbose = True)

	else:
		import daemon
		from daemon import pidfile
		from signal import SIGTERM
		pid_path = "tra-daemon.pid"
		if len(sys.argv) == 2:
			if 'start' == sys.argv[1]:
				start(pid_path)
			elif 'stop' == sys.argv[1]:
				stop(pid_path)
			elif 'restart' == sys.argv[1]:
				restart(pid_path)
			elif 'verbose' == sys.argv[1]:
				start(None, verbose = True)
			elif 'profile' == sys.argv[1]:
				start(None, profile=True)
			elif 'debug' == sys.argv[1]:
				start(None, debug = True)
			else:
				print("usage: %s start|stop|restart|verbose|profile|debug" % sys.argv[0])
				sys.exit(2)
			sys.exit(0)
		else:
			print("usage: %s start|stop|restart|verbose|profile|debug" % sys.argv[0])
			sys.exit(2)