# testing purposes only, not to be used or run

import json
import multiprocessing
import os
import math
from multiprocessing import Pool
import time
import warnings
import sys
import asyncio
import websockets
import lockfile

from interface import splash, log, ERR, INF, stdout, stderr
from dataset import get_previous_time, set_current_time, load_match, push_match, load_metric, push_metric, load_pit, push_pit
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

async def main(socket, path):

	#warnings.filterwarnings("ignore")
	#sys.stderr = open("errorlog.txt", "w")

	#splash(__version__)

	#loop_exit_code = 0
	#loop_stored_exception = None

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
				#log(stderr, INF, e)
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

			previous_time = get_previous_time(apikey)
			await socket.send("analysis backtimed to: " + str(previous_time))

			start = time.time()
			await socket.send("loading match data")
			match_data = load_match(apikey, competition)
			await socket.send("finished loading match data in " + str(time.time() - start) + " seconds")

			start = time.time()
			await socket.send("performing analysis on match data")
			results = matchloop(apikey, competition, match_data, match_tests, exec_threads)
			await socket.send("finished match analysis in " + str(time.time() - start) + " seconds")

			start = time.time()
			await socket.send("uploading match results to database")
			push_match(apikey, competition, results)
			await socket.send("finished uploading match results in " + str(time.time() - start) + " seconds")

			start = time.time()
			await socket.send("performing analysis on team metrics")
			results = metricloop(tbakey, apikey, competition, current_time, metrics_tests)
			await socket.send("finished metric analysis and pushed to database in " + str(time.time() - start) + " seconds")

			start = time.time()
			await socket.send("loading pit data")
			pit_data = load_pit(apikey, competition)
			await socket.send("finished loading pit data in " + str(time.time() - start) + " seconds")

			start = time.time()
			await socket.send("performing analysis on pit data")
			results = pitloop(apikey, competition, pit_data, pit_tests)
			await socket.send("finished pit analysis in " + str(time.time() - start) + " seconds")

			start = time.time()
			await socket.send("uploading pit results to database")
			push_pit(apikey, competition, results)
			await socket.send("finished uploading pit results in " + str(time.time() - start) + " seconds")

			set_current_time(apikey, current_time)
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

import daemon
from daemon import pidfile

if __name__ == "__main__":
	with daemon.DaemonContext(
		working_directory=os.getcwd(),
		pidfile=pidfile.TimeoutPIDLockFile("/var/run/tra-daemon.pid"),
		):
		if sys.platform.startswith("win"):
			multiprocessing.freeze_support()
		start_server = websockets.serve(main, "127.0.0.1", 5678)
		asyncio.get_event_loop().run_until_complete(start_server)
		asyncio.get_event_loop().run_forever()