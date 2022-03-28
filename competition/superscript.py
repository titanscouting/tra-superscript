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

import os, sys, time
import pymongo # soon to be deprecated
import traceback
import warnings
from config import Configuration, ConfigurationError
from data import get_previous_time, set_current_time, check_new_database_matches, clear_metrics
from interface import Logger
from module import Match, Metric, Pit
import zmq

config_path = "config.json"

def main(logger, verbose, profile, debug, socket_send = None):

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
			clear_metrics(client, config.competition)
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

			set_current_time(client, loop_start)
			close_all()

			logger.info("closed threads and database client")
			logger.info("finished all tasks in " + str(time.time() - loop_start) + " seconds, looping")
			socket_send("closed threads and database client")
			socket_send("finished all tasks in " + str(time.time() - loop_start) + " seconds, looping")

			if profile:
				return 0

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
			print("usage: %s start|stop|restart|verbose|profile|debug" % sys.argv[0])
			sys.exit(2)