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

import json
from multiprocessing import freeze_support
import os
import pymongo
import sys
import time
import traceback
import warnings
import zmq
import pull
from config import parse_config_persistent, parse_config_variable, resolve_config_conflicts, load_config, save_config, ConfigurationError
from data import get_previous_time, set_current_time, check_new_database_matches
from interface import splash, log, ERR, INF, stdout, stderr
from module import Match, Metric, Pit

config_path = "config.json"

def main(send, verbose = False, profile = False, debug = False):

	def close_all():
		if "exec_threads" in locals():
			exec_threads.terminate()
			exec_threads.join()
			exec_threads.close()
		if "client" in locals():
			client.close()
		if "f" in locals():
			f.close()

	warnings.filterwarnings("ignore")
	exit_code = 0

	if verbose:
		splash(__version__)

	modules = {"match": Match, "metric": Metric, "pit": Pit}

	while True:

		try:

			loop_start = time.time()

			send(stdout, INF, "current time: " + str(loop_start))

			config = {}

			if load_config(config_path, config):
				raise ConfigurationError("could not find config at <" + config_path + ">, generating blank config and exiting", 110)
			
			send(stdout, INF, "found and loaded config at <" + config_path + ">")

			apikey, tbakey, preference, sync = parse_config_persistent(send, config)

			send(stdout, INF, "found and loaded database and tba keys")

			client = pymongo.MongoClient(apikey)

			send(stdout, INF, "established connection to database")
			send(stdout, INF, "analysis backtimed to: " + str(get_previous_time(client)))

			config = resolve_config_conflicts(send, client, config, preference, sync)

			exec_threads, config_modules = parse_config_variable(send, config)
			if 'competition' in config['variable']:
				competition = config['variable']['competition']
			else:
				competition = pull.get_team_competition()
			for m in config_modules:
				if m in modules:
					start = time.time()
					current_module = modules[m](config_modules[m], client, tbakey, loop_start, competition)
					valid = current_module.validate_config()
					if not valid:
						continue
					current_module.run(exec_threads)
					send(stdout, INF, m + " module finished in " + str(time.time() - start) + " seconds")
					if debug:
						f = open(m + ".log", "w+")
						json.dump({"data": current_module.data, "results":current_module.results}, f, ensure_ascii=False, indent=4)
						f.close()

			set_current_time(client, loop_start)
			close_all()

			send(stdout, INF, "closed threads and database client")
			send(stdout, INF, "finished all tasks in " + str(time.time() - loop_start) + " seconds, looping")

			if profile:
				exit_code = 0
				break

			event_delay = config["variable"]["event-delay"]
			if event_delay:
				send(stdout, INF, "loop delayed until database returns new matches")
				new_match = False
				while not new_match:
					time.sleep(1)
					new_match = check_new_database_matches(client, competition)
				send(stdout, INF, "database returned new matches")
			else:
				loop_delay = float(config["variable"]["loop-delay"])
				remaining_time = loop_delay - (time.time() - loop_start)
				if remaining_time > 0:
					send(stdout, INF, "loop delayed by " + str(remaining_time) + " seconds")
					time.sleep(remaining_time)

		except KeyboardInterrupt:
			send(stdout, INF, "detected KeyboardInterrupt, killing threads")
			close_all()
			send(stdout, INF, "terminated threads, exiting")
			break

		except ConfigurationError as e:
			send(stderr, ERR, "encountered a configuration error: " + str(e), code = e.code)
			traceback.print_exc(file = stderr)
			exit_code = 1
			close_all()
			break

		except Exception as e:
			send(stderr, ERR, "encountered an exception while running", code = 1)
			traceback.print_exc(file = stderr)
			exit_code = 1
			close_all()
			break
	
	return exit_code

def start(pid_path, verbose = False, profile = False, debug = False):

	if profile:

		def send(target, level, message, code = 0):
			pass

		import cProfile, pstats, io
		profile = cProfile.Profile()
		profile.enable()
		exit_code = main(send, profile = True)
		profile.disable()
		f = open("profile.txt", 'w+')
		ps = pstats.Stats(profile, stream = f).sort_stats('cumtime')
		ps.print_stats()
		sys.exit(exit_code)

	elif verbose:

		exit_code = main(log, verbose = verbose)
		sys.exit(exit_code)

	elif debug:

		exit_code = main(log, verbose = True, profile = True, debug = debug)
		sys.exit(exit_code)

	else:
		
		f = open('errorlog.log', 'w+')
		with daemon.DaemonContext(
			working_directory = os.getcwd(),
			pidfile = pidfile.TimeoutPIDLockFile(pid_path),
			stderr = f
			):

			context = zmq.Context()
			socket = context.socket(zmq.PUB)
			socket.bind("tcp://*:5678")

			socket.send(b'status')

			def send(target, level, message, code = 0):
				socket.send(bytes("status: " + message, 'utf-8'))

			exit_code = main(send)
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
		else:
			traceback.print_exc(file = stderr)
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