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
		- linux daemon now sends stderr to errorlog.txt
		- added verbose option to linux superscript to allow for interactive output
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

import json
import os
import math
from multiprocessing import Pool, freeze_support
import time
import warnings
import sys
import asyncio
import websockets
import pymongo

from interface import splash, log, ERR, INF, stdout, stderr
from data import get_previous_time, set_current_time, load_match, push_match, load_metric, push_metric, load_pit, push_pit
from processing import matchloop, metricloop, pitloop

config_path = "config.json"
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

async def main_lin(socket, path):

	while True:

		try:

			loop_start = time.time()

			current_time = time.time()
			await socket.send("current time: " + str(current_time))

			config = {}
			if load_config(config_path, config) == 1:
				sys.exit(1)

			error_flag = False

			try:
				competition = config["competition"]
			except:
				await socket.send("could not find competition field in config")
				error_flag = True
			try:
				match_tests = config["statistics"]["match"]
			except:
				await socket.send("could not find match_tests field in config")
				error_flag = True
			try:
				metrics_tests = config["statistics"]["metric"]
			except:
				await socket.send("could not find metrics_tests field in config")
				error_flag = True
			try:
				pit_tests = config["statistics"]["pit"]
			except:
				await socket.send("could not find pit_tests field in config")
				error_flag = True
			
			if error_flag:
				sys.exit(1)
			error_flag = False

			if competition == None or competition == "":
				await socket.send("competition field in config must not be empty")
				error_flag = True
			if match_tests == None:
				await socket.send("match_tests field in config must not be empty")
				error_flag = True
			if metrics_tests == None:
				await socket.send("metrics_tests field in config must not be empty")
				error_flag = True
			if pit_tests == None:
				await socket.send("pit_tests field in config must not be empty")
				error_flag = True
			
			if error_flag:
				sys.exit(1)

			await socket.send("found and loaded competition, match_tests, metrics_tests, pit_tests from config")

			sys_max_threads = os.cpu_count()
			try:
				cfg_max_threads = config["max-threads"]
			except:
				await socket.send("max-threads field in config must not be empty, refer to documentation for configuration options", code = 109)
				sys.exit(1)

			if cfg_max_threads > -sys_max_threads and cfg_max_threads < 0 :
				alloc_processes = sys_max_threads + cfg_max_threads
			elif cfg_max_threads > 0 and cfg_max_threads < 1:
				alloc_processes = math.floor(cfg_max_threads * sys_max_threads)
			elif cfg_max_threads > 1 and cfg_max_threads <= sys_max_threads:
				alloc_processes = cfg_max_threads
			elif cfg_max_threads == 0:
				alloc_processes = sys_max_threads
			else:
				await socket.send("max-threads must be between -" + str(sys_max_threads) + " and " + str(sys_max_threads) + ", but got " + cfg_max_threads)
				sys.exit(1)

			await socket.send("found and loaded max-threads from config")
			await socket.send("attempting to start " + str(alloc_processes) + " threads")
			try:
				exec_threads = Pool(processes = alloc_processes)
			except Exception as e:
				await socket.send("unable to start threads")
				sys.exit(1)
			await socket.send("successfully initialized " + str(alloc_processes) + " threads")

			exit_flag = False

			try:
				apikey = config["key"]["database"]
			except:
				await socket.send("database key field in config must be present")
				exit_flag = True
			try:
				tbakey = config["key"]["tba"]
			except:
				await socket.send("tba key field in config must be present")
				exit_flag = True

			if apikey == None or apikey == "":
				await socket.send("database key field in config must not be empty, please populate the database key")
				exit_flag = True
			if tbakey == None or tbakey == "":
				await socket.send("tba key field in config must not be empty, please populate the tba key")
				exit_flag = True

			if exit_flag:
				sys.exit(1)
			
			await socket.send("found and loaded database and tba keys")

			client = pymongo.MongoClient(apikey)

			previous_time = get_previous_time(client)
			await socket.send("analysis backtimed to: " + str(previous_time))

			start = time.time()
			await socket.send("loading match data")
			match_data = load_match(client, competition)
			await socket.send("finished loading match data in " + str(time.time() - start) + " seconds")

			start = time.time()
			await socket.send("performing analysis on match data")
			results = matchloop(client, competition, match_data, match_tests, exec_threads)
			await socket.send("finished match analysis in " + str(time.time() - start) + " seconds")

			start = time.time()
			await socket.send("uploading match results to database")
			push_match(client, competition, results)
			await socket.send("finished uploading match results in " + str(time.time() - start) + " seconds")

			start = time.time()
			await socket.send("performing analysis on team metrics")
			results = metricloop(tbakey, client, competition, current_time, metrics_tests)
			await socket.send("finished metric analysis and pushed to database in " + str(time.time() - start) + " seconds")

			start = time.time()
			await socket.send("loading pit data")
			pit_data = load_pit(client, competition)
			await socket.send("finished loading pit data in " + str(time.time() - start) + " seconds")

			start = time.time()
			await socket.send("performing analysis on pit data")
			results = pitloop(client, competition, pit_data, pit_tests)
			await socket.send("finished pit analysis in " + str(time.time() - start) + " seconds")

			start = time.time()
			await socket.send("uploading pit results to database")
			push_pit(client, competition, results)
			await socket.send("finished uploading pit results in " + str(time.time() - start) + " seconds")

			set_current_time(client, current_time)
			await socket.send("finished all tests in " + str(time.time() - loop_start) + " seconds, looping")

		except KeyboardInterrupt:
			await socket.send("detected KeyboardInterrupt, killing threads")
			if "exec_threads" in locals():
				exec_threads.terminate()
				exec_threads.join()
				exec_threads.close()
			await socket.send("terminated threads, exiting")
			loop_stored_exception = sys.exc_info()
			loop_exit_code = 0
			break
		except Exception as e:
			await socket.send("encountered an exception while running")
			await socket.send(str(e))
			loop_exit_code = 1
			break

	sys.exit(loop_exit_code)

def main_win():

	warnings.filterwarnings("ignore")
	sys.stderr = open("errorlog.txt", "w")

	splash(__version__)

	loop_exit_code = 0
	loop_stored_exception = None

	while True:

		try:

			loop_start = time.time()

			current_time = time.time()
			log(stdout, INF, "current time: " + str(current_time))

			config = {}
			if load_config(config_path, config) == 1:
				sys.exit(1)

			error_flag = False

			try:
				competition = config["competition"]
			except:
				log(stderr, ERR, "could not find competition field in config", code = 101)
				error_flag = True
			try:
				match_tests = config["statistics"]["match"]
			except:
				log(stderr, ERR, "could not find match_tests field in config", code = 102)
				error_flag = True
			try:
				metrics_tests = config["statistics"]["metric"]
			except:
				log(stderr, ERR, "could not find metrics_tests field in config", code = 103)
				error_flag = True
			try:
				pit_tests = config["statistics"]["pit"]
			except:
				log(stderr, ERR, "could not find pit_tests field in config", code = 104)
				error_flag = True
			
			if error_flag:
				sys.exit(1)
			error_flag = False

			if competition == None or competition == "":
				log(stderr, ERR, "competition field in config must not be empty", code = 105)
				error_flag = True
			if match_tests == None:
				log(stderr, ERR, "match_tests field in config must not be empty", code = 106)
				error_flag = True
			if metrics_tests == None:
				log(stderr, ERR, "metrics_tests field in config must not be empty", code = 107)
				error_flag = True
			if pit_tests == None:
				log(stderr, ERR, "pit_tests field in config must not be empty", code = 108)
				error_flag = True
			
			if error_flag:
				sys.exit(1)

			log(stdout, INF, "found and loaded competition, match_tests, metrics_tests, pit_tests from config")

			sys_max_threads = os.cpu_count()
			try:
				cfg_max_threads = config["max-threads"]
			except:
				log(stderr, ERR, "max-threads field in config must not be empty, refer to documentation for configuration options", code = 109)
				sys.exit(1)

			if cfg_max_threads > -sys_max_threads and cfg_max_threads < 0 :
				alloc_processes = sys_max_threads + cfg_max_threads
			elif cfg_max_threads > 0 and cfg_max_threads < 1:
				alloc_processes = math.floor(cfg_max_threads * sys_max_threads)
			elif cfg_max_threads > 1 and cfg_max_threads <= sys_max_threads:
				alloc_processes = cfg_max_threads
			elif cfg_max_threads == 0:
				alloc_processes = sys_max_threads
			else:
				log(stderr, ERR, "max-threads must be between -" + str(sys_max_threads) + " and " + str(sys_max_threads) + ", but got " + cfg_max_threads, code = 110)
				sys.exit(1)

			log(stdout, INF, "found and loaded max-threads from config")
			log(stdout, INF, "attempting to start " + str(alloc_processes) + " threads")
			try:
				exec_threads = Pool(processes = alloc_processes)
			except Exception as e:
				log(stderr, ERR, "unable to start threads", code = 200)
				log(stderr, INF, e)
				sys.exit(1)
			log(stdout, INF, "successfully initialized " + str(alloc_processes) + " threads")

			exit_flag = False

			try:
				apikey = config["key"]["database"]
			except:
				log(stderr, ERR, "database key field in config must be present", code = 111)
				exit_flag = True
			try:
				tbakey = config["key"]["tba"]
			except:
				log(stderr, ERR, "tba key field in config must be present", code = 112)
				exit_flag = True

			if apikey == None or apikey == "":
				log(stderr, ERR, "database key field in config must not be empty, please populate the database key")
				exit_flag = True
			if tbakey == None or tbakey == "":
				log(stderr, ERR, "tba key field in config must not be empty, please populate the tba key")
				exit_flag = True

			if exit_flag:
				sys.exit(1)
			
			log(stdout, INF, "found and loaded database and tba keys")

			client = pymongo.MongoClient(apikey)

			previous_time = get_previous_time(client)
			log(stdout, INF, "analysis backtimed to: " + str(previous_time))

			start = time.time()
			log(stdout, INF, "loading match data")
			match_data = load_match(client, competition)
			log(stdout, INF, "finished loading match data in " + str(time.time() - start) + " seconds")

			start = time.time()
			log(stdout, INF, "performing analysis on match data")
			results = matchloop(client, competition, match_data, match_tests, exec_threads)
			log(stdout, INF, "finished match analysis in " + str(time.time() - start) + " seconds")

			start = time.time()
			log(stdout, INF, "uploading match results to database")
			push_match(client, competition, results)
			log(stdout, INF, "finished uploading match results in " + str(time.time() - start) + " seconds")

			start = time.time()
			log(stdout, INF, "performing analysis on team metrics")
			results = metricloop(tbakey, client, competition, current_time, metrics_tests)
			log(stdout, INF, "finished metric analysis and pushed to database in " + str(time.time() - start) + " seconds")

			start = time.time()
			log(stdout, INF, "loading pit data")
			pit_data = load_pit(client, competition)
			log(stdout, INF, "finished loading pit data in " + str(time.time() - start) + " seconds")

			start = time.time()
			log(stdout, INF, "performing analysis on pit data")
			results = pitloop(client, competition, pit_data, pit_tests)
			log(stdout, INF, "finished pit analysis in " + str(time.time() - start) + " seconds")

			start = time.time()
			log(stdout, INF, "uploading pit results to database")
			push_pit(client, competition, results)
			log(stdout, INF, "finished uploading pit results in " + str(time.time() - start) + " seconds")

			set_current_time(client, current_time)
			log(stdout, INF, "finished all tests in " + str(time.time() - loop_start) + " seconds, looping")

		except KeyboardInterrupt:
			log(stdout, INF, "detected KeyboardInterrupt, killing threads")
			if "exec_threads" in locals():
				exec_threads.terminate()
				exec_threads.join()
				exec_threads.close()
			log(stdout, INF, "terminated threads, exiting")
			loop_stored_exception = sys.exc_info()
			loop_exit_code = 0
			break
		except Exception as e:
			log(stderr, ERR, "encountered an exception while running")
			print(e, file = stderr)
			loop_exit_code = 1
			break

	sys.exit(loop_exit_code)

def load_config(path, config_vector):
	try:
		f = open(path, "r")
		config_vector.update(json.load(f))
		f.close()
		#socket.send("found and opened config at <" + path + ">")
		return 0
	except:
		#log(stderr, ERR, "could not find config at <" + path + ">, generating blank config and exiting", code = 100)
		f = open(path, "w")
		f.write(sample_json)
		f.close()
		return 1

def save_config(path, config_vector):
	try:
		f = open(path)
		json.dump(config_vector)
		f.close()
		return 0
	except:
		return 1

def start(pid_path, profile = False):
	f = open('errorlog.txt', 'w+')
	with daemon.DaemonContext(
		working_directory=os.getcwd(),
		pidfile=pidfile.TimeoutPIDLockFile(pid_path),
		stderr=f
		):
		start_server = websockets.serve(main_lin, "127.0.0.1", 5678)
		asyncio.get_event_loop().run_until_complete(start_server)
		asyncio.get_event_loop().run_forever()

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
		main_win()

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
				main_win()
			else:
				print("usage: %s start|stop|restart|verbose" % sys.argv[0])
				sys.exit(2)
			sys.exit(0)
		else:
			print("usage: %s start|stop|restart|verbose" % sys.argv[0])
			sys.exit(2)